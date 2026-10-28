---
name: bigip-zscaler-reconnect-loop-conflict
description: 会社Mac(d14461)でBIG-IP VPNが数秒おきに再接続を繰り返す問題は、ZscalerとBIG-IPとMicrosoft Defenderネットワーク拡張が同時稼働していることによる競合が濃厚。Wi-Fi/テザリング設定とは無関係と切り分け済み
metadata:
  type: project
  originSessionId: session-2026-08-26-wifi-tethering
  modified: 2026-08-26T02:01:43.983Z
---

2026-08-26、会社Mac(d14461)でF5 BIG-IP(Endpoint Inspector/SSL VPN Plugin)が「接続中」表示を数秒おきに繰り返し、時々切断ウィンドウが出る症状が発生。

## 切り分け経緯
- 直前に[[company_mac_wifi_jamf_restriction_and_tethering_workaround]]の作業(iPhoneテザリング自動接続スクリプト+LaunchAgent)を行っており、当初はそれが原因かと疑われた
- LaunchAgentを完全停止、Wi-Fiをテザリング→自宅Wi-Fiに変更、BIG-IPを終了・再起動しても症状は変わらず再現 → ネットワーク環境(Wi-Fi/テザリング)由来ではないと確定
- プロセス確認の結果、以下が同時常駐していることが判明:
  - Zscaler(ZscalerTunnel/ZscalerService、ログイン時から常駐)
  - F5 BIG-IP(PolicyServer/svpn、esq-vpn.dentsu.co.jp向け)
  - Microsoft Defenderネットワーク拡張(`com.microsoft.wdav.netext`、activated enabled)

## 結論(未確定・推測)
ZscalerとBIG-IPは両方ともルーティング/DNSを制御しようとするクラウドプロキシ/VPNクライアントであり、同時稼働時に経路の奪い合いで接続が不安定になる既知のパターンに合致する。ただしIT部門への確認・修正は未実施。

## How to apply
- 今後同様の「VPN/BIG-IPが頻繁に再接続する」相談があれば、まずWi-Fi環境を変えて再現するか切り分け(再現するならネットワーク側は無罪)、次に`ps aux | grep -iE "vpn|zscaler|f5"`でZscalerとBIG-IPの同時稼働を確認する。
- 管理者権限がない([[company_mac_no_admin_no_homebrew]])ため、Zscaler側の設定変更やアンインストールはユーザー側では実施不可。解決には社内ITヘルプデスクへの相談が必要。
