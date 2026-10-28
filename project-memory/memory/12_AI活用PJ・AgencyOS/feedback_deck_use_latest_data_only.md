---
name: feedback-deck-use-latest-data-only
description: Agency OS等の説明資料に入れるデータ件数・スライドは必ず最新版から取る。古い版(例:9/17全体像)を流用しない
metadata:
  type: feedback
---
2026-10-26、石坂MD向け資料で9/17の「活用しているデータソース」2枚を流用したところ、「古すぎる」と指摘された。最新は PoCフィードバック報告_20261022 の「いま入っている知見(1/2,2/2)」。

**Why:** 件数・構成は月次で変わる(CCS・BP局・Web検索は9/17以後に追加)。MDへの説明で古い数字は信用を落とす。
**How to apply:** 既存スライドを流用する前に、更新日が最新か・同テーマのより新しい資料が無いかを探す(`GBC-Knowledge/output/monthly_check/` の最終更新、`報告・説明資料/` の最新日付)。数値は取れるものを今日取り直し、日付を添える(例: アレココ閲覧数は SharePoint検索API ViewsRecent、CDP 9226で取得可)。メモリ内の過去の数字をそのまま使わない。
Related: [[agency_os_poc_feedback_20261013]]
