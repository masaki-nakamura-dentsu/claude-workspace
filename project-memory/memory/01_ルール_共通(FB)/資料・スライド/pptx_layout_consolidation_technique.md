---
name: pptx-layout-consolidation-technique
description: How to safely repoint many pptx slides to a single shared slideLayout without visual breakage (position/style/background baking)
metadata: 
  node_type: memory
  type: project
  originSessionId: a39c86bb-94b1-4ad3-a38c-2d0a16e4640f
  modified: 2026-08-19T07:03:39.708Z
---

Companion to [[pptx_filesize_reduction_technique]]. Validated 2026-08-19 on the same
`Dentsu France_JCI_DJ_Intro_20280825.pptx` (GBC/JCI France project, Yamada-san's file, owned in
`.../dentsu France/`) — consolidated 46 of 55 slides onto one shared layout
(slideLayout105, "2_タイトルと縦書きテキスト", the layout P4/P7 already used), excluding
title/section-divider/contents/closing slides plus one slide on a colour-inverted layout.

## Why naive reference-swapping breaks slides
Simply editing a slide's `_rels` "slideLayout" relationship target is NOT safe if:
1. **Placeholders lack explicit `<a:xfrm>`** — they inherit position from the *old* layout's
   matching-idx placeholder. If the new layout defines no placeholder of that idx (common for a
   thin "just a background" layout), the shape loses its position.
2. **Placeholders' `<a:lstStyle>` is empty** (`<a:lstStyle/>`) — they inherit font/size/bold from
   the old layout's placeholder `defRPr`. Same loss-of-inheritance risk as above.
3. **Every layout carries its own non-placeholder decorative shapes** (background pictures, page
   footer/logo textbox, ovals, freeforms) that show through only while that specific layout is
   assigned. Switching layout swaps this artwork out from under the slide.
4. **Background** (`<p:bg>`) is almost always inherited (layout's own, or master's if the layout
   has none), never set explicitly per-slide — switching layout can silently change background
   color/image.
5. **`<p:clrMapOvr>` per layout** — some layout variants (typically "...-Black" ones) invert the
   theme's bg1/tx1 mapping so `schemeClr` references render inverted (e.g. white text via `tx1` on
   a black `bg1`). Moving such a slide to a layout using `<a:masterClrMapping/>` (no override)
   flips every schemeClr-based fill/text back to the un-inverted color — e.g. white title text
   silently becomes black-on-black. **Check every layout's `<p:clrMapOvr>` before batching; carve
   out any slide whose layout inverts differently from the target.** (One slide, "One column -
   Black", was excluded for exactly this reason rather than risk it.)

## The safe procedure (per slide, scripted with lxml over the raw XML)
1. **Bake background**: if slide has no own `<p:bg>`, resolve one from its current layout (or the
   master if the layout has none) and copy it verbatim into the slide's `<p:cSld>`.
2. **Copy decorative shapes**: copy every non-placeholder shape from the *old* layout's spTree
   into the slide (inserted right after `grpSpPr`, i.e. behind the slide's own content), including
   the "Slide Number Placeholder"-style textbox — don't assume the target layout's own equivalent
   will render (empirically its absence was inconsistent to rely on; copying is cheap and safe
   since duplicate position = no visible difference).
3. **Rewire relationships**: any copied shape with `r:embed`/`r:link` (pictures) needs its
   relationship copied from the source layout's `.rels` into the slide's `.rels` under a fresh
   `rId`, then the attribute rewritten to point at it.
4. **Bake placeholder position + style**: for each slide placeholder missing `<a:xfrm>` and/or
   with an empty `<a:lstStyle>`, find the matching-idx placeholder in the *old* layout and copy its
   `<a:xfrm>` / full `<a:lstStyle>` onto the slide shape. This freezes the *currently rendered*
   position and default text formatting independent of whatever the new layout provides.
5. Only then edit the slide's `.rels` "slideLayout" relationship Target to the new layout file.
6. Assign fresh unique shape `id`s to every copied shape (scan existing `p:cNvPr id` values on the
   slide, continue from `max+1`) — collisions corrupt the file silently.

## Gotchas hit during implementation
- **lxml `Element or Element` for existence checks is a trap**: an empty self-closing element
  (`<p:ph type="title"/>`, no children) is falsy under `len(el)==0` semantics, so
  `find(...) or find(...)` silently skips a legitimately-found empty placeholder. Always use
  explicit `is not None` chains.
- **QuickLook (`qlmanage`) is not a reliable visual-diff oracle for this kind of check.** It
  mis-rendered a `<a:fld type="slidenum">` field as literal fallback glyphs inconsistently across
  otherwise-identical runs, and separately rendered one slide's literal `srgbClr` card fills (with
  `lumMod`/`lumOff` tints) as a wildly different hue. Byte-diffing the actual `<a:solidFill>`
  elements between before/after XML proved they were 100% identical — the discrepancy was purely a
  QuickLook rendering artifact, not a real regression. When qlmanage shows something surprising,
  verify against the raw XML before concluding the edit broke something. Real PowerPoint via
  `open` could not be visually confirmed in this session either (app activated but no window
  surfaced, and `System Events` window queries are blocked — this Mac has no accessibility
  permission grant for osascript, consistent with [[notification_setup]]'s prior finding).
- **A real, expected side effect**: slides that gain the shared layout's own decorative
  page-number/logo textbox now show it even if their old layout didn't have one. This is not a
  bug — it's the same design the reference slide already displays — but it's a visible change
  worth flagging to the user rather than silently absorbing.
- Extracting a single slide for isolated visual QA: load with python-pptx, remove all other
  `<p:sldId>` entries from `presentation.xml`'s `sldIdLst` (`p.slides._sldIdLst`), save. This does
  *not* prune unused parts, so the file stays full-size — fine for a one-off render, not for
  distribution.

See [[feedback_pptx_visual_qa_method]] — this task pushed past qlmanage's reliability envelope;
worth updating that memory if a better PowerPoint-real-render QA method is found later.
