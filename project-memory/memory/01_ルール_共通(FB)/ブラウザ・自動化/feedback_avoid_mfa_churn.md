---
name: feedback_avoid_mfa_churn
description: "Don't repeatedly kill/restart browser automation processes that require interactive MFA login to debug them — batch diagnosis into one session instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b8fb3d93-93e1-4986-955c-081a6878f921
---

When debugging a Playwright/browser-automation script that logs into a Microsoft/dentsu SSO session (e.g. [[continuous_data_capture_setup]]'s Teams daemon), avoid killing and relaunching the browser process multiple times in a row to iterate on a fix.

**Why**: dentsu's SSO session doesn't survive process kills cleanly — each relaunch after an abrupt `kill`/`pkill` tends to invalidate the saved session, forcing the user through interactive SSO + MFA again. During the 2026-07-14 session, iterating on a DOM-selector bug this way triggered ~4 unplanned MFA prompts in a row, and the user had to explicitly ask "何度もTeamsの認証画面が出るのを止められませんか？" (can you stop making the auth screen appear over and over?).

**How to apply**: When a fix requires inspecting live DOM/browser state that needs a login, do all the inspection and iteration *within a single browser session* (e.g. one script that logs in once, then runs multiple diagnostic checks / retries the same page without closing the context) rather than editing code and relaunching the process repeatedly. If a fix genuinely can't be verified without a fresh process, say so explicitly and ask before spending another login on it, rather than doing it silently.

See [[feedback_browser_automation_standing_practices]] for the consolidated set of standing browser-automation rules this is one of.
