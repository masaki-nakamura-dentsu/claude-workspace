---
name: feedback-close-bot-browser-when-done
description: 作業用ブラウザ(CDPのbotブラウザ)は、その用事が終わったら閉じる。開きっぱなしにしない
metadata:
  type: feedback
---

2026-10-15、エアコン見積もり依頼で使った個人用ブラウザ(9230 maxakisan-bot)のミツモア・エアコン総本舗のタブが開きっぱなしになっており、ユーザーから「用事が終わったら閉じるように」と指摘された。

**Why:** 画面やDockに残り続けて邪魔になる。ログイン情報はプロファイルに残るので、閉じても次回再ログインは基本不要。

**How to apply:** ブラウザ操作の一区切り(送信完了の確認まで)がついたら、CDPの `Browser.close` でそのbotブラウザを閉じる(常駐が前提の共有ブラウザ、例: 会社Mac 9226 や定期ジョブ用は、自分が開いたタブだけ閉じる)。ユーザーに画面を見せるために前面に出した場合も、ユーザーの作業終了を確認したら閉じる。[[shared_bot_browser]] [[feedback_browser_automation_no_focus_steal]]

関連: [[feedback_close_tabs_after_browser_work]](共有ブラウザはタブ単位で閉じる)
