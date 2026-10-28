---
name: feedback-browser-automation-standing-practices
description: "Consolidated pattern (2026-08-24 memory review) of six standing rules for ALL Playwright/Chrome browser automation (Salesforce, Teams, ChatGPT, Gemini, Google Maps, Power Automate, etc.): stay headless/off-screen, minimize screenshot token cost, don't churn MFA sessions, verify destination before an irreversible send, default to using it proactively, and parallelize independent generations"
metadata:
  node_type: memory
  type: feedback
  originSessionId: memory-weekly-review-20260824
  modified: 2026-09-02T00:35:25.112Z
---

Six separate feedback incidents, all about how Claude should operate Playwright/Chrome browser automation across every project that uses it ([[shared_bot_browser]], [[chatgpt_web_automation]], [[gemini_web_automation]], Salesforce/Teams/Power Automate work). Kept as one place to check before any new browser-automation task, since the individual lessons came from different projects but apply universally.

## The six rules
1. **Never steal focus, and minimize whenever no user action is needed.** Default `headless=True`; where a visible window is genuinely needed (first-time SSO login, screenshot debugging), don't force it frontmost, don't repeatedly relaunch it. See [[feedback_browser_automation_no_focus_steal]]. **Escalated 2026-09-02**: for the non-headless shared bot browsers (which must stay visible-capable for persistent-profile SSO reuse), the old "reposition off-screen to -3000,-3000" trick is not enough — the user hit it live when a Salesforce download's UI bled into a screen-shared meeting. Standard is now to actually **minimize the OS window** (CDP `Browser.setWindowBounds` with `bounds: {"windowState": "minimized"}`, falling back to the off-screen trick only if minimize fails) for any browser automation step that doesn't need the user to see or act on it — not just downloads, all unattended browser automation. Do this as early as possible (right after `new_page()`/`connect_over_cdp`, before `goto`), not after some delay where the window is briefly visible. Already patched 2026-09-02: `~/SalesforceExport/reports_pipeline/download_all_reports.py`, `~/CASExport/cas_download.py`, `~/TeamsExport/teams_daemon.py` (minimizes once after login confirmation — this one is the most impactful fix since it's the always-running daemon that had no window-hiding at all, so the shared browser sat visible on-screen indefinitely), `~/TeamsExport/scripts/weekly_ai_digest.py`. Other on-demand browser-automation scripts (ChatGPT/Gemini bots, Google Maps, TimeTree, JCI pitchlist, GBC Smart-KINMU, Salesforce weekly-report scripts, teams_cli) don't have this yet — apply the same minimize pattern to each opportunistically the next time it's touched or run, same as the existing shared-browser migration policy in [[shared_bot_browser]].
2. **Minimize screenshot/token cost.** Get facts via `innerText()`/`getAttribute()`/`evaluate()` (text) rather than full-page screenshots; screenshot only on first-time layout discovery or a cropped `element.screenshot()`; batch several operations before checking once instead of checking after every click. See [[feedback_reduce_browser_automation_tokens]].
3. **Don't churn MFA/SSO sessions.** Do all iteration/debugging inside one logged-in browser session rather than killing and relaunching the process repeatedly — each relaunch can force a fresh interactive MFA prompt. See [[feedback_avoid_mfa_churn]].
4. **Verify the destination before an irreversible send.** Immediately before and after any paste/submit/click that posts or sends something (a Teams message, a Salesforce update), re-confirm the current page/chat/record identity — never assume state hasn't drifted, especially if a concurrent daemon might be manipulating the same DOM. See [[feedback_verify_destination_before_shared_browser_send]].
5. **Default to using it, don't wait to be asked again.** Once a browser-automation recipe exists for a service (ChatGPT/Gemini image gen, image search), reach for it proactively in any project/chat that needs that capability, not just the one it was first built for. See [[feedback_use_ai_web_automation_proactively]].
6. **Parallelize independent generations.** When more than 1-2 images/items need generating via the same web UI, run multiple browser tabs concurrently (worker-pool pattern) instead of looping sequentially — watch for rate-limit modals at high concurrency. See [[feedback_parallel_tab_image_generation]].

## Known scoped exception
[[feedback_powerautomate_aicon_browser_manual_only]] narrows rule 5 for one specific account (aicon@dentsu.co.jp): Claude may prepare the login window but must wait for explicit per-action instructions before clicking anything — a project-specific tightening, not a contradiction of the general default.

## How to apply
Before writing or running any new browser-automation script, check this file first — most individual mistakes that prompted the six source memories were violations of a rule that had already been learned in a *different* project. Treat all six as defaults for every browser-automation task, not just the project each was discovered in.

関連: [[feedback_close_tabs_after_browser_work]] [[feedback_close_bot_browser_when_done]](作業後の後片付け)
