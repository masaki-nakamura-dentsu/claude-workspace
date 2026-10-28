---
name: work_status/euromonitor_dl_company_20261023
description: Euromonitor 3年分DL(会社Mac担当 task-024)の進捗と再開手順
metadata:
  type: project
---
Status: in_progress (2026-10-23 18:40)
- 全1909件(Opinion/Briefing/Country Report/Video/Global Company Profile)。2台合算で約1787件完了、未完了122件を調査スクリプト/run_each.sh 0 と 1(1件ずつ別プロセス、会社Mac)で処理中。
- 保存先: Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/Euromonitor_レポート保存_20261023/downloads/
- 個人Macのbulk.jsは停止済み(task-025 done)。重複321件は同名上書きでファイル重複なし。個人Macへの依頼は mac_direct send.sh で即時([[feedback_use_mac_direct_first]])。
- 問題: タブが閉じてbulk.jsが落ちる事象(2498289 Briefing FMCG World Market で再現。skipped記録済み)。
- 終了時: dl_progress*.jsonl を合算し未完了を確認 → company_mac_inbox task-024 の Result 記入 + teams_notify DONE。ダウンロード結果.md は個人Mac側担当。

Status: done (2026-10-23 19:25)
- 1909/1909件を downloads/ で確認(失敗0)。inbox task-024 を done にしResult記入、Teams DONE通知済み。残りは個人Mac側のダウンロード結果.md作成のみ。
