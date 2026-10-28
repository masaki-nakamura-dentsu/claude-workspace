---
name: personal-windows-wol-via-crd
description: "会社Mac→Chrome Remote Desktop→個人Mac→WOLで個人Windows(DESKTOP-RYZEN5950)を遠隔起動する経路。MACアドレス・コマンド・CRD設定の注意点"
metadata:
  type: project
  originSessionId: unknown
  modified: 2026-09-10T11:40:50.029Z
---

2026-09-10、[[mac_handoff_relay]]のtask-005として会社Mac側から依頼、個人Mac側で構築・実機確認済み。

## 経路
会社Mac → Chrome Remote Desktopで個人Mac(ICPTokyo2022)に接続 → 個人Macから以下のコマンドを実行 → 個人Windows(DESKTOP-RYZEN5950)がWOLで起動。

```
wakeonlan -i 192.168.0.255 -p 9 2C:F0:5D:D8:02:6F
```

- MACアドレス: `2C:F0:5D:D8:02:6F`
- Windows側LAN内IP: `192.168.0.11`
- wakeonlanはHomebrewで個人Macに導入済み(`brew install wakeonlan`)。
- 2026-09-10に実機テスト成功(送信後約10秒でping応答)。

## Windows側のWOL設定
既に設定済み(NIC WOL有効化・高速スタートアップ無効化・BIOS WOL有効化)。ユーザーはiPhoneアプリ「Wolow」で外出先からのWOLを以前から運用済みだった。アプリ設定画面のIP欄`113.147.123.63`はルーターのWAN側公開IP経由の外部転送用と推測され、同一LAN内から送る場合(個人Mac側)は使わず、ローカルブロードキャスト`192.168.0.255`を使う。

## Chrome Remote Desktop設定の注意点
`brew install --cask chrome-remote-desktop-host`はpkgインストーラーでsudoパスワードが必要なためCLIから自動実行できず、ユーザー本人にターミナルで手動実行してもらう必要があった(完了後ログアウト/ログイン要)。

**ペアリングは「リモートアクセス」タブで行うこと。** 初回、ユーザーが誤って「リモートサポート」タブ(一時コード方式)でPIN設定してしまい、永続化されず`org.chromium.chromoting`(LaunchAgent)が起動しない状態になった。「リモートアクセス」タブでのペアリングに変更したところ成功。稼働確認は`launchctl print gui/<uid>/org.chromium.chromoting`ではなく、`org.chromium.chromoting.broker`(root権限、LaunchDaemon)プロセスの起動有無、または実際にremotedesktop.google.com/accessでこのMacが「オンライン」表示されているかで見るのが確実(me2me_host_serviceは常時起動ではなくbrokerがオンライン状態を管理している模様)。

## How to apply
今後「会社Macから個人Windowsを起こしたい」等の依頼があれば、上記コマンドをそのまま案内・実行すればよい(MACアドレスや経路を再確認する必要はない)。CRDの導入・ペアリングが必要になる別マシンがあれば、上記の「リモートアクセスタブを使う」「brokerプロセスで確認する」の教訓を適用する。
