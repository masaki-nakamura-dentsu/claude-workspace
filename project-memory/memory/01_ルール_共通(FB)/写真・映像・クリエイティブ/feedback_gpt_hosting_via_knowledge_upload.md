---
name: feedback-gpt-hosting-via-knowledge-upload
description: ChatGPT Custom GPT連携でホスティング先が無い/未定の時は、APIを外部公開する代わりにデータ自体(DB+検索スクリプト)をCode Interpreter用Knowledgeとしてアップロードする方が良い場合がある — 中村さんの指摘で採用した設計転換
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1749c365-0287-43f7-83ff-d010d1abf3b0
  modified: 2026-08-26T04:55:39.592Z
---

ChatGPTのCustom GPTにサーバー側データへアクセスさせたい時、「Actionで外部APIを
呼ばせる」以外に「データそのもの(DBファイル+検索スクリプト)をCode Interpreter対応の
Knowledgeとしてアップロードし、GPTにPythonで直接クエリさせる」という選択肢がある。
後者はホスティング(公開HTTPSサーバー)が一切不要になる。

**背景**: [[gbc_intelligence_engine_project]]でChatGPT Action方式
(`/api/report`エンドポイント)を先に設計したが、ホスティング先が未定という
壁にぶつかった。ngrok等での一時公開も、Salesforce案件情報・局員個人情報を含む
APIを外部に晒すことになるため保留していた。中村さんから「今我々がまとめた
知見そのものはGPTに渡さなくてよいのですか？渡したほうがサーバーの問題を
解決できる気がします」と指摘があり、これがまさに正解だった。

**なぜこれで解決するか**: ホスティングの壁は「サーバーを外部公開する」という
発想が前提になっていた。データ量が小さい(この例では33MB)なら、公開サーバーを
作る代わりにデータそのものをChatGPT側にアップロードしてしまえば、外部からの
到達性という問題自体が消える。

**やり方の注意点(2種類あるうち片方を選ぶこと)**:
1. **データをテキスト化してKnowledgeに読ませ、ChatGPT標準の埋め込み検索に
   任せる** — 手軽だが、埋め込み/FTS5系の検索は短い日本語キーワード
   (例: 2文字の国名)で精度が落ちることが多く、根拠なき推測(幻覚)も
   起きやすい。[[gbc_intelligence_engine_project]]では2026-08-18に
   まさにこの理由でFTS5からLIKE+複合AND検索に切り替えた経緯があり、
   同じ失敗を繰り返すリスクが高いため避けた。
2. **DBファイルそのもの+決定的なクエリロジックをPythonスクリプトとして
   Knowledgeに置き、Code Interpreterで実行させる**(採用した方式)。
   検索精度は元のAPI/SQLロジックと完全に同一のまま、ホスティングだけを
   不要にできる。データが更新されたらDBファイルを再アップロードすれば
   追随する(常時最新ではなくスナップショット、という制約は残る)。

**How to apply**: 他のプロジェクトでも「ChatGPT/GPTに社内データへアクセスさせたいが
ホスティング先が無い/決められない」という壁に当たったら、まずデータ量が
Knowledgeアップロード可能な範囲(数十MB程度)に収まるか確認し、収まるなら
Code Interpreter+スクリプト方式を検討する。ただし機密データを外部(OpenAI等)に
渡すこと自体は変わらない意思決定なので、Action方式かKnowledge方式かに関わらず
「データが社外に出る」という点はユーザーに明示的に確認すること
([[feedback_verify_against_ground_truth]]寄りの一般則とも共通)。
