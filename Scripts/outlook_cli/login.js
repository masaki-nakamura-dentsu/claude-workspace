#!/usr/bin/env node
const { connect, ensureLoggedIn } = require('./lib');

(async () => {
  const { page } = await connect();
  try {
    await ensureLoggedIn(page);
    console.log('ログイン済みです。');
  } catch (err) {
    console.log(err.message);
    console.log('開いたブラウザ(共有ボットブラウザ)で手動ログインしてください。完了後もう一度 `outlook login` を実行して確認できます。');
  }
  process.exit(0);
})().catch((err) => {
  console.error('エラー:', err.message);
  process.exit(1);
});
