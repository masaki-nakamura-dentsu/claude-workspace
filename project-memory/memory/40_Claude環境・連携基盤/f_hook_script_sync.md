---
name: f_hook_script_sync
description: 同期されるsettings.jsonのhookが ~/.claude 直下のスクリプトを呼ぶと他マシンでプロンプトがブロックされる
metadata:
  type: feedback
---
2026-10-21、UserPromptSubmit hook（context_warn.py）が個人Macに無く、全プロンプトがブロックされた。
**Why:** settings.jsonは.claude-syncで3台に同期されるが、~/.claude/*.py は同期されない。
**How to apply:** hookスクリプトは `.claude-sync/Scripts/hooks/` に置いて全台へ配布し、他マシンへのrelayも同時に出す。可能なら `[ -f x ] && python3 x || true` のように、ファイルが無くても失敗しない書き方にする。[[mac_handoff_relay]]
