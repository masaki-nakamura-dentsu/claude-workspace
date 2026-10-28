#!/bin/bash
# 別のMacのClaude Codeへ指示を直接送る(2026-10-19)。受け手側で worker.sh が常駐していれば、数十秒以内に claude -p で実行される。
#   send.sh "指示文"                         個人Macへ送る(会社Macから)。依頼IDを表示して終わる
#   send.sh --wait "指示文"                   結果が返るまで待って表示(既定で最大60分)
#   send.sh --to company_mac "指示文"         宛先を指定(personal_mac / company_mac)
#   send.sh --result <依頼ID>                 結果を表示
# 指示文の受け渡しは Dropbox の .claude-sync/claude_relay/direct/<宛先>/ (pending → running → done)。
set -u
WS="$(cd "$(dirname "$0")/../../.." && pwd)"
BASE="$WS/.claude-sync/claude_relay/direct"
case "$(whoami)" in d14461) ME=company_mac; TO=personal_mac;; maxakisan) ME=personal_mac; TO=company_mac;; *) ME=$(whoami); TO=personal_mac;; esac
WAIT=0; WAIT_MIN=60
while [ $# -gt 0 ]; do
  case $1 in
    --to) TO=$2; shift 2;;
    --wait) WAIT=1; shift;;
    --wait-min) WAIT=1; WAIT_MIN=$2; shift 2;;
    --result) cat "$BASE"/*/done/"$2".result.md 2>/dev/null || ls "$BASE"/*/*/"$2"* 2>/dev/null || echo "見つかりません: $2"; exit 0;;
    *) break;;
  esac
done
[ $# -ge 1 ] || { sed -n 2,8p "$0"; exit 1; }
ID="$(date +%Y%m%d-%H%M%S)-$ME"
mkdir -p "$BASE/$TO/pending" "$BASE/$TO/running" "$BASE/$TO/done"
TMP="$BASE/$TO/pending/.$ID.tmp"
{ echo "From: $ME"; echo "Created: $(date '+%F %T')"; echo "---"; echo "$*"; } > "$TMP"
mv "$TMP" "$BASE/$TO/pending/$ID.md"
echo "送信しました: $ID → $TO"
[ $WAIT = 1 ] || exit 0
for i in $(seq 1 $((WAIT_MIN * 6))); do
  [ -f "$BASE/$TO/done/$ID.result.md" ] && { cat "$BASE/$TO/done/$ID.result.md"; exit 0; }
  sleep 10
done
echo "まだ終わっていません(後で: send.sh --result $ID)"; exit 2
