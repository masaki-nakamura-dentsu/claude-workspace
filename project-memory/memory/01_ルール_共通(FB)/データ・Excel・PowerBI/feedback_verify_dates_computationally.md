---
name: feedback-verify-dates-computationally
description: When a date/weekday fact matters for scheduling logic, compute it in code rather than reading it off a screenshot or UI label — screenshot text for weekday/day labels is easy to misread and hard to double-check visually.
metadata:
  node_type: memory
  type: feedback
  originSessionId: b66a1c5e-c0ed-40c3-9c83-46a8e8714a9a
  modified: 2026-09-06T00:27:35.274Z
---

2026-09-06、[[photo_club_contact_sheet_pdf_workflow]]の自動化(МФК PHOTOS/モスクワ写真部の定例会スケジュール)で、Outlookカレンダーの検索結果スクリーンショットを見て「定例会は毎月最終日曜日」と判断しかけた(結果一覧の日付の横に小さく表示されていたラベルを「日」=日曜と読んだ)。実際にはPythonの`datetime.date(...).strftime('%A')`で全候補日を計算し直したところ全て土曜日だった。ユーザーからも「定例会は月末の土曜日です。日曜日ではありません」と直接訂正が入った。

**Why**: スクリーンショットの小さいテキスト(曜日ラベル、日付の一部)は視覚的に誤読しやすく、しかも「見た目で合っていそうだ」という確信を持ちやすいため、コード側での二重チェックを省略してしまいがちになる。曜日はほぼ必ずコードで機械的に検証可能な事実であり、目視確認だけに頼る理由がない。

**How to apply**: 曜日・月末日・「第n営業日」など日付計算が絡む事実は、スクリーンショットや画面表示のテキストを読んだだけで確定させず、必ず`python3 -c "import datetime; print(datetime.date(Y,M,D).strftime('%A'))"`等で計算して裏取りする。特に、その事実を元にlaunchd/cron/RRULE等の繰り返しスケジュールを組む場合は、間違えると発火タイミングがずれる(サイレントに1日ずれる等)ため、実装前に必ず計算で確認する。[[feedback_verify_against_ground_truth]](一次情報確認の一般則)の日付版として扱う。
