#!/usr/bin/env node
const fs = require('fs');
const {
  connect, ensureLoggedIn, clearSearch, openCompose, fillRecipientField,
  fillSubject, fillBody, attachFiles, clickSend, discardCompose,
} = require('./lib');

function parseArgs(argv) {
  const args = { to: [], cc: [], bcc: [], subject: null, attach: [], dryRun: false, bodyParts: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--to') args.to.push(argv[++i]);
    else if (a === '--cc') args.cc.push(argv[++i]);
    else if (a === '--bcc') args.bcc.push(argv[++i]);
    else if (a === '--subject') args.subject = argv[++i];
    else if (a === '--attach') args.attach.push(argv[++i]);
    else if (a === '--dry-run') args.dryRun = true;
    else args.bodyParts.push(a);
  }
  return args;
}

function usage() {
  console.error('使い方:');
  console.error('  outlook send --to "a@example.com" [--to "b@example.com"] [--cc "c@example.com"] \\');
  console.error('    --subject "件名" [--attach /path/to/file] [--dry-run] "本文"');
  console.error('本文は引数の代わりに標準入力からも渡せます。--to は複数回指定可。');
}

(async () => {
  const args = parseArgs(process.argv.slice(2));
  if (args.to.length === 0 || !args.subject) {
    usage();
    process.exit(1);
  }
  for (const p of args.attach) {
    if (!fs.existsSync(p)) {
      console.error(`添付ファイルが見つかりません: ${p}`);
      process.exit(1);
    }
  }

  let body = args.bodyParts.join(' ');
  if (!body) body = fs.readFileSync(0, 'utf8').trimEnd();
  if (!body) {
    console.error('本文が空です');
    process.exit(1);
  }

  const { page } = await connect();
  await ensureLoggedIn(page);
  await clearSearch(page);
  await openCompose(page);

  await fillRecipientField(page, '宛先', args.to);
  await fillRecipientField(page, 'CC', args.cc);
  await fillRecipientField(page, 'BCC', args.bcc);
  await fillSubject(page, args.subject);
  await fillBody(page, body);
  if (args.attach.length > 0) await attachFiles(page, args.attach);

  if (args.dryRun) {
    console.log('[dry-run] 宛先:', args.to.join(', '));
    if (args.cc.length) console.log('[dry-run] CC:', args.cc.join(', '));
    console.log('[dry-run] 件名:', args.subject);
    console.log('[dry-run] 添付:', args.attach.join(', ') || '(なし)');
    console.log('[dry-run] 本文・宛先を入力欄に反映しました(送信はしていません)。下書きを破棄します。');
    await discardCompose(page);
    process.exit(0);
  }

  await clickSend(page);
  console.log(`送信しました → 宛先: ${args.to.join(', ')} / 件名: ${args.subject}`);
  process.exit(0);
})().catch((err) => {
  console.error('エラー:', err.message);
  process.exit(1);
});
