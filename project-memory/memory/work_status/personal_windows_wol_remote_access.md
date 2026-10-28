# 個人WindowsへのWOL遠隔起動(会社Mac→Chrome Remote Desktop→個人Mac→WOL)

## 2026-09-10T13:38
Status: in progress
What: 会社Macから個人WindowsをWake on LANで起動したいとの要望。会社Macと個人Windowsは別LANのため直接WOLは届かないので、「会社Mac→Chrome Remote Desktopで個人Macを遠隔操作→個人Macから同一LAN内の個人WindowsへWOL送信」という経路に決定。個人Mac宛てタスクキュー(`.claude-sync/claude_relay/personal_mac_inbox.md` task-005)に、Chrome Remote Desktop導入・個人WindowsのWOL事前設定確認・wakeonlanコマンド用意・経路通しテストの4項目を登録した。
Next: 個人Macセッション起動時にtask-005が自動で拾われるのを待つ。BIOS設定等ユーザー本人の操作が必要な箇所はその時点で個人Mac側からユーザーに確認が入る想定。

## 2026-09-10T18:00
Status: in progress
What: セッション開始時にpersonal_mac_inbox.mdのtask-005(pending)を自動検知。wakeonlanコマンドをHomebrewで導入済み。Chrome Remote Desktop Host(`brew install --cask chrome-remote-desktop-host`)は存在を確認したが、pkgインストール+ログアウト/ログイン必須+Googleアカウントでのペアリング(認証・PIN設定はユーザー本人操作必須)という、現在のセッションを中断する影響があるため、インストール実行はユーザーに一声確認してから進める。
Next: ユーザーにCRD Host導入(ログアウト要)の実行可否を確認。承諾後インストール→ペアリングはユーザー本人に依頼。個人WindowsのMACアドレス確認・WOL設定状況の確認も未着手。

## 2026-09-10T18:15
Status: blocked
What: wakeonlan導入済み。Chrome Remote Desktop Host導入はユーザーに確認し承諾を得たが、brew caskのpkgインストールがsudoパスワード入力を要求しCLIから自動実行できず失敗(sudo: a terminal is required to read the password)。ユーザー本人にターミナルでの手動実行を依頼した。
Next: ユーザーが`brew install --cask chrome-remote-desktop-host`を手動実行→ログアウト/ログイン→Googleアカウントでのペアリング完了後、個人WindowsのMACアドレス確認とWOL送信テストに進む。

## 2026-09-10T18:30
Status: in progress
What: ユーザーがターミナルで`brew install --cask chrome-remote-desktop-host`を手動実行完了。インストール自体は`/Library/PrivilegedHelperTools/ChromeRemoteDesktopHost.app`の存在で確認済み。有効化に必要なログアウト/ログインはユーザーがこれから行う予定。
Next: ログアウト/ログイン後、ユーザー本人にGoogleアカウントでのペアリング(chrome.google.com/remotedesktopでPIN設定)を依頼。並行して個人WindowsのMACアドレス確認とWOL事前設定(NIC有効化/高速スタートアップ無効化/BIOS)の案内を準備する。

## 2026-09-10T18:10
Status: in progress
What: ユーザーがremotedesktop.google.com/accessの「リモートアクセス」タブでペアリング完了、Web UI上でこのMacがオンライン表示されることを確認。プロセス確認では`org.chromium.chromoting`(me2me_host_service、LaunchAgent)は"not running"のままだったが、`org.chromium.chromoting.broker`(remoting_agent_process_broker、root権限、LaunchDaemon)は起動していることを確認 — こちらがオンライン表示の実体と判断。会社Mac→個人MacへのChrome Remote Desktop経路は成立。
Next: 個人WindowsのMACアドレス確認、WOL事前設定(NIC有効化/高速スタートアップ無効化/BIOS)の確認・案内、個人MacでのWOL送信テストへ進む。

## 2026-09-10T20:40
Status: done
What: 個人WindowsのWOLは既に設定済み(iPhoneアプリ「Wolow」で運用実績あり)と判明。MACアドレス(2C-F0-5D-D8-02-6F)をスクリーンショットから取得。個人MacはWindowsと同一LAN(192.168.0.0/24)上にあることを確認し、`wakeonlan -i 192.168.0.255 -p 9 2C:F0:5D:D8:02:6F`で実機WOLテストを実施、約10秒でping応答を確認し起動成功。Chrome Remote Desktopも「リモートアクセス」タブでのペアリングが完了しオンライン表示済み(前エントリ参照)。経路(会社Mac→CRD→個人Mac→WOL→個人Windows)が完成。
Next: なし。会社MacからWindowsを起こす際は、CRDで個人Macに接続後`wakeonlan -i 192.168.0.255 -p 9 2C:F0:5D:D8:02:6F`を実行すればよい。
