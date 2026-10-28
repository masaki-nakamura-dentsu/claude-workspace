# CLAUDE.md 週次レビュー 2026-09-28

Status: done

- 対象: マーカー 2026-09-20T23:36:33Z 以降に更新された .jsonl 26件(Dropboxルート25件＋`-`プロジェクト3件、うち自動実行プロンプト除く)。ユーザー発話約190件を確認。
- 追記(1件): 「アクセス不可と言う前に既存経路(ログイン済み共有ブラウザ・ローカルエクスポート等)を試す」ルール。根拠 `1ddfd5f8`(09-21 Vimeo字幕)、`053e5ad7`(09-27 個人Gmail)。詳細は新規メモリ `feedback_exhaust_access_routes_before_giving_up.md`、MEMORY.mdに索引1行追加。
- バックアップ: `.claude-sync/Scripts/MemoryWeeklyReview/claude_md_backups/20260928/CLAUDE.md`
- 見送り(既存メモリでカバー済み/根拠が単一セッション): TimeTree登録漏れ・既存フラグ確認(timetree_web_automation / feedback_timetree_no_specific_content)、JAAA論文ページ数超過の反復(jaaa_ronbun_2026_essay_project)、PprBridgeパネル開き直し依頼の反復(premiere_cli_investigation、1セッションのみ)、Lightroom CLI強制終了(lightroom_cli_setup)。
- 注意: macOS の `find -newermt` は `2026-09-20T23:36:33Z` 形式を解釈できず0件になった。`touch -t`で基準ファイルを作り `-newer` で代替した(runnerプロンプト側の改善候補)。

## 追記(同日、別セッションによる重複起動の検知)
同じ2026-09-28 08:30台に、本タスクとほぼ同一の手動起動(セッション`795ad812`)が別途発生。マーカー・CLAUDE.md本体・バックアップフォルダ・本ファイルが既に上記の内容で更新済みであることを確認し、追加の編集はスキップ(二重追記防止)。対象ウィンドウ(マーカー2026-09-20T23:36:33Z以降)の候補セッション6件(`87a3a707`/`0b58de0b`/`27ec2c0f`/`3f326f97`/`e43b0e6f`/自分自身)を独自に確認したが、いずれも上記レビュー済み内容と重複するか、単一セッションの自動化スクリプト固有の不具合(GBC週次AIダイジェストのTeamsセッション切れ、ai_teams_weekly_digest.mdで既知)で、新規のグローバルルール追加には値しないと判断。Status: done(本セッションは追加変更なし)。
