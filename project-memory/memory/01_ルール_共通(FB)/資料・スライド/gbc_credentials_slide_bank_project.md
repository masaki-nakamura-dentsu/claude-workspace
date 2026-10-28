---
name: gbc-credentials-slide-bank-project
description: New architecture for reusing dentsu's existing OneDrive credential-deck slides via Agency OS — master PPTX files + a slide catalog + a PowerPoint Copilot "keep-list" instruction, instead of AI-redrawn slides
metadata:
  node_type: memory
  type: project
  originSessionId: unknown
  modified: 2026-09-30T08:27:48.666Z
---

Started 2026-09-30, a sibling initiative to [[gbc_intelligence_engine_project]]'s credentials-deck feature but architecturally distinct — this one reuses existing pre-formatted slides verbatim rather than generating new ones from extracted data.

## The problem
OneDrive `GBC - 02．クレデン共有チャネル` (116 files, 28GB) has years of accumulated credential/capability decks that GBC staff currently reuse by manual copy-paste ("ツギハギ"). Design inconsistency and no systematic way to find/combine the right slides.

## Rejected approach
Nakamura-san's initial idea: convert every reusable slide into a separate dentsu-format file, 1 slide = 1 file, Agency OS links to them. Rejected after real measurement: excluding video-heavy files (>500MB, several 1.8–2.9GB per-country decks), the remaining 85 files still total **6,008 slides** — converting/redesigning that many individually is not practical, and per-file client-name duplication would recreate the exact "same fact baked into many files" version-drift problem the sibling recipe+data architecture was built to avoid.

## Chosen approach: master deck + catalog + Copilot keep-list instruction
1. Keep a handful of **theme-based master PPTX files** (not one single 6,000-slide file) as-is, stored on SharePoint/Dropbox — never uploaded to the ChatGPT Skill (sidesteps the binary-upload restriction entirely, see [[gbc_intelligence_engine_project]] 2026-09-30 finding).
2. Each master deck gets a **Markdown catalog** (slide number → chapter → title/topic → client-name warning) that Agency OS reads from the Knowledge Pack.
3. When a user asks for a credentials proposal, Agency OS picks slide numbers from the catalog and outputs a plain-text instruction: *"このマスターデッキから、スライド番号 X, Y, Z のみを残し、それ以外はすべて削除してください"* (a **keep-list**, not a delete-list — shorter and less error-prone for an LLM to parse correctly at scale).
4. The user opens the master deck in PowerPoint, pastes that instruction into Copilot or the ChatGPT add-in, and gets a ready single-file deck — no link-clicking, no custom python-pptx slide-copy tool needed, no AI redrawing (so [[feedback_generation_time_diagram_fabrication]]'s risk doesn't apply here at all).

## Why this beats the two other options considered
- vs. per-slide pre-rendering: doesn't require converting thousands of slides, no per-fact version-drift across many files.
- vs. the recipe+data architecture (`credentials_slide_library_01.md`/`deck-production.md`): no generation-time fabrication risk (nothing is redrawn, just deleted), no output-design variance between requests — directly addresses Nakamura-san's explicit "ブレを無くしたい" requirement in a way recipe+data cannot fully guarantee.
- Known open risk: **PowerPoint Copilot's reliability at correctly executing a keep-list instruction against dozens/hundreds of slide numbers is not yet validated** — this is the next thing to test, not an implementation detail to assume away.
- Slide-numbering sync discipline is required: if a master deck's slide order changes, the catalog must be regenerated in lockstep or Agency OS's instructions reference the wrong slides.

## First master deck: capability deck (256 slides), catalogued
`電通ケイパビリティプレゼン資料（日本語 2026年版）.pptx` (電通クレデンシャル folder, updated 2026-08-04) chosen as master #1 — already dentsu-formatted, current, chapter-structured with per-slide titles. Catalogued in full (`GBC-Knowledge/slide_bank_source/slide_catalog_capability_deck_jp2026.md`).

Two notable discoveries during cataloguing:
1. **The source deck already contains its own recommendation table** (slide 3): client pain-point → recommended chapter → target audience. This is dentsu's own existing mapping logic and is now the starting point for Agency OS's slide-selection judgment, transcribed into the catalog rather than re-invented.
2. **Slides 2–4 are internal/meta pages, not client content** — slide 2 literally instructs "delete this page before presenting," slide 3 is the internal recommendation table, slide 4 is a hyperlink-navigation note. Catalog marks these `ALWAYS_EXCLUDE` so Agency OS never accidentally includes them in a client-facing keep-list.
3. Client-name detection (19 of 256 slides flagged `CLIENT_NAME_WARNING`, cross-checked against a diff with the deck's own "配布送付可能版" — which independently removes/anonymizes 4 of the same client-named slides, confirming the flagging approach is on the right track) is automated (title scan + body-text "様"-honorific scan) but explicitly **not exhaustive** — flagged to Nakamura-san as needing a human skim pass before external use, per [[feedback_verify_stock_license_per_image]]-style per-item confidentiality caution.

## Status / next steps (as of 2026-09-30)
1. **Not yet validated**: whether PowerPoint Copilot/ChatGPT add-in can reliably execute a multi-slide-number keep-list instruction at realistic scale. Must pilot-test with Nakamura-san before treating this architecture as production-ready.
2. If validated: catalogue the remaining ~84 files (minus the excluded video-heavy per-country decks), decide theme groupings for additional master decks (candidates observed: 国別広告事情, インダストリーナレッジ, ソリューション事例).
3. Wire the catalog + instruction-output rule into SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.md once the Copilot mechanism is confirmed working.

Full session log: [[work_status/gbc_credentials_slide_bank_master_deck_project_20260930]].
