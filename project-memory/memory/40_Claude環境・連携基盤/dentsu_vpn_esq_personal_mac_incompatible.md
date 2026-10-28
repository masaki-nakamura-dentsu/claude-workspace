---
name: dentsu_vpn_esq_personal_mac_incompatible
description: esq-vpn.dentsu.co.jp (会社VPN)は個人Mac(ICPTokyo2022)からは接続できないことが判明、F5関連ソフトはアンインストール済み
metadata: 
  node_type: memory
  type: project
  originSessionId: 292b875d-d503-4ca0-a5ba-4e4fd4888950
  modified: 2026-08-21T14:59:25.451Z
---

2026-08-21、個人Mac(ICPTokyo2022)から https://esq-vpn.dentsu.co.jp/ への接続を試みた。

## 経緯
- 会社アカウント(Chrome Profile 1: masaki.nakamura@dentsu.co.jp)でポータルにログイン、MFA通過
- ポータルの案内でインストールを実施 → 「F5 Endpoint Inspector.app」のみがインストールされ、本体の「BIG-IP Edge Client」アプリは/Applicationsに現れなかった
- ユーザー本人が確認し、**個人Macでは接続できない**と判断(会社支給端末専用の制限と思われる、未確認)

## 対応
- F5 Endpoint Inspector関連を完全アンインストール済み(2026-08-21実施)
  - /Applications/F5 Endpoint Inspector.app
  - /Library/LaunchDaemons/com.f5.f5epihelper.plist
  - ~/Library/LaunchAgents/com.f5.f5epihelper.plist
  - ~/Library/Application Support/F5 EPI

## Why
個人Mac(私用Mac)は会社VPN(esq-vpn.dentsu.co.jp)接続の対象外である可能性が高い。会社支給Mac(d14461)側であれば接続できる可能性がある(未検証)。

## How to apply
- 今後、個人Macで会社VPN接続を求められた場合はこの制限を先に伝える。再インストールを試みる前に、まずd14461(会社Mac)側での接続可否を確認するか、社内ITに個人端末での利用可否を確認するのが妥当。
- 関連: [[reference_mac_naming]](マシン呼称の対応表)
