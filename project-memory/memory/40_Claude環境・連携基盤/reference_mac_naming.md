---
name: reference_mac_naming
description: "User's names for the 3 machines: this Mac (ICPTokyo2022) is '個人Mac'/'私用Mac', d14461 is '会社Mac', and the personal Windows PC (user maxak) is '個人Windows'"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ac8045b6-6dee-4de2-8f92-3f40483d2d01
  modified: 2026-08-16T22:41:05.290Z
---

Stated explicitly by the user 2026-08-03.

- **This Mac** (hostname/path `ICPTokyo2022`, working directory under `ICPTokyo2022 Dropbox/中村正樹`) = **「個人Mac」** or **「私用Mac」** (personal/private Mac).
- **The other Mac** (hostname/user `d14461`, working directory under `dentsuDropbox/Dropbox`) = **「会社Mac」** (company Mac).

**How to apply**: when the user says "個人Mac" or "私用Mac", they mean the Mac this session is usually running on (ICPTokyo2022). When they say "会社Mac", they mean d14461 — the one running the Teams daemon and the one referenced throughout [[continuous_data_capture_setup]] for cross-Mac sync work. Since per-project memory is local to each machine (not Dropbox-synced by default — see the CLAUDE.md note on `~/.claude/projects/` paths), a session running on a different machine won't automatically see this memory; if giving the user instructions to relay to a session on another machine, spell out full context rather than assuming the alias is understood there too.

**Added a 3rd machine (2026-08-17)**: a personal Windows PC (macOS-style username analog `maxak`), which the user calls **「個人Windows」**. Its `~/.claude` config/memory were added to the same Dropbox-symlink sync as the two Macs — see [[dropbox_config_sync]] for the setup details, including its differently-formatted project key (`c--Users-maxak-ICPTokyo2022-Dropbox-----`) and Windows-specific symlink/encoding gotchas encountered during setup.
