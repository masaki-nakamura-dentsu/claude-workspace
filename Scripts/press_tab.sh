#!/bin/bash
# 30秒ごとにTabキーを送信する。停止は Ctrl+C。
# 初回実行時、ターミナル(またはVSCode)に「システム設定 > プライバシーとセキュリティ > アクセシビリティ」の許可が必要。
INTERVAL=${1:-30}
echo "Tabキーを${INTERVAL}秒ごとに送信します(Ctrl+Cで停止)"
while true; do
  sleep "$INTERVAL"
  osascript -e 'tell application "System Events" to key code 48'
  echo "$(date '+%H:%M:%S') Tab送信"
done
