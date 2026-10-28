#!/usr/bin/env node
const { connect, ensureLoggedIn, search, clearSearch, listMessageItems } = require('./lib');

function parseArgs(argv) {
  const args = { query: null, limit: 15 };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--limit') args.limit = parseInt(argv[++i], 10);
    else rest.push(a);
  }
  args.query = rest.join(' ') || null;
  return args;
}

(async () => {
  const args = parseArgs(process.argv.slice(2));
  const { page } = await connect();
  await ensureLoggedIn(page);

  if (args.query) {
    await search(page, args.query);
  } else {
    await clearSearch(page);
  }

  const items = await listMessageItems(page);
  const limit = Math.min(items.length, args.limit);
  if (limit === 0) {
    console.log('該当するメッセージが見つかりませんでした。');
  }
  for (let i = 0; i < limit; i++) {
    const text = (await items[i].innerText().catch(() => '')).replace(/\n/g, ' | ').trim();
    console.log(`[${i}] ${text.slice(0, 160)}`);
  }
  console.log(`\n(${items.length}件中 ${limit}件表示。詳細は \`outlook read <index>\` ${args.query ? `--search "${args.query}"` : ''} で開けます)`);
  process.exit(0);
})().catch((err) => {
  console.error('エラー:', err.message);
  process.exit(1);
});
