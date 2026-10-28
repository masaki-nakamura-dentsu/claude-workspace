#!/bin/bash
# 他のMacから届いた指示を claude -p で実行する常駐プロセス(2026-10-19)。launchd com.nakamura.macdirect が KeepAlive で動かす。
# 15秒ごとに .claude-sync/claude_relay/direct/<自分>/pending/*.md を見て、1件ずつ実行する。
#   結果: done/<ID>.result.md(返答全文)、指示文は done/<ID>.md に移す。開始・完了・失敗はTeamsへ通知
#   権限: claude -p --permission-mode auto(ふだんの対話と同じ。auto modeが拒否する操作は実行されず、結果にその旨が出る)
#   時間切れ: 1件あたり MACDIRECT_TIMEOUT 秒(既定 3600)
set -u
WS="$(cd "$(dirname "$0")/../../.." && pwd)"
case "$(whoami)" in d14461) ME=company_mac;; maxakisan) ME=personal_mac;; *) ME=$(whoami);; esac
Q="$WS/.claude-sync/claude_relay/direct/$ME"
NOTIFY="$WS/.claude-sync/Scripts/notify/teams_notify.py"
LOGDIR="$HOME/MacDirect"; mkdir -p "$LOGDIR" "$Q/pending" "$Q/running" "$Q/done"
CLAUDE="${CLAUDE_BIN:-$(command -v claude)}"
TIMEOUT="${MACDIRECT_TIMEOUT:-3600}"
notify() { python3 "$NOTIFY" "$1" "Mac間指示" "$2" --detail "${3:-}" >/dev/null 2>&1 || true; }
[ -x "$CLAUDE" ] || { echo "claude が見つからない"; notify ERROR "claudeが見つからない($ME)"; sleep 300; exit 1; }

# 前回途中で落ちたものは pending に戻す
for f in "$Q/running"/*.md; do [ -e "$f" ] && mv "$f" "$Q/pending/"; done

while true; do
  for f in "$Q/pending"/*.md; do
    [ -e "$f" ] || continue
    ID=$(basename "$f" .md)
    mv "$f" "$Q/running/$ID.md" || continue
    BODY=$(sed '1,/^---$/d' "$Q/running/$ID.md")
    echo "$(date '+%F %T') start $ID" >> "$LOGDIR/worker.log"
    notify INFO "受付 $ID" "$(echo "$BODY" | head -c 200 | tr '\n' ' ')"
    PROMPT="【別のMacから届いた指示(依頼ID $ID)】
$BODY

(このセッションが終わると、ここから起動した子プロセスも止まります。10分を超えそうな処理は、nohupではなく
 perl -MPOSIX -e 'POSIX::setsid(); exec @ARGV' <コマンド> </dev/null >ログ 2>&1 & のように別セッションで起動し、ログの場所を報告してください。
 終わったら、何をしたか・結果・残っていることを簡潔に報告してください。Teams通知はこの仕組みが送るので不要です。)"
    (cd "$WS" && perl -e 'alarm shift; exec @ARGV' "$TIMEOUT" "$CLAUDE" -p --permission-mode auto "$PROMPT") \
      > "$Q/running/$ID.out" 2>> "$LOGDIR/worker.log"
    RC=$?
    { echo "ID: $ID"; echo "Finished: $(date '+%F %T')"; echo "ExitCode: $RC"; echo "---"; cat "$Q/running/$ID.out"; } > "$Q/done/$ID.result.md"
    mv "$Q/running/$ID.md" "$Q/done/$ID.md"; rm -f "$Q/running/$ID.out"
    echo "$(date '+%F %T') end $ID rc=$RC" >> "$LOGDIR/worker.log"
    if [ $RC = 0 ]; then notify DONE "完了 $ID" "$(sed '1,/^---$/d' "$Q/done/$ID.result.md" | head -c 300 | tr '\n' ' ')"
    else notify WARN "失敗 $ID(rc=$RC)" "結果: $Q/done/$ID.result.md"; fi
  done
  sleep 15
done
