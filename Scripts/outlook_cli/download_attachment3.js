#!/usr/bin/env node
const { connect, ensureLoggedIn, search, openMessageAt } = require('./lib');
const path = require('path');

(async () => {
  const query = process.argv[2];
  const index = parseInt(process.argv[3] || '0', 10);

  const { page } = await connect();
  await ensureLoggedIn(page);
  await search(page, query);
  await openMessageAt(page, index);
  await page.waitForTimeout(1500);

  const chip = page.locator('[aria-label*="GBC案件Items_Errors.csv"]').first();
  await chip.waitFor({ timeout: 10000 });
  await chip.click();
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/outlook_attach_click.png' });

  const all = await page.locator('[aria-label]').evaluateAll(els => els.map(e => e.getAttribute('aria-label')).filter(Boolean));
  console.log(JSON.stringify(all.filter(a => /download|ダウンロード|保存/i.test(a)), null, 2));
  process.exit(0);
})().catch(err => { console.error('エラー:', err.message); process.exit(1); });
