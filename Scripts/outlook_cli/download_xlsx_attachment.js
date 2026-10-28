#!/usr/bin/env node
// Generic attachment downloader: searches the inbox, opens the Nth result,
// finds the first attachment chip matching a filename substring, and saves
// it via the right-click "ダウンロード" menu item.
//
// Usage: node download_xlsx_attachment.js "<search query>" <result index> "<save path>" ["<filename substring>"]
// Default filename substring is ".xlsx" (first Excel attachment found).
const { connect, ensureLoggedIn, search, openMessageAt } = require('./lib');

(async () => {
  const query = process.argv[2];
  const index = parseInt(process.argv[3] || '0', 10);
  const savePath = process.argv[4];
  const nameSubstr = process.argv[5] || '.xlsx';

  if (!query || !savePath) {
    console.error('使い方: node download_xlsx_attachment.js "<検索語>" <index> "<保存先パス>" ["<部分一致するファイル名>"]');
    process.exit(1);
  }

  const { page } = await connect();
  await ensureLoggedIn(page);
  await search(page, query);
  await openMessageAt(page, index);
  await page.waitForTimeout(1500);

  const chip = page.locator(`[aria-label*="${nameSubstr}"]`).first();
  await chip.waitFor({ timeout: 10000 });
  await chip.click({ button: 'right' });
  await page.waitForTimeout(500);

  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 10000 }),
    page.getByRole('menuitem', { name: 'ダウンロード' }).click(),
  ]);
  await download.saveAs(savePath);
  console.log('saved:', savePath);
  process.exit(0);
})().catch(err => { console.error('エラー:', err.message); process.exit(1); });
