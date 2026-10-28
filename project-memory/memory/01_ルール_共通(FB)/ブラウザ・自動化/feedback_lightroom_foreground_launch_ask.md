---
name: feedback-lightroom-foreground-launch-ask
description: Lightroom等を前面化する必要があるテストは事前に一言確認→許可後は自動で進めてよい(2026-09-25)
metadata:
  type: feedback
---
Lightroomは`open -g`だと起動途中で止まるため、テストには前面化が必須。2026-09-25、ユーザーが動画視聴中だったのでAskUserQuestion+Teams通知で確認したところ「前面に出してOK」と即答された。

**Why:** フォーカス奪取禁止ルール([[feedback_browser_automation_no_focus_steal]])があるため無断前面化は不可。ただし短時間・目的明確なら許可は得やすい。
**How to apply:** 前面化が必要と分かった時点で一度だけ確認し、許可後はまとめて検証を終える（前面化の回数を最小化）。スクショ前に画面がユーザー使用中でないかも意識する。関連: [[lightroom_cli_setup]]
