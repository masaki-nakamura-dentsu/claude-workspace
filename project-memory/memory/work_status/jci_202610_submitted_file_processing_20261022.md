# JCI 10月提出版(岩田さん受領)の処理 (2026-10-22)
Status: in_progress (ユーザー判断待ち: 要確認30件の扱い、SFインポート実行可否)
- ★10月提出版_日系ピッチ案件リスト_20261021.xlsm と 202609日系ピッチサマリーレポート_20261022.pptx を Downloads → BD部集約_JPターンアラウンド/BD部提出済み/ へ移動(名前そのまま)。
- build_import_csv.py で output/ に 親案件_更新(31行)/親案件_新規登録(20行)/月別見込_既存分(27行)/要確認レポート(30件) _20261021_10月.csv を生成(--existing-ym は10/13メモの台帳7本)。月別見込_新規分は親案件取込後のID払い出し待ち。
- 年月移動1件: S-Cup Sachet(a1hfP00000EcR0z) 2026/09→10。
- 要確認の主因: フェーズ「<削除依頼>」(City 4door, JTI Global Branding)、選択肢マスタ外の値、金額空欄で月別見込除外4件(アシックス,Honda 2W,JTI Global Branding,JTI Ploom)。
- verify_against_source.py の差分は9/28 SF書き出し以降のBD編集が中心。SFインポートは未実行。

## 2026-10-22 追記(2回目)
- ユーザー指示: PPTXは参考、Excelが正(PPTXの4件取りこぼしは無視)。<削除依頼>2件(City 4door a1hfP00000ADVZh / JTI Global Branding a1hfP00000EcR18)はインポート完了後にSF上で削除(未実施)。
- 選択肢マスタ外の値をユーザー承認の対応案で修正し、別名 BD部提出済み/★10月提出版_日系ピッチ案件リスト_20261022.xlsm を作成(xlsx XMLを直接編集。openpyxl保存はx14入力規則を壊すため不使用、fullCalcOnLoad付与)。変更は戦略企画部コメント欄(AP列)に「10/22 …」で記録。AnyMind=その他日系, CXM=Data/CRM, Vistraスコープ=Brand - Product/Service。ANA/Festiveの勝因は選択肢+その他、自由文は自由記入欄へ。Event/Promotion (Online, E-commerce)は変更せず取込、エラーのみ後で修正。獲得グループ空の完了・不成立(Baleno, Auto Expo)はCSV側で不明/Unknown補完+コメント記録。
- build_import_csv.py に<削除依頼>行の除外を追加(旧版は_archive/build_import_csv_before20261022.py)。output/*_20261022_10月.csv を再生成(更新29/新規20/月別見込既存分/要確認9件)。旧CSVは output/_old_20261021/。
- 未実施: SFへのインポート。親案件(CLIENT)取込は常設ウィザード対象外。ユーザーに進め方を確認中。

## 2026-10-22 追記(3回目) 親案件インポート実行
Status: done(親案件のみ。月別見込は未着手)
- 新規スクリプト `~/SalesforceExport/import_scripts/jci_parent_wizard.py`(prepare parent-update|parent-insert <csv>。start/jobsは jci_import_wizard.py を使う)。実行は `/usr/local/bin/python3 -P`(playwrightが入っているのはこのpython)。設定値は手順書(親案件_更新/新規作成)どおり: 一致条件=Salesforce ID(更新)/なし(新規)、Client=Salesforce ID、活動項目=名前、責任者=外部キー、レコードタイプ=CLIENT、文字コードUTF8手動。
- 親案件_更新(29行): 28更新/1失敗 → 失敗はHertz/Delectables(a1hfP00000EcR17)の「その他/Others（*自由記入）」3,299字でSTRING_TOO_LONG(上限は216字は通る=おそらく255字)。233字に短縮したretry CSV(…_retry_Hertz.csv)で再取込→1更新/0失敗。全文はBD部提出Excelにあり、SF上は短縮版(末尾に「全文はBD部提出Excel参照」)。
- 親案件_新規登録(20行): 20作成/0失敗。
- メール確認: noreply@salesforce.com の2通を outlook read で確認。エラー添付CSVは、添付チップ(GBCItems_Errors.csv)クリック→Excelプレビュー→Ctrl+End等で読む(ダウンロードは今も不可)。
Next: ①月別見込_新規分(新規登録20件のID払い出しレポートから --new-id-map で生成→sales-insert) ②月別見込_既存分(sales-upsertを2回) ③<削除依頼>2件(City 4door a1hfP00000ADVZh / JTI Global Branding a1hfP00000EcR18)のSF削除 ④build_import_csv.pyに「その他/Others」255字超の警告を入れる

## 2026-10-22 追記(4回目) 月別見込インポート
Status: done(重複1件の削除のみユーザー確認待ち)
- 新規登録IDレポート(00OfP00000IrB4bUAF)はグリッドが遅延描画。スクロール+Endで全行取得(rep.py)→ output/新規登録一覧ID_20261022.xlsx(20件)→ build_import_csv.py --new-id-map で 月別見込_新規分_20261022_10月.csv(15行)生成(既存分26行は前と同一)。
- sales-insert 新規分: 15作成/0失敗。既存分 sales-upsert 1回目: 4作成/22更新/0失敗、2回目: 1作成/25更新/0失敗。
- **失敗点**: 年月移動行(S-Cup Sachet a1hfP00000EcR0z, 識別コード旧202609_1)を2回目に送ったため、移動後は識別コードが202610_1になっており不一致→新規作成され2026/10が2件重複(check: 行数2)。新しい方(2026/10/22作成)の削除待ち。
- **次回ルール**: 円貨回避策の2回目アップセートでは年月移動行を除いたCSVを使う(または移動後コードで送る)。

## 2026-10-22 追記(5回目) 重複削除・最終確認
Status: in_progress(<削除依頼>親2件の削除のみ未完)
- S-Cup重複(新しい方 a1hfP00000JUVt3)を親案件ページの月別見込関連リストの行アクション→削除で削除済み(残り EdhI1 のみ確認)。月別見込レコード単体ページには削除ボタンが無い(関連リストの行メニューから)。
- <削除依頼>親2件(City 4door a1hfP00000ADVZh / JTI Global Branding a1hfP00000EcR18)の削除は auto mode classifier に拒否(親は子の月別見込ごと消えるため)。ユーザーが自分で実行 or 許可ルール追加待ち。スクリプト: scratchpad/delp.py(<ID> <タイトル断片>)。
- 確認レポート 00OfP00000Cq0rRUAR(462行)はエクスポートせず遅延描画グリッドをスクロール収集(rep3.py)。49件(更新29+新規20)をCSVと突合: 実質差異なし(戦略企画部コメントはCSV空欄でSF側既存値が残るのみ。Hertzはレポート非掲載=フィルタ?)。

## 2026-10-22 追記(6回目) エクスポート突合・方針
- ユーザー提供の全項目エクスポート(Downloads/APAC Pitch - List All_v1.31-…xlsx, 461件)で49件を全項目突合: 差異は複数選択の並び順2件とKao UK Bioreの「GBCサポートその他」(CSV空欄/SF「確認中」)のみ。月別見込は金額あり全親でGroup売総(JPY)>0・外貨合計一致(金額0の3親は円貨0で正常)。Hertzはエクスポート対象外(絞り込み)。<削除依頼>2件は未削除のまま。
- 方針: 次回からレポートexportはClaudeが実行可(本人承認はユーザー)。戦略企画部コメントは日付先頭+対応を書く。/clear推奨時は再開用の一言も添える(グローバルCLAUDE.mdに追記)。
Next: <削除依頼>2件(City 4door a1hfP00000ADVZh / JTI Global Branding a1hfP00000EcR18)の削除のみ。

## 2026-10-22 追記(7回目) AP列コメントの書き換え・再インポート
Status: in_progress(<削除依頼>親2件の削除のみ未完)
- ユーザー指示: AP列は日付先頭(10/22)+「項目:判断理由→入力内容」の書き方に統一(今後も継続、memory feedback_jci_comment_style_and_export_permission)。
- BD部提出済み/★10月提出版_日系ピッチ案件リスト_20261022_01.xlsm を作成(xlsx XML直接編集、A=12,24,25(Hertz新規),34,35 / B=6,7,8,10,16,21,23の12セル)。
- output/親案件_更新_20261022_10月_コメント修正.csv(12行、新規20のうち7件はID付き更新に変換)で再取込: 11更新/1失敗(Vistra、コメント291字でSTRING_TOO_LONG)→コメントを246字に短縮した _Vistra再.csv で再取込1更新/0失敗。Excelも短縮版に反映済み。
- build_import_csv.py に生成CSVのコメント(255字超)警告は未実装。

## 2026-10-22 追記(8回目) 過去コメントの日付補完
Status: in_progress(<削除依頼>親2件の削除のみ未完。日付補完の反映確認はユーザーの再エクスポート待ち)
- ユーザー指摘: 戦略企画部コメントに日付なしの過去分あり。10/22 10:55エクスポートで60件中24件が日付なし。全て8/14エクスポート時点で既存。BD部Excelの初出版から推定日を決定(ユーザー承認「推定日を付けて」): 4/28時点=3件(a1hGA00000A0Rkv,a1hfP000001v9Fh,a1hfP000003pqPR)/5/29時点=2件(a1hfP000002dQ4j,a1hfP00000ADVQ1)/6/30時点=18件。a1hfP000007jjhhは既に「(6/17)」あり→対象外。
- output/親案件_更新_20261022_10月_日付補完.csv(23行、ID+コメント以外は空欄=ウィザードは空欄を無視)で取込: 23更新/0失敗。Excel(BD部提出ファイル)側の過去分は未修正(SFのみ)。
- 未確認: 他項目が空欄で消えていないか(次回エクスポートで10:55版と差分確認すること)。
