# Agency OS Dify — 検索クエリ用ブリーフ要約ステップ(次のチャットへ引き継ぎ)

## 2026-09-12T18:00:00+09:00 (approx)
Status: pending(未着手、次の新規チャットで実施予定)
What: [[work_status/agency_os_dify_retrieval_architecture_split_20260912]]で変数集約器導入まで完了した後、
中村さんが実ブリーフ(Acecook Vietnam)でテストしたところ、CASES/KNOWLEDGE/overseas_staff_index全てが
「該当なし」と報告される問題が再発した。Claudeが調査した結果、**アーキテクチャ自体は正常**(Preview機能で
同じ内容を短い直接質問でテストしたところ、CASE_ID 1200(実URL付き)・Knowledge Card・駐在員テーブル
(伊藤広貴/野口紗知子等、ホーチミン)全て正しく表示された)と判明。

## 根本原因(推定、高確度)
知識検索のクエリテキストは`テンプレート`ノードでJinja結合された`sys.query + テキスト抽出.text(添付
ファイル全文、2600文字超)`。ブリーフ全文をまるごとベクトル検索のクエリに使うと、日付・宛名・定型文等の
ノイズでクライアント名/国名等の核心キーワードの重みが薄まり、検索精度が落ちる(ベクトル検索の一般的な
弱点)。Claudeが同じ内容を「Acecook Vietnamのプロジェクトベース移行について...」という短い直接質問で
テストしたところ正常にヒットしたことから、クエリの長さ・ノイズが原因と特定。

## 合意した対応方針(次のチャットで実装)
新規LLMノード「ブリーフ要約」を追加し、検索クエリ専用に添付資料を600字程度へ圧縮する:

1. **配置**: `テキスト抽出`ノードの直後、`テンプレート`ノードの前に新規LLMノードを挿入
   (`スタート→テキスト抽出→[ブリーフ要約]→テンプレート→知識検索/知識検索2→変数集約器→LLM→回答`)
2. **入力**: `テキスト抽出.text`(Array[String])
3. **プロンプト方針**: 「以下の資料から、検索に使うクライアント名・国/地域・業界・案件種別・核心的な
   課題を600字以内で抽出してください。日付・宛名・定型文は除外し、検索キーワードとして機能する
   密度の高い文章にすること」
4. **テンプレートノードの修正**: `doc_text`変数の参照元を`テキスト抽出.text`から`ブリーフ要約.output`
   (String、単数)に差し替え。既存のJinjaコード(`{% for t in doc_text %}`で配列ループ)は単一文字列用に
   簡略化する必要がある(`{% if doc_text %}...{{ doc_text }}...{% endif %}`程度に変更)
5. **重要: LLMノードのSYSTEM prompt内に直接埋め込んでいる`テキスト抽出.text`(本文全体)はそのまま
   維持すること**。要約は検索クエリ構築専用であり、LLMが実際に読んで回答する本文は今まで通りフルで
   渡し続ける(要約に置き換えてはいけない)。

## 現在のDifyフロー構成(2026-09-12 17:10時点、公開済み)
`スタート→ユーザー入力→テキスト抽出(files入力)→テンプレート(query+doc_text結合、Jinja)→
知識検索(元データセット, 15ファイル)/知識検索2(CASES大容量データセット, 4ファイル: cases_global_01.md/
case_expert_index.md/cases_apac_01.md/knowledge_untagged_01.md)→変数集約器(両方のresultを統合)→
LLM(コンテキスト=変数集約器.output、SYSTEM prompt=SKILL_Dify.md全文42698文字+テキスト抽出.text直接
埋め込み)→回答`。SYSTEM prompt冒頭に本来不要なYAML frontmatter/HTMLコメントが混入している
(軽微、動作に支障なし、気になれば除去可)。

## 診断に使った有効な手法(次回同様の調査で再利用可)
- 実行ログの個別ノードトレース確認は難しい(Difyのログ詳細はチャット全体のみ表示、per-node詳細は
  見つけられず)。**代わりにStudioの「プレビュー」機能でリアルタイム再現テストする方が早い**。
- 特定のナレッジベースの検索精度は、そのデータセットの「検索テスト」ページで直接クエリを打って
  スコアを見るのが最も確実(チャットフロー全体を経由せず単体検証できる)。
- 添付ファイルなしで直接テキストで質問する簡易テストと、実際のdocx添付テストを比較することで、
  「添付ファイル経由の長いクエリ」と「短い直接質問」の精度差を切り分けられた。

## Next(次の新規チャットで最初にやること)
1. 上記「ブリーフ要約」ノードを追加・配線・プロンプト設定(中村さんと相談しながら実施、
   これまでの傾向からユーザーが自分で手を動かしたい場合はガイド、急ぐ場合はClaudeが代行)
2. テンプレートノードのJinjaコード修正
3. 同じAcecook Vietnamブリーフで再テストし、CASE_ID/実URL/駐在員名が正しく出るか確認
4. 問題なければ「公開する」で本番反映
5. 未着手のまま残っている項目: SYSTEM prompt冒頭のfrontmatter除去(軽微)、ChatGPT版SKILL.mdへの
   同種改善の反映要否、Difyワークスペース(dJ-Dify_共通プレイグラウンド)移行要否の中村さんの判断待ち

## 参照(今回のセッションの全記録、時系列順)
[[work_status/agency_os_quickmode_removal_and_dify_websearch_20260912]] →
[[work_status/agency_os_dify_skill_split_and_file_upload_bug_20260912]] →
[[work_status/agency_os_dify_flow_rewiring_20260912]] →
[[work_status/agency_os_dify_fabrication_and_retrieval_gaps_20260912]] →
[[work_status/agency_os_dify_case_fabrication_and_privacy_excuse_20260912]] →
[[work_status/agency_os_dify_retrieval_architecture_split_20260912]] → (本ファイル)
