# Outlook CLI 会社Mac(d14461)展開

## 2026-08-12T08:50:00+09:00
Status: in progress
What: 個人Mac側で構築済みのoutlook CLI(Dropbox `.claude-sync/Scripts/outlook_cli/`)を会社Macにセットアップ。install.sh実行(~/Scripts/outlook_cli, ~/.local/bin/outlookのシンボリックリンク作成完了)、Playwright環境は既存のものを流用可能と確認。lib.jsのPORT/PROFILE_DIRは単純上書きだと個人Mac側を壊すため(両Machineで同一Dropboxファイルを共有している)、`SalesforceExport/browser_profile`の存在有無で自動判定する方式に修正(d14461=port 9226/SalesforceExport、個人Mac=port 9227/timetree-bot)。`outlook login`実行→共有ボットブラウザ(9226)を自動起動したが、myapps.dentsu.comのSSOサインイン画面で停止(個人Macと違い既存セッションの自動引き継ぎなし)。ユーザー指示により新規ウィンドウは開かず、既存の共有ボットブラウザウィンドウを前面化してユーザーの手動SSO/MFA完了待ち。
Next: ユーザーのSSO/MFA完了後、`outlook login`で再確認→`outlook list`で受信トレイ確認→結果をoutlook_cliメモリに追記。

## 2026-08-12T09:05:00+09:00
Status: done
What: ユーザーがブラウザで手動SSO/MFAログイン完了。`outlook login`→「ログイン済みです」、`outlook list`→受信トレイ7件を正常取得(件名/差出人/時刻/プレビュー)。会社Mac(d14461)への展開・動作確認が完了。途中、ユーザーが「Teamsのブラウザが既に立ち上がっている」と誤認していた件を整理: d14461にはport 9226(SalesforceExport、本来の共有ボットブラウザ)とTeamsExport/browser_profile(teams_daemon.py専用・pipe接続で外部接続不可)の2系統があると説明し、port 9226側で進めることに合意。ユーザーから新規依頼: teams_daemon.pyのTeams収集機能をCLI化しport 9226に統合したい、Outlook完了後の別タスクとして着手予定([[teams_daemon_cli_migration_todo]]に記録済み)。outlook_cliメモリとMEMORY.mdを更新済み。
Next: 次回セッションでteams_daemon.py CLI化タスクに着手(まずteams_daemon.py実装を読むところから)。
