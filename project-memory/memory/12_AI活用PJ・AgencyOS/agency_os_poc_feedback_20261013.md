---
name: agency-os-poc-feedback-20261013
description: Agency OS PoCアンケート第1弾(6件)の内容と、共有チャット実読から出した改良方針6点(未反映)
metadata:
  type: project
---
2026-10-13、Formsの「GBC バーチャルAI Agency OS PoCフィードバック(1-6).xlsx」を確認。回答者: 須田幸宏(3)、百々奈菜子(3)、石井美香(3,4,4/コメントなし)、中村佳奈(4)。平均3.5。
用途: Carlyle Japanブランド施策、GBCケイパ紹介、味の素ナイジェリアのブリーフ添削、AnyMind(比KOL)への戻し確認、はま寿司台湾PPT化(ユーザー持込テンプレ)、ANA競合ピッチ敗因分析。

声:
- 須田: 多角的で有用だが長い。トークン節約できる指示の仕方が要る。
- 百々: アレココ資料のリンクが「アクセス権なし」。中村さん権限では同URLが開く(10/13確認)。(10/13時点の推測「GBCグループ外」は誤り。10/14調査でPoC参加者28名は全員GBCグループ(161人)のメンバーと確認。原因は下の2026-10-14追記)
- 中村佳奈: 通常ChatGPTより指摘の納得性が高い。ただしANA敗因分析ではAIが自分で作ったBrand Role文を資料由来のように提示し、ユーザーに突っ込まれて訂正した。

改良方針(2026-10-13 改訂版 GPT作業/*_20261013.md に反映済み、ChatGPT/Difyへの本番反映は中村さん作業待ち。反映するときは[[feedback_agency_os_skillmd_multi_deployment_sync]]に従いSKILL.mdとSKILL_Dify.mdの両方へ):
1. 付録ブロック(A–I)は該当があるときだけ出し、1つの表にまとめる。該当なしは1行。本文は結論を先に書く。
2. 添削・振り返り系のタスクでは「資料に書いてある」と「AIの再構成」を区別して書く。
3. アレココのリンクには「GBCメンバー限定」と添え、要点は本文に書く。PoC参加者の閲覧権付与は事務局判断(要明示OK、[[feedback_sharepoint_permission_change_needs_explicit_ok]])。
4. ケイパ紹介にはdentsuグループ全体の数字ではなくGBCクレデン([[gbc_credentials_slide_bank_project]])を返す。Google Driveの接続を勧めない。
5. 最後の提案は日本語で書き、頼まれていない画像生成は持ちかけない。
6. PoC運用: /s/t_形式の共有リンクでは最終回答しか見えないので、会話全体の共有リンクを頼む。石井さん・百々さんにヒアリングする。
Related: [[gbc_intelligence_engine_project]]

参加者名簿は28名(Agency_OS_PoC_参加者名簿_20260911.xlsx)なので回答率は4/28。報告PPTXは Agency_OS_PoCフィードバック報告_20261013.pptx。
Difyの公開中プロンプトは、共有ブラウザ9226からconsole APIの /console/api/apps/<id>/workflows/publish を fetch(X-CSRF-Token=csrf_tokenクッキー)すればJSONで取れる。GUI操作はいらない。

2026-10-13 反映後テスト: ChatGPT版は改訂ルールどおりに動いた。Dify版はファイル名の表示と長さ(12,000字)が残ったため、*_20261013_01.md で修正(Dify反映待ち)。ルール本文でファイル名を例示すると、Difyのモデルはそれを回答にそのまま出す。ルールは「データの中身」で書き、ファイル名を書かない。
ChatGPTの自動テスト: 9224のbotで送り、完了したら新しいタブで /c/<id> を開き直し、[data-message-author-role] の innerText を読む。送信直後のタブは中身が空になることがある。Difyの自動テスト: console APIの /advanced-chat/workflows/draft/run にPOST(SSE、X-CSRF-Token)。
局内展開について中村さんの考え: 課題は「どう使ってもらうか」。手順は Skill有効化 → ハンズオン → 使用事例の紹介。RFP対応ツールと思われがちなので、案件の前から振り返りまでの用途を示したい。Nidec案件は成功事例候補だが機密なので、まだ名前を出さない(資料では「進行中の競合プレゼン案件」と表記)。

2026-10-14 ローンチ準備案: 20260909PoC説明/Agency_OS_ローンチ準備_20261014.md。Teams経由のFB: 満生さん(10/5、ABM事例をDify→ChatGPTでPPT化、構成が良い)、勝又さん(口頭で「いいね」)、項琳さん(Salesforce由来の事例ばかりで資料ケースが少ないと指摘)。未回答のヒアリング対象22名。名前候補はChatGBC/Ask GBC推奨(未決)。ChatGPT Skillの利用回数は開発者から見えないため、KPIは管理者確認→回答末尾Formsリンク→月次アンケート→SF項目追加の順で検討(未決)。

2026-10-14 Skill名変更の調査: Skillエディタに「名前」欄(現在 gbc-ai-agency、編集可)と「説明」欄がある。画面上の表示名「Agency OS」は agents/openai.yaml の display_name。名前変更はこの2か所の書き換えで済み、作り直し不要(dentsu_gtm_template_clean.pptxはSkill内に残る)。ChatGPT Skillは現在テキスト以外を新規アップロードできないため、作り直しは避ける。変更前に「スキルをダウンロード」でバックアップを取る。

2026-10-14 リンク不通の原因調査(確定分):
- アレココの添付ファイル(DocApp/Knowledge/<id>/<file>)は、ライブラリ「添付ファイル」がサイトと別権限。中村さんは「GBCメンバー」(8人)/「GBCマネージャー」(16人)のSPグループ経由で直接開けるが、一般局員は開けない。アレココ本体のアプリ(arekoko-search-web-part)は直URLを使わず、PDFは _layouts/15/embed.aspx?UniqueId={..}、Officeは Doc.aspx?sourcedoc={..}&action=interactivepreview で表示する(閲覧のみ・DL不可運用)。
- 局員が開けるリンク: https://esq365.sharepoint.com/sites/GBCarekoko/SitePages/Knowledge.aspx#/Detail/<id>(ToolはTool.aspx#/Detail/<id>)。<id>はDocAppのフォルダ番号=Knowledges/Toolsリストの項目ID。10/14に#/Detail/111で表示を確認。
- Packの直URLは241件(Knowledge 222 / Tool 19)。Pack全296件のうちリンク切れは3件(全角「）」がURLにくっついたもの、旧サイトgbcknowledgesharearekoko、途中で切れたURL)。
- ChatGPTの回答でも、URLの直後に全角括弧や日本語が続くとリンクに取り込まれて壊れる(石井さんの会話のdeepl/campaignasia)。
- Salesforceのリンク(dgx.lightning.force.com/lightning/r/GBC__c/<id>/view)は正常に開いた。
- 対策(未実施): Pack生成時にDocApp直URLを#/Detail/<id>へ置換、壊れた3件を修正、SKILL.mdに「URLは前後に半角スペースを入れるかMarkdownリンクにする」を追記。
2026-10-14 対策を実施(差し替えは中村さん作業): GBC-Knowledge/fix_pack_links.py(元packは変えず別フォルダへ出力、CRLF保持)→ output/agency_os_pack_20261014/(直URL1,507件置換、変更15ファイル)、差し替え用の15ファイルは output/差し替え用_20261014/。指示文は GPT作業/SKILL_20261014.md・SKILL_Dify_20261014.md・SKILL_Dify_for_paste_20261014.md(#6書き換え・#8リンク書式新設)。Knowledges 117(ベトナム広告事情2025)は10/8に非公開化されており詳細ページが見えない可能性あり。packを作り直したら毎回fix_pack_links.pyを通すこと。

2026-10-15 第2弾の声: フォーム7件目 解明明(タカラトミー北米、評価5、ツール・契約・担当者まで分かる)→平均3.7。Teams返信(10/14): 庄司(誰に相談/どこに情報が分かる、SF連携)、杉山(過去案件・ケイパ検索、リンクから開けない)、譚(拠点依頼の事例収集とケイパPPT化、SF中心でアレココを拾ってほしい)、中村壮詔(競合ブリーフ初動の事例抽出、ドンピシャは少ない)、孫(未使用・録画を見てから)、西海(今週中に回答予定)。項琳は名称ChatGBC推し、最終は石坂さんに選んでもらう方針。報告資料は Agency_OS_PoCフィードバック報告_20261015_01.pptx。
フォーム回答の取得: Forms連携のExcel(OneDrive、UniqueId e2236f4f-f462-4fd1-bfab-797d2fb32786)はブラウザで開くまで新しい回答が反映されない。9226でDoc.aspxを開いて40秒待ち、_api/web/GetFileById(...)/$valueで取得する(先にonedrive.aspxを開かないと403)。

2026-10-15 Difyログ(9/11〜10/14): 中村以外7名・17問(庄司7、満生5、勝又・岩井・榎本・徳田・西海各1)。社内ツール該当なし13/17、MODEL MEMORY依存9/17、👍👎ゼロ。用途は議事録・人探し・事例・社内ルール質問・RFP。
KPI方針(中村さん判断10/15): ChatGPTは宮川さん権限で個人別スキル利用が見えない→不可。回答毎のリンクURL表示もUI上NG、定期アンケートも迷惑でNG、Salesforce項目追加もNG。採用案=Difyの利用ログ(自動)+アレココ資料の閲覧数(SharePoint検索APIのViewsRecent/ViewsLifeTime、DocApp/Knowledge 641件で累計2,582・直近14日24回@10/15)+事例共有数。
名称: 10/14 Teamsで中村さん提案・項さん賛成の3案 ChatGBC / askGBC / GBCNavi(項さんはChatGBC推し、最終は石坂さん)。
改修(10/15): 指示文に Retrieval and scope rules 7項目+ツール索引埋め込み、Pack事例に参照行。Difyは検索が先に走るため、言い換え検索はワークフロー側に「質問の言い換え」ノードを足すのが本筋(未実施・要相談)。

2026-10-15 Dify本番反映(console API、GUIなし): 指示文=SKILL_Dify_for_paste_20261015(公開前の本番は10/14版と空行差のみだった)。ノード1789201851613「ブリーフ要約」→「検索語の言い換え」(質問+添付から日英・略語・上位カテゴリの検索語を600字以内、temp0.2)。テンプレート1789193097091は「{{query}}+検索語(言い換えを含む)」。Lovethework+Credentials検索(1790663085627)もテンプレート出力を使うよう変更。公開名「20261015言い換え追加」(marked_nameは20字以内)。テスト: ABM→1回目で直接一致3件(ENEOS/Cohere/森永)、法定外労働時間→データ外と明言し短く回答。Difyナレッジのファイル差し替え(差し替え用_20261015)とChatGPT Skillは未反映。
Difyワークフロー編集API: GET/POST /console/api/apps/<id>/workflows/draft(bodyにgraph,features,environment_variables,conversation_variables,hash)、POST .../advanced-chat/workflows/draft/run(SSE)、POST .../workflows/publish。
2026-10-15 午後: ChatGPT Skill(version 139)とDifyナレッジ(21件)に10/15版を反映し、両方とも照合一致。中村さんがChatGPT版でテストOKを確認。報告書の最新版は Agency_OS_PoCフィードバック報告_20261015_04.pptx(_03に文字数制限撤廃を反映)(本編=要点→全体像16/28名→使われ方→評価→課題6→対応6(全反映済)→テスト→局内展開→名称→相談、Appendix=改修内容・アンケート一覧・Teamsの声・Difyログ・使い方例・使い分け)。
2026-10-15 夕: 文字数制限を撤廃した *_20261015_01.md を ChatGPT Skill(指示文一致を確認)と Dify(公開「20261015文字数制限撤廃」)に反映。Difyテスト: ベトナム即席麺→7,878字・事例7件・現駐在4名・過去6名・エキスパート/部署/ツールあり、タイ飲料→事例3件・アレココ資料2件・駐在員あり。指示文の差し替え・テスト・公開は tools/dify_prompt.js で行える。
