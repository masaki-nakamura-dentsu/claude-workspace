---
name: feedback-bilingual-single-file-pptx
description: "When a deck needs both Japanese and English, put both languages in one pptx (JP line + smaller EN line beneath) rather than maintaining a separate translated file"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 408e38bd-2b36-4750-afc0-56dbb6f22b27
  modified: 2026-08-03T06:47:53.378Z
---

When the user needs an English version of a deck that already exists in Japanese, don't default to producing a second `_EN.pptx` file. Instead consolidate: add the English translation as an additional, smaller/italic line directly beneath each Japanese text element within the same file.

**Why:** Stated explicitly (2026-08-03, [[toyota_india_aot_hyryder_project]]) — "ファイルがどんどん増えるのを防ぐためにも" (to stop the number of files from proliferating). A prior turn on the same project had created a standalone EN file per the general [[feedback_pptx_filename_versioning]] no-overwrite convention; the user corrected that this specific case (translation, not a content revision) should merge into one bilingual file instead.

**How to apply:** Bilingual layout pattern that worked well: JP text at its normal size/color, EN translation as a new paragraph directly after it at roughly 55-85% of the JP font size (smaller for big display headlines, closer to full size for small captions/body text), italic, muted gray (`#595959`) unless the JP line itself is already colored (e.g. an orange accent title), in which case keep the EN a shade more muted. Watch for two recurring template gotchas when doing this (see [[dentsu_pptx_template]]): (1) placeholders with native auto-numbering will double up with any manual "1./2./3." prefix already in the JP text — disable `buAutoNum` on the paragraph rather than removing the manual prefix; (2) any placeholder with tight/negative character tracking (`spc` in the layout's `lstStyle`, e.g. -700 on the "Statement" headline layout) reads fine for Japanese (no inter-word spaces) but collapses English word-spacing — explicitly set `spc="0"` on any new English run added to such a placeholder. This is the second time the same tracking bug surfaced (once on a dedicated EN file, once on newly-inserted bilingual runs), so check for it proactively on any first-time English text going into a "Statement"-style layout rather than waiting to spot it in QA.

This preference is about deck/file proliferation specifically — it doesn't override [[feedback_pptx_filename_versioning]] for actual content revisions (those should still get a new dated file, not overwrite the delivered version in place).
