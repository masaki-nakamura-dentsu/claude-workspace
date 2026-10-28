---
name: gbc-intelligence-engine-project
description: GBC Intelligence Engine — ローカルLLM(Ollama)で社内知見をSharePointから知見カード化するプロジェクト。GBC LaunchPad構想と統合し、知見カード+Salesforce案件履歴+局員プロフィール+FAQ+契約ツール+PMチェックリストをSQLite統合検索。2026-08-23時点、FastAPIによるWeb化に着手(ローカル動作確認済み、ホスティング先未定)。2026-08-26、AI Agency Team(ChatGPT側の企画書生成GPT)と組ませるため状況報告→5種類のアウトプットを返す機能を追加。当初想定のChatGPT Actions方式はホスティング未定で断念し、最終的にDB(33MB)+検索スクリプトをGPTのKnowledge/Code Interpreterにアップロードするホスティング不要方式(`gpt_integration/`フォルダ)に確定。同日、別Skill「Agency OS」向けにDBを軽量Markdown Knowledge Packへ変換する`generate_agency_os_pack.py`も実装(POC/FULL、月次再生成対応、sf_id非一意という新事実を発見)。さらに同日、300件サンプルでのKnowledge Card品質監査を実施し、why_it_matters/when_to_use/actionフィールドの大半に元資料に無い一般化・因果断定が混入していることが判明(`knowledge_quality_audit.md`)。全14,897件の再生成は中村さんの確認待ちで保留中。2026-08-27、Stage A/B分離の新Pipelineで
300件Regression Test完了(regression_report.md)、過剰一般化は56%→0.7%に改善も数値計算混入の
新課題を発見、対策実装をtask-007としてWindows側へ依頼済み(waiting)、FULL DB再生成は保留中。
2026-09-08、局内管理職向けPoC募集PPTX資料(概要/仕組み/使い方/PoCで試してほしいこと)を
dentsu GTMテンプレートで新規作成、実例は機密性の高い実案件(AGHケース)ではなく既存の
架空テストブリーフ(Nusantara Roast)を使用。同日、Agency OS Skillのpptx出力が電通フォーマット
にならない不具合を修正(テンプレート未同梱が原因、軽量化したdentsu_gtm_template_clean.pptxを
Skillに追加+deck-production.md/SKILL.mdを必須使用ルールへ改訂、動作確認済み)。
metadata: 
  node_type: memory
  type: project
  originSessionId: a2b1d5fa-32d1-43c1-a288-bd925645a6b0
  modified: 2026-08-26T22:08:40.224Z
---

## 概要
社内資料(SharePoint「GBCarekoko」サイト、DocAppライブラリのKnowledge/Toolフォルダ)をローカルLLMで読み込み、
「知見カード」(JSON+Markdown)として構造化する社内ナレッジ基盤。GBC_戦略企画部の取り組み。
きっかけは会社Mac(d14461)でChatGPTと構築していたもの(Continue+VS Codeで不安定化→純Pythonへ転換)。
そのChatGPTセッションが利用上限に達し、PDF引き継ぎ資料を経てClaude Codeへ引き継がれた(2026-08-15〜)。

## プロジェクトの場所(Dropbox経由で複数Macから見える共有フォルダ)
`中村正樹/Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
(GBC_戦略企画部配下は会社Dropboxと個人Dropbox双方からアクセス可能な共有フォルダ)

## アーキテクチャ
- Ollama + `qwen3:8b`(コード用の`qwen2.5-coder`ではなく通常版。知見の要約・分類には非coderモデルの方が適切)
- パイプライン: `Evidence → Fact → Insight/Knowledge → Card` の3段LLM呼び出し
  - `src/readers.py`: pdf(pymupdf)/pptx/docx/xlsx/md/txt を統一形式`{page, section, text}`で読む
  - `src/extractor.py`: 資料を`chunk_size`(3000字)+`overlap`(300字)でチャンク分割し、各チャンクからFact候補を抽出。
    LLMが返した引用(evidence quote)を元資料の各ページ/シートと突き合わせて実際のページ番号を機械的に特定
    (`_locate()`。ページ番号はLLMに推測させずPython側で確定させる設計)
  - `src/knowledge_builder.py`: Fact→Knowledgeへ変換
  - `src/card_builder.py`: Knowledge→KnowledgeCard(dataclass)、JSON保存・読込
  - `src/markdown_writer.py`: KnowledgeCard→Markdown(YAML frontmatter付き、Obsidian互換)
  - `src/deduplicate.py`: 類似カードを検出しrelated_cardsで相互リンク(カード自体は削除しない=証拠を消さない設計)
  - `src/sharepoint.py`: ローカルファイルパス→SharePoint直リンクURLを機械的に再構築(`config.sharepoint.input_root`基準の相対パスをURLエンコードして接続)
  - `main.py`: 全体オーケストレーション、resumable(処理済みマニフェスト)+worker分割対応
  - `dedupe.py`: 全カード読み込んで重複統合をかける独立スクリプト(main.pyとは別、いつでも再実行可)

## データモデル(`src/models.py`)
`Evidence(quote, file, path, page, section, url)` / `Fact(title, summary, evidence, country, client, industry)` /
`KnowledgeCard(id, title, knowledge, why_it_matters, when_to_use, action, warning, confidence, evidence, country, client, industry, tags, related_cards, created_at)`
- `country`/`client`/`industry`は2026-08-15にユーザー要望で追加(「国名が分からない知見は使えない」「クライアント名も業界名も必要」)。
  抽出は**最初のextract.txt段階**で行う(後段は元の資料全文を見ていないので国/クライアント情報を復元できないため)。
- カードIDは`GBC-`+UUID4hex12桁。当初6桁だったが1万件規模で誕生日問題により衝突確率が無視できず(~85%)拡張した。

## 設計原則(引き継ぎ資料由来、5原則)
1. Evidenceが無い知見は作らない
2. FactとInsight/Knowledgeは分ける
3. AIは推測しない(資料に書かれていないことは書かない)
4. あとから必ず元資料へ戻れる(file, path, page, url を保持)
5. 知見はActionへ繋がる形にする

## 2台並行処理(Mac + 自宅Windows RTX3090)
`config.yaml`は共有設定(モデル名・chunk設定・SharePoint URLマップ)のみに留め、マシン固有値は環境変数で渡す
(`GBC_WORKER_ID`, `GBC_WORKER_COUNT`, `GBC_INPUT_DIR`, `GBC_SHAREPOINT_ROOT`)。
CRC32ハッシュで`input_dir`相対パス(`.as_posix()`で区切り文字統一)を分割キーにする静的分担。
処理済みマニフェストは`output/processed_files_worker{N}.txt`とworker毎に分け、**判定は全workerのmanifestを
まとめて見る**(自分の担当分だけでなく他マシンの処理済みも見る)。これにより、一方が担当分を終えたら
`GBC_WORKER_COUNT=1`に切り替えて相手の残りを二重処理なく巻き取れる。
Windows側とはSlack等の直接連携が無いため、ユーザーが2つの独立したClaude Codeセッション間でメッセージを
手動コピペ中継する運用だった。

## 踏んだ罠(次回また同じことをやる時のために)
- **Qwen3のデフォルト思考モード**: Ollama API呼び出しに`"think": false`を入れないと、内部で大量の推論トークンを
  生成し1呼び出しが300秒超でタイムアウトする。`temperature`も0.2程度に下げないとJSON出力が不安定(壊れたJSONを
  返すことがある)。`src/ollama.py`の`chat_json()`はJSON解析失敗時に3回までリトライする設計。
- **`.venv`と頻繁に書き換わるログを絶対にDropbox同期フォルダの中に置かない**。Mac版(Unix形式)とWindows版が
  同じ`.venv`パスで衝突し、両方壊れた(Dropbox conflicted copy多発)。修正後はvenv・ログともDropbox外のローカル
  パス(このMacでは`~/gbc_knowledge_venv`, `~/gbc_knowledge_logs`)に配置。[[feedback_venv_outside_dropbox_sync]]参照
- **CRC32分割は絶対パスではなく相対パス+posix正規化でハッシュすること**。絶対パス(`/Volumes/...` vs `D:\...`)や
  区切り文字(`/` vs `\`)が違うと同じファイルが両マシンで別workerに割り当てられ、担当が噛み合わなくなる
- **外付けSSD(exFAT)は長時間の無人実行中に瞬断することがある**。読み込み失敗を「処理済み」としてmanifestに
  書いてしまうと二度と再試行されなくなる重大バグを一度作った(163件中150件が巻き添えになった)。読み込み失敗時は
  manifestに書かずnext runで再試行させるのが正解
- **dedupe.pyは素朴なO(n²)総当たりだと15,000件規模で終わらない**。同一出典ファイル+タイトル先頭一致でブロック化
  してからUnion-Findで連結成分を取る方式に変更、23秒で完了するようになった
- **macOSのLaunchAgent(`~/Library/LaunchAgents/*.plist`)はログイン時に自動的に再ロードされる**。
  `launchctl bootout`で止めただけではファイルが残っているので、完全に終わらせたい時はplist自体を削除する必要がある

## 現状(2026-08-16時点、Mac側作業を一旦終了)
- 対象コーパス: 402ファイル(Knowledge 345 + Tool 68のうち対応拡張子)
- 生成カード数: 14,897件(JSON+Markdown)
- 重複統合: 672グループ、1,564件のカードに`related_cards`をリンク済み
- 抽出0件だったファイル: 12件(画像中心スライド・空の表紙ページ等、内容的に妥当なケースと判断)
- 両マシンとも担当分を完了。ユーザーは「会社Macで続ける」とのことで個人Mac側の作業はここで一旦終了
  (`~/Library/LaunchAgents/com.gbc.knowledge.batch.plist`は削除済み、次回はまた明示的にセットアップが必要)

## 今後の展開(引き継ぎ資料に書かれていた将来構想、未着手)
Phase2: Knowledge Graph化(知見同士のリンク)/ Phase3: Assistant Partner(業務報告からPush型で関連知見を提示)/
Phase4: GPT連携 / Phase5: Web化・SharePoint連携。当面はPhase1(知見収集)が最優先という方針だった。

## 2026-08-17: メタデータ品質問題の発見・修正・本番backfill完了
中村さんが会社Mac(d14461)で作業再開を希望し、個人Mac側の「GBC知見収集ローカルLLM」の
続きだと判明(トリガーフレーズが不明瞭だったため特定に手間取った経緯あり)。

### 発見した問題(14,897件の生成済みカードを検証)
- **tags フィールドが全件(100%)空**: `models.py`にフィールドはあるが、
  どのプロンプト(extract.txt/knowledge.txt/card.txt)もtagsを一度も要求していない、
  純粋な未実装漏れだった
- **country/client/industry の空欄率が異常に高い**(85%/88%/68%)。本文に国名が
  明記されているのに空欄のケースを複数確認(例: Myanmarと明記されているのに
  country空欄)
- **旧形式(6桁hex)IDが1,767件(11.9%)残存**(誕生日問題対策で12桁化した際の
  移行漏れ。ただし実際のID衝突は0件で実害は無かった)

### 対応方針: 既存カードのevidence(引用)だけを再利用してメタデータのみ埋め直す
新スクリプト `backfill_metadata.py` を作成。元資料(外付けSSD)は一切読み直さず、
カードに保存済みのevidence.quote等だけを使うため、SSD未接続のマシンでも実行可能。
tagsは自由記述ではなく、SharePoint「GBCアレココ」の既存タグ体系
(`config/gbc_tag_taxonomy.json`、[[gbc_weekly_report_kimura_dmd_project]]で
取得済みだったものを流用)から選択式にした。

### ローカルLLM(qwen3:8b)特有のハルシネーションと対策の変遷
プロンプトの指示だけでは防ぎきれず、最終的に**コード側での機械的な検証**に
移行した。時系列:
1. 初回テスト(20件): 15%で根拠不明な補完 → プロンプト強化
2. 再テスト: 「Digi-Keyは米国企業だから」のような**企業名からの一般知識推測**が
   残存 → プロンプトにさらに強い禁止文言を追加
3. 再々テスト: プロンプトでは対処しきれない、**evidence中に企業名が一切
   登場しないのに"Dentsu"/"Advertising"等を丸ごと捏造**するケースを発見
   (学習データの記憶が漏れ出た可能性)。ここで方針転換し、
   `_grounded_in_evidence()`(NFKC正規化+部分文字列一致)でLLMの回答を
   機械的に検証し、evidence引用文に実在しない値は自動破棄する方式に変更。
   industryも同様に、"industry_evidence_phrase"(判断根拠となる引用)を
   LLMに別途返させ、その引用文自体をevidenceと照合する二段構えにした
   (タグの候補一覧に「Event Management」のようなテーマ名を書いてしまう
   誤用も、候補を21種類の正式業種タグに絞ることで機械的に排除)
4. **教訓**: 8Bクラスの小型ローカルLLMは、プロンプトで「推測するな」と
   指示するだけでは不十分。特に固有名詞(企業名等)がキーになる補完は、
   コード側の文字列照合で検証しないと信用できない

### 汚染データの発見・除去
上記の検証機構導入前に、ユーザーがWindows機のチャット窓を2つ同時に開いて
それぞれ独立にフル実行を走らせてしまい、旧プロンプト・検証なしのコードで
約3,000件規模のカードが処理される事故があった(データ破損は無く、
「空欄のみ埋める」設計により上書き事故も無かったが、汚染された非空値が
残った)。`clean_ungrounded_fields.py`という新スクリプトで対応:
- **重要な設計判断**: 対象を「tagsが非空のカード」に限定した。tagsは
  main.pyの元々の抽出処理(このbackfillプロジェクト以前)では絶対に生成
  されないため、「非空=今回のbackfillが触った証拠」として確実に使える。
  最初これを絞らずevidence.quote全件と照合したところ7,407件がヒットし、
  今回のbackfill以前からmain.pyが正しく入れていた既存データまで巻き込む
  ところだった(evidence.quoteは元の抽出時に参照した3000字チャンクより
  ずっと狭い1文だけなので、正しく入っていた値でも引用文には無いことが多い)。
  **同種の作業をする際は、必ず「いつ・どの処理が触ったか」を機械的に
  区別できる目印を用意してから範囲を決めること。**
- 対象2,982件のうちcountry 602件・client 302件を根拠なしとして破棄、
  industry 1,155件・tags 2,982件は一度も検証していなかったため一律破棄し、
  manifestをリセットして正しいコードで再処理させた

### 本番フル実行の結果(2026-08-17 13:15-16:31、Windows RTX3090、約3時間15分)
対象14,772件(事前テスト分と合わせ全14,897件) / 更新8,815件・変更なし5,954件・
エラー3件。根拠グラウンディングによる自動破棄は本番規模で323件発生
(安全機構が実際に機能していたことの実測値)。

最終状態(全14,897件): country 15.8%充足(以前14.7%)/ client 13.0%(以前12.3%)/
**industry 27.6%(以前32.5%から意図的に減少— 質を優先し不正確な値を除去した結果)**/
**tags 58.8%(以前0% — 今回の最大の成果)**。

残課題(小規模・既知): (1) cp932コンソールでの文字コードクラッシュ3件
(→`sys.stdout.reconfigure(encoding="utf-8", errors="replace")`で修正済み、
該当3件は未処理のまま残っているので次回実行時に自動再試行される)、
(2) LLMのJSON解析失敗38件が誤って「処理済み」としてmanifestに記録され
再試行対象から漏れる問題(→`backfill_one()`がNoneを返す設計に修正済み、
ただし今回発生した38件自体は遡って特定できず未修正のまま残存)。

## Mac↔Windows 非同期作業依頼キュー([[claude_relay_system]]参照)
今回のWindows側との協業のために`.claude-sync/claude_relay/`という汎用の
ファイルベース中継システムを構築した(このプロジェクト専用ではなく全プロジェクト
で使い回せる)。詳細は独立メモリ[[claude_relay_system]]を参照。

## 2026-08-17後半: 品質テスト2件 → Salesforce案件履歴の統合、SQLite検索インデックス構築

### 品質テストで判明した限界
backfill完了後、中村さんの依頼で実際の業務報告2件を使い検索品質をテストした:
- **ダイキン(重金属不使用宣言書・DPA契約の相談)**: ほぼ0件。重金属/DPA/宣言書等の
  キーワードが全く無く、SharePoint資料(GBCアレココ)には元々この種の法務・
  コンプライアンス実務の資料がほとんど無いことが判明
- **ANA(グローバルデジタルメディアピッチ)**: 49件ヒットし非常に有用(ブランド
  戦略・過去クリエイティブ・グローバルピッチの組織体制知見等)。ANAのように
  過去に厚く文書化された既存クライアントには強いが、案件の厚みで精度が大きく
  変わることが分かった
- 検索方式自体の限界も判明: 素朴な部分一致検索は誤検出が多い(例:"DPA"が
  "food**panda**"に、"インド"が"インド**ネシア**"に、化学規制の"REACH"が
  広告用語"reach"(到達率)に、それぞれ紛れ込む)

### Salesforceデータの統合(中村さんの新規要望)
「過去のGBC作業履歴と、誰がその事例を知っているかを提示したい」という要望を受け、
Salesforceの「GBC案件/Items」オブジェクト(週報で使っている
`00O7F00000AmEiQUAV`と同一レポート定義)の期間フィルタ・優先度フィルタを両方
外して全期間データを取得した。

- **取得結果**: 14,936件(2005年〜2029年、責任者(GBC)充足率99.8%・
  ユニーク責任者161名)。保存先: `salesforce_source/GBC全履歴_案件活動_20260817.xlsx`
- **ハマった罠**: 画面上で一時フィルタを広げてもエクスポートは保存済み条件に
  戻ることがある(既知の罠、[[salesforce_report_download_automation]]参照)。
  メール認証を挟むと特に起きやすい。今回は中村さんが手動でブラウザ操作を完了させ、
  Chromeのdownloads履歴(SQLite `History`テーブル、`cp <profile>/Default/History`
  してから`sqlite3`でtarget_pathを引く)から実ファイルを特定した
- **オンスクリーン表示は2,000行上限**だが、エクスポート自体はその上限を受けない
  (合計レコード数はオンスクリーンでも正しく表示される)

### 設計判断: LLM不要、SQLite+FTS5で統合検索
中村さんから「統合するかはどちらでも良い、検索が速い方で」「LLMを使うかは
考えて」と判断を委ねられ、以下を検討・実施:
- **検索速度**: 従来の「毎回全JSONファイルをglobで読む」方式は14,897件でも
  数秒かかっていた。ファイルを1つのフォルダにまとめるかどうかより、
  そもそもインデックスが無いことが遅さの本質だったため、**SQLite+FTS5の
  検索インデックスDB**(`build_search_index.py`→`output/knowledge_index.db`)
  を新規構築した。doc_cards(既存14,897件)とcase_records(Salesforce
  14,936件)を別テーブル+別FTS5仮想テーブルにしつつ、`search.py`で両方を
  同時にクエリして統合表示する設計にし、「統合するか分けるか」の二択を
  実質的に無効化した。効果: ANA検索30ms、ダイキン検索11.5ms(以前は数秒)
- **LLM不要と判断した根拠**: Salesforceの「概要/アップデート(5W1H)」欄は
  WHEN/WHERE/WHO等のラベル付き構造化フォーマットに従っている行が
  **全体のわずか2.8%**(実測)で、残り97%は普通の自由記述文だったため、
  LLMに「読み取らせる」価値が薄いと判断。責任者・クライアント・予算・
  完了日は最初からSalesforceの構造化列そのもので、**地域(Region)列も
  実は6値(APAC/Global/Other/Americas/EMEA/Japan)に整理済みのピックリスト
  だった**(実測、正規化の必要すら無かった)。自由記述部分はFTS5全文検索
  に任せることで、LLM呼び出しゼロ・無料・ハルシネーションリスクゼロで
  実用的な検索を実現した。5W1Hラベル付きの2.8%だけは`parse_5w1h()`で
  正規表現により機械的に分解している(推測ではなく決定的パース)
- **教訓**: 今日一日「LLMは根拠が無いと平気で捏造する」問題と戦ってきたが、
  データソースが元々構造化されている場合はLLMを挟まない方が速く安全。
  LLMが本当に必要なのは「非構造化文書から事実を読み取る」段階だけで、
  それ以外(正規化・分類・検索)は決定的な方法で代替できないか毎回検討すべき

### 検証結果(2026-08-17時点)
`search.py`でANA/ダイキン双方を再テスト:
- **ダイキン**: SharePoint単独では0件だった状態から一変、中村さんが最初に
  提示した業務報告と**同一の案件**(「2026 ダイキン グローバルブランド情報発信」、
  責任者: 勝又隆至さん)が直接ヒット。加えてタイ/ベトナムでの過去のダイキン案件
  (FutureCompassPJ、製造業ブランディング事例収集)も担当者名付きで発見
- **ANA**: 過去のピッチ結果(「敗退、獲得代理店はBBDO、アニメ手法提案が勝因」等)
  まで担当者名付きでヒット。Salesforce統合により「勝敗の実績」という
  SharePoint資料には無かった情報が加わった

## 2026-08-18: 元データへのURL付与 + FTS5→LIKE方式への転換 + 局員プロフィール統合

### 元データURLの付与(中村さん要望)
検索結果から元データへワンクリックで戻れるようにした。
- **SharePoint(doc_cards)**: 元々`evidence.url`をカードごとに保持していた
  (main.pyのsrc/sharepoint.pyが生成済み)ので、search.pyの表示に追加するだけで対応
- **Salesforce(case_records)**: エクスポートしたExcelにはIDもハイパーリンクも
  含まれていなかった(要確認・実測)。中村さんが提示したURLパターン
  (`https://dgx.lightning.force.com/lightning/r/GBC__c/{id}/view`)から、
  レポートに`GBC案件/Items: ID`列を追加すれば取得できると判明。
  **既存の週報レポート(00O7F00000AmEiQUAV)は編集せず**、「名前を付けて保存」で
  `GBC全履歴_知見集約用`という別レポートを新規作成し、そちらにID列を追加・
  期間フィルタを外して再エクスポート(14,939件、`salesforce_source/
  GBC全履歴_案件活動_20260818.xlsx`)。SF_RECORD_URL_TEMPLATEでURL組み立て

### 検索方式をFTS5からLIKEへ変更(重要な修正)
FTS5(既定のunicode61トークナイザー)で「英国」と検索しても、実際に
「英国ロンドン駐在」と書かれたカード(田辺さん)がヒットしないバグを発見。
原因は日本語に分かち書き(単語間スペース)が無いため、トークナイザーが
正しく単語区切りを認識できないこと。trigramトークナイザーも試したが、
3文字未満のクエリ(「英国」「中国」「米国」等、日本語の国名に極めて多い
2文字パターン)では機能しなかった。**この規模(3万件強)ならLIKE(部分一致、
インデックス無しでも全表走査は10〜30ms程度)で十分高速**と判断し、FTS5仮想
テーブルを廃止してLIKEベースの検索に統一した(`build_search_index.py`/
`search.py`)。日本語データを検索対象にする時はFTS5を安易に使わず、まず
実データで短い日本語クエリが引けるか検証すること。[[feedback_prefer_deterministic_over_llm]]
とも通じる教訓(凝った仕組みより素朴な方法が確実、という点で)。

### 局員プロフィールの統合(SharePoint「今週の注目局員」)
`https://esq365.sharepoint.com/sites/gbcknowledgesharearekoko/SitePages/
attentionStaffs.aspx`が局員紹介ページへのリンク集(41件、うち39件を正常取得)
と判明。各人のページは「名前/所属/趣味/海外経験/担当業務」の表1つ+自由記述
(挨拶・経歴・エピソード)という共通構造。REST APIではなく個別ページを
Playwrightで直接巡回してスクレイピング(`sharepoint_staff_source/
staff_profiles_20260818.json`)。趣味38/39件・海外経験14/39件が充足
(全員が海外駐在経験を持つわけではないため、この数字は自然)。
DBの`staff_profiles`テーブルに格納、urlはページ自体のURLをそのまま使う
(Salesforceと違い変換不要)。「タイ経験者を探す」「英国経験者を探す」等の
検索で正しく人物とプロフィールURLがヒットすることを確認済み。

### 現状(3ソース統合済み、2026-08-18時点)
`output/knowledge_index.db`: doc_cards 14,897件・case_records 14,939件・
staff_profiles 39件。すべて元データへのURL付き、LIKEベースの高速検索
(数十ms)。`search.py`は簡易CLIのみ(本格的な問い合わせインターフェースは
未着手)。Salesforce/局員プロフィールいずれも定期更新の仕組み化は未着手
(今回は一回限りの手動取得)。次回候補: 検索インターフェースの本格化、
データ更新の自動化。中村さんに提示済み、まだ未確定。

## 2026-08-19: 実データでの品質テスト(ANA/ダイキン)、電通GTMテンプレートでの
台割自動生成デモ
中村さんの依頼で実際の業務報告2件をテスト。「タイの味の素ブランドキャンペーン」
の報告文からは、client="味の素"での直接検索1件に加え、country="タイ"×契約/
ベンダーの精緻フィルタ(「タイ」の単純部分一致は「タイアップ」等に誤爆するため
除外パターンを追加)で65件の高精度なヒットを得た。結果を電通GTM PowerPoint
テンプレート([[dentsu_pptx_template]])で台割(穴埋め式)として自動生成する
デモも実施(`build_daiwari.py`、1-3-1方式+3ファクト+解釈フレームワーク
[[proposal_writing_framework]]を踏襲)。検索結果の「責任者名」「過去実績の
数値」をそのままAppendixスライドに実データとして反映できることを実証した。

## 2026-08-21: GBC LaunchPad構想との統合(中村さんが「同じ構想」と判断し統合)
中村さんの協業者から届いた資料(`GBC Lauchpad0820.pptx`ほか4ファイル)が、
このプロジェクトと概念的にほぼ同一の構想(「入力したキーワードに関連コンテンツ
が自動で集まる」「誰に聞けばよいかを毎回確認せず提示」「似た案件から近道を
つくる」)と判明。中村さんの指示で**LaunchPadを今後の主軸とする**方針に変更し、
全ファイルを`launchpad_source/`に統合。

### 新規追加した3テーブル(いずれもLLM不要、決定的パース)
- `faq_records`(88件): アカウントプロデュース部FAQリスト。既存の構造化データを
  そのまま取り込み
- `contract_tools`(25件): GBC契約ツール一覧(eMarketer/RECMA/WARC/Statista等)
- `case_briefs`: 届いた2件の実案件ブリーフィング(Immersive Fort Las Vegas、
  Inoac ID)を番号見出しでセクションパース。**重要な設計判断**: 中村さんから
  「これは特定クライアント案件で使うものなので、それ以外ではユーザーに提示
  する必要はない」と明確な指示があり、実案件の内容(クライアント名等)は
  `search.py`の一般検索から除外し、DBには保持するが検索非公開とした。
  代わりに様式(セクション構成)だけを`launchpad_source/task_briefing_format_template.md`
  という汎用テンプレートとして抽出し、これを「Case & Format」機能の実体とした。
  **教訓**: 複数クライアントの情報を横断検索できる基盤を作る際は、個別案件の
  機密情報が意図せず別クライアント文脈で露出しないよう、都度「これは一般公開
  してよい情報か」を確認する必要がある。

### PM CHECKLIST機能の実装方針(`pm_checklists`テーブル、`checklist.py`)
LaunchPadの「案件タイプごとに確認すべき項目を最初に提示」機能に対応。
**チェックリストを一から創作せず、既存のSharePoint知見カードを根拠として
引用する設計**(source_idでdoc_cards.idに遡れる)。「Global Pitch」タイプのみ
7項目分の十分な根拠(5R Qualification Process、GBCの役割定義、Glo-Cal体制、
等)が見つかったため構築、他の案件タイプは根拠不足のため空のまま(推測で
埋めない)。`python3 checklist.py "Global Pitch"`で参照可能。

### PROCESS & TOOLKIT機能(`tool_phase_mapping`テーブル)
契約ツール25件を①Kick-off準備②リサーチ・情報収集③提案作成④実行⑤振り返り・
評価の5フェーズにマッピング。初稿はツール説明文からの機械的な分類だったが、
中村さんの実務知識で訂正あり(RECMA/COMvergenceは「エージェンシー評価」ではなく
「クライアントの競合社調査・出稿量調査」用途)。**教訓**: ツールの公式説明文
だけからの用途推測は、実際の現場での使われ方とズレることがある。ドラフト提示
→実務者確認、のフローが有効だった。

### LaunchPadの6機能軸に対する充足状況(2026-08-21時点)
RELATED CONTENTS/DATA & INSIGHT=充足、EXPERT NETWORK=部分的(Salesforce
責任者161名は充足、局員プロフィールは39名の一部のみ→**完全な名簿はあるが
スキルセット情報が無いため拡張不可、と中村さんから明言済み**、これ以上は
望めない)、CASE & FORMAT=様式のみ(実案件2件は非公開のため薄いまま、
中村さん曰くこれ以上の蓄積フォルダは無い)、PROCESS & TOOLKIT=構築済み、
PM CHECKLIST=Global Pitchのみ構築済み、AI ACCELERATION=台割自動生成等で
実証済み(機能であってデータではない)。

## 2026-08-23: Webアプリ化に着手(個人Mac、続きは会社Macへ引き継ぎ)
中村さんから「Webアプリにできるか」と質問があり、既存のCLI(search.py)+
knowledge_index.dbをそのまま流用してWeb化した。データパイプライン側は
無改修。

### 利用範囲・ホスティングの確認結果
- 想定利用者: GBC戦略企画部など少人数チーム(自分専用ではない)
- ホスティング先: **未定、IT部門に確認が必要**とのこと(社内サーバー/VM/
  Azure等の候補はあるが心当たりがまだ無い)。Salesforce案件情報・局員
  プロフィール等の機密データを含むため、公開Webサービスやpublicなクラウド
  への安易なデプロイは不可という前提で設計した
- 上記の理由で、まずは「どこにでも後からデプロイできる」ホスティング非依存の
  構成(標準的なFastAPI、Docker化しやすい単一プロセス)を優先し、ローカルで
  動くところまでを今回のスコープとした

### 実装したもの
- 場所: `GBC-Knowledge/webapp/`(既存プロジェクトフォルダ内、Dropbox経由で
  会社Mac/個人Mac双方から見える)
  - `app.py`: FastAPIバックエンド。`search.py`のLIKE検索ロジックをAPI化
    (`/api/search?q=`)、加えて`pm_checklists`→`/api/checklist/{case_type}`、
    `tool_phase_mapping`+`contract_tools`のJOIN→`/api/toolkit`も新規API化
  - `static/index.html`: 依存ライブラリ無しの単一HTML/CSS/JS。
    統合検索/PM CHECKLIST/PROCESS & TOOLKITの3タブ構成
  - `requirements.txt`: fastapi, uvicorn
  - DBは`output/knowledge_index.db`をそのまま参照(コピーしていない)
- **`case_briefs`テーブルは意図的にどのAPIからも除外**(2026-08-21の
  既存設計判断「実案件の機密情報は一般検索に出さない」を踏襲)
- venvは`~/gbc_knowledge_venv`に作成(Dropbox外、[[feedback_venv_outside_dropbox_sync]]
  の罠を踏まないため)。起動は`uvicorn app:app --port 8800`、
  `http://localhost:8800`で動作確認済み(検索/toolkit/checklistの各API
  ともに正常応答、ブラウザ表示も確認)。作業終了時にプロセスは停止済み

### 残作業(会社Macで継続予定)
1. IT部門にホスティング先を確認(社内サーバー/VM/Azure等)
2. 決まり次第、`webapp/`をそこへデプロイ(構成上どこでも動くはずだが未検証)
3. 会社Mac(d14461)側にも別途venvを作る必要あり(Dropbox越しのvenv共有は
   既知の罠のため不可、個人Mac側のvenvとは別物として作成すること)
4. 認証の要否は未検討(社内ネットワーク限定アクセスなら不要かもしれないが、
   ホスティング先が決まってから改めて判断)

## 2026-08-25: 会社Mac(d14461)でローカルサーバー起動完了
`~/gbc_knowledge_venv_d14461`(Dropbox外、個人Mac側`~/gbc_knowledge_venv`とは別物)を
新規作成。**会社Mac(d14461)はデフォルトでpypi.org等の外部PyPIに直接到達できず
(`connect timeout`)、社内プロキシ経由でのみ到達可能**と判明。プロキシURLは
`~/.npmrc`に設定済みの`http://proxy1.dentsu.co.jp:8080`を流用
(`export https_proxy=http://proxy1.dentsu.co.jp:8080 http_proxy=...`してから`pip install`)。
これで`fastapi==0.141.1`/`uvicorn==0.52.4`のインストールに成功。
**教訓**: 会社Mac(d14461)でpip installが原因不明にタイムアウトする時は、まず
`~/.npmrc`のproxy設定を確認してhttp_proxy/https_proxy環境変数に流用すること。

サーバーは`cd webapp && nohup ~/gbc_knowledge_venv_d14461/bin/uvicorn app:app --port 8800`
で起動、`/api/search`・`/api/toolkit`とも正常応答を確認済み(バックグラウンドプロセスとして
起動中、ログは`~/gbc_knowledge_logs_d14461_server.log`)。DBは`GBC-Knowledge/output/
knowledge_index.db`をDropbox経由でそのまま参照(コピーなし)。
IT部門へのホスティング先確認は未着手のまま(引き続き会社Macでのローカル起動のみ)。
詳細経緯は[[work_status/gbc_intelligence_engine_webapp_d14461_setup_20260825]]参照。

## 2026-08-26: ChatGPT Custom GPT Action向け統合エンドポイント`/api/report`を新設
中村さんの依頼で、「知見活用プロジェクト」と、別途ChatGPT側で構築中の
「AI Agency Team」(企画書生成担当GPT)を統合する方針が決まった。役割分担:
知見活用GPTが状況報告から①PMチェックリスト②ツール紹介③関連データ/知見
④類似CASE・フォーマット⑤エキスパート紹介の5つを出し、それをAI Agency Teamに渡して
企画書に組み込む。

`webapp/app.py`に`/api/report`(operationId: `getSituationReport`)を新設し、
既存の個別API(`/api/search`等はWeb UI用に維持)とは別に、5カテゴリを1回の呼び出しで
返す統合エンドポイントとした。設計:
- `keywords`(カンマ区切り、AND条件)・`case_type`・`phase`をクエリパラメータとして受け取る
  (状況報告の自然文からキーワードへ分解する作業はGPT=LLM側に担わせ、API側は
  従来通り決定的なSQLのみ、という役割分離。[[feedback_prefer_deterministic_over_llm]]の
  方針を踏襲)
- 5カテゴリの実体: ①`pm_checklists`テーブル(既存) ②`contract_tools`×
  `tool_phase_mapping`(既存、phase指定時はフェーズ一致+全フェーズ共通、未指定時は
  キーワード検索にフォールバック) ③`doc_cards`検索(既存) ④`case_records`検索+
  `launchpad_source/task_briefing_format_template.md`を常時同梱(類似CASEが0件でも
  雛形は必ず返す) ⑤`staff_profiles`検索+④でヒットした`case_records`の
  `responsible_person`(類似案件の元担当者)を統合、reasonフィールドでどちらの根拠かを明示
- `case_briefs`は`/api/report`でも引き続き非公開(既存方針を踏襲)
- ローカル(`localhost:8800`)で起動確認済み、5カテゴリとも正常応答
  (例: keywords="味の素,タイ"で類似案件2件+元担当者2名がヒット、phase指定で
  ツール19件がヒット、case_type="Global Pitch"でチェックリスト7件が根拠付きで返る)。
  `/openapi.json`に`operationId`/`description`/`summary`が正しく出ることも確認済み
  (GPT Actionsの「スキーマをインポート」にそのまま使える)

GPT Builder側の設定手順・Instructions本文(状況報告→keywords抽出のルール、
5見出しでの回答整形ルール、捏造禁止・0件の正直な報告等の禁止事項、AI Agency Teamへ
Markdown形式で引き渡す旨)を`GBC-Knowledge/gpt_integration/GPT_Instructions_知見活用GPT.md`
にまとめて作成済み。

**残課題→方針転換の経緯(2026-08-26)**: 当初はChatGPT Custom GPT Actionsを想定
していたが、ChatGPT側サーバーから到達可能な公開HTTPS URLが必須で`localhost`の
ままでは接続できない問題があり、ホスティング先(IT部門確認待ち)・ngrok一時公開の
是非という選択肢を提示。中村さんは「GPTにスキルとして読み込ませて、残りはChatGPTに
対応して貰う形にしたい」と回答したため、いったんAction方式の`openapi.json`を
静的ファイル化して渡す準備をした。**その後、中村さんから「知見データそのものを
渡した方がサーバー問題を解決できるのでは」と指摘があり、これが正しい方向と判断して
最終的にホスティング不要のCode Interpreter方式に切り替えた**(下記が最終形)。

### 最終方式: Code Interpreter + Knowledgeファイル方式(ホスティング不要)
`gpt_integration/`フォルダに以下を作成し、ChatGPT Custom GPTの「Code Interpreter &
Data Analysis」を有効にした上でKnowledgeとしてアップロードするだけで完結する構成にした:
- `knowledge_index.db`(33MBをコピー配置、doc_cards/case_records/staff_profiles等
  全テーブルそのまま)
- `query_report.py`: `/api/report`と全く同じロジック(複合キーワードAND検索、
  PMチェックリスト・ツール・知見・類似CASE・エキスパートの5カテゴリ抽出)を
  FastAPI非依存の素のPython関数`get_situation_report()`として切り出したもの。
  GPTがCode Interpreter内で`exec(open('/mnt/data/query_report.py').read())`→
  関数呼び出し、という形で実行する。ローカルで実行し`/api/report`と同一結果に
  なることを確認済み
- `task_briefing_format_template.md`(既存ファイルをコピー配置)
- `openapi.json`は将来Actions方式に戻す場合用として残置(今回は未使用)

**採用しなかった案とその理由**: 生データをテキストとしてKnowledgeファイルに
アップロードしChatGPT標準の埋め込みベース検索に任せる案は不採用。2026-08-18に
このプロジェクトが「FTS5(埋め込み風トークン検索)は短い日本語キーワードで
正しくヒットしない」と判明しLIKE+複合AND方式に切り替えた経緯があり、ChatGPT側の
埋め込み検索でも同じ問題(と、根拠なき推測=幻覚の再発)が起きるリスクが高いと
判断したため。Code Interpreterで同一のSQLロジックをそのまま実行させることで、
検索精度と「根拠に基づく回答」という設計原則をサーバーレスのまま維持している。

**データがOpenAI側にアップロードされる点は中村さんに確認済み**(全テーブルを
そのまま渡す方針で承認、2026-08-26)。`case_briefs`(実案件機密情報2件)は
DBファイル自体には物理的に含まれるが、`query_report.py`のどのクエリからも
参照しないため回答には出てこない(既存の非公開方針を維持)。

`GPT_Instructions_知見活用GPT.md`をCode Interpreter方式向けに全面改訂
(Actions方式の説明は末尾に「将来オプション」として残した)。
**次にこのプロジェクトに触るときは、ChatGPT側でのGPT作成・動作確認がどこまで
進んだかを中村さんに確認してから再開すること**。

## 2026-08-26: 「Agency OS」Skill向けKnowledge Pack生成機能を追加
別のChatGPT Skill「Agency OS」(Researcher/Strategic Planner/Creative Director等の
仮想エージェンシーチームを動的編成しRESEARCH→STRATEGY→CREATIVE→BUDGET→PPTXを
行う仕組み)からGBC共通知見を参照できるようにする依頼(25項目の詳細仕様書)。
`knowledge_index.db`(33MB、SQLite)は大きすぎ&Skill上でSQLite+Python検索を
そのまま実行できないため、Markdown形式のKnowledge Packへ変換する
`generate_agency_os_pack.py`を新規実装(プロジェクトルート、既存の
main.py/search.py等と同列)。

**分析→設計の順で実施**(いきなり実装しない、という指示に従った)。分析結果は
`agency_os_pack_analysis.md`。主な発見:
- doc_cards: country/client/industryの充足率が15.8%/13.0%/27.6%と低く主軸に
  使えない。tags列が58.8%充足かつユニーク値31種のみ(既存GBCタグ体系)と判明し、
  これを分割軸に採用(新分類をLLM/推測で作らない設計原則を維持)。ただし
  「tagsは非空だが中身が言語タグ(英語/中国語)のみでトピックタグが1つも無い」
  カードが大量(11,612/14,897=77.9%)にあり、結果としてタグベース分類は
  約22%にしか効かず大半が「untagged」バケットに集約されると判明(データの
  構造的限界として明記、新分類の推測作成はしていない)。
- case_records: 5W1H系フィールド(when/where/who/why/what/how)の充足率が
  軒並み2%台(14,939件中14,563件=97.5%が5W1Hを1つも持たない)。依頼書が
  想定していた「国レベル×業界/年/案件タイプ」での分割は、対応する構造化列が
  実データに存在しないため実行不可と判断。実際に使える地理軸はregion
  (APAC/Global/Other/Americas/EMEA/Japan の6分類、100%充足)のみ。

**Pack設計**: knowledge/(タグ別)・cases/(region別)・tools/・pm/・faq/・
experts/(Case Expert Index)・briefing/(task_briefing_format)+README.md+
manifest.json という構成。ファイル分割は固定件数でなくバイト数ベースの
貪欲パッキング(目標2MB/ファイル)。POC Pack選定(doc_cards 1,500件・
case_records 2,500件目標)は**乱数を一切使わない決定的スコアリング**
(doc: confidence×0.35+フィールド充足率×0.25+本文情報量×0.25+出典の質×0.15、
重複タイトルは非代表を-0.5減点/ case: 直近性×0.30+充足率×0.30+情報量×0.25+
出典の質×0.15、重複item_titleは非代表を-0.3減点)+層化割当(タグ/リージョンの
サイズに比例した目標件数配分、最低5件のフロアで多様性確保)で行う設計にした。

**Validationで3件の実装バグを発見・修正**(この過程で新たなデータ特性も判明):
1. case_briefs漏洩チェックが`task_briefing_format_template.md`自身の正当な
   出典引用(「出典:`241108_Inoac ID_Task Briefing 1 (1).docx`...」)を
   誤検知。実際の機密フィールド(background/objective/budget等)のみを
   対象に絞って修正。
2. **【重要な新発見】sf_id(Salesforce ID)が実は一意ではない**: 14,939件に
   対しユニーク値は4,111件のみ(1つのsf_idに最大210件が紐づく)。当初
   CASE_IDにsf_idを使う設計だったが、この発見によりrow_num(1〜14,939の
   密な連番、重複ゼロを確認済み)に変更、sf_idはSALESFORCE_IDとして
   参照情報のみに位置づけ変更。**この非一意性は他の用途(検索結果の
   重複排除等)にも影響し得るため、今後sf_idを識別子として使う設計をする
   際は要注意**。
3. Markdown構造検証が、report_text本文中に偶然含まれる"---"文字列
   (8件で確認)を誤検知。TYPE:行の直前に"---"があるかで判定する方式に修正。

**テストレポート生成でも既知の罠が再発**: 「タイ」→「タイアップ」への誤爆
(2026-08-19の味の素/タイ検証で判明済みの罠と同一パターン)がテストレポートの
grep処理で再発しているのを発見、negative lookaheadで除外して修正。

**最終結果**: POC(doc_cards 1,500件+case_records 2,500件、18ファイル、
4.21MB)・FULL(全件14,897+14,939件、27ファイル、24.83MB)を生成。
全Validation項目(ファイル存在/0件ファイル無し/case_briefs非漏洩/manifest件数
一致/Markdown構造/サイズ上限/ID重複無し/UTF-8可読/POC再現性)がOK。
テストレポート(Malaysia/B2B・SaaS・CRM/Thailand・Event/Influencer/
過去案件担当者の5テーマ)も想定通りの結果を`agency_os_pack_test_report.md`に
記録。月次運用は`python3 generate_agency_os_pack.py --db output/knowledge_index.db
--output output/agency_os_pack --mode poc`(FULL版は`--mode full`)で再生成、
DBは読み取り専用(`file:...?mode=ro`)で開くため実行失敗時も元DBは無傷。

## 2026-08-26(同日続き): Knowledge Card品質監査(重大、300件サンプル)→全件再生成は保留中
中村さんから「Agency OS PackのKnowledge Cardに、元資料に無い解釈・一般化・推奨行動の
混入や数値抽出誤りの疑いがある」との指摘。**いきなり全14,897件を再生成せず、まず
リスクベースで300件を監査せよ**との明示指示があり、`audit_select_sample.py`
(7カテゴリ層化抽出+数値/単位/通貨/年号の機械的整合性チェック)と
`knowledge_quality_audit.md`(監査報告)を作成した(既存DBは読み取り専用、変更なし、
md5/mtime確認済み)。

**主要発見(詳細は`knowledge_quality_audit.md`参照)**:
- **Knowledgeフィールド自体は概ね元資料に忠実**。しかし**why_it_matters/
  when_to_use/actionの体感8〜9割が、元資料に無い一般化・因果断定・
  プレゼクリプティブな推奨を含む**(1件の成功事例を再現可能な法則であるかの
  ように一般化するパターンが最頻出)。ACTIONフィールドにヘッジ表現
  (「可能性がある」等)を含むカードはサンプル300件中1件(0.3%)のみという
  機械的集計あり
- 重大な捏造例を複数発見: 「アメリカの重み係数はカナダの25倍」(実際は
  x25/x5=5倍という単純計算ミス)、根拠皆無の「9年ぶり」という年号捏造、
  調査に存在しない「都市部中高年層」というターゲット層の創作、著作権
  フッターのみのevidence_quoteから実在しないPhilips撤退ストーリーを
  生成、等
- RECMA報告書(511件のカードを生成した単一資料)等の**競合ランキング表由来
  カード群では、evidence_quoteが表の1行断片のみで年度/表題等の文脈が
  失われている**という構造的欠陥を発見(捏造ではなく、SOURCE_EVIDENCEの
  保存範囲が狭すぎる設計上の問題)
- **Negative Knowledge(失敗/訴訟/規制違反)は300件中1件のみ**(電通・
  東京五輪談合起訴の件)、しかも通常のポジティブなACTION推奨テンプレートに
  押し込められ「制裁による強制是正」という文脈が失われていた。
  TYPE:LESSON/FAILURE型がそもそも存在しないため

**中村さんが提示したschema改訂案**(SOURCE_FACT/INTERPRETATION/
TRANSFERABLE_IMPLICATION/HYPOTHESIS/RECOMMENDED_USEの分離、数値Quality Gate、
Source Quality階層、Knowledge Quality Score、Deduplication、Negative
Knowledge型、Human Review Queue等)は監査結果と整合しており妥当と判断。
pipeline修正案として、生成をStage A(SOURCE FACT抽出、元資料に無い情報を
一切含めない)とStage B(INTERPRETATION生成、Stage Aのみを入力とし因果関係の
断定を禁止)に分離することを提案済み。

**現在の状態**: 中村さんの明示指示により**全件再生成はまだ開始していない**
(監査結果の確認待ち)。次にこのプロジェクトに触るときは、(1)新パイプラインを
300件サンプルに試作適用してのRegression Test、(2)FULL DB適用要否の判断、
のどちらに進むか中村さんに確認すること。**Agency OS Pack(`gpt_integration/`
`output/agency_os_pack*/`)は今回の監査対象と同じ品質問題を抱えたまま**なので、
品質改善版(`agency_os_pack_v2/`)が出来るまでAgency OSへの本番投入は
慎重に判断すべき。

## 2026-08-26(同日続き): Regression Test実施中に会社Mac作業を中断→個人Windowsへ引き継ぎ
上記の新Pipeline(Stage A/B分離)を実装し、300件サンプルでRegression Testを
実行開始(会社Mac d14461に管理者権限不要でOllama+qwen3:8bを新規セットアップ、
[[ollama_company_mac_setup]]参照)。**追加の重大発見**: 既存DBの`evidence_quote`
自体が元資料の逐語引用ではなく、既にLLMによる要約・言い換えを経たテキストだった
(単純な部分文字列検索では300件中8割が元資料を特定できず、文字3-gramベースの
フォジーマッチに切り替えて解決)。35/300件処理した時点で、中村さんが会社Macを
シャットダウンする必要が生じ、個人Windows(自宅RTX3090)への引き継ぎとなった。
バックグラウンドプロセスは安全に停止(35件のjsonlは正常、データ破損なし)。
`regression_pipeline_v2.py`はマシン固有パスを環境変数化済み
(`GBC_SSD_ROOT`/`GBC_OLLAMA_URL`/`GBC_OLLAMA_MODEL`)、同じ`--out`ファイルへ
再実行すれば36件目から自動再開する設計。詳細は
[[work_status/gbc_intelligence_engine_regression_v2_20260826]]参照。
**次にこのプロジェクトに触るとき(会社Mac側)は、個人Windows側での進捗
(300件完了・レポート作成状況)を必ず中村さんに確認してから再開すること**。

## 2026-08-27: 個人Mac側で引き継ぎ状況を確認、Regression Test完了を発見→次タスクをWindowsへ依頼
中村さんから「会社Macがメインで進めていたPJの続きをこの(個人)Macでも引き継げるか」
との質問。確認したところ、個人Windows側が既にtask-006を完了させていたと判明
(300件全件処理・`regression_report.md`作成済み、2026-08-27 02:43、詳細は
[[work_status/gbc_intelligence_engine_regression_v2_20260826]]の追記分参照)。

**regression_report.mdの要旨**: generalization_suspect_rate(過剰一般化)が
56.0%→0.7%に劇的改善(新Pipelineの最大の成果)。一方でnumeric_error_rate
5.3%→21.0%・QUARANTINE件数15→75と悪化しているが、主因は「has_fact=False
(事実抽出不可)のカードを機械的に0点/隔離とする設計変更」であり、事実抽出に
成功した246件だけで見れば平均スコアは旧とほぼ同水準。severe事例8件+RECMA由来
5件は13件中12件で明確な改善を確認。**結論: FULL DB(14,897件)一括再生成は
時期尚早、まず3-1(SOURCE_FACTへの数値計算混入、例: GBC-0102B8C9F333の
小数点15桁比率)への対策を先に実装すべき**、との判断が示された
(FULL適用時の推定所要時間: 約80.7時間/3.4日、1プロセス)。

**個人Mac側の環境確認**: `~/gbc_knowledge_venv`(2026-08-23作成分)・
Ollama `qwen3.8:27b`(Windowsが最終的に使ったものと同一)は導入済み。
**外付けSSD「Extreme SSD」(元資料804ファイル)は個人Macには未接続** —
元資料への再アクセスが必要な検証作業はこのMac単体では完結しない。

**対応**: 中村さんの指示で「レポート内容を確認しWindows側への指示を準備する」
方針となり、`regression_pipeline_v2.py`のstage_a()・`backfill_metadata.py`の
`_grounded_in_evidence()`を読んだ上で、数値グラウンディングチェックの実装案
(SOURCE_FACT中の数値トークンをcontext_text全文に対して照合、小数点4桁超は
機械的にsuspect扱い)を設計し、`.claude-sync/claude_relay/windows_inbox.md`に
**task-007**として追記した(Status: waiting、中村さんのトリガーフレーズ待ち)。
task-007は63件のNUMERIC_SUSPECT事例での効果検証までを依頼、FULL DB再生成は
今回も明示指示があるまで禁止する制約を継続。

**次にこのプロジェクトに触るときは、task-007のStatus/Result欄を確認してから
再開すること**。

## 2026-08-27(同日続き): task-007完了(数値グラウンディングチェック実装・検証)
Windows側が`regression_pipeline_v2.py`に`numeric_grounding_check()`を実装
(SOURCE_FACT vs Stage Aに渡した元資料抜粋context_textを照合。小数点5桁以上は
無条件で`long_decimal`、それ以外の2桁以上の数値(年号除く)がcontext_text中に
無ければ`not_in_context`)。`regression_compare.py`の`score_new()`にも強制
QUARANTINE条件として組み込み済み(既存300件データには未適用、次回再実行分から反映)。

**検証結果**: 既存63件のNUMERIC_SUSPECTのうち17件(27%)を検出。`long_decimal`は
1件(GBC-0102B8C9F333、3-1で指摘した小数点15桁比率の計算混入を正しく検出)で
精査した範囲では誤検知ゼロ。`not_in_context`は16件検出したが手動精査4件中3件が
誤検知(①日本語「〜月」と英語月名表記のズレ、②ファイル名/ページ番号がSOURCE_FACT
本文に混入しその数字がフラグされた別種の問題、③欧州式コンマ小数点を桁区切りと
誤認識)で、精度に改善余地あり。ただし自動破棄ではなくQUARANTINE止まりの設計
なので誤検知があってもデータは失われない(安全側)。旧heuristicで未検出だった
残237件への適用では誤検知0件。詳細は`regression_report.md`11章に追記済み。
**推奨改善(必須ではない)**: (1)コンマを小数点区切りとして扱うケースの判定改善、
(2)ファイル名/ページ番号直前の数字を対象外にする。

FULL DB・既存Agency OS Packへの変更は今回も無し。**判断: long_decimalシグナルは
本番投入判断材料として十分信頼できるが、not_in_contextは改善余地ありのまま。
次にこのプロジェクトに触るときは、中村さんに(a)上記2点の精度改善を先にやるか
(b)このままFULL DB適用の是非を検討するか、どちらに進みたいか確認すること**。

## 2026-08-27(同日続き): 精度改善2点を個人Mac側で直接実装、実データ検証はWindowsへ依頼(task-008)
中村さんが「精度改善を先にやる」と選択。個人Macは外付けSSD(元資料)には
アクセスできないが、`regression_pipeline_v2.py`自体はDropbox同期フォルダ内に
あるため、コード修正自体はこのMacで直接実施できた(コーディングとSSDが要る
実データ検証は分離できる、という判断)。

**実装**: (1)`numeric_grounding_check()`にコンマ小数点対応(桁区切り用/欧州式小数点用の
2通りの正規化形のいずれかに一致すればgroundedとする)、(2)`_strip_filename_and_page_refs()`
新設(ファイル名・ページ参照の正規表現除去に加え、`context["source_file"]`の文字列が
SOURCE_FACT中にそのまま含まれる場合は丸ごと除去 — 正規表現だけでは"FY25"のように
拡張子と離れた数字を拾いきれなかったため)。

**個人Mac側での簡易検証**(SSD無し、`output_v2/regression_v2_results.jsonl`の
`source_evidence_quote`をcontext_textの近似として使用): GBC-01647E(コンマ小数点)・
GBC-0129FAFA0EDD(ファイル名/ページ番号)とも誤検知解消を確認、GBC-0102B8C9F333・
GBC-040C75E406BD(本物の問題)は退行なく検出維持を確認。GBC-00CAA957627A(英語月名との
表記ズレ)は依頼範囲外のため未対応のまま。

**次のアクション**: 実データ(本物のcontext_text)での本番同等の再検証を依頼する
task-008を`windows_inbox.md`に追記(Status: waiting)。63件全件の再検証・
GBC-01647E/0129FAFA0EDDの個別確認・残237件への新規誤検知有無の確認を依頼。
**次にこのプロジェクトに触るときは、task-008のStatus/Result欄を確認してから
再開すること**。

## 2026-08-27(同日続き): task-008完了(実データでの精度改善検証、63件中17件→13件)
Windows側が実データ(SSD経由locate_context()で再取得したcontext_text、LLM再呼出しなし)で
再検証。個人Mac側の2改善(コンマ小数点対応・ファイル名/ページ番号除外)により
63件中の検出数が17件→13件に減少。GBC-01647E・GBC-0129FAFA0EDDは実データでも誤検知
解消を確認(個人Macの近似検証と一致)。GBC-0102B8C9F333・GBC-040C75E406BD(本物の問題)は
退行なく検出維持。旧heuristic未検出だった残237件への新規誤検知は0件。GBC-00CAA957627A
(日英月表記ズレ)は依頼範囲外のため誤検知のまま残存(想定通り)。詳細は
`regression_report.md`12章に追記済み。

**判断**: 依頼された2パターンは実データでも解消確認、真陽性の退行無し。残る月表記ズレは
QUARANTINE止まりの安全設計のため許容範囲。**FULL DB(14,897件、約80.7時間)適用可否の
最終判断は変更なし — 中村さんの指示待ちのまま**。次にこのプロジェクトに触るときは、
FULL DB適用に進むか、さらに精度を詰めるか(月表記ズレ対応等)、中村さんに確認すること。

## 2026-08-27(同日続き): FULL DB適用の移行設計(スキーマ移行)を作成
中村さんが「FULL DB適用の可否を本格検討」を選択。ただし実際に検討すると、
新Pipeline(Stage A/B)は旧Pipelineと**スキーマそのものが違う**ことが未解決の
論点として判明: 旧`knowledge/why_it_matters/when_to_use/action/warning`に対し
新は`type/source_fact/interpretation/transferable_implication/do_not_generalize`
(actionは意図的に生成しない設計)。さらにtagsを新Pipelineは一切生成しない
(Agency OS Packのバケット分割の生命線であるtags 58.8%充足の仕組みが壊れる懸念)。
既にChatGPT Custom GPTにアップロード済みの`gpt_integration/knowledge_index.db`
(Code Interpreter方式、2026-08-26運用開始)も影響範囲に含まれる。

**80時間かけて処理しても本番への組み込み方が決まっていないと作業が無駄になる**
と判断し、いきなりFULL実行はせず`full_db_migration_design.md`という設計文書を
プロジェクト直下に作成した(分析→設計の順、いきなり実装しない方針を踏襲)。

**推奨方針**: 置き換えではなく「追加型(Additive)」— `doc_cards`に`v2_*`列
(type/source_fact/interpretation/transferable_implication/do_not_generalize/
quality_score/quality_bucket/has_fact)を追加し、旧列(knowledge/why_it_matters/
action等、tags/country/client/industryも含む)は無変更のまま残す。理由:
(1)新Pipelineがhas_fact=False(18%)で情報ゼロになるケースでも旧情報を失わない、
(2)tags(Agency OS Pack分割軸)・country/client/industry(既にbackfill_metadata.pyで
別途グラウンディング済み)を、検証の浅い新Stage Aの値で無条件上書きしない、
(3)ロールバックが容易、既存GPT統合・Web UIも無改修で動作継続する。

ダウンストリーム改修範囲を特定済み: `search.py`(doc_cols拡張)、`webapp/app.py`
(2箇所: /api/search, /api/report)、`generate_agency_os_pack.py`(render_doc_card
のフォールバック設計、doc_raw_scoreへのv2_quality_score反映)、
`gpt_integration/query_report.py`(webapp/app.pyとほぼ同一ロジックの別コピー、
二重改修が必要)。`gpt_integration/knowledge_index.db`のChatGPT側再アップロードは
**Claude Codeからは自動化不可、中村さんの手動作業として残る**。

**次にこのプロジェクトに触るときは、`full_db_migration_design.md`末尾の
4つのオープンな論点**(tags/country等の優先順位、has_fact=Falseの扱い、
QUARANTINEカードの検索露出可否、gpt_integration再アップロードのタイミング)
**を中村さんに確認してから、マイグレーションスクリプト実装→300件での試験→
FULL DB実行(qwen3.8:27b、Windows機、SSD接続、約80.7時間)の順に進めること**。

## 2026-08-27(同日続き): 移行設計の4論点、中村さんが全て決定
`full_db_migration_design.md`の4つのオープンな論点、全て決定済み:
①tags/country/client/industryは既存backfill値を維持(新Stage Aの値は不採用)
②has_fact=Falseのカード(約2,600件見込み)は「未検証」バッジを表示
③QUARANTINE判定カード(約3,700件見込み)は検索・Agency OS Pack双方から除外
④gpt_integration/knowledge_index.dbの再アップロードはAgency OS Pack確認と同時に
まとめて実施(中村さんの手動ChatGPT操作)
設計文書に反映済み(6章決定事項、4章ダウンストリーム改修範囲、5章ロールアウト手順)。

**次にこのプロジェクトに触るときは、`full_db_migration_design.md`の設計に沿って
マイグレーションスクリプト(output_v2 jsonl→doc_cardsのv2_*列UPDATE、ALTER TABLE含む)を
実装するところから再開する。実装後は300件サンプルで試験→問題なければFULL DB
(14,597件残、qwen3.8:27b、Windows機SSD接続、約80時間)実行、の順**。

## 2026-08-27(同日続き): マイグレーションスクリプト実装+ダウンストリーム4ファイル改修、300件サンプルで検証完了
`full_db_migration_design.md`の設計・4決定事項に沿って、個人Mac上で以下を実装(すべて
SSD不要、Dropbox同期コードのみで完結):

1. **`migrate_v2_schema.py`新規作成**: doc_cardsへの`v2_*`列ALTER TABLE(冪等)+
   `output_v2/regression_v2_results.jsonl`から`regression_compare.py`の
   score_new()/bucket()を再利用して分類・UPDATE。has_fact=Falseは`v2_quality_bucket=
   "UNVERIFIED"`(QUARANTINEとは別カテゴリとして明確に分離、決定②)、has_fact=Trueで
   bucket()がQUARANTINE判定したものはそのまま`v2_quality_bucket="QUARANTINE"`
   (決定③)。本番DB(output/knowledge_index.db)を直接指定すると`--allow-production`
   無しでは拒否する安全策付き
2. **`search.py`/`webapp/app.py`/`gpt_integration/query_report.py`**:
   doc_colsにv2_source_fact/v2_interpretationを追加、
   `(v2_quality_bucket IS NULL OR v2_quality_bucket != 'QUARANTINE')`条件で除外。
   search.py/webapp/app.pyは`GBC_DB_PATH`環境変数でテスト用DBに向けられるよう変更
3. **`generate_agency_os_pack.py`**: `build_knowledge_files()`でQUARANTINE行を除外、
   `render_knowledge_card()`はv2_has_fact=1かつbucket∈(VERIFIED,USABLE)の場合のみ
   新フィールド(Source fact/Interpretation/Transferable implication/Do not
   generalize)+TYPE/QUALITY_SCORE行を優先表示、それ以外は旧フィールドにフォール
   バック。has_fact=0の場合は`UNVERIFIED: true`行を追加。`doc_raw_score()`は
   v2_quality_scoreがあればconfidence代わりに使用

**検証**: 本番DBのコピー(scratchpad上、本番は無変更)に300件サンプルを migrate_v2_schema.py
で適用→内訳VERIFIED 109/USABLE 73/USE_WITH_CAUTION 43/QUARANTINE 21/UNVERIFIED 54
(21+54=75で監査時のQUARANTINE合算75と一致、正しく分離できていることを確認)。
search.py・webapp API(/api/search)・query_report.py・generate_agency_os_pack.py
(POCモード、全Validation OK)の4つとも、QUARANTINE除外・UNVERIFIEDバッジ表示・
新フィールド優先表示(TYPE/QUALITY_SCORE/Source fact等)が期待通り動作することを
実データで確認済み。テスト用ファイルはクリーンアップ済み(本番には一切触れていない)。

**次にこのプロジェクトに触るときは、ロールアウト手順(`full_db_migration_design.md`
5節)のステップ3、FULL DB本実行(残り14,597件、qwen3.8:27b、Windows機、SSD接続、
約80.7時間)に進んでよいか中村さんに確認してから着手すること**。実行後はステップ4
(migrate_v2_schema.pyを本番DBに`--allow-production`付きで適用)→ステップ6
(Agency OS Pack再生成+gpt_integration同時再アップロード)の順。

## 2026-08-27(同日続き): クオリティ優先の判断→残課題の棚卸し→task-009(未検証分レビュー)依頼
中村さんから「クオリティを優先したい、今のもので十分か」と問われ、率直に評価:
過剰一般化(56%→0.7%)は確実に改善したが、(1)SOURCE FACTへの解釈混入(20.0%、
regression_report.md 3-2章、今回未着手)、(2)数値チェックの検証範囲の狭さ(63件中
実際に人間が中身を見たのは5件のみ)、(3)月表記ズレ(GBC-00CAA957627A)という
既知の誤検知パターンが未対応、(4)300件サンプルがqwen3:8b/qwen3.8:27b混在という
検証条件の粗さ、の4点が未解決として残っていると回答。中村さんは「未検証の8件を
人間レビュー」を選択。

**レビュー着手前にレポート自体の集計ミスを発見**: regression_report.md 12章は
「それ以外の8件」としながら実際は10個のIDを列挙(レポート内でも「実際は10件」と
自己言及)、「上記4件」としながら列挙は5件、5+10=15≠13(63件中の検出数)で
辻褄が合っていなかった。個人MacはSSDが無く元資料を直接参照できないため、
正確な件数確定+実データでの人間レビューをtask-009としてWindowsへ依頼
(`windows_inbox.md`、Status: waiting)。依頼内容: (1)現行`numeric_grounding_check()`
再適用で正確な13件のID一覧を出力(過不足なく)、(2)既レビュー済み5件を除いた
残り全件を元資料と照合してレビュー(真陽性か新種の誤検知パターンかを判定)、
(3)新しい誤検知パターンが見つかれば対応要否の推奨も記載。

**次にこのプロジェクトに触るときは、task-009のStatus/Result欄を確認してから
再開すること**。解釈混入(20%)・月表記ズレ・モデル混在サンプルの3点は依然として
未対応のまま残っており、task-009完了後もFULL DB適用の可否は改めて中村さんと
相談が必要。

## 2026-08-27(セッション終了): 司令塔を個人Macから会社Macへ移行
中村さんが「Windowsにtask-009を依頼する、司令塔を個人Macから会社Macに移す」と
宣言しこのセッションを終了。**次に会社Mac側でこのプロジェクトに触れる際の
引き継ぎ状況**:
- task-009(数値グラウンディング疑い13件の正確な確定+未検証分の実データレビュー)は
  windows_inbox.mdでStatus: waiting、中村さんのトリガー待ち
- 個人Mac側で実装した`migrate_v2_schema.py`・`search.py`/`webapp/app.py`/
  `gpt_integration/query_report.py`/`generate_agency_os_pack.py`の改修は
  すべてDropbox同期フォルダ内のファイルなので、会社Macでも同じ状態がそのまま
  見える(再実装不要)。本番DB(`output/knowledge_index.db`)・既存Agency OS Pack
  はまだ一切変更していない(検証はすべてコピー上で実施済み)
- 未解決の品質論点: (1)SOURCE FACTへの解釈混入20%(未着手)、(2)月表記ズレの
  既知誤検知パターン(対応範囲外のまま)、(3)300件サンプルのモデル混在(8b/27b)
- FULL DB本実行(qwen3.8:27b、Windows機、SSD接続、約80.7時間見込み)は
  中村さんが「クオリティ優先」の方針を示したため、task-009の結果と上記3論点への
  対応方針が固まるまで着手しない

**次に会社Mac側でこのプロジェクトに触れるときは、まずtask-009のStatus/Result欄と
このメモリの最新セクションを確認してから再開すること**。会社Macは独自の
venv(`~/gbc_knowledge_venv_d14461`)を持つので、個人Mac側のvenvパスは
流用不可な点に注意([[feedback_venv_outside_dropbox_sync]]参照)。

## 2026-08-27(会社Mac側で再開): 新しい品質軸「自己PR/CSR定型文」検出 → task-010依頼
中村さんから「わりと当たり前のことが知見として書いてあるものが多い、除外する方法は
ないか」との新規指摘(数値グラウンディングの話とは別軸)。

**試行錯誤の経緯:**
1. LLM不要のヒューリスティック(country/client/industry空欄+evidence_quoteに数字なし)を
   試したが、5,764件(38.7%)がヒットし精度も五分五分(手動サンプルで確認)。
   「紅・抖音・微信が中国のコア広告チャネル」のような固有名詞ベースの有用な知見も
   country/industry空欄というだけで巻き込まれた。
2. LLM分類スクリプト`audit_genericness.py`(GENERIC=一般常識 vs SPECIFIC=固有名詞・
   数値あり)を実装し既存300件層化サンプル(`audit_sample.json`)に適用開始したが、
   **中村さんに20件×2ラウンドで実際に100点満点採点してもらったところ、GENERIC群
   平均80点・SPECIFIC群平均85点とほぼ差が無く、この軸は価値判断と相関しないと判明**。
   232/300件処理した時点でこの監査は停止(データは参考として残置、削除せず)。
3. **採点結果から判明した本当の判断軸**: 「一般常識かどうか」ではなく
   「**誰について語っているか**」— 自社の実績・体制についての自己PR/CSR定型開示文
   (低評価: 「実績を積んできた」30点、「取締役会の実効性評価を外部機関を活用して
   実施」40点、テンプレートファイル由来の中身の無い比喩10点)か、外部の市場・消費者・
   事例についてのリサーチ知見(高評価: 一見抽象的な「都市部の消費者は新しい支払い
   方法を好む」でも90点、実際のペルソナ・生活者リサーチ例も80-90点)か、という軸。
   **教訓**: 「抽象的/具体的」という表面的な文体では価値を判定できず、内容が誰について
   語っているか(自社の自己言及 vs 外部対象のリサーチ)で判断する必要がある。
4. この教訓を反映した`audit_boilerplate.py`(BOILERPLATE vs SUBSTANTIVE)を新規実装。
   qwen3:8bで28件の人間採点済みカードに簡易検証したところ、BOILERPLATE判定群人間平均
   68.0点・SUBSTANTIVE判定群80.8点(差13点、v1の差5点弱から改善)。ただし誤判定も残存
   (「NTT-dentsu×TGS VRで大阪万博スポンサー獲得」という明確な具体事例を構造的な
   言い回しからBOILERPLATEと誤判定、逆に固有名詞があるだけの「Digi-Keyブランド
   キーワード競合入札」を人間は「通常の広告会社の作業」(60点)と評価したがLLMは
   SUBSTANTIVEと誤判定、等)。

**現在の状態**: `task-010`として、300件本実行+28件でのqwen3.8:27b vs qwen3:8b
モデル比較検証をWindowsへ依頼済み([[claude_relay_system]]、Status: waiting)。
会社Mac(d14461)にもモデル統一のためqwen3.8:27bをpull中(ollama、~17GB、
`~/Applications/Ollama.app`経由、[[ollama_company_mac_setup]]参照)。

**次にこのプロジェクトに触るときは、task-010のStatus/Result欄と
`boilerplate_audit_report.md`を確認してから再開すること**。数値グラウンディング側の
未解決論点(SOURCE FACTへの解釈混入20%・月表記ズレ)、この新しい「自己PR/CSR定型文」
軸、両方が片付くまでFULL DB(14,897件)再生成は開始しないこと。

## 2026-08-27(同日続き): task-010完了 → 中村さんが「今のクオリティでPoC進めたい」と判断
→ FULL DB本実行を2本同時開始

task-010完了(Windows): qwen3.8:27bでBOILERPLATE判定群人間平均67.3点・SUBSTANTIVE判定群
81.5点(分離幅14.2点、qwen3:8bの13.0点からわずかな改善)。300件本実行はBOILERPLATE
69件(23.0%)・SUBSTANTIVE 231件(77.0%)。credential_source/success_storyカテゴリで
BOILERPLATE比率最高(26-27%)。推奨は自動除外でなく「レビュー優先度を下げるフラグ」。

`full_db_migration_design.md`に7節「BOILERPLATE軸の統合」を追加:
BOILERPLATE検出はStage A/Bと独立・SSD不要なため即座に全件へ適用可能と判明。
新スキーマ案`v2_content_type`/`v2_content_type_reason`列を追加。除外か優先度低下かは
オープンな論点として整理(中村さんの判断待ちのまま据え置き)。

中村さんが「まずは今のクオリティでPoC進めたいので、Fullをスタートしても良い」と判断
(数値グラウンディング解釈混入20%・月表記ズレ等の未解決論点があっても、これ以上の
精度改善を待たずにPoCとして進める、という意思決定)。これを受けて**FULL DB本実行を
2本同時に開始**:

1. **Stage A/B新パイプライン本実行**(`full_pipeline_v2.py`新規作成、
   `regression_pipeline_v2.py`のstage_a/stage_b/locate_contextを再利用し入力を
   「300件サンプル」→「doc_cards全件のうち300件サンプルを除く14,597件」に変更):
   task-011としてWindowsへ依頼(Status: waiting)。qwen3.8:27b、SSD接続、
   実測19.5秒/件ペースで約79時間見込み。過去に複数プロセス同時実行事故が
   繰り返されたため、開始前のプロセス確認・Teams定期進捗報告(1,000件毎/6時間毎の
   早い方)を明記。**本番DBへのマイグレーション適用はこのタスクの範囲外**(完了後に
   別途判断)
2. **BOILERPLATE軸の全件分類**(`full_boilerplate_audit.py`新規作成、
   `audit_boilerplate.py`のロジックを流用し300件サンプル除く14,597件に適用):
   会社Mac(d14461)側で直接実行(PID記録済み)。**qwen3.8:27bはこのMacのApple Silicon
   統合メモリでは1件120秒超と非現実的に遅く、task-010実測の精度差(27b分離幅14.2点 vs
   8b分離幅13.0点)がわずかなため、qwen3:8bで実行する判断**(実測約10秒/件、
   14,597件で約40時間見込み)。500件刻み+30分無進捗でのスタール検知付きMonitorで
   監視中。出力は`output_v2/full_boilerplate_audit_results.jsonl`(v1の
   `genericness_audit_results.jsonl`・300件本実行結果`boilerplate_audit_results.jsonl`
   とは別ファイル)

両実行とも既存本番DB(`output/knowledge_index.db`)・既存Agency OS Packには一切触れず、
出力は新規ファイルのみ。完了後、(1)`migrate_v2_schema.py --allow-production`の
適用要否、(2)BOILERPLATE軸の扱い方(除外/優先度低下、7-4節のオープンな論点)を
中村さんと相談してから本番DBへ反映する。

**次にこのプロジェクトに触るときは、task-011のStatus/Result欄と、会社Mac側
`full_boilerplate_audit.py`のプロセス状況(`ps -p <PID>`または
`output_v2/full_boilerplate_audit_results.jsonl`の行数)の両方を確認してから
再開すること**。どちらも数日規模の処理のため、完了していない場合は進捗状況を
報告した上で待つこと。

## 2026-08-27(同日続き): 中村さん指示で「FULLはWindows側に統一」→ BOILERPLATE軸もtask-012としてWindowsへ
中村さんから「FULLはWindows側で実行するので、このMacでの実行は止めて下さい」との指示。
会社Mac側の`full_boilerplate_audit.py`(PID 10069、37件処理済み)を停止し、監視Monitorも
停止した。37件の出力(`output_v2/full_boilerplate_audit_results.jsonl`)はシードデータ
として残置(削除せず)。

BOILERPLATE軸のFULL監査をtask-012としてWindowsへ依頼(windows_inbox.md、Status: waiting)。
中村さんの指示で**task-011(Stage A/B FULL)と同時並行実行**とする。同一GPU(RTX3090)を
2プロセスで共有するリスクがあるため、task-012側はモデルをqwen3:8b(軽量、精度差は
わずか)に指定し、task-011への悪影響(OOM・速度低下)があればtask-012を一時停止して
task-011を優先するよう明記した。

**現在の状態(2026-09-03、windows_inbox.mdで確認し訂正)**: task-011・task-012は
その後実際に開始されたが、**両方とも中村さんの指示で停止・保留中**。task-012は
task-011と並行実行した結果、11.5時間後にtask-011の処理速度が単独実行時の約2倍
(19.5秒/件→39.3秒/件)に低下していることが判明し、事前合意どおりtask-012を一時停止
(1,921/14,597件処理済み、resumableなのでデータは保持)。**その後task-011自体も
「時間がかかりすぎる」との中村さんの判断で停止され、「PoCが終わって改めてFULLで
回すことを考える」という位置づけに変わった**(task-011のResult欄より)。task-012も
同じ位置づけで保留。既存DB・既存Agency OS Packはどちらの作業でも一切変更されて
いない。

**次にこのプロジェクトに触るときは、windows_inbox.mdのtask-011・task-012の最新
Status/Resultを確認すること**。「PoCが終わったらFULL実行を再検討」という中村さんの
方針が生きているため、FULL DB再生成(約80時間、Windows GPU必須)を勝手に再開しない。

## 2026-09-03: 「Agency OS」ChatGPT Skillのテストフィードバック対応(データではなく振る舞いの問題と判明)
中村さんから「Agent OSのフィードバックがあった」と依頼があり、共有されたChatGPTの
テスト会話PDF(`GBC-Knowledge`と同じフォルダ内`Agency OS活用事例_やりとり試験.pdf`、
AGH「贅沢搾り」グローバル展開ケーパ紹介セッションのデモ)を読んで確認した。
**注意: 依頼時は別の自作システム(`~/AIAgency`、Claude Code nativeの`/agency`
subagent群)を誤って対象と誤認し、先にそちらを修正してしまった($HOME直下の
`~/.claude/projects/-Users-d14461/memory/ai_agency_team_build.md`参照、これはこれで
無駄ではないが今回のフィードバックの対象ではなかった)。実際のフィードバック対象は
このプロジェクトが作った`generate_agency_os_pack.py`のKnowledge Packを読む、
ChatGPT Custom GPT「gbc-ai-agency」(会話内での自称は「Agency OS」)だった。**

### フィードバック4点への調査結果
1. 「関連事例をURLで表示してほしい」→ **データ側は問題なし**。`knowledge_index.db`を
   直接クエリしたところ、doc_cards(14,897件)・case_records(14,939件)・
   staff_profiles(39件)いずれも**URL充足率100%**。テスト会話では事例引用
   (例:「CASE_ID 14040」)にURLが本文に印字されず、ChatGPTの「情報源」引用チップ
   のみになっていた(チップはコピー&ペースト/PPTX化で失われる)ことが原因。
2. 「案件チェックリストを必ず出す」→ `pm/pm_checklists.md`に「Global Pitch」向け
   7項目チェックリスト(根拠URL付き)が既に存在するが、テスト会話では5R(1項目)
   のみをAgency OS自身の内部判断に使い、残り6項目をユーザー向けチェックリストとして
   提示していなかった。
3. 「自己分析用ツールの提案」→ `tools/tools.md`にツール×フェーズ対応表
   (Advertising Age等、既にPhase(s)列でKick-off/リサーチ/提案/実行/振り返りに
   マッピング済み)が存在するが、テスト会話では一度も参照されていなかった。
4. 「ツール以外の一般情報・国別データ」→ `knowledge/*.md`に「各国広告事情」タグの
   知見が既に存在(インドネシア広告費データ等、URL付き)。

**結論**: 4件とも「データが足りない」のではなく、**Agency OSのInstructionsが
Pack内の既存データ(URL/チェックリスト/ツール)を毎回使い切るよう指示されていない**
という振る舞い側の問題。

### 対応
`GBC-Knowledge/agency_os_skill_instructions_addendum_20260903.md`を新規作成。
ChatGPTのGPT Builder(Configure→Instructions)に貼り付ける追加ルール5点
(URL明記必須/チェックリスト必須/ツール提案必須/国別データ案内必須/Expert欄の
扱い再徹底)と、Skillの標準アップデート手順(データ側=Pack再生成→ChatGPT側で
旧ファイル削除→再アップロード、Instructions側=Configure画面で直接編集)を記載した。

**判明した構造的ギャップ**: 姉妹GPT「知見活用GPT」は`gpt_integration/
GPT_Instructions_知見活用GPT.md`としてInstructions全文をローカル保存する習慣が
あるが、Agency OS側は同様のファイルが無く、Instructions全文はChatGPT側にしか
存在しない(ローカルに現状のコピーが無いため、今回は「追記用アドオン」としてのみ
作成し、全文の書き換え・整合性チェックはできていない)。

**Why**: ユーザーが実際にAgency OSを試したことで「事例のURLが見えない」
「チェックリストが出ない」等の具体的な使用感フィードバックを得られた。原因を
データ欠損と決めつけず、DBを実際にクエリして確認したことで「データはあるのに
使われていない」という正確な診断ができた。
**How to apply**: 次にAgency OS関連の依頼が来たら、まず`agency_os_skill_
instructions_addendum_20260903.md`が実際にChatGPT側のInstructionsへ反映
されたか、反映後の再テストでURL/チェックリスト/ツール提案が出るようになったかを
中村さんに確認すること。また、可能なら中村さんから現行Instructions全文を
もらい、`GBC-Knowledge/agency_os_instructions_current.md`のような形でこの
プロジェクトにも保存する運用に切り替えることを提案する(知見活用GPT側と
同じ習慣に揃える)。

## 2026-09-03(同日続き): 訂正— これはCustom GPTではなくChatGPT Skill、実体は既にローカル保存済み
上記対応の直後、中村さんから2点の訂正・追加情報があった: (1)「これはGPTではなく
Skillで作っている」、(2)Skill関連ファイルは既に`GBC-Knowledge`と同じ階層の
`GPT作業/`フォルダにローカル保存済み(`SKILL.md`=最新版2026-08-26 16:24時点344行、
`SKILL_V1.md`/`SKILL_V2.md`=旧版、`skill.zip`=初回登録用パッケージ)。さらに、
「Claude Code構築方法.pdf」という別のChatGPT会話PDFがあり、Agency OS Skillの
構築・改修の全経緯(2026-08-25〜26)が記録されていた。これを読み、直前の対応
(`agency_os_skill_instructions_addendum_20260903.md`)の「GPT BuilderのInstructions
欄に貼る」という反映方法が誤りだったため訂正した(正しくはChatGPTのSkillエディタで
`SKILL.md`本体を直接編集)。

### Claude Code構築方法.pdfから判明した全体像
- ユーザーは元々「4人のAI組織(指示役+企画者2+経営者)」というClaude Code
  subagent構想の相談から始め、広告会社型9エージェント構想(≒`~/AIAgency`と同系統の
  発想)を経て、最終的に**ChatGPT Skill「agency-os」**として実装した(Claude Codeの
  subagent機能ではなく、ChatGPT側のSkill機能で作られている点が重要な相違点)。
- Agency OS Skillは案件ごとに動的にResearcher/Planner/Creative/Media/PR/Event等の
  仮想チームを編成し、Research→Strategy→Creative Divergence(3ラウンド)→Red Team→
  Execution→PPTXまで一気通貫で行う設計(`~/AIAgency`と設計思想は酷似しているが、
  実体はまったく別のChatGPT Skillコードベース)。
- 当初`knowledge_index.db`(33MB SQLite)をSkillに直接組み込もうとしたが、
  **Skillの実行環境はCustom GPTのCode Interpreterと異なりSQLite+Pythonをその場で
  実行できない**ことが判明(重要な技術的制約)。解決策として、`generate_agency_os_pack.py`
  (このプロジェクトの既存スクリプト)でDBをMarkdown化した「GBC Common Knowledge
  Pack」(cases_*.md/knowledge_*.md/tools.md/pm_checklists.md/case_expert_index.md/
  faq.md/task_briefing_format.md、計17ファイル、POCモード)を生成し、Skillの
  `references/gbc-pack/`にアップロードする方式に変更した。
- **重大な発見**: SkillはデフォルトではChatGPT利用者個人がアクセスできる社内
  SharePoint/GBCarekoko/Salesforce Live Searchを優先的に検索してしまい、
  局員ごとに検索結果が変わってしまう(PoCとして使えない)。これを解決するため
  `SKILL.md`に「COMMON KNOWLEDGE TEST MODE」を追加し、Skill内蔵の
  `references/gbc-pack/`だけを情報源として強制するモードを実装・検証済み(PASS)。
  通常モードでは「Common Pack最優先→個人アクセス可能な社内Knowledge→Web」の
  優先順位を明記している。
- Knowledge Card自体の品質問題(untagged 77.9%、Why/When/Actionフィールドの
  8〜9割に原資料にない一般化・因果断定の混入)も同じ会話内で発見され、
  `knowledge_quality_audit.md`(300件監査)→Stage A/B分離パイプライン→300件
  Regression Testという、上記2026-08-26〜27のメモリ記録と完全に同じ流れに合流する
  (この部分は既存メモリと重複するため詳細は上記参照)。

### 「これは私がアクセスできるファイルからの情報」という中村さんの鋭い指摘
COMMON KNOWLEDGE TEST MODE導入前のテストで、中村さんが「これは私個人がアクセス
できるSharePoint情報であり、局員全員がアクセスできる場所の情報ではない。Salesforce
全件リストも別の作業でたまたま自分がエクスポートしたものが引っかかっているだけ」
と指摘し、これが上記のCOMMON KNOWLEDGE TEST MODE実装のきっかけになった。
**教訓**: 複数人で使う共有AIツールを検証する際は、必ず「自分が特別にアクセスできる
情報が紛れ込んでいないか」を疑うこと。この教訓は[[feedback_verify_against_ground_truth]]
とも通じる。

**How to apply**: 次にAgency OS Skillに触る際は、`GPT作業/SKILL.md`(ローカル控え)を
まず読んで現状を確認すること(ChatGPT側が正だが、ローカル控えとの差分が無いか
都度確認する運用にする)。データ更新(Knowledge Pack再生成)は`generate_agency_os_pack.py`
の実行のみで軽量・非LLM処理なので個人Mac/会社Macどちらでも良い。一方、
`knowledge_index.db`自体の中身を良くするStage A/B FULL再生成(約80時間規模)は
Windows RTX3090必須の重い処理で、現在中村さんの判断で保留中(上記2026-08-27の
記録参照)。両者を混同しないこと。

## 2026-09-03(同日続き): 海外駐在員リスト(現在・過去)をAgency OS Knowledge Packに追加
中村さんの要望で、案件の対象国について「過去にその国へ駐在していた人」「現在駐在している
人」をAgency OSの出力に必ず表示するようにした。データソースはOneDrive「Global Q - 駐在員
リスト」フォルダの`overseas_staff_assignment_history_*.xlsx`(既存の別自動化が月次スナップ
ショットから集計・維持している履歴ファイル、Claude Codeはこれを読み取るだけで書き込まない)。
2026-09-03時点のスナップショット: 342行・20か国・283名(氏名ベース)・66回分の月次名簿
(2019-09〜2026-09)から集計。中国(現在19名/過去111件)・アメリカ・イギリス・タイ・
インド等が多い。

`GBC-Knowledge/generate_overseas_staff_pack.py`(新規)で、最新の`overseas_staff_
assignment_history_*.xlsx`をファイル名の日付から自動検出し、`output/agency_os_pack/
experts/overseas_staff_index.md`へ国別(現在駐在中/過去の駐在経験者に分割)で出力する。
xlsxの「データソースについて」シートに書かれた前提・限界(確認期間はスナップショット
ベースで実際の赴任/帰任日と数日〜1か月ずれる可能性、表記ゆれの正規化、等)もそのまま
Markdownへ転記している。**踏んだ罠**: 元シートの注記は「・」で始まる箇条書きだが、
折り返し部分は次のセル(「・」なし)に入っているため、素朴に「・」始まりの行だけ拾うと
継続文が欠落する。行を`・`の有無で判定し、`・`なしの行は直前の箇条書きに連結する処理が
必要だった。

`GPT作業/SKILL.md`にこのファイルを組み込み: GBC Knowledge Pack構成一覧・COMMON
KNOWLEDGE TEST MODEの検索バケット・「How to use each internal source」への追記、
および新規ルールF(該当国の現在・過去駐在員を必ず表示、Expertと呼ばない、Current
Overseas Assignee/Past Case Contactとして扱う)を追加(344行→415行)。`agency_os_pack/
README.md`にもファイル一覧と生成コマンドを追記。

**Why**: 案件のある国に土地勘のある局員(過去駐在者)や、現地から生の情報を得られる
局員(現駐在員)を毎回自分で探すのは手間がかかるため、Agency OSの標準出力に組み込む
ことで「誰に聞けばいいか」を自動的に提示できるようにしたい、という要望。
**How to apply**: このファイルは`knowledge_index.db`とは別系統のデータソース(月次
Excelスナップショット)なので、`generate_agency_os_pack.py`の月次実行だけでは更新
されない。`generate_overseas_staff_pack.py`も同じタイミングで実行することを、
月次更新のルーチンに含めること。次に触るときは、まずChatGPT側のSkillに
`overseas_staff_index.md`と更新後の`SKILL.md`が実際にアップロードされたか、
PoCテストブリーフ(Nusantara Roast、インドネシア設定)で駐在員情報が正しく出力される
かを確認すること。

**2026-09-03、運用方針を中村さんに確認して決定**:
1. **Knowledge Pack(Markdown、Skill用)の再生成は月次で定例化する**。
   `generate_agency_os_pack.py`実行→Skillエディタでファイル差し替え→保存、を毎月1回の
   ルーチン作業とする(軽量処理なのでどちらのMacでも可)。トリガー方法(月初に中村さんが
   依頼/Claude Code側から自動提案 等)はまだ未確定 — 次にこの作業をする際、まだ仕組み化
   されていなければ具体的な運用(例えばこのメモリのwork_status確認時に「前回いつ実行
   したか」を毎回チェックする等)を相談すること。
2. **`knowledge_index.db`自体のStage A/B FULL品質改善再生成の再開可否は、今回は
   まだ判断しない**(2026-09-03時点、保留継続)。次にこの話題に触れる際は、
   改めて中村さんの判断を仰ぐこと(単独実行に戻す/スコープを絞る等の選択肢は
   `agency_os_skill_instructions_addendum_20260903.md`および本メモリに提示済み)。

## 2026-09-03(同日続き): Skill実体のファイルツリーを中村さんがスクリーンショットで共有(重要・確定情報)
`SKILL.md`が`references/gbc-pack/*.md`というパスを前提に書かれていたが、実際の
ChatGPT Skillエディタの構造は異なっていた(**過去に中村さんがChatGPTから「GBCパックは
ルート直下に置くように」と指示されていたため**)。スクリーンショットで確認した実際の
構造は以下の通り(以後このプロジェクトでSKILL.mdを編集する際は必ずこの構造に従うこと):

```
(Skillルート)
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── icon.svg
├── references/                          ← Agency OS自身の「動作定義」ドキュメントのみ
│   ├── agency-role-library.md
│   ├── creative-protocol.md
│   ├── deck-production.md
│   ├── knowledge-integration.md
│   ├── modes-and-routing.md
│   ├── quality-standards.md
│   ├── research-protocol.md
│   └── strategy-frameworks.md
│   (2026-09-03時点、overseas_staff_index.mdも一時的にここに入っていた
│    — ルート直下へ移動予定/移動済みか要確認、下記参照)
├── case_expert_index.md                  ← GBCデータパックはルート直下にフラット配置
├── cases_americas_01.md
├── cases_apac_01.md
├── cases_emea_01.md
├── cases_global_01.md
├── cases_japan_01.md
├── cases_other_01.md
├── faq.md
├── knowledge_consumer_trend_01.md
├── knowledge_country_ad_landscape_01.md
├── knowledge_csr_csv_01.md
├── knowledge_industry_info_01.md
├── knowledge_media_planning_01.md
├── knowledge_misc_minor_tags_01.md
├── knowledge_untagged_01.md
├── pm_checklists.md
├── task_briefing_format_template.md      ← 未使用の重複ファイルの可能性(下記参照)
├── task_briefing_format.md               ← SKILL.mdが実際に参照しているのはこちら
└── tools.md
```

**重要な区別**: `references/`フォルダは**GBCデータパックの置き場ではない**。
Agency OS自身の思考プロセス定義(役割ライブラリ、リサーチ手順、品質基準等)専用。
GBCの実データ(事例・知見・ツール・チェックリスト・駐在員情報等)は全てSkillの
ルート直下にフラットなファイル名で置かれている。この誤認に基づいて一度
`references/gbc-pack/`という誤ったパスでSKILL.mdを書いてしまったため、全て
`references/`プレフィックス無しのファイル名表記に修正済み(2026-09-03)。

**2026-09-03、上記2点とも中村さんが確定**:
1. `overseas_staff_index.md`は**ルート直下に移動済み**。SKILL.mdは既に全箇所
   プレフィックス無し(`overseas_staff_index.md`)表記になっており、追加修正は不要
   だった(確認のみで完了)。
2. `task_briefing_format_template.md`は**削除せず残す**(SKILL.mdからは引き続き
   参照しない、未使用のまま置いておく方針)。今後もこのファイルには触らないこと。

## 2026-09-04: overseas_staff_index.mdのローカル再生成を週次パイプラインへ組み込み(ChatGPT Skill本体への反映は引き続き手動)
2026-09-03に`generate_overseas_staff_pack.py`で一度生成・アップロードした`overseas_staff_index.md`が、
その後[[overseas_staff_list_sync_automation]]側の週次更新(sync→駐在履歴再生成→タイムラインワークブック
再生成)には組み込まれておらず、ソースの`overseas_staff_assignment_history_*.xlsx`が更新されても
このファイルだけ再生成されないまま放置される構造になっていたと中村さんの指摘で判明。

**対応**: `~/OverseasStaffList/update_agency_os_pack.py`を新規作成し、
`~/OverseasStaffList/weekly_update.py`の4番目のステップとして追加(sync→駐在履歴再生成→
タイムラインワークブック再生成→**Agency OS Pack再生成**、の順)。中身は`generate_overseas_staff_pack.py`
をsubprocessで呼び出し`output/agency_os_pack/experts/overseas_staff_index.md`を上書きするだけ
(このプロジェクト側のコードは無改修)。生成後の内容をSHA-256で前回と比較し、**変化があった週だけ**
Teams通知(「Agency OS 駐在員データ 更新あり」)で中村さんに手動差し替えを促す設計にした
(毎週の空振り通知を避けるため)。動作確認済み(2026-09-04、342行・20か国、正常に再生成)。

**依然として自動化できない部分(プラットフォーム制約、変更なし)**: ローカルで再生成した
`overseas_staff_index.md`をChatGPT Skillエディタの実ファイルへ反映する作業自体は、
Claude Code/スクリプトからは引き続き自動化不可。Teams通知を受けた中村さんが手動で
Skillエディタ上のファイルを差し替える必要がある。この手動ステップが残っている点は
`generate_agency_os_pack.py`側(GBC Common Knowledge Pack本体)の月次更新運用と同じ制約。
**次にこのプロジェクトに触るとき、Agency OS周りの更新について聞かれたら、
「ローカルのMarkdown再生成は自動化済み(週次)」「ChatGPT Skillへの実アップロードは
Teams通知を見て中村さんが手動で行う」の2段階に分かれている点を明確に説明すること**。

**2026-09-04追記**: 中村さんから「通知内容にやり方も含めて」との依頼があり、Teams通知本文に
`agency_os_skill_instructions_addendum_20260903.md`の「A. データを更新する場合」の手順
(Skillエディタを開く→ルート直下の既存overseas_staff_index.mdを削除→新ファイルをアップロード→
保存(ボタンが無効なら1文字変更で有効化)→COMMON KNOWLEDGE TEST MODEで確認)をそのまま
番号付きで埋め込んだ(`~/OverseasStaffList/update_agency_os_pack.py`のsend_teams呼び出しを更新)。
今後、この手順自体(Skillエディタの操作方法)が変わった場合は、addendumファイルとこの
Teams通知文言の両方を更新する必要がある点に注意。

**2026-09-04追記(同日続き)**: 中村さんからSkillエディタの直接URLの提供があり、通知本文に追記。
**Agency OS(agency-os)Skillエディタ直リンク: `https://chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080`**
(`update_agency_os_pack.py`の`SKILL_EDITOR_URL`定数)。次に何らかの理由でこのURLが変わった場合は
この定数を更新すること。

## 2026-09-08: 局内管理職向けPoC募集PPTX資料を新規作成
中村さんの依頼で、Agency OSを各部の現場部員にPoCとして試用・フィードバックしてもらうための
社内配布資料(概要/仕組み/使い方/PoCで試してほしいこと、各1枚+表紙+Closing)をdentsu GTM
テンプレートで作成。保存先: `20260814GBC知見集約プロジェクト/Agency_OS_PoC募集資料_20260908.pptx`
(SKILL.md・`GPT作業/`と同じプロジェクトルート直下)。

**実データの扱いで判断したこと**: 「実際の画面・使い方」スライド用の実例として、`Agency OS活用事例_
やりとり試験.pdf`(AGH「贅沢搾り」ケースの実演デモ)の全文はpymupdfでテキスト抽出して仕組み・処理
フローの理解には使ったが、スライド上の具体例としては**実クライアント名(AGH等)を出さず**、既存の
架空PoCテストブリーフ(`PoCテスト用_架空ブリーフ_NusantaraRoast_Indonesia_20260903.md`)の方を
実例として引用した。理由: AGHデモは特定の新規開拓検討中案件に基づく実演で機密性が高く、局内配布用
の一般資料に出す実例としては架空ブリーフの方が安全([[feedback_gbc_ai_material_authoring_rules]]
の「機密プロジェクト名は言及しない」原則の延長で判断)。次にAgency OS関連の配布資料を作る際も、
実例はAGHケースではなくNusantara Roast(またはMalaysia等の既存架空テストケース)を使うこと。

**実際の画面キャプチャは無い**: ChatGPT Skillの実行画面のスクリーンショットは今回入手していない
(`Agency OS活用事例_やりとり試験.pdf`はテキストベースの会話コピーで、UI画像ではなかった)。
「使い方」スライドはSKILL.mdの処理ステップ(案件診断→GBC知見検索→チーム編成→リサーチ/戦略/
クリエイティブ発散→Red Team批評→PPTX化)をテキストベースのSTEP図解で表現する形で代替した。
本物の画面キャプチャが要る場合は中村さんに新規スクリーンショットの提供を依頼する必要がある。

## 2026-09-08(同日続き): PPTX出力が電通フォーマットにならない問題を修正(PoC前の重要修正)
上記のPoC募集資料作成の直後、中村さんから「Agency OS Skillのpptx出力が電通フォーマットで
出てこない、PoC前に直したい」と相談。原因は`references/deck-production.md`のテンプレート追従
ルールが「ユーザーがテンプレートを供給したら従う」という**条件付き**の書き方で、電通GTMテンプレート
自体がSkillに同梱されていなかったこと(SKILL.md/deck-production.mdはローカルに`GPT作業/`として
控えがあったため、Claude Code側で直接原因を特定・修正できた)。

**対応**: `GPT作業/`に3点を用意しローカル保存:
1. `dentsu_gtm_template_clean.pptx`(新規) — 電通GTMテンプレート(28MB)からサンプルスライド75枚を
   python-pptxで削除し、レイアウト70種のみの空テンプレートに軽量化(9.4MB)。重さの大半はサンプル
   スライドの画像で、レイアウト自体が使う背景アセット(9MB)は削除不可のため残置。
2. `deck-production.md`(全面改訂) — 「常に同梱の`dentsu_gtm_template_clean.pptx`を使う」という
   必須ルールに変更。[[dentsu_pptx_template]]のレイアウトカタログ・色パレット(`accent1` #FE5021等)・
   Verdanaフォント・python-pptx実装時の既知の罠(プレースホルダー`text_frame.clear()`忘れ、
   Statement系レイアウトの`spc`文字間隔バグ、xfrm4軸同時設定、Contents-01の自動採番等)をこの
   プロジェクト向けに転記。
3. `SKILL.md`10章 — 同様に「常時使用」の文言へ直接修正。

**中村さんの手動作業**: Skillエディタ(`https://chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080`)
で上記3ファイルをアップロード・差し替え・保存。動作確認の結果「上手くいきました」と報告あり、
電通フォーマットでのPPTX出力に成功したことを確認済み(2026-09-08)。

**教訓**: ChatGPT SkillのInstructions(SKILL.md/references/)に「ユーザーが◯◯を提供したら従う」
という条件付きルールを書くと、Skill自身がその◯◯を常に持っているべきケースでも見落とされやすい。
Skillが自己完結すべき参照素材(今回のテンプレートのような)は、ルール文言を「常に同梱の<ファイル名>
を使う」という無条件の形にした上で、そのファイル自体をSkillに同梱すること。
**次にAgency OS Skillの出力品質に関する相談が来たら、まずローカル控えの`GPT作業/SKILL.md`・
`references/deck-production.md`が実際にChatGPT側の最新版と一致しているか(差分がないか)を
確認してから調査すること**(この修正でSKILL.mdは415行→約417行に変化、ローカル控えは最新のはず
だが、今後ChatGPT側で直接編集された場合はズレる可能性がある)。

## 2026-09-09: Claude Code側「AI Agency Team」(`~/AIAgency`)をChatGPT用に移植 + GM別仮ブリーフ(Word)作成
このプロジェクト(ChatGPT Custom GPT「Agency OS」)とは別に、Claude Codeネイティブsubagentで
構築した「AI Agency Team」([[ai_agency_team_build]]、`~/AIAgency`、Agency Producer+8サブエージェント)
をChatGPTでも使えるよう1本のMarkdownに統合し、`~/AIAgency/chatgpt/agency_os_for_chatgpt.md`
(約34,000字)として作成した。Agent tool(別プロセスsubagent)が無いため「ChatGPT自身が1人格の中で
8人を順番に演じ分け、`### 🔍 RESEARCHER`等の見出しで会話内にセクション出力する」方式に置換し、
`workspace/*.md`へのファイル読み書きは「会話内の該当セクションを読み返す」に、ローカル参照ファイル
(`reference/tools_and_sources.md`)は内容をそのまま巻末付録に埋め込んだ。Custom GPTのInstructions欄
(8,000字上限)には収まらないため、通常チャットへの貼り付け/添付ファイル利用を前提にした。

続けて、本日開催のGBC Agency OS PoC説明会(2026-09-08の[[work_status/agency_os_poc_recruitment_deck_20260908]]
募集資料に続く回、AP2部小川様/AP3部金井様/BD部新保様/SP1部山本様/SP2部土門様/SK部山田様の6GM対象)向けに、
各GMの実案件に紐づく仮想クライアントブリーフ(Word、python-docx)を6本作成した。詳細経緯・[[feedback_brief_means_client_brief]]
の訂正(「ブリーフ」=内部説明資料ではなくクライアント視点の入力ドキュメントだった)・保存先は
[[work_status/agency_os_poc_gm_briefs_20260909]]を参照。保存先フォルダは本プロジェクトと同じ
`Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/20260909PoC説明/`。

**AP1部 GM = 項琳**(2026-09-11、中村さん本人に確認済み)。項琳はこのAgency OS PoCプロジェクト自体の共同発表者(表紙に「項琳・中村(正)」と並記、スライド5のフィードバック窓口も「項琳GM・中村」)だが、AP1部向けの個別説明会は今回のPoC説明会(9/9、AP2/AP3/BD/SP1/SP2/SK対象)とは別に改めて実施予定。7本目の仮ブリーフ(AP1部向け、`仮ブリーフ_SEIKO中国市場勝ち筋策定_AP1部項様_20260911.docx`)はSalesforceで項琳が責任者になっている実案件「SEIKO中国攻略」(セイコーウオッチ、中国市場勝ち筋提案)を基に作成。詳細は[[work_status/agency_os_poc_gm_briefs_20260909]]参照。

**新スライド追加(2026-09-11)**: 5枚目「試し方」の直後に「フィードバックの送り方（Chatの共有）」を追加(全7枚に)。ChatGPT Enterprise(dentsuワークスペース)の実機確認で判明した仕様: 会話右上「共有する」ボタンはワンクリックでリンクをクリップボードにコピー(確認ダイアログ無し、トーストで「リンクはワークスペースメンバーにのみ表示されます」と表示)。共有リンクを開くと「これは共有されたChatGPTのチャットのコピーです」というバナー付きで表示されるが、**ChatGPTの共有ビューにはコメント機能が無い**(テキスト選択しても「ChatGPTに質問する」「書き始める」のみ)。したがってスライド5の「コメントを添えて」は、共有リンクをTeams等に貼る際に人力で一言添える運用を指す(ChatGPT側の機能ではない)。詳細は[[work_status/agency_os_poc_recruitment_deck_20260908]]参照。

## 2026-09-11: テナント違い問題の発覚 → GBC Business「3拠点目」展開の準備
PoC参加者(AP1部石井美香さん、AP3部須田さん、AP1部五十嵐さん、AP1部徳田さん、BD部石井憲吾さん、
BD部吉田寿哉さん)がAgency OS(ChatGPT Enterprise Custom GPT)を開けないエラーを報告。原因は
ワークスペース違い: 上記6名は電通本体Enterpriseの枠が埋まっていたため、GBCが単独契約している
別テナントのChatGPT Businessアカウントを個別付与されていた(Teams記録に、庄司直弘さんの
AP1部会アンバサダー報告として「帰任した米里さん・徳田さんはEnterprise枠が埋まっておりGBC個別
アカウントで対応」との記載あり=既知の運用)。ChatGPT Enterprise側の共有リンクは
「ワークスペースメンバーにのみ表示」される仕様(2026-09-11に実機確認済み、上記スライド追記の
根拠と同じ)のため、Custom GPTもワークスペースをまたいで共有できない。

中村さんが自分のメールで両ワークスペース(電通Enterprise＋GBC Business)にまたがってアカウントを
持てないか、GBC Business側の管理者に付与を依頼中(2026-09-11時点、結果待ち)。付与された場合、
GBC Business側にAgency OSの複製(=3拠点目)を作る運用になる見込み。

**現状2拠点の実体を確認**: ①Claude Code側=`GPT作業/SKILL.md`(現行2026-09-08版)を直接参照する
運用、②ChatGPT Enterprise側=Custom GPT「Agency OS」、Knowledgeに`SKILL.md`+`deck-production.md`+
`dentsu_gtm_template_clean.pptx`+`GBC-Knowledge/output/agency_os_pack/`配下のGBC Knowledge Pack
(cases/knowledge/faq/pm/tools/experts/briefing、Markdown)をアップロードしている。

**発見した不整合**: `GPT作業/skill.zip`(2026-08-26作成)が旧版のまま放置されている
(中のSKILL.mdは8,929バイトで現行26,707バイトと大幅に乖離、`scripts/query_report.py`+
`knowledge_index.db.gz`というMarkdown Pack以前の旧設計(SQLite直読み方式)の残骸を含む)。
3拠点目を作る前に、まずこのzipを現行ファイル一式から作り直すべき、と特定。

3拠点目構築の具体手順(GPT Builder新規作成→Instructions/Knowledgeの内容→Code Interpreter要否→
共有設定→COMMON KNOWLEDGE TEST MODEでの動作確認)は`GPT作業/GBC_Business展開_準備メモ.md`に
詳細を記録済み。**次にこの件に触るとき**は、(1)GBC Businessアカウント付与の結果、
(2)ChatGPT Enterprise側GPT Builderの実際のInstructions/Knowledge設定(この準備メモは推測を
含むため実物と突き合わせて修正要)、を中村さんに確認してから進めること。

なお、これとは別に`~/AIAgency`(Claude Codeネイティブsubagent版、[[ai_agency_team_build]])を
ChatGPT用に1本のMarkdownへ移植した`agency_os_for_chatgpt.md`という並行実装(2026-09-09作成)も
存在するが、今回のPoC(項琳GM他6GM対象)で使われているのはこのプロジェクトのSKILL.md版
「Agency OS」であり、混同しないこと。

## 2026-09-11: 4拠点目「Dify」版を構築(社内Dify、`console.dj-dify.dentsu.jp`)
テナント問題の副産物として、PoC対象者の一部(五十嵐さん・吉田寿哉さんはシニアのためChatGPT
ライセンス自体が無くCopilotのみ)にはChatGPT/Copilotどちらのルートでも解決しないことが判明。
社内で全社員が使える単一Difyインスタンス(モデルはVertex AI経由でClaude Sonnet 5等、Amazon
Bedrock、Azure OpenAI等が選択可、中村さんはアプリ作成権限あり)が使えると分かり、ライセンス
階層を丸ごと迂回できる解として即日構築した。GBC Business複製プランとは並行して両方持つ方針
(ユーザー明示)。

**アクセス方法**: `console.dj-dify.dentsu.jp`はMicrosoft Entra(Teams等)SSOとは別のdentsu Japan
Okta(`djn-client.dentsu.jp`)ログインが必要で、共有ボットブラウザ(port 9226)のTeamsセッションは
引き継げない。中村さんに一度だけ対話的ログインしてもらえば、以降はそのセッションを共有ブラウザ
経由で自動操作できる。

**構築したもの**: アプリ「GBC Agency OS」(id: `047d1529-f9fb-4211-a5a9-dc45aaee90a1`)、
チャットフロー(ワークフローではなくチャットフロー選択——SKILL.mdの「固定ロースターを強制しない」
設計思想とWorkflowの固定ノード配線は相性が悪いと判断したため)。構成: スタート→知識検索
(ナレッジ「GBC Knowledge Pack」相当、自動生成名`knowledge_consumer...`のまま未リネーム)→LLM
(SYSTEM prompt=SKILL.md本文をそのまま貼付、25.8KB)→回答。知識検索の出力はLLMの「コンテキスト」
欄に紐付け、SYSTEM prompt末尾に`{{#context#}}`変数チップを明示的に挿入(Dify側の仕様で「コンテキスト
利用時はプロンプトに変数を明記」が必須)。

**ナレッジベース**: `GBC-Knowledge/output/agency_os_pack/`配下の19ファイル(cases×6、
knowledge×7、faq/pm_checklists/tools/task_briefing_format×各1、case_expert_index/
overseas_staff_index×2)を5件ずつ4バッチでアップロード(Dify上限)。検索方式はハイブリッド検索
+Rerank(cohere.rerank-v3-5:0)、Top K=6に変更(既定3から拡大、複数バケット横断検索を想定)。
チャンク設定は操作ミスでカスタム/4000文字になった(意図した1024文字ではない)が、動作確認は
問題なく、実害小さいためそのまま許容。

**重大な発見: Claude Sonnet 5(Vertex AI経由)はこのDifyインスタンスで動作不可**。
`temperature`パラメータを送るとモデル側が400エラー(`temperature is deprecated for this model`)、
Temperature/TopP/TopKを全て無効化して再試行すると今度はDify側のClaude用プラグイン
(`/app/models/llm/llm.py`の`_handle_claude_stream_response`)がストリーミング中の`ThinkingDelta`
チャンク(Sonnet 5の拡張思考モード由来)を処理できず`AttributeError: 'ThinkingDelta' object has no
attribute 'text'`でクラッシュする。LLMノードの「推論タグの分離を有効にする」トグルをONにしても
解消せず——**これはアプリ側の設定では回避不可能な、Dify側Vertex AI Claudeプラグインの既知バグ
(Sonnet 5の拡張思考ストリーム未対応)**と判断。**Claude Sonnet 4.6に切り替えたところ正常動作を
確認**(同一の知識検索コンテキスト・同一SYSTEM promptで、CASE_ID付きの正確な引用・
CHECKLIST・Past Case Contact表記等、SKILL.mdの要件を満たす高品質な応答を生成)。

**次にこの件に触るときは**: (1) Dify管理者/ベンダーにSonnet 5のストリーミング処理バグを報告
すべきか中村さんに確認、(2) 修正されればSonnet 5に戻すか、Sonnet 4.6のまま運用するか判断、
(3) データセット名のリネーム(`knowledge_consumer...`→分かりやすい名前)、(4) 未公開のまま
なので中村さんが動作確認して問題なければ「公開する」を押す必要あり、(5) PPTX自動生成は
ユーザー指示により意図的に未着手(後回し)。

### 2026-09-11同日追記: 公開後にアクセス権・ファイル添付の2件を共有ブラウザ経由で診断・修正
中村さんが「公開する」を押した後、(1)アクセス権を付与した相手が開くと編集画面(Studio)に
なりChatGPTのような画面にならない、(2)WebAppは開けるようになったがファイル添付ができない、
の2件を質問。共有ブラウザ(company Mac, port 9226, [[shared_bot_browser]])の既ログイン済み
Difyタブ経由でPlaywright CDP接続しDOMを直接調査して原因特定・修正した。

- **(1)の原因**: 「公開する」ボタンは変更反映のみで、エンドユーザーが使うべきURLは
  同パネル内の「アプリを実行」(WebApp本体URLを開くリンク)。編集画面が開いてしまうのは、
  相手をワークスペースメンバーとして招待していたため(Studio全体に入れてしまう)。
- **重大な発見: 「アプリを実行」ボタンがグレーアウトする条件**: Webアプリアクセス権を
  「特定のプラットフォーム内メンバー」にした場合、そこに指定した相手(石井美香さん)だけを
  追加しても「アプリを実行」ボタン(`<a>`要素、実際のWebApp URLへのリンク、無効時は
  `cursor-not-allowed opacity-30`クラス付与でhref自体が張られない)は無効化されたまま。
  **操作している本人(ワークスペース管理者自身)もアクセス許可リストに含めないと有効化されない**
  ——このボタンは実際のWebApp URLをそのまま開くリンクで、今ログイン中のアカウントがアクセス
  権を持っているかどうかをボタン自体の有効/無効に反映する仕様と判明。「プラットフォーム内の
  全メンバー」に変えると即座に押せるようになったのも、自分自身が「全メンバー」に含まれる
  ため。**教訓: PoC等で「特定のプラットフォーム内メンバー」に絞る場合、テスト対象者だけでなく
  管理者自身も必ずメンバーリストに追加すること。**
- **(2)の原因**: アプリの「機能」パネルの「ファイル アップロード」トグルがデフォルトOFF
  (`aria-checked="false"`)だった。チャットフロー新規作成時、このトグルはオフが初期値らしく、
  ドキュメント検索・LLM連携が動いていても添付ボタン自体が入力欄に出ない。
  ONにすると「サポートされるファイルのタイプ」設定(トグル直下の要約行をクリックすると
  「ファイル アップロード設置」モーダルが開く)で画像/ドキュメント/音声/映像/その他を個別選択
  できる。**ドキュメントカテゴリの対応拡張子**: TXT, MD, MDX, MARKDOWN, PDF, HTML, XLSX, XLS,
  DOC, DOCX, CSV, EML, MSG, PPTX, PPT, XML, EPUB(Word/PDFはここに含まれる)。
  画像はデフォルトでON済みだったので、ドキュメントを追加選択(両方ON)して保存。
- **UI操作上のハマりどころ**: この「機能」パネルの各種行(トグル要約行など)はPlaywrightの
  通常の`locator.click()`やJSの`element.click()`では反応しない(要素自体はcursor:pointerで
  無くクリックイベントが正しい座標で発火しない模様)。`getBoundingClientRect()`で座標を取得し
  `page.mouse.click(cx, cy)`で実座標クリックする方式に切り替えたら正常に動作した。
  今後Dify管理画面をブラウザ自動操作する際はこの座標クリック方式を優先すること。
- 最終的に「機能」→ファイルアップロードON+ドキュメント追加→保存→「公開する」→
  「更新を公開」まで実行し、「公開日時 数秒前」「公開済み」表示で本番反映を確認済み。
  作業後は[[shared_bot_browser]]の標準手順通りウィンドウを最小化。

## 2026-09-11: Agency OS(ChatGPT Skill)がQUICKモードで社内ナレッジ検索・電通フォーマットを
スキップする不具合を修正

ユーザーフィードバック: 「指示をしても社内ナレッジを見てくれないことがある(理由:アイディア
出しだから)。アウトプットも電通フォーマットじゃない場合があった。」ChatGPT共有リンク4件は
いずれも本セッションから403/アクセス不可(既知の制約、詳細は[[ai_agency_team_feedback_20260903]])
だったため会話本文は未読。`GPT作業/SKILL.md`本体を精読して原因特定:

- 「Mandatory internal search pattern」節と「Client deliverable requirements(A-F)」節の
  両方が**QUICKモード(雑談的なアイデア出し依頼)を明示的に対象外**にしていた。つまり
  「アイディア出しだから社内ナレッジを見ない」はChatGPT側の誤動作ではなく、SKILL.mdの
  指示通りの正しい動作だった。
- チャット回答の構成をリボン思考(拡散→収束→拡散)/1-3-1/fact+解釈の電通標準フォーマットに
  する規定がSKILL.mdに一切存在しなかった(PPTX生成時のテンプレート指定はモード制限なしで
  既にあったが、テキスト回答の構成規定が丸ごと欠けていた)。

対応: `GPT作業/SKILL.md`を直接編集(編集前は`SKILL_V4.md`として保存)。(1) Core principles
直後に「社内ナレッジ検索と電通フォーマットはどのモードでも省略不可」の明示ブロックを追加、
(2) Mandatory internal search patternをQUICKモードにも拡大(QUICKは最低1-2バケットの軽量版)、
(3) Client deliverable requirementsの適用範囲をQUICKにも拡大(簡略化は可、省略は不可)、
(4) 新規ルールG追加(拡散収束・1-3-1・fact+解釈・PPTXは全モードでdentsu_gtm_template_clean.pptx
必須)。418行→472行。詳細な差分記録は`GBC-Knowledge/agency_os_skill_instructions_addendum_20260911.md`。

**残作業(ユーザー対応)**: `GPT作業/SKILL.md`最新版をChatGPT Skillエディタに貼り付けて保存し、
QUICKモードのカジュアルな依頼で再テスト(社内ナレッジ検索/電通フォーマット構成/PPTXテンプレート
の3点)。問題が再現する場合は当該やり取りの本文(PDF等)を共有してもらえば、共有リンク403の
制約を回避して原因特定できる。

## 2026-09-11 続き: ChatGPT共有リンクを実際に読了+Dify版のライブ調査で根本原因を確定

ChatGPT bot browser(port 9224、社内ワークスペース済みログイン)経由で共有リンク4件を実際に
開いて読了(社外からは403だが社内ログイン済みセッションからは閲覧可)。4件は同一KFC
マレーシア案件で条件を変えた依頼: 内部ナレッジ引用に成功したのは「Thinkingモデル」で
生成された1件のみ、失敗した3件は全て「5.5 Instant」モデルで生成されており、うち1件は
「アイディア出し段階なので内部検索していません」(ユーザー報告と一致)、もう1件は「この
チャット環境ではKnowledge Pack本体にアクセスできていません」と明言(ただし直前の成功例と
ほぼ同一の依頼文だったため、本物の権限差ではなくInstantモデルがツール呼び出しを試みず
先回りで判断した可能性が高いと判定——バンドルされたKnowledge Packは全ユーザー共通のはず)。
SKILL.mdにさらに2点追記(内部検索必須化をユーザー依頼文の文言に依存させない、「アクセス
できない」と言う前に必ず実際に検索を試みることを明記)。472行→484行。

Dify版「GBC Agency OS」(console.dj-dify.dentsu.jp)も共有ブラウザ(port 9226)経由でライブ
調査。SYSTEM promptはまだ旧版(貼り付けはリスク回避のため未実施、更新版はSKILL.mdに用意済み)。
「駐在員の名前が出なかった」の根本原因を確定: ナレッジベース内`overseas_staff_index.md`が
インデックス作成エラー(Bedrock埋め込みAPIの1テキスト最大2048文字制限を、チャンク長設定
4000文字が生む一部チャンク(過去の駐在経験者セクション、3986文字)が超過、ドキュメント
全体が0/64チャンクとも一度も検索されていない)。再試行2回も同一エラーで失敗、既存
ドキュメントのチャンク長再設定機能がないため削除→チャンク長1024文字での再アップロードが
必要(他18ファイルには影響なし)。作業中、SYSTEM promptエディタでja-JP環境由来の誤字混入
事故が1回発生したが即座に復旧、バージョン履歴で本番(直近公開17:11時点)への影響なしを
確認済み。詳細は`GBC-Knowledge/agency_os_and_dify_investigation_20260911.md`。

**残作業(ユーザー確認待ち)**: (1)SKILL.md最新版のChatGPT/Dify両方への反映、
(2)Difyの`overseas_staff_index.md`削除+チャンク長1024での再アップロード、
(3)PoC参加者へのThinkingモデル利用案内の要否。

## 2026-09-12: Dify版overseas_staff_index.mdの再アップロード完了(残作業(2)を解消)
中村さんの指示で残作業(2)に着手。個人Mac(ICPTokyo2022)の共有ブラウザ(port 9227)で
Dify(console.dj-dify.dentsu.jp)へ**今回初めてSSOログイン**(djn-client.dentsu.jp Okta。
これまでは会社Mac port 9226でのみログイン済みで、ブラウザプロファイルはマシン別のため
個人Macでも別途ログインが必要だった。以後は個人Macからも自動操作可能)。
ナレッジベース「knowledge_consumer...」から該当ファイル(エラー状態)を削除→18/18利用可能を
確認→再アップロード。STEP2のチャンク長設定は**既にデフォルトで1024文字**になっており
(前回の4000文字は一時的な操作ミスだったと判明)、変更不要のままそのまま保存。
「チャンクをプレビュー」機能はDify側のバグ(`enable`フィールドのNone/バリデーションエラー)
でプレビュー表示自体には失敗したが、設定値は正しいため無視して保存を実行。処理完了後、
19/19ドキュメント全件が「利用可能」ステータスになりエラーバナーが消えたことを確認。
**検索テストで有効性を実証済み**: 「タイ 駐在 経験者」で検索し、現在駐在中10名
(バンコク中島幸子さん等)・過去の駐在経験者(ヤンゴン池田充聰さん、台北野元陽さん等)が
正しくヒット。詳細は[[work_status/gbc_intelligence_engine_dify_staff_reupload_20260912]]参照。

残作業(ユーザー確認待ち、変わらず未着手): (1)SKILL.md最新版のChatGPT/Dify両方への反映、
(3)PoC参加者へのThinkingモデル利用案内の要否。加えて2026-09-11メモの
GBC Business「3拠点目」展開(アカウント付与結果待ち)も引き続き未確認。

## 2026-09-12: GBC Business「3拠点目」は権限付与されず終了、QUICKモード廃止、Dify Web検索は断念
GBC Business側管理者への権限付与依頼の結果、**権限付与されないことが確定**。3拠点目展開は終了。

続けて、中村さんが上記(1)の反映後に実機テストを実施したところ、QUICKモードが「詳細URLはSTANDARD/
FULL AGENCYで展開します」と引用を先送りし、内部ファイル名(`cases_apac.md`等)をそのまま出し、
「部分ヒット」とだけ言って中身を出さない、という新たな違反を発見。SKILL.mdを修正し
**QUICKモードを廃止**(484→515行。ユーザーがQUICKと言った場合は廃止通知を出しつつSTANDARD相当で
実行)、出し惜しみ禁止の3条文を追加。あわせて「Web検索ツールが無い環境では正直に申告し
外部知識はMODEL MEMORYとラベル付けする」ルールも新設(Difyの対応と連動、下記)。

中村さんの依頼でDifyにもWeb検索を追加できるか調査(設定操作自体は中村さんが自分で行う方針)。
Difyの「GBC Agency OS」は知識検索→LLM→回答のみでWeb検索ツールが元々無いことを確認。
インストール済みのBrave/Jina AIはどちらもAPIキー課金の壁(Braveは無料プラン無し、Jinaは既存
キー残高マイナス)、無料・キー不要の定番DuckDuckGoは中村さんの会社アカウントにマーケットプレイス
新規インストール権限が無く断念。最終的に中村さんの判断で**「Difyは社内ナレッジ専用ツールと
割り切る」ことに決定**(2026-09-12)。深い外部リサーチが必要な場合はChatGPT版Agency OSを使う
役割分担がSKILL.md本体にも明記された。詳細は
[[work_status/agency_os_quickmode_removal_and_dify_websearch_20260912]]参照。

**次にこのプロジェクトに触るとき**: (1)修正済みSKILL.md(515行)がChatGPT/Dify両方に反映
済みか、(2)反映後にURL引用・内部ファイル名不使用・中身の完全表示が直っているか再テスト、
(3)PoC参加者へのThinkingモデル利用案内の要否、を確認すること。

## 2026-09-12(同日続き): SKILL.md/SKILL_Dify.mdの2ファイル分岐 + Dify添付ファイル未読み込みバグ発見
中村さんの指示で、ChatGPT版とDify版でSkill内容が分岐する(Web検索・PPTX)ため
`GPT作業/SKILL.md`(ChatGPT版、515行、変更なし)と新規`GPT作業/SKILL_Dify.md`
(Dify版)の2ファイル体制にした。SKILL_Dify.mdでは、Web検索・社内コネクタが常時
利用不可であることの明記、外部リサーチが必要な場面で1回だけWebサーチ非対応と
ChatGPT版への案内を出す文言、PPTXは電通テンプレート非対応を明示した上で
Markdownエクスポーターツール(既存インストール済み)経由で無地PPTXをその場で
生成する手順に全面差し替え、`references/`フォルダ自体が存在しない前提への
書き換え、を実施。

さらに中村さんの実機テストでDocxファイル添付がDifyで機能しておらず、モデルが
「画像として確認しましたが解像度で読み取れない」という**事実と異なる言い訳を
捏造**していたことが判明(実際はDOCXで画像ではない)。原因はDifyの
「GBC Agency OS」チャットフローが`知識検索→LLM→回答`のみで、添付ファイルの
内容を抽出してLLMに渡すノードが無いため(2026-09-11のファイルアップロード
トグルON化は添付ボタンを出しただけで、内容抽出・LLM受け渡しの配線までは
未実装だったと判明)。SKILL.md・SKILL_Dify.md両方に「添付ファイルの中身が
実際に見えていないのに読んだふりをしない」正直性ルールを追加。Difyの
「ドキュメント抽出」ノードを知識検索とLLMの間に追加する配線修正手順を
中村さんに提示済み(中村さんがDify操作を自分で覚えたい意向のため、実際の
配線修正はユーザー対応待ち)。詳細は
[[work_status/agency_os_dify_skill_split_and_file_upload_bug_20260912]]参照。

**次にこのプロジェクトに触るとき**: (1)中村さんが「ドキュメント抽出」ノードを
追加し添付ファイルが正しく読めるようになったか、(2)SKILL_Dify.mdがDifyの
SYSTEM promptに貼り直されたか、(3)Webサーチ非対応・PPTX非対応の開示文言と
Markdownエクスポーター経由のPPTX生成が意図通り動くか、を確認すること。

## 2026-09-12(同日続き): テキスト抽出ノード配線+2件のブリーフ実機テストで
捏造・検索漏れを複数発見、SKILL.md/SKILL_Dify.md両方に追加修正
中村さんとの対話形式(中村さんがDify画面を操作、Claudeは調査・手順提示)で
「テキスト抽出」ノードを追加・配線し、docx添付が実際にDropboxプレースホルダー
(0バイト)だった問題も発見・解決(`open -g`で実体化)。知識検索ノードの
クエリテキストが`sys.query`のみで添付資料の内容を見ていなかった問題も
中村さん自身が気づき、テンプレートノード(Jinja2)で`sys.query`+テキスト抽出
結果を結合してから知識検索に渡す構成に修正
(`スタート→テキスト抽出→テンプレート→知識検索→LLM→回答`)。

その後の2件の実機ブリーフテストで新たに4件の問題を発見(詳細は
[[work_status/agency_os_dify_fabrication_and_retrieval_gaps_20260912]]参照):
(1)SKILL.mdルールA自身の説明用サンプルURLをモデルがそのまま実データとして
流用、(2)tools.md(実28ツール、grep確認済み)に存在しない「GBCarekoko」
「Nielsen」等のツール名を完全捏造、(3)overseas_staff_index.md(実データに
ベトナム駐在3名を確認済み、うち1名はブリーフ宛先と同姓)があるのに「特定
できず」と回答、(4)「検索実施バケット」の生ファイル名リスト表示の再発。
根本原因は知識検索のTop K=6が8ファイル分の横断検索には不足しており、
tools.md/overseas_staff_index.mdのような該当範囲が狭いファイルが検索結果に
入らないこと(→ルールで必須とされたセクションを埋めるため捏造が発生)。
SKILL.md/SKILL_Dify.md両方に(1)説明例URLの明示的フェイク化、(2)ツールは
今回の検索結果にあるものだけ使い0件なら正直に0件と言う、(3)検索バケット
リストをユーザー向け出力に出さない、を追加。Top K増加(6→15-20程度)は
中村さんへの設定変更提案として提示済み、未実施。

**次にこのプロジェクトに触るとき**: (1)Top K設定変更の実施有無、
(2)SKILL_Dify.md最新版の貼り直し、(3)同じAcecook Vietnamブリーフで
再テストし実URL/tools.md実ツールのみ/ベトナム駐在3名が正しく出るか確認。

## 2026-09-12(同日続き): 知識検索アーキテクチャを分割(変数集約器導入)、
ワークスペース懸念も発覚、公開完了
overseas_staff_index.mdの見出し修正・CASE捏造発見([[work_status/agency_os_dify_case_fabrication_and_privacy_excuse_20260912]])
を受け、根本原因(Top K=10で8ファイル横断検索は巨大ファイルに埋もれる)への対処として、
検索アーキテクチャ自体を再設計した。データ精査の結果、`knowledge_untagged_01.md`
(74.6万語)・`cases_apac_01.md`(55.6万語、Acecook Vietnam実ケースCASE_ID 7133を含む)を
既存の分離済み2ファイルと合わせ計4ファイル(約185万語)を専用データセット
「GBC Knowledge Pack - CASES (large files)」に集約。Difyフローに「知識検索2」ノードを
追加(Claude実施)し、中村さんが「変数集約器」ノードを追加して両知識検索の結果を統合、
LLMのコンテキストを変数集約器の出力に差し替え(中村さん実施)。SYSTEM promptに
補足セクションを追記し公開完了。

作業中、Dify contenteditableエディタで「/」がスラッシュコマンドとして誤発動する事故、
Escape後のBackspaceでLLMノードが誤削除される事故が発生したが、いずれもCmd+Z等で
即座に復旧しデータ損失なし(詳細は[[work_status/agency_os_dify_retrieval_architecture_split_20260912]]参照)。
「文末へ確実に移動」は`Cmd+A→ArrowRight`のみ有効、`Control+End`等は効かないことが判明。

副次的な発見: このDifyワークスペース「dJ-Dify_共通プレイグラウンド」が他部署の様々な
テストアプリと同居する全社共有サンドボックスである可能性が高く、実PoC用途としては
GBC専用ワークスペースへの移行をDify管理者に確認すべきと中村さんに提示済み(未実施、
判断待ち)。

**次にこのプロジェクトに触るとき**: (1)Acecook/Aureliaブリーフで4回目のテスト
(CASE_ID 7133・実ツールURL・駐在員名フル表示の確認)、(2)ワークスペース移行要否の
判断、(3)ChatGPT版SKILL.mdへの同種の思想反映要否、(4)`*_`という原因未特定の
文字化け(優先度低)。

## 2026-09-12(同日続き・チャット引き継ぎ): 検索クエリが長すぎて精度が落ちる問題を発見、
「ブリーフ要約」ノード追加が次のタスク
変数集約器導入後、中村さんが実ブリーフで再テストしたところCASES/KNOWLEDGE/駐在員が
全て「該当なし」に。ClaudeがStudioの「プレビュー」機能で同一内容を短い直接質問で
再現テストしたところ、CASE_ID 1200(実URL付き)・Knowledge Card・駐在員テーブル
(伊藤広貴/野口紗知子等)が全て正常に表示され、**アーキテクチャは正常**と確認。
原因は「知識検索のクエリテキストがブリーフ全文(2600文字超)をそのまま使っており、
ベクトル検索が長文ノイズで精度低下していたこと」と特定(短い直接質問では正常動作した
ことから逆算)。

**次の新規チャットで最初にやること(中村さんがこのセッションを閉じて新チャットへ
引き継ぎ希望)**: `テキスト抽出`と`テンプレート`の間に新規LLMノード「ブリーフ要約」
(検索用に600字要約を生成)を追加し、`テンプレート`の`doc_text`変数の参照元を
`テキスト抽出.text`から`ブリーフ要約.output`に差し替える。**LLMノードのSYSTEM prompt
に直接埋め込んでいる`テキスト抽出.text`(本文全体)は変更しない**(要約は検索クエリ
専用、LLMが読む本文は今まで通りフル)。詳細な実装手順・現在のフロー構成全体・
診断に使った有効な手法(プレビュー機能でのリアルタイムテストが実行ログより有効)は
[[work_status/agency_os_dify_query_summarization_handoff_20260912]]に詳細記録済み。

## 2026-09-12(同日続き): overseas_staff_index.mdの見出し構造バグ修正 + CASE捏造・
個人情報言い訳という新たな捏造パターンを発見
Top K=10(Difyプラン上限)に変更後もベトナム駐在員が検索されない問題を中村さんと共同調査。
`overseas_staff_index.md`を直接grepし、「## ベトナム」という国名見出しと実際の駐在員リスト
「### 現在駐在中」が別チャンクに分かれ、名前入りチャンクには国名の単語自体が一度も
出現しない構造的バグを発見(検索テストで実証: スコア0.21の4文字だけのゴミチャンクしか
ヒットせず)。生成スクリプト`generate_overseas_staff_pack.py`を修正(各国の"###"見出しに
国名を繰り返し埋め込む)し、既存の出力ファイルにも同じ変換をPythonスクリプトで直接
パッチ(20カ国・40見出し分)。中村さんがDifyへ再アップロード、検索テストでスコア0.71に
改善・名前入りチャンクが1位に。ChatGPT側のKnowledgeも中村さんが修正版に更新済み。

その後の3回目のAcecookブリーフテストで、tools.mdだけでなくCASE/KNOWLEDGE全般で同種の
捏造が起きていることを発見: `cases_apac_01.md`を直接grepしたところ、ブリーフと一言一句
レベルで一致する完璧な直接ヒットケース(CASE_ID 7133「Acecook Vietnam 年間コントラクト」、
担当者は新保泰史—ブリーフ宛先本人、実URL付き)が存在するにもかかわらず、Dify出力は
どのCASE_IDにも対応しない完全に捏造されたケース名を提示していた。さらに、駐在員名を
「個人情報保護のため」と自己判断で秘匿しユーザーに丸投げする新しい違反パターンも発見
(ルールFは氏名表示を明確に要求しているのに反する)。SKILL.md/SKILL_Dify.md両方に
(1)捏造禁止をTOOLSだけでなく全バケットに拡張、(2)個人情報を理由にした氏名秘匿を
明示的に禁止、を追加。根本原因は知識検索がTop K=10で8ファイルを1回で横断検索する設計の
限界(巨大ファイル内の完全一致レコードでも他ファイルと競合し漏れることがある)で、
将来的にはファイル別に知識検索ノードを分割する再設計が必要になる可能性が高いことを
中村さんに提示済み(未着手、相談中)。詳細は
[[work_status/agency_os_dify_case_fabrication_and_privacy_excuse_20260912]]参照。

**次にこのプロジェクトに触るとき**: (1)SKILL_Dify.md最新版の貼り直し、
(2)同じAcecookブリーフで4回目のテスト(CASE_ID 7133が正しく見つかるか、
駐在員名がフル表示されるか)、(3)検索アーキテクチャのファイル別分割に着手するか
中村さんと相談、(4)出力に散発する`*_`という原因未特定の文字化け(優先度低)。

## 2026-09-14: Dify版の実際のWebApp URLを確定 + PoC説明会資料にDify使い方ページ追加
「GBC Agency OS」アプリ(id: 047d1529-f9fb-4211-a5a9-dc45aaee90a1)の公開パネル
「アプリを実行」リンクから実URLを取得(共有ブラウザ port 9226経由): **https://app.dj-dify.dentsu.jp/chat/UhIAspvW1bROU3Ar**
(これまでメモに記録がなかったため今後はこのURLをそのまま使う。念のため:
`GBC-Knowledge/output/agency_os_pack_full/cases/cases_global_02.md`内に出てくる
`app.dj-dify.dentsu.jp`や`udify.app`のURL群は無関係の過去ケース事例の引用であり、
このアプリのURLではない)。

本日のPoC説明会に向け、`20260909PoC説明/Agency_OS_PoC募集資料_20260914.pptx`
(ベースは15:25版`_20260911.pptx`)に「使い方(Dify版)」スライドを5枚目として追加
(ChatGPT Enterprise未保有者向け、STEP1アクセス申請/STEP2使い方(上記URL記載)/
STEP3現時点でのご留意点=Web検索非対応・PPTX電通テンプレ非対応・フィードバックは
スクショ/テキストのコピー貼付)。詳細は
[[work_status/agency_os_dify_deck_page_20260914]]参照。

**未確認のまま**: DifyのWebAppにChatGPTの「共有する」相当の会話共有リンク機能が
あるかどうか(Oktaへの再ログインが必要でこのセッションでは未検証、スライドでは
断定せず代替案のみ記載)。

## 2026-09-14(別セッション): Agency OS SKILL.mdの安全性レビュー警告→ChatGPT Skillの
「Needs Review」承認ボタンで解消

SKILL.mdを更新後、再度開いたら「安全性レビューにより潜在的に危険な動作が検出されました
(想定ワークフロー外へのデータ送信の可能性/承認・ロギング・認証等の安全管理回避の可能性)」
という警告が表示された件。

**このセッションでの誤り(記録用)**: 質問された時点でプラットフォームを確認せず、
いきなりClaude(claude.ai)側のEnterprise Skill security scanningの話だと決め打ちして
Web調査・回答してしまった。中村さんに「いまはChatGPTのSkillを使って構築しています」と
訂正されて発覚。[[feedback_agency_os_is_chatgpt_skill_not_gpt]]に教訓として統合済み
(3回目の同種取り違え)。

**判明した事実(OpenAI公式ヘルプ「Skills in ChatGPT」より)**: アップロードしたSkillの
スキャン結果は「即利用可/Needs Review(要レビュー、使用自体は継続可)/Blocked(使用不可)」
の3段階。今回は使用は継続できていたためNeeds Review相当と推測。

**試した対処と結果**:
1. SKILL.md内の「Withholding」ルール(`overseas_staff_index.md`/`case_expert_index.md`の
   個人名をプライバシー懸念を理由に伏せるな、という文言)が最有力候補と判断し、
   「社内アクセス権者向けの正確な引用が目的」という理由づけに書き換え、
   Always-on constraintsに「Scope and audience」(社内限定利用の明記)を追加。
   → **警告は消えなかった**。文言修正だけでは効かないケースがあると判明
   (個人名・内部URLをそのまま出力する設計自体が構造的にフラグされている可能性)。
2. ChatGPT UI上に表示されていた「承認」ボタンを押したところ警告が消えた
   (この存在は中村さんが自分で発見、UI詳細情報は文言修正の効果検証には出てこなかった)。
3. 承認直後にSkill編集画面が「Content failed to load」で開けなくなったが、
   ブラウザを新規に立ち上げ直してログインし直したら解消(一時的な不具合と判断)。

**次回同種の警告が出た時の推奨手順**: SKILL.mdの文言をあれこれ調整する前に、
まずChatGPT UI上に「承認」ボタンが出ていないか確認するのが早い。それでも消えない/
Blocked表示になる場合のみ、個人情報・内部URL出力箇所の文言/設計を見直す。

## 2026-09-15: 「Topic Expert Index」を新設(SharePoint部署別担当者 + チーム別エキスパート手動リスト)
中村さんの要望で、Agency OSに「誰に聞けばよいか」の第3の人物インデックスを追加した。
既存の`case_expert_index.md`(Salesforce案件履歴から機械推定、Potential Candidate扱い)・
`overseas_staff_index.md`(駐在履歴、機械集計)とは異なり、今回は**公式担当者一覧または
本人の直接申告に基づく確認済みの現役担当窓口**なので、留保表現なしで`Topic Expert`/
`Task Contact`として案内してよい設計にした。

**取得方法の決定(中村さんが「スクショはトークンを食うのでHTML分析で節約できないか」と
質問)**: SharePoint「GBC-アレココ」ホーム(`https://esq365.sharepoint.com/sites/GBCarekoko/
SitePages/Home.aspx#gbc各部紹介`)の「業務関連：GBC担当者一覧」ブロックを、既存の共有
ブラウザ(d14461、port 9226、Teams/Entra SSOが既にSharePointにも通ることを確認済み)で
Playwright接続しDOMテキスト(`document.body.innerText`)を読む方式を採用・実装した。
スクリーンショット+画像解析より圧倒的に安く、表形式データでは精度も高い
(2026-08-18の局員プロフィールスクレイピングと同じ方針、[[feedback_prefer_deterministic_over_llm]]
とも合致)。ブロックの構造は「トピック見出し行→(氏名行,役職行)の連続」だが、役職値に
既知の語彙(`-`/`なし`/`ＧＭ`/`シニア・マネージャー`/`ＨＲＭ`)を使った先読みで氏名行/
トピック行を判定する方式にした(1件、"Ｇｌｏｂａｌ Ｑ Global Q"という氏名部分に
日本語文字が無いエントリがあり、素朴な「ASCII文字+日本語文字の両方を含む」判定では
誤ってトピック見出しと誤認識するバグを発見・修正した)。

**実装した新規ファイル**(`GBC-Knowledge/`配下):
- `sharepoint_department_contacts_source/scrape_gbc_dept_contacts.js`: 上記スクレイパー
  (Node/Playwright、`~/.local/share/claude-playwright/`から実行)。出力は日付付きJSON。
- `generate_topic_expert_pack.py`: 上記JSON(最新ファイルを自動検出)+スクリプト冒頭の
  `MANUAL_TEAM_EXPERTS`辞書(チーム/スキル軸のエキスパート、SharePointに掲載が無く
  中村さんから直接申告されたもの: AI開発・AI相談/インバウンド/IPコンテンツ・アニメ・
  ゲーム/日系外食産業海外進出/博報堂分析/Salesforce/PowerBI・PowerApps開発/アプリ開発、
  計8トピック)を合成し、`output/agency_os_pack/experts/topic_expert_index.md`を生成。
  `generate_overseas_staff_pack.py`と同じ設計パターン(既存パイプラインとは独立、
  読み取り専用ソース、同名ファイル上書き方式)を踏襲。

**SKILL.md(ローカル控え、`GPT作業/SKILL.md`)への反映**: 新規Requirement H
「該当するTopic/Task Expertを必ず紹介する」を追加(既存A–GにH追加、Common Knowledge
Test Modeの記述・GBC Knowledge Pack構成一覧・Withholdingルール・How to use each
internal source・月次更新の生成日注記もすべて`topic_expert_index.md`を含むよう更新)。
`output/agency_os_pack/README.md`にもファイル一覧・生成コマンド・Expert Index注意事項を追記。

**未実施・要判断(次にこの件に触るとき確認すること)**:
1. **定期更新の頻度**: 中村さんは「定期的に更新したい」と述べたが具体的頻度は未確定。
   Part1(SharePoint)はブラウザ操作が要るため完全自動化は現状未設定(手動再実行の
   コマンドはREADMEに記載済み)。Part2(手動リスト)は自動更新元が無いため必然的に
   手動。**現状は月次のKnowledge Pack再生成ルーチンに相乗りする形を仮の運用としており、
   専用launchdジョブは作っていない**。次回、中村さんに頻度の希望を確認すること
   ([[feedback_match_automation_frequency_to_source_cadence]]参照、hourly等を安易に
   採用しない)。
2. **Teamsチャット履歴からの暗黙エキスパート抽出**: 中村さんから「Teamsのやり取りから
   『この人はこのエキスパート』というものもリスト化してAgency OSに組み込みたい」との
   追加要望あり。スコープ(全履歴を対象にするか/どんな発言を根拠として採用するか/
   本人の同意なく個人のTeams発言から専門性を推定して共有ナレッジベースに載せることの
   適否)が未確定なため、今回は着手せず中村さんに確認中(スコープ確定後に着手予定)。
3. ChatGPT Enterprise/Dify/GBC Business等、実際にAgency OSが動いている拠点への
   `topic_expert_index.md`のアップロード自体はまだ実施していない(ローカルのPack生成
   とSKILL.md控えの更新のみ完了)。既存の月次アップロード運用に乗せて中村さんが
   手動で反映する想定。

## 2026-09-15(続き): 定期更新方針の確定 + Teamsマイニングのタスク中継(task-013)
中村さんに確認した結果:
1. **Part1(SharePoint)の再取得頻度**: 既存の月次Knowledge Pack再生成ルーチンに相乗りする
   運用で確定(専用launchdは作らない)。READMEの月次更新手順に既に反映済み。
2. **Teams全履歴からの暗黙エキスパート抽出**: 「本格的に、全履歴を対象に」やる方針に確定。
   ボリューム(7,340件)から一次分類にOllamaを使う方針を提案・承認、当初は会社Mac
   (qwen3:8b)か個人Windows機(qwen3.8:27b、より大型)かの選択を提示したところ個人Windows
   機を希望されたが、**会社Macから192.168.0.11:11434へ接続できず**(ネットワーク到達不可、
   タイムアウト)。中村さんの判断で、この処理自体をWindows側Claude Codeセッションへ
   `claude_relay`(windows_inbox.md)のtask-013として中継依頼した。
   - 対象データは`teams_export_source/teams_messages_d14461_20260915.jsonl`として
     会社MacのTeamsExportから本プロジェクトへコピー配置済み(Dropbox同期、7,340件、
     2026-01-01以降、42チャット分)。
   - 設計要件: author欠損補完(mid順forward-fill)/EXPLICIT(名指し推薦)とINFERRED
     (関与パターンからの推定)を区別/根拠グラウンディング必須(evidence_quoteの文字列
     照合、既存の`_grounded_in_evidence()`と同じ思想)/業務外の私的内容は対象外/
     出力は中間JSON(`output/teams_implicit_expert_candidates.json`、確定リストではなく
     候補)。Markdown化・SKILL.md反映は次回Mac側で行う。
   - **次にこの件に触るとき**: まず`windows_inbox.md`のtask-013のStatus/Resultを確認する
     こと(中村さんがWindows側セッションに「windows_inbox.md を確認して」と伝えた後に
     着手される、手動トリガー方式)。完了していれば`teams_implicit_expert_candidates.json`
     をレビューし、`experts/topic_expert_index.md`に「Part 3: Teams由来の推定エキスパート
     (要検証)」のような、`case_expert_index.md`と同様に留保表現付きのセクションとして
     統合し、SKILL.mdにも反映する。

## 2026-09-15(続き2): task-013の結果をレビュー・Part 3として統合完了
Windows側task-013が完了(候補405件、explicit=160/inferred=245、グラウンディング不一致で
77件自動破棄)。結果(`output/teams_implicit_expert_candidates.json`)をMac側でレビューし、
`generate_topic_expert_pack.py`を拡張してPart 3として`topic_expert_index.md`に統合した。

**レビューで対応した精度上の論点**:
- 氏名表記ゆれ(124種)のうち、**厳密に同一のフルネーム(姓+名)が空白/ローマ字有無だけ
  違う場合のみ**`TEAMS_NAME_MERGE`辞書で正規化して統合(例: 「中村正樹」「中村 正樹」
  「中村 正樹 Masaki Nakamura」→「中村 正樹」)。**姓のみの言及(宮川/小松/山内/田村/
  岩田/山田/星野/牧野等、`TEAMS_UNRESOLVED_SURNAMES`)は、同姓のフルネームが他で
  見つかっても同一人物と断定せず統合しなかった**(誤同定リスク回避、このプロジェクトの
  「推測で埋めない」原則を踏襲)。Part 3末尾に「氏名未確定」セクションとして分離表示。
- Windows側が報告した「中村正樹への構造的バイアス(候補全体の34%)」はそのまま残し、
  Part 3冒頭に注意書きとして明記(Teamsエクスポート自体が本人アカウント起点のため)。
- Part 1/2(確認済み現役担当窓口、断定表現`Topic Expert`可)とPart 3(機械推定、
  `case_expert_index.md`と同じ留保表現`Teams-Inferred Candidate`必須)の性格の違いを
  `SKILL.md`(Requirement H、Withholdingルール、bucket一覧、How to use each internal
  source、生成日注記)・`README.md`双方に明記し、Part 3をPart 1/2と混同して断定的に
  紹介しないよう徹底した。

`generate_topic_expert_pack.py`は`output/teams_implicit_expert_candidates.json`の有無を
見て自動的にPart 3を追加/省略する設計(ファイルが無ければ警告なしにPart 3を省略、
既存の2ソース合成は影響を受けない)。

**未実施**: 実際のAgency OS拠点(ChatGPT Enterprise/Dify/GBC Business)へのアップロードは
中村さんが月次運用で実施予定(ローカルPack生成とSKILL.md控えの更新まで完了)。

## 2026-09-15(続き3): 中村さんの内容チェック→大幅トリム、今後は本人を抽出除外
中村さんが`topic_expert_index.md`を自分でチェックし、Part 3(Teams由来候補)の大半
(51KB→8.3KB)を手動削除。理由: 「私の業務に関する周辺のことが多く局員が通常使える
エキスパートではなかった」。ただし「これだけでも十分有用なデータソース」と評価あり、
Part 1/2はそのまま維持。**指示: 今後の更新では中村さん本人の過去履歴は含めなくてよい**。

対応: `extract_implicit_experts.py`(Windows実行、プロジェクト直下)に
`EXCLUDED_PERSONS_NORMALIZED`(表記ゆれ吸収の正規化比較)を追加し、グラウンディング段階で
本人言及を機械的に除外するよう変更(Part 2の本人による直接申告は対象外、あくまでTeams
機械推定パスのみ)。`generate_topic_expert_pack.py`のPart 3イントロにもこの運用変更を
明記。**現在デプロイ用の`topic_expert_index.md`は中村さんの手動編集後のものが正**——
`generate_topic_expert_pack.py`を安易に再実行すると405件の未トリム版に戻ってしまうため、
次にPart 3を更新する際は再実行後に必ず再レビュー・再トリムが必要(Part 2と同様、
完全自動更新はできない運用と割り切ること)。

またPart 2のMANUAL_TEAM_EXPERTS辞書を中村さんの手動修正に合わせて更新
(「田上」→「田上 浩次郎」、「山内」→「山内 康弘」、本人が知っているフルネームで補完)。

**次のアクション(中村さん依頼)**: この内容をChatGPT Skill「Agency OS」とDify「GBC Agency OS」
の両方に反映したい、更新方法を教えてほしいとの依頼。両プラットフォームとも
topic_expert_index.mdは新規ファイル(2026-09-11時点の既存19ファイルには含まれない)。
SKILL.md自体も今回Requirement H等を追加済みでローカル控え(`GPT作業/SKILL.md`)は
更新済みだが、ChatGPT Skill本体・Dify LLMノードのSYSTEM prompt双方への反映はまだ。
具体的な手順(URL・ナレッジタブの場所等)はこのメモリの過去エントリ
([[feedback_agency_os_is_chatgpt_skill_not_gpt]]のURL、2026-09-11のDify構築記録)を
参照して回答した。

## 2026-09-15(続き4): 「法務担当」で捏造された架空の人物名を報告→原因特定(既知バグの再発)
中村さんがChatGPT Skillに「GBCの法務担当は誰ですか」と聞いたところ、実在しない
「佐藤 真理」という人物名が返ってきた(正しくは「佐多 茜」)という重大な捏造報告あり。

**調査(会社Macの共有ブラウザとは別、ChatGPT専用bot、port 9224、`~/.chrome-profiles/
chatgpt-bot`を起動)**: Skillエディタ(`chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080`)
を直接調査した結果:
1. `topic_expert_index.md`は正しくアップロード済み・内容も正確(法務担当=佐多茜と一致)
2. `SKILL.md`もRequirement H含め正しく更新・保存済み(29,861文字、CodeMirrorエディタに
   `.cm-content`へフォーカスしてCmd+A/Cで全文コピーして確認——`body.innerText`は仮想
   スクロールで冒頭しか取れないことが判明、次回同種の調査ではこの方法を使うこと)
3. 保存ボタンを押すと実際に「保存中...」が表示され、直前まで**未保存の変更が残っていた**
   ことが判明(ユーザーが直接編集後、保存を忘れていた可能性)
4. 保存後も「5.5 Instant」モデルでは検索できず素直に「検索できない」と回答(捏造はしないが
   機能しない)、**「5.5 Thinking」モデルに切り替えたところ即座に正しく「佐多 茜」を出典付きで
   回答**——**2026-09-11に記録済みの既存の既知バグ([[gbc_intelligence_engine_project]]
   「Thinkingモデルでのみ内部ナレッジ引用に成功」)の再発だったと確定**

**結論**: データ(topic_expert_index.md/SKILL.md)は正しい。**原因は非Thinkingモデル
(Instant)使用時に内部ナレッジ検索ツールを確実に呼び出さず、素直に「検索できません」と
言う代わりに捏造することがある、という既知のモデル依存の限界**。中村さんへの回答:
実際にAgency OSを使う際は必ずThinking(推論)対応モデルを選択すること、を案内。

**How to apply**: 次にAgency OSの回答品質を疑う相談を受けたら、まずデータ側(Pack
ファイル)を疑う前に、使用モデルがThinking系かInstant系かを確認すること。CodeMirror系
エディタ(ChatGPT Skillエディタ含む)のフルテキスト取得は`body.innerText`では不可
(仮想スクロールで冒頭のみ)、`.cm-content[role="textbox"]`へfocus→Cmd+A→Cmd+C→
`navigator.clipboard.readText()`が確実。

## 2026-09-15(続き5): ChatGPT用SKILL.mdとDify用SKILL_Dify.mdの分岐に気づかず一時混同
中村さんから「Dify用にSKILL.mdは修正していたと思うが、ChatGPTと同じ内容にしない方が
良いのでは」と指摘を受け発覚: 今日の作業でRequirement H等を`GPT作業/SKILL.md`にのみ
追加し、**2026-09-12に分岐済みの`GPT作業/SKILL_Dify.md`(640行、Web検索/PPTX電通
テンプレ無効化・知識検索アーキテクチャ分割等、Dify専用差分多数)への反映を失念していた**。
そのままDifyにSKILL.md(ChatGPT版)を貼ってしまうと、Dify専用の全修正が消える事故に
なるところだった。

**対応**: SKILL_Dify.mdに個別にパッチを適用(bucket一覧・Common Knowledge Test Mode
一覧・Withholdingルール・「照合をお願いします」禁止フレーズ集・How to use each
internal source・Requirement H新設(既存A–GにH追加)・月次更新セクションのbucket一覧+
生成日注記、の7箇所)。SKILL.md側とほぼ同じ追加内容だが、Dify特有の文脈
(Web検索・PPTXテンプレ非対応の断り書き等)は一切変更していない。640→660行、
topic_expert_index参照9箇所。

**教訓**: このプロジェクトは同じ役割のドキュメントが拠点ごとに複数ファイル分岐している
(SKILL.md=ChatGPT、SKILL_Dify.md=Dify、将来GBC Business用が増える可能性もある
[[gbc_intelligence_engine_project]]2026-09-11参照)。**次にSKILL.md系のルール追加・
修正をする際は、必ず両方(該当する拠点分すべて)に同じ変更を適用すること。片方だけ
直して満足しない。**

## 2026-09-15(続き6): 実際のDify system promptは既にローカルSKILL_Dify.mdより先に進んでいた
中村さんが実際にDifyへ入っていたsystem prompt全文を貼付。ローカルの`SKILL_Dify.md`
(2026-09-12版)と突き合わせたところ、ローカルファイルには無い3つの内容が本番側にのみ
存在すると判明(誰かが直接Dify側を編集し、ローカルへの反映を忘れていた):
1. 冒頭の「事前抽出」変数注入ブロック2つ(`{{{#1789217537282.text#}}`=完全一致CASE情報、
   `{{{#1789217622601.text#}}`=海外駐在員情報)。Dify側の別ノード(知識検索アーキテクチャ
   分割・変数集約器、2026-09-12の作業)の出力をLLMノードのプロンプト先頭に直接注入する
   ワイヤリングで、静的なMarkdownではなくこのDifyアプリ固有のノードID依存。
2. セクション10に「Markdown出力時の注意」(デッキ全体をコードブロックで囲むと表示が
   崩れる、アスキーアート禁止)という追加ルール。
3. ファイル末尾に「検索結果には物語文形式だけでなくメタデータブロック形式のケース記録も
   含まれる、スコアの高低で0件と誤報告しない」という追加ルール。

**対応**: 3つとも`GPT作業/SKILL_Dify.md`に統合(679行)。さらにDify貼り付け用に
フロントマター+ローカル専用HTMLコメントを除去した`GPT作業/SKILL_Dify_for_paste.md`
(659行)を新規作成——今後Difyへ貼る際は毎回このファイルを生成し直す運用にする
(SKILL_Dify.md自体は今後もfrontmatter付きのローカル管理版として維持)。

**教訓**: SKILL.md系ファイルは「ローカルが正、Difyは反映するだけ」という前提が崩れていた
——**Dify側で直接編集されて先に進んでいる可能性を毎回疑い、反映前に必ずDify側の現在の
system promptを聞く/取得して差分を確認すること**。[[feedback_agency_os_skillmd_multi_deployment_sync]]
に追記が必要(ChatGPT/Dify分岐の教訓だけでなく「ローカルコピーとライブ環境の両方が
それぞれ独立に編集されうる」という三方向の同期問題として拡張すべき)。

## 2026-09-15(続き7): KNOWLEDGEカードでURLが表示されない不具合を発見・修正
中村さんがDify版で「過去のケース紹介でURLが表示されない場合がある」と報告(例:
GBC-8DD9855805BF/GBC-1771E1BA2C8Bが出典URL無しで引用された)。

**原因**: `render_knowledge_card()`(generate_agency_os_pack.py)がSource URLを
カードの**本文の最後**(Knowledge/Why it matters/When to use/Recommended action/
Warningの後)に`## Source`セクションとして配置していた。一方`render_case_card()`は
SALESFORCE_URLを**ヘッダーブロック内**(ID/TITLE等と一緒)に配置済み。DifyのRAG
チャンク分割(1024文字)で本文とURLが別チャンクに割れると、検索でヒットした
チャンクにURLが含まれずLLMが引用できなくなる——CASEカードでは起きずKNOWLEDGEカード
でだけ起きていた理由がこの構造差だった。

**恒久対策**: `generate_agency_os_pack.py`の`render_knowledge_card()`を修正し、
SOURCEをヘッダーブロックに移動(`SALESFORCE_URL`と同じパターン)、本文末尾の
`## Source`セクションは削除。SKILL.md/SKILL_Dify.mdの該当箇所(`Source`→`SOURCE`
フィールド名)も追記修正。

**既存生成済みファイルへの適用**: `knowledge_index.db`がv2_quality_bucket列を
欠いており(会社Mac側DBが古い、Windows側のv2移行が未反映と推測)generate_agency_os_pack.py
のフルパイプライン再実行はできなかったため、既存の生成済みMarkdownを直接後処理する
`fix_knowledge_source_placement.py`(プロジェクト直下、再利用可能・冪等)を新規作成し、
POC/FULL両方のknowledge_*.mdに適用。POC 1,500件・FULL 14,897件、計16,397件の
KNOWLEDGEカード全件にSOURCEフィールドを追加、整合性チェック(改行欠落・本文Source
残存)は全件パス。

**踏んだ罠**: 初回実装(セクション単位で本文を再構築)でカード間の改行が失われる
バグを作った(「...可能性がある。---\nTYPE: KNOWLEDGE」のように直結してしまう)。
本文全体を再構築せず、`## Source`セクションの該当箇所だけを文字列操作で切除し
残りは一切触らない方式に変更して解消。さらに「Sourceのみで他セクションが無い」
スパースなカード(CONFIDENCE: low、内容抽出0件のカード)ではbody先頭が直接
`## Source`で始まり前方に`\n\n`が無いため最初の正規表現が拾えないエッジケースも
発見・修正(155件、主にknowledge_untagged_01.md)。

**次のアクション(中村さん依頼)**: 修正済みの`knowledge_*.md`(POC、7ファイル)を
ChatGPT Skill/Dify両方に再アップロード(既存ファイルの差し替え)する必要がある——
今回はローカルのMarkdownファイルを直接修正しただけで、まだどちらのライブ環境にも
反映していない。

**未解決の別課題(次にこのプロジェクトに触るとき)**: `output/knowledge_index.db`の
スキーマがv2_quality_bucket列を欠いており、`generate_agency_os_pack.py`のフル
パイプラインが実行できない状態。会社Mac側DBが個人Mac/Windows側のv2移行後のDBと
同期していない可能性が高い。最新のDBをどこから取得すべきか(Dropbox経由の共有か、
Windows側から転送か)を次回確認すること。

## 2026-09-15(続き8): Difyのナレッジベース構成は4データセットに分散(重複に見えるが設計通り)
中村さんの「knowledge_*.mdの2ファイルはどこに入れるか」「cases_apac_01.md/
overseas_staff_index.mdの重複を整理したい」という質問を機に、ブラウザ自動操作で
Dify「GBC Agency OS」の実際のワークフロー構成を調査し確定させた(port 9226、
`console.dj-dify.dentsu.jp`)。

**確定した全体構成(4データセット、ノードID付き)**:
```
知識検索(node 1789106230921, dataset "knowledge_consumer...", 16件)
  → {{#context#}} (通常回答用の主検索。topic_expert_index/overseas_staff_index/
     faq/tools/task_briefing_format/cases_japan・other・americas・emea/
     knowledge_consumer_trend・country_ad_landscape・csr_csv・industry_info・
     media_planning・misc_minor_tags)

知識検索2(node 1789197921866, dataset "cases_global_01.md...", 4件:
  knowledge_untagged_01.md/cases_apac_01.md/case_expert_index.md/cases_global_01.md)
知識検索3(node 1789203563407, dataset "cases_apac_01.md...", 1件: cases_apac_01.md単独)
  → 知識検索2+3 → LLM3 CASES抽出(node 1789217537282)
    → 【事前抽出: 完全一致CASE情報】(システムプロンプト冒頭に必須反映)

知識検索4(node 1789203717224, dataset "overseas_staff_ind...", 1件: overseas_staff_index.md単独)
  → LLM4 駐在員抽出(node 1789217622601)
    → 【事前抽出: 海外駐在員情報】(システムプロンプト冒頭に必須反映)
```
これはSKILL_Dify.mdの「Supplementary CASES and KNOWLEDGE search results
(large-file dataset)」の記述(cases_global_01.md/case_expert_index.md/
cases_apac_01.md/knowledge_untagged_01.mdは突出して大きいので別検索が要る)を
実装したものと確認。AIモデルはClaude Sonnet 4.6(Sonnet 5はVertex AIストリーミング
バグで不可、既知)。

**一見「重複」に見える理由**: cases_apac_01.mdは知識検索2(大容量ファイル一括)と
知識検索3(APAC専用、精度重視の個別検索)の両方に存在。overseas_staff_index.mdは
知識検索(メイン、一般検索でも拾えるようにするフォールバック)と知識検索4
(専用の確実な抽出ルート)の両方に存在。**どちらも削除するとLLM3/LLM4の事前抽出が
壊れるため、単純な「重複削除」の対象ではない**——中村さんに整理範囲を確認したところ
「今回は何もしない(現状維持)」との判断。

**次にこのプロジェクトのDify側ナレッジを更新する時の注意**:
- `knowledge_untagged_01.md`を再アップロードする際は**メインの"knowledge_consumer..."
  データセットではなく"cases_global_01.md..."という名前のデータセット(知識検索2)**に
  差し替えること。
- `cases_apac_01.md`を更新する際は**2箇所**(知識検索2内の1つ、および単独の
  "cases_apac_01.md..."データセット=知識検索3)両方に反映が必要。
- `overseas_staff_index.md`を更新する際も**2箇所**(メインの"knowledge_consumer..."
  データセット内、および単独の"overseas_staff_ind..."データセット=知識検索4)両方に
  反映が必要。
- `case_expert_index.md`と`cases_global_01.md`は知識検索2(1箇所のみ)。
- 上記以外(topic_expert_index.md含む)はメインデータセットの1箇所のみ。
- データセット名は全て自動生成のままで用途が名前から分からず紛らわしい
  (中村さんは「名前だけでも分かりやすくリネーム」を選択肢として提示されたが今回は
  見送り)。次にこの整理を持ちかけられたら、上記の対応関係表をそのまま提示できる。

## 2026-09-15(続き9): ChatGPT Skillのファイル差し替え作業で重大なヒヤリハット
「knowledge_*.md 7ファイルを修正版に差し替えて」との依頼を受け、ブラウザ自動操作
(port 9224, chatgpt-bot)でSkillエディタのファイル削除→再アップロードを実施。

**ヒヤリハット**: 隠しinput要素(`#upload-files`)に対して直接`setInputFiles()`する方式
(Playwrightでよく使う標準的手法)を使ったところ、**削除は確実に反映されるが再
アップロードがブラウザのリロード後に消えてしまう**という非対称な不具合に遭遇。
削除→即再アップロード→保存クリック→数秒待機、という手順を7ファイル分実行した後に
`page.reload()`で検証したところ、**7ファイル全てがSkillから消えている**ことが
判明した(一時的にKNOWLEDGEバケットが全滅する状態を作ってしまった)。

**原因と対処**: 可視の「アップロードする」ボタンをクリックし、Playwrightの
`page.waitForEvent('filechooser')`で開いたネイティブファイル選択ダイアログに対して
`fileChooser.setFiles()`する正规の方式に切り替えたところ、リロード後も確実に
永続化することを確認(1ファイルずつ「アップロード→保存クリック→reload→DOM確認」で
検証しながら7ファイル全て復旧・再確認済み)。隠しinputへの直接`setInputFiles()`は、
このSkillエディタでは(おそらくReact側のファイル選択イベントハンドラが実際のブラウザ
ネイティブファイル選択フローを前提にしており)保存トリガーが正しく発火しない、という
アプリ固有の癖と判明。

**教訓(重要、次回同種の作業で必ず踏まえること)**: Web UIでのファイルアップロード
自動化は、隠しinput要素への直接`setInputFiles()`ではなく、**可視のアップロードボタン
クリック+`page.waitForEvent('filechooser')`+`setFiles()`という正規のブラウザネイティブ
フローを再現する方式をデフォルトにすること**。特に「削除」を伴う差し替え作業では、
削除だけが先に確実に反映され、後続のアップロードが失敗する非対称なリスクがあるため、
**1件処理するごとに`page.reload()`で実際に永続化されたか確認してから次に進む**
慎重な手順が必須(バッチで全部やってから最後にまとめて確認、は危険)。

**最終確認結果**: knowledge_*.md 7ファイル全てSOURCEフィールド付きで正常復旧、
重複なし(各1件)、Skill全体のファイル数33件で整合性確認済み。SKILL.md・その他の
ファイルには影響なし。

## 2026-09-15(続き10): Dify側の反映完了(中村さん自身で実施)
中村さんがDify「GBC Agency OS」への修正版knowledge_*.md反映(knowledge_untagged_01.mdは
cases_global_01.md系データセットへ、他6ファイルはメインデータセットへ)を自身で完了。
本セッションのtopic_expert_index.md追加+KNOWLEDGEカードURL欠落修正+ChatGPT/Dify両反映は
これで一区切り。

## 2026-09-15(続き11): SKILL_Dify.mdの長さ整理を実施(ChatGPT版と同じ手法)
中村さんの依頼で、以前ChatGPT版SKILL.mdに適用した「ルール本体は簡潔に、経緯説明は
changelog.mdへ」という手法をSKILL_Dify.mdにも適用した。

**Before**: 679行・約49,000文字。「このデプロイにはreferences/フォルダが無い」という
同一の注意書きが6セクションに渡って繰り返され、各ルールに「(added DATE, from
incident...)」という経緯説明がインラインで付いていた。

**After**: 265行・約31,600文字(約35%削減)。
- 「references/フォルダなし・Web検索なし・PPTXテンプレートなし」という3つの構造的
  制約をAlways-on constraints内の1箇所(#5)に統合、各セクションでの重複記述を撤廃
- ChatGPT版とDify版で内容が完全に同一のセクション(3〜9、11)はSKILL.md側の既に
  圧縮済みの文言をそのまま流用(重複した圧縮作業を回避)
- 経緯説明はすべてchangelog.mdへ移動(Dify分岐の経緯・知識検索アーキテクチャ分割・
  Markdown出力コードフェンス問題・2026-09-15のライブ版乖離発見、の4エントリを新規追加)
- 機能的な差分(2つの事前抽出変数ブロック、{{#context#}}、Markdownエクスポーター
  ツール名、大容量ファイル専用検索セクション等)は一切失われていないことをgrepで
  逐一検証済み(Requirement A-H各1回、両変数ブロック各1回、全バケットファイル名、
  各種警告文の完全一致、等)

**新規ファイル**: `SKILL_Dify_for_paste.md`(252行、frontmatter+ローカル専用HTML
コメント除去済み、Difyへそのまま貼り付け可能)を生成し、これを開いて中村さんに提示。
Dify貼り付け時は今後もこのファイルを都度再生成する運用(前回のChatGPT版と同じパターン)。

**教訓の補強**: changelog.mdの冒頭説明を「SKILL.md用」から「SKILL.md/SKILL_Dify.md
共通」に更新。ChatGPT側はreferences/へアップロードするが、Dify側はreferences/概念
自体が無いためローカル専用(Claude Code/人間の参照用)である旨を明記。

## 2026-09-15: Global Department Index追加(グローバル対応部署一覧)
中村さんの依頼で、Agency OSに「グローバル対応部署」情報を追加。ソースは2つ:
(1) SharePoint「GlobalTeam」ページ(`https://esq365.sharepoint.com/sites/globalonedentsu/
SitePages/GlobalTeam.aspx`、Global Q編集部運営、8カテゴリー・31部署へのリンク一覧)、
(2) その元データであるMicrosoft Forms登録内容Excel(「グローバル関連組織紹介ページ
内容登録」、`esq365-my.sharepoint.com`上の個人OneDrive共有、47件の登録・更新、
2021-12〜2026-07、~37組織)。

**新しい技法の発見**: SharePoint共有リンク(`:x:/r/personal/.../file.xlsx?d=...&e=...`)を
そのまま開くとOffice Web Appのビューアーに飛ばされダウンロードイベントが発火しない。
`/_layouts/15/download.aspx?UniqueId=<ファイルのGUID>`形式のURLに変換して
`page.goto()`すると、Office Onlineを経由せず直接バイナリダウンロードがトリガーされる
(`page.goto()`が`page.goto: Download is starting`という例外を投げるのが成功のサイン、
try/exceptで捕捉しつつ`page.waitForEvent('download')`で拾う)。GUIDは他のDoc.aspx URL
(`sourcedoc=%7B<GUID>%7D`パラメータ)から抽出できる。今後SharePoint上のファイルを
Playwright経由で直接ダウンロードしたい場合はこの技法を再利用できる。

**マージロジック(決定的、推測なし)**: Formsの回答シートは同一組織が定期的に再登録する
構造で、内容を変更しない項目は文字通り「変更なし」と記入される慣習だった。
`generate_global_dept_pack.py`(GBC-Knowledge直下)では、組織名の完全一致(全角/半角
スペース正規化のみ)でグループ化し、「変更なし」値は前回の値を保持。組織名自体が
「変更なし」の行(1件のみ確認)は、メールアドレスで直前にその人が登録した組織名を
機械的に解決——内容の類似性から同一組織と推測することは一切していない(表記揺れの
異なる組織名同士、例えば「dentsu innovation initiative」と「電通イノベーション
イニシアティブ」は意図的に別エントリのまま、自動統合していない)。

**出力**: `output/agency_os_pack/experts/global_department_index.md`(約100KB)。
Part 1(SharePointに現在掲載中、カテゴリー別、31部署中23件がExcel内容にマッチ)は
`Global Department`として断定案内可。Part 2(Excel登録はあるが現行SharePoint一覧に
一致しない組織、14件、組織改編・改称・掲載終了の可能性)は留保表現必須。

**Skill反映**: SKILL.md(ChatGPT)/SKILL_Dify.md(Dify)両方に並行して6箇所ずつ反映
(bucket一覧・COMMON KNOWLEDGE TEST MODEのバケットリスト・Withholdingルール・
「Global department routing」使い方説明・新規**Requirement I**「該当する
Global Departmentを必ず紹介する」・Section 12月次更新セクション)。
[[feedback_agency_os_skillmd_multi_deployment_sync]]の教訓通り、SKILL_Dify.mdを
先に手動編集し、SKILL_Dify_for_paste.mdはそこからPythonスクリプトで機械的に
再生成(frontmatter+ローカル専用HTMLコメント除去)——手編集の二重管理によるドリフトを
防止。この過程で、SKILL_Dify.md内に元々あった「Client deliverable requirements A–H」
という古い参照(Section 10のPPTXフォールバック説明内、他のgrep対象から漏れていた
箇所)を発見し「A–I」に修正——Requirement追加時は`grep -n "A–H"`で全出現箇所を
確認してから完了とすべき教訓。`README.md`(`output/agency_os_pack/`)にも新bucketの
説明・再取得手順(`global_dept_source/scrape_global_team_page.js`/
`download_global_dept_registration.js`)を追加。changelog.mdに詳細記録済み。

**未完了**: ローカルファイルの更新のみで、実際のAgency OS拠点(ChatGPT Skill editor:
`https://chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080`、Dify:
`console.dj-dify.dentsu.jp`「GBC Agency OS」アプリ)への`global_department_index.md`
アップロードとSKILL.md/SKILL_Dify_for_paste.mdの反映は中村さん自身が実施する必要あり
(過去のtopic_expert_index追加時と同じ運用)。

**同日追記(訂正)**: 中村さんから「もうなくなってしまった組織もあるので、それは案内
しないで下さい」との指摘。当初設計はPart 2(現行SharePoint一覧に無い組織)を「留保付きで
案内」としていたが、これは廃止済み組織を案内してしまうリスクを残していた
(表記揺れによる不一致か、本当に廃止済みかを機械的に見分ける手段が無いため、
「良いヘッジ文言」では解決できない構造的な問題と判断)。SKILL.md/SKILL_Dify.md/
SKILL_Dify_for_paste.md/generate_global_dept_pack.py/global_department_index.md本体/
README.md全てを「Part 2は案内・推奨に一切使わない(留保付きでも不可、履歴保存のみ)」
に修正。詳細は[[feedback_dont_recommend_defunct_orgs]]およびchangelog.md
「2026-09-15 (same day, correction)」参照。

**同日追記2(ChatGPT側の既知バグ再発を確定)**: 「ユニ・チャームの海外向け契約交渉について
相談したい」をChatGPT Skillで試したところ検索が一切行われずヒアリング質問のみ返る
(Dify側は同じ質問で正しくGlobal Department/CASE/駐在員を返した)。これは2026-09-11・
2026-09-15午前に既に確認済みの「ChatGPT Instantモデルは内部ナレッジ検索ツールを
確実に呼ばない」バグの3回目の再発と判定。中村さんがChatGPT 5.5のreasoning effortを
**「高」(5段階中3段階目、中間)**に切り替えたところ即座に正しく検索・回答されることを
確認。以前は「Instant/Thinkingの二択」と理解していたが、実際は5段階のeffortセレクタで
あり、**「高」で動作確認済み(それ以下の「低」「中」は未検証)**。詳細は
[[feedback_agency_os_chatgpt_requires_thinking_model]]参照。次回同種の相談を
受けたら、まずeffort設定を疑うこと。

**同日追記3(閾値の断定を撤回)**: 中村さんが下から2番目のeffortでも正しく検索できることを
確認し、「一番下でも拾ってくることもあると思われるので、何が本当の要因かはまだはっきり
しません」とコメント。特定のeffort段階が「これなら確実」という閾値ではなく、確率的な
挙動(effortが高いほどツール呼び出しの信頼性が上がるが、保証ではない)と判断し、
memoryの記述を「◯段階で動作確認済み」という断定から「低いeffortはリスクが高い、
高いeffortはリスクが下がる、が保証ではない」という表現に修正済み。

## 2026-09-16: 中村さんからAgency OSの今後のTODO2件(未着手、書き留めのみ)
1. **dentsudot.comのレポート参照**: 海外電通の事例・分析レポートが豊富だが要ログイン。
   Agency OSから参照できるようにしたいとの要望。ログイン認証をどう扱うか(手動DL経由か、
   認証つきスクレイピングか)は未検討。
2. **Salesforce新規案件登録時の自動トリガー**: 新しい案件がSalesforceに登録されたら、
   自動的にAgency OSを動かしてアドバイスを出したい。実現には(a)Salesforce側の新規登録を
   検知する仕組み(Webhook/定期ポーリング)、(b)Agency OS(ChatGPT Skill/Dify)側をAPI越しに
   無人起動する方法、の両方が必要で、現状のAgency OSは対話ベース(手動プロンプト起動)
   のため無人自動実行の経路が無い。要設計検討。
次にAgency OSプロジェクトに触るときは、この2件が中村さんの希望に残っているかを
確認し、着手するかどうかを相談すること。

## 2026-09-16(同日): TODO1件目(dentsudot.com連携)完了
dentsudot.com(電通グローバルイントラ、News/Wins/Thought Leadership/Case Studies/Blogs構成、
SharePoint/SalesforceのSSOとは別の独自ログインが必要)にログイン後、サイト構造を調査。
`search-center`エンドポイントの`source`パラメータで、サイト全体検索(5,000件超)とは別に
Case Studies(source=109901、222件)とThought Leadership(source=102855、435件)という
**閉じた・扱いやすい件数の**コンテンツタイプが存在することを発見。各記事はMarket/Year/Brand/
Industry Vertical/Topicsの構造化タグ+Summary/Challenge/Strategy/Results形式の本文を持ち、
既存のcases_*.md/knowledge_*.mdと同じ設計パターンが流用可能と判断。

共有ブラウザ(port 9226、Playwright、DOMテキスト抽出のみ・スクリーンショット不使用)で全件
スクレイピング→`generate_dentsudot_pack.py`でMarkdown化し、`dentsudot_case_studies_01.md`
(932KB、業種別セクション)・`dentsudot_thought_leadership_01.md`(1.4MB、トピック別、
実際は全件Topics未設定のため「General」1セクションのみ)としてAgency OS Knowledge Packに追加。
SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.mdの5箇所(バケット一覧・Mandatory search
pattern・COMMON KNOWLEDGE TEST MODEリスト・使い方bullet・月次更新セクション)を更新、
changelog.md/README.mdにも記録済み。

**踏んだ罠**: スクレイピング中に共有ブラウザのタブが2回「Target page, context or browser
has been closed」で中断。1回目は原因不明の一過性障害、2回目は「古いbashリトライループの
停止漏れ→同じページに対して2つのnodeプロセスが同時にgoto()する競合」が真因と判明
(`ps aux`で二重プロセスを発見・強制終了して解消)。スクリプトを記事ID単位でresumable
(未処理分のみ再取得)に設計していたため、手動での再実行のみでデータ欠損・重複なく完走できた。
**教訓**: 長時間の共有ブラウザ自動化は必ずresumable設計にすること、バックグラウンドジョブの
リトライラッパーを使う際はps auxで二重起動していないか確認すること。

出力は当初、業種別/トピック別に33個の細分化ファイルへ分割する設計にしたが、コーパス規模
(合計約2.3MB)を踏まえ、既存のglobal_department_index.md等と同じ「単一ファイル+セクション
見出し」方式に作り直した。スクレイパー本体・ヘルパースクリプトは`dentsudot_source/`配下に
格納(既存の`global_dept_source/`と同じ配置ルール)。

**既知の残課題(未解決)**: (1)再取得のたびに人によるdentsudot.comへの手動サインインが必要
(SharePoint/Salesforceと異なる認証系のため自動ログイン未実装)、(2)更新頻度は未定、
(3)TODO2件目(Salesforce新規案件登録時のAgency OS自動起動)は今回未着手のまま。
実際のChatGPT Skill/Dify appへの新ファイルアップロード反映は、既存運用と同様
中村さん自身が実施する必要がある。

## 2026-09-17: dentsudot連携のDify反映は実は既に完了していたと判明
上記の「中村さん自身が実施する必要がある」という記述は前回セッション終了時点の想定
だったが、実際には中村さんご本人(または別セッション)が同日中(2026-09-16 17:57頃、
ローカルファイル完成のわずか数分後)にDify側の反映まで完了させていた。共有ブラウザ
(port 9227)で確認したところ: (1)「GBC Agency OS」LLMノードのSYSTEM promptは
SKILL_Dify_for_paste.mdの内容(dentsudotバケット・fabrication対策込み)と一致、
(2)ナレッジベース「knowledge_consumer...」データセットに
`dentsudot_case_studies_01.md`/`dentsudot_thought_leadership_01.md`が
2026/09/16 05:54 PMアップロード・「利用可能」ステータスで存在、(3)ワークフローは
「公開済み 13時間前」(=2026-09-16 17:57頃)。よってdentsudot連携のDify反映一式は
完了済み。work_status側の古い「Next: 中村さんが反映」という記述は本エントリで訂正。

実機での動作確認(Previewでの自動テストクエリ送信)は、類似した複数の入力欄
(LLMノード設定パネルのコンテキスト欄・Startノードのデバッグ用デフォルト値欄・
実際のチャット送信欄)をテキスト抽出だけで区別できず失敗(ワークフローは実行されず、
入力した文字列がStartノードの表示用デフォルト値欄に残っただけだった)。中村さんから
「画面キャプチャは使わないでください」との指摘も受けたため、それ以上のブラウザ試行
錯誤は打ち切り、残留文字列はクリア・ブラウザはオフスクリーンに復帰させた。教訓は
[[feedback_reduce_browser_automation_tokens]]に追記済み(静的な状態確認はテキスト
抽出で十分だが、複数の似た入力欄から正しい実行系を当てにいく動的な機能テストは
苦手なので、そこは中村さん自身に一言お願いするか、的を絞った1回のスクリーンショット
で入力欄を確定させてから操作する)。

**Next**: 実際にdentsudot事例が正しく引用され、2026-09-16に見つかった「捏造で穴埋め
する」不具合が再発していないかは、中村さんが実際のDify画面で一度試すか、次回このプロ
ジェクトに触るセッションで改めて検証する。Salesforce新規案件→Agency OS自動起動
(2つ目のTODO)は依然未着手。

## 2026-09-17(続き): 内部ファイル名/外部システムへの誘導バグを発見・修正・公開
中村さんが上記の反映結果を実際にテストし、「自動車業界の海外事例」への回答が
`topic_expert_index.md`/`tools.md`等の**内部ファイル名を名指しで直接照会するよう誘導**、
さらに`dentsudot.com`/`GBCarekoko`/SharePoint「GlobalTeam」へ**ユーザー自身が直接検索
するよう誘導**する不具合を報告(「URLは必須表示」「MDファイルはユーザーがアクセス
できないので不適切」)。既存のOffloadingルールが「バンドルファイルを引用に使うな」という
狭い範囲にしか触れておらず、ゼロヒット時にモデルが親切のつもりでファイル名やライブ
システムへの誘導文を生成することを防げていなかったのが原因。SKILL.md/SKILL_Dify.md/
SKILL_Dify_for_paste.mdのOffloadingルールを強化(内部ファイル名を一切出さない・外部/内部
ライブシステムへの自己検索を促さない・許される「次の一手」は今回の検索で実際に見つかった
人物/部署のみ)し、Dify本体のSYSTEM promptへ反映・公開まで完了。詳細・技術メモ(貼付/公開
操作にはブラウザを実際にオンスクリーン・フォアグラウンドにする必要がある、「公開する」
ボタンはメニューを開くだけで実際は「更新を公開」を追加クリックする必要がある、等)は
[[work_status/agency_os_dify_offloading_filename_leak_fix_20260917]]参照。

なお今回dentsudotの自動車事例がゼロヒットだった件は、`dentsudot_case_studies_01.md`
(790.9k語)/`dentsudot_thought_leadership_01.md`(887.4k語)という突出して大きい
2ファイルがメインデータセット(他17ファイルと共存)に同居しているためのTop-K競合が
原因の可能性が高く、根本修正には`cases_global_01.md`系と同様の専用データセット+
専用ノードへの分離が必要になりうる——これはキャンバス上のノード追加・配線作業なので、
着手前に中村さんの意向確認が必要(まだ未着手・未確認)。

## 2026-09-17(続き): dentsudot専用ノード追加+引用ルールの構造的整理
中村さんが「専用データセット+専用ノード」への分離を承認。データセット分離
(新規`ナレッジベース`作成・dentsudot 2ファイルの再アップロード)はClaude側が実施、
キャンバス上のノード追加・配線は中村さんが担当という分担で合意(ノード配線は
スクリーンショット多用になりやすく、中村さんもDify操作を覚えたい意向のため)。

実機再テストでもう1つのバグが発覚: CASE_ID 13014(GM Korea、`cases_apac_01.md`に
実在・正規のSALESFORCE_URL付き)が回答内で「(ナレッジ記録より)」「出典URL未掲載」に
格下げされていた(6件リストの4番目、1〜2番目は正しく引用)。中村さんから「指示文/
出力が長くなって省略されているなら構造改善も検討して」と要望を受け、単純な
ルール追記でなく構造的対応を実施: (1)「Equally binding failure modes」7項目を
4項目に統合し重複除去、事例注釈は全てchangelog.mdへ退避、(2)ルールAに
「CASE系レコード3件以上は表形式(案件名/CASE_ID/担当者/出典URL列)必須」を追加
——表形式なら空のURLセルが目視で一目瞭然になり、段落形式のように後半項目だけ
引用が雑になる現象を構造的に防止する狙い。SKILL_Dify.mdは278行/41.8KB→
277行/40.3KBと実質圧縮しつつ新ルールも追加できた。

中村さんが実施したDify側反映(SYSTEM prompt貼替+公開、dentsudot専用ノード追加・
配線)は完了・確認済みだが、途中でコード実行ノードのバグを1件発見: 中村さんの
1回目の修正がreturn文にのみ`(e or [])`を追加し関数シグネチャへの`e`引数追加を
忘れており(NameErrorでワークフロー全体が落ちる)、指摘後に
`def main(a: list, b: list, c: list, d: list, e: list) -> dict: return {"result":
(a or []) + (b or []) + (c or []) + (d or []) + (e or [])}`に修正、最終確認済み。

詳細・技術メモ(Difyのタブを長時間掴んだままだと自動保存/公開タイムスタンプが
古いまま返り続けることがある、reloadで解消する等)は
[[work_status/agency_os_dify_citation_completeness_and_dentsudot_dedicated_node_20260917]]参照。

Next: 中村さんが実機で再テストし、(1)表形式表示、(2)dentsudot事例が拾われるか、
(3)後半項目の引用省略が直っているか、を確認する。

## 2026-09-17(続き): Scope inflation(南アフリカへの偏り)修正v1→v2、PoC進行を決定
再テストで新たな不具合を発見: 「海外の自動車業界事例を教えて」という国指定なしの
クエリで、毎回faq.mdの南アフリカ/スズキ勉強会記録(担当:紙村、実質唯一の
「自動車マーケット」を含むFAQ)に引きずられ、無関係な他ケース(タイ・韓国等)まで
南アフリカ向けの示唆にこじつけていた。中村さんが同じ質問を毎回新規チャットで
送っていたことを確認済み(会話履歴の影響ではない)。プロンプト自体にも南アフリカの
例文は無い(grep確認済み)ため、データの疎さ(自動車系FAQが実質1件)が原因と特定。

対応は2段階: v1で新規「Scope inflation」ルール追加(単独ヒットで回答全体の
スコープを決め打ちしない)。再テストで「他バケット(海外駐在員)を南アフリカで
検索する」「独立見出しセクションになる」がまだ残ったため、v2でルールF
(海外駐在員検索)を「ユーザー自身の依頼文に出てくる国のみ対象、検索結果の
レコード内に出てくる国は対象外」と明確化、Scope inflationも「独立セクション
でなく既存セクション内の1行に留める」と具体化。3ファイル(SKILL.md/
SKILL_Dify.md/SKILL_Dify_for_paste.md)へ適用。

v2適用後、他ケースへのこじつけ・単独市場概況フル表は消滅、dentsudot専用ノードも
機能しAutomotiveタグ付き実例を正規URL付きで取得できることを確認。ただし
「検索サマリー行に国名が出る」「独立セクションになる」の2点は完全には解消せず
(LLMの指示遵守の限界と判断、これ以上の追い込みは収穫逓減)。中村さんが
「これでPoC進めます」と現状での運用開始を決定。詳細は
[[work_status/agency_os_dify_scope_inflation_fix_and_poc_go_20260917]]参照。

**この日のセッションで得た運用上の教訓**: (1)ブラウザ自動操作(Dify SYSTEM
prompt貼替・公開)は接続断続的に不安定になり、以降のSYSTEM prompt反映は
中村さんご本人が実施する運用に切替(トークン効率も良いと本人判断)。
(2)プロンプト修正は「ルール追記」より先に「本当にプロンプトの問題か
(データの疎さ・会話履歴・LLMの指示遵守限界ではないか)」を毎回切り分けてから
着手する方が手戻りが少ない。

Next: 追加のDify側微調整は中村さんの判断待ち(保留)。未着手の別TODO
(Salesforce新規案件→Agency OS自動起動)も引き続き保留。

## 2026-09-17〜18: 役員向け「Agency OS全体像」説明資料を新規作成(Artifact→PPTX)
中村さんの依頼で、役員にAgency OSの仕組み・データソース・更新方法・活用例を説明する資料を作成。

**進め方**: (1)まずArtifact(HTML図解ページ、`artifact-diagramming`スキル使用)で構成を素早く確認・反復、(2)承認後に同内容を電通GTMテンプレートのPPTXへ変換([[dentsu_pptx_template]]の色パレット・レイアウトカタログを使用)。python-pptxで手組みの図解(4段階フロー図、チーム編成フロー図)を構築、フォントサイズは中村さん指定の「本文18pt以上・注意書き9pt以上」を全スライドで厳守(qlmanageで1枚ずつレンダリング確認、[[feedback_pptx_visual_qa_method]])。

**データソースの見せ方で重要な学び**: 当初「社内資料」等の抽象的なラベルで書いていたが、中村さんから「知見活用が課題の会社なので、使っているソースはもっと具体的に・小分けにして、多くの情報を使っていることをアピールしたい」と明確な方向修正があった。GBCアレココ/Global Q/Salesforce/dentsudot.comという実名+具体的な内訳(件数付き)に書き直した。**教訓: 「データソースを使っている」ことを見せる資料では、抽象化・要約するより、実名を出して細かく分解する方が説得力が上がる場合がある**(通常の「簡潔に」という原則と逆方向になるケース)。

Web検索(ChatGPT Skill限定、Difyには非搭載)は他4システムと違い更新パイプラインを経由しない「相談ごとのリアルタイム検索」という設計的に異なる性質を持つため、図解上も点線+別経路で分離して描いた。

**活用イメージの実例化**: 中村さんが実際のChatGPT共有リンク4件(提案ブリーフ例/事例依頼例/契約相談例/エキスパート検索例)を提示。共有リンクはこのMacの共有ブラウザ(port 9229、`chatgpt-work-bot`専用プロファイル、[[chatgpt_web_automation]])経由でテキスト抽出して内容を把握した(社外からは403、workspace内ログイン済みセッションなら閲覧可)。

**役員限定資料ならではの2つの判断**(詳細は新規メモリ[[feedback_executive_deck_disclosure_and_brevity]]参照):
1. 実クライアント名(Acecook Vietnam、ユニ・チャーム)や実際の契約交渉詳細を含む共有リンクURLをそのまま資料に掲載してよいと中村さんが即答で承認(通常の[[feedback_gbc_ai_material_authoring_rules]]の匿名化方針とは逆方向— 対象読者が役員限定だから)。
2. 中村さんが最終的に、各図解に付けていた注意書き・補足キャプション(手動反映・PoC運用中等の注記)を全て削除。「役員にはあまり意味がない」との理由。実務者向け現状スナップショット文書とは異なる基準。

**最終成果物**: `Agency_OS_全体像_20260917.pptx`(電通GTMテンプレート、当初15枚→中村さんの編集で14枚、「更新の仕組み」スライドを削除)。保存先はこのプロジェクトのルート直下(`GBC-Knowledge/`と同じ`20260814GBC知見集約プロジェクト/`フォルダ)。作成したArtifact本体(Web版の同内容)は中村さんのclaude.aiアカウントに別途公開済み。

## 2026-09-29: 電通クレデンシャル生成機能(フェーズ1)を新規実装

中村さんの依頼で、Agency OSがクライアント向け「電通クレデンシャル」(会社紹介資料)を業種・地域に応じてカスタマイズ生成できる機能に着手。brainstorming→設計書(`credentials_pack_design.md`)→実装計画(`credentials_pack_phase1_implementation_plan.md`)→executing-plansで実装、という一連のプロセスを踏んだ。**このプロジェクトフォルダはgitリポジトリではない**ため、executing-plansのgit worktree/sdd-workspace等のスクリプトは使えず、手書きMarkdown台帳(`credentials_pack_phase1_ledger.md`)で進捗管理・セルフレビューを代替した(サブエージェントレビューの代わり)。同様の非gitプロジェクトでexecuting-plansを使う際はこのパターンを再利用できる。

### スコープ全体像(12の情報軸、設計段階で洗い出し)
過去のクレデンシャル資料`DentsuCredentialGBC_Master.pptx`(2020年版、69スライド、Dentsu Aegis Network当時のもので数値は古いが構成の型として有用)を分析し、会社規模・地域別売上構成比・展開国リスト・ブランドポートフォリオ・グローバルクライアントリスト・年表・事例・Vision/Mission/マテリアリティ・経営戦略・組織体制、の12軸に整理。フェーズ1(会社規模・受賞歴・海外事例)のみ今回実装、フェーズ2(ブランド紹介・年表)以降は未着手。

### 調査で判明した新規データソース
- **受賞歴**: `dentsu.co.jp/aboutus/introduction.html`(「広告賞受賞歴」ページ)。静的HTML、ログイン不要、更新日明記("n年n月n日現在")。カンヌライオンズ・D&AD等7種(海外)+TCC等5種(国内)を表形式で掲載。
- **会社規模ファクト**: `group.dentsu.com/en/sustainability/reports/`のIntegrated Report PDF(毎年ファイル名が変わる——2024年は"ESG Data Book"、2025年以降"Non-financial Databook"に改名された実績があるため、**固定URLをハードコードせず毎回インデックスページから発見する設計が必須**)。
- **公表可能な海外事例**: `lovethework.com`(Cannes Lions/WARC運営の業界横断アーカイブ、25万件超、ログイン済み確認済み)。代理店名(DENTSU/CARAT/ISOBAR/IPROSPECT/MERKLE/DENTSU X)で検索・フィルタ可能。**このPackはクレデンシャル専用ではなく通常のAgency OS事例検索にも使う**という中村さんの明示指示あり。
- **経営戦略(中期経営計画・海外戦略)**: 当初「自動取得不可、手動のみ」としていたが、中村さんの指摘で`group.dentsu.com/jp/ir/library/`(決算説明会資料・中期経営計画アップデート・統合レポート)から取得可能と判明、フェーズ3対象に格上げ(未実装)。
- **Vision/Mission**: `https://www.group.dentsu.com/jp/brand/`(中村さんから提示、フェーズ3未着手)。
- **グローバルクライアントリスト**: Salesforceの使用を中村さんが明示的に禁止、代替情報源未定のまま保留。

### 実装したパイプライン(6タスク、全て動作確認済み)
1. `credentials_source/scrape_awards_page.py` — 受賞歴スクレイパー(BeautifulSoup)
2. `credentials_source/fetch_integrated_report_facts.py` — IR PDFから会社規模ファクトを抽出(PyMuPDF)
3. `generate_credentials_facts_pack.py` — 1+2をMarkdown Pack化(`output/agency_os_pack/knowledge/credentials_facts_01.md`)
4. `lovethework_source/scrape_lovethework.js`(`~/.local/share/claude-playwright/`にも複製) — lovethework.comスクレイパー(Playwright、共有ブラウザCDP port 9226)
5. `generate_lovethework_pack.py` — Markdown Pack化(`output/agency_os_pack/knowledge/lovethework_case_studies_01.md`)
6. SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.mdへのバケット統合(4箇所ずつ)+changelog.md記録

### 実装中に発見・修正した技術的な罠(次回同種の作業をする際の参考)
- **会社Mac(d14461)の既知SSL証明書問題**が`group.dentsu.com`への`requests`通信でも発生([[feedback_d14461_python_https_cert_verify_use_curl]]と同一パターン、ただし同じ会社Macから`dentsu.co.jp`へは`requests`が問題なく成功した——**発生するかどうかはドメイン依存で予測できないので、新しいAPIエンドポイントを叩く前に必ず素朴な`requests.get`を試し、失敗したらcurlに切り替える**、という順序が結果的に正しかった)
- **PDFキーワード抽出で最初のマッチを使うと誤爆する**: `pattern.search()`(1件目のマッチ)は、統合レポートp.3の本命統計「Approx. 67,000 Employees」より先に、本文中の脇道的な言及「roughly 5,400 employees are engaged in company-wide functions」を拾ってしまった。**マッチ前後の窓内にある最大の数値をスコアとして最良マッチを選ぶ**(`best_match()`)方式に変更して解決。同種のキーワード検索ベースPDF抽出をする際は、必ず「最初のヒットが本当に欲しい情報か」を疑うこと。
- **「非公表」を「0件」と表記するのは中村さんに明確に誤りと指摘された**: 数値の0(ゼロという事実)と、情報が非公開であること、は全く違う意味。データパイプラインで「確認したが見つからなかった」場合は、黙って省略せず(省略すると「確認し忘れた」のか「確認したが無かった」のか区別できない)、かつ「0」でもなく、明示的に「ー(非公表)」として記録・表示する設計にした。この原則は本プロジェクト限定ではなく汎用的なデータ表現の教訓として[[feedback_non_disclosed_vs_zero]]に別途保存。
- **Difyの検索性能は「専用データセット化」だけでは解決しないことがある**: 2026-09-17のdentsudot専用データセット化の実績([[gbc_intelligence_engine_project]]同日記載)を踏襲し、`credentials_facts_01.md`+`lovethework_case_studies_01.md`を新規専用データセット+専用ノードに分離(役割分担: Claude側がデータセット作成・ファイルアップロード、中村さんがキャンバスのノード追加・配線・変数集約器`main()`への引数追加・公開)。結果、`lovethework_case_studies_01.md`(134件、短い事例カード)は解決したが、`credentials_facts_01.md`(当初23カード、うち会社概要ファクトがPDFページ全文=2,000〜4,000字超)は依然ヒットしなかった。**原因は同一データセット内で長すぎるカードが短いカードに埋もれること**と判断し、VERBATIM_QUOTEをページ全文からマッチ箇所前後500字の抜粋に短縮(52KB→19.7KB)。原文ママ引用ルールは「範囲を絞るだけで言い換えない」ことで維持。この短縮版の再アップロードは中村さんに依頼(自動化での削除→再アップロードがChatGPT Skillエディタ側でUI操作の特定に失敗したため)。**教訓: Difyの検索改善は「専用データセット化」の次に「カード自体の長さ」も疑うべき**。
- **lovethework.comのpaywall表示は間欠的な現象だった**: 当初「DENTSU Xブランドは24件中24件が有料会員限定、アカウントの購読制限」と誤って判断したが、時間を置いて再試行したところ24件中23件が正常取得できた。中村さんの説明(会社Macは中村さんのスマホテザリング経由でネットワークに出ている構成のため、電車移動中で接続不安定だった)が濃厚な原因。**教訓: 初回の失敗パターンをすぐに固定的な制約と断定せず、時間を置いた再試行で切り分けるべき**。

### 現在の状態(2026-09-29セッション終了時点、以下2026-09-30セッションで更新)
- `credentials_facts_01.md`(19.7KB、短縮版)・`lovethework_case_studies_01.md`(134件)ともChatGPT Skill・Dify両方にアップロード済み、SKILL.md系3ファイルも反映・公開済み(中村さんが実施)
- ChatGPT側のテスト結果は良好(会社概要・受賞歴・「非公表」表記とも正確、CARATのlovethework事例もいずれ再テスト予定)
- Dify側は`lovethework_case_studies_01.md`の検索は成功確認済み。`credentials_facts_01.md`の短縮版アップロード後の再テストは次回セッション待ち
- Difyワークスペース「dJ-Dify_共通プレイグラウンド」に「有効期限21日」の表示(プレミアムプラン期限切れバッジ)を発見。全社共有サンドボックスであることは以前から判明していたが、プラン切れの緊急性が新たに判明。中村さんが管理者に確認予定(未対応)
- フェーズ2(ブランドポートフォリオ・年表)・フェーズ3(組織体制・Vision/Mission・経営戦略)は未着手。グローバルクライアントリストは代替情報源未定のまま保留

## 2026-09-30セッション: Phase 2・Phase 3完成 + PoC実地テストで見つかった3つの不具合を修正

**Phase 2(軸⑥ブランド紹介・軸⑧展開国リスト・軸⑨年表)完了**: 軸⑥はdentsudot.com「Brands」ページ(`SitePageModern/194188/brands`、11ブランドの公式紹介文+URL、当初想定の「News/Wins」区分は存在しなかった)。軸⑧は「約120カ国・地域」の集計値のみで打ち切り(信頼できる全展開国一覧は見つからず)。軸⑨は`group.dentsu.com/en/about-us/history/`(1901-2024年、電通自身が選別済みの公式沿革11件)+`en/news/release/`(2025年以降の全ニュースリリース119件、大きな出来事の選別はAgency OS自身に判断させる方針)。ニュースリリースの「年」フィルタはJS/AJAX処理でcurl不可、Playwrightで2025年分のみ一度きり遡って取得(`scrape_news_releases_backfill.js`)、以降は軽量curl版(`fetch_recent_news.py`)で追記していく設計。

**Phase 3(軸⑩組織構造・軸⑪企業理念/マネジメントチーム・軸⑫経営戦略)完了**: 軸⑩は`group.dentsu.com/jp/group/`(体制図、4地域統括、国内約140社・海外約540社)。軸⑪はNORTHSTAR(`/jp/brand/`+`/jp/brand/8ways.html`)、マテリアリティ(`/jp/philosophy/materiality.html`、4カテゴリ17項目)、マネジメントチーム21名(`/jp/about-us/group-management-team.html`、`div.teammember`構造)。軸⑫は`/jp/about-us/mtmp.html`(中期経営計画アップデート2026-2028)。`credentials_facts_01.md`は最終的に144KB(全10セクション)まで成長したが、1カードあたりのサイズは小さく保たれておりDify側の検索問題は再発しなかった。詳細な実装ログは`credentials_pack_phase1_ledger.md`(プロジェクトフォルダ直下)参照。

**PoC実地テストで発見・修正した3つの不具合**(中村さんが実際にChatGPT/Difyへ模擬クレデンシャル依頼を投げて発覚):

1. **SKILL.mdの「Once approved, Claude Code builds the PPTX」が誤り**: Claude Codeは全局員が使えるツールではない([[dentsu_claude_code_it_application_process]])。これまでもPPTX出力はChatGPT/Dify自身が行ってきた実態と矛盾していた。SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.md全てで「build the PPTX yourself」(Dify版は無地出力である旨も明記)に修正し、トリガー判定も「credentials/company-profile」という単語ではなくプロンプト内容・意図から判断するよう明記。changelog.mdに記録済み。**教訓: Skillの振る舞い記述に、ユーザー集団の実際のツールアクセス状況と矛盾する前提(この場合Claude Code)を書いてしまわないよう注意。**

2. **Difyのトップコンテンツ検索設定(`credentials_facts_01.md`が入っているデータセット、id `70359cd4-c6b6-4332-a80a-8653894382a5`)でトップK=3・スコア閾値0.5という初期設定のまま放置されていた**。単一トピックのクエリでは問題なかったが、「クレデンシャル資料を作りたい」のような複合的・広い質問では、ファイル冒頭の「このファイルの性格」説明文(意味的に広いクエリと相性が良い)が上位を占め、肝心の会社規模数値(従業員数・売上高・地域別構成比)が一切コンテキストに渡らず、**モデルがそれらしい数字を捏造してVERBATIM_QUOTEと偽って提示する**という重大な信頼性事故が発生(実際の値67,000名/1,197.5十億円/Japan42%に対し、捏造値56,000名/7,194億円/22.4%)。トップKを10に引き上げて改善したが、**Dify UIには埋め込みモデルのmax_tokensに連動したトップK上限(この設定では10)があり、それ以上は上げられないと判明**。10でもなお広範な複合質問では核心数値が競合に負けて漏れることがあり、恒久対策(ファイル冒頭説明文の短縮、または既存の「事前抽出」固定注入ブロックと同じ仕組みで会社規模数値を検索に依存せず常時注入する)は未実施の宿題として残っている。**教訓: Difyでの「検索したはずが数字が間違っている」系の不具合は、まずヒットテストで実際に何が取得されているか確認し、取得されていなければ捏造を疑う。トップK設定には埋め込みモデル依存の上限があることも念頭に置く。**

3. **`knowledge_untagged_01.md`(GBC Knowledge Pack本体、14,897件の一般知見カードの一部)に、3件の相互に矛盾する古い「会社規模」知見カード**(2023年4月/2025年10月/2025年9月の異なる古い営業資料から抽出、68,000/69,000/71,000名・11,000社以上、といった互いに不一致な数値)が混入しており、新しい`credentials_facts_01.md`の正確な数値(67,000名・クライアント数非公表)と競合し混乱の元になっていた。中村さんの指示で削除(ID: GBC-422A69E284E0/GBC-5DCE7C988F5F/GBC-028627EC8B33)。**対応方法**: `output/knowledge_index.db`・`gpt_integration/knowledge_index.db`両方をバックアップ後にDELETE(将来のパイプライン再生成でも復活しないように)、かつ現在デプロイ中の出力ファイル`output/agency_os_pack/knowledge/knowledge_untagged_01.md`を直接編集して該当3ブロックを除去(`generate_agency_os_pack.py`を実際に再実行しようとしたところ、DBスキーマに`v2_quality_bucket`列が無く実行不可と判明 — 別途保留中のStage A/B品質改善パイプラインのDB移行(`migrate_v2_schema.py`)が未適用のままであることが原因。**今後Packを正式に月次更新する際は、先にこのDB移行を解決する必要がある**、これも宿題)。
   - この修正版`knowledge_untagged_01.md`の再アップロード時、**Dify側で正しい置き場所を誤りかけた事故が発生**: このファイルはSKILL_Dify.mdの「Supplementary CASES and KNOWLEDGE search results (large-file dataset)」セクション(`{{#context#}}`変数で読み込まれる、`cases_global_01.md`/`case_expert_index.md`/`cases_apac_01.md`と同じ専用の「大容量ファイル」データセット)に属するべきだが、中村さんが最初「knowledge_consumer...」という別のデータセット(通常の知識検索ノードが見る側)に新規追加してしまった。ヒットテストで発見・`cases_global_01...`という名前のデータセット(id `0722efab-946e-48f7-b6c4-db168eca45bf`)へ移動して解決。**教訓: 「大容量ファイル専用の別データセット」という設計(SKILL_Dify.md 275-281行目)を忘れないこと。ファイルが「見当たらない」場合、単純に無いのではなく別の専用データセットに属している可能性を先に疑う。**

**次にこのプロジェクトに触るときの宿題**: (1)Dify検索の恒久対策(会社規模数値の固定注入 or ファイル冒頭説明文の短縮)、(2)`generate_agency_os_pack.py`のDBスキーマ不整合(`v2_quality_bucket`列)の解消、(3)軸⑦(グローバルクライアントリスト)の上司確認結果待ち(`credentials_pack_open_questions_for_manager.md`)、(4)軸⑥のブランド別人数・展開国数の情報レベル不揃いについても同じく上司確認待ち、(5)ChatGPT側のPPTXデザイン品質改善 — **同日セッション後半で対応済み、下記参照**。

## 2026-09-30セッション(続き): デザインパターン追加 + 「レシピ+データ」新アーキテクチャ + ChatGPTアップロード制限の発見 + 生成時捏造パターンの発見

**(5)のデザイン品質改善を実施**: 中村さんから実際のサンプル資料(`dentsuグループクレデンシャル（海外ネットワーク部分増補版）Jul2023.pdf`、OneDrive GBCアレココ)を受領、PyMuPDFで画像化して視覚確認(poppler未インストールのためpdftoppm不可、fitzの`get_pixmap()`で代替)。6パターン(統計サマリータイル、組織図ボックス+コネクタ、ブランドランキングカード、マネジメントチーム顔写真グリッド、地域別国名マップ、3Dリボン年表)を確認し、`deck-production.md`に「Credentials/company-profile deck patterns」節として、実際のpython-pptx実装方針(色は元サンプルの紺色系ではなく必ずテンプレート正規パレット使用)を追加。

**新アーキテクチャ「レシピ+データ」の発見・実証**: 中村さんから、OneDrive共有フォルダ「GBC - 02．クレデン共有チャネル」(国別広告事情レポート・過去クライアント提案書等、多数・一部1GB超)も情報源にしたいとの提案。当初「Claude Codeが都度参照」を提案したが、**局員はChatGPT/Dify/Copilotしか使えずClaude Code前提の設計は成立しないと中村さんに訂正された**(重要な教訓、[[dentsu_claude_code_it_application_process]]と整合)。さらに検討する中で、**ChatGPT Skillエディタの「アップロード」ボタンが最近の仕様変更で「新しいテキストファイル」作成しか選べなくなっており、新規バイナリファイル(PPTX/画像)の直接アップロードができなくなっていることが判明**(ドラッグ&ドロップ・既存ファイル差し替えメニューも中村さんが試したが不可)。

この制約を踏まえ、**個別スライドをPPTXファイルとしてバンドルする方式は断念**し、代わりに「(a)過去資料の中身(データ)だけをMarkdownカード化 → (b)`deck-production.md`に蓄積した描画レシピで都度Code Interpreterが組み立て直す」という方式を採用。画像が必要な場合の経路を2つ実証:
1. **チャット添付+その場で使用**: 実際の顔写真(佐野傑CEO、group.dentsu.comより取得、400x400にリサイズ)をチャット添付→Code Interpreterが`dentsu_gtm_template_clean.pptx`の「1x headshot-design」レイアウトへ`insert_picture`で配置。生成物を検証しレイアウト総数70(本物のテンプレート)・埋め込み画像がバイト単位で一致、を確認(この時点では成功)。
2. **base64テキストとして恒久バンドル**: base64エンコード→デコード→ファイル保存→読み込みの往復と、1x1赤ピクセル画像の新規生成→python-pptxでのスライド埋め込みを、それぞれ実際に検証(いずれも成功、テキストアップロードは制限を受けないため実現可能)。

新バケット`credentials_slide_library_01.md`を追加(OneDriveの`20260128 Dentsu international business outline.pptx`から3件を試験抽出: グローバルマネジメントのタイプ(2x2マトリクス)、Dentsu In-Out体制、A社匿名化ケーススタディ)。`deck-production.md`に2x2マトリクス・多者間フロー図のレシピと「Slide library (recipe + data)」節を追加。SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.mdのバケット一覧4箇所全てに反映。Difyヒットテストで新バケットの検索成功を確認済み(スコア0.53/0.46)。

**セッション終盤の実地テストで新たに2つの問題を発見**:
1. **テンプレート不使用が再発(未解決)**: デザインパターン追加後も、依頼によっては相変わらず`dentsu_gtm_template_clean.pptx`を開かず自由描画(レイアウト名「DEFAULT」、埋め込み画像0件)になることがある。原因未特定、次回優先的に切り分けが必要(Needs Review未承認の可能性を最初に疑う)。
2. **生成時捏造という新パターンを発見(重大、対応済み)**: COMMON KNOWLEDGE TEST MODEでのテキスト検索は`credentials-slide-inout-structure`カードを正確に引用したが、直後に「これをスライドにして」と頼んだ途端、3段階のシンプルなフローが、存在しない組織名(「BP局/DJN」「GBC PMO」「1CRP/5CRP」)や4段階プロセスを伴う5ボックスの図に膨らまされ、「出典：社内GBC Knowledge Pack」と偽って表示された。検索は正確でも生成(スライド化)の瞬間に捏造が起きるという、Dify側のトップK不足による捏造とは別系統の失敗パターン。SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.md/deck-production.mdに「カードが名指ししている要素だけを描画し、豊かに見せるための創作をしない」旨を明記して対応済み。汎用的な教訓として`feedback_generation_time_diagram_fabrication.md`に保存。

**このセッション終了時点の宿題(次回優先順位)**: (1)テンプレート不使用の再発原因調査(未着手)、(2)Dify検索の恒久対策(会社規模数値の固定注入等、未着手)、(3)`generate_agency_os_pack.py`のDBスキーマ不整合解消(未着手)、(4)OneDriveの残り大量ファイル(一部1GB超)の処理方針検討 — 中村さんは処理量次第で個人Windows機のOllamaへの分担も検討中、(5)軸⑦(グローバルクライアントリスト)・軸⑥の情報レベル不揃いは上司確認結果待ち。
- **次にこのプロジェクトに触るときは**: (1)`credentials_facts_01.md`短縮版のDify再テスト結果を確認、(2)Difyワークスペースのプラン期限対応状況を確認、(3)フェーズ2着手の要否を中村さんに確認、の順で状況把握すること

## 2026-09-30セッション(続き2): 宿題(2)Dify検索の恒久対策・(3)DBスキーマ不整合を解消
中村さんの指示で、直前セッションの宿題リストのうち(2)(3)に着手(実装済み、詳細ログは`work_status/gbc_intelligence_engine_credentials_pack_permanent_fixes_20260930.md`)。

**宿題(2)の実態調査で判明した新事実**: `credentials_facts_01.md`が「検索されにくい」原因は、当初想定していた「トップK設定」だけでなく、**`fetch_integrated_report_facts.py`の`net_revenue`正規表現が緩すぎるという実データ上のバグ**だったことが判明。「net revenue」という語だけで59ページ中7ページにヒットしており、うち6ページ(AI活用事例・UEFAスポンサーシップ・完成車サイト事例・財務諸表等)は本文中に偶然その語が出てくるだけの無関係な地の文で、p.3の本当の見出し数値(1,197.5 billion yen)と同じ「売上高」ラベルのカードとして混入し、Dify検索でTop-Kを奪い合っていた。見出し数値に直接隣接する箇所のみにマッチを絞る正規表現に修正し、7ページ→1ページに正常化。あわせて`EXCERPT_CONTEXT_CHARS`を500→250字に縮小(実測で67,000名/1,197.5十億円/Japan42%・Americas26%・EMEA23%・APAC9%/120カ国、全ての核心数値が窓内に残ることを確認済み)。`generate_credentials_facts_pack.py`のファイル冒頭説明文(「取得方法・更新」という開発者向けメタ情報を含む4段落、1,434字)も、Agency OSの回答生成には不要と判断し491字に短縮。結果、会社概要ファクトカードが12件→6件に整理された。ローカルの`output/agency_os_pack/knowledge/credentials_facts_01.md`は更新済みだが、**ChatGPT Skill・Dify両方への再アップロードは中村さんの手動作業として引き続き必要**(役割分担は既存踏襲)。

**宿題(3)**: `migrate_v2_schema.py --allow-production`を本番DB(`output/knowledge_index.db`)に適用(事前にコピーで試験実行→問題なし確認、本番はバックアップ後に実行)。300件のStage A/Bサンプルのみ追加更新、既存14,597件はNULLのまま無変更(2026-08-27決定の追加型設計通り)。これにより`generate_agency_os_pack.py`のクラッシュ原因(`v2_quality_bucket`列不存在によるKeyError)が解消し、poc/full両モードとも全Validation項目OKで生成できることを確認。QUARANTINE21件の除外、および以前手動削除した汚染カード3件(GBC-422A69E284E0等)が再生成後も正しく非表示のままであることも確認済み。ローカルの`output/agency_os_pack/`(POC)はこの修正込みで再生成・上書き済み(旧版は`_backups_20260930/`にバックアップ)。**FULL DB本実行(残14,597件へのStage A/B適用、qwen3.8:27b・Windows機・約80時間)は今回のスコープ外のまま**、引き続き中村さんの判断待ち。

**次にこのプロジェクトに触るときの宿題(更新)**: (1)`credentials_facts_01.md`更新版のChatGPT Skill・Dify再アップロード+会社規模数値の検索再テスト、(2)テンプレート不使用の再発原因調査(未着手のまま)、(3)Difyワークスペースのプラン期限対応状況の確認、(4)OneDriveの残り大量ファイル処理方針、(5)軸⑦・軸⑥の上司確認結果待ち、(6)FULL DB本実行の要否を中村さんに確認。

## 2026-09-30セッション(続き3): 中村さんの再アップロード後にhitTestingで再検証 → コード修正だけでは不十分と確定
中村さんが`credentials_facts_01.md`をDifyへ再アップロード完了と報告。共有ブラウザ(port 9226)経由でDifyのhitTesting(検索テスト)ページに直接アクセスし、2026-09-29に実際に事故を起こしたのと同一の広いクエリ、および「電通グループの従業員数と売上高を教えてください」という直接的なクエリの両方でTop10チャンクを確認した。

**結果(重要)**: 今回のコード修正(ノイズ除去・冒頭説明文短縮)後も、見出し数値(67,000名/1,197.5十億円/地域別%/120カ国)を含むカードはどちらのクエリでもTop10に一切入らなかった。代わりに財務目標KPI(2028年度オペレーティング・マージン16%等)・経営理念NORTHSTAR・組織図(680社体制)・マネジメントチーム個別氏名カード等、同じファイル内の他セクションが上位を占めた。`credentials_facts_01.md`が113.9k words(会社規模ファクト以外に受賞歴・ブランド・年表・組織・理念・経営戦略・マネジメントチームを含む12軸の統合ファイル)であるため、TopK=10の上限下では狭い数値カードが同じファイル内の他セクションとの競合に**構造的に**負け続けることを実データで確認した。

**結論**: コード側のノイズ除去(宿題2の対応)は必要な前提条件だったが、それだけでは不十分。[[feedback_dify_retrieval_starvation_causes_fabrication]]で以前から提案されていた「事前抽出固定注入」(CASE/海外駐在員と同じ、検索を経由せずワークフローに直接注入する方式)が、選択肢の一つではなく**実際に必要**と確定した。

中村さんの代わりに準備できる範囲として、注入用テキストブロックを`credentials_source/company_scale_fixed_injection_block.txt`に作成済み(SKILL_Dify_for_paste.mdの既存2ブロックと同じ書式、検証済み数値5項目: 従業員数・売上高・地域別売上構成比・展開国数・クライアント数非公表)。Difyキャンバスへのノード追加・配線(既存のCASE/海外駐在員ノードと同じパターンで複製)は既存の役割分担によりまだ未実施。アプリ一覧から「GBC Agency OS」ワークフロー編集画面への直接URL遷移はDOM調査・複数回のクリック試行でも特定できず(SPAの内部ルーティングのため)、それ以上のGUI操作の深追いはトークン消費に見合わないと判断し中断した。

**次にこのプロジェクトに触るときの宿題(再更新)**: (1)`company_scale_fixed_injection_block.txt`の内容を中村さんに確認してもらい、Difyキャンバスに3つ目の事前抽出ノードを追加・配線 → SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.mdに3つ目の【事前抽出】ブロックを追記(中村さんの公開作業と合わせて実施)、(2)ChatGPT Skill側(こちらはDifyのTopK問題と無縁のはずだが、同じ113.9k words統合ファイルである以上、埋め込み検索の粒度次第で同様の問題が起きうるため要確認)、(3)テンプレート不使用の再発原因調査(未着手のまま)、(4)Difyワークスペースのプラン期限対応状況の確認、(5)OneDriveの残り大量ファイル処理方針、(6)軸⑦・軸⑥の上司確認結果待ち、(7)FULL DB本実行の要否を中村さんに確認。
