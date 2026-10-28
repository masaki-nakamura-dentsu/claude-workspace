# GBC Salesforce In-Out案件 Excel書き出し

## 2026-09-03T00:00:00+09:00 (approx)
Status: done
What: ユーザー依頼「SalesforceのGBC過去1年in-out案件をExcelに書き出したい」に対応。既存の自動DL済みレポート「（設定突合用）SF案件リスト」（`Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し/`、[[sf_reports_qbr_download_automation]]によりd14461でlaunchd自動更新済み）の最新ファイル(2026-09-03 11:16版)から、レコードタイプ=CLIENT かつ 商流/Business flow列に"In-Out"を含む案件を抽出。作成日2025/09/03〜2026/09/03で418件・ユニーククライアント203社。2シート構成(クライアント別サマリー/案件明細)のExcelを新規作成し`Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/GBC_InOut案件リスト_過去1年_20260903.xlsx`に保存、openで表示、ユーザー要望によりFinderで格納フォルダも開いた。ユーザーはタスク終了を宣言("OK, task end")、追加フィードバックなし。
Next: —
