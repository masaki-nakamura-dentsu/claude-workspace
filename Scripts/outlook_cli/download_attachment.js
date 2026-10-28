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

  // Attachments usually render as clickable chips in the reading pane.
  const chips = page.locator('[role="button"][aria-label*="csv"], [role="button"][aria-label*="CSV"], [role="listitem"][aria-label*="csv" i]');
  const count = await chips.count();
  console.error('attachment chip candidates:', count);
  if (count === 0) {
    // fallback: dump all aria-labels containing "添付" or file-looking names
    const all = await page.locator('[aria-label]').evaluateAll(els => els.map(e => e.getAttribute('aria-label')).filter(Boolean));
    console.error('all aria-labels sample:', all.filter(a => /csv|attach|添付/i.test(a)).slice(0, 20));
    process.exit(1);
  }

  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 15000 }),
    chips.first().click(),
  ]);
  const suggested = download.suggestedFilename();
  const dest = path.join(outDir, suggested);
  await download.saveAs(dest);
  console.log('saved to:', dest);
  process.exit(0);
})().catch(err => { console.error('エラー:', err.message); process.exit(1); });
