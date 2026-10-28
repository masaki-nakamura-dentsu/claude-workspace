---
name: feedback_shutdown_windows_after_use
description: 個人Windows(Ollama/RTX3090)を使う作業が終わったら、Claudeがwin_power.shでシャットダウンする。電気代のため(2026-10-17指示)
metadata:
  type: feedback
---

個人Windows(desktop-ryzen5950)を使う作業(Ollama/Qwenでの要約・分類、ssh作業など)が終わったら、Claudeが自分でシャットダウンする。起動が必要なときは `win_power.sh wake` で起こし、作業後に `win_power.sh shutdown`(Ollamaが直前に使われていたら止めない安全版、60秒後)で落とす。

**Why:** 電気代が高いので、つけっぱなしにしたくない(2026-10-17 中村さん)。

**How to apply:**
- スクリプト: `.claude-sync/Scripts/windows_power/win_power.sh`(status/wake/ollama/shutdown/shutdown-now/cancel)。詳細は [[home_network_setup]]、Ollamaの使い方は [[ollama_qwen_remote_backend]]。
- 作業の最後に `status` で「停止中」になったことを確かめてから報告する。
- 自分が起こしていなくても、作業でWindowsを使ったなら終わったら落とす。ただし Windows側でユーザー本人や別セッションが作業中かもしれないとき(windows_inbox に in_progress のタスクがある、直前にOllamaが使われている等)は落とす前に確認する。
- 2026-10-17時点で、個人MacのlaunchdにWindowsのOllamaに依存するジョブは無い(homebrew.mxcl.ollama は個人Mac内のもので無関係)。

関連(落とす前の確認チェックリスト・WoL復帰手順はこちら): [[feedback_windows_auto_shutdown]]
