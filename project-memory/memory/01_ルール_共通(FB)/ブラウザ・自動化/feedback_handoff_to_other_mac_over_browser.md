---
name: feedback-handoff-to-other-mac-over-browser
description: もう一方のMacのローカルファイル操作で済む作業は、ブラウザ自動操作ではなくリレーで引き渡す(2026-10-19)
metadata:
  type: feedback
---
Dropbox Webでのフォルダ移動のように、会社Mac(または個人Mac)のローカルでファイルを見る・動かすだけで済む作業は、ブラウザを操作せず company_mac_inbox などのリレーで引き渡す。ブラウザを使うのは、そこでしかできない操作(共有の招待・参加など)に限る。

**Why:** 2026-10-19、Dropboxの共有のあと、Webの移動ダイアログを操作し続けていたら、中村さんから「ブラウザ操作にキャプチャなどトークンを使うものは使わないで。会社Macに引き渡せばファイル構造を見るだけで確認できるのでは」と言われた。

**How to apply:** ブラウザ操作を始める前に「もう一方のMacのファイル操作で済まないか」を確認する。済むならリレータスクにする。[[mac_handoff_relay]] [[feedback_reduce_browser_automation_tokens]]
