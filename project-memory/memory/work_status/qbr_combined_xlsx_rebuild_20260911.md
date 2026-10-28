# QBR COMBINED.xlsx全量再構築・ホーユー/サントリーBF金額差異調査

## 2026-09-11T12:00:00+09:00
Status: done
What: 「案件別ランキング」チャートのサントリーBF/ホーユー案件のPower BI-Tableau金額差異を調査。サントリーBFは見込データの鮮度差(バグなし)、ホーユーは`Prep_CAS X SF Crosstable.xlsx`の実データ誤り(台湾/シエロ案件の二重登録4件)が真因と確定・修正。この誤りはPower BI側にも波及していたことも判明・修正確認済み(ユーザーがPower BIリフレッシュ後の新しい数字を確認)。ユーザーの依頼で`COMBINED.xlsx`を「追記オンリー」から「file1(Raw YTD)からの全量再構築」方式に転換するスクリプト`~/CASExport/rebuild_cas_combined_actual.py`を作成・実行(総額はfile1と完全一致、Salesforce案件名解決率67%)。`Prep_SalesforceAllRecord.xlsx`に18桁ID列を追加(将来の大文字小文字衝突リスク低減)。twbのデータソース接続先を一時ファイル`COMBINED_SF案件名版.xlsx`から修正済み`COMBINED.xlsx`に復元、一時ファイルはアーカイブへ退避。Tableau側での最終確認(`Tableau002.xlsx`)でも新しい正しい数字(ホーユー_シエロ7,707,024、サントリーBF9,840,000)と一致することを確認済み。詳細は[[qbr_combined_xlsx_rebuild_20260911]]参照。
Next: フェーズ2(`Prep_SalesforceAllRecord.xlsx`の自動DL化、[[sf_reports_qbr_download_automation]]基盤の拡張)は未着手。ユーザーから依頼があれば着手。

## 2026-09-11T13:00:00+09:00
Status: done
What: フェーズ2着手・完了。既存の[[sf_reports_qbr_download_automation]]が既に「（設定突合用）SF案件リスト」を平日11:15/16:45に自動DL済みと判明したため、新規Salesforce自動化は不要と判断。`~/CASExport/sync_sf_record_list.py`を新規作成しその最新ファイルから`Prep_SalesforceAllRecord.xlsx`を同期(5,232→5,335行、103件の新規案件を反映)、`COMBINED.xlsx`を再構築して確認。続けてユーザー依頼で完全自動化: `download_all_reports.py`に`run_combined_rebuild_sync()`を追加し、パイプライン完了後に自動連鎖するよう組み込み(Excel使用中は`osascript`でチェックしスキップ+Teams通知)。単体テストで正常完走を確認済み。
Next: 実際のlaunchd定時実行(次回11:15または16:45枠)で自動連鎖が動くか確認。個人Mac側への移植は対象ファイルの所在上不要と判断済み。

## 2026-09-14T16:57:00+09:00
Status: done
What: 実運用開始後、初めて自動連鎖が2回とも失敗/スキップした。(1) 12:18定時実行: `sync_sf_record_list.py`が`ModuleNotFoundError: No module named 'openpyxl'`で失敗(launchd経由のsubprocessが対話シェルと別のpython3を掴んだ可能性、原因未特定)。(2) 16:51再実行: `excel_has_open_workbooks()`がExcel使用中と誤検知しTeams通知でスキップ、ユーザー確認では実際には開いていなかった。ユーザーからのTeams通知を受け、Excelプロセス不在(`ps aux`)・`osascript`の判定結果が`missing value`であることを確認した上で、`python3 sync_sf_record_list.py`→`python3 rebuild_cas_combined_actual.py`を手動実行、両方成功(5,341行→Actual 6,115行、総額1,445,686,232円で[[qbr_combined_xlsx_rebuild_20260911]]記載値と一致)。
Next: 未解決。(a) launchd実行時に`subprocess.run(["python3",...])`がopenpyxl入りのpython3(`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`)を解決できているか要検証(フルパスに固定した方が安全かもしれない)。(b) `excel_has_open_workbooks()`の誤検知が再現するか次回の定時実行で要観察、再発するなら判定ロジック(osascriptタイムアウトやリトライ)の見直しが必要。
