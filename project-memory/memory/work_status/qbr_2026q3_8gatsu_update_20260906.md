# QBR用データ更新 2026年8月分（貢献実績・見込・COMBINED）

## 2026-09-06
Status: partial done
What: 中村さんから5ファイル更新依頼。ソースのSalesforceレポート(v2.1/v2.2/v2.3)はDropbox `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し/`配下(会社Mac自動DLパイプラインの成果物、オンライン専用プレースホルダーだったのでopen -gでダウンロードトリガー済み)から取得。
完了: `GBC 貢献見込_LATEST.xlsx`(v2.2で346件、貢献見込/貢献見込_Original全件入替)、`GBC 貢献実績_FY22 TO DATE.xlsx`(v2.3で3060件、貢献実績/貢献実績_Original全件入替、部署"部"除去+ASCII変換+DATEVALUE追加)、`GBC 貢献実績+見込_COMBINED.xlsx`(Actual 2126件=確度Aのみ抽出、Forecast 338件=確度Xのみ除外、貢献売総はAtt.Rev(A)列を使用)。バックアップは`Archive - Data for Tableau/20260906/`。
追記2026-09-06(1回目、誤り): `GBC CAS見込_LATEST.xlsx`と`GBC CAS実績+見込_COMBINED.xlsx`を「（QBR集計用）月別_貢献利益（仕掛）_v2.1」データ(貢献売総ベース)で更新したが、これは誤ったソース——中村さんから訂正が入った。またCAS見込シートが実は数式ベース(`=CAS見込_Original!A2`等、C列はXLOOKUP、DATEVALUE列(S列)あり)だったのを知らずに値で直接上書きし、数式とDATEVALUE列を破壊してしまった。

追記2026-09-06(2回目、修正): 中村さんが正しいレポート「（QBR集計用）月別_設定利益（仕掛）_v2.1」(SFレポートID 00O7F00000Ayt1TUAR、マニュアル記載通り)を手動エクスポートし`~/Downloads/QBR      _        _v2.1-2026-09-06-09-14-34.xlsx`として提供。このファイルには`GBC取設定/SETTEI TO(JPY)`列(16列目)と`GBC設定売総/SETTEI Rev(JPY)`列(17列目)が両方存在し、CAS見込_LATEST.xlsx側の列名と完全一致することを確認。
対応: (1) `GBC CAS見込_LATEST.xlsx`をバックアップ(`Archive - Data for Tableau/20260906/`)から復元し、`CAS見込_Original`に新データ(2026年かつ月>=09、244件)を値で投入、`CAS見込`シートは元の数式(DATEVALUE含む)を行番号だけ置換して244行分に正しく伸長。(2) `GBC CAS実績+見込_COMBINED.xlsx`のForecastシートを同じ244件・`GBC設定売総/SETTEI Rev(JPY)`列(マニュアル85行目の対応表通り)で再構築。
中村さんへの申し送り: CAS見込シートは外部リンク`[1]List - Project`参照のC列XLOOKUPがあるため、[[cas_csv_download_automation]]と同様Excel側の自動再計算(AppleScript)が失敗しやすい既知の問題がある——開いて一度保存し直してもらうのが安全。
Next: 中村さんに開いて数字を確認してもらう。

## 2026-09-06(3回目)
Status: done
What: 中村さんの確認で3件追加修正。(1) CAS見込_LATEST.xlsxの外部リンク(`[1]List - Project`参照、C列XLOOKUP)がopenpyxl保存でExcel拡張メタデータ欠落→バックアップから`xl/externalLinks/`をzip直接操作で復元、DATEVALUE/金額列のnumber_formatも修正——詳細は[[feedback_openpyxl_formula_sheet_extend]]。(2) CAS実績+見込_COMBINEDのActualが7月までしかなく、かつ7月分107行のDATEVALUE書式が`yyyy-mm-dd h:mm:ss`と異常([[qbr_2026q3_cas_koken_july_update]]の7月追加時の書式崩れ)——`mm-dd-yy`に統一し、CAS実績_FY22 TO DATEのRaw YTDから8月分95件(¥29,687,397、既知の確定値と一致)を追加。(3) 貢献見込_LATEST/貢献実績_FY22/貢献実績+見込COMBINEDのDATEVALUE列も同様に`yyyy-mm-dd h:mm:ss`だったが、これは今回のセッション開始前のバックアップ時点で既にその書式だった(自分が壊したのではない)ことを確認の上、`yyyy-mm-dd`(時刻なし)に統一。
これでQBR8月分更新5ファイル+CAS実績+見込COMBINEDのActual8月分反映まで全て完了。恒久的な学びは[[qbr_cas_mikomi_source_report]](正しいCAS見込ソースレポートの特定)と[[feedback_openpyxl_formula_sheet_extend]](openpyxl更新時の3注意点)に切り出し済み。
Next: なし。
