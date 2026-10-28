---
name: feedback-parallel-tab-image-generation
description: User wants ChatGPT/Gemini image generation run across multiple browser tabs in parallel to cut wall-clock time, as a standing rule across all chats
metadata:
  type: feedback
  originSessionId: unknown
  modified: 2026-08-07T01:17:25.188Z
---

Stated explicitly 2026-08-07 during the Vietnam Blue Lock cross-promotion work (see `work_status/vietnam_anime_ip_cross_promotion_project.md`, 2026-08-07 entry): when a task requires generating multiple images via [[chatgpt_web_automation]] or [[gemini_web_automation]], open several tabs/pages in the same browser context and run the generations concurrently instead of one at a time. The user said explicitly this time-saving rule applies in *other chats too*, not just this project — same spirit as [[feedback_use_ai_web_automation_proactively]].

**Why**: sequential one-by-one generation wastes wall-clock time waiting on each ~30-60s render; running N tabs in parallel (via Playwright, multiple `context.newPage()` against the same debug-port browser) cuts total time roughly by the concurrency factor.

**How to apply**: whenever a task calls for generating more than 1-2 images via the ChatGPT/Gemini web-automation recipes, default to a worker-pool pattern (e.g. concurrency 4) submitting/polling multiple tabs at once, rather than looping sequentially. Practical ceiling observed: ChatGPT's web UI can throw a rate-limit modal (`#modal-conversation-history-rate-limit`) after a burst of ~12-15 generations in one session — if a tab's send-click times out because that modal is intercepting pointer events, wait ~60s and reload before retrying rather than treating it as a hard failure. Don't push concurrency so high it triggers this immediately (4 tabs worked fine for 15 images).

See [[feedback_browser_automation_standing_practices]] for the consolidated set of standing browser-automation rules this is one of.
