
## 08:30 AgencyOS週次(クレデン) カード数108→0(会社Mac N650893)
- Status: pending-user
- 事象: weekly_credential_update.sh が112件を「抽出失敗 PermissionError」→ cards=0 → 90%ガードで反映中止(ガードは正常動作、Skill/Difyは未変更)
- 原因: build_credential_pack.py が読む ~/Library/CloudStorage/OneDrive-電通/GBC - 02．クレデン共有チャネル へ、この実行経路(launchd/headless)が「Operation not permitted」(macOS TCCのOneDrive/ファイルアクセス権)。10/23の対話実行では読めていた。ファイル自体は存在(ls可)。
- 対応: スクリプト無編集・再実行なし(同じ権限エラーになるため)。
- ユーザー対応: システム設定>プライバシーとセキュリティ>フルディスクアクセスで /bin/bash と python3(/Library/Frameworks/Python.framework/Versions/3.14/bin/python3、launchd実行元)を許可、またはOneDriveで当該フォルダを「常にこのデバイスに保持」に。確認: ターミナルでなくlaunchd経由 `launchctl kickstart -k gui/$(id -u)/com.nakamura.agencyosweeklycredential` 後 run_20261026.log に cards=108 前後が出ること(last_run.txtが2026-W43のままなので再実行される)。
## 08:40 ラズパイ停止通知(healthchecks.io, 10/24 22:44JST発) — 誤検知/回復済み
- Status: done
- 確認: tailscale statusでraspi(100.96.219.107)が active・LAN直結(192.168.0.16)。通知は2日前の一時停止で、既に復旧。対応不要。
- 原因は不明(停電/LAN/回線の一時断の可能性)。再発時は電源・LAN確認。

## 09:44 KGI/KPIレポート定期保存 PDF 0 bytes(会社Mac N650893)
- Status: monitoring
- 事象: 09:40定期実行と09:42の私の `--force` 再実行(1回)で、ダウンロードは完了するが0 bytes。Botブラウザ(9226)は稼働中、ログイン/UIクリックまでは通過。
- 判断: 10/22午前にも同症状(0 bytes×3)があり、15:40の枠で自然回復。Power BI側のエクスポート生成が空になる一過性と推定。スクリプト無編集。
- 対応: 再実行は1回のみ。launchdが同日11:40/13:40/15:40に自動再試行(成功済みならスキップ)。
- 再発・継続時: 15:40枠でも失敗なら、Botブラウザで手動でレポート→PDFエクスポートが空にならないか確認(レポート側の重いビジュアル/容量・Power BI障害)。

## 17:30 Salesforce QBR DL(個人Mac) connectOverCDP Timeout
- Status: pending-user
- 原因: Bot Chrome(dentsu-work-bot, port 9231, PID7540, 金曜から常駐)がハングし、CDP接続がタイムアウト(ws接続後に応答なし)。単体テストでも再現。
- 対応: ハングしたChromeをkill→スクリプトの自動起動で復旧(接続OK)。再実行1回 → 今度は「SSOセッション切れ(myapps.dentsu.com)」で中止。スクリプト無編集。
- ユーザー対応: dentsu-work-botプロファイルのChrome(port 9231、画面外-2500,-2500)でMyApps経由でSalesforceに再ログイン(MFA)。確認: failover_log.txtの次回ポーリング(20分毎)で「まだN本欠けています」が減り、pipeline_log.txtに「成功」が出ること。10/23にも同じSSO切れが出ており、再発傾向。
