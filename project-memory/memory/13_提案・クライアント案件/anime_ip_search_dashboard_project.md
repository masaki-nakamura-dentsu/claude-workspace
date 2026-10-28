---
name: anime-ip-search-dashboard-project
description: 日本アニメIPの海外人気度をGoogle検索データ中心に可視化するダッシュボードプロジェクト。Artifactでプロトタイプ公開済み(5タイトル×5ヶ国)、次はYouTube API接続や拡張が課題
metadata: 
  node_type: memory
  type: project
  originSessionId: cd33b668-7789-4d46-a92b-e8ec2676d0c1
  modified: 2026-09-30T02:01:48.891Z
---

## 目的
日本アニメIPが「どこの国でどれぐらい人気があるか」をいつでも見られるダッシュボードを作る2本立て構想:
1. **最新タイトルランキング分析**: 指定地域・期間での「検索意図」「市場浸透度」をTOP10+注視作品のランキング形式で定量・定性分析
2. **特定タイトルのトレンド**: 特定の「国」×「アニメタイトル」に絞り、現地語検索キーワード・過去のコラボ・YouTube/SNSの熱量・Googleマップ/ニュースのリアルタイム状況を分析

## 2026-08-27: 初回ヒアリング→プロトタイプ構築・公開まで完了

### ユーザーが選択した方針(AskUserQuestionで確認済み)
- 実装基盤: **Webダッシュボード(Artifact)**(PowerBI/Excelは不採用)
- SNS(X/Instagram/TikTok等): **今回は対象外**(Google系サービスではなく別途API/契約が要るため)
- 初期スコープ: **少数タイトル×少数国のプロトタイプ**からスタート

### 技術的な現実(着手前にユーザーへ共有済み)
- Google Trends: **公式APIなし**。非公式ライブラリ`pytrends`(unauthenticated公開エンドポイントを叩く)経由。レート制限が厳しく、実行するとすぐ429が返る(3〜4コール目で発生実測)。`collect.py`にリトライ+バックオフ(3回、5s×試行回数)を実装済みで、5ヶ国×5タイトルのランキング取得+25件のrelated_queries取得(合計約30コール)が約3分で完走した実績あり
- YouTube: 公式Data APIはあるが**APIキー未発行**(ユーザーのGoogleアカウント側の作業が必要、無料枠1万unit/日)。今回は未接続、プロトタイプには含めていない
- Googleマップ: Places API等で店舗情報は部分的に取れるが「リアルタイムの熱量」は限定的。今回は未着手
- ニュース: 公式News APIなし。今回は**WebSearchツールでタイトル単位(国別フィルタなし)**の要約を手動収集して代替
- **Artifactの構造的制約**: 厳格なCSPによりブラウザ側から外部API(Google Trends等)へライブ接続できない。そのため今回のダッシュボードは**静的スナップショット**。最新化するには`collect.py`再実行→同じ`file_path`でArtifact再公開、という手動サイクルが必要(自動更新は未実装、次フェーズ候補)

### 実装内容
- venv: `~/anime_dashboard_venv`(Dropbox外、[[feedback_venv_outside_dropbox_sync]]に準拠)
- `pip install pytrends`は会社Mac(d14461)のためプロキシ経由(`http_proxy`/`https_proxy=http://proxy1.dentsu.co.jp:8080`、[[feedback_d14461_pip_needs_corporate_proxy]]と同一パターン)
- `~/anime_dashboard_venv/collect.py`: 対象5タイトル(Spy x Family / Jujutsu Kaisen / One Piece / Demon Slayer / Attack on Titan、Google検索でヒットする英語表記を採用)× 5ヶ国(US/FR/BR/ID/PH、地域的に分散させた選定)。
  - ランキング用: 国ごとに5タイトルを1回のcompareコールで同時取得(pytrendsの「1回のcompareは最大5語まで」という制約をちょうど使い切る設計、`timeframe='today 12-m'`で12ヶ月週次系列を同時に取得しランキングとトレンドチャート両方に流用)
  - 詳細用: タイトル×国ごとに`related_queries`(現地語の実際の検索語、top/rising)を個別取得
  - 出力: `~/anime_dashboard_venv/dashboard_data.json`(約57KB)
- `~/anime_dashboard_venv/news_data.json`: WebSearchで取得したタイトル単位のニュース要約(手動収集、自動化はまだ無し)
- Artifact本体: `/private/tmp/.../scratchpad/anime_dashboard.html`が元ファイル(セッション終了でscratchpadは消える可能性があるため、**再編集が必要な場合はArtifact側をaction:"read"で取得してから作業すること**)。タブ構成「タイトルランキング」「タイトル×国 詳細トレンド」の2画面、[[dataviz]]skillのデフォルトパレット(5系列: blue/orange/aqua/yellow/magenta)を使用、`validate_palette.js`で検証済み(lightモードで3色がcontrast WARN→凡例・ラベルをテキストトークンで表示することで relief 済み)
- 公開URL: **https://claude.ai/code/artifact/99375019-caf8-4805-a43a-9f23a947cf75**(タイトル "Anime IP Global Pulse")。同じセッションから同じfile_pathで再publishすれば同一URLのまま更新できる

### 未着手・次の判断ポイント
1. YouTube Data API v3のキー発行要否をユーザーに確認(ユーザーのGoogleアカウント作業)
2. タイトル/国の拡張(今は5×5のプロトタイプ)
3. 定期更新の自動化(`/loop`やcronで`collect.py`を定期実行→Artifact再publishする仕組み化)
4. ニュース収集の自動化・国別フィルタ対応
5. Googleマップでのコラボ店舗/イベント可視化

次回このプロジェクトに触るときは、上記5点のどれから進めるかユーザーに確認してから着手すること。

## 2026-09-17: Geminiプロンプト(3機能)を統合、3タブ構成へ本格拡張

### きっかけ: Agency OSへの統合相談→このダッシュボード拡張へ方針転換
ユーザーから「Geminiに聞いて使っている日本アニメIP分析プロンプト(①市場レポート作成②タイトルランキング分析③特定タイトルのトレンド分析の3機能、SMS=Search Momentum Scoreという指標を使用)を[[gbc_intelligence_engine_project]]のAgency OS(ChatGPT Skill)に入れられないか」と相談があった。Agency OSはGeminiのようなGoogle Trends/YouTube/Googleマップへのネイティブ連携を持たないため精度が落ちる制約を説明した上でAskUserQuestionで方針確認し、「既存のこのダッシュボードを本格拡張する、Agency OS連携は次回」という結論になった(スコープはGeminiプロンプトの①②③全てカバー)。

### 実装: 4体の並列general-purposeエージェントで実データ収集
5カ国(US/FR/BR/ID/PH)を2エージェント(US/FR、BR/ID/PH)、5タイトルを2エージェント(Spy x Family/Jujutsu Kaisen、One Piece/Demon Slayer/Attack on Titan)に分担させ、WebSearchで実在の参照URL付きデータを収集(推測・捏造は禁止と明示)。
- 国別7項目: geo_social(地政学的・社会的背景)/digital_behavior(SNS行動)/platform_share(配信プラットフォームシェア)/local_events/business_collabs/ip_health(海賊版対策状況)/outlook
- タイトル別4項目: collab_events(過去コラボ事例、参照URL必須)/search_intent_by_country(5カ国×3カテゴリの現地語検索キーワード)/audience_reception(作画/ストーリー/キャラクター/楽曲の4軸評価)/engagement_density_notes

### SMSスコアの実装方針(重要な設計判断)
Geminiプロンプト原本のSMS定義(Search Volume 40%+Momentum 30%+Engagement Density 30%)をそのまま踏襲したが、Engagement Density(YouTube再生数・SNS拡散量等)はYouTube Data API等の実測手段が無いため、**収集した定性データ(コラボ件数・バイラル事例の再生数/いいね数等)を根拠に5段階(55/70/90/95/100)の参考スコアを人間has判断で付与**した(`engagement_density.json`、算出根拠を`basis`フィールドに明記)。UIのnote-cardとfooter両方に「実測値ではない」旨を明記し、[[gbc_intelligence_engine_project]]の品質監査事件(根拠のない数値の捏造)と同じ轍を踏まないよう透明性を優先した。Search Volume/MomentumはGoogle Trends実データ(既存collect.pyの成果物)からそのまま計算。

### UI構成変更: 2タブ→3タブ
Geminiプロンプトの①②③に対応させ、タブ順を「市場レポート」→「タイトルランキング(SMS)」→「タイトル×国 詳細トレンド」に変更。
- **市場レポート(新規)**: 国選択→地政学的背景/SNS行動/プラットフォームシェア/イベント動向/コラボ事例/IP健全性/展望をカード表示、各セクション末尾に参照URLリンク。「人気IPランキング」セクションはSMSランキング(②)をそのまま反映(Geminiプロンプン原本の「Slide4は②の結果をそのまま使い独自順位を作らない」という制約に対応)
- **タイトルランキング(既存拡張)**: SMS内訳を3色積み上げバー(Search Volume/Momentum/Engagement Density)で可視化、SMS定義の注記カードを追加
- **詳細トレンド(既存拡張)**: 既存のGoogle Trends関連キーワード+ニュース要約に加え、現地語検索インテント(3カテゴリ×5カ国)・過去コラボ事例カード(参照URL付き)・視聴者熱量4軸評価・エンゲージメント密度メモを追加

### 実装ファイル・公開先
- データ: `scratchpad/market_data.json`(国別)、`scratchpad/title_deepdive.json`(タイトル別)、`scratchpad/engagement_density.json`(SMS第3軸)。いずれもscratchpad配下のため**セッション終了で消える可能性があり、再編集時はArtifact側をaction:"read"で取得してから作業すること**(前回と同じ注意点)
- ビルドスクリプト: `scratchpad/build.py`(既存DATA/NEWSと新規3データセットを1つのJS `BUNDLE`変数にまとめてHTMLへ埋め込む方式、CSSトークン・既存2タブの構造はそのまま維持し3タブ目を追加)
- 公開URL: 変わらず **https://claude.ai/code/artifact/99375019-caf8-4805-a43a-9f23a947cf75**(同一file_pathで再publish、Version更新)

### 未着手・次の判断ポイント(更新版)
1. **Agency OSとの連携方法**(今回ユーザーが明示的に次回送りにした最優先項目) — SKILL.md/SKILL_Dify.mdに参照導線を追加するか等、[[feedback_agency_os_skillmd_multi_deployment_sync]]の3系統同期に注意しながら検討
2. YouTube Data API v3のキー発行要否(未確認のまま継続)
3. タイトル/国の拡張(今回も5×5のまま)
4. 定期更新の自動化
5. Googleマップでのコラボ店舗/イベント可視化(今回も未着手)

次回はまず1(Agency OS連携)から確認して着手すること。

## 2026-09-30: 「Geminiのネイティブ連携」という前提を訂正(要再検討)
上記53行目の「GeminiはGoogle Trends/YouTube/Googleマップにネイティブ連携を持つ」という
説明について、ユーザーから「本当か」と問われWebSearchで検証した。結果は**部分的に誤り**:
- 実在するのはGemini Apps(消費者向けgemini.google.com)の「YouTube拡張機能」のみ。
  ON にすると特定の動画URL/チャンネルを指定して要約・字幕取得・メタデータ参照ができる
  ([Google公式ヘルプ](https://support.google.com/gemini/answer/16622858))。
- Google Cloud公式のGrounding一覧には「YouTube」への公式グラウンディング経路は無く
  (Google検索/Google Maps/自社データのみ)、YouTube Data APIとの連携は外部連携ツール
  (Pipedream等)経由の自作が必要([Google Cloud Grounding overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/overview))。
- Gemini Apps自体にも「視聴履歴等の包括的な一覧化はできない」という制限が明記されている。
- **結論**: SMSのEngagement Density軸に必要な「複数タイトル×複数国を横断した再生数・
  エンゲージメントの集計」について、Geminiが公式API水準の正確な数値を持っている保証は無く、
  実態は通常のWeb検索・ブラウジングで拾える範囲に近い可能性が高い。
- **示唆**: Agency OS(ネイティブ連携なし)とGeminiの差は、53行目で説明したほど大きくない
  かもしれない。次回Agency OS連携([[gbc_intelligence_engine_project]])を検討する際、
  「Geminiだからできる」という前提を鵜呑みにせず、Gemini側も実際どう数値を出しているか
  (webブラウジングでの推定か、ユーザーが個別に動画URLを渡しているのか)を確認してから
  優劣を判断すること。

## 2026-09-30(続き): 実際に使われていたGeminiプロンプト全文を精査(gemini-3.1-pro-preview)
ユーザーが実際にGeminiで使っていたプロンプト全文の提供を受け、WebSearchで各データソースclaim
を個別検証した。`gemini-3.1-pro-preview`自体は実在(2026-02-19リリース、Google最新フロンティア
モデル、Preview状態継続中)。検証結果:
- **Google Maps**: 本物。Gemini APIに公式Grounding toolがあり2.5億件超の場所/レビュー/写真/
  営業時間に実アクセス可能。2025-10-13よりGemini Appsでデフォルト有効化済み。③の現地イベント/
  クチコミ調査には正当な優位性あり。
- **YouTube**: 部分的に本物、ただし限定的。同じ2025-10-13の変更でYouTube「公開データ」が
  デフォルトで回答に混入するようになったが、これは検索インデックス上の一般公開情報であり、
  YouTube Data API水準の正確な再生数/いいね数を認証済みで取得しているわけではない。特定動画
  URLを渡した場合の音声・映像解析は本物だが1本ごとの機能でSMSの集計ランキングには使えない。
  → SMSのEngagement Density軸は、Gemini版も結局「検索で拾える範囲からの推計」であり、
  このダッシュボードが採用した「人間判断による参考スコア」方式と実質同じ限界を抱えている
  ことが判明(想定していたより両者の差は小さい)。
- **SNS拡散(X/Instagram/TikTok)**: 公式連携なし。Google公式Groundingソース一覧は
  Google検索/Maps/自社データのみで、これらSNSへの直接API連携は存在しない。
- **【重要】「Geminiインサイト: ユーザーがGeminiに対して行っている具体的な質問内容の傾向」
  という項目はほぼ根拠なし**: 全ユーザー横断の質問傾向を集計して返す消費者向け製品は
  確認できず、見つかった近い仕組み(Gemini Enterprise管理者が自社デプロイ内ログをBigQuery
  分析)とは対象が全く異なる。この項目についてGeminiに聞いた場合、実在しないデータを
  もっともらしく生成(捏造)している可能性が高い。[[gbc_intelligence_engine_project]]の
  知見カード品質監査事件(根拠なき一般化・捏造)と同種のリスクとしてユーザーに明示済み。
- **結論としてユーザーに伝達**: 前回説明した「Geminiはネイティブ連携がある」は、Maps=正しい/
  YouTube=半分正しい(精度限定的)/SNS・Geminiインサイト=誤り、と訂正。Agency OS連携の
  優劣判断は、この訂正後の実態を前提に行うこと。

## 2026-09-30(続き): Agency OS移植の設計書を作成(実装はまだ、設計のみ)
ユーザーから「Gemini担当者のアウトプットをAgency OSで実現できるか」と問われ、実現可能と判断
(Google Maps以外は同等以上の情報源で再現可能、SMSの数値面はAgency OS側の方がGoogle Trends
実測値を正直に使える分誠実)。ユーザーは「設計だけ先に固める」を選択したため、設計書を
`GBC-Knowledge/agency_os_anime_ip_design.md`に作成(実装は未着手)。

要点: Agency OS本体(`GPT作業/SKILL.md`)は静的Markdownバケット方式(ライブ計算なし)で、
Geminiプロンプトの動的ヒアリング(地域/期間/属性をその場で変えて再計算)とは相性が悪いと判明。
そのため2案を提示——**案A(推奨・まず着手)**: 事前計算済みSMSランキング等を`anime_ip_*.md`
として既存Knowledge Packバケットに追加するだけの軽量版。**案B**: [[gbc_intelligence_engine_project]]
の「知見活用GPT」(`gpt_integration/`)と同じCode Interpreter+事前収集データ方式で専用サブGPTを
新設し、Geminiと同じ動的UXを再現する重量版。段階的に案A→必要なら案B、という進め方を提案済み。
既存資産(`collect.py`のpytrends実測値、2026-09-17収集のmarket_data.json等)はそのまま流用可能、
「Geminiインサイト」の代替は`related_queries`(実在データ)を使う設計とした。

未決事項5点(設計書末尾に記載): 案A/B選択、対象国/タイトル範囲拡張の要否、属性別SMSをスコープに
含めるか、Google Maps代替の妥協ライン、Gemini担当者への実際の使い方ヒアリング。

## 2026-09-30(続き2): 「5タイトルでは網羅できない」問題→AniList/Jikan APIの発見
ユーザーから「5タイトルでは網羅できないので別のサブSkill(GPTまたはGemini)に切り出し、Agency OS
からシームレスに呼び出せないか」と問われ、ChatGPTプラットフォームの実際の連携可否をWebSearchで
検証した。結果: ①ChatGPT「Skills」同士は公式に同一会話内で自動スタックする仕組みがあるが軽量な
指示合成に過ぎない、②Custom GPT同士は`@`メンションで呼び込めるがユーザーの明示操作が必要で
Agency OS側からの自動呼び出しではない、③ChatGPT→Geminiは公式連携経路が無く、自前でGemini API
プロキシをホスティングする必要がある([[gbc_intelligence_engine_project]]の知見活用GPTがActions
方式を断念した理由と同じ壁)。**いずれもユーザーが期待する意味での「シームレスな呼び出し」には
ならない**とユーザーに伝達済み。

より本質的な指摘として、Gemini自身も全タイトル網羅DBを持たず検索推測に頼っているため、網羅性は
オーケストレーション(どのLLM/Skillを使うか)では解決しないと判明。代わりに**AniList API**
(GraphQL、APIキー不要、trending/popularity/top-rated/seasonalランキング完備)と**Jikan API**
(MyAnimeList非公式、無料、top/most-popularランキング完備)という、何千タイトル規模の実在する
網羅的アニメ人気度データベースを発見し、これを`collect.py`の収集範囲に追加する方針へ設計変更した。
これにより案Bを選んでも既存のCode Interpreter+事前収集データのパターン内で完結し、クロス
プラットフォーム呼び出しの問題自体を回避できる。

設計書(`GBC-Knowledge/agency_os_anime_ip_design.md`)に追記済み。

## 2026-09-30(続き3): AniList/Jikan API実データ検証(curl直接テスト)完了
- **AniList**: 正常動作・採用推奨。APIキー不要、company Mac経由プロキシ不要で到達可能。既存5タイトル
  全て実在確認(popularityが既存ダッシュボードの選定と整合)。`popularity`/`trending`/`favourites`/
  `averageScore`等が取得可能。
- **Jikan(MAL非公式)**: 個別ID照会は正常だが、`/top/anime`等スクレイピング系エンドポイントは検証
  時点で複数回504エラー(非公式スクレイパーゆえの構造的不安定リスク)。補助的利用に留める。
- **重要な制約**: 両APIとも「アニメファンコミュニティ登録ユーザー」の集計値であり、国別の人気度は
  取得できない。既存`collect.py`(Google Trends、一般人口の国別検索行動)とは母集団が異なり、
  **置き換えではなく補完関係**と判明。
- **更新した設計方針**: AniListのpopularity/trendingを「全タイトル網羅の一次スクリーニング層」とし、
  そこから絞り込んだ候補について国別にpytrends実測する**2段階パイプライン**を採用。Jikanは個別
  タイトルの補助データ取得用に温存。詳細は設計書の「2026-09-30追記2」セクション参照。
- **次回**: AniListの`pageInfo.total`(5000と返ったが表示上限の可能性、実DB規模は未確認)を別クエリ
  形状で再確認した上で、2段階パイプラインの実装に着手するか、案A/Bの選択を先に固めるかユーザーに
  確認すること。

## 2026-09-30(続き4): 2段階パイプライン実装・実行完了(検証成功)
ユーザー指示で実装に着手。`~/anime_dashboard_venv/anilist_screen.py`(Stage1)と`collect_v2.py`
(Stage2)を新規実装し、実際に実行して動作確認した。
- Stage1: AniList GraphQL APIから94件の候補プール(popularity上位60+trending上位40マージ)を
  `anilist_screening.json`に出力。成功。
- Stage2: フランチャイズ重複除去した上位15タイトル×5カ国でpytrends実測(ranking+related_queries)を
  実行、`dashboard_data_v2.json`に出力。バックグラウンド実行で完走(429エラー2回、既存リトライで
  回復)。
- **会社Mac固有の罠**: AniList取得を`urllib.request`で書いたら`SSL: CERTIFICATE_VERIFY_FAILED`で
  失敗([[feedback_d14461_python_https_cert_verify_use_curl]]と同一パターン)。`subprocess`経由の
  `curl`に変更して解決。同種のPython外部HTTPS通信を会社Macで書く際は最初からcurl経由で実装すること。
- **発見した軽微な問題2件**: ①フランチャイズ重複除去の正規表現が"Final Season"等の数字なし
  パターンを見落とし、"Attack on Titan"と"Attack on Titan Final Season"が別枠のまま残った(次回
  修正要)。②米国"ONE PIECE"のrelated_queriesに一般名詞"one piece swimsuit"が混入——タイトル名が
  日常語と衝突する新パターンとして記録(既知の「タイ→タイアップ」と同種)。
- **結論**: 2段階パイプライン設計は実証済み。次は①②の修正、既存3タブダッシュボードへの統合方法、
  Agency OS案A/B選択、のいずれかをユーザーに確認してから進める。
- 実装ファイル: `~/anime_dashboard_venv/anilist_screen.py`、`~/anime_dashboard_venv/collect_v2.py`、
  出力`anilist_screening.json`/`dashboard_data_v2.json`。設計書
  `GBC-Knowledge/agency_os_anime_ip_design.md`の「2026-09-30追記3」に詳細記録済み。

## 2026-09-30(続き5): 発見した2件の軽微な問題を修正・再検証完了
`collect_v2.py`を修正し再実行、両方の修正を確認した:
1. `franchise_key()`に"Final Season"(数字なし)除去を追加 → 再実行で"Attack on Titan Final
   Season"が正しく重複認定され外れ、"Chainsaw Man"が15枠目に入った。
2. `NOISE_KEYWORDS`辞書によるタイトル名/一般語衝突フィルタを新設、"ONE PIECE"→
   swimsuit系キーワードを登録 → 再実行で"one piece swimsuit"が1件フィルタされ、残りは全て
   作品関連語であることを確認。"Sword Art Online"の"sword art online game(s)"は公式ゲーム展開
   への正当な言及と判断しフィルタ対象から意図的に除外(判断基準として記録)。
3. 追加で`TITLE_AMBIGUITY_RISK`辞書を新設、"Your Name."のようにタイトル自体が日常語で
   related_queriesが空になりやすいケースを`ambiguity_caveat`として出力に明示する仕組みを実装
   (「データ無し=関心無し」の誤読防止)。

いずれも辞書形式で拡張可能な設計。**結論: 2段階パイプラインは実用レベルに到達**。

## 2026-09-30(続き6): 既存Artifactへの統合完了(Version 3として公開)
Artifact(https://claude.ai/code/artifact/99375019-caf8-4805-a43a-9f23a947cf75、"Anime IP Global
Pulse")をaction:"read"で取得→ローカルでBUNDLE JSON+JSロジックを編集→再publish(Version 3)。
ランキングタブが5タイトル→16タイトル(AniList上位15+"Spy x Family"をウォッチリストとして保持)に
拡張された。

**対処した課題**: ①AniList/既存データ間のタイトル表記揺れ(大文字/表記違い)を正規化辞書で解決。
②"Spy x Family"が純粋なpopularity順だと脱落するため、Geminiプロンプト原本の「Custom Watchlist」
思想を踏襲し追加取得・保持。③Engagement Density実データが無い新規11タイトルは「SMS」ではなく
「参考値(2軸)」と明確にラベル分け(3軸目を仮の値で埋めない)。④トレンド時系列チャートは
[[dataviz]]の「カテゴリ色は循環させない」原則に従い、初期5タイトルの安定コホートに限定表示、
全16件の順位は色分け無しのランキング一覧で確認する設計。

**新たに発見した未解決の課題(次回対応)**: `collect_v2.py`はpytrendsの制約で5タイトルずつ
チャンク化してcompare取得しているため、**チャンクを跨いだSearch Volume絶対値の比較は本来正確
ではない**(チャンク内の相対順位のみ正確)。今回はUIの注記カードにこの限界を明記する対応に留めた。
改善案: 全チャンクに共通の基準タイトルを含めて相互再正規化する手法を次回検討。

詳細は設計書`GBC-Knowledge/agency_os_anime_ip_design.md`の「2026-09-30追記5」参照。次回は
①上記のチャンク跨ぎ正規化改善、②市場レポート・詳細トレンドタブの新規11タイトルへの拡張要否、
のいずれかをユーザーに確認して進める。

## 2026-09-30(続き7): 追加要望3件(対象国拡大/期間切替バグ/提案ブリーフ機能)→Version4で対応、
## デプロイ後バグ発生→Version5で修正
ユーザーから3件の追加要望: ①対象国が5カ国では少ないので主要国に拡大してほしい、②ランキングタブの
12ヶ月/3ヶ月切り替えが結果に反映されていないように見える、③クライアント提案用に「特定タイトル×国で
どの世代・ターゲットに刺さるか」を出す仕組みが欲しい(例: Blue Lockをベトナムで売り込む場合)。

**②のバグを実際に確認**: `computeSMSRows()`が`periodMonths`の値に関わらず常に「直近4週 vs
その直前4週」を比較する固定ロジックになっており、期間切り替えが計算に一切反映されていなかった
(実データで検証し確認、weeksBackを変えても recent/prior が完全に同一になることを再現)。
3ヶ月=約13週前を基準点、12ヶ月=約52週前を基準点として比較する設計に修正。

**③は「Artifact内の第4タブ」方式をAskUserQuestionで確認の上、汎用的な`PITCH_BRIEFS`辞書
(タイトル|国キー)+専用タブとして実装**。Blue Lock×ベトナムを動作確認用の1件として登録したが、
ユーザーから「Blue Lock×ベトナムはあくまで例なので、そこにこだわらないで」と明示的に指摘があり、
それ以上の作り込みはしなかった(仕組みの汎用性を優先、他の組み合わせは要望時に都度追加する運用)。

**①(対象国拡大)は`collect_v3_expand.py`をバックグラウンド実行中**(GB/DE/MX/IN/VN/KRの6カ国追加+
Blue Lockを全11カ国で取得)。pytrendsの429エラーが頻発する場面があったが自動リトライで継続。

**【重大インシデント】Version4公開直後にダッシュボード全体が空表示になるバグが発生**:
新規実装した提案ブリーフ機能のJSコードで、`const PITCH_BRIEFS = BUNDLE.PITCH_BRIEFS || {};`という
宣言をせずに、いきなり`Object.keys(PITCH_BRIEFS || {})`と未宣言のbare識別子を参照してしまい、
スクリプトのトップレベルで`ReferenceError`が発生→**スクリプト全体の実行がそこで停止し、
それより後にあった`renderRanking()`/`renderDetail()`/`renderReport()`の呼び出しも一切実行されず、
市場レポート含む全タブが空表示になった**。ユーザーからのスクリーンショット付き報告で発覚。

**教訓(重要)**: `node --check`によるJS構文チェックは**構文エラーしか検出できず、この種の
「未宣言変数の参照」という実行時エラー(ReferenceError)は検出できない**。今回`node --check`で
「SYNTAX OK」と確認した上で公開したにも関わらず実際には壊れていた。再発防止として、Node上で
最小限のDOMスタブ(document.getElementById/createElement等をモック)を用意し`new Function(script)()`
で実際に実行してReferenceErrorが出ないかを検証する`dom_stub_check.js`
(`scratchpad/dom_stub_check.js`、`Claude作業フォルダ/アニメIP海外人気度ダッシュボード/`にも
コピー保存済み)を作成、以後Artifactの新規JS機能追加時はこの実行時チェックを構文チェックに加えて
必ず行うこと。TypeError(DOMスタブの不備由来)は許容し、ReferenceErrorのみを実バグとして扱う設計。
修正後はVersion5として再公開し、同じチェックで正常実行を確認済み。

## 2026-09-30(続き8): 国拡張データ統合完了(Version6) + 429継続によるGB部分欠落 + 追加要望5件
`expansion_data.json`(6カ国+Blue Lock)をVersion5に統合しVersion6として公開。11カ国(US/FR/BR/ID/
PH/GB/DE/MX/IN/VN/KR)・17タイトル(AniList上位15+Spy x Family+Blue Lockのウォッチリスト2件)。

**GBのみ5タイトル分欠落**: `collect_v3_expand.py`実行中、イギリスの最初のチャンク(Attack on Titan/
Demon Slayer/Jujutsu Kaisen/Death Note/My Hero Academia)が429エラーで失敗。ピンポイント再取得も
試みたが、この時点でセッション内の累積pytrendsリクエスト数が多すぎたためか4回リトライしても
回復せず断念。**フッターに欠落を明記し、`computeSMSRows()`を「その国のentry.seriesに存在しない
タイトルは行ごとskipする」設計に修正**(`entry.series[t] || []`だと欠落データが0点として誤って
ランキングされてしまう危険があったため、`hasOwnProperty`チェックで確実に除外する設計に変更)。

**公開後、ユーザーから5件の追加要望**(「Agency OSの話からズレてきたので別チャットを開く」との
ことで今回は未着手、次回持ち越し):
1. タイトル数をさらに増やしてほしい(現行17は少ないとの指摘)
2. 「アニメコアファンの熱量」(AniList由来のグローバルファンダム規模)と「国ごとの一般的傾向」
   (Google Trends由来の一般人口検索行動)を**両方見せてほしい** — これはまさに前回セッションで
   発見した「AniList=ファンコミュニティ/Google Trends=一般人口」という構造的な違いと一致しており、
   現状は両者を1つのSMSスコアに混ぜてしまっているため、2レンズとして分離表示するUI改修が必要
3. **性別・年齢のターゲット層を選んでその国でのランキングを見る機能**(Geminiプロンプト原本の
   「Segmented SMS」相当)。ただし前回確認済みの通りGoogle Trendsは属性別データを直接持たないため、
   実装する場合は代理シグナルからの推計であることを明示する必要がある(要ユーザー確認)
4. **タイトル名を日本語・英語併記に** — `anilist_screen.py`は既に`title.native`(日本語)を
   取得済みなので上位15タイトル分は新規収集不要、表示ロジック変更のみで対応可能。ウォッチリスト
   2件(Spy x Family/Blue Lock)のみ別途AniList APIで日本語タイトルを1回ずつ取得すれば良い
5. **個人Mac(ICPTokyo2022)でもデータ収集できるようにしたい**

**対応**: 上記5件は着手せず、以下を準備して次回(新規チャット)に引き継ぐ設計にした:
- スクリプト一式(`anilist_screen.py`/`collect_v2.py`/`collect_v3_expand.py`/
  `fetch_watchlist_addon.py`)+最新データJSON+`dom_stub_check.js`を
  `Claude作業フォルダ/アニメIP海外人気度ダッシュボード/`(Dropbox同期、個人Macからも参照可能)に
  コピー保存
- `SETUP.md`(個人Macでのvenv構築手順、会社Mac固有の罠の注意書き)を新規作成
- `TODO.md`(上記5件の詳細な背景・技術的制約・対応方針)を新規作成、次回セッションはこれを読めば
  即座に状況を把握できる設計

**現状**: ダッシュボードはVersion6が最新
(https://claude.ai/code/artifact/99375019-caf8-4805-a43a-9f23a947cf75)。次回セッション開始時は
`TODO.md`を確認してから着手すること。

## 2026-09-30(続き9): Version7公開 — TODO.md 5項目中4項目を実施(タイトル増量/2レンズ分離/属性別ランキング/日英併記/GB再取得)
前回セッション末尾でユーザーが「Agency OSの話からズレたので別チャットへ」と持ち越した5項目
(TODO.md参照)について、新規チャットでAskUserQuestionにより優先度を確認。①タイトル増量
②AniList(ファン熱量)とGoogle Trends(現地一般傾向)の2レンズ分離④日英併記⑥GB欠落再取得、
に加え③(性別・年代ターゲット層別ランキング)も「推計値であることを明示した上で実装を試みる」
という条件で承認され、実質5項目中4項目に着手・完了。⑤(個人Mac収集環境構築)はこのマシンが
会社Macのため今回も未着手のまま。

**公開URLが変わった**: `action:"read"`で旧Artifact(99375019-...)を取得→ローカルでBUNDLE/JS編集
→同じ`url`を指定して`publish`したところ、返ってきた新URLは
`https://claude.ai/artifact/KvM7kk6va5bokmQouvj6Za`(Version7)に変わった。今後この
プロジェクトのArtifactを参照する際はこちらの新URLを使うこと(旧URLは同一artifactのエイリアス
として引き続き機能する可能性はあるが未検証)。

**実装内容**:
- タイトル20→22件(AniList候補プール94件中16〜20位の5タイトル追加: The Promised Neverland/
  Assassination Classroom/Mob Psycho 100/Re:ZERO -Starting Life in Another World-/
  Your lie in April)。11ヶ国全てでpytrends実測完了。
- ランキングタブに指標レンズ切り替え(合成指標SMS/グローバルファン人気(AniList)/現地検索関心
  (Google Trends))を追加。AniListのpopularityをリスト内相対指数に変換した値と、Google Trends
  検索量そのものを独立した指標として提示し、母集団の違いを注記。
- 性別(男性/女性)×年代(ティーン/大人)によるターゲット層並び替え機能を追加。AniList公式ジャンル
  タグ(Shounen/Seinen/Shoujo/Josei、3件のみ推定で補完)×固定重み付けテーブルで「適合度」を算出、
  UIに「★推定値」の注記を常時表示。
- タイトル名の日英併記(AniList `title.native`)をランキング一覧・タイトル選択プルダウン・
  詳細トレンド見出し・市場レポートに反映。
- GB(イギリス)の欠落5タイトルを再取得(429で数回リトライ後成功)。

**発見・修正したバグ2件(今後の同種作業で再発しうるため詳細を記録)**:
1. **pytrendsは特定の記号を含むタイトル文字列でリクエスト自体を壊す**: "Re:ZERO -Starting Life
   in Another World-"(コロン+末尾ハイフン)を5タイトルcompareチャンクに含めると、そのタイトル
   単体のrelated_queriesも、5タイトル合同のranking(build_payload+interest_over_time)も、
   **国を問わず必ず**400/429/KeyErrorで失敗することを確認(11ヶ国全てで再現)。同じ作品でも
   Google Trends上で実際に使われる一般的な略称("Re:Zero")に差し替えたところ、11ヶ国すべてで
   即座に成功した。**教訓**: pytrendsに渡すクエリ語は、コロン・ハイフン等の記号を含む正式タイトル
   ではなく、実際の検索行動に近い略称を使うこと。表示名(UI上のラベル)とクエリ語は分離して
   管理する設計が必須(今回`fix_rezero.py`で「表示名は正式タイトルのまま、クエリ語だけ差し替えて
   結果を表示名キーで格納する」という設計にした)。
2. **国名/タイトル名の正規化漏れによるサイレントなマージ失敗**: GB再取得スクリプト
   (`gb_retry.py`)はAniList側の生表記("JUJUTSU KAISEN"、"Demon Slayer: Kimetsu no Yaiba")を
   そのまま使っていたが、ダッシュボード本体のDATA.titlesは正規化済みの表示名("Jujutsu Kaisen"、
   "Demon Slayer")を使っている。単純にキーをコピーしてマージしたため、この2件だけ実際には
   ダッシュボードに反映されず(エラーも出ずに静かに欠落)、検証時に気づいた。**教訓**: 複数の
   収集スクリプトを跨いでデータをマージする際は、生データのタイトル表記とUI側の正規化済み表示名
   が一致するとは限らないため、必ず`DISPLAY_TO_ANILIST_RAW`のような正規化辞書を経由してから
   マージし、マージ後に「全タイトル×対象国でキーが揃っているか」を機械的に検証すること
   (今回は`[t for t in data['titles'] if t not in data['ranking']['GB']['series']]`のような
   チェックで発覚した)。

**JS実装時の追加の安全策(既存の`feedback_artifact_js_runtime_check`を拡張)**:
- `document.querySelector`(単数形)は既存の`dom_stub_check.js`のグローバルdocumentスタブに
  実装されていない(`querySelectorAll`のみ実装、常に空配列を返す)。実装前にこれに気づき、
  該当箇所を`document.getElementById`ベースの実装に書き換えて回避した。**今後このArtifactに
  新規JS機能を書く際は`document.querySelector`ではなく`getElementById`を使うこと**
  (使うと過去のReferenceErrorインシデントと同種の「スクリプト全体停止」を引き起こしうる)。
- 今回、単純な初期状態チェックだけでは新機能(レンズ×ターゲット層の組み合わせ)の全パスを
  検証できないため、`test_lens_logic.js`という補助スクリプトを新設。11ヶ国×3レンズ(sms/fan/
  local)×3性別×3年代=297通りを`computeSMSRows()`に総当たりで通し、例外が出ないこと・
  `targetScore`が常に数値であることを確認してから公開した。**複数の選択肢を組み合わせる新機能
  (フィルタ×フィルタ等)を追加する際は、このような総当たりテストを書いてから公開すること**
  (dom_stub_check.jsだけでは初期状態1パターンしか検証できず不十分)。

**既知の残存ギャップ(今回のスコープ外、次回の判断材料)**:
- Spy x Familyが拡張6ヶ国(GB/DE/MX/IN/VN/KR)で未取得のまま(`fetch_watchlist_addon.py`が旧5
  ヶ国専用の設計だったため、今回のGB再取得作業とは無関係の既存ギャップ)。`computeSMSRows()`は
  `hasOwnProperty`チェックで欠落タイトルを自動的にランキングから除外する設計のため、表示上の
  クラッシュにはならないが、データとしては欠けたまま。
- ⑤個人Mac(ICPTokyo2022)でのデータ収集環境構築は今回も未着手。
- スクリプト・データ一式(`build_v7.py`/`fix_rezero.py`/`gb_retry.py`/`collect_v4_new_titles.py`
  等)は`Claude作業フォルダ/アニメIP海外人気度ダッシュボード/`にコピー済み、次回はTODO.md
  (2026-09-30更新版)を確認してから着手すること。

## 2026-09-30(続き10): Agency OS移行を一旦保留 — Geminiのランキングのブレの原因を特定し、榎本さんへ共有
プロンプト提供者は**榎本さん**(Geminiでこのアニメ海外人気度調査を運用している担当者)。榎本さんから
以前「結果にブレがある」との指摘があったとのこと。今回、その原因調査を行い、Gemini本人への
直接質問(gemini.google.com)と、Dify版Agency OS SKILL.mdの実際の記述(Always-on constraints 5番:
"This deployment permanently has no live web search"、Research gap handoff節)を突き合わせて
以下を特定した:

- **Geminiはgoogle Trends/YouTubeの生データにAPI連携していない**。Gemini自身が「Google Trendsの
  生データに直接API連携しているわけではないため、ウェブ上で公開・報道されている最新のトレンド
  データや集計レポートを検索・参照して回答を構成します」と明言。YouTubeも同様に、自分が管理
  していないコンテンツについては公開データ(二次データ)・Google Trends・SNSリスニング・
  サードパーティツール(Social Blade/Similarweb)・業界レポート(JETRO/AJA)を組み合わせた
  推計であり、YouTube Data APIのような認証済み解析ではない。
- **カスタムプロンプト(担当者の指示文)は、Geminiというプロダクト自体が持たないデータアクセス権を
  付与できない**。プロンプトに「不確かなデータは使わない」と書いてあっても、手段が無い以上は
  Web検索からの合成に頼らざるを得ず、指示だけでは防げない。
- **これが「ランキングのブレ」の直接的な説明になる**: 認証済みAPI(pytrends等)は同じ期間なら
  毎回同じ数値を返すが、Web検索グラウンディングは検索のたびに拾う記事・スニペットが変わるため、
  同じ質問を繰り返しても結果が変動する。
- **ChatGPT版Agency OSでも「同程度に不正確」なものは技術的に再現可能**(Web検索が実際に有効なら)
  だが、これは精度向上ではなく「Geminiと同じ弱点を持つものが増えるだけ」であり、意味のある
  移行メリットにはならないと整理した。

**ユーザーが榎本さんへ伝えた内容(2026-09-30)**: 「Agency OSへのそのまま移行は一旦保留」「Gemini
の結果のブレの理由が分かった(Google Trends/YouTubeの生データにはAPI連携しておらず、Web検索経由の
点数化のため揺らぎが出る)」「それでも現状を反映した資料として使える」「ChatGPTでも同様の仕組みは
作れるが、実績のあるGemini運用から今移す時期ではない」「検索以外でデータが安定する方法を今後
自分の方で検討する」という結論で共有済み。**Agency OS移行の話はこれで一旦クローズ**、
今後は本プロジェクト(pytrends+AniListによる実データ収集、Artifact/PowerBI化)の方向で
「検索によらない安定したデータ取得法」を継続検討する。

## 2026-09-30(続き11): 5レンズ化(Netflix Top10/Wikipedia pageviews/YouTube Data API追加)、PowerBI用CSV出力完了
ユーザーから「pytrendsはファンデータか」と問われ、**実は逆(pytrends=一般大衆の検索行動、AniList=
コアファン)**であることを整理。その上で「マスコミュニケーションの視点が必要」との要望を受け、
Google Trends(検索マス)に加えて以下3つの新データソースを追加、5レンズ体制にした:
- **Netflix Top10**: `https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv`から
  全週・全国のTV/映画Top10履歴(2021-07〜現在、510,340行)を一括ダウンロード可能と判明(無料・
  ログイン不要・機械可読)。22タイトル×11ヶ国でフィルタしたところ、Attack on Titan/Demon Slayer/
  Jujutsu Kaisen/One Piece/Naruto等で複数回・複数国のランクイン実績を確認(視聴実態に近いマス指標)。
- **Wikipedia pageviews**: Wikidata検索→QID解決→sitelinksで各言語版記事名取得→Wikimedia REST
  pageviews APIで月次PV取得、という3段パイプラインを新規構築(`collect_wikipedia_pageviews.py`)。
  完全無料・APIキー不要。**重要な制約**: 言語版単位の集計であり国単位ではない(en版は米国/英国/
  インド/フィリピン等が合算され分離不可)。対応言語: en/fr/pt/id/de/es/vi/ko の8言語。
- **YouTube Data API v3**: ユーザーが個人Gmailで新規APIキー発行(`~/.zshenv`に`YOUTUBE_API_KEY`
  として保存済み)。search.listで「<タイトル> official trailer PV」上位3件を検索→videos.listで
  再生数/高評価数/コメント数を取得(`collect_youtube_stats.py`)。**制約**: 検索結果は関連度推定で
  あり本当に公式動画か保証はない(channelTitleでの目視確認を推奨する設計にした)。

**会社アカウント(dentsu.co.jp)ではGoogle Cloud ConsoleのAPI有効化操作ができない**(組織ポリシーで
権限エラー)ことが判明、個人Gmailアカウントで発行して解決。詳細は
per-project memory `dentsu_google_workspace_gcp_restriction.md` 参照。

**踏んだ実装上の罠(いずれも今回中に発見・修正済み)**:
1. Wikidata検索API(`wbsearchentities`)は非常に厳しいレート制限(数回連続で429)があり、
   0.3秒間隔では即座に制限にかかった。1.5秒(QID検索)/1.0秒(pageviews取得)に緩和し、
   429時は15秒刻みの指数バックオフで再試行するよう修正して解決。
2. **Wikidata検索の「一番上のヒット」を無条件に採用すると同名の別エンティティに誤爆する**
   (2026-09-30収集時点で6件確認、うち2件は重大): "Attack on Titan"→2016年のビデオゲーム作品
   (Q21686710)に誤爆、**"One Piece"→まさかの衣服(ワンピース、ドレス)のWikidataエンティティ
   (Q200539)に誤爆**(タイトル名が日常語と衝突する既知パターン「タイ→タイアップ」「ONE PIECE→
   水着」と同種、Wikidata版として新たに発見)。他に"Naruto"→個体の猿の名前、"Tokyo Ghoul"→
   season1限定の記事(全言語版で統一されていないseason別ページ構造)、"Your Name"/"Spy x Family"/
   "Blue Lock"→検索ヒットなし、も発見・修正。**教訓**: Wikidata自動解決は「取得できたら正しい」
   ではなく、必ず`wbgetentities`でdescriptionを取得し「manga」「anime」「TV series」等の
   期待ワードが含まれるか監査してから確定させること(zero-sitelinksだけを異常検知の基準にすると、
   "One Piece→dress"のように少数言語のsitelinksが存在するケースを見逃す)。同じ「タイトル名が
   日常語と衝突する」問題が、pytrends(検索クエリレベル)とWikidata(エンティティ解決レベル)の
   両方で独立に発生することが分かった。
3. YouTube Data API検索クエリの日本語タイトル・記号(コロン等)はurllib.parse.quote_plus等で
   適切にURLエンコードする必要がある(単純な`.replace(' ','+')`では記号が壊れる)。

**PowerBI取り込み用のCSVデータマート出力**(`build_powerbi_export.py`)を新規作成、
`Claude作業フォルダ/アニメIP海外人気度ダッシュボード/powerbi_export/`に以下6ファイルを出力:
`dim_titles.csv`(22行、native表記/デモグラ/AniList実測値)、`dim_countries.csv`(11行)、
`fact_google_trends.csv`(12,508行、週次)、`fact_netflix_top10.csv`(706行)、
`fact_wikipedia_pageviews.csv`(2,086行、月次×8言語)、`fact_youtube.csv`(66行、候補動画上位3件×22)。
スター型(dim+fact)でPower Query取り込みしやすい設計。Google Trendsデータは既存Artifact(v7)の
BUNDLE.DATAから抽出(正規表現でJSON部分を切り出し)、他3ソースは新規収集データをそのまま使用。

**次回**: このCSVセットを実際にPowerBIへ取り込み、レポート(ビジュアル/ページ)を構築するのが
次のステップ。ダッシュボード設計(どの指標をどう見せるか、5レンズの統合表示方法等)は未着手。
`netflix_top10_raw.tsv`(31MB、全世界全期間の生データ)もフォルダに保存済みなので、対象国・
タイトルを拡張する際は再ダウンロード不要でフィルタし直すだけで良い。

## 2026-09-30(続き12): 各データソースの代表性をWebSearchで実証、信頼度マトリクスを実装
ユーザーから「Netflixは全世界シェアが高いわけではない」「Wikipediaは全世界共通か」「Googleは
全世界トップシェアか」「AniListは全世界で有力か」という鋭い指摘があり、WebSearchで実際の
シェア・利用実態を調査した。

**判明した事実**(全てWebSearchで確認、project memory内に出典URL保存):
- **Netflix**: ベトナム(加入者120万人のみ)・インドネシア(浸透率4%、現地Vidioが上回る)・
  インド(浸透率5%、JioHotstarが58%シェアで圧倒)では弱小。一方、米国/英国/独/仏/ブラジル
  (1,787万)/メキシコ(1,495万)/**韓国(31%シェアで実は1位)**は強い。韓国は事前の想定(弱いはず)
  と逆の結果だった。
- **Google Trends**: 対象11ヶ国中、**韓国だけが例外**。ブラウザ計測ではGoogle46-49%でNaver
  41-44%とほぼ拮抗だが、Naverのアプリ内検索(知識iN/ブログ/カフェ/ショッピング含む)まで含めると
  Naverが50-58%、Googleは28%という調査もあり、実際の検索行動を過小評価している可能性が高い。
  他10ヶ国はGoogleが圧倒的。
- **Wikipedia**: 米国・英国・ドイツ・インドが上位トラフィック国である一方、**ベトナムは主要
  トラフィック国に入らないほど利用度が低い**。さらに**韓国では衝撃的な発見**: ポップカルチャー・
  アニメ情報は競合wiki「namuwiki」が主流で、韓国語版Wikipediaの**7.2倍のトラフィック**を持ち、
  アニメ記事の詳細さでも上回るとされる。つまり`ko`言語版Wikipediaのpvデータは、実際の韓国内
  アニメ関心を大きく過小評価している可能性が高い(次回namuwikiのデータ取得可否を検討する価値あり、
  ただし公式API等は未確認)。
- **AniList**: 登録者数で比較すると**MyAnimeList(1.5億人超)の方がAniList(月間訪問者数約
  1,500万人)より規模が大きい**ことが判明。AniListは「英語圏中心の国際アニメファンダム」という
  限定付きの指標であり、特定の国のファン文化を直接代表するものではない(API安定性を優先して
  AniListを採用した経緯は既存メモ参照)。

**実装**: `build_reliability_matrix.py`を新規作成し、`dim_source_reliability.csv`
(source×country/言語×信頼度3段階(高/中/低)×理由×出典URL)をpowerbi_exportに追加。
YouTube Data APIについては国別ではなく動画候補ごとの信頼度(`fact_youtube.csv`に`confidence`
列を追加、チャンネル名に公式配信元を示唆するキーワード(TOHO animation/Sony Pictures/Netflix/
VIZ/Aniplex/Crunchyroll/ジャンプ等)が含まれるかのヒューリスティック判定)で別管理する設計にした。

**設計方針として確定**: 5レンズは統合スコア化せず独立表示のまま維持し、**各レンズの数値の横に
信頼度(高/中/低)を併記する**。これにより「この国のこの指標はどこまで信じて良いか」が一目で
分かるダッシュボードにする。PowerBIレポート構築時にこの信頼度列を必ず参照・表示すること。
