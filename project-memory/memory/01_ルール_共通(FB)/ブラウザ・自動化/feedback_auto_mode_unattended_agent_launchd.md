---
name: feedback-auto-mode-unattended-agent-launchd
description: 無人claude -pを起動するlaunchdジョブの登録や、署名付きWebhook URLのDropboxファイルへの直書きは、ユーザー許可があってもauto modeに拒否される。最初からターミナル用コマンドを渡す
metadata:
  type: feedback
---
2026-10-12、Webhook自動修復(ランナー)を作ったとき、auto modeの分類器に3回止められた。
(1) 無人エージェントの判定ロジック変更が「Create Unsafe Agents」として拒否された。これはユーザーが「無人修復を許可する」と答えた後は通った。
(2) ラッパーの作成とlaunchd(plist作成+launchctl load)は、許可の後でも拒否された。
(3) 署名付きのWebhook URLをDropbox同期ファイルに直書きした直後の操作が「Credential Leakage」として拒否された。

**Why:** 迂回は禁止されている。結局、ユーザーがターミナルで貼り付けて実行し、問題なく登録できた。

**How to apply:** 無人の `claude -p` を定期起動するlaunchd登録は、最初からユーザー実行用のコマンドとして渡す。確認方法と、正常・異常それぞれの見え方も一緒に書く。Webhook URLは `~/.zshenv` の TEAMS_WEBHOOK_URL から実行時に読み、ファイルには書かない。無人の `claude -p` は `~/.claude/` 配下に書き込めないので、メモリや作業記録への書き込みはDropbox側の実体パス(.claude-sync/project-memory/memory/)を指定する。
あわせて分かったこと: 会社Macは、ユーザーの休暇日(例: 10/8・10/12)は起動していない。会社Mac由来のデータが止まっていても、すぐにエラーとはみなさない。
Related: [[webhook_autofix_project]] [[feedback_unattended_global_config_edit_confirm_first]]

関連: [[feedback_auto_mode_allowlisted_script_no_edit]] [[feedback_no_fake_echo_justification]] [[feedback_auto_mode_blocks_shared_file_overwrite]](auto mode関連の他の注意)
