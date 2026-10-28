---
name: feedback_teams_notify_sh_is_source_only
description: teams_notify.shはsource専用。bashで直接実行すると何も送られない。対話からはpython3 teams_notify.pyのCLIで送る
metadata:
  type: feedback
---
2026-10-21、`bash teams_notify.sh DONE ...` で送ろうとしたが、Teamsに届かなかった。このファイルは関数 `notify_teams` を定義するだけで、エラーも出ない。
**Why:** 送信が失敗しても無言なので、届いたと誤って報告しかねない。
**How to apply:** 対話セッションからは `zsh -c 'source ~/.zshenv; python3 <notify>/teams_notify.py DONE "ジョブ" "要約" --detail "..."'` を使う。シェルから使う場合は `source teams_notify.sh; notify_teams ...`。関連 [[webhook_autofix_project]]。
