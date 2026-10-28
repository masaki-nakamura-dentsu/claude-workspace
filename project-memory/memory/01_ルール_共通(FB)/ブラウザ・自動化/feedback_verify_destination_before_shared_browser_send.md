---
name: feedback_verify_destination_before_shared_browser_send
description: "Standing rule: any script that sends/posts via the shared bot browser (Teams, Salesforce, etc.) must verify it actually landed on the intended destination immediately before pasting/sending, and abort rather than send blindly — especially when a background daemon (e.g. teams_daemon.py) may be manipulating the same DOM concurrently"
metadata:
  type: feedback
  originSessionId: 86655793-9c0c-4cdd-867b-e20342b361f7
  modified: 2026-08-18T08:31:54.494Z
---

Discovered 2026-08-18 while building [[ai_teams_weekly_digest]]'s auto-post-to-Teams feature. A test run of the posting script (`post_html_to_self_chat` in `weekly_ai_digest.py`) happened to overlap with `teams_daemon.py`'s own scheduled poll cycle, which was actively clicking through dozens of chats in the same shared browser (port 9226, see [[shared_bot_browser]]). The posting script read the left-rail treeitem list, then clicked the index it believed was the self-chat — but by the time the click executed, the daemon's concurrent DOM manipulation had shifted what was actually at that index, and the script landed on a real colleague's 1:1/group chat instead. The script had no verification step and reported success regardless (`page.keyboard.press("Enter")` never raises even if nothing happened) — this was a **silent failure that could just as easily have been a real misdirected send to an unintended person**, only avoided because the paste/send itself also failed to land anywhere (confirmed by grepping the daemon's own freshly-collected `teams_messages.jsonl` for the digest's distinctive text and finding it nowhere but the correct self-chat entries).

**Why this matters**: sending a message to the wrong chat via automation is a real, visible-to-others mistake (per the "actions with care" principle around anything visible to others) — and unlike most automation bugs, it can happen with zero exception, zero error output, and zero indication anything went wrong, because the click/paste/send calls all "succeed" from Playwright's perspective even when they acted on the wrong element.

**How to apply**: any future script that sends/posts content via this shared browser (Teams self-chat, Salesforce record updates, any future automation) must, immediately before and after the point of no return (paste, submit, send):
1. Re-verify the current page/chat/record identity (e.g. `page.title()` contains an expected marker) right after navigating/clicking to it — not just once at the start, but again immediately before the send action, since state can drift between steps.
2. Abort with a raised exception (not a silent `return`) if verification fails at any checkpoint — never fall through to sending on unconfirmed state.
3. After sending, verify the effect actually happened (e.g. message count increased in the expected chat) rather than assuming success from the absence of an exception.
4. Where practical, avoid scheduling manual/test automation runs while a known concurrent background job (teams_daemon.py's 30-min poll, or any other shared-browser daemon) might be active — check its log for a recent "poll complete" line first. This isn't a substitute for verification (concurrent runs can still happen unexpectedly), but reduces how often the defensive path gets exercised.

This pattern (read state → act → verify before/after irreversible step) should be the default for all shared-browser send/post/submit automation going forward, not just this Teams digest feature.

See [[feedback_browser_automation_standing_practices]] for the consolidated set of standing browser-automation rules this is one of.
