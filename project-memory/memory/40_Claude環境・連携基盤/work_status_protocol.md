---
name: work-status-protocol
description: "Standing protocol for cross-chat visibility — each chat appends a short work-log entry after every response (while doing substantial work) to a shared, never-deleted folder, so other chats can see both what's in flight now and what was done in the past"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ce019663-7eff-47e4-a117-4af2acf0f4fa
---

Requested 2026-07-16, revised same day, scope broadened 2026-07-20: all chats in this project should leave a short work-log entry so any other chat (opened in parallel, or later) can see what's currently in flight *and* what was already done. Files in `memory/work_status/` are a **permanent history, never deleted** — the user wants to be able to look back at what was done, not just see live status.

Original ask was "every 10 minutes," but there's no reliable ambient timer for that (see limitation below), so the actual rule is: **append an entry after every response**, not on a wall-clock cadence.

**2026-07-20 update**: the original "skip trivial responses" exception is repealed. Every response now gets an entry, including simple one-off Q&A with no multi-step work — not just substantial work. Log briefly even for a quick answer (e.g. `What: answered a quick question about X`).

## Where

`memory/work_status/` — one file per chat/task, named `<topic-slug>.md` (short, stable for the life of that chat's task — don't rename mid-task, don't reuse a slug for an unrelated task later).

## What goes in each file

**Append-only log, oldest entry first, newest at the bottom.** Never delete the file and never delete or overwrite prior entries — each entry is a permanent record of that turn's work. Skip appending an entry only when a response did no real work (e.g. a pure clarifying question with nothing done yet).

```
# <topic>

## <ISO timestamp>
Status: in progress | blocked | done
What: <1-3 sentences on what happened this turn>
Next: <1 sentence, or "—" if done>

## <ISO timestamp>
...
```

## Cadence rule

- Append one entry per response (not per 10 minutes) — **every response, including a single quick Q&A with no multi-step work.** (As of 2026-07-20 there is no "too trivial to log" exception; a one-line `What:` is enough for a simple answer.)
- When a task wraps up, add a final entry with `Status: done` — **do not delete the file.** The file is the historical record of that task; other chats (and future sessions) may need to know what was done, when, and how, long after it's finished.
- At the start of any task (however small), check `memory/work_status/` for files with a recent timestamp and `Status: in progress` (something live, possibly worth coordinating with) as well as older `done` files relevant to the topic (past work worth knowing about before starting something similar).

## Known limitation — read before assuming this runs unattended

Claude Code only acts when a session is actively processing a turn (or, if the `/loop` skill has been explicitly started on a task, via scheduled wake-ups). There is no ambient background timer that fires across *all* chats regardless of whether they're active — a chat sitting idle between user messages will not spontaneously wake up and write a memo. That's why the rule is per-response rather than per-10-minutes: it rides on something that actually happens (a response being generated) instead of a timer that doesn't exist outside of an explicit `/loop`.

See [[proactive_project_memory_saving]] for the related (but distinct) policy on writing durable curated memory — this protocol is a lower-effort, higher-frequency work log, not a replacement for it.
