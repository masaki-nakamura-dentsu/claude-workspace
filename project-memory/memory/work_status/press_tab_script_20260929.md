# 30秒ごとTabキー送信スクリプト (2026-09-29)
Status: done
- ~/Scripts/press_tab.sh 作成(osascript key code 48、引数で間隔変更可、Ctrl+C停止)。アクセシビリティ許可が必要。実行はユーザー側(キー送信のため自動実行せず)。
- 08:28 会社Mac対応: 本体を `.claude-sync/Scripts/press_tab.sh`(Dropbox同期)へ移動、個人Macの ~/Scripts/press_tab.sh はsymlink化。company_mac_inbox.md に task-003(symlink作成)を pending 登録。
- 2026-10-06 08:50 会社Mac: 「tab押しスクリプトスタート」でClaudeからnohup起動を試行→osascriptにキー送信権限なし(1002)で失敗、停止。Claude経由の起動では権限が付かないため、ユーザーがTerminal.appで `~/Scripts/press_tab.sh` を実行する運用(従来どおり)。
