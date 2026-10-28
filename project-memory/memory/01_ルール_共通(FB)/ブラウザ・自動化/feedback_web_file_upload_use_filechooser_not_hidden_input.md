---
name: feedback-web-file-upload-use-filechooser-not-hidden-input
description: "When automating a file upload on a web app via Playwright, click the visible upload button and handle the native filechooser event rather than calling setInputFiles() directly on the hidden <input type=file> — the latter can silently fail to persist on some apps (React apps whose upload handler expects the real browser file-picker flow)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: unknown
  modified: 2026-09-15T06:25:47.507Z
---

**Rule**: automate a web file upload with `page.waitForEvent('filechooser')` paired with a real click on the visible upload button, then `fileChooser.setFiles(path)` — not `page.$('input[type=file]').setInputFiles(path)` directly on a hidden input, even when that input is easy to find and the direct call appears to work.

**Why**: On 2026-09-15, replacing files in a ChatGPT Skill editor (`chatgpt.com/skills/editor/...`), calling `setInputFiles()` on the hidden `#upload-files` input showed the new file appearing in the DOM immediately and even survived a "保存する" (save) click — but a full page reload afterward showed the file gone. Deleting a file via the UI's own delete button persisted fine; only the direct-hidden-input upload path was silently non-persistent. Doing this for 7 files in a row without checking each one after a reload meant the app briefly had ALL 7 knowledge files missing before the mistake was caught. Switching to the filechooser-event method (clicking the real "アップロードする" button and answering the resulting native file dialog) persisted correctly every time, verified by reload after each file.

**How to apply**: 
1. Default to the filechooser-event pattern for any web file upload automation, regardless of how convenient a hidden input looks.
2. When a task involves deleting-then-replacing files (not just adding new ones), treat it as higher risk than an additive-only upload — verify each file individually with a `page.reload()` + DOM check before moving to the next one, rather than batching all deletes/uploads and checking at the end. A delete-persists/upload-doesn't-persist asymmetry can leave a live shared tool (an app other people use) in a worse state than before you started, and batching hides exactly when things went wrong.
3. This generalizes beyond ChatGPT Skills to any React/SPA-style file manager UI automated via Playwright — see [[gbc_intelligence_engine_project]] 2026-09-15 entry for the specific incident.
