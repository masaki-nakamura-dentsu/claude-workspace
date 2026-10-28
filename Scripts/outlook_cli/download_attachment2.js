#!/usr/bin/env node
const { connect, ensureLoggedIn, search, openMessageAt } = require('./lib');
const path = require('path');

(async () => {
  const query = process.argv[2];
  const index = parseInt(process.argv[3] || '0', 10);
  const outDir = process.argv[4] || process.env.HOME + '/Downloads';

  const { page } = await connect();
  await ensureLoggedIn(page);
  await search(page, query);
  await openMessageAt(page, index);
  await page.waitForTimeout(1500);

  const chip = page.locator('[aria-label*="GBC案件Items_Errors.csv"]').first();
  await chip.waitFor({ timeout: 10000 });

  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 15000 }),
    chip.click(),
  ]);
  const suggested = download.suggestedFilename();
  const dest = path.join(outDir, suggested);
  await download.saveAs(dest);
  console.log('saved to:', dest);
  process.exit(0);
})().catch(err => { console.error('エラー:', err.message); process.exit(1); });
