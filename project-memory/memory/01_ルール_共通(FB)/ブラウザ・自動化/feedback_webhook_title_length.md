---
name: feedback_webhook_title_length
description: Teams Webhookの件名は28字以内。長いと31字目以降が表示されない。入りきらない分は本文へ回す(10/17指摘)
metadata:
  type: feedback
---
2026-10-17、「[INFO] アレココ要約(ローカルLLM): 開始: 残り257件/全426件」が「…開始: 残り2」までしか表示されず、中村さんから「タイトルが長すぎると表示されない。他のWebhookも同様。文字数に注意して」「入りきらない部分は本文に回して良い」と指摘された。

**Why:** Teamsのカード(Power Automateフロー経由)は件名の表示が約30字で切れる。NOTIFY_RULES.mdは要約40字以内としていて、件名全体の長さを見ていなかった。
**How to apply:** 件名は `[LEVEL] ジョブ名: 要約` で**全体28字以内**(ジョブ名10字以内、要約は15字前後)。詳しいことは本文に書く。共通送信口 teams_notify.py が自動で縮める(TITLE_MAX=28、JOB_MAX=10、長い既存ジョブ名は SHORT_JOB の短縮名、縮めたときは本文の先頭に「件名全文: …」)。対話セッションの [DONE]/[WAIT] 通知も同じ長さを守る。送信口を通らない経路(PAのクラウドフロー、Windowsの Send-TeamsMessage、スクリプト内のcurl直送のフォールバック)には自動の縮めが効かないので、文言を短く書く。[[webhook_autofix_project]]
- 2026-10-17 中村さんがテスト通知で表示を確認(28字の件名+本文に件名全文)。TITLE_MAX=28で問題なし。
