#!/bin/bash
# 個人Windows(自宅 192.168.0.11 / tailnet desktop-ryzen5950)の電源操作。個人Macから使う。
# 自宅でも外出先でも同じように使える(ssh は win-home → だめなら win-ts(Tailscale) の順に試す)。
#   win_power.sh status            起動しているか + つながる経路 + Ollamaの応答
#   win_power.sh wake              起動(ラズパイ中継からWake-on-LAN)→ sshが通るまで待つ → Ollamaを起動。完全停止から約70秒
#   win_power.sh ollama            Ollamaだけ起動(Windowsは起動済みのとき)
#   win_power.sh shutdown [秒]     シャットダウン(既定60秒後。Windows画面に予告が出る)。Ollamaで処理中なら止めない
#   win_power.sh shutdown-now      Ollamaの処理中でもすぐシャットダウン
#   win_power.sh cancel            予約したシャットダウンを取り消す
# 2026-10-17 作成、同日 win_wake_full.sh を統合。Windows側は OpenSSH Server(鍵認証のみ、LAN と Tailscale からだけ受付)。
# ~/.ssh/config: win-home(192.168.0.11) / win-ts(desktop-ryzen5950)、どちらも User maxakisan。
# Windows側Tailscaleは unattended(ログオン不要)。Ollamaはログオンしないと自動で上がらないので wake で起動する。
set -u
RELAY="http://100.96.219.107:8090"   # ラズパイのWOL中継(Tailscale内のみ)
OLLAMA_EXE='C:\Users\maxak\AppData\Local\Programs\Ollama\ollama.exe'

pick_host() {  # sshが通る経路を返す
  local h
  for h in win-home win-ts; do
    ssh -o ConnectTimeout=4 -o BatchMode=yes "$h" hostname >/dev/null 2>&1 && { echo "$h"; return 0; }
  done
  return 1
}

ollama_url() {  # 届くほうのOllama URL
  local u
  for u in http://192.168.0.11:11434 http://desktop-ryzen5950:11434; do
    [ "$(curl -s -m 4 -o /dev/null -w '%{http_code}' "$u/api/tags")" = 200 ] && { echo "$u"; return 0; }
  done
  return 1
}

status() {
  echo "電源: $(curl -s -m 8 "$RELAY/status/windows")"
  local h u
  h=$(pick_host) && echo "ssh: $h" || echo "ssh: つながりません"
  u=$(ollama_url) && echo "Ollama: 応答あり ($u)" || echo "Ollama: 応答なし"
}

start_ollama() {  # ssh切断で子プロセスが落ちないよう、WMI(Win32_Process.Create)で切り離して起動する
  local host=$1 u enc i
  u=$(ollama_url) && { echo "Ollama: すでに起動中 ($u)"; return 0; }
  enc=$(python3 - "$OLLAMA_EXE" <<'PY'
import base64,sys
exe=sys.argv[1]
ps=("$c='cmd.exe /c \"set OLLAMA_HOST=0.0.0.0:11434&& set OLLAMA_MODELS=D:\\ollama_models&& " + exe + " serve\"'\n"
    "if (-not (Get-Process -Name ollama -ErrorAction SilentlyContinue)) { (Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$c}).ReturnValue | Out-Null }")
print(base64.b64encode(ps.encode('utf-16le')).decode())
PY
)
  ssh -o BatchMode=yes "$host" "powershell -NoProfile -EncodedCommand $enc" >/dev/null 2>&1
  for i in $(seq 1 12); do
    sleep 5
    u=$(ollama_url) && { echo "Ollama: 起動しました ($u)"; return 0; }
  done
  echo "NG: Ollamaが応答しません"; return 2
}

wake() {
  local h i
  if h=$(pick_host); then
    echo "すでに起動中: $h"
  else
    echo "起動パケット送信: $(curl -s -m 8 "$RELAY/wake/windows")"
    for i in $(seq 1 36); do
      sleep 5
      h=$(pick_host) && break
    done
    [ -z "${h:-}" ] && { echo "NG: 3分待ってもsshが通りません(BIOSのErP設定などを確認)"; return 1; }
    echo "起動確認: $h ($((i*5))秒)"
  fi
  start_ollama "$h"
}

ollama_busy() {  # 読み込み中のモデルがあり、直近で使われていれば処理中とみなす
  local u ps
  u=$(ollama_url) || return 1
  ps=$(curl -s -m 5 "$u/api/ps") || return 1
  python3 - "$ps" <<'PY'
import json,sys
from datetime import datetime,timezone
m=json.loads(sys.argv[1]).get("models",[])
# expires_at は最後の利用から既定5分後。残りが4分以上 = 1分以内に使われた
busy=any((datetime.fromisoformat(x["expires_at"].replace("Z","+00:00"))-datetime.now(timezone.utc)).total_seconds()>240 for x in m if x.get("expires_at"))
sys.exit(0 if busy else 1)
PY
}

need_host() { HOST=$(pick_host) || { echo "NG: sshがつながりません(Windowsが停止中かも。status で確認)"; exit 1; }; }

case "${1:-status}" in
  status) status ;;
  wake) wake ;;
  ollama) need_host; start_ollama "$HOST" ;;
  shutdown|shutdown-now)
    delay=${2:-60}; [ "$1" = shutdown-now ] && delay=0
    if [ "$1" = shutdown ] && ollama_busy; then
      echo "Ollamaが直近1分以内に使われています(処理中の可能性)。止める場合は shutdown-now を使ってください。"; exit 2
    fi
    need_host
    ssh -o BatchMode=yes "$HOST" "shutdown /s /t $delay /c \"個人Macからのシャットダウン(${delay}秒後)\"" && echo "シャットダウンを予約しました(${delay}秒後、経路 $HOST)" ;;
  cancel) need_host; ssh -o BatchMode=yes "$HOST" "shutdown /a" && echo "取り消しました" ;;
  *) sed -n 2,12p "$0"; exit 1 ;;
esac
