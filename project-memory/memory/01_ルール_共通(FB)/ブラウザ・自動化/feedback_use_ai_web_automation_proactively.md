---
name: feedback-use-ai-web-automation-proactively
description: User explicitly wants ChatGPT and Gemini web browser automation used proactively across all chats/projects, not just where first set up
metadata:
  type: feedback
  originSessionId: fc9a2fff-4ac2-4c64-8ec5-4fd6c0f41f81
  modified: 2026-08-22T12:18:16.412Z
---

After the ChatGPT web-automation setup ([[chatgpt_web_automation]]) worked well in [[toyota_india_aot_hyryder_project]] (driving actual image generation end-to-end rather than just handing off prompts), the user said explicitly: "今後も他のチャットでも連携してください" (keep using this in other chats going forward too) and asked for Gemini/NanoBanana set up the same way ([[gemini_web_automation]]).

**Why**: removing the manual round-trip (write a prompt → user pastes it → user pastes result back) is a real time savings the user values, confirmed twice in one session (once by asking to run ChatGPT directly, again by asking for the same for Gemini after it had previously been abandoned due to that exact friction — see [[gemini_nanobanana_setup]]).

**How to apply**: whenever a task in *any* project/chat calls for generating images, or otherwise interacting with ChatGPT's or Gemini's web UI, default to driving it directly via the established browser-automation recipes rather than just writing prompt text for the user to run manually. Check whether the relevant debug-port Chrome profile is already running (`~/.chrome-profiles/chatgpt-bot` port 9224, `~/.chrome-profiles/gemini-bot` port 9225) before assuming a fresh login flow is needed — profiles persist login across sessions. This preference is general (not project-specific) — don't wait for the user to re-request it in a new chat.

**2026-08-22 addendum — photo/image search, not just generation**: user reported that in another chat, searching for reference photos of 地下鉄銀座線上野駅 (Ueno station, Ginza subway line) worked much better via Gemini than via Claude Code's own WebSearch — Gemini returned more and better photos. Root cause: Claude Code's `WebSearch` tool is a text-oriented web search, not an image search engine, so it's structurally weak at photo discovery/curation tasks. Gemini's web UI is backed directly by Google Image Search, which is stronger for this. **Apply**: for tasks that are specifically about finding/curating real photos (not generating them), prefer driving Gemini's web UI via the same browser-automation recipe (port 9225) over relying on Claude's own WebSearch, across all projects.

See [[feedback_browser_automation_standing_practices]] for the consolidated set of standing browser-automation rules this is one of.
