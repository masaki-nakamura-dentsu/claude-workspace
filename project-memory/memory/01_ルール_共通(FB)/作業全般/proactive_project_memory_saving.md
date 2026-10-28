---
name: proactive-project-memory-saving
description: "Save project work content to memory more liberally, not just \"surprising\" facts — user needs cross-Mac continuity"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 934c198c-2214-4254-aab0-8f6b51e1945c
---

Be more proactive about writing **project**-type memories that summarize the actual content/substance of work discussed in a session (decisions made, current status, what was tried, what's next) — don't wait only for facts that feel "surprising" or "non-obvious" before saving.

**Why**: user asked about past project work on a different Mac ([[dropbox_config_sync]] setup, 2026-07-08) and was told the content wasn't in history. The Dropbox symlink sync for `MEMORY.md`/`memory/` was verified working correctly (2026-07-12) — the real gap is that the memory system only stores curated/distilled notes, not raw transcripts, and raw session logs (`*.jsonl`) are local-only per machine and never auto-loaded into new chats anyway. So the only mechanism that actually carries work content across Macs/chats is memory entries — if a session's content isn't written to memory, it is effectively gone for future chats regardless of sync.

**How to apply**: at natural checkpoints in a session (a task/subtask wrapping up, a decision getting made, a status changing), write or update a project-type memory capturing it — even if it doesn't feel "surprising," as long as it's the kind of thing the user would want to ask about later ("where did we leave off on X"). Bias toward capturing too much project substance rather than too little, since the cost of a slightly redundant memory is much lower than the cost of losing continuity across machines. This is in addition to (not instead of) the normal filter that excludes pure ephemeral/in-progress task-tracking detail.
