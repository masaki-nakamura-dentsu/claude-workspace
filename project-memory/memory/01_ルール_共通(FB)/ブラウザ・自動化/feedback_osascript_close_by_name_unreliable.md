---
name: feedback-osascript-close-by-name-unreliable
description: PowerPointのプレゼンをAppleScriptで閉じるとき、日本語名の whose name is 指定は別ファイルを閉じることがある。インデックスで名前を確認してから閉じる
metadata:
  type: feedback
---
`close (first presentation whose name is "日本語名.pptx") saving no` を実行したら、目的のNidecデッキではなく、別に開いていた「AI_Tips2026年10月分_20260929 1.pptx」が保存せずに閉じられた(2026-10-13)。日本語ファイル名の一致判定がUnicode正規化の違いで外れたとみられる。

**Why:** saving no で他のファイルを閉じると、未保存の編集を失わせる。今回は最終保存が10/6でAutoSave対象のため実害は小さいとみられるが、ユーザーに報告して開き直した。

**How to apply:** PowerPointのファイルを閉じる必要があるときは、`repeat with i from 1 to count of presentations` で `name of presentation i contains "<ASCIIの一部>"` を確かめてから `close presentation i` する。そもそも自分で開いたファイル以外は閉じない。可能ならユーザーに閉じてもらう。[[feedback_dont_overwrite_open_pptx]]

**追記(2026-10-13 午後)**: OneDriveの正本がPowerPointで開いているかは `lsof` では分からない(0件と出る)。書き込み前は `osascript -e 'tell application "Microsoft PowerPoint" to get name of every presentation'` で確認し、開いていたら書かずにユーザーに閉じてもらう。この確認を書き込み後に見てしまい、開いた状態の正本に上書きした。
