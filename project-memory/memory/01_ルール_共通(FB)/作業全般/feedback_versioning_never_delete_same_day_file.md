---
name: feedback-versioning-never-delete-same-day-file
description: "Self-correction: when applying the standing YYYYMMDD/_NN file-versioning rule, never delete a same-day file to 'make room' for the next _01/_02 suffix — always add alongside, since the rule's whole point is that every prior save stays untouched"
metadata:
  type: feedback
  originSessionId: 87a3a707-5aa7-4607-86a4-94721fd80aff
  modified: 2026-09-08T06:29:58.172Z
---

While iterating on [[ai_katsuyo_pj_weekly_tips]]'s "ChatGPT活用講義" Artifact across a same day (2026-09-08), a second same-day revision was saved by running `rm` on the existing `ChatGPT活用講義_20260908.html` and then `cp`-ing the new content to `ChatGPT活用講義_20260908_01.html` — i.e., deleting the first same-day save instead of leaving it in place alongside the new `_01` file.

**Why this is wrong**: the global standing rule (`~/.claude/CLAUDE.md`) exists specifically so a previously delivered file is never lost — "save the revision as a new file, keeping the previous version untouched," with the `_01`/`_02` running suffix explicitly for *additional* same-day revisions, not replacements. Deleting the prior same-day file defeats the entire purpose of the rule.

**How to apply**: when creating a `_01`, `_02`, etc. suffixed same-day revision, only ever `cp`/`Write` the new file — never `rm` any existing dated file first. If a destination folder is getting cluttered with same-day iterations, that's an acceptable and expected trade-off of the versioning rule; do not "clean up" by deleting older same-day saves. This applies to every project, not just this one.

In this specific incident the actual content wasn't truly lost (the artifact platform itself retains its own version history independent of local file copies, and the diff between the deleted version and the current one was already fully documented in [[work_status_protocol]]'s log for that task), so no user-facing harm resulted — but the local file trail was broken, which is exactly what the rule is meant to prevent.
