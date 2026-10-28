# Salesforceダウンロード自動化: 検証方式をメールコード→Authenticator承認に変更

## 2026-09-02T17:30
Status: done
What: dentsu側のSalesforceセキュリティ要件変更で、本人確認画面のデフォルトが「管理者から取得した仮のコード」入力(TempCodeVerificationUi)に変わった。実機確認の結果、正しい対応は「別の検証方法を使用してください」→「Salesforce Authenticator」を選ぶとiPhoneにpush通知が届き承認するだけでよいことが判明。これに合わせて`~/SalesforceExport/reports_pipeline/download_all_reports.py`(平日2回・8レポート完全自動)からOutlook Web自動操作によるメールコード読み取りロジックを削除し、`select_salesforce_authenticator()`でAuthenticator方式に切り替え、Teams通知＋5分タイムアウト待機に変更。`~/SalesforceExport/download_step1_export.py`(業況見通し用、対話実行)も同様に更新し、`download_step2_enter_code.py`は不要化(廃止コメントのみ追記、ファイルは削除せず保持)。メモリ更新: [[salesforce_report_download_automation]] [[sf_reports_qbr_download_automation]] [[feedback_salesforce_verification_code_standing_permission]](失効マーク)。
Next: —

## 2026-09-03T09:35
Status: done
What: ユーザー依頼で実機テストを実施。共有ブラウザ(9226)経由で1レポートをダウンロード。テストで「別の検証方法を使用してください」リンク(href="javascript:srcUp(...)")がPlaywrightの`.click()`では遷移しない不具合を発見・修正(hrefを解析してpage.goto()で直接遷移する方式に変更)。修正後、「検証方法を選択してください」画面→「Salesforce Authenticator」選択→iPhoneへpush通知→ユーザー承認→ダウンロード完了、までエンドツーエンドで成功を確認。`download_all_reports.py`と`download_step1_export.py`の両方に修正を反映。テストファイルはスクラッチ領域にのみ保存し、本番フォルダ(今後の業況見通し/202609/)は汚していない。メモリ更新: [[salesforce_report_download_automation]] [[sf_reports_qbr_download_automation]]。
Next: 次回のlaunchd定時実行(平日11:15/16:45)で実際に検証が発生した際、pipeline_log.txtとTeams通知を見て本番でも問題なく動くか確認する。
