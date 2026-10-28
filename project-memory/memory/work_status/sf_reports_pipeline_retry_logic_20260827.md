# SFレポート自動DLパイプラインへのリトライ実装

## 2026-08-27T00:00:00+09:00 (概算)
Status: done
What: `~/SalesforceExport/reports_pipeline/download_all_reports.py`にレポート単位の失敗時リトライを実装。`download_one_report`をtry/finallyでページ確実クローズするよう整理し、新設`download_one_report_with_retry`が最大3回・20秒間隔で再試行するように変更。`main()`は変更なし(1本の失敗が他レポートを止めない構造を維持)。構文チェック済み(py_compile OK)。[[sf_reports_qbr_download_automation]]の該当メモリにも詳細を追記済み。
Next: 次回の平日実行(11:15/16:45)でリトライが実際に動くか、失敗が起きた場合にログ・Teams通知が正しく出るかを観測。
