---
name: dentsu-france-jci-pptx-project
description: "Multi-session overhaul of the Dentsu France JCI intro pptx (compression, layout unification, translation, design cleanup, staff photo styling)"
metadata: 
  node_type: memory
  type: project
  originSessionId: a39c86bb-94b1-4ad3-a38c-2d0a16e4640f
  modified: 2026-08-21T05:53:35.531Z
---

File: `/Users/d14461/Library/CloudStorage/OneDrive-電通/山田 桂太 Keita Yamada さんのファイル - dentsu France/Dentsu France_JCI_DJ_Intro_20280825.pptx` — a co-edited (with 山田桂太/Keita Yamada) intro deck for dentsu France about JCI (Japan Client Initiative) / GBC / entertainment IP business. The user (中村正樹) and Yamada both actively edit this file in parallel — slide count and content shift between sessions from the other person's edits, so always re-scan current state rather than trusting earlier turns' slide numbers.

## Work completed (2026-08-19 to 2026-08-21)
- **File size**: 473MB → ~280MB via [[pptx_filesize_reduction_technique]] (avconvert for video, sips for images).
- **Layout unification**: all content slides (excl. title/section-dividers/contents/closing) pointed to the single "2_タイトルと縦書きテキスト" layout (slideLayout105) — done manually by the user in PowerPoint after I scoped the risk (many slides relied on layout-inherited background/placeholder position; user did it via PowerPoint UI which handles this more gracefully than a scripted XML rewrite would have).
- **Translation**: 16 Japanese-content slides translated to English in place; original Japanese versions duplicated and moved to the end of the deck as hidden slides (`show="0"`), per user's explicit request to preserve them rather than delete.
- **Slide design cleanup**: e.g. the "four domains" 4-quadrant slide had wildly uneven explanation-text length; rewrote to balanced ~8-13 word blocks and fixed a misaligned/narrower text box.
- **Title normalization**: unified font (Verdana), size, and color (black) across slide titles; stripped decorative effects (drop shadows) and stray leading numbers left over from copy-pasted slides.
- **Slide49 (CLAMP展 Seoul case)**: filled a blank "Merchandise & social media buzz" template slide with two images extracted (via PyMuPDF/`fitz`) from `CLAMP展韓国_初動レポート_260427.pdf` — a product flat-lay photo + a real X/Twitter fan-post screenshot — plus a source caption. No backup requested for this specific edit (user's explicit call).
- **GBC org-chart staff photos** (slide with "Structure of Global Business Center" title, position shifts — was P16, is P17 as of 2026-08-21): circle-cropped + drop-shadow styling applied to 11 headshots total (8 division heads + MD/DMD/HRM). Names, as given by the user 2026-08-21:
  - MD = 石坂直樹 Naoki Ishizaka, DMD = 木村剛 Tsuyoshi Kimura, HRM = 河野哲 Satoshi Kono
  - Account Produce div1 = 項林, div2 = 小川美子 Yoshiko Ogawa, div3 = 金井耕一 Koichi Kanai
  - Solution Planning div1 = 山本肇 Hajime Yamamoto, div2 = 土門達郎 Tatsuro Domon
  - Business development div = 新保泰史 Yasufumi Shimpo, Strategic planning div = 山田桂太 Keita Yamada, Back office = 宮川武 Takeshi Miyakawa
  - **Gotcha hit during this work**: the MD/DMD/HRM photos are each wrapped in their own PowerPoint group (with their role-label textbox), so a shape-tree walk that only iterates top-level `slide.shapes` misses them — a first pass circle-cropped only the 8 non-grouped division-head photos and silently skipped these 3. Always recurse into `GROUP` shapes (`shape_type == 6`) when batch-editing picture styling on a slide. Also: QuickLook (`qlmanage`) does not reliably render `prstGeom`/`effectLst` overrides on pictures nested inside a group — verify via raw XML diff against a known-working sibling shape instead of trusting the thumbnail when a grouped shape looks unchanged.
- Staff headshot source photos for future poster/deck work live in two folders (professional shoot, named by surname/kana + code; and small poster-ready JPGs, named by full name): `Photographer/2025/20250707GBCプロフィール写真撮影/20260413山本肇さん依頼/` and `Photographer/2026/20260423プロフィール写真撮影企画/Poster制作/局員写真/JPG_small/`. That broader "replace + circle-crop + shadow all staff photos" task (originally requested against those folders/a poster project) turned out to actually mean *this* pptx's org-chart slide, not a separate poster .ai file — the poster `Poster制作/` folder's .ai/.jpg files are Dropbox online-only placeholders (0 bytes) and weren't the real target this round.

## Backup convention used throughout
Dated backups saved alongside the live file each work session, e.g. `..._backup_20260819.pptx`, `_02`, `_03` same-day suffixes, `_backup_20260820.pptx`, `_backup_20260821.pptx` — per [[feedback_pptx_filename_versioning]]. Always check for a `~$`-prefixed PowerPoint lock file before overwriting.

See also [[feedback_pptx_visual_qa_method]] (qlmanage limitations, now including the grouped-shape rendering gap noted above).
