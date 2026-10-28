// GBCすべての週報：部長会進行用(過去1週間・優先度高) のエクスポート(ステップ1)
// 会社用ブラウザ(このMacはport 9231 dentsu-work-bot、2026-10-12〜)を使う。~/Scripts/outlook_cli/lib.js と同じ接続パターン。
// メール認証コードが必要な場合はこのスクリプトが停止し、download_step2_enter_code.js <code> を実行する。
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.GBC_BOT_PORT) || 9231; // d14461では GBC_BOT_PORT=9226 で起動
const CDP_URL = `http://127.0.0.1:${PORT}`;
const REPORT_ID = '00O7F00000AmEiQUAV';
const REPORT_URL = `https://dgx.lightning.force.com/lightning/r/Report/${REPORT_ID}/view?queryScope=userFolders`;
const DOWNLOAD_DIR = path.join(__dirname, 'downloads');
const STATE_FILE = path.join(__dirname, '.export_state.json');

async function connect() {
  const browser = await chromium.connectOverCDP(CDP_URL);
  const context = browser.contexts()[0];
  return { browser, context };
}

(async () => {
  if (!fs.existsSync(DOWNLOAD_DIR)) fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });

  const { context } = await connect();
  const page = await context.newPage();
  await page.goto(REPORT_URL, { waitUntil: 'domcontentloaded' });

  let frame = null;
  for (let i = 0; i < 20; i++) {
    await page.waitForTimeout(1500);
    const f = page.frames().find((fr) => fr.url().includes('lightningReportApp'));
    if (f) {
      const txt = await f.evaluate(() => document.body.innerText).catch(() => '');
      if (txt.includes('合計レコード数')) { frame = f; break; }
    }
  }
  if (!frame) {
    console.log('ERROR: レポートフレームが見つかりません（読み込みタイムアウト）');
    process.exit(1);
  }

  const countLine = await frame.evaluate(() => {
    const m = document.body.innerText.match(/合計レコード数\s*\n?\s*(\d+)/);
    return m ? m[1] : null;
  });
  console.log('合計レコード数:', countLine);

  // 追加アクション menu (the "..." dropdown) — accessible name confirmed: 追加アクション - 編集
  const moreBtn = frame.getByRole('button', { name: /追加アクション/ }).first();
  await moreBtn.click({ timeout: 15000 });
  await page.waitForTimeout(800);
  await frame.getByText('エクスポート', { exact: true }).click({ timeout: 10000 });
  await page.waitForTimeout(2000);

  // Export options modal is portal-rendered on the OUTER page, not the iframe
  const exportConfirmBtn = page.getByRole('button', { name: 'エクスポート', exact: true }).last();
  await exportConfirmBtn.click({ timeout: 15000 });
  console.log('エクスポート確認ボタンをクリックしました。検証タブの出現を待ちます...');

  await page.waitForTimeout(4000);

  // Check for a new tab (identity verification) OR a direct download
  const pages = context.pages();
  const verifyPage = pages.find((p) => p.url().includes('identity/verification'));

  if (verifyPage) {
    console.log('メール認証コードが必要です。masaki.nakamura@dentsu.co.jp 宛のメールを確認し、');
    console.log('  node download_step2_enter_code.js <6桁コード>');
    console.log('を実行してください。');
    fs.writeFileSync(STATE_FILE, JSON.stringify({ awaitingCode: true, ts: Date.now() }));
    process.exit(0);
  }

  // No verification needed this time — try to catch the download directly
  console.log('検証タブなし。直接ダウンロードを試みます...');
  try {
    const download = await page.waitForEvent('download', { timeout: 20000 });
    const fname = `GBC週報_部長会_${new Date().toISOString().slice(0, 10)}.xlsx`;
    const dest = path.join(DOWNLOAD_DIR, fname);
    await download.saveAs(dest);
    console.log('保存しました:', dest);
    fs.writeFileSync(STATE_FILE, JSON.stringify({ awaitingCode: false, downloadedFile: dest, ts: Date.now() }));
  } catch (e) {
    console.log('ダウンロードイベントを検知できませんでした:', e.message);
    console.log('手動確認が必要かもしれません。');
  }

  process.exit(0);
})();
