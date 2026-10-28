## 2026-09-29 — ラズパイ到着、セットアップ開始
Status: in progress
- Raspberry Pi Imager導入(brew cask)、SSH鍵 ~/.ssh/id_ed25519 作成
- 次: SD書込(ユーザー操作) → 初回起動 → SSH → Tailscale
## 2026-09-29 — SD書込完了
Status: in progress
- OS書込+cloud-init設定済み、SD取り出し済み。次: ユーザーが起動→ssh masaki@raspi.local→Tailscale
## 2026-09-29 — 起動確認・Tailscale導入
Status: in progress
- IP 192.168.0.16、更新済、Tailscale認証URL提示中
## 2026-09-29 — Tailscale exit node稼働
Status: in progress
- 100.96.219.107、exit node承認済。次: key expiry無効化、DHCP予約、AdGuard Home
## 2026-09-29 — HGWパスワード復旧
Status: in progress
- 過去セッションのラベル写真から初期Webパスワードを提示。次: DHCP予約
## 2026-09-29 — DHCP予約完了、AdGuard導入は許可待ち
Status: in progress
## 2026-09-29 — AdGuard Home稼働
Status: in progress
- 次: HGW DNS配布設定(ユーザー)、WOL中継、Uptime Kuma
## 2026-09-29 — HGWにDNS配布設定なし判明
Status: in progress
- 代替案をユーザーに提示中
## 2026-09-29 — 個人MacにTailscale導入中
Status: in progress
- GUIインストーラー起動、ユーザー操作待ち。次: ログイン→管理画面DNS設定→確認
## 2026-09-29 — 個人Mac Tailscale DNS経由の広告ブロック確認
Status: in progress
- 次: WOL中継、Uptime Kuma
## 2026-09-29 — iPhone Tailscale設定手順を案内
Status: in progress
- ユーザー外出中に設定予定。次: WOL対象機器の確認→WOL中継、Uptime Kuma
## 2026-09-29 — WOL中継構築
Status: in progress
- wol-http稼働、パケット検証済、Pi単独の実機起動は再テスト待ち。次: iPhoneショートカット、Uptime Kuma
## 2026-09-29 — WOL Pi単独起動を実機確認
Status: in progress
- シャットダウン→約75秒で起動。次: Uptime Kuma
## 2026-09-29 — Uptime Kuma稼働
Status: in progress
- 6監視、Teams通知テスト送信成功。残: ラズパイ自体の死活を外部から監視、Macジョブ監視
## 2026-09-29 — 常時自動化の置き場+外部見張り着手
Status: in progress
- Pi: rclone 1.60, python3-truststore導入、RSS取得OK。rclone Dropbox認証待ち、healthchecks.io登録待ち
## 2026-09-29 — 方針確定
Status: in progress
- web_tips移設・Macジョブ見張りは中止。healthchecks.ioのURL待ち
## 2026-09-30 — healthchecks.io稼働
Status: in progress
- 合図送信OK、停止/復旧通知のTeams着信をユーザー確認待ち
## 2026-09-30 — healthchecks Teams通知修正
Status: done
- Test!着信OK、本番経路再テスト実施。ラズパイ4用途(VPN/AdGuard/WOL/監視)+外部見張り完了。web_tips移設・Macジョブ見張りは中止
## 2026-09-30 — 追加用途の提案
Status: done
- healthchecks本番経路の停止/復旧通知着信をユーザー確認。追加用途候補(サブネットルーター/Ollamaオンデマンド起動/changedetection/Time Machine/回線速度記録)を提示
## 2026-09-30 — ゼロトラストとの比較を説明
Status: done
- Tailscale自体がゼロトラスト型である点、強化策(ACL最小権限/2FA/Tailnet Lock)を説明
## 2026-09-30 — 現状運用で確定
Status: done
- ACL等の強化・追加用途は見送り。ラズパイセットアップ一式完了
## 2026-10-04 — 海外での使い方を再案内
Status: done
- Exit Node手順を回答
## 2026-10-04 — Exit Nodeの仕組みを説明
Status: done
## 2026-10-04 — Fire TV StickでのTailscale利用手順を案内
Status: done
- Appstore掲載は未確認のため、無い場合はDownloader経由のAPK導入を併記
## 2026-10-06 — Fire TV開発者オプション表示方法を案内
Status: done
## 2026-10-07 — HDY定点観測のラズパイ移設可否を回答
Status: done
- 公開情報系は技術的に可、ただし出力先(Dropbox/aicon OneDrive)に届かない・社内認証系は不可・会社データを私物機器で扱う懸念→全面移設は非推奨。代替: 会社Macの収集ジョブからhealthchecks.ioへ合図→止まったらTeams通知、を提案
## 2026-10-07 — ラズパイ一般用途の提案
Status: done
- HDY定点観測は保留(ユーザー判断)。一般用途の候補一覧を提示
