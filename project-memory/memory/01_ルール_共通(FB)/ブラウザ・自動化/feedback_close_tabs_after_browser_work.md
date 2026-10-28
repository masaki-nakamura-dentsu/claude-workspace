---
name: feedback-close-tabs-after-browser-work
description: 共有ボットブラウザ等で作業に使ったタブは作業終了時に閉じる(Teams等の常用タブは残す)。全作業共通
metadata:
  type: feedback
---
ブラウザ自動操作で自分が開いた/使ったタブは、作業が終わったら閉じる。対象は勤務登録に限らず全作業。Teams・Outlook・他の定期ジョブが使う常駐タブ(例: esq365-myのOneDriveタブ、teams.cloud.microsoft)は閉じない。

**Why:** 2026-10-15、勤務登録後にsmtkin・SKBタブが開きっぱなしでユーザーから指摘。

**How to apply:** 閉じるのは `page.close()` だけ(`browser.close()`/`context.close()`は禁止、[[shared_bot_browser]])。最後の1枚まで閉じるとウィンドウが消えるので、残りが0になるなら閉じない。勤務登録は `~/SmartKinmuReg/closetabs.js` を最後に実行。[[smart_kinmu_personal_registration]]

関連: [[feedback_close_bot_browser_when_done]](専用botブラウザはブラウザごと閉じる)
