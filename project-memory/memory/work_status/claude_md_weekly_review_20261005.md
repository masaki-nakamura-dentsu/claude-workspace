# CLAUDE.md 週次レビュー 2026-10-05
Status: done

- 対象: マーカー 2026-09-27T23:31:59Z 以降に更新された .jsonl 41件(本セッション除く)、ユーザー発話 約240件を jq 抽出して分析。
- 注: BSD find の `-newermt` が ISO8601(Z付き)を解釈できず0件になったため、`TZ=UTC touch -t` で参照ファイルを作り `-newer` で代替。
- 追記(1件): 「手作業をユーザーに渡すときは検証用テストプロンプト/確認手順と期待結果を同じメッセージで渡す」(根拠: 8b32504c, ea09c319, 40daba17, 3f326f97)。詳細は feedback_handoff_include_verification_prompt.md。
- 見送り(既存メモリでカバー済み): 日系ピッチリストの原本照合(feedback_jci_pitchlist_check_against_bd_original)、局員はChatGPT/Dify/Copilotのみ使用(gbc_intelligence_engine_project)、停止→「続けて」(既存の停止検知ルール)。
- バックアップ: .claude-sync/Scripts/MemoryWeeklyReview/claude_md_backups/20261005/CLAUDE.md
- ほか: d0b9fb08 (2026-09-30) でユーザーがYouTube Data APIキーをチャットに平文で貼っている。ログに残っているので、必要ならキーのローテーションを検討。
