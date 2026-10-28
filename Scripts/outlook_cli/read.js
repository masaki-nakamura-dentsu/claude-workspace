#!/usr/bin/env node
const { connect, ensureLoggedIn, search, clearSearch, openMessageAt, readOpenMessage } = require('./lib');

function parseArgs(argv) {
  const args = { index: null, query: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--search') args.query = argv[++i];
    else if (args.index === null) args.index = parseInt(a, 10);
  }
  return args;
}

(async () => {
  const args = parseArgs(process.argv.slice(2));
  if (args.index === null || Number.isNaN(args.index)) {
    console.error('使い方: outlook read <index> [--search "検索文字列"]');
    console.error('index は `outlook list` の [番号] に対応します。');
    process.exit(1);
  }

  const { page } = await connect();
  await ensureLoggedIn(page);

  if (args.query) await search(page, args.query);
  else await clearSearch(page);

  await openMessageAt(page, args.index);
  const msg = await readOpenMessage(page);
  console.log(`件名: ${msg.subject}`);
  console.log(`差出人: ${msg.from}`);
  console.log(`日時: ${msg.date}`);
  console.log('---');
  console.log(msg.body || '(本文を取得できませんでした)');
  process.exit(0);
})().catch((err) => {
  console.error('エラー:', err.message);
  process.exit(1);
});
