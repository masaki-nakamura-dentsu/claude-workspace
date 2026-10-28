---
name: qbr-combined-xlsx-rebuild-20260911
description: サントリーBF/ホーユー案件のPower BI vs Tableau金額差異を調査し、真因(Crosstableの実データ誤り)を特定・修正。COMBINED.xlsxを追記オンリーからfile1全量再構築方式に転換した経緯
metadata:
  node_type: memory
  type: project
  originSessionId: 687a7e64-b7f1-4671-82ab-53ad3313fe88
  modified: 2026-09-14T07:55:51.287Z
---

# 背景
2026-09-11、[[qbr_powerbi_case_collision_investigation_20260910]]の続きで「案件別ランキング」チャートのサントリーBF/ホーユー案件の金額差異を調査。最終的にPower BI/Tableau双方が一致する状態まで解決した。

# 発見・解決した問題

## 1. サントリーBFの「+200万円」差異 → バグではなく鮮度差
`2026 サントリーBF ハイドレーション新商品コミュニケーション`案件、Tableauは7,840,000(実績のみ)、Power BIは9,840,000(実績+2026年9月・確度B見込2,000,000)。原因はTableauの見込データソース(`GBC CAS実績+見込_COMBINED_SF案件名版.xlsx`のForecastシート、当時)にこの見込レコードが存在しなかっただけ(Salesforceへの新規見込登録がTableauの最終データ取込より後だった)。バグではなく両者とも正しい、データの鮮度差。

## 2. `COMBINED_SF案件名版.xlsx`とは何だったか
2026-09-09セッションで「案件ランキング」のNULL案件名バグ修正の副産物として作られた一回限りの代替データソース(生成スクリプトは保存されず)。Power BIの`Raw YTD`クエリと同じく、`Prep_CAS X SF Crosstable.xlsx`(受発注ヘッダNo→案件ID)経由で`SF案件リスト`(Salesforce)と結合しSalesforce案件名を得る処理を再現しようとしたもの。**`COMBINED.xlsx`自体は元々このSalesforce結合を持たず、file1(CAS原本)の自由入力の件名をそのままコピペしているだけ**(手入力ではなく手順書通りのコピペ運用、[[qbr_crosstable_monthly_update_process]]参照)と判明。

## 3. ホーユー「台湾/シエロ」混同の真因 → Crosstableの実データ誤り(確定・修正済み)
`Prep_CAS X SF Crosstable.xlsx`の`Crosstable`シートに、4件の受発注ヘッダNo(H10-2601026335/H10-2601045605/H10-2601045621/H10-2601045647、いずれも2026年1〜4月分)が**ホーユー_台湾(`a1hGA00000A0Rj8YAF`)とホーユー_シエロ(`a1hGA00000A0ReaYAF`)の両方の案件IDに二重登録**されていた。file1で該当伝票の件名を確認すると全て「シエロ」関連(「ｼｴﾛｲﾝﾊﾞｳﾝﾄﾞ施策 X月分」)で、台湾への紐付けは明確な誤り(Crosstableの月次手動更新作業でのコピペミスと推測)。
**この誤りはPower BI側(山田啓太さんのOneDrive経由の同一Crosstableファイル)にも波及していた** — 修正前の「Power BIの正しい値」として扱っていた数字(台湾5,565,092/シエロ5,047,141)自体が、実はこの誤りの影響を一部受けていた(H10-2601026335分・約121万円が誤って台湾側に計上されていた)。修正後の正しい値は**台湾2,905,209/シエロ7,707,024**(合計10,612,233は修正前後で不変)。Crosstable修正後、Power BIをリフレッシュしたところ新しい数字に切り替わったことをユーザーが確認済み(`data (9).xlsx`のエクスポートで検証)。

## 4. COMBINED.xlsxを「追記オンリー」から「全量再構築」方式に転換
ユーザーの明示的な依頼「ちゃんと全部が更新されるシステムにして下さい」を受け、Power BIと同じ結合ロジック(file1 Raw YTD → Crosstable → SF案件マスタ → クライアント名変換)をPythonで再現し、`COMBINED.xlsx`のActualシートを毎回file1から全量再構築するスクリプトを作成。

**スクリプト**: `~/CASExport/rebuild_cas_combined_actual.py`(2026-09-11作成、恒久配置済み)
- file1(`GBC CAS実績_FY22 TO DATE.xlsx`のRaw YTD)を全量読み込み
- `Prep_CAS X SF Crosstable.xlsx`で受発注ヘッダNo→案件ID(18桁)を解決
- `Prep_SalesforceAllRecord.xlsx`の`_Original`シート(18桁ID→Salesforce案件名)で件名を置換、解決できない行はfile1の生の件名にフォールバック
- `Client Name_CAS_SF_FY22 TO DATE.xlsx`のListシート(列A→列E、完全一致)でクライアント名を調整後表記に変換
- 総額はfile1と完全一致(1,445,686,232円)、Salesforce案件名での解決率67%(4,116/6,114行)
- **今後の更新方法**: このスクリプトを再実行するだけで全量再構築される。実行前に対象ファイル(`Prep_CAS X SF Crosstable.xlsx`/`Prep_SalesforceAllRecord.xlsx`/`GBC CAS実績+見込_COMBINED.xlsx`)がExcelで開かれていないことを必ず確認すること(§6参照)。

## 5. 副次的に実施した恒久対応
- `Prep_SalesforceAllRecord.xlsx`に「案件ID(18桁)」列を追加(Z列、`_Original`・main両シート、Python計算値)。[[qbr_powerbi_case_collision_investigation_20260910]]で判明した15桁ID大文字小文字衝突リスクをこのファイルでも解消。ただし**このファイル自体は2026-07-30時点で更新が止まっている**(Salesforce直結ではない静的コピー)ため、新規案件には対応できない — [[sf_reports_qbr_download_automation]]の自動DL基盤を拡張してこのファイルも自動更新対象に加える「フェーズ2」は未着手。
- twb(`8. CAS実績_見込比較 V1.0.twb`)のデータソース接続先を`COMBINED_SF案件名版.xlsx`→修正済み`COMBINED.xlsx`に復元(filename・caption属性を編集、Tableauを閉じた状態で実施)。
- `COMBINED_SF案件名版.xlsx`は削除せず`Archive - Data for Tableau/20260911_combined_rebuild/`に`_unused`サフィックスで退避。

## 6. 重大なハマりポイント: Excelで開いたままのファイルへの書き込みは巻き戻る
作業中、`Prep_CAS X SF Crosstable.xlsx`/`GBC CAS実績+見込_COMBINED.xlsx`/`COMBINED_SF案件名版.xlsx`がユーザー自身によってExcelで開かれたままになっており、openpyxlでの直接編集が2回連続で巻き戻る事故が発生した。詳細・確認コマンドは[[feedback_autosave_cloud_file_direct_edit]]に統合済み。[[openpyxl_empty_v_tag_corruption]]の「保存で数式キャッシュが消える」問題とは別種の事故。

# 7. フェーズ2完了: 自動化(同日、続きセッション)
`Prep_SalesforceAllRecord.xlsx`の鮮度問題は、[[sf_reports_qbr_download_automation]]が既に平日11:15/16:45に「（設定突合用）SF案件リスト」レポートを自動DLしていたため、新規のSalesforce自動化基盤は不要だった。以下を追加するだけで完了:

- `~/CASExport/sync_sf_record_list.py`(新規): 上記自動DLの最新ファイルを読み、`Prep_SalesforceAllRecord.xlsx`の`_Original`シートを全量置換(A列/C列削除は元レポートの列インデックスで対応)、`案件ID(18桁)`列も再計算。mainシート(`_Original`参照の数式シート、IF-wrapper/ASC-wrapperの2パターンのみ、コピー元テンプレートの文字列置換ではなく列ごとに正しい式を都度生成)も行数分だけ数式を張り直す。実行結果: 5,232行→5,335行(2026-07-30止まりだった103件の新規Salesforce案件を反映)。
- `~/SalesforceExport/reports_pipeline/download_all_reports.py`に`run_combined_rebuild_sync()`を追加、`main()`のパイプライン完了後(成功/失敗問わず)に自動実行するよう組み込み。`excel_has_open_workbooks()`(osascriptで`tell application "Microsoft Excel" to get name of every workbook`、`missing value`以外なら開いていると判定)でExcel使用中は必ずスキップしTeams通知(手動実行コマンド付き)、それ以外は`sync_sf_record_list.py`→`rebuild_cas_combined_actual.py`の順にsubprocess実行。単体テストで正常完走を確認済み(2026-09-11)。
- 個人Mac側`reports_pipeline_personal/`には移植していない(COMBINED.xlsx/Prep_SalesforceAllRecord.xlsxはd14461ローカルのOneDrive-電通パス限定のファイルで、そもそも個人Mac側から書けない)。

**未検証**: 実際のlaunchd定時実行(平日11:15/16:45)でこの自動連鎖が動くのは次回以降。構文チェック・単体テストのみ済み。

# 8. 運用開始後の初回トラブル(2026-09-14)
実運用初日、自動連鎖(`run_combined_rebuild_sync()`)が2回とも正常完走しなかった。
- 12:18定時実行: `sync_sf_record_list.py`が`ModuleNotFoundError: No module named 'openpyxl'`で失敗。対話シェルの`python3`(`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`、openpyxl 3.1.5インストール済み)とは別のpython3をlaunchd経由のsubprocessが掴んだ可能性がある(原因未特定、`subprocess.run(["python3", ...])`がPATH解決に依存しているため)。
- 16:51再実行: `excel_has_open_workbooks()`(osascriptで`tell application "Microsoft Excel" to get name of every workbook`)が「開いている」と誤検知しTeams通知でスキップ。ユーザーに確認したところ実際には開いていなかった(誤検知)。
- どちらもTeams通知の指示通り`python3 sync_sf_record_list.py`→`python3 rebuild_cas_combined_actual.py`を手動実行して解消。総額1,445,686,232円で本メモリ§4の値と一致することを確認済み。
- **未解決の再発防止策**: (a) `download_all_reports.py`内の`python3`呼び出しをフルパス(`sys.executable`または`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`)に固定する、(b) Excel誤検知が再現するか次回の定時実行を観察し、再現するなら`excel_has_open_workbooks()`のリトライ/タイムアウト調整を検討する。いずれも次回発生時またはユーザー依頼時に着手。

# 関連メモリ
[[qbr_powerbi_case_collision_investigation_20260910]] [[powerbi_gbc_dashboard_current_state]] [[qbr_crosstable_monthly_update_process]] [[cas_csv_download_automation]] [[openpyxl_empty_v_tag_corruption]] [[feedback_pbix_use_fresh_download]]
