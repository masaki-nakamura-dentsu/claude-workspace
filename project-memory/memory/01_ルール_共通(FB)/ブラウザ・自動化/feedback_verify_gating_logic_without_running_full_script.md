---
name: feedback-verify-gating-logic-without-running-full-script
description: "When verifying a fix to gating/skip logic inside a script that has real side effects if the gate passes (launches a browser, sends notifications, downloads real data, etc.), test the gate function in isolation — never execute the whole script to 'see what it prints'"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8295d78a-e70b-414d-95cf-dfb851f0e805
  modified: 2026-09-14T05:39:18.380Z
---

Never run a full script end-to-end just to check whether its gating/skip condition evaluates correctly, if passing that gate triggers a real side effect (browser automation, Teams/email notification, actual file download, external API call). Instead, import and call the specific gate function in isolation, e.g. `python3 -c "from module import gate_func; print(gate_func(...))"`.

**Why**: During [[sf_reports_qbr_download_automation]] work on 2026-09-14, after fixing `retry_1815_if_missed.py`'s skip-condition logic, ran `python3 retry_1815_if_missed.py` directly to confirm the new logic worked. The gate correctly evaluated to "not yet done," which meant the script's designed behavior — actually launching the real 18-report Salesforce download pipeline — kicked in exactly as intended, duplicating that day's already-successful downloads and nearly sending an unwanted Teams confirmation message to the user mid-afternoon. Caught it by watching the log and killed the background task before it reached the browser/Teams step, but this was luck (noticed via log tail within ~10-15 seconds), not a safe-by-design test.

**How to apply**: Before running any script whose entire job is "decide whether to trigger action X, then do X," ask whether the goal right now is to verify the decision or to actually perform X. If it's just the decision, isolate and call that one function/check directly rather than executing the script's `main()`/`__main__` block. This applies broadly — not just to this Salesforce pipeline — to any cron/launchd-style automation with a guard clause in front of a real side effect (deploy scripts, notification dispatchers, data-sync jobs, etc.).
