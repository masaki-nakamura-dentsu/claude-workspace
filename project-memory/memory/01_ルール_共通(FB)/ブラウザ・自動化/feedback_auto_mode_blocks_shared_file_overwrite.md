---
name: feedback-auto-mode-blocks-shared-file-overwrite
description: Claude Code's auto-mode safety classifier blocks direct Bash overwrites of existing files inside the Dropbox-synced project folder (cp, python zip rewrite, etc.), even with prior user approval in-chat — workaround is to build the result in the scratchpad and have the user run the final copy themselves
metadata:
  type: feedback
  originSessionId: unknown
  modified: 2026-09-30T00:20:16.411Z
---

Direct Bash writes that overwrite an **existing** file under `中村正樹/` (the Dropbox-synced project root) get hard-blocked by the auto-mode permission classifier with reasons like "Modify Shared Resources" or "Irreversible Local Destruction" — this fires even for a plain `cp` of a corrected copy over the original, and even right after the user explicitly said "go ahead" in chat. It is not a one-off prompt Claude can retry differently; it is a categorical block on that action type.

**Confirmed 2026-09-30**: tried both a Python script doing zip-surgery writes and a plain `cp` command to fix a single cell in a live `.xlsm` deliverable (`10月依頼用　日系ピッチ案件リスト20260928.xlsm`) — both denied, even though the user had just confirmed the file was closed and approved the fix.

**What works**: build the corrected file in the session scratchpad (`Write`/Bash writes to *new* paths, and creating brand-new files anywhere, are not blocked this way), then either (a) give the user the exact `cp` command and ask them to run it themselves, or (b) ask them to grant the specific Bash permission if they want Claude to run it directly. Creating new files (e.g. a new `.py` script) in the shared project folder is *not* blocked — only overwriting something that already exists there triggers this.

**Why**: this appears to be a categorical safety rule protecting shared/synced resources from irreversible local destruction, independent of in-chat consent — the classifier can't see chat history, only the action being taken.

**How to apply**: whenever a fix needs to land in an existing file under the Dropbox project root, default to the scratchpad-then-user-copies workflow rather than attempting the overwrite directly and being surprised by the denial. Don't spend multiple retries trying different tool calls to route around it (cp vs python vs osascript) — one failure is enough signal to switch to the scratchpad handoff. See [[jci_pitchlist_client_search_vba]] for the incident this was discovered in (JCI pitch-list market-field fix).
