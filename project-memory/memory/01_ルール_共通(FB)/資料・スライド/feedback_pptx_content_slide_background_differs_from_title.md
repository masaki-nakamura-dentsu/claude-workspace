---
name: feedback-pptx-content-slide-background-differs-from-title
description: "Standing rule: in any PPTX deck, title/section-divider slides and regular content slides must use visibly different background variants chosen from the slide master's layout catalogue — never reuse the same background graphic on every slide"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08c80e0c-bfb3-4666-856b-deb9e3b9cbaa
  modified: 2026-09-02T07:28:01.711Z
---

Title slides and section-divider (中扉) slides should look visually distinct from ordinary content slides. Pick a different background variant from the slide master's layout catalogue for content slides than the one used for title/dividers — don't default to the same background graphic across the whole deck.

**Why**: Explicitly stated as a standing, deck-wide rule (2026-09-02, [[ikeda_coaching_profile_photo_project]]) after a deck built from [[dentsu_pptx_template]] used "-plain grey" layouts (e.g. `1x column-plain grey`, `3x column-plain grey`) for every content slide — same grey background with the dot/line "network" graphic as `Title-01` and `Section divider-01`, so title, dividers, and body slides were visually indistinguishable.

**How to apply**: This template ships background variants per layout family — `-plain grey` / `-plain off-white` / `-plain off-black` for column layouts, `Image right-plain grey/off-white/black`, `Chart-grey/off-black/off-white`, `Closing-01/02/03`, `Free-grey/off-black/off-white`. Reserve the grey dotted-network background (`Title-01`, `Section divider-*`, and any bare `-plain grey`/`-grey` layout) for title and section-divider slides only. For all regular content slides, use the `off-white` (or `off-black`, if a darker deck is wanted) sibling layout instead.

**Known gap**: some layout families in this template have only one background variant (no off-white/off-black sibling) — e.g. `Quote-01`, `Statement slide-01`/`Statement-02..09`, `1_2x images with text-design`, `1_3x images with text-design`, `1x headshot-design`, `2x/4x headshots-plain grey`, `Contents-01/02/03`. Before reusing one of these for a content slide, check via each layout's `.rels` (or a rendered QA thumbnail) whether it actually carries the grey dotted background — if so, don't use it verbatim for body content; instead build the same visual intent (quote styling, statement-style big text, image+caption panels) manually on top of an off-white base layout (e.g. `Free-off-white`, `1x column-plain off-white`) using plain textboxes/picture shapes, so the background differentiation rule still holds.
