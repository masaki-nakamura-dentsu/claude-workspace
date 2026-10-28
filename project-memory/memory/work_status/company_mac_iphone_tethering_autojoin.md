# 会社Mac iPhoneテザリング自動接続

## 2026-08-26T10:20:00+09:00
Status: done
What: 会社MacがiPhoneテザリング(SSID「OfficeのiPhone15 Masaki」)を見つけられない問題に対応。Wi-Fi優先ネットワーク編集はJamf管理プロファイルで管理者専用にロックされておりCLI/GUIとも変更不可と判明。回避策として`networksetup -setairportnetwork`(管理者権限不要)でSSID/パスワードを直接指定して接続するスクリプトを作成し、`/Users/d14461/Scripts/network/hotspot_autojoin.sh`に配置。Wi-Fi未接続時のみ動作、電源オフなら先にオンにする。30秒間隔のLaunchAgent(`~/Library/LaunchAgents/com.nakamura.hotspotautojoin.plist`)で常時自動実行するよう登録済み。
Next: —
