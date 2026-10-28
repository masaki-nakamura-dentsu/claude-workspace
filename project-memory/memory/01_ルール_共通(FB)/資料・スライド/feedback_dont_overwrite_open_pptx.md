---
name: feedback-dont-overwrite-open-pptx
description: "Standing rule — before overwriting a pptx/docx/xlsx file on disk from a script, check for its Office lock file (~$filename) to see if it's currently open in the app; if open, warn the user or wait rather than overwriting blind"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 86655793-9c0c-4cdd-867b-e20342b361f7
  modified: 2026-08-18T00:46:25.141Z
---

Don't overwrite an Office file (pptx/docx/xlsx) on disk via script (cp, python-pptx save, etc.) without first checking whether it's currently open in the app — check for the sibling lock file `~$<filename>` in the same directory. If the lock file exists, the app has it open in memory; an external overwrite creates a mismatch between what the app holds and what's on disk, which — especially inside a cloud-synced folder (Dropbox/OneDrive) — is a real cause of app freezes/hangs, not just a theoretical risk.

**Why:** Confirmed 2026-08-18. In the AI活用PJ_アンバサダーキックオフ project, a pptx was overwritten twice via `cp` (layout pruning, then photo compression) while it was still open in PowerPoint from an earlier `open` call — the user reported PowerPoint "freezing often" the next time they used it. Root cause matches the known [[feedback_autosave_cloud_file_direct_edit]] OneDrive mechanism, but applies equally to Dropbox: external file mutation + cloud sync + an app's open file handle on the same path is a recipe for corruption-like hangs.

**How to apply:** Before any script-driven overwrite of a pptx/docx/xlsx the user might have open (especially right after building/revising one that was just `open`ed per the standing PPTX-auto-open rule), check `ls "~\$<filename>"` in the same folder first:
- If no lock file: safe to overwrite directly.
- If a lock file exists: either ask the user to close it first, or (preferred, since it avoids interrupting them) save as a genuinely new file/version instead of overwriting the open one, and tell them which file is now current.
- After telling the user "I opened this file," assume it may still be open in later turns of the same session unless they've indicated otherwise — don't overwrite it blind just because time has passed.
