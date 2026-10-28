---
name: globalq-top-banner-monthly-export
description: "Recurring monthly task: export Global Q TOP page banner slides from top_bnr__テンプレート.pptx as JPGs — naming convention and export method"
metadata: 
  node_type: memory
  type: project
  originSessionId: e7bfb43f-eb91-46d0-8ef0-3bed77dca9b5
  modified: 2026-08-31T00:28:51.518Z
---

Recurring monthly task: the user maintains Global Q's TOP page banners in a single running pptx template — `top_bnr__テンプレート.pptx` in `Work共有作業系/戦略企画部/Global Q/8_素材アセット/バナー_TOPページ/` — and each month asks to export that month's banner slides as JPGs into the same folder.

**Naming convention** (inferred from existing files, confirmed working 2026-08-31): `top_bnr_YYYYMM-NN.jpg`, NN = 2-digit sequence (01, 02, 03...) matching the order the slides appear in the deck for that month. A rare variant suffix like `-2`/`-3` appears on some months (e.g. `top_bnr_202511-01-2.jpg`) when a banner had an alternate crop/version — only add that if the user asks for a variant, not by default.

**Export method** (used for 2026年8月, slides 6-8 → top_bnr_202608-01/02/03.jpg): do NOT drive PowerPoint via AppleScript (see [[feedback_pptx_visual_qa_method]] — same risk applies to export, not just QA, since the app may have other unrelated decks open). Instead:
1. python-pptx: copy the template, strip `sldIdLst` down to one target slide, save as standalone single-slide pptx (repeat per slide).
2. `qlmanage -t -s 2100 -o <outdir> <single-slide.pptx>` (macOS QuickLook, read-only) → renders a PNG at the requested max dimension.
3. `sips -s format jpeg -s formatOptions 90 <in>.png --out <out>.jpg` → convert to JPG.
4. Copy into the banner folder with the `top_bnr_YYYYMM-NN.jpg` name matching slide order.

Confirmed output resolution matches the deck's existing exports: slide aspect ratio ~18.97in x 6.25in → 2100x693px JPG (matches prior months' files, e.g. `top_bnr_202607-02.jpg` was also 2100x692/693).

**How to apply**: next month, just find the current month's relevant slide numbers in the same template (ask the user which slide range, since slide count/order changes each month) and repeat this same pipeline — no need to re-derive the naming convention or the AppleScript-avoidance rationale from scratch.
