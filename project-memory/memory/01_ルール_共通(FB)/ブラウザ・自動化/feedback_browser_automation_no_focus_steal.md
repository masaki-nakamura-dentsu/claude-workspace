---
name: feedback-browser-automation-no-focus-steal
description: "All Playwright/Chrome browser automation (Salesforce, ChatGPT, Gemini, Google Maps, etc.) must not steal foreground focus or pop visible windows in front of the user's active work"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d4c639f0-5e2e-444f-aef8-00fa7bd9a949
  modified: 2026-08-07T05:42:38.738Z
---

Whenever launching a Chrome instance for browser automation (Salesforce export scripts, [[chatgpt_web_automation]], [[gemini_web_automation]], Google Maps list saving, or any future debug-port/Playwright-driven browser task), the window must not come to the foreground or interrupt whatever the user is actively doing on screen.

**Why**: Stated explicitly 2026-08-07 during Salesforce report investigation, after repeated automated browser launches kept popping visible windows in front of the user mid-task. The user was annoyed enough to interrupt and give this as a standing rule, explicitly generalizing it beyond Salesforce to "other work too, including AI image generation."

**How to apply**: Default to `headless=True` for Playwright launches where interactive login isn't required in that specific run. Where a visible browser is genuinely needed (e.g. first-time interactive SSO login, or debugging by screenshot), avoid explicitly focusing/activating it, don't repeatedly relaunch it (each relaunch can steal focus again), and prefer background/off-screen techniques (e.g. launching without bringing to front, using a secondary display area, or minimizing immediately after launch) over anything that forces the window frontmost. If a task requires several diagnostic attempts, batch them into as few launches as possible rather than spawning a new visible browser per attempt — related to [[feedback_avoid_mfa_churn]]'s "don't repeatedly kill/restart SSO-login browser automation" guidance, but broader: this is about screen/focus disruption specifically, not just login churn.

See [[feedback_browser_automation_standing_practices]] for the consolidated set of standing browser-automation rules this is one of.
