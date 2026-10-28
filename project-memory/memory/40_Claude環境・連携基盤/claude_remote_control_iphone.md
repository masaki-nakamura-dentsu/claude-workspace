---
name: claude-remote-control-iphone
description: iPhoneのClaudeアプリから会社Mac/個人MacのClaude CodeをRemote Controlで操作する設定(2026-10-20)
metadata:
  type: project
---
- 会社Mac(d14461): `claude`はVS Code拡張同梱バイナリのみ→ `~/.local/bin/claude` ラッパー(最新拡張のnative-binaryをexec)を作成。
- 自動起動: launchd `~/Library/LaunchAgents/com.nakamura.claude-rc.plist`(RunAtLoad+KeepAlive, Throttle60s) → `~/ClaudeRC/run_rc.sh`(Dropbox作業フォルダでcaffeinate -is claude remote-control)。ログ `~/ClaudeRC/rc.log`。
- 同フォルダで手動`claude rc`が動いていると「already served」で終了→手動側を止めればlaunchdが引き継ぐ。
- 個人Mac(maxakisan): ホームでは`claude rc`不可(trust不保存)。作業フォルダで一度`claude`→trust承認後に実行。launchd化も2026-10-20完了(task-020、中村さん確認済み)。
関連: [[claude_relay_system]] [[reference_mac_naming]]

## 個人Mac(ICPTokyo2022)設定済み 2026-10-20
- ~/ClaudeRC/run_rc.sh(caffeinate -is ~/.npm-global/bin/claude remote-control、作業フォルダ=~/ICPTokyo2022 Dropbox/中村正樹)
- launchd com.nakamura.claude-rc(RunAtLoad+KeepAlive, Throttle60, log ~/ClaudeRC/rc.log)。auto modeでは登録拒否→中村さんがターミナルで実行。iPhone接続確認OK。
- 再起動: launchctl kickstart -k gui/$(id -u)/com.nakamura.claude-rc
