---
name: feedback-sudo-and-mas-install-limitations
description: sudoパスワードが必要な操作とmas(Mac App Store CLI)での大容量アプリ取得は、このBashツールからは自動化できない既知の制約
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f93e50d1-bd7c-49e4-82a3-5ac3d32fbcbf
  modified: 2026-09-16T06:58:59.196Z
---

Claude CodeのBashツールから実行するコマンドが`sudo`のパスワード入力を要求する場合、対話的ターミナルが無いため必ず失敗する（`sudo: a terminal is required to read the password`）。`sudo -n`で非対話モードにしても同じく失敗する。

加えて、`mas`（Mac App Store CLI）経由での大容量アプリ（Xcodeなど）インストールは、Apple側の再ダウンロードAPI制限により「このApple Accountでは再ダウンロードできません」等のエラーで失敗することがある（2026-09-16、CurrencySortアプリのビルド環境構築時に発生、[[currencysort_app_project]]参照）。これは`mas`側のバグ/Apple側API仕様の既知の制約で、CLIからの回避策はない。

**Why**: どちらも2026-09-10のChrome Remote Desktop導入時（[[mac_handoff_relay]]のtask-005）と同じ「sudoパスワードが必要でCLIから自動化不可」パターンの再発。今回はさらにmas特有の制限も重なった。

**How to apply**:
- sudoが必要な操作に遭遇したら、まずユーザーに「ターミナルでこのコマンドを実行してください」と具体的なコマンドを提示して依頼する。無理にワークアラウンドを探して時間を浪費しない。
- ビルド/実行ツール（`xcodebuild`等）がDEVELOPER_DIR環境変数で開発者ディレクトリを指定できる場合は、`xcode-select -s`（sudo必要）を避けてそちらを使う（sudo回避のショートカットとして有効）。
- Xcode本体の取得は`mas install`より先にApp Storeアプリ(GUI)での手動インストールを提案する方が早い場合がある（`mas`はしばしば大容量アプリで失敗するため）。`open "macappstore://apps.apple.com/jp/app/xcode/id497799835"`でXcodeのページを直接開いてユーザーの手間を減らせる。

関連: [[company_mac_no_admin_no_homebrew]]は会社Mac(d14461)固有の「管理者権限がそもそも無い」という別種の制約(root不要のmicromamba回避策あり)。本ファイルは「管理者権限があってもClaude CodeのBashツールからは対話的sudo/大容量mas installを実行できない」というツール側の一般的制約で、どのMacでも当てはまる点が異なる。
