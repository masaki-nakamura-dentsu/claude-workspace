#!/bin/bash
# 個人Windows(自宅 192.168.0.11)の電源操作。個人Macから使う(SSH鍵 ~/.ssh/id_ed25519_windows、~/.ssh/config の Host win-home)。
#   win_power.sh status            起動しているか(ラズパイ中継のping結果)
#   win_power.sh wake              起動(ラズパイ中継からWake-on-LAN。完全停止からは約75秒)
#   win_power.sh shutdown [秒]     シャットダウン(既定60秒後。Windows画面に予告が出る)。Ollamaで処理中なら止めない
#   win_power.sh shutdown-now      Ollamaの処理中でもすぐシャットダウン
#   win_power.sh cancel            予約したシャットダウンを取り消す
# 2026-10-17 作成。Windows側は OpenSSH Server(鍵認証のみ、LAN と Tailscale からだけ受付)。
set -u
RELAY="http://100.96.219.107:8090"   # ラズパイのWOL中継(Tailscale内のみ)
HOST="win-home"
OLLAMA="http://192.168.0.11:11434"

status() { curl -s -m 8 "$RELAY/status/windows"; echo; }

ollama_busy() {  # 読み込み中のモデルがあり、直近で使われていれば処理中とみなす
  local ps; ps=$(curl -s -m 5 "$OLLAMA/api/ps") || return 1
  python3 - "$ps" <<'PY'
import json,sys
from datetime import datetime,timezone
m=json.loads(sys.argv[1]).get("models",[])
# expires_at は最後の利用から既定5分後。残りが4分以上 = 1分以内に使われた
busy=any((datetime.fromisoformat(x["expires_at"].replace("Z","+00:00"))-datetime.now(timezone.utc)).total_seconds()>240 for x in m if x.get("expires_at"))
sys.exit(0 if busy else 1)
PY
}

case "${1:-status}" in
  status) status ;;
  wake) curl -s -m 8 "$RELAY/wake/windows"; echo ;;
  shutdown|shutdown-now)
    delay=${2:-60}; [ "$1" = shutdown-now ] && delay=0
    if [ "$1" = shutdown ] && ollama_busy; then
      echo "Ollamaが直近1分以内に使われています(処理中の可能性)。止める場合は shutdown-now を使ってください。"; exit 2
    fi
    ssh -o BatchMode=yes "$HOST" "shutdown /s /t $delay /c \"個人Macからのシャットダウン(${delay}秒後)\"" && echo "シャットダウンを予約しました(${delay}秒後)" ;;
  cancel) ssh -o BatchMode=yes "$HOST" "shutdown /a" && echo "取り消しました" ;;
  *) sed -n 2,9p "$0"; exit 1 ;;
esac
