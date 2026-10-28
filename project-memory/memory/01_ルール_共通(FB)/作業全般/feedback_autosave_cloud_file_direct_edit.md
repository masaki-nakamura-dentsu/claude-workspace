---
name: feedback-autosave-cloud-file-direct-edit
description: Never rely on direct filesystem edits reaching the cloud for an AutoSave-enabled OneDrive/SharePoint file while an Office desktop app has it open — root-caused via OneDrive sync logs, 2026-08-06
metadata:
  type: feedback
  originSessionId: fc9a2fff-4ac2-4c64-8ec5-4fd6c0f41f81
  modified: 2026-09-11T02:54:10.640Z
---

Direct filesystem edits (e.g. python-pptx writing straight to a `.pptx` path under `~/Library/CloudStorage/OneDrive-*/...`) can silently fail to ever reach the cloud copy — even though the local file on disk is correctly modified every time and re-verified — if a Microsoft Office desktop app (PowerPoint, Word, Excel) has that same file open with **AutoSave ON**. See [[toyota_india_aot_hyryder_project]] for the full incident this was discovered in.

**Why**: AutoSave means the desktop app holds an active co-authoring **upload session** against the SharePoint/OneDrive-backed cloud item for as long as the file is open. When the OneDrive sync client tries to upload a separate, out-of-band filesystem change to the same cloud item, the server rejects it (`X-ClientErrorCode:UploadSessionInProgress`) and the upload fails — invisibly, with no error surfaced to the person editing. `~/Library/Logs/OneDrive/<Account>/SyncDiagnostics.log` (`numFileFailedUploads`, `failedBytesUploadedTotal`, `successfulBytesUploadedTotal`) and `strings` over the `SyncEngine-*.odl` trace files are how this was actually confirmed, after "close and reopen the app" failed to fix it (reopening quickly can re-lock the session before the failed upload retries, or the underlying conflict needs resolving, not just a fresh open).

**Why:** MD5/mtime re-checks immediately before a write only guard against a *different* class of problem (a second local writer racing the same edit) — they do nothing to prevent this upload-session conflict, since the local write itself always succeeds; it's the cloud sync afterward that silently fails.

**How to apply**: before doing any direct file-level edit (via a script, not through the Office app itself) to a file that lives in an OneDrive/SharePoint-synced folder, ask whether the file might be open in a desktop Office app right now, and if AutoSave could be on. If there's any chance it is, ask the user to explicitly fully quit that app (not just close the window/tab) before editing, and treat "I already closed it" with skepticism if the change still doesn't show up afterward — verify by checking OneDrive's own sync logs rather than assuming a simple close/reopen will always clear a stuck upload session. If the file can't reliably be guaranteed closed (e.g. a colleague might have it open, as with Teams-shared files), don't force direct in-place edits — fall back to producing a new dated file for manual merge instead, per [[feedback_pptx_filename_versioning]].

**Confirmed for Excel too, 2026-09-11** ([[qbr_combined_xlsx_rebuild_20260911]]): openpyxl edits to `Prep_CAS X SF Crosstable.xlsx` and `Prep_SalesforceAllRecord.xlsx` (both OneDrive/SharePoint-synced) were silently reverted twice within seconds/minutes because the user had them open in Excel with AutoSave on. **Cheap, reliable pre-check before any openpyxl write to a cloud-synced file**: `osascript -e 'tell application "Microsoft Excel" to get name of every workbook'` — if it lists anything (not `missing value`), don't write; ask the user to close first, then re-check the same way before proceeding. Faster and more certain than trying to eyeball SyncDiagnostics.log for a quick one-off edit.
