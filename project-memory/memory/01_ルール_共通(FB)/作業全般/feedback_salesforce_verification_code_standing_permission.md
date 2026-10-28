---
name: feedback-salesforce-verification-code-standing-permission
description: "[廃止済み2026-09-02] Salesforceのメール認証コード自動入力の標準許可 — dentsu側のセキュリティ要件変更でメールコード方式自体が使われなくなり無効化"
metadata:
  type: feedback
  originSessionId: a36d9ee0-bcf1-47ae-adda-432964be5953
  modified: 2026-09-02T08:28:14.288Z
---

**2026-09-02追記: この許可は実質的に失効した。** Salesforceの本人確認方式がメールの6桁コードから「別の検証方法」経由のSalesforce Authenticator(iPhoneへのpush通知承認)に切り替わったため（[[salesforce_report_download_automation]] [[sf_reports_qbr_download_automation]]参照）、メールを読んでコードを入力する処理自体を`download_all_reports.py`/`download_step1_export.py`から削除した。今後、確認コード入力が必要な場面が再び発生した場合（Authenticatorの選択肢が見えない等のフォールバック時）は、ユーザーに直接確認を取ってから対応すること — 過去のような「無条件の自動承認」は前提にしない。

---
(以下、元の記録。2026-08-11時点の背景として残す)

Salesforceでレポートをエクスポートすると、セキュリティ要件により毎回メールに6桁の確認コードが届く仕組みになっている（[[salesforce_report_download_automation]]、[[gbc_weekly_report_kimura_dmd_project]]参照）。2026-08-12、[[gbc_weekly_report_kimura_dmd_project]]の実データテスト中に確認コード入力の許可を求めたところ、ユーザーが明示的に「Salesforceのエクスポートは例外で、あなたが私のメールをチェックしてその数字を入れてよいです。私の許可は不要です」と述べた。

**Why**: 毎週水曜夜など繰り返し発生するタスクで、コードのためだけに毎回中村さんの手を止めるのは非効率。メール自体は[[outlook_cli]]で自分で読める。

**How to apply**: （廃止）今後、Salesforceのレポートエクスポートで確認コードが必要になった場合、`outlook list`→`outlook read <index>`（差出人`noreply@salesforce.com`、件名「Salesforce で ID を確認」）でコードを自分で取得し、都度の許可を取らずにそのままエクスポートフローに入力してよい。これはSalesforceのエクスポート確認コードに限定された例外— 他の目的（他人への送信内容の確認等）でメールを読む/操作する際は、引き続き通常の確認プロセスに従う。
