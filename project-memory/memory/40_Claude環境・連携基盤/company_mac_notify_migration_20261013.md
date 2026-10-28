---
name: company-mac-notify-migration-20261013
description: 会社Mac(N650893/d14461)専用スクリプトのTeams通知を共通送信口へ移行した記録(job名・レベル割当)と、起動直後の誤検知対策の設定値
metadata:
  node_type: memory
  type: project
  originSessionId: d34cba87-76e5-4941-a7b4-3a7a1c77344d
  modified: 2026-10-12T23:31:02.033Z
---

2026-10-13、relay task-015 として実施。[[webhook_autofix_project]] の続き。

- 移行済み(URL直書き撤去、teams_notify経由): Salesforce QBR DL / COMBINED.xlsx自動更新 / CAS月次パイプライン / Crosstable月次更新 / KGI/KPIレポート定期保存 / 海外拠点別数字 / Teams取込デーモン / OverseasStaffList(common.send_teamsをアダプタ化: title末尾「失敗」=ERROR、他=OK)。各ファイル .bak_20261013HHMM あり。
- 共有コードの設定値: カレンダー同期 `WAKE_GRACE_SECONDS=3600`(kern.waketime→無ければkern.boottimeからの経過でPAフロー停止判定を保留)。週次AIダイジェスト `STARTUP_WAIT_S=180`、自分チャット検出は30秒×10回リトライ、投稿直前に状態ファイル再読込(他マシン実行済みなら投稿しない)。
- 原因の型: 会社Macは長時間電源オフ→起動直後にRunAtLoadジョブが走ると、OneDrive/Dropbox未同期・Teams未ログインで誤ERRORを出す。両Macで同じ週次ジョブが動く(個人Mac 08:00が正)。
- `com.nakamura.webhookautofix`(15分おき+RunAtLoad、ログ `WebhookAutoFix/logs/launchd_*_d14461.log`, `run_YYYYMM_N650893.log`)は auto mode が「Unauthorized Persistence」で拒否したため、ユーザーが手動登録。2026-10-13 08:30 稼働開始を確認。task-015 done。

**How to apply:** 会社Macからの通知文言の質問はこの割当で答える。launchd登録は auto mode では通らないので、最初からユーザーにコマンドを渡す。
