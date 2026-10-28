// Node用: const { notifyTeams } = require('<このファイル>'); notifyTeams('ERROR', 'ジョブ名', '要約', { detail, log });
// 文言ルールは NOTIFY_RULES.md。中身は teams_notify.py を呼ぶだけ(execFileSyncなのでシェル展開の心配なし)。
const { execFileSync } = require('child_process');
const path = require('path');

function notifyTeams(level, job, summary, opts = {}) {
  const args = [path.join(__dirname, 'teams_notify.py'), level, job, summary,
    '--detail', String(opts.detail || ''), '--log', String(opts.log || ''),
    '--script', String(opts.script || (require.main && require.main.filename) || '')];
  if (opts.noFix) args.push('--no-fix');
  try {
    execFileSync('python3', args, { stdio: 'ignore', timeout: 90000 });
    return true;
  } catch (e) {
    return false;
  }
}

module.exports = { notifyTeams };
