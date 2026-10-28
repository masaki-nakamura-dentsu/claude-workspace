---
name: feedback-bake-error-notifications-into-automation
description: 無人自動化スクリプト(launchd常駐/定期実行)を作る・保守する際は、失敗パス自体にTeams Webhook通知を埋め込む。Claudeセッションが見ていなくても気づけるようにする
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f5909fbc-7dfe-4330-a401-f6421f8ee421
  modified: 2026-09-07T00:36:34.594Z
---

無人で動く自動化スクリプト(launchdジョブ、常駐デーモン、定期実行タスク)を新規作成・修正する際は、**失敗を検知する箇所(例外ハンドラ、ログイン失敗時のabort分岐など)そのものに[[teams_webhook_powerautomate]]のWebhook通知を埋め込む**こと。

**Why**: 2026-09-07、GBC AI業務活用PJの`teams_daemon.py`(Teamsメッセージ収集デーモン)と`weekly_ai_digest.py`(週次ダイジェスト投稿)が、共有ボットブラウザのTeamsログインセッション切れにより3日間サイレントに停止していた。ユーザーが自発的に「動いていないようだが確認して」と聞いてくれるまで誰も気づかなかった。ユーザーからの明示的フィードバック: 「そういうエラーが起きている時は必ずWebhookやTeamsでの自分への投稿で知らせて」。

これは既存の[[work_status_protocol]]的なClaudeセッション内の振る舞い(セッションが生きている間だけ気づける)とは別レイヤーの話——**Claudeセッションが一切開いていない状態でも、スクリプト自身が自分の失敗をユーザーに知らせる**必要がある、という要求。Power Automate Webhookはローカルの認証状態(Teamsブラウザセッション等)に依存しない独立経路なので、「Teamsセッションが壊れて連絡できない」という状況そのものでも確実に届く。

**How to apply**:
- 新規/既存の無人スクリプトに例外ハンドラや「N分待ってダメならabort」的な分岐を書くとき、必ずそこに`notify_teams_webhook(title, message)`相当の呼び出しを追加する(実装例: `~/TeamsExport/teams_daemon.py`のログイン失敗時、`~/TeamsExport/scripts/weekly_ai_digest.py`の`main()`を包む`try/except`——いずれも2026-09-07に追加済み)。
- Webhook自体の失敗(ネットワーク不通等)でスクリプト本体の異常終了処理を妨げないよう、通知呼び出し自体は`try/except: pass`で囲み、必ず本来のraise/exit処理を続行させる。
- 対象は今回のTeams関連2スクリプトに限らない——[[cas_csv_download_automation]]、[[salesforce_report_download_automation]]、[[gbc_smart_kinmu_automation]]等、他の無人launchdジョブも同じ設計思想を適用すべき対象。次にそれらを触る機会があれば同様の通知埋め込みを検討する。


**2026-10-12追記**: 通知は共通送信口 `teams_notify` の `notify("ERROR", ...)` で送る。そうすると自動修復キューにも積まれる([[webhook_autofix_project]])。ログのパスは `log=` で渡す。
