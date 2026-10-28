---
name: feedback_no_os_clipboard_in_browser_automation
description: ブラウザ自動操作でOSクリップボード/Meta+Vを使わない。ユーザーが別ブラウザを操作中だとそちらに貼り付く
metadata:
  type: feedback
---

万博ウォッチ(expo_watch.py)のTeams投稿が、ユーザーが操作中の別ブラウザに貼り付いてしまい、チャンネルに投稿されなかった(2026-10-28)。それでも `[OK] 投稿しました` が出ていた。

**Why:** `navigator.clipboard.write` + `Meta+V` はOS共通のクリップボードとフォーカスに依存する。
**How to apply:** 貼り付けは対象ページ内で `ClipboardEvent('paste')` を合成して行う(修正済み)。投稿後は再読込して実在を確認してから成功通知を送る。関連 [[feedback_long_job_progress_reporting]]
