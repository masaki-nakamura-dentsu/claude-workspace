---
name: dropbox-config-sync
description: "Global CLAUDE.md, settings.json, and this project's MEMORY.md/memory/ are symlinked into Dropbox so they sync across the user's 3 machines (2 Macs + 1 Windows PC)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e0f9f86e-3b1b-420e-964e-56a5e845cbae
  modified: 2026-08-16T22:40:52.323Z
---

Set up 2026-07-08: three pieces of Claude Code config now live physically in Dropbox at `~/dentsuDropbox Dropbox/中村正樹/.claude-sync/` and are referenced via symlinks so any Mac with this Dropbox mounted sees the same state:

- `~/.claude/CLAUDE.md` → `.claude-sync/CLAUDE.md` (global preferences)
- `~/.claude/settings.json` → `.claude-sync/settings.json` (hooks incl. the Stop-hook sound alert, [[notification-setup]])
- `~/.claude/projects/-Users-d14461-dentsuDropbox-Dropbox-----/memory/` → `.claude-sync/project-memory/memory/` (whole dir symlinked — this is the one that actually matters, see correction below)
- `~/.claude/projects/-Users-d14461-dentsuDropbox-Dropbox-----/MEMORY.md` → **local** symlink to `.../memory/MEMORY.md` (not its own separate Dropbox file — see correction below)

**Why**: user wants preferences, hooks (e.g. the completion-sound alert), and accumulated per-project memory to be identical on every Mac they use, without manually copying files each time they set up a new machine.

**Correction (found & fixed 2026-07-12, on the `maxakisan` Mac only so far)**: the auto-memory harness actually reads/writes the index at `<project-dir>/memory/MEMORY.md` (nested inside the memory folder), not at `<project-dir>/MEMORY.md` (project root). The original 2026-07-08 setup below wrongly symlinked project-root `MEMORY.md` to its own separate Dropbox file, which then went stale (frozen at 3 entries) while the real index at `memory/MEMORY.md` kept growing correctly via the whole-directory sync. Symptom: user asked about past project content on the other Mac and was told it wasn't in history — root cause was this file split, not a broken sync. Fixed by deleting the stray Dropbox file and repointing project-root `MEMORY.md` to a local symlink pointing at `memory/MEMORY.md` instead (see corrected commands below — `mkdir` step also removed since it's redundant once the `memory/` symlink is created).

**How to apply on a new Mac** (corrected): once Dropbox has synced `中村正樹/.claude-sync/`, recreate the symlinks (adjust the local username if it differs from `d14461`):
```bash
ln -sf "/Users/<user>/dentsuDropbox Dropbox/中村正樹/.claude-sync/CLAUDE.md" ~/.claude/CLAUDE.md
ln -sf "/Users/<user>/dentsuDropbox Dropbox/中村正樹/.claude-sync/settings.json" ~/.claude/settings.json
mkdir -p ~/.claude/projects/-Users-<user>-dentsuDropbox-Dropbox-----
ln -sf "/Users/<user>/dentsuDropbox Dropbox/中村正樹/.claude-sync/project-memory/memory" ~/.claude/projects/-Users-<user>-dentsuDropbox-Dropbox-----/memory
ln -sf ~/.claude/projects/-Users-<user>-dentsuDropbox-Dropbox-----/memory/MEMORY.md ~/.claude/projects/-Users-<user>-dentsuDropbox-Dropbox-----/MEMORY.md
```

**Fixed on d14461 Mac too (2026-07-13)**: confirmed the project-root `MEMORY.md` symlink was indeed broken (pointing at the deleted `.claude-sync/project-memory/MEMORY.md`). Repointed it with `ln -sf ~/.claude/projects/-Users-d14461-dentsuDropbox-Dropbox-----/memory/MEMORY.md ~/.claude/projects/-Users-d14461-dentsuDropbox-Dropbox-----/MEMORY.md` and verified `cat` now shows the same 11-entry index as `memory/MEMORY.md`. Both Macs (`maxakisan` and `d14461`) are now consistent — no more open TODO here.

**Caveat — project-memory only syncs correctly if the project key matches**: the project directory name (`-Users-d14461-dentsuDropbox-Dropbox-----`) is derived from the absolute working-directory path. It only lines up automatically across Macs if the macOS username is also `d14461` there; on a Mac with a different username, the memory symlink must be created under that machine's own differently-named project folder.

**Caveat — `settings.json` may accumulate machine-specific entries later** (e.g. permission allowlists referencing local absolute paths, or env vars specific to one machine). If that happens, stop syncing the whole file wholesale and split into a shared part (hooks, generic prefs) plus a local `settings.local.json` for per-machine bits.

**Caveat — concurrent edits**: editing the same synced file from two Macs at once can produce a Dropbox conflicted copy. Low risk since these files are edited infrequently.

**Confirmed on a second Mac (2026-07-08)**: username `maxakisan`, Dropbox folder named `ICPTokyo2022 Dropbox` (not `dentsuDropbox Dropbox`), project key derived as `-Users-maxakisan-ICPTokyo2022-Dropbox-----`. All four symlinks (CLAUDE.md, settings.json, MEMORY.md, memory/) set up successfully by deriving paths from this Mac's own `whoami`/Dropbox mount rather than assuming the first Mac's values — confirms the "adjust for differing username/Dropbox folder name" guidance above works in practice, not just in theory.

**Re-verified still working (2026-08-04, on d14461)**: user asked to "migrate" the company Mac's memory into the shared Dropbox folder, worried today's (2026-08-03) SIGALRM→subprocess.run fix notes were trapped in a company-Mac-only copy. Checked and found the sync has simply been running unattended and correctly since 2026-07-08 — the `memory/` symlink still points at the same shared path, holds 69 real `.md` files (matches the user's "~67" recollection from the personal Mac side), and the SIGALRM/subprocess content was already present in the shared `continuous_data_capture_setup.md`, cross-referencing both Macs by name in the same file. No separate un-shared folder existed anywhere under `~/.claude` on this Mac. Lesson for future sessions: if asked to "migrate to the shared folder" again on either Mac, check `ls -la` on the `memory` symlink target **first** before assuming a merge is needed — this setup is durable and doesn't silently break.

**Extended to a 3rd machine — personal Windows PC (2026-08-17)**: user has a personal Windows machine (username `maxak`) and wanted it added to the sync, same as the two Macs. Since the Windows session has no access to this project's memory (different project key = fresh session with no context), it was briefed with a self-contained instruction set rather than relying on it reading this file. Confirmed Dropbox path on that machine: `C:\Users\maxak\ICPTokyo2022 Dropbox\中村正樹\.claude-sync\`.

Windows-specific findings, reported back by the user after completion:
- **Symlinks need elevation**: Developer Mode was off on that PC, so `mklink`/`New-Item -ItemType SymbolicLink` needed admin rights. Worked around via a single UAC-elevated PowerShell session rather than permanently enabling Developer Mode.
- **Project key format differs from Mac's**: Mac keys use the pattern `-Users-<user>-<DropboxFolderName>-Dropbox-----`. The Windows equivalent (derived by the user's Windows Claude session by pattern-matching against the Mac example) came out as `c--Users-maxak-ICPTokyo2022-Dropbox-----` — note the `c--` drive-letter prefix replacing the Mac's leading `-Users`. Useful reference if adding a 4th Windows/WSL machine later.
- **PowerShell script encoding gotcha**: a setup script written without a BOM caused all symlink-creation calls to fail because the Japanese path component (`中村正樹`) got mangled — Windows PowerShell needs UTF-8 **with BOM** for scripts containing non-ASCII literals, unlike Mac shells. Rewriting the script with a BOM fixed it. Console output still *displayed* as mojibake afterward even though the underlying files were fine — resolved by reading with `-Encoding UTF8` rather than assuming actual corruption.
- All 4 symlinks created successfully (CLAUDE.md, settings.json, `memory/` — 107 files at time of setup, and the local `MEMORY.md` → `memory/MEMORY.md` redirect) and verified readable.

Now 3 machines total: `maxakisan` (personal Mac, "個人Mac"), `d14461` (company Mac, "会社Mac"), and this Windows PC (personal, "個人Windows" — see [[reference_mac_naming]]).
