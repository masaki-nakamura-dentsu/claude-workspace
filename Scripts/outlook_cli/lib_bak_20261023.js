const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');

// This file is shared via Dropbox and symlinked on both Macs, so it cannot
// hardcode one machine's shared-bot-browser PORT/PROFILE_DIR — each Mac runs
// its own separate shared Chrome instance (see memory shared_bot_browser.md).
// Detect the machine by the presence of d14461's Salesforce automation
// profile dir, which only exists on that Mac.
const D14461_PROFILE = `${process.env.HOME}/SalesforceExport/browser_profile`;
const IS_D14461 = fs.existsSync(D14461_PROFILE);
// 2026-10-12: 個人Mac(ICPTokyo2022)ではアカウント種別で使い分ける(memory browser_account_routing)。
// Outlookは会社アカウントなので、個人Gmail系の9227ではなく会社用 dentsu-work-bot / 9231 を使う。
const PORT = IS_D14461 ? 9226 : 9231;
const PROFILE_DIR = IS_D14461 ? D14461_PROFILE : `${process.env.HOME}/.chrome-profiles/dentsu-work-bot`;
const CDP_URL = `http://127.0.0.1:${PORT}`;
// 2026-09-02: Outlook Web migrated from outlook.office.com to
// outlook.cloud.microsoft (new Fluent UI ribbon, see 2026-08-12 note below)
// weeks ago, but this tab-matcher/login-check still only recognized the old
// domain — every connect() call failed to find the existing tab and opened
// a fresh one instead, silently accumulating dozens of stray Outlook tabs
// over repeated runs (found 11 duplicates in the shared bot browser this
// way). Fixed to recognize either domain.
const MAIL_URL = 'https://outlook.cloud.microsoft/mail/';
const MAIL_URL_PATTERNS = ['outlook.office.com', 'outlook.cloud.microsoft'];
function isMailUrl(url) {
  return MAIL_URL_PATTERNS.some((p) => url.includes(p));
}

async function isRunning() {
  try {
    const res = await fetch(`${CDP_URL}/json/version`);
    return res.ok;
  } catch {
    return false;
  }
}

function launchBrowser() {
  spawn('open', ['-na', 'Google Chrome', '--args',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE_DIR}`,
    '--window-position=-2500,-2500',
    '--lang=ja-JP', '--no-first-run', '--no-default-browser-check',
    MAIL_URL], { detached: true, stdio: 'ignore' }).unref();
}

// 2026-09-02: this shared bot browser window is never used for the user's
// own manual browsing (only occasional passkey/approval prompts) — but
// scripts that call connect() and then run for a while (goto/search/clicks)
// were leaving the window fully on-screen for their whole runtime, because
// nothing here ever repositioned it. context.newPage() (used when no
// existing mail tab is found) always forces the window to windowState
// "normal" at whatever position the OS puts it. goto()/click() on an
// already-obtained page do NOT re-trigger this, so a single reposition
// right after connect() obtains its page is enough to cover the rest of a
// script's run. windowState "minimized" is deliberately NOT used — it gets
// forced back to "normal" by any *other* script's new_page() elsewhere in
// this shared browser and that transition remains visible even with macOS
// window animations disabled — so we keep it "normal" and pin the position
// off-screen instead (see shared_bot_browser.md for the full history).
async function repositionOffscreen(context, page) {
  try {
    const session = await context.newCDPSession(page);
    const { windowId } = await session.send('Browser.getWindowForTarget');
    await session.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'normal' } });
    await session.send('Browser.setWindowBounds', { windowId, bounds: { left: -2500, top: -2500 } });
  } catch {
    // best-effort — never let window positioning break the actual task
  }
}

function getFrontmostApp() {
  try {
    const { execFileSync } = require('child_process');
    const out = execFileSync('osascript', ['-e',
      'tell application "System Events" to get name of first application process whose frontmost is true'],
      { timeout: 5000 }).toString().trim();
    return out || null;
  } catch {
    return null;
  }
}

function restoreFrontmostApp(appName) {
  if (!appName || appName === 'Google Chrome') return;
  try {
    const { execFileSync } = require('child_process');
    execFileSync('osascript', ['-e', `tell application "${appName}" to activate`], { timeout: 5000 });
  } catch {
    // best-effort
  }
}

async function connect() {
  if (!(await isRunning())) {
    launchBrowser();
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      if (await isRunning()) break;
    }
    if (!(await isRunning())) {
      throw new Error('Outlook用ブラウザの起動に失敗しました。');
    }
  }
  const frontApp = getFrontmostApp();
  const browser = await chromium.connectOverCDP(CDP_URL);
  const context = browser.contexts()[0];
  // Always open a fresh tab if no existing Outlook tab is found — this
  // browser is shared with other tools (teams_daemon, Salesforce scripts),
  // so reusing "whatever tab happens to be first" would hijack another
  // tool's tab instead of leaving it alone (bit us once: an existing
  // Outlook tab got silently navigated away to Teams by teams_daemon.py
  // before it got the same fix).
  let page = context.pages().find((p) => isMailUrl(p.url()));
  if (!page) {
    page = await context.newPage();
    await page.goto(MAIL_URL, { waitUntil: 'domcontentloaded' });
  }
  await repositionOffscreen(context, page);
  restoreFrontmostApp(frontApp);
  return { browser, page };
}

async function ensureLoggedIn(page) {
  for (let i = 0; i < 60; i++) {
    if (isMailUrl(page.url())) break;
    await page.waitForTimeout(1000);
  }
  await page.waitForTimeout(1000);
  // Use the search box as the "app has loaded" signal, not the message
  // listbox — the listbox is absent whenever a search has zero results, which
  // would otherwise be misdiagnosed as "not logged in".
  const searchBox = page.getByLabel('メール、会議、ファイルなどを検索します。');
  try {
    await searchBox.waitFor({ timeout: 15000 });
  } catch {
    if (page.url().includes('login.microsoftonline.com') || page.url().includes('myapps.dentsu.com')) {
      throw new Error('Outlook未ログインです。`outlook login` を実行し、開いたブラウザで手動ログイン(SSO/MFA)してください。');
    }
    throw new Error('Outlookの受信トレイが読み込めませんでした(表示が変わった可能性があります)。');
  }
}

async function getMessageListbox(page) {
  const lb = page.locator('[role="listbox"][aria-label*="メッセージ一覧"]');
  await lb.waitFor({ timeout: 15000 });
  return lb;
}

async function listMessageItems(page) {
  const lb = page.locator('[role="listbox"][aria-label*="メッセージ一覧"]');
  try {
    await lb.waitFor({ timeout: 8000 });
  } catch {
    return []; // no results (e.g. an empty search) renders no listbox at all
  }
  return lb.locator('[role="option"]').all();
}

async function search(page, query) {
  const box = page.getByLabel('メール、会議、ファイルなどを検索します。');
  await box.click();
  await box.fill('');
  await box.type(query, { delay: 10 });
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2000);
}

async function clearSearch(page) {
  const clearBtn = page.getByRole('button', { name: /検索を閉じる|検索のクリア|クリア/ }).first();
  if (await clearBtn.count() > 0) {
    await clearBtn.click().catch(() => {});
    await page.waitForTimeout(500);
  }
}

async function openMessageAt(page, index) {
  const items = await listMessageItems(page);
  if (index < 0 || index >= items.length) {
    throw new Error(`メッセージ一覧の範囲外です(0〜${items.length - 1})。`);
  }
  await items[index].click();
  await page.waitForTimeout(1500);
}

async function readOpenMessage(page) {
  const headings = await page.locator('[role="heading"][aria-level="3"]').all();
  if (headings.length === 0) {
    throw new Error('メッセージが開かれていません。');
  }
  const subject = (await headings[0].innerText().catch(() => '')).trim();
  let from = '';
  let date = '';
  for (const h of headings.slice(1)) {
    const t = (await h.innerText().catch(() => '')).trim();
    if (!t) continue;
    if (!date && /\d{4}\/\d{1,2}\/\d{1,2}/.test(t)) { date = t; continue; }
    if (!from && !t.startsWith('宛先')) from = t;
  }
  let body = '';
  const bodyLoc = page.locator('[aria-label="メッセージ本文"]').first();
  if (await bodyLoc.count() > 0) {
    body = (await bodyLoc.innerText().catch(() => '')).trim();
  }
  return { subject, from, date, body };
}

async function openCompose(page) {
  await page.getByRole('button', { name: /新規メール/ }).first().click();
  await page.waitForTimeout(1500);
}

async function fillRecipientField(page, ariaLabel, addresses) {
  if (!addresses || addresses.length === 0) return;
  const field = page.locator(`[aria-label="${ariaLabel}"]`).first();
  await field.click();
  for (const addr of addresses) {
    await page.keyboard.type(addr, { delay: 15 });
    await page.waitForTimeout(1200);
    const listbox = page.locator('[role="listbox"][aria-label="受信者の選択"]');
    if (await listbox.count() > 0 && await listbox.locator('[role="option"]').count() > 0) {
      await page.keyboard.press('Enter');
    } else {
      // no suggestion matched — still commit as a raw address
      await page.keyboard.press('Enter');
    }
    await page.waitForTimeout(300);
  }
}

async function fillSubject(page, text) {
  const subject = page.getByRole('textbox', { name: '科目' });
  await subject.click();
  await subject.fill('');
  await subject.type(text, { delay: 10 });
}

async function fillBody(page, text) {
  // A new compose window pre-fills the default signature into the body, so
  // a plain click() can land the cursor mid-signature (observed: split
  // "dentsu.co.jp" in half). Jump to the very start of the field first, then
  // push the signature down with trailing newlines after typing.
  const body = page.getByRole('textbox').nth(1);
  await body.click();
  await page.keyboard.press('Meta+ArrowUp');
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (lines[i]) await page.keyboard.type(lines[i], { delay: 5 });
    if (i < lines.length - 1) await page.keyboard.press('Enter');
  }
  await page.keyboard.press('Enter');
  await page.keyboard.press('Enter');
}

async function attachFiles(page, paths) {
  for (const p of paths) {
    // 2026-08-12: Outlook Web が outlook.cloud.microsoft の新UIに移行し、添付ボタンは
    // 「ホーム」ではなく「挿入」タブ内にある。role=button の accessible name では見つからず、
    // button要素のカスタム属性 label="添付ファイル" で掴む必要がある。
    const insertTab = page.getByRole('tab', { name: '挿入' }).first();
    if (await insertTab.isVisible().catch(() => false)) {
      await insertTab.click();
      await page.waitForTimeout(300);
    }
    await page.locator('button[label="添付ファイル"]').first().click({ timeout: 10000 });
    await page.waitForTimeout(500);
    const [chooser] = await Promise.all([
      page.waitForEvent('filechooser', { timeout: 10000 }),
      page.getByRole('menuitem', { name: 'このコンピューターから選択' }).click(),
    ]);
    await chooser.setFiles(p);
    await page.waitForTimeout(1500);
  }
}

async function clickSend(page) {
  const btn = page.getByRole('button', { name: '送信', exact: true });
  await btn.waitFor({ timeout: 5000 });
  await btn.click();
  await page.waitForTimeout(1500);
}

async function discardCompose(page) {
  const discardBtn = page.getByRole('button', { name: '破棄' });
  if (await discardBtn.count() > 0) {
    await discardBtn.click();
    await page.waitForTimeout(800);
    const ok = page.getByRole('button', { name: 'OK', exact: true });
    if (await ok.count() > 0) await ok.click();
    await page.waitForTimeout(500);
  }
}

module.exports = {
  connect, ensureLoggedIn, getMessageListbox, listMessageItems, search, clearSearch,
  openMessageAt, readOpenMessage, openCompose, fillRecipientField,
  fillSubject, fillBody, attachFiles, clickSend, discardCompose,
  repositionOffscreen, getFrontmostApp, restoreFrontmostApp,
  PORT, PROFILE_DIR, CDP_URL, MAIL_URL,
};
