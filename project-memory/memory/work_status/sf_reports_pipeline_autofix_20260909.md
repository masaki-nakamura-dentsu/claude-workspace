# SFレポート自動DLパイプライン: 全滅事故の調査と自動リカバリ追加

## 2026-09-09T12:53:00+09:00
Status: done
What: 本日11:15の定時実行が18本全滅(84分間、全て"BrowserContext.new_page: Target page, context or browser has been closed")していたのをユーザー報告で発覚。ブラウザ(port 9226)が復旧していたため手動再実行し18/18成功。根本原因(実行中にCDP接続が切れると既存のレポート単位リトライが無意味)への対策として`~/SalesforceExport/reports_pipeline/download_all_reports.py`に(1)`BrowserState`クラスによるCDP接続の生死確認・自動再接続、(2)全滅時のみパイプライン全体を5分後に自動再実行(最大2回、3回連続全滅でTeams通知して諦める)を追加。構文チェック済み、次回定時実行(本日16:45)で実地検証待ち。詳細は[[sf_reports_qbr_download_automation]]に追記。
Next: 16:45の定時実行で新ロジック(特にBrowserState再接続)が正常動作するか確認。個人Mac版(reports_pipeline_personal/download_all_reports.js)には未移植。

## 2026-09-09T13:XX (続き)
Status: done
What: ユーザーから「昼の移動時間に会社Macを閉じていることが多く、その間は11:15の定時実行自体が起動できない」との指摘を受け、13:00の保険ジョブを追加。新規`retry_1300_if_missed.py`は代表レポートフォルダに本日日付のファイルが無ければ「11:15分が未実行」と判断しdownload_all_reports.pyをフル実行(既に本日分があれば何もせず二重実行を防止)。新規launchdジョブ`com.nakamura.sfreports1300retry.plist`(平日13:00)としてload・稼働確認済み(exit code 0)。構文チェック済み、実地検証はまだ(次に11:15を跨いで会社Macが閉じているタイミングで確認予定)。詳細は[[sf_reports_qbr_download_automation]]に追記。
Next: 実際に会社Macが閉じた状態で11:15を跨いだ日に、13:00ジョブが正しく検知・実行するか確認。
