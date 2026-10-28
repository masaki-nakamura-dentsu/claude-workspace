# CAS CSV自動ダウンロード

## 2026-08-17T15:20:00+09:00
Status: done
What: ユーザーの依頼を受け、CAS「汎用検索」の全項目CSV自動ダウンロードを実装。共有ボットブラウザ(d14461, port 9226)がCASに既にSSO済みであることを確認、月指定でperiodを書き換えるPlaywrightスクリプトを作成し、2026-06/2026-07で件数の異なる正しいCSVが取得できることを検証済み。スクリプトは ~/CASExport/download_cas_csv.sh、詳細は memory/10_GBC_QBR・KPI・PowerBI/cas_csv_download_automation.md。
Next: PowerBI(Raw YTD)への取り込み方法は未着手・未決定。ユーザーが希望すればPower Query「フォルダから結合」方式か、既存Excelへのマージ方式のどちらかを次回相談。

## 2026-08-17T16:15:00+09:00
Status: done
What: ユーザーから振替利益の統合要否・過去のアップデート方法・保存先変更(CAS集計/<月>フォルダへ)の依頼を受け、完全自動の月次パイプラインを構築。過去の手動更新スクリプト(~/Downloads/cas_raw_ytd_append_with_split_onedrive_v2.py)を発見しロジックを完全移植、7月データで実ファイルと数値・行順とも完全一致することを検証。振替利益は通常の全項目CSVに既に含まれておりロジック変更不要と判明(6月のサンリオ案件で実証)。中村さんに「完全自動でよいか」確認の上、launchdジョブ(com.nakamura.caspipeline)を構築・登録し、確定日(3/6/9/12月=翌月第3営業日、他=翌月第2営業日、jpholiday使用)に自動でCASダウンロード→変換→利益スプリット反映→GBC CAS実績_FY22 TO DATE.xlsx(半角変換)とCAS集計_クライアント_件名別_final(全角)の両方へ追記する仕組みが稼働開始。ビジネスデー計算は実際の過去確定日(6月=7/3、7月=8/4)と完全一致を確認済み。詳細は memory/10_GBC_QBR・KPI・PowerBI/cas_csv_download_automation.md。あわせて、ユーザーがPowerBI作業を自分で行う方針に転換(トークン節約目的)したため feedback_token_conscious_powerbi.md を作成。
Next: 初回の実運用は2026-09-02(8月分確定日)以降。その翌朝以降にログ・本番ファイルを確認すること。

## 2026-08-17T16:35:00+09:00
Status: done
What: 中村さんの依頼でTeams Webhook通知を追加(既存の[[teams_webhook_powerautomate]]を再利用)。月次処理成功時/確定日なのに0件の場合/エラー時それぞれに通知を送るよう cas_monthly_pipeline.py の send_teams() を実装。urllib経由はこのPythonビルドのCA証明書ストア不備でSSL検証エラーになったためcurl経由に変更して解決。テスト送信し、中村さんがTeamsで実際に受信したことを確認済み。
Next: パイプライン一式(ダウンロード→変換→利益スプリット→2ファイル追記→Teams通知)は構築・検証完了。あとは2026-09-02(8月分確定日)以降の初回実運用を待つのみ。

## 2026-08-24T00:00:00+09:00 (JSTタイムスタンプ概算)
Status: done
What: 中村さんから「社外にいる場合、BIG-IP Edge Clientは起動するだけで自動接続される」と確認を得たため、cas_download.py の download_month() 冒頭に ensure_bigip_connected()(open -g -a "BIG-IP Edge Client" → 8秒待機)を追加。社内/接続済みでも無害。構文チェック済み、実際の社外オフライン実行での検証はまだ。
Next: 2026-09-02(8月分確定日)の実運用時、その日中村さんが社外にいた場合にログで動作確認。

## 2026-09-02T11:33:02
Status: done
What: 自動パイプラインが2026-08分のCAS実績を確定日を迎えて自動取得。87行、振替利益合計0円、利益スプリット11行反映。file1/file2へ追記完了。
Next: —

## 2026-09-02T14:30:00 (継続セッション、13:16の更新完了~14:30頃まで)
Status: in_progress（PowerBI側の反映が未解決のまま、ユーザーがチャットを一旦閉じて別チャットで再開予定）
What: 上記11:33の初回実運用で3件の重大バグを発見・修正済み（詳細は[[cas_csv_download_automation]]本体メモリ参照）：
  1. CSVヘッダー行位置が検索条件欄の行数変動でずれてパースエラー → 動的検出に修正
  2. find_last_data_row/existing_monthsがread-onlyモードの1セルずつアクセスで極端に遅い(10分以上)→ iter_rows()ベースに高速化
  3. openpyxl保存で数式セルのキャッシュ値が全消失する既知バグ → _xlsx_recalc_fix.py(fix_and_recalc)を~/CASExport/にコピーし、cas_monthly_pipeline.pyのfile1追記後に自動で呼ぶよう統合済み
  さらに、途中でlaunchdの20分間隔自動実行と手動実行が同時に走り本番ファイル二重書き込みしかけたため両方kill、launchdは最終的に再load済み。
  自分(masaki.nakamura)のOneDrive上の「QBR作成/GBC CAS実績_FY22 TO DATE.xlsx」は8月分95行(¥29,687,397)を含む正しい状態に修復・確認済み。
  **その後、Power BIの「GBC数字管理レポート」ワークスペースのRaw YTDテーブルが実際に参照しているのは、自分のOneDriveではなく yamada_keita_dentsu_co_jp（山田啓太さん）のOneDrive上の同名ファイル
  （https://esq365-my.sharepoint.com/personal/yamada_keita_dentsu_co_jp/Documents/Shared Projects/GBC戦略企画部・見込/QBR作成/GBC CAS実績_FY22 TO DATE.xlsx）だと判明**。
  ユーザーいわく「山田さんから共有フォルダとして自分のOneDriveに同期されており内容は同じはず」とのことで、CAS実績データ最終更新日時マーカーのタイムスタンプ(11:32/11:33)は一致していた。
  しかしPower BIを4回（11:30計画済み、12:09/12:32/13:16オンデマンド）更新しても、DAXクエリでの検証（EVALUATE ROW/SUMMARIZECOLUMNSで計上年=2026×MONTH(計上月)=8を確認）では2026年8月データが一貫して0件のまま（2026年計は¥215,633,242＝1〜7月分のまま変わらず）。
  一方Excel Online（山田さんのファイルを直接ブラウザで開いた版）では一時「最終行6114、8月データ含む」ように見えたが、その後Power Query Editor（オンライン版、TMDLビュー経由「クエリの編集」）でRaw YTDクエリのソースM式を確認したところ、プレビューには見覚えのないデータ（受発注ヘッダNo「202201615338」のような"H10-"接頭辞なしの数字のみ形式、クライアント名「味の素(株)」「オイスターソース競合調査」）が表示されており、原因は特定できていない。矛盾する観測結果がある状態。
Next（次のセッションで最初に行うべきこと）:
  1. まずDAXクエリ（①EVALUATE ROW("2026年8月_件数",CALCULATE(COUNTROWS('Raw YTD'),'Raw YTD'[計上年]=2026,MONTH('Raw YTD'[計上月])=8),...) ）で再度8月データの有無を確認する。
  2. まだ0件なら、時間経過（SharePoint/Power BI側キャッシュ）で解決したかを見る。解決していなければ、Power Query「クエリの編集」で見えた不可解なプレビューデータ（味の素/オイスターソース等）が何なのか要調査（別シート？別ステップ？意図しないマージ結果？)。
  3. 自分(masaki.nakamura)のOneDrive側ファイルは既に正しい状態なので再修復は不要。
  4. launchdジョブ(com.nakamura.caspipeline)は正常にload済み、次回9月分は10/5確定予定。
  5. cas_monthly_pipeline.py / cas_pipeline_lib.py / _xlsx_recalc_fix.pyの今回の修正はコミット済み（gitではなくファイル直接編集、バックアップ等は取っていないので変更差分はファイル内コメントで確認可能）。

## 2026-10-05T08:00
Status: in_progress
What: ユーザー「CASデータ更新されているはずなので処理進めて」。9月分(確定日10/5)の自動パイプラインは07:41に初回起動したがCSV出力ボタン待ちでタイムアウト。原因はCAS側が503「オンラインサービス停止中」(朝のメンテ)。パイプラインは状態を進めず20分毎に自動リトライするため、完了待ちの監視をバックグラウンドで開始。
Next: 完了後、追記行のP列(DATEVALUE)が埋まっているか(9/3修正の初回本番検証)と、両ファイルの9月分件数・金額をスポットチェック。

## 2026-10-05T08:10
Status: in_progress
What: ユーザー提示のCAS稼働時間(平日9-24時、土日祝・深夜早朝は非稼働)に合わせ、cas_monthly_pipeline.pyに稼働時間ゲート(cas_online_now)を追加。時間外は待機ログのみでエラー/Teams通知を出さない。単体テストで平日7:41=False、9:00/23:59=True、土曜・10/12祝日=False確認済み。
Next: 9:00以降の次回実行で9月分取り込み→完了監視は継続中。

## 2026-10-05T09:02:50
Status: done
What: 自動パイプラインが2026-09分のCAS実績を確定日を迎えて自動取得。91行、振替利益合計0円、利益スプリット9行反映。file1/file2へ追記完了。クライアント名マッピング: 要確認(自動登録せず、新規クライアントの可能性):
  ・MBC Game Studio Ltd（SP1 20269月 MGS Launch PR (Japan) 利益-61,410円）
  ・NISSIN FOODS(U.S.A.)Co.,Inc.（SP2 20269月 日清食品 米国ｷｬﾝﾍﾟｰﾝ ﾀﾞﾝﾀﾞﾀﾞﾝ 制作費(映像回り) 利益6,052,083円）
Next: —

## 2026-10-05T09:02:58
Status: done
What: 自動パイプラインが2026-09分のCAS実績を確定日を迎えて自動取得。91行、振替利益合計0円、利益スプリット9行反映。file1/file2へ追記完了。クライアント名マッピング: 自動登録したクライアント名変換:
  ・(株)ﾄﾗｽﾄﾊﾌﾞ → ﾄﾗｽﾄﾊﾌﾞ
  ・日本たばこ産業(株) → 日本たばこ産業
要確認(自動登録せず、新規クライアントの可能性):
  ・MBC Game Studio Ltd（SP1 20269月 MGS Launch PR (Japan) 利益-61,410円）
  ・NISSIN FOODS(U.S.A.)Co.,Inc.（SP2 20269月 日清食品 米国ｷｬﾝﾍﾟｰﾝ ﾀﾞﾝﾀﾞﾀﾞﾝ 制作費(映像回り) 利益6,052,083円）
Next: —

## 2026-10-05T09:10
Status: done
What: ユーザー「CASのデータ更新始めて」→9:00過ぎに手動実行し9月分取り込み完了(09:02の定時実行と重なったが重複ガードでスキップ、二重追記なし)。CSV111行→変換91行、スプリット適用後97行。売上397,162,120/売上総利益57,456,572円がCSV変換後・file1(GBC CAS実績_FY22 TO DATE.xlsx)・file2(final20261005.xlsx)で完全一致。file1のP列(DATEVALUE)は97行全て数式入り・再計算後2026/9/1→9/3修正の本番初回検証OK。振替利益0円。クライアント名自動登録2件(ﾄﾗｽﾄﾊﾌﾞ、日本たばこ産業)、要確認2件(MBC Game Studio Ltd、NISSIN FOODS(U.S.A.))。スプリット未マッチ10件はログ上の通知(他月分依頼と推定、未精査)。
Next: 要確認クライアント2件のマッピング判断はユーザー。

## 2026-10-05T09:08
Status: done
What: (1) 新規クライアント登録: ユーザー指示で MBC Game Studio Ltd / NISSIN FOODS(U.S.A.)Co.,Inc. を独立クライアント(調整後名=元名、C列CAS=Y)としてClient Name_CAS_SF_FY22 TO DATE.xlsx Listの1184/1185行に追加→再計算、未登録0件。(2) 「未マッチ10件」は管理表の他月(6-8月)依頼を全件未マッチ扱いしていたノイズ。9月依頼3件(ホーユー H10-2608042240 -1,416,249 SP2→AP2 / MBC H10-2609000051 SP1→SP1・AP2折半 / バンナム H10-2609046603 AP2→SP2・SP1・AP2)は全て正しく反映済み。cas_monthly_pipeline.pyで当月依頼のみ未マッチ判定、cas_pipeline_lib.pyで未マッチ0なら古い「利益スプリット確認」シートを削除するよう修正。本番2ファイルからノイズシート削除、9月97行/売総57,456,572円・P列再確認OK。バックアップ: Archive - Data for Tableau/20261005/ (_01付き)。
注意: MBCは依頼元金額2,380,460に対しCAS実績売総2,319,050で、差額-61,410がSP1に残る(合計は不変)。ユーザーに報告済み。

## 2026-10-05T09:15
Status: done
What: 「PowerBI反映と各部GMに送るExcelは出来ているか」→ PowerBIはService定時更新(平日11:30/17:00)待ちでまだ未反映(9時台時点)。GM送付用Excel=パイプラインが作るCAS集計 final<日付>.xlsx(8月分も9/2にfinal20260902を「集計済みExcel」として山本高さんへ送付→山本さんが各GMへ転送する運用、メール履歴で確認)。final20261005はopenpyxl保存でピボットのキャッシュ値が空だったため、Excel(AppleScript open→refresh all→save)で全更新。Rev/Sales YTD_Pivotの9月列が部別合計含め一致(売総57,456,572/売上397,162,120)。Combinedシート(1-5月のみ)とClient Name_Pivot(空)は前版9/11と同じ既存状態のため触らず。更新前コピー: Archive - Data for Tableau/20261005/..._before_pivot_refresh.xlsx。送付メール用の9月利益ランキングTOP8を作成しユーザーへ提示(送信はユーザー本人)。
Next: 11:30以降にPowerBI反映確認。ピボット更新をパイプラインに組み込むかは未提案。

## 2026-10-05T09:20
Status: done
What: ユーザー指示「MBCは折半指示なので元金額・スプリット金額を修正しPowerBI/Excelも修正」。CAS実績売総2,319,050(売上3,619,050-原価1,300,000)に合わせ、①GBC利益スプリット管理表 Requests 13行目 元金額H=2,319,050、J/L=1,159,525(差額0のまま、SplitRequestsテーブルA1:S14維持)②GBC CAS実績_FY22 TO DATE.xlsx Raw YTD N6162=0/N6163(SP1)=N6164(AP2)=1,159,525③final20261005.xlsx Raw YTD N1276-1278同様+ピボット再更新。全てExcelアプリ(AppleScript)で直接セル編集(openpyxl経由を避け書式・テーブル・ピボット保全)。9月合計57,456,572不変、部別SP1 4,711,283/AP2 10,384,433に。青字(FF0000FF)・P列DATEVALUE維持確認。バックアップ: Archive - Data for Tableau/20261005/*_before_MBC_fix.xlsx。
Next: PowerBIは次回Service定時更新(11:30/17:00)で反映。

## 2026-10-05T09:40
Status: done
What: ユーザー質問「ホーユー9月スプリット依頼は-140万なのにExcelで-49万」→スプリット(H10-2608042240、SP2→AP2 -1,416,249)は正しく適用済み。Rev YTD_PivotでAP2を展開したホーユー行=-488,022は、同月AP2の別案件(H10-2609001183 シエロ9月分 +578,227、H10-2609002988 VPON広告 +350,000)との合算。SP2側ホーユー計-1,398,245は6月/8月実施分の赤伝(-945,651/-496,020等)による。
副次発見・修正: 9月追記97行が全て青字になっていた(append時に直前行=8月スプリット行の青字書式を継承)。cas_pipeline_lib.pyで非スプリット行はfont.color=Noneに戻すよう修正(bak_20261005_01)、scratch検証OK。本番2ファイルの9月行をExcel(AppleScript)で黒字化+スプリット9行のみ青字に戻し、合計57,456,572・P列不変を確認。final20261005のRev YTD_PivotはAP2が展開状態で保存されている(ユーザー閲覧時の操作と推定、未変更)。

## 2026-10-05T12:45
Status: done
What: 管理表Requests 14行目に資生堂 2026 Q3 Global Media Central Fee(H10-2511043790、9月、AP2→AP3全額 3,119,976、小川GMメール依頼)が追加→事後反映。CAS実績のQ3行売総は3,049,995で、差額69,981は同月AP2計上のQ2案件(H10-2511043776 9月 +69,981)分=依頼額はQ2残分込み。パイプライン同ロジック(Q3行N=3,049,995-3,119,976=-69,981、直下にAP3 +3,119,976行を挿入、両行青字)で反映→AP2純増減0/AP3 +3,119,976。GM送付用はfinal20261005を開いていたExcelを閉じ(保存済み確認)、final20261005_01.xlsxとして新規作成・ピボット更新。file1(GBC CAS実績_FY22 TO DATE.xlsx)はRaw YTD 6118/6119行に同処理(P列DATEVALUE維持)。9月98行・売総57,456,572・売上397,162,120不変、AP2 10,384,433→7,264,457、AP3 6,125,000→9,244,976。9月TOP8再集計(資生堂Q3がAP3 3,119,976で5位)。バックアップ: Archive - Data for Tableau/20261005/*_before_shiseido_Q3.xlsx。
Next: PowerBIは17:00のService定時更新で反映。

## 2026-10-05T12:50
Status: done
What: ユーザー「ok, task end」で資生堂Q3事後スプリット反映セッション終了。
Next: 17:00 PowerBI定時更新でAP3 9,244,976を確認(任意)。
