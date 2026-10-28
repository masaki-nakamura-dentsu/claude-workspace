# AI活用Tips: Open AI Office Add-in(ChatGPT Add-in)対応

## 2026-09-03T00:00:00+09:00 (JST時刻はおおよそ)
Status: done
What: ユーザーからChatGPT Office Add-in(PowerPoint版)の作業効率Tipsを週次AIダイジェストに加えたいとの依頼。WebSearchで調査→[[feedback_ai_tips_content_curation_criteria]]の基準で3件採用(選択範囲への直接書き込み/配色だけ統一/デッキ構成のAIレビュー)。追加先をAskUserQuestionで確認→「次回の週次AI Teamsダイジェストに手動挿入」を選択。`weekly_ai_digest.py`に`manual_staged_topics.json`を1回限り差し込む機構(`load_manual_staged_topics`/`clear_manual_staged_topics`/`generate()`の`extra_topics`引数)を実装し、3件をこのJSONに投入済み。py_compile通過・ドライラン(実posting無し)でレンダリング確認済み。詳細は[[ai_teams_weekly_digest]]の2026-09-02セクションに記録。
Next: 次回月曜(2026-09-07想定)の本番実行で3件が実際にTeams自分チャットへ投稿され、`manual_staged_topics.json`が自動クリアされるか確認すること。
