---
name: company-mac-startup-automation
description: 会社Mac(d14461)の起動時自動処理(caffeinate -dis常駐・Teams始業ボタン・smtkin登録)の構成と未完部分
metadata:
  type: project
---
2026-10-23設定。会社Macの起動時にやること。
- `~/Library/LaunchAgents/com.nakamura.caffeinate.plist`: `caffeinate -dis` を RunAtLoad+KeepAlive で常駐(稼働確認済み)。
- `com.nakamura.startupworkreg.plist` → `~/StartupWorkReg/run.sh`(RunAtLoad、平日のみ、1日1回、stampは `state/`)。ネット待ち→9226ブラウザ確認→社内判定(SSID ew-hq / ルーター10.110.x なら出社、他は在宅。ユーザー指定)→`teams_start.js`でTeams「SKB/1-1. 出退勤報告用」の本日カードの始業ボタン(在宅/出社)を押す→Teams webhook通知。
- smtkin(スマート勤務)登録は無人`claude -p`が必要で、auto modeが「Create Unsafe Agents」で拒否→`smtkin_step.sh`/`smtkin_prompt.md`はユーザーがターミナルで設置する([[feedback_auto_mode_unattended_agent_launchd]])。run.shは `smtkin_step.sh` があれば呼ぶ。
**Why:** 起動後の定型作業の自動化。**How to apply:** 時刻・判定を変えるときは run.sh を編集。plistは未load(即実行で今日の始業が押されるため)。ログ `~/StartupWorkReg/logs/`。関連 [[smart_kinmu_personal_registration]] [[powerautomate_attendance_summary_project]]
