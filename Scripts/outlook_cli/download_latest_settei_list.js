#!/usr/bin/env node
// Finds the newest non-reply "受発注設定リスト" email (from 青山さん) and
// downloads its .xlsx attachment. Walks search results from the top until
// it finds one whose subject is a fresh original (not "Re:"/"RE:") and that
// actually has an .xlsx attachment, so a reply-thread message with no
// attachment doesn't get picked by mistake.
const { connect, ensureLoggedIn, search, clearSearch, listMessageItems, readOpenMessage, MAIL_URL } = require('./lib');

(async () => {
  const savePath = process.argv[2];
  if (!savePath) {
    console.error('使い方: node download_latest_settei_list.js "<保存先パス>"');
    process.exit(1);
  }

  const { page } = await connect();
  await ensureLoggedIn(page);
  // This script reuses whatever Outlook tab is already open (shared bot
  // browser), which may be left mid-context-menu or mid-search from a
  // previous run/other script. Force a clean slate before searching —
  // observed flaky "message list index out of range" and stale-download
  // errors on 2026-09-02 that a fresh reload reliably clears.
  await page.keyboard.press('Escape').catch(() => {});
  await page.goto(MAIL_URL, { waitUntil: 'domcontentloaded' });
  await ensureLoggedIn(page);
  await page.waitForTimeout(2000);

  let items = [];
  for (let attempt = 0; attempt < 3 && items.length === 0; attempt++) {
    await search(page, '受発注設定リスト');
    await page.waitForTimeout(1500);
    items = await listMessageItems(page);
    if (items.length === 0) {
      await clearSearch(page).catch(() => {});
      await page.waitForTimeout(1000);
    }
  }
  if (items.length === 0) {
    console.error('エラー: 検索結果が取得できませんでした(3回リトライ後も0件)。');
    process.exit(1);
  }

  const resultCount = Math.min(items.length, 10);
  for (let i = 0; i < resultCount; i++) {
    // Re-run the search fresh before every click, not just re-fetch the
    // listbox — opening a message can drop Outlook out of "search results"
    // mode back to the plain folder view, which silently emptied the
    // listbox on later iterations (2026-09-02 flakiness). Re-searching each
    // time is slower but reliable.
    let freshItems = [];
    for (let retry = 0; freshItems.length <= i && retry < 3; retry++) {
      if (retry > 0) await page.waitForTimeout(1000);
      await search(page, '受発注設定リスト');
      await page.waitForTimeout(1200);
      freshItems = await listMessageItems(page);
    }
    if (freshItems.length <= i) {
      console.error(`エラー: メッセージ一覧の再取得に失敗しました(index ${i}, 現在${freshItems.length}件)。`);
      process.exit(1);
    }
    await freshItems[i].click();
    await page.waitForTimeout(1500);
    const { subject } = await readOpenMessage(page);
    if (/^(re|fw)[:：]/i.test(subject.trim())) continue;

    const chip = page.locator('[aria-label*=".xlsx"]').first();
    if (await chip.count() === 0) continue;

    await chip.click({ button: 'right' });
    await page.waitForTimeout(500);
    const menuItem = page.getByRole('menuitem', { name: 'ダウンロード' });
    if (await menuItem.count() === 0) {
      await page.keyboard.press('Escape');
      continue;
    }
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 10000 }),
      menuItem.click(),
    ]);
    await download.saveAs(savePath);
    console.log(JSON.stringify({ subject, index: i, saved: savePath }));
    process.exit(0);
  }
  console.error('エラー: 添付付きの受発注設定リストメールが見つかりませんでした(上位10件を確認)');
  process.exit(1);
})().catch(err => { console.error('エラー:', err.message); process.exit(1); });
