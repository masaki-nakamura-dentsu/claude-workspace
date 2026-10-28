---
name: feedback_long_job_progress_reporting
description: 長時間バックグラウンド作業では、聞かれる前に節目で進捗を報告し、確認手段を最初に決める
metadata:
  type: feedback
---

長時間ジョブ（Euromonitor DL、海外事業調査F群のWindows処理など）で、「状況？」「ステータス教えて」「どこまで進んでる？」が複数セッションで繰り返された。

**Why:** 根拠は 37669bd4（10/23頃、Euromonitor、「残り何本？」「状況？」×2「終わった？」）、c8c7197f（10/20頃、海外事業調査F群、「ステータス確認」「ステータス教えて」×3）、f0b53a22（10/19頃、Windows処理、「状況どう？」×2、「止まっていた感じがしたけど大丈夫？」）。

**How to apply:** 開始時に進捗確認の手段（ログ・状態ファイル・監視）を決める。節目や一定間隔で「完了数/残り/止まっていないか」を伝える。停止に気づいたらTeams通知（[[teams_webhook]]）。

関連: [[work_status_protocol]]
