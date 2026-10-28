# memory_cross_mac_sync_verification

## 2026-08-04T12:30:00+09:00
Status: done
What: User asked to migrate/merge 会社Mac's memory folder into the shared Dropbox location (fearing today's SIGALRM/subprocess fix notes were stuck in a company-Mac-only copy). Investigated and found the premise was outdated: `~/.claude/projects/-Users-d14461-dentsuDropbox-Dropbox-----/memory` has been a symlink to `/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/project-memory/memory` since 2026-07-08 (per [[dropbox_config_sync]]), and today's SIGALRM→subprocess.run fix content was already present in the shared `continuous_data_capture_setup.md`. No separate real folder existed to merge; no other memory-like directories found anywhere under `~/.claude`. Confirmed with the user — no migration action needed. Added a confirmation note to dropbox_config_sync.md.
Next: —
