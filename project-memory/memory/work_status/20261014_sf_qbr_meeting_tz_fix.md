# 2026-10-14 SF QBR DL 会議遅延誤判定の対応
Status: done
- 9:00枠が「大船会」(夜)を会議中と誤判定→11:30まで遅延。原因はカレンダーUTC時刻をJSTとして比較。
- 待機プロセスkill→手動DL 18/18成功、COMBINED更新済み。download_all_reports.pyのTZ変換を修正・検証。
