---
name: outlookexport_dropbox_migration
description: DONE (2026-07-21) — migration of ~/OutlookExport and ~/TeamsExport/data from d14461-Mac-local storage into Dropbox so maxakisan Mac can read it too
metadata: 
  node_type: memory
  type: project
  originSessionId: 1940d4b0-d807-4c36-84bf-715eb5850f8b
---

**STATUS: DONE as of 2026-07-21.** Both Macs now have working symlinks into the shared Dropbox folder `.../中村正樹/.claude-sync/data-export/`. `~/OutlookExport` and `~/TeamsExport/data` on d14461 are symlinks (real content moved into Dropbox); on maxakisan they were already symlinks pointing at the same place. `sync_power_automate_export.py` and `teams_daemon.py` were verified to read/write correctly through the symlinks. Full session log: work_status/outlookexport_dropbox_migration.md. The content below is the original planning note, kept for history.

Started 2026-07-17. The user works across two Macs (`d14461` and `maxakisan`, see [[dropbox_config_sync]]). `~/OutlookExport` (parsed email export, see [[local_work_data_export]]) physically lives only on the `d14461` Mac's local disk — never synced. User wants it usable from `maxakisan` too, but `d14461` won't be started again for a while.

**Why**: user wants email history readable from whichever Mac he's on, consistent with the standing "shared context across chats" default in CLAUDE.md.

**Done so far (maxakisan side only, 2026-07-17)**:
- Created `/Users/maxakisan/ICPTokyo2022 Dropbox/中村正樹/.claude-sync/data-export/` with `OutlookExport/` and `TeamsExport/data/` subpaths (empty, ready to receive synced content).
- Created symlink `~/OutlookExport` → that Dropbox folder's `OutlookExport` subpath. **Currently dangling** (target doesn't exist yet) until the d14461 side does its part and Dropbox syncs the content down.
- Created real dir `~/TeamsExport` with `~/TeamsExport/data` symlinked → the Dropbox `TeamsExport/data` subpath (also dangling for now). Only the `data/` subfolder (parsed `teams_messages.jsonl` etc.) is synced — user confirmed this scoped approach (2026-07-17) after the credential-risk caveat below.

**How to apply / remaining steps (must run ON the d14461 Mac)** — user will do this next time that Mac is up; exact wording to give Claude there:
```bash
# Email
mkdir -p "/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/data-export/OutlookExport"
mv ~/OutlookExport/* "/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/data-export/OutlookExport/"
rmdir ~/OutlookExport
ln -s "/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/data-export/OutlookExport" ~/OutlookExport

# Teams (data subfolder only — leave scripts/browser_profile local, see caveat below)
mkdir -p "/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/data-export/TeamsExport/data"
mv ~/TeamsExport/data/* "/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/data-export/TeamsExport/data/"
rmdir ~/TeamsExport/data
ln -s "/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/data-export/TeamsExport/data" ~/TeamsExport/data
```
Then verify `sync_power_automate_export.py` and `teams_daemon.py` still work through the symlinks (both use `~`-relative paths, so file writes/appends should transparently continue working through the symlink).

**Deliberately NOT migrated**: `~/TeamsExport/browser_profile/`, `login.py`, `scrape_teams.py`, `teams_daemon.py`, launchd plist — all stay local-only on d14461. `browser_profile/` holds live Teams login cookies; syncing that into Dropbox would push session credentials into cloud storage. Only the parsed `data/` output is shared cross-Mac.

**Once d14461 side is done**: check back on `maxakisan` that `~/OutlookExport/parsed_emails.jsonl` and `~/TeamsExport/data/teams_messages.jsonl` resolve through the symlinks (Dropbox sync may take a few minutes for the initial folder). No further action needed on maxakisan — both symlinks are already in place.
