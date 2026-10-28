# GBC クレデンシャル マスタースライドバンク構想(新規プロジェクト)

## 2026-09-30T08:40:00Z
Status: in progress(1本目のマスターデッキのカタログ化完了、Copilot実地テスト待ち)
What: 中村さんから、OneDrive「GBC - 02．クレデン共有チャネル」(116ファイル・28GB)の
既存クレデンシャルスライドを再利用する新方式の相談を受けた。当初案(スライド1枚ずつ
事前レンダリング)を実地調査(du/find/python-pptxでのスライド数カウント)で検証したところ、
動画埋め込みの巨大ファイル(各国拠点クレデン、個別1.8〜2.9GB)を除いても85ファイル
合計6,008スライドあり、「全部入り1本」は非現実的と判明。議論の末、以下の方式で合意:
- テーマ別に複数の「マスターPPTX」を用意(1本ずつ丸ごと保管、ChatGPT Skillにはアップロード
  しない=バイナリアップロード制限を回避)
- Agency OSはカタログ(Markdownカード)からスライド番号を判断し、「残すスライド番号のみを
  列挙する」形式の指示文を提示
- ユーザーはPowerPointでマスターデッキを開き、Copilot/ChatGPTアドインにその指示文を貼り付けて
  該当スライドだけが残ったデッキを得る(python-pptxでのスライドコピー実装が不要になる、
  ChatGPT Skillのバイナリアップロード制限も無関係になる)

**1本目: 電通ケイパビリティプレゼン資料（日本語 2026年版）.pptx(256枚)をカタログ化**。
markitdownで全文抽出→章立て17区分に分類→クライアント実名が入るスライド19枚を検出し
CLIENT_NAME_WARNINGを付与(自動検出のため完全ではない旨を明記)。重要な副発見2件:
(1)スライド3に元資料自身の「クライアントの困りごと→推奨パート」対応表が存在し、Agency OSの
選定ロジックの出発点としてそのまま使える。(2)スライド2が「プレゼン時は削除してください」という
制作者向け説明ページ、スライド3・4も内製向け(推奨表・ナビゲーション注記)と判明したため、
ALWAYS_EXCLUDEとしてカタログに明記。
配布送付可能版(253枚)との差分も確認: スポーツ事例3枚の削除+1枚のクライアント名匿名化
(KIRIN×日本サッカー協会→社名なし)で、単純な新旧重複ではなく意図的な社外配布版と判明。
カタログは`GBC-Knowledge/slide_bank_source/slide_catalog_capability_deck_jp2026.md`に保存。
markitdownは会社Mac未導入だったため社内プロキシ経由でpip install済み(既知の
feedback_d14461_pip_needs_corporate_proxy.mdパターンを踏襲)。
Next: (1)中村さんに実際にこのマスターデッキ+サンプルのキープリスト指示文をPowerPoint
Copilotで試してもらい、複数スライド番号指定での削除が正確に動くか検証(まだ未検証の
技術的前提)。(2)問題なければ残り84ファイルのカタログ化に着手(テーマ別マスター2本目
以降の選定も含む)。(3)Agency OS Skill側(SKILL.md等)にこの新カタログの参照ルールを
追記。

## 2026-10-23 方針変更(週次カタログ運用)+URL方式の検証
Status: in progress(手順1完了)
What: 中村さんと合意。SharePointにマスターは置かず、カタログをAgency OSの知見に取り込み、回答時に元ファイルのURLを提示する。週次でチャネルを差分チェックして更新分だけカタログ化・反映。
元フォルダ(ローカル同期): ~/Library/CloudStorage/OneDrive-電通/GBC - 02．クレデン共有チャネル (117ファイル/28GB)
**URL方式(検証済み)**: サイト https://esq365.sharepoint.com/sites/GBCarekoko ・ライブラリ Shared Documents ・フォルダ名=チャネル名。
 ファイル: `https://esq365.sharepoint.com/sites/GBCarekoko/Shared%20Documents/02．クレデン共有チャネル/<相対パス>?web=1` をURLエンコード(?web=1なしだとダウンロードになる)。フォルダは?web=1不要。共有ブラウザ(9226)で開けることを確認(ファイル→Office Web、フォルダ→一覧)。
Next: (2)残り84ファイルのカタログ化(ファイル概要カード+スライド詳細の2段、動画入り巨大ファイル除外)、(3)Agency OS取り込み+週次差分処理(launchd)。

## 2026-10-23 手順2完了: 全チャネル自動カタログ化
Status: in progress(手順3待ち)
What: SharePoint REST(_api GetFolderByServerRelativeUrl, 共有ブラウザ9226のpage.evaluate経由)で113ファイルのUniqueId/更新日/サイズ取得→ローカル同期ファイルをzipfileでslide XMLのみ読み(動画はスキップ、3GB級も数秒)→109ファイル(pptx100弱+pdf)をカタログ化。
成果物: GBC-Knowledge/slide_bank_source/credential_channel_20261023/ (credential_cards.md=ファイル概要カード92KB, slide_detail/*.md=スライド別タイトル+140字抜粋, manifest.json=UniqueId→更新日(週次差分用), errors.txt, scripts/{listfiles,build_catalog}.py)
URL: pptxはUniqueId方式 `.../_layouts/15/Doc.aspx?sourcedoc=%7BGUID%7D&action=default`(改名・移動に強い)、pdfはパス+?web=1。全種類ブラウザで開くこと確認。フォルダに固有権限なし(サイト継承=GBCメンバー)。アレココの教訓でカードに「URLは前後に半角スペース/Markdownリンクで」を明記。
除外: dentsuX Vietnam 2025.pptx(元ファイルが破損=ZIP末尾欠損、SharePoint上のサイズも同じ)、xlsx/docx/loop。
運用ルールPDF(2026/2/13): 社外秘・持出厳禁、事務局がファイル改名して格納、ナレッジサブリーダー会(月例)がアレココへ追加。
Next: 手順3 Agency OS取り込み(本番反映は中村さんOK後)+週次差分(manifest.jsonとUniqueId/更新日比較)のlaunchd化。

## 2026-10-23 手順3(途中): Agency OS取り込み+週次差分
Status: in progress
済み: (1)カタログを検索向けに作り直し(credential_channel_source/build_credential_pack.py: 資料カード1ファイル1枚+フォルダ別スライド一覧、各行に【資料名】、15行ごとにURL、運用ルール資料は除外、108資料)。出力 GBC-Knowledge/output/credential_channel_20261023_01/。
(2)ChatGPT Skill 反映済み v174(11ファイル+指示文 要件K追加 GPT作業/SKILL_20261023.md、照合一致)。反映前バックアップ output/skill_backup_20261023(v173)。
(3)Dify ナレッジ credential_channel_catalog(ID 71e8e7cd-3c1f-4e1f-a69a-685b943ff5ce)作成・11文書indexing完了。ワークフロー退避 output/dify_workflow_backup_20261023.json。
(4)週次スクリプト tools/weekly_credential_update.sh(SharePoint REST一覧→manifest差分→変更時のみSkill push+Dify replace/create→Teams通知)、credential_channel_source/{fetch_channel_listing,build_credential_pack,diff_manifest}.py。未実走。
未了: (a)Dify検索ノード配線 tools/dify_wire_credential_node.js --dataset 71e8e7cd... (b)Dify指示文 GPT作業/SKILL_Dify_for_paste_20261023.md を dify_prompt.js でテスト→公開 (c)weekly_credential_update.sh --force 実走確認(変更なしのはず) (d)launchd登録: auto modeがLaunchAgents書き込みを拒否→tools/install_weekly_credential.sh を会社Macで本人実行 (e)dentsuX Vietnam 2025.pptx破損を事務局へ。

## 2026-10-23 夕 手順3ほぼ完了
Status: 本番反映済み(残: launchd登録=本人実行、変更ありパスの実地確認)
- Dify: 検索ノード「知識検索 クレデン共有チャネル」(1792200000004、top_k8)配線、コード実行ノードはBP局(i)とクレデン(k)を合わせて1要素に(30要素上限エラー対策)。指示文 SKILL_Dify_for_paste_20261023.md(要件K)で下書きテスト2問OK(マレーシア/タカラトミー)→「20261023クレデン追加」で公開。
- 弱点: タカラトミー回答はチャネルのDoc.aspx URLでなくアレココ詳細URLを出した(アレココにも同資料があるため)。要観察。
- weekly_credential_update.sh --force 実走OK(変更なし判定、last_run=2026-W43)。変更ありパス(Skill push/Dify replace・create)は初回の実変更時に初めて動く。
- launchd: tools/install_weekly_credential.sh を会社Macで本人が実行(平日8:30、週1回だけ動く)。

## 2026-10-23 夜 launchd登録
Status: done(本人がinstall_weekly_credential.shを実行。チャット終了)
Next(次回): 初回の実変更時にTeams通知とSkill/Dify反映を確認。タカラトミー回答のURL(アレココ優先になる件)を観察。Vietnam破損ファイルは事務局へ。
