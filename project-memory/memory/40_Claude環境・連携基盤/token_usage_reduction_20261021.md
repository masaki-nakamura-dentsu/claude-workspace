---
name: token_usage_reduction_20261021
description: 2026-10-21 会社Macのトークン固定費削減(MEMORY.md 2段索引化・superpowers無効・context警告hook)。新セッション固定費28.9k
metadata:
  type: project
---
- MEMORY.md(22KB)を12フォルダの目次だけにし、詳細は各フォルダの INDEX.md へ移した。バックアップは _backups/20261021_before_index_split。週次レビューの指示書にも、この形式を守るよう追記。
- superpowers を無効化。settings のバックアップは ~/.claude/settings.json.bak_20261021。UserPromptSubmit hook ~/.claude/context_warn.py が、12万トークン超で/clearを勧める注意を差し込む(Claudeへの送信はそのときだけ)。
- agencyサブエージェント8体は、開発中のためグローバル(~/.claude/agents)に残す。一度プロジェクトへ移したが、本人の指示で戻した。
- ~/.claude/statusline_tokens.py は会社Macに存在しない(statusLine設定だけが残っている)。
- relay task-021 は完了。新セッションの/contextで固定費28.9k(tools 15.3k / skills 5.8k / memory 3.0k)。
Related: [[mcp_on_demand]] [[memory_weekly_review_automation]] [[mac_handoff_relay]]
