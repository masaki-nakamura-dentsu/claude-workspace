---
name: mcp_on_demand
description: claude.aiコネクタ(Gmail等)とgithub/context7プラグインを既定オフにした設定と、必要時に一時的にオンにする方法
metadata:
  type: project
---
2026-10-21、トークン節約のため個人Mac(maxakisan)の `~/.claude/settings.json` を変更した。
- `env.ENABLE_CLAUDEAI_MCP_SERVERS="false"` → claude.ai コネクタ(Gmail、Claude Docs等)をすべて読み込まない。
- `enabledPlugins` の github / context7 を false にした（どちらも認証エラーで接続できていなかった）。
- バックアップは `~/.claude/settings.json.bak_20261021`。
- 一時的にオンにする方法: `ENABLE_CLAUDEAI_MCP_SERVERS=true claude` で起動する。VS Code拡張の場合はsettingsの値をtrueに戻し、ウィンドウを再読み込みする。プラグインは `/plugin` から有効にする。
- settings.jsonはマシンごとの設定なので、会社Mac(d14461)には未適用。
同じ日に MEMORY.md をフォルダ別の圧縮形式に変更し（41.9KB→22KB）、CLAUDE.md を要点だけに縮めた（21KB→約5KB、旧全文は [[global_claude_md_full_history]]）。
