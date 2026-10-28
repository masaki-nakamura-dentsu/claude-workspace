---
name: feedback_senduserfile_not_visible_in_vscode
description: このVSCode拡張機能セッションではSendUserFileツールで送ったファイルがユーザー側に見えないことがあった(2026-08-24実例)。ファイル納品はDropbox上の可視パスに直接保存し、パスを伝える方式を優先する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 24064df7-8ad4-4237-9afc-6c145606ca8d
  modified: 2026-08-24T21:12:45.834Z
---

2026-08-24、ICSファイル(自動化タスクスケジュール)をSendUserFileツールで送付したところ、ツール結果は「1 file delivered to user」と成功表示されたにもかかわらず、本人から「ICSファイルはどこに送付しているのですか？見れません」と言われた。原因は未特定(VSCode native extension環境特有の表示問題の可能性)だが、再現性がありそうなので運用を変更した。

## 対応
scratchpad(一時ディレクトリ)からユーザーの実際のDropboxフォルダ(`/Users/maxakisan/ICPTokyo2022 Dropbox/中村正樹/...`)へ`cp`でファイルを直接コピーし、絶対パスをテキストで伝える方式に切り替えたところ、本人が問題なく開けた。

## How to apply
このセッション(VSCode拡張、Claude Code)でファイルを納品する際は、SendUserFileだけに頼らず、**Dropbox配下の実パスにファイルを直接保存し、そのパスをテキストで案内する**ことを基本とする(特にファイル整理ルール[[feedback_claude_work_folder_organization]]に従い`Claude作業フォルダ/<タスク名>/`配下に置く)。SendUserFileは補助的に使ってもよいが、「見れない」と言われたら疑わず即座にこの代替手段に切り替える。他のCLI/ターミナル環境(VSCode拡張でない場合)ではSendUserFileが正常に機能する可能性もあるため、環境によって挙動が違う前提で都度確認する。
