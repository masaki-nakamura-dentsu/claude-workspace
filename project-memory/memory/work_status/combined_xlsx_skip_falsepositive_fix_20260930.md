# COMBINED.xlsx自動更新「スキップ」誤判定の修正 (2026-09-30)

## 2026-09-30T00:00
Status: done
What: ユーザーから「Salesforceバックアップ後に毎回『COMBINED.xlsx自動更新: スキップ』が出る、Excelで開いていないのに」と相談。調査の結果、`download_all_reports.py`の`excel_has_open_workbooks()`がExcelに1つでもワークブックが開いていれば(対象ファイルかどうか無関係に)True→スキップする実装だったことが原因と判明。実機確認したところ、Excelプロセスがバックグラウンドで起動しており、無関係な`20260917_★9月提出用_日系ピッチ案件リスト.xlsm`(JCIピッチリスト作業の開きっぱなし)が開いたままになっていて、これが誤って「開いている」判定を引いていた。ログ(`launchd_stdout.log`)でも9/28・9/29 17:41・9/30 13:41のスキップがこのパターンと一致することを確認。
ユーザーに2択(対象ファイルに絞る/今回だけ閉じる)を提示し「絞る」を選択。`excel_has_open_workbooks()`を`excel_open_target_workbooks()`に置き換え、COMBINED.xlsx/Prep_SalesforceAllRecord.xlsx/Prep_CAS X SF Crosstable.xlsxの3ファイル名のみをチェック対象にするよう修正(それ以外のファイルが開いていても同期を実行する)。副次的に、Excel未起動時にAppleScriptのtell自体がExcelを起動させてしまう副作用を避けるため、先にSystem Eventsでプロセス存在確認するよう変更。構文チェック・実機での動作確認(現状Excelは起動中だがJCIファイルのみ→`[]`が返り実行対象と判定されることを確認)済み。
Next: 次回の定時実行(11:15/16:45等)で修正版が動く。ユーザーには開きっぱなしのJCIピッチリストファイルを閉じるよう伝えるかは未確認(今回の修正で閉じなくても同期は進むようになったため必須ではない)。
