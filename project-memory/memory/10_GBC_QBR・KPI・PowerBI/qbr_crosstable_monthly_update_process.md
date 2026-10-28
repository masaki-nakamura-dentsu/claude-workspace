---
name: qbr-crosstable-monthly-update-process
description: "The monthly '受発注設定リスト→Prep_CAS X SF Crosstable.xlsx' update (manual's step 3) — what 'run the automated process' for this task means, how to do it, and what it is NOT (not the same as [[cas_setting_request_powerautomate_flow]] or [[cas_csv_download_automation]])"
metadata: 
  node_type: memory
  type: project
  modified: 2026-09-02T08:13:30.028Z
  originSessionId: 1e53c218-bea5-4ac3-ba3d-613205a64493
---

## What this task is
Every month, 業務管理部の青山夏子さん(gzc408@dentsu.co.jp)がメールで「【N月】受発注設定リスト」(添付: `☆【20XX】受発注設定リスト.xlsx`, シート`受発注設定リスト`, ヘッダ行2)を送ってくる。これは`受発注ヘッダNo.`(CAS側キー)と`案件ID`(Salesforce側キー)の対応表の元データで、QBR/ABR資料更新マニュアル(`.../QBR作成/(Manual) GBC QBR_Tableau20260401.docx`)のセクション3「元データの更新(受発注設定リスト...)」に手順が書かれている。マニュアル自体は「ChatGPTでやってもらう」半自動フローを想定しているが、2026-09-02にClaude Codeで完全自動化して実行した(ユーザーが「3のところを自動化してもらったことがある」と言及したのはこの作業)。

**これは[[cas_setting_request_powerautomate_flow]](Formsの空欄バグ調査)や[[cas_csv_download_automation]](CAS実績CSVの月次取込)とは別物** — 名前が紛らわしいので次回混同しないこと。前者はFormsのDIAS担当者欄が空になる不具合調査、後者はCAS実績データそのものの取込パイプライン。このメモは「受発注設定リストの新規行をCrosstableに追記する」タスク専用。

## Where to find the source email
`outlook list "受発注設定リスト"` (要 `outlook login`)で見つかる。**ローカルのOutlookエクスポート(`~/OutlookExport/parsed_emails.jsonl`)には頼らないこと** — 2026-09-02時点でこのファイルの同期が壊れており最新メールが反映されない([[outlook_email_sync_onedrive_deadlock_20260902]]参照)。添付DLの手順は[[outlook_cli]]の「添付ファイルのダウンロード」セクション参照。

## The process (what "自動処理" does)
1. `outlook list "受発注設定リスト"` → 最新(今月分)を`outlook read`で確認 → 添付`.xlsx`をダウンロード。
2. 対象ファイル: `.../GBC戦略企画部_GBC設定実績・見込/QBR作成/Prep_CAS X SF Crosstable.xlsx`のシート`Crosstable`(列: A=Year of 設定日, B=Month of 設定月, C=受発注ヘッダNo., D=案件 ID/Item ID, E=得意先名, F=受発注ヘッダ件名, G=Check 1(`=LEN(C)`), H=Check 2(`=LEN(D)`))。
3. 既存Crosstableの列C(受発注ヘッダNo.)を集合化し、ダウンロードした受発注設定リストの列U(受発注ヘッダNo., ヘッダ行2, データ行3〜)を1行ずつ突合。`None`/`"0"`は除外(注記行・金額変更行など)。
4. 新規行(既存に無いヘッダNo.)について、列H(得意先名)・列I(受発注ヘッダ件名)・列Y(案件ID)を取得。**列Yは結合セルが多い**ので、`ws.merged_cells.ranges`から結合範囲を解決し左上セルの値を使うこと(そのまま読むと`None`になる行が大量に出る)。**案件IDが18桁で末尾`YAV`の場合は末尾3文字を削って15桁にする**(マニュアル記載のルール)。
5. Year/Month of 設定日は、受発注設定リストの列A(セル値が日付シリアル値の行=その月のセクション開始マーカー)から、対象行が属する月を逆算する(例: 2026-01-01マーカー行以降〜2026-02-01マーカー行未満は「2026年1月」)。
6. 新規行をCrosstableの末尾に追記(A〜F=値、G/H=`=LEN(Cn)`/`=LEN(Dn)`の数式で既存行と揃える)。
7. **編集前に`Archive - Data for Tableau/Prep_CAS X SF Crosstable_<今日の日付>.xlsx`へバックアップ**(Tableauがこのファイルを絶対パス参照しているため、[[qbr_2026q2_null_join_troubleshooting]]の教訓通りファイル名は変更せず原本を直接編集)。
8. 保存後、[[openpyxl_empty_v_tag_corruption]]の`fix_and_recalc()`(`~/CASExport/_xlsx_recalc_fix.py`)を必ず実行し、**その後に「本当に閉じたか」を`get name of every workbook`で確認**(2026-09-02は1回目の`close`が効かず、手動で`save`→待機→`close`を再実行して初めてキャッシュが正しく書き込まれた — 詳細は[[openpyxl_empty_v_tag_corruption]]の新セクション参照)。
9. Check1/Check2が異常値(14/15以外)の行があれば、6月分の前例(受発注ヘッダNo.が「0」の行を青山さんに確認)のように青山さんへの確認メールが必要になる可能性がある — ユーザーに報告し、送るかどうかは必ず確認を取ること(このタスク自体には送信は含まれない)。

## 2026-09-02実行結果(初回)
【8月】受発注設定リスト(715行)を処理。既存2,405行→2,464行(59件追加)。全59件ともCheck1=14/Check2=15で異常なし(青山さんへの確認メール不要)。重複ヘッダNo.が2件(H10-2608008273×2、H10-2608017034×3)source側にあったが、既存Crosstableにも同種の無害な重複が約210組確認済み([[powerbi_migration_gbc_dashboard]]参照)なのでそのまま追加。

## 恒久スクリプト化 完了(2026-09-02、同日中)
ユーザーから「来月以降も同じ処理をするのでスクリプト化して」と依頼され、`~/CASExport/crosstable_monthly/update_crosstable.py`として実装済み。**毎月これを実行するだけでよい**(べき等 — 既に反映済みの受発注ヘッダNo.は自動スキップされるので同じ月に何度実行しても二重追加されない)。

**構成**:
- `~/Scripts/outlook_cli/download_latest_settei_list.js` — 検索結果を上から最大10件たどり、件名が「Re:」「FW:」で始まらない(=返信ではない原本)かつ`.xlsx`添付があるメールを見つけて右クリック→「ダウンロード」で保存。Playwright/Outlook Web自動化特有の再現性の低さ(SPAの再レンダリングでリストが一時的に空になる等)への対処として、各候補メッセージを開く直前に検索をやり直す設計にしている。
- `update_crosstable.py`側でもこのnodeスクリプト自体を最大3回リトライする(1回の起動全体をやり直す方式 — 個々のステップを個別に頑健化するより信頼性が高いことを確認済み、[[continuous_data_capture_setup]]と同じ思想)。
- ダウンロード後は本メモリの「The process」節と同じロジック(結合セル解決、YAV接尾辞除去、月マーカー逆算、Check1/2数式付き追記)をPythonで実行し、バックアップ→保存→`fix_and_recalc`→Excelが実際に閉じたかの確認、まで自動化済み。

**2026-09-02の実行結果**: 8月分に対して再実行し、正しく「新規0件」(既に同日早い時間帯に手動で59件追加済みだったため)を検出・べき等性を確認。

**既知の注意点(次回このスクリプトを触るときのために)**:
- Outlook Webは`outlook.office.com`から`outlook.cloud.microsoft`へドメイン移行済み。`~/Scripts/outlook_cli/lib.js`のタブ再利用ロジックがこれに未対応で、実行するたびに新しいタブが増殖し続けていた(今回11個の重複タブを発見・削除)というバグを本タスク中に発見・修正済み([[outlook_cli]]参照)。この修正は`outlook`コマンド全体に効くので、他のOutlook自動化タスクにも恩恵がある。
- 実行にはExcel.app・shared bot browser(d14461ならport 9226)・Playwright環境が必要。完全headless/cronでの無人実行は未検証(Excelの実ウィンドウ操作が絡むため)——現状は「ユーザーまたはClaudeセッションが月1回起動する」運用を想定。

## Not yet done
- Check1/Check2異常時の「青山さんへの確認メール」自動送信は未実装(意図的 — 対外メールは要確認)。
- 完全無人cron化(launchd等)はしていない — 添付が来るタイミングが月によって不定なため、現状はオンデマンド実行が現実的。

## 2026-10-07 自動化拡張(中村さん依頼:「CAS更新時・受発注設定リスト到着時にCrosstable追加を忘れない」)
- 背景: 9月CAS実績(10/5取込)だけ入りCrosstableが9/11のまま→KGIKPI案件別内訳で(空白)47M([[feedback_kgikpi_blank_anken_means_crosstable_lag]])。
- `update_crosstable.py --auto`: 前月分(state `crosstable_state.json` の last_list_month 未満)かつ `~/OutlookExport/parsed_emails.jsonl` に「【N月】受発注設定リスト」原本(Re/FW/自動応答除外、全角数字NFKC)が届いている時だけBotブラウザでDL→追記→PBI更新(`~/PowerBIExport/pbix/refresh.py start`)→Teams通知。`--force`でメール確認省略、`--fix-ids`は既存行のID補完のみ。
- 起動: launchd `com.nakamura.crosstableupdate` 毎日10:20/14:20/17:20(処理済み月は即終了)+ `cas_monthly_pipeline.py` process_month末尾から `--auto` 呼び出し(結果をTeams完了通知に併記)。
- **受発注設定リストの保存先(中村さん指定)**: `QBR作成/☆受発注設定リスト/☆【YYYY】受発注設定リストYYYYMMDD.xlsx`(YYYYMMDD=メール受信日、既存は上書きしない)。10/2受信分は中村さんが手動保存済み。
- **案件ID欠損の自動補完**: 案件IDが`a1h`始まり15桁未満なら、Dropbox `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し/（設定突合用）SF案件リスト/` の最新DL(1日2回自動)で前方一致→複数なら得意先名(NFKC・株式会社/(株)除去)で絞り、一意なら列D(15桁)と列I(18桁)を補完。決まらなければTeamsで中村さんに確認依頼。空得意先の候補が全一致する罠を修正済み。
- 2026-10-07: 9月分85件追加、第一ライフ メディア費4件(H10-2609037295/97/301/305)の欠損ID `a1hGA00000A0Q1`→`a1hGA00000A0Q1B`(中村さん提示と一致)で補完。state=2026-09。
- バックアップは同日2回目以降 `_01` 連番(以前は同名上書きしていたので修正)。スクリプトの旧版は `.bak_20261007`。
