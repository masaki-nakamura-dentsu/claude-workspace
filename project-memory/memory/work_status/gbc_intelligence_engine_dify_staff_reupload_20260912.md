# GBC Intelligence Engine / Agency OS — Dify版 overseas_staff_index.md 再アップロード

## 2026-09-12T11:30:00+09:00 (approx)
Status: done
What: [[gbc_intelligence_engine_project]]の残作業のうち「Difyの`overseas_staff_index.md`削除+チャンク長1024での再アップロード」を実施。個人Mac(ICPTokyo2022)の共有ブラウザ(port 9227)でDify(console.dj-dify.dentsu.jp)へ初回SSOログイン(djn-client.dentsu.jp Okta、これまでは会社Mac port 9226でのみログイン済みだった。ブラウザプロファイルはマシン別のため個人Macでも別途ログインが必要だった)。ナレッジベース「knowledge_consumer...」(GBC Knowledge Pack、19ドキュメント中1件がエラー状態)から`overseas_staff_index.md`(エラー)を削除→18ドキュメントに減少・全件利用可能を確認→同じファイルを「ファイルを追加」で再アップロード。STEP2のチャンク設定はデフォルトで既に最大チャンク長1024 charactersになっていた(前回の4000文字は一時的な操作ミスだったと確認)。「チャンクをプレビュー」ボタンはDify側のバグ(`Input tag 'None' found using 'enable' does not match any of the expected tags: False, True`)でプレビュー表示に失敗したが、設定自体は正しいため無視して「保存して処理」を実行。処理後、19ドキュメント全件が「利用可能」ステータスになりエラーバナーが消えたことを確認。
検索テストページで「タイ 駐在 経験者」を検索し、Chunk-21(現在駐在中10名、バンコク中島幸子さん等)・Chunk-52/Chunk-43(過去駐在経験者)が正しくヒットすることを確認し、修正の有効性を実証した。
作業後、共有ブラウザ(port 9227)は最小化して後片付け。

## 副産物: 個人MacでのDifyアクセスが今回初めて確立
[[shared_bot_browser]]に記載の通りブラウザプロファイルはマシン別。今回、個人Mac(ICPTokyo2022)のport 9227ブラウザでもDify SSOログインを完了させたため、次回以降は個人Macからも会社Macと同様にDify自動操作が可能(再ログイン不要、Cookieがプロファイルに保持される想定)。

Next: [[gbc_intelligence_engine_project]]の他の残作業(SKILL.md最新版のChatGPT/Dify両エディタへの反映確認、GBC Business「3拠点目」進捗確認)は未着手。次にこのプロジェクトに触るときは中村さんにどちらから進めるか確認すること。
