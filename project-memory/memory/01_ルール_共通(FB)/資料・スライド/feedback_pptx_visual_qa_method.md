---
name: feedback-pptx-visual-qa-method
description: "How to visually QA a pptx slide without touching the PowerPoint app — avoid AppleScript window/quit automation, use qlmanage on an extracted single-slide file instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b8022472-1bc0-4868-8507-8a93f8bb298d
  modified: 2026-08-21T05:53:49.709Z
---

Don't drive Microsoft PowerPoint via AppleScript (window enumeration, `set index of window`, `quit`) to screenshot or verify a slide's layout. In practice (2026-07-30, [[vietnam_anime_ip_cross_promotion_project]]) this proved unreliable — window/name references failed intermittently, a native "save as PNG" export command silently no-opped, and while chasing a working window reference `tell application "Microsoft PowerPoint" to quit` was run with several *other* unrelated QBR pptx files still open in the same app instance. The process quit cleanly with no save-prompt, so it's likely nothing was lost, but there was no way to be fully certain from outside the app, and the user was not asked first.

**Why**: PowerPoint is frequently kept open with multiple unrelated documents (this user routinely has several QBR/other decks open at once). Any AppleScript command sent to "Microsoft PowerPoint" as an application affects the whole app instance, not just the file being worked on — there is no safe way to isolate one document's window from the others via automation in this environment.

**How to apply**: For visual QA of newly-built or edited slides, never send AppleScript commands to a running Office app (no `activate`, `quit`, window indexing, etc.). Instead:
1. With python-pptx, copy the working presentation and strip the `sldIdLst` down to just the one slide of interest (delete all other `sldId` entries), saving it as a standalone single-slide pptx.
2. Run `qlmanage -t -s <size> -o <outdir> <path-to-single-slide.pptx>` (macOS QuickLook) to render that one slide to a PNG — this is read-only, doesn't launch or touch any GUI app, and doesn't risk any already-open document.
3. Read the resulting PNG to check for overlaps, overflow, and overall layout before calling the work done.

This is also the same technique already used successfully in an earlier session for the BlueLock visual-concept deck (per-slide thumbnailing via qlmanage), so it's a proven, safe default — reach for it first rather than PowerPoint/Keynote automation.

If genuinely nothing else will do (e.g. checking something QuickLook can't render, like an embedded video), ask the user before sending any command to an Office app that already has other documents open.

**Known gap (2026-08-21, [[dentsu_france_jci_pptx_project]])**: qlmanage does not reliably render `prstGeom`/`effectLst` overrides (e.g. circle-crop + drop shadow) applied to a picture shape nested inside a PowerPoint `GROUP` — the thumbnail kept showing the old rectangular shape even after a QuickLook cache reset (`qlmanage -r cache`), while the underlying XML was verified byte-correct against an already-working sibling shape. When a grouped shape's styling edit doesn't show up in the thumbnail, don't conclude the edit failed — diff the raw XML instead of trusting the render, and note the limitation to the user rather than re-attempting the edit.

**Known gap #2 (2026-08-25, [[ai_agency_team_build]], Kintone Malaysia deck)**: qlmanage renders bar/column charts (`XL_CHART_TYPE.COLUMN_CLUSTERED`, `BAR_CLUSTERED`) correctly, but a `XL_CHART_TYPE.PIE` chart inserted into a `Chart-grey` placeholder rendered as a completely blank area (title/legend text around it showed fine, no pie visible at all) even though the chart XML (`ppt/charts/chartN.xml`) was verified well-formed and complete (categories, values, `c:pieChart` element, legend, data labels all present and schema-valid) and the zip had no duplicate/corrupted parts. No LibreOffice/`soffice` was available on this machine to cross-check via an independent renderer. Treat this as the same class of qlmanage chart-type rendering gap as the grouped-picture gap above — **don't conclude a pie chart failed to build just because it's blank in a qlmanage thumbnail; verify via the raw chart XML instead**, and tell the user to confirm visually in actual PowerPoint (`open` the file) rather than trusting QuickLook for pie charts specifically. Bar/column charts remain safe to trust via qlmanage.

**Known gap #3 (2026-10-08, [[bigidea_random_keyword_experiment]])**: qlmanage ignored per-point bar colors (`c:dPt`), `reverse_order` (orientation maxMin), and data-label number formats (`0%`, `0"案"`) — all showed as default even though the XML was correct. XY scatter markers rendered as squares without data labels. Verify these through the chart XML (grep dPt/orientation/formatCode), not the thumbnail. Separate python-pptx pitfall: setting only `.top` on a placeholder that inherits its position from the layout writes an xfrm with zero width (the text wrapped one character per line) — always set left/top/width/height together.

**Known gap #4 (2026-10-12)**: 個人Mac(ICPTokyo2022)のHomebrew soffice は日本語を一切描画しない(fontconfigはYuGothic等を認識するのにPDFにはLinux Libertine等しか埋め込まれない)。日本語デッキのQAは最初から qlmanage の1枚ずつ分割方式で行う。pptxgenjsのグラフは qlmanage で空白になる(LibreOfficeでは描画される)ので、グラフはXML/validateで確認。
