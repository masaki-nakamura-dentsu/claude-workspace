---
name: feedback-launchd-reload-without-runatload
description: RunAtLoad付きlaunchdジョブの設定(環境変数等)を変えて読み込み直すときは、即実行されて投稿・DLが走らないようRunAtLoadを一時的に外して読み込み、ファイルは元に戻す
metadata:
  type: feedback
---

launchdは設定ファイルを読み込み直さないと環境変数などの変更が反映されない。しかしRunAtLoad=trueのジョブは読み込んだ瞬間に1回実行される(例: 2026-10-12、AI Teamsダイジェストの予備ジョブ。今週分が未実行だったため、読み込み直すとその場でTeams投稿されるところだった)。

**Why:** 設定を変えただけなのに投稿・ダウンロード・通知が予定外に走ると、ユーザーにとっては「勝手に動いた」ことになる。

**How to apply:** ①元のplistを退避 → ②`PlistBuddy -c "Delete :RunAtLoad"` → ③`launchctl bootout` → `bootstrap` → ④元のplistをファイルに戻す(次回ログイン時は元の設計どおりRunAtLoadが効く) → ⑤`launchctl print`で新しい値になっていて`runs = 0`であることを確認する。読み込み直す前に、スクリプト側に二重実行の防止(stateファイル)があるかどうかと、それが今回効くかどうかを見ておく。関連: [[browser_account_routing]]
