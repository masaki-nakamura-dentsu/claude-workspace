---
name: feedback-powerautomate-aicon-browser-manual-only
description: aicon@dentsu.co.jp共有アカウントを使うPower Automate作業では、ブラウザ操作はユーザー本人が行い、Claudeは指示があった時だけ操作する(トークン節約)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0435a50a-a2ed-4d66-a1a6-9879a08f83a6
  modified: 2026-08-13T00:52:52.627Z
---

[[powerautomate_attendance_summary_project]]の障害対応中(2026-08-13、d14461)に明示された、このプロジェクト限定のルール。

**ルール**: aicon@dentsu.co.jp(戦略企画部の共有アカウント)を使うPower Automate作業では、Claudeが専用ブラウザプロファイル/ウィンドウを起動してログイン画面まで用意するのはよいが、**ログイン操作および以降のブラウザ操作は基本的にユーザー本人が行う**。Claudeがブラウザを実際に操作してよいのは、ユーザーがそのつど明示的に指示したときだけ。

**Why**: aiconは中村さん個人のアカウントとは別IDなので、共有ボットブラウザ(個人アカウント用、[[shared_bot_browser]])とは分離した専用プロファイルが必要になる。加えて、[[feedback_reduce_browser_automation_tokens]]の一般方針(スクリーンショット多用は高コスト)を、この特定プロジェクトでは「そもそも自動操作させない」レベルまで厳格に適用したいというユーザーの明示的な選好。

**How to apply**: このプロジェクトでPower Automate/aicon関連の作業依頼が来たら、まず必要ならブラウザ(プロファイル`/Users/d14461/.chrome-profiles/powerautomate-aicon-bot`、port 9229、d14461の場合)を起動してログイン画面を用意するところまでは自発的にやってよいが、その先(実際にクリックする、フローを開く、等)はユーザーから「これをやって」という具体的な指示が来るまで待つこと。他のプロジェクト([[shared_bot_browser]]を使う Salesforce/Teams/Outlook等)には適用しない、本プロジェクト限定の例外。

**2026-08-13追記(ユーザー明示確認)**: 「AICON用のブラウザは別で立ち上げてもよい」と明言された。つまり専用プロファイル/ウィンドウを別途起動する行為自体は毎回許可を取らずに標準的にやってよい(既存のd14461: port 9229 / `~/.chrome-profiles/powerautomate-aicon-bot`のように、他Macでも同様のaicon専用プロファイルを新規に起動してよい)。制約が残るのは「起動後の実際の操作(クリック・入力等)はユーザー指示があるまで待つ」という部分のみ。
