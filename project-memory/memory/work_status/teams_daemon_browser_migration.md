# teams_daemon.py 共有ブラウザ移行(d14461)

## 2026-08-12T09:35:00+09:00
Status: done
What: outlook CLIの会社Mac展開に続き、ユーザー依頼でteams_daemon.py(Teams継続収集デーモン)を独自の専用ブラウザ(TeamsExport/browser_profile)から共有ボットブラウザ(port 9226, SalesforceExport/browser_profile)経由のCDP接続に移行。スクレイピング本体ロジックは一切変更せず、ブラウザ接続部分のみ置き換え。移行中に発見した実バグ(該当タブが見つからない場合にcontext.pages[0]を再利用する実装が、既存のOutlookタブを乗っ取ってTeamsに書き換えてしまう)をteams_daemon.py・outlook_cli/lib.jsの両方で修正(常に新規タブを開く方式に変更)。旧手動プロセスで1サイクル検証(ログイン無風・新規55件正常取得・エラーなし)→launchd経由(load)でも自然にコールドスタート成功(起動待機→ログイン確認→ポーリング開始)を確認。旧browser_profile(2.3GB)は未使用だが削除せず保持。継続的データ収集は中断せず稼働継続中。
Next: なし。次回sync健全性チェック時は新アーキテクチャを前提に確認する([[continuous_data_capture_setup]]更新済み)。
