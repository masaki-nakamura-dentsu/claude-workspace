---
name: webhook-autofix-project
description: Webhook通知の文言ルール・共通送信口(teams_notify)と、[ERROR]を無人で修復するランナー(WebhookAutoFix)の構成と設定値。2026-10-12構築、無人修復はユーザー許可済み
metadata:
  type: project
---
2026-10-12、ユーザーから「Webhookでエラー報告が届いたら自動で修正を試みて」と依頼があり、続けて「送信する時点で仕組みを改善し、文言をルール化して」と頼まれた。**無人修復はユーザーが明示的に許可した(10/12)**。

## 構成(すべて `.claude-sync/Scripts/` 配下、Dropbox同期)
- `notify/teams_notify.py`(本体) と `.sh` / `.js`(薄いラッパー): 共通送信口。件名を `[LEVEL] ジョブ名: 要約` に整形し、本文を1行に潰す。送信はcurlを先に使う(会社MacのTLS傍受でurllibが失敗するため)。URLは `~/.zshenv` の TEAMS_WEBHOOK_URL から読み、ファイルに直書きしない(直書きはauto modeに「Credential Leakage」として拒否された)。ERRORのときは `WebhookAutoFix/queue/pending/` にJSONを積み、`launchctl kickstart gui/<uid>/com.nakamura.webhookautofix` で修復を即時起動する。
- `notify/NOTIFY_RULES.md`: 文言ルールの正本。ERROR=修復対象、WARN=再試行予定、WAIT=人待ち、OK/DONE/INFO、FIX=ランナー専用。
- `WebhookAutoFix/webhook_autofix.py`: 修復ランナー。入力は (A) キュー(主)、(B) teams_messages.jsonl の「ワークフロー」チャットにあるタグなし旧形式(件名のキーワードで判定、後方互換)、(C) jsonlの更新停止。結果は [FIX] / [WAIT] で通知する。`fix_prompt_template.md` は修復を担当する `claude -p` への指示書(破壊的操作禁止、編集前のバックアップ、MFAは人に回す、relayでの依頼、SUMMARY形式)。
- **設定値**: 起動は15分おき+RunAtLoad / 1日6回まで / 同じ件名は6時間再修復しない / 他ホストのキュー項目は30分後に引き取る / claudeは40分でタイムアウト / jsonlの更新停止(26時間超・平日9〜20時)は修復せず、停止1回につき[INFO]通知1回だけ(会社Macを起動しない休暇日にも起きるため、10/12ユーザー指摘で変更)。
- ホスト名: 個人Mac=`MacBookMN`。

## 移行済みの送信元(10/12、各ファイルに .bak_202610120747 前後のバックアップあり)
メール同期・カレンダー同期(data-export)/ TimeTreeチェック / 週次AIダイジェスト(URL直書きを削除)/ HDY定点観測(core.send_teamsの引数を(level, job, summary, detail, log)に変更)/ Salesforce個人Mac DL+failover(URL直書きを削除。各回の失敗=WARN、9回再試行しても失敗=ERROR)/ 週次メモリレビュー。
会社Mac専用(sfreportspipeline, teams_daemon, CAS等)は relay task-015 で依頼済み。Power Automateのクラウドフローからの通知は旧形式のまま(Bで拾う)。

## 稼働状況
- 2026-10-12、個人Macでユーザーがlaunchdに登録した(com.nakamura.webhookautofix)。auto modeでは2回拒否されたため手動での登録。最初の実行(9:09)で取込停止を検知し、約1.5分で「他マシンに依頼(task-015で依頼済み)・要ユーザー対応」と判定して通知した。全体が通しで動くことを確認済み。
- 判明した点: 無人のclaude -pは `~/.claude/` 配下に書き込めない。指示書はDropbox側の実体パス(.claude-sync/project-memory/memory/)に書くよう修正済み。無人ランナーのメモは `WebhookAutoFix/logs/autofix_notes_YYYYMMDD.md` にも残る。

## 未完了
- teams_messages.jsonl が 10/8 18:24 から更新されていない(会社MacのTeamsデーモン)。
- 旧形式の判定: 件名だけを見る(本文まで見ると対話セッションの報告を誤検知する)。例外は「0/18件成功」のような部分成功。
Related: [[teams_webhook_powerautomate]] [[feedback_bake_error_notifications_into_automation]] [[automation_schedule_overview]] [[mac_handoff_relay]]
- 2026-10-13: Claude Codeのzsh(Bash tool)からteams_notify.shをsourceすると、日本語パスが化けてcdに失敗し黙って送られない。対話セッションではteams_notify.pyを直接呼ぶ。
- 2026-10-17: 件名の長さ制限を追加(TITLE_MAX=28/JOB_MAX=10/SHORT_JOB、超えた分は本文先頭の「件名全文」へ)。バックアップ teams_notify_bak_20261017.py。NOTIFY_RULES.md更新。[[feedback_webhook_title_length]]
