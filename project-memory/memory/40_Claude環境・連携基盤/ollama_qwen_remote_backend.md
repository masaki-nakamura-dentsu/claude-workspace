---
name: ollama_qwen_remote_backend
description: "Remote Ollama server (192.168.0.11:11434, model qwen3.8:27b) set up 2026-08-23 as a token-saving offload path for bulk/simple tasks"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d662d2bf-d31e-4cb4-980c-9ddcb8c022ed
  modified: 2026-08-23T05:47:48.076Z
---

Remote Ollama server at `192.168.0.11:11434` running model `qwen3.8:27b` (~17GB), set up 2026-08-23 as a lower-cost alternative to Claude Code tokens for bulk/simple work.

**Setup (personal Mac / ICPTokyo2022 only)**:
- `OLLAMA_HOST=192.168.0.11:11434` is exported in `~/.zshenv` (comment: "リモートOllamaサーバー(モデル qwen3.8:27b)"). `.zshenv` is NOT Dropbox-synced, so this only applies on this machine — the company Mac (d14461) or personal Windows would need the same line added separately if the user wants it there too.
- **2026-10-17 更新(個人Mac)**: `~/.zshenv` は `OLLAMA_HOST=desktop-ryzen5950:11434`(Tailscale名)に変更済み。自宅でも外出先でも届く。Windowsが停止していたら `.claude-sync/Scripts/windows_power/win_power.sh wake` で起動からOllamaまで立ち上がる(Ollamaはログオンしないと自動起動しないため)。詳細は [[home_network_setup]]。
- `ollama` CLI installed via `brew install ollama` (v0.32.15) on this Mac, since no local Ollama-based tool existed yet.
- Model pulled onto the *remote* server (not this Mac) via `OLLAMA_HOST=192.168.0.11:11434 ollama pull qwen3.8:27b` — confirmed present with `ollama list` / `curl http://192.168.0.11:11434/api/tags`.

**Usage pattern**:
```bash
# CLI, one-off
OLLAMA_HOST=192.168.0.11:11434 ollama run qwen3.8:27b "prompt here"

# API, from a script
curl http://192.168.0.11:11434/api/generate -d '{"model":"qwen3.8:27b","prompt":"...","stream":false}'
```

**Why this exists / how to apply**: this backend does NOT change what Claude Code itself uses (Claude Code always runs on Anthropic's Claude models; there's no way to redirect Claude Code's own reasoning to a local/remote Ollama model). It's only useful for separate scripts/tools that call the Ollama API directly, bypassing Claude Code tokens entirely. The "advise before offloading" rule is recorded directly in global `~/.claude/CLAUDE.md` (2026-08-23 entry), not duplicated here.

Good fits: large-volume summarization, classification, draft generation — repetitive tasks where some quality loss vs. Claude is acceptable.
Poor fits: anything needing deep context, nuanced Japanese, code editing, or judgment tied to the user's memory/history — i.e., most of what this user actually delegates to Claude Code.

**Standing instruction from the user (2026-08-23)**: before Claude processes a task itself that looks like it would consume meaningfully fewer Claude Code tokens if routed through this Ollama/Qwen backend instead, tell the user that option exists and ask before proceeding — don't just silently do the token-costly version.

No concrete offload script has been built yet as of 2026-08-23; the user hasn't named a specific task to migrate. When one is built (e.g. for Teams/email digest summarization — see [[ai_teams_weekly_digest]]), record the script location and invocation here.

**並列処理(2026-10-17 計測)**: Windows(RTX 3090 24GB、Ollama 0.32.15、OLLAMA_NUM_PARALLEL未設定=自動)は同時リクエストを並列で処理できる(Windows側の短い依頼では2件2.0倍・3件3.1倍・6件4.8倍、VRAM 19.9GB/24GBでCPUはみ出しなし)。ただし、資料本文を入れた長い依頼(数千字)では読み込みでGPUが埋まり、3件並列でも約1.1倍しか速くならなかった(アレココ要約照合: 1件ずつ10件/分 → 3並列11件/分)。長い依頼の大量処理は並列化より依頼を短くする方が効く。OLLAMA_NUM_PARALLELは明示設定しない方がよい(自動調整が効く)。個人MacのローカルLLMは使わない([[feedback_no_personal_mac_local_llm]])。

関連: [[feedback_shutdown_windows_after_use]](使用後はWindowsをシャットダウン)
