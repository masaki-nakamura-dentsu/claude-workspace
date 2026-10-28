---
name: session_2026-07-07_agent_and_notification_setup
description: "Summary of the 2026-07-07 session that explored a custom subagent, settled on global CLAUDE.md for standing preferences, and set up desktop notifications"
metadata: 
  node_type: memory
  type: project
  originSessionId: a6866f6c-94e8-435a-a177-a220362fdb57
  modified: 2026-09-12T08:39:31.838Z
---

Summary of a prior session (2026-07-07, session id de3ccab7) preserved so the exchange isn't lost across app restarts/compaction.

**1. Custom subagent exploration → abandoned in favor of CLAUDE.md**
User initially asked for a Claude Code "agent" to run on all work. A global custom subagent (`~/.claude/agents/assistant.md`) was created, but the user pointed out subagents only run when explicitly invoked via the Agent tool — they don't apply automatically to every conversation the way a global `CLAUDE.md` does. The subagent was deleted; `~/.claude/CLAUDE.md` was created instead as the mechanism for standing, cross-project preferences.

**Why:** the user wants "all work" covered automatically, which only `CLAUDE.md` (auto-loaded every session) and the per-project memory system (also auto-loaded) provide — subagents are opt-in per call.

**2. Standing preferences added to CLAUDE.md**
- Complete Claude-Code-doable tasks end-to-end without asking first; only pause for genuine blockers (user-only decisions, destructive/hard-to-reverse actions, missing unresolvable info).
- Proactively keep CLAUDE.md / per-project memory current when a durable preference or working style surfaces, rather than waiting to be asked again.

**3. Response-completion alert**
User asked for an alert each time Claude finishes responding, to avoid watching the screen and waiting. First attempt was a macOS notification (`osascript` + `sandbox.allowAppleEvents`), which required a full app restart to test — but even after restarting, Notification Center permission for `osascript`/Script Editor could not be granted on this Mac (didn't appear in System Settings search; direct plist bit-flip didn't help either; Focus mode was ruled out). Landed on a simpler, permission-free fix instead: a `Stop` hook that plays a system sound via `afplay`. Confirmed audible and working 2026-07-07. Full detail in [[notification_setup]].

**How to apply:** treat CLAUDE.md as already carrying the "finish tasks autonomously" and "keep instructions current" preferences — don't ask permission for routine, reversible, Claude-Code-native work. If the user reports notifications not firing again, start from [[notification_setup]] rather than re-diagnosing from zero.

**Reconfirmed 2026-09-12 (JAAA essay project, `jaaa-shinsain` judge agent)**: custom agent definitions (`~/.claude/agents/*.md`) are NOT hot-reloaded — a file created mid-session does not appear in the Agent tool's available-agents list until the next session/restart. When asked to create a custom subagent that should be used "immediately"/"always" going forward: (1) write the `.md` file as usual, (2) tell the user it will only be callable via the Agent tool starting next session, (3) for the current session, manually apply the same criteria written into the agent file as a self-review step instead of trying to invoke it. This is a distinct issue from the original 2026-07-07 finding (that subagents never auto-trigger without explicit invocation) — this one is about a *newly created* agent's definition not being visible to *any* invocation attempt until reload.
