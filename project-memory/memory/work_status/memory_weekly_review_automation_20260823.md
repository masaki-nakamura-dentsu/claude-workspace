---
name: memory_weekly_review_automation_20260823
description: 週次メモリレビュー自動化を構築・会社Macへ展開したセッションの記録
metadata: 
  node_type: memory
  type: work_status
  originSessionId: 8e9cbaae-ac73-44e1-ada8-c4c2e424f32d
  modified: 2026-08-22T22:15:57.203Z
---

Status: done(個人Mac側)/ 会社Mac側の`launchctl load`のみ未実施

## やったこと
1. CLAUDE.mdの既存ルール(2026-07-25)を「毎セッション終了時に必ず学び・失敗をmemoryへ反映」という無条件ルールへ強化
2. `~/.claude/projects/*/memory/`を週次で棚卸しする自動化を新規構築
   - 重複メモリの統合+統合済み重複ファイルの削除のみ許可(老朽化削除は禁止、ユーザー承認済み)
   - 実行前に必ず`_backups/`へバックアップ
   - `claude -p`の週次利用上限到達時はTeams通知(過去にこれが原因で無言失敗した前例への対策)
   - タイミングは当初水曜夜→ユーザー指示で月曜8:30(既存snsdraftジョブに合わせる)に変更
3. launchd登録(`com.nakamura.memoryweeklyreview.plist`)、個人Macで有効化確認済み
4. **重大な自分のミス**: 「memoryはMac個別でDropbox同期外」と確認せずに断定し、CLAUDE.md・project memory両方に誤った記述をした。既存の[[feedback_check_dropbox_sync_before_claiming_isolated]]という、まさにこの失敗を警告するfeedbackメモリが存在していたにもかかわらず再発。ユーザーの質問で発覚し、`dropbox_config_sync`を確認して訂正、該当feedbackメモリに再発インシデントとして追記した
5. 別セッション由来と思われる「CLAUDE.md週次自動編集」機能が同じ共有ファイル上に並行して追加されているのを発見。ユーザーに意図的なものか確認(AskUserQuestion)→意図的と確認、継続
6. スクリプト一式(`run_weekly_review.sh`等)がDropbox同期対象外の`~/MemoryWeeklyReview/`に置かれていたため、`.claude-sync/Scripts/MemoryWeeklyReview/`(既存のGBCWeeklyReport等と同じ共有パターン)へ移設。これによりCLAUDE.md自動編集機能の重複実行防止マーカーも複数Mac間で正しく共有されるよう修正
7. 会社Mac(d14461)用launchd plist(`com.nakamura.memoryweeklyreview.d14461.plist`)を共有フォルダに用意。会社Macでの残作業は`cp`+`launchctl load`の2行のみ、per-project memory `memory_weekly_review_automation.md`に記載済み

## 次回への引き継ぎ
- 会社Macで`launchctl load`が実際に行われたか未確認
- 次回自然発火は2026-08-24(月)8:30。ログ・Teams通知・実際のmemory変更内容(バックアップとの差分)を確認すること
- 詳細は per-project memory [[memory_weekly_review_automation]] を参照
