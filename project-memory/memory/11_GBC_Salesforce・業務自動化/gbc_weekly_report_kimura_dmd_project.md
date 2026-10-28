---
name: gbc-weekly-report-kimura-dmd-project
description: 毎週水曜夜にSalesforce週報とGBC知見を突合して木村剛DMDにまとめを送るプロジェクト。GBC知見インデックス構築済み、パイプラインスクリプト構築済み、実データでの検証が次のステップ
metadata:
  type: project
  originSessionId: a36d9ee0-bcf1-47ae-adda-432964be5953
  modified: 2026-08-12T02:48:40.914Z
---

## 背景・目的
中村さんが2026-08-11に依頼: 毎週水曜夜にSalesforceの週次レポートから概要・アップデート内容を読み取り、GBCの知見（気をつけるところ・関連知見）を加えたまとめシートを**木村剛DMD（tkimura@dentsu.co.jp）**にメール送付するフローを作りたい。GBC知見自体も他プロジェクトで再利用できるよう索引化したい、というのが二本立ての依頼。「進め方を相談させてください」という相談ベースの依頼だったが、AskUserQuestionで4点合意の上、実装まで着手した。

## 合意事項(2026-08-11、AskUserQuestion)
- 宛先: 木村剛さん tkimura@dentsu.co.jp で確定(GBC AI業務活用PJ等で頻繁にやり取りしている人物)
- 実行スタイル: 半自動（水曜夜リマインダー→トリガーフレーズでClaude実行、Salesforce認証コードだけ都度入力）を選択。完全無人クラウド自動化は今回は見送り
- 出力形式: Excel表形式
- GBC知見インデックスの作り方: Claude主導でまず草案作成 → 後でユーザーレビュー

## 技術的な前提（確認済み）
- **アクセス**: SharePoint(GBCarekoko)・Salesforce(dgx.lightning.force.com)とも、共有Botブラウザ(このMac=port 9227, `~/.chrome-profiles/timetree-bot`)で**追加ログイン不要**（既存SSOセッションで通る）。[[shared_bot_browser]]参照
- **GBC知見サイトの正体**: [[gbc_department_move_2026]]で言及されていた「GBCアレココ」ハンドブックそのもの。SharePointリストとして既に構造化されている（ゼロから分類体系を作る必要はなかった）
- **既存の分類体系（そのまま流用）**: `KnowledgeTagCategory`(7カテゴリ: 情報の種類/ソリューションカテゴリ/メディアカテゴリ/業種/エリア/ブランド/言語) × `KnowledgeTags`(80タグ)
- **知見データ**: `Knowledges`リスト253件（title, clientName, market, summary, notice(要注意事項), tags, publicStart等）、`教えてGBC`リスト54件（Q&A: title, questionBody, answer, postedDate）。SharePoint REST API (`_api/web/lists/getbytitle(...)/items`) を認証済みページ内fetchで取得可能
- **Salesforceレポート**: ID `00O7F00000AmEiQUAV`「GBCすべての週報：部長会進行用(過去１週間・優先度高)」。列構成: 部署名/Dept., GBC案件/Items:案件名/Item title, フェーズ/Phase, 商流/Business flow, クライアント/Client, 概要/アップデート(5W1H)/Report(5W1H), ネクストステップ(5W1H), 責任者(GBC), 地域/Region, 関係会社/Partner companies, Group売上/Turnover(JPY), Group売総/Revenue(JPY), GBC取設定/SETTEI TO(JPY), GBC営業費/Business expenses(JPY), GBC貢献売総(AB見込), 貢献度/Contribution ratio, 完了日(予定)
- **Salesforce Analytics REST API (`/services/data/vXX.0/analytics/reports/...`)は401（セッションcookieだけではOAuthトークンが無く使えない）**。DOM直接スクレイピングも、レポートグリッドが仮想スクロールテーブル(`data-grid-table`、15行程度しかレンダリングされない)のため171件などの全件取得には不向き。**エクスポート機能(Excel)を使うのが正解**（[[salesforce_report_download_automation]]と同じ結論、ただし今回は共有Botブラウザ経由で別レポートID向けに再構築）
- 2026-08-12朝の時点でこのレポートは「過去1週間・優先度高」フィルタで**該当0件**だった（週の後半にかけて活動が随時登録されるため。実行は夜が確実）

## 構築済み成果物
### GBC知見インデックス（`~/Library/CloudStorage/OneDrive-電通/GBC戦略企画部_知見インデックス化・週次まとめ/`）
- `gbc_chishiki_taxonomy.json`, `gbc_chishiki_knowledges_index.json`(253件), `gbc_chishiki_oshietegbc_index.json`(54件), `README.md`
- 再取得スクリプト: `~/.local/share/claude-playwright/build_gbc_index.js`
- **他プロジェクトでも即座に使ってよい**: 何かの案件で「GBCの知見で気をつける点は？」と聞かれたら、まずこの2ファイルをクライアント名/エリア/業種タグでマッチングして提示する
- 知見ギャップ（2026-08-11時点）: 業種別では交通・レジャー(10件)以外ほぼ薄い。エリア別ではグローバル/日本/中国/台湾/北米以外が手薄

### 週報パイプライン（`~/GBCWeeklyReport/` — 2026-08-12に会社Mac引き継ぎのためDropbox `.claude-sync/Scripts/GBCWeeklyReport/`に実体を移動、各Macの`~/GBCWeeklyReport`はシンボリックリンク）
- `download_step1_export.js` / `download_step2_enter_code.js` — Salesforceエクスポート自動化(Node/Playwright、`NODE_PATH=$HOME/.local/share/claude-playwright/node_modules`で実行)
- `build_summary.py`（`/usr/bin/python3`で実行、他のpython3にはopenpyxl未インストール）— ダウンロードしたxlsxをGBC知見インデックスと突合し、クライアント名一致/エリア一致/文字n-gram類似度でスコアリング、「GBC知見アドバイス」列を追加した`output/GBC週報まとめ_<日付>.xlsx`を生成。実行のたびに`archive/weekly_snapshots.jsonl`に案件を追記し、次回以降の**同クライアント過去案件（類似事例）検索**にも使う（ユーザーが2026-08-11に追加提案したアイデア）
- ダミーデータでのロジック検証済み（2026-08-12）: 台湾PizzaHutの架空ケースで、実際の「教えてGBC」にある台湾PizzaHutのPerformanceベース契約に関する実在のQ&Aを正しく最上位マッチさせた。UNIQLOのケースでは実在の「クライアントやBPに出す前に要事前相談」という注意事項も自動表示された。マッチングは簡易n-gramなので時々弱い誤マッチも出る（人の目でのチェックは必要）
- README: `~/GBCWeeklyReport/README.md`に全体フロー記載

## 2026-08-12: 実データでのエンドツーエンドテスト実施（送信はしていない、下書きまで）
中村さんから「過去のレポートでテストしたい。今仮で過去20日間のレポートで開いたので。これをテストでメール下書きまで作ってみて」と依頼され、実データで一連の流れを検証した。

- **Salesforceのメール認証コードについて標準ルール確立**: 「Salesforceのエクスポートは例外で、あなたが私のメールをチェックしてその数字を入れてよいです。私の許可は不要です」と明示的に許可を得た。今後この用途に限り、`outlook read`等でコードを自分で取得し都度の許可なく入力してよい。
- **実際のSalesforceエクスポートの罠が2つ判明**:
  1. **エクスポートは保存済みレポート定義の「現在の実行状態」を使う。UIで一時的にフィルタを緩めても、追加アクション→エクスポートをそのまま押すと元の保存済みフィルタ(この場合「過去7日間・優先度高」)に基づいてエクスポートされてしまい、UI上に見えている一時フィルタ後の件数(33件)は反映されない。** 対策: `条件`パネルを開いたまま(パネルが開いた状態だと追加アクションのクリックが正しく効かないことがあるため)一時フィルタを再適用→**必ずパネルを閉じてから**エクスポートする、という手順を踏む必要がある。
  2. **「詳細のみ」(Details Only)形式は、実体はHTMLテーブルで、しかも`charset=ISO-8859-1`と誤宣言されているため日本語(2バイト文字)が全て`?`に文字化けする(実データ破損、見た目の文字化けではない)。** 「フォーマット済みレポート」(デフォルト)は正真正銘のXLSX(zip)で日本語も正しく保持される。**今後は必ず「フォーマット済みレポート」を使う**。
- **「フォーマット済みレポート」のExcel構造が判明**（`build_summary.py`はこれに対応済み）: 1〜13行目はタイトル・検索条件のヘッダーブロック、14行目が本当の列見出し行、15行目以降がデータ。**グループ化されているため部署名/Dept.・案件名/Item title・フェーズ/Phaseの3列は各グループの先頭行にしか値が入らない**(2行目以降はNone) → 前方補完(ffill)が必須。33件のデータで確認済み、末尾に余計なフッター行は無い。
- **マッチングロジックの実データバグを発見・修正**: ①クライアント名の部分一致判定が「ー」(値なしプレースホルダー)を「アサヒビール」等の長音記号と誤マッチしていた → 2文字未満やプレースホルダー文字列(`ー`,`-`,`N/A`等)をマッチング対象から除外する`is_meaningful_name()`を追加。②n-gram類似度が緩すぎて無関係なQ&Aが多数ヒットしていた → 最小共有bigram数(4個以上)・スコア閾値を引き上げ、未回答のQ&A(`answer`が空)は除外。修正後、33件中16件に関連知見が付き、17件は正しく「知見ギャップ」として除外されるようになった。花王ベトナムの案件では実際に木村DMD本人が過去共有した資料が最上位ヒットするなど、質的にも妥当な結果が得られている。
- **outlook_cliの添付機能が新UI(`outlook.cloud.microsoft`)で壊れていたのを発見・修正**: 詳細は[[outlook_cli]]参照。「挿入」タブに移動していた添付ボタンを`button[label="添付ファイル"]`で掴むよう修正し、木村剛さん宛の下書き（宛先・件名・本文・添付ファイル全て）を`--dry-run`で正常作成できることを確認した（実送信はしていない）。

## 2026-08-12: 会社Mac(d14461)への引き継ぎのため移設
中村さんが「一旦会社Macにこの作業を移行するので、このPCでの作業を切り上げます」と明言。個人Mac(ICPTokyo2022)ローカルにあった`~/GBCWeeklyReport/`をDropbox `中村正樹/.claude-sync/Scripts/GBCWeeklyReport/`に実体移動し、このMacの`~/GBCWeeklyReport`はシンボリックリンクに変更([[outlook_cli]]と同じパターン)。デバッグ用の一時スクリーンショット・調査用スクリプトは削除済み、本番用の3スクリプト(download_step1/2, build_summary.py)とREADME・archive・downloads・outputのみ残した。

**d14461で動かす前に必要な調整（README.mdに詳細記載済み）**:
- 共有Botブラウザのport/profileが違う（[[shared_bot_browser]]: d14461=port 9226・`/Users/d14461/SalesforceExport/browser_profile`）。3つのdownload系スクリプトは`GBC_BOT_PORT`環境変数で切り替えられるよう修正済み（`GBC_BOT_PORT=9226 node download_step1_export.js`のように実行する）
- d14461にNode/Playwright環境([[claude_playwright_setup]])があるか未確認、無ければ導入が必要
- d14461のどのpython3にopenpyxlが入っているか未確認（ICPTokyo2022では`/usr/bin/python3`だった）
- GBC知見インデックス(OneDrive-電通経由)と週次アーカイブ(`archive/weekly_snapshots.jsonl`、Dropbox経由)はどちらもMac間で自動共有されるので、これらは移設不要・そのまま使える

## 2026-08-12: d14461(会社Mac)側の環境検証完了
水曜朝、`~/GBCWeeklyReport`シンボリックリンクを作成し、README記載の前提条件を確認:
- Node/Playwright(`~/.local/share/claude-playwright`)は既にd14461にセットアップ済みだった
- python3は複数系統あるが、デフォルトの`python3`(`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`)にopenpyxl 3.1.5が入っており使える。`/usr/bin/python3`にはopenpyxlなし
- 共有Botブラウザ(port 9226)は既に起動中で追加ログイン不要
- `GBC_BOT_PORT=9226 NODE_PATH=$HOME/.local/share/claude-playwright/node_modules node download_step1_export.js` → `download_step2_enter_code.js`(コードはoutlook_cliで自メールから自動取得、[[feedback_salesforce_verification_code_standing_permission]]の許可通り)→ `python3 build_summary.py` を実際にフルパイプライン実行し、d14461上でエンドツーエンドに動くことを確認した。
- この時点(水曜11時台)は保存済みフィルタで0件（過去実績通り、活動は水曜日中に随時登録されるため）。出力Excelのヘッダー行・「GBC知見アドバイス」列の追加は正しく機能した。0件のテスト用ダウンロード/出力ファイルはその場で削除済み（本番実行ではない一時確認のため）。
- **d14461側の残作業はこれで解消**。本番の実行だけが残っている。

## 2026-08-12: マッチングロジックの品質検証・バグ修正（本番実行前の確認依頼への対応）
中村さんから「まだテストなので、知見がちゃんと意味のあるものになっているかを先に確認して次に進みます」との指示。8/11の実データ(33件)の出力を再検証し、2つの実バグを発見・修正した：
1. **「電通」への誤マッチ**: クライアント名部分一致ロジックが、知見側の`clientName`が単に自社名「電通」であるケースを、summary中に「電通」を含む無関係な案件（電通シンガポール等）に誤って「クライアント名部分一致」としてヒットさせていた。`GENERIC_OWN_NAMES`除外セット（電通/dentsu/Dentsu/DENTSU等）を`is_meaningful_name()`に追加して修正。
2. **英字・日本語の頻出2-gramによる誤爆**: `keyword_overlap_score`の文字2-gram類似度が、(a)英語部分の"an","in","it"等の頻出アルファベット2文字組み合わせ、(b)「です」「ます」「対応」「実施」「電通」等の日本語定型句、を「内容の類似」として拾ってしまい、KDDI・MSG・ARCHION等の短い定型文的な週報コメントに無関係な「教えてGBC」Q&Aが大量にヒットしていた（ある空欄クライアント行では英語人名の羅列だけで類似度40%と出るケースも）。`_ASCII_BIGRAM`除外パターンと`_STOPWORD_BIGRAMS`除外セットを追加、oshieteのマッチ閾値も0.15→0.20に引き上げて修正。
- **効果**: 33件中「知見あり」判定が16件→5件に減少。残った5件（サンリオ、花王×2、富士通、MSG×1）はいずれもクライアント名の具体的一致か、妥当性の高い内容一致で、質的に大幅改善を確認した。
- 検証中に`archive/weekly_snapshots.jsonl`へテスト再実行分の重複が2回発生（33件→66件）したが、その都度dedupeして33件に復元済み（`_saved_at`が異なるだけの完全重複行を除去）。
- 出力ファイルは`output/GBC週報まとめ_20260812.xlsx`に保存済み（修正後のロジックで生成、中村さんへの提示待ち）。

## トリガーフレーズ確定（2026-08-12）
**「木村さんへGM会週報のレポートをまとめて」** — これが本フロー（GBC週報×知見まとめ→木村DMD送付）専用のトリガーフレーズ。[[salesforce_report_download_automation]]の「業況見通し用のSalesforceをダウンロードして」とは別物、混同しないこと。

## 残作業（次回セッション）
1. **本番の週次実行はまだ実施していない**（今回はマッチングロジックの品質検証が主目的。中村さんが修正後の`output/GBC週報まとめ_20260812.xlsx`の中身を見て、知見の質がOKと判断したら次に進む）
2. ~~d14461での動作確認~~ → 2026-08-12完了
3. Outlookカレンダーへの水曜夜リマインダー設定はClaudeには書き込み権限がないため、中村さん本人が設定する必要がある（[[salesforce_report_download_automation]]の業況見通しと同じ制約）
4. n-gramマッチングは大幅改善したが、根本的には簡易ロジックであることに変わりはない（送付前に人の目でのチェックを推奨、と毎回のメール文面にも明記している）
5. 木村DMDへの送付前に、毎回内容を中村さんに確認してもらう運用を継続する（今回もdry-run下書きどまりで実送信はしていない）
6. 8/11作成の木村さん宛テスト下書き（件名「【テスト】GBC週報×GBC知見 週次まとめ」）は中村さんの指示で**そのまま残す**ことに決定（2026-08-12確認済み、削除しない）

## 関連メモリ
[[gbc_department_move_2026]]（アレココの位置づけ）、[[salesforce_report_download_automation]]（エクスポート自動化の先行事例、別レポート/別マシン）、[[shared_bot_browser]]（共有Botブラウザ）、[[outlook_cli]]（送付に使うCLI）
