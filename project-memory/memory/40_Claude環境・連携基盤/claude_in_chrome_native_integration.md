---
name: claude-in-chrome-native-integration
description: "Claude Code has a native browser-automation integration (Claude in Chrome extension + `--chrome`/`/chrome`) distinct from claude.ai's own Chrome extension and distinct from the existing Playwright/CDP shared-browser setup"
metadata:
  type: reference
  originSessionId: session-2026-09-01-chrome-extension-inquiry
  modified: 2026-09-01T00:11:38.176Z
---

**What it is** (confirmed via code.claude.com/docs/en/chrome, 2026-09-01): Claude Code (CLI and VS Code extension) can connect to the "Claude in Chrome" browser extension (Chrome Web Store, `fcoeoabgfenejglbffodgkkbkcdhcgfn`, v1.0.36+) and get browser automation as native MCP tools (`claude-in-chrome` MCP server) directly inside a Claude Code session — read_page, get_page_text, find, click/type, tab/window management, screenshot, browser_batch, session-recording GIFs, file uploads to web forms, etc. This is **separate** from:
- claude.ai's own "Claude for Chrome" experience (runs inside claude.ai chat, not reachable from this CLI)
- The existing hand-rolled Playwright/CDP shared-browser setup documented in [[shared_bot_browser]] (port 9226 on d14461, port 9227 on ICPTokyo2022)

**Requirements**: Chrome/Edge/Chromium-based browser + the extension installed, a direct Anthropic plan (Pro/Max/Team/Enterprise), signed in via `/login` (API-key/long-lived-token auth keeps this off even with `--chrome`). Not available via Bedrock/Vertex/Foundry.

**How to enable**: `claude --chrome` at launch, or run `/chrome` anytime to check status/reconnect/enable-by-default/pick which connected browser to use. In the VS Code extension, it's available automatically whenever the extension is installed (no flag needed) — but still needs the one-time extension handshake. `/chrome` is an interactive slash-command — cannot be triggered programmatically by Claude itself; the user has to run it.

**Status as of 2026-09-01**: user installed the Chrome extension and asked (as a new global rule) that browser tasks prefer this over the existing automation for token efficiency. Checked via ToolSearch in this session — no `claude-in-chrome` MCP tools were exposed. Asked the user to run `/chrome`; they first tried it in a different chat panel entirely (a non-Claude tab labeled "チャット", model shown as "MAI-Code-1.1-Flash" — some other tool sharing the same VSCode sidebar, not Claude Code). Retried in the actual "CLAUDE CODE" tab and got: **"/chrome isn't available in this environment."**

**Conclusion**: this specific VSCode-native-extension environment does not support Chrome integration (the slash command itself is unavailable, not just unconnected — likely this surface predates/excludes that feature, or an org policy blocks it via `deniedMcpServers`). So the user's "use the Chrome extension for efficiency" instruction is **not actionable from this environment today**. Keep using the existing [[shared_bot_browser]] Playwright/CDP setup as before. Re-check periodically (e.g. next time the VSCode extension updates, or if the user switches to the standalone `claude` CLI in a terminal, where `--chrome` may work) rather than retrying `/chrome` repeatedly without a reason to expect it changed.

**Caveat from the docs**: "Enabling Chrome by default in the CLI increases context usage since browser tools are always loaded" — the docs themselves suggest using `--chrome` only when needed rather than enabling by default, which cuts against blanket "always prefer this" if the goal is token conservation. Worth weighing against [[feedback_token_conscious_practices]] once confirmed working — may want "use `--chrome`/`/chrome` on-demand per browser task" rather than always-on.

**Next step**: once user confirms `/chrome` shows Enabled/Installed, re-check via ToolSearch for the `claude-in-chrome` tools and start using them for new ad-hoc browser tasks (one-off lookups, testing, data extraction) in this VSCode session. Migrating the *existing* scripted automations ([[shared_bot_browser]], [[teams_cli]], [[chatgpt_web_automation]], etc.) is a separate, larger decision — those are unattended/scripted and `claude-in-chrome` is interactive-session-only, so it's not a drop-in replacement for background/scheduled jobs.

**Decided 2026-09-01**: user confirmed to keep using the existing Playwright/CDP automation for now, given `/chrome` is unavailable in this environment. Don't re-propose switching to Claude in Chrome unless the environment changes (standalone terminal `claude` CLI, or a VSCode extension update that adds `/chrome` support) or the user raises it again.
