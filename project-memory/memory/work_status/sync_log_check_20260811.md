# 同期ログ確認 2026-08-11

## 2026-08-11T07:55:00+09:00
Status: done
What: 「メールなどの同期ログ確認して」を受け、[[feedback_sync_check_scope]]に従いメール/カレンダー/Teams/Facebookの4chを確認。メール(2日stale, 37件滞留)・カレンダー(12h stale, 54件滞留)・Facebook(3日stale, Errno11削除失敗継続)がバックログ化していたため手動インタラクティブ実行で全て解消。加えて、これらのstale状態を自動リカバリする役割だった毎朝7:30の`com.nakamura.timetreecheck`ジョブ自体が2026-08-10から`claude -p`の`Connection closed mid-response`で失敗し続けており、レポート未生成なのを発見(未解決)。Teamsはこの個人Macにデーモンがないため未対処、d14461側で要確認。[[continuous_data_capture_setup]]に詳細追記済み。
Next: `~/TimeTreeCheck/run_daily_check.sh`/`daily_check_prompt.md`のclaude -p呼び出しがなぜ途中切断するか原因調査(未着手)。次回d14461使用時にTeamsデーモンの状態確認。

## 2026-08-11T08:05:00+09:00
Status: in progress
What: ユーザーから「会社Mac(14時起動率高)にも同様の同期チェックを14:00に設定して」と依頼。個人Macのセッションからは会社Macへリモート到達性がなく直接設定不可(ping/ssh確認済み)。代わりにDropbox共有`.claude-sync/Scripts/company_sync_check/`配下に導入一式(run_daily_check.sh, daily_check_prompt.md, com.nakamura.companysynccheck.plist Hour=14, INSTALL.md)を作成済み。会社Mac版はメール・カレンダー同期チェック+Teams監視(report-only、feedback_avoid_mfa_churnにより自動再ログインはしない)の2タスクのみに絞り、TimeTree/Facebookは個人Mac側が担当のまま重複させない設計。[[continuous_data_capture_setup]]に詳細追記済み。
Next: 次回d14461上のセッション(またはユーザー自身のターミナル操作)で`INSTALL.md`の手順を実行し、`launchctl load`まで完了させる必要あり。導入後は14:00の初回自然発火を待ってログ/レポートを確認。

## 2026-08-11T08:15:00+09:00
Status: done
What: ユーザー依頼で上記セットアップ手順プロンプトを`teams_cli`(`teams send --self`)経由で自分宛てTeamsチャットに送信。送信作業中に`teams send`が完全に機能していないバグを発見(送信ボタンのdata-tidがUI側で`sendMessageCommands-send`→`newMessageCommands-send`にドリフト+macOSでは`Control+A`が全選択にならず既存下書きが全くクリアされていなかった)。両方`~/Scripts/teams_cli/lib.js`で修正し、修正後に正常送信できることをスクリーンショットで確認済み。詳細は[[teams_cli]]に追記。
Next: なし(完了)。
