# GBC Intelligence Engine — ChatGPT Custom GPT Action化(知見活用GPT × AI Agency Team統合)

## 2026-08-26T13:40:00+09:00
Status: in progress
What: 中村さんから「GBC知見活用プロジェクトとAI Agency Teamを統合したい。知見活用側は
状況報告に対し①PMチェックリスト②ツール紹介③関連データ/知見④類似CASE・フォーマット
⑤エキスパート紹介の5つを出し、それをAI Agency Team(ChatGPT側で企画書生成担当を検討中)
に渡す仕組みをGPTに組み込む前提で作ってほしい」との依頼。既存の
`GBC-Knowledge/webapp/app.py`(FastAPI)が個別API(`/api/search`
`/api/checklist/*` `/api/toolkit`)を既に持っていたため、5カテゴリを1呼び出しで
返す統合エンドポイント `/api/report`(operationId: getSituationReport)を新設。
doc_cards/case_records/staff_profiles/contract_tools/pm_checklists/
tool_phase_mappingを組み合わせ、複数キーワードAND検索・出典URL付与・
`task_briefing_format_template.md`の常時同梱・類似案件担当者のエキスパート化を実装。
`~/gbc_knowledge_venv_d14461`のuvicornでローカル起動しテスト済み(5カテゴリとも
正常応答、`/openapi.json`にoperationId等が正しく出ることも確認)。
GPT Builder向けの手順書・貼り付け用Instructions本文を
`GBC-Knowledge/gpt_integration/GPT_Instructions_知見活用GPT.md`に作成。
Next: ホスティング先が未定(IT部門確認待ち、既知の課題)なのでChatGPT Actionsからは
まだ接続できない。ホスティングが決まり次第 `openapi.json`をGPT BuilderにImportし、
Instructions本文を貼るだけで有効化できる状態まで用意した。認証方式は未検討。

## 2026-08-26T13:55:00+09:00
Status: done
What: ホスティング/ngrok一時公開のどちらで進めるか中村さんに確認したところ、
「GPTにスキルとして読み込ませて、残りはChatGPTに対応して貰う形にしたい」との回答。
このセッション側でのホスティング作業・Action接続は行わず、ChatGPTに委ねる方針に確定。
稼働中ローカルサーバーの`/openapi.json`を静的ファイル化し`gpt_integration/openapi.json`
として保存(servers.urlに`https://REPLACE-WITH-HOSTING-URL`のプレースホルダを追加)。
`GPT_Instructions_知見活用GPT.md`冒頭に「この2ファイルをそのままChatGPTに渡せばよい」
というハンドオフメモを追記。プロジェクト本体メモリ([[gbc_intelligence_engine_project]])
にも同内容を反映済み。
Next: — (このセッションでの作業は完了。次回はChatGPT側の進捗を中村さんに確認してから再開)

## 2026-08-26T14:10:00+09:00
Status: done
What: 中村さんから「知見データそのものをGPTに渡した方がサーバー問題を解決できるのでは」と
指摘があり、これを受けてAction/ホスティング方式からホスティング不要のCode Interpreter方式に
最終的に切り替えた。テキストKnowledgeファイルへの生データ投入(埋め込み検索任せ)は、
このプロジェクトが2026-08-18に発見済みの「短い日本語キーワードで埋め込み/FTS5検索が
外れる」問題の再発リスクが高いため不採用と判断・説明。代わりに`/api/report`のロジックを
FastAPI非依存の`query_report.py`として切り出し、`knowledge_index.db`(33MBコピー)・
`task_briefing_format_template.md`と合わせて`gpt_integration/`に配置。中村さんに
「全テーブルそのまま渡す」か「機密テーブル除外の軽量版を作る」か確認したところ
「全テーブルそのまま渡す」を選択、承認済み。ローカルで`query_report.py`が
`/api/report`と同一結果を返すことを確認済み。`GPT_Instructions_知見活用GPT.md`を
Code Interpreter方式向けに全面改訂(Actions方式は「将来オプション」として末尾に残置)。
プロジェクト本体メモリ([[gbc_intelligence_engine_project]])にも最終方式として反映済み。
Next: — (このセッションでの作業は完了。次回はChatGPT側でのGPT作成・動作確認の進捗を
中村さんに確認してから再開)
