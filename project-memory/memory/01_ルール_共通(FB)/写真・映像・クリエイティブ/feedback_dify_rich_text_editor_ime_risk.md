---
name: feedback-dify-rich-text-editor-ime-risk
description: "Keyboard-shortcut automation (Cmd+A etc.) inside Dify's rich-text SYSTEM prompt editor can insert stray characters under the ja-JP Chrome locale; use clipboard paste instead of raw keyboard select-all"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 84978898-dfb7-4599-a7c7-1acda18aba04
  modified: 2026-09-11T08:26:23.162Z
---

While live-editing the Dify "GBC Agency OS" chatflow's LLM node SYSTEM prompt (a CodeMirror-like
rich-text editor) via Playwright/CDP on the shared bot browser (`--lang=ja-JP` Chrome), sending
`page.keyboard.press('Meta+A')` followed by `Meta+C` produced a stray inserted character
(`a decision-ready` became `aハン decision-ready`) even though neither keypress should mutate
content. Root cause not fully confirmed but most likely IME interference under the ja-JP locale
intercepting/converting a raw keypress mid-editor-focus. Caught immediately via character-count
diff (25867→25868) and fixed with `Meta+Z` (undo), confirmed clean via char count and visual
diff, and confirmed via Dify's own publish-version history that the corruption never reached a
published version.

**Why**: This happened on a live, shared, actively-in-use production system (a PoC other dentsu
staff were testing), so even a one-character corruption in a 25KB SYSTEM prompt is a real risk —
undetected, it could have silently shipped a broken instruction set to everyone using the Skill.

**How to apply**: When automating text replacement inside any rich-text/code editor (Dify SYSTEM
prompt fields, and likely similar CodeMirror/Monaco-based editors elsewhere) on a `--lang=ja-JP`
Chrome profile, do NOT use raw `Meta+A`/keyboard-shortcut select-all as the mechanism to select
existing content before replacing it. Instead: (1) write the new full text to the OS clipboard via
`context.grantPermissions(['clipboard-read','clipboard-write'], {origin})` +
`page.evaluate(() => navigator.clipboard.writeText(text))`, (2) click into the editor on a blank
margin (not mid-text, to avoid accidental word-selection), (3) select-all and paste as a single
atomic `Meta+V` operation rather than separate select/copy/inspect steps, (4) immediately verify
via character count AND a visual screenshot diff of the start/end of the text before considering
the edit done, (5) never click "publish"/"公開する" until that verification passes. If a
corruption is caught, `Meta+Z` (undo) worked reliably to revert it — check character count returns
to the pre-edit value as confirmation. Also verify via the platform's own version/publish history
(if available, as Dify's is) that no corrupted state was ever published, not just that the current
draft looks clean.
