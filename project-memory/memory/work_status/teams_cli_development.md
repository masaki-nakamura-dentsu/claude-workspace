# Teams CLI開発

## 2026-08-09T10:20:00+09:00
Status: done
What: ユーザー要望「TeamsのCLIを開発して」に対応。範囲確認(自分チャット投稿+任意チャット送信、読み取りは対象外)後、~/Scripts/teams_cli/ にPlaywright+Chrome debug-port方式でCLIを構築(teams login/list/send)。当初はTeams専用の新規Chromeプロファイル(port 9228)を作ったが、ユーザーから「操作するブラウザを1つにまとめて」と指摘を受け、既存のtimetree-bot共有ブラウザ(port 9227)にTeamsタブとして統合し直し、専用プロファイルは削除。login/list/send --self/send --to --dry-run/曖昧宛先エラーをすべて実機で動作確認済み。詳細は per-project memory [[teams_cli]] と [[shared_bot_browser]] 更新分を参照。
Next: — (完了。将来的にチャット履歴の読み取りや新規相手とのチャット開始が必要になれば拡張)
