---
name: feedback-unattended-global-config-edit-confirm-first
description: "Auto mode classifier blocks building automation that unattendedly edits global config files (e.g. CLAUDE.md) until the user explicitly approves full automation via AskUserQuestion"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3a502140-90c5-40df-90dc-68e1b6335ff0
  modified: 2026-08-22T22:07:33.324Z
---

When adding a step to an unattended/scheduled job (launchd + `claude -p`, cron, etc.) that would let it **edit a global, cross-project config file** (e.g. `~/.claude/CLAUDE.md`) without a human in the loop, expect Claude Code's auto mode classifier to block the Edit that wires this up, even though the user already approved the underlying analysis/idea.

**Why:** Observed 2026-08-23 while adding a weekly automated CLAUDE.md-improvement step (session log mining → CLAUDE.md edits) to the existing `com.nakamura.memoryweeklyreview` launchd job. The classifier denied the script edit outright with no specific reason beyond "risky automation." Asking the user directly via [[AskUserQuestion]] resolved it immediately — they approved full automation (edit CLAUDE.md automatically, not just propose+notify) in one round trip.

**How to apply:** Don't try to work around a classifier denial (e.g. rephrasing the same edit, splitting it into smaller steps to slip through). Stop, briefly explain what you were trying to build and why it got flagged, and ask the user via AskUserQuestion whether they want full automation or a human-in-the-loop variant (e.g. "propose + Teams-notify" instead of "auto-apply"). This applies specifically to *unattended edits of files with cross-project/global scope* (CLAUDE.md, shared settings) — routine automation that only touches project-local files or memory has not triggered this in past sessions. See [[memory_weekly_review_automation]] for the resulting design (backups before edit, no staleness-based deletion, capped number of additions per run) that made full automation acceptable once approved.
