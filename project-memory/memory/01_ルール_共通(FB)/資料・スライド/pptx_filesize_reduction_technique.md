---
name: pptx-filesize-reduction-technique
description: "How to shrink an oversized .pptx (video/image bloat) on macOS without ffmpeg/Homebrew, using built-in avconvert + sips"
metadata: 
  node_type: memory
  type: project
  originSessionId: a39c86bb-94b1-4ad3-a38c-2d0a16e4640f
  modified: 2026-08-19T06:20:18.402Z
---

Reusable workflow for "このpptx重いので軽くして" requests, validated 2026-08-19 on
`Dentsu France_JCI_DJ_Intro_20280825.pptx` (473MB → 286MB, ~40% reduction, GBC/JCI France project).

## Diagnosis
- Unzip the pptx (`unzip -q file.pptx -d extracted`) and `du -sh` / sort `ppt/media/*` — in decks with embedded video, media is almost always 90%+ of total size, dwarfing slide XML/layout bloat. Check media breakdown before touching anything else.

## Video compression (no ffmpeg needed)
- macOS ships `avconvert` (AVFoundation CLI) — no Homebrew/ffmpeg install required.
- `avconvert -s in.mp4 -o out.mp4 -p Preset960x540 --replace` — presets cap resolution, they don't upscale smaller sources.
- **Critical gotcha**: presets target a quality/bitrate baseline for that resolution. If the source video is already small/efficiently encoded (e.g. already <960x540 or already low-bitrate H.264/H.265), re-encoding can make it *larger*, not smaller. Always compare before/after size per file and revert (re-extract original from the zip) any file that grew. Don't blanket-apply and trust it.
- Quality check method: `qlmanage -t -s 800 -o outdir video.mp4` generates a poster-frame thumbnail — enough to sanity-check visual quality without opening the video.

## Image compression via `sips`
- JPEG (no alpha): `sips -Z 1920 -s formatOptions 80 file.jpeg` if width >1920px, else just `-s formatOptions 80` to recompress. Typically 90%+ reduction on print-resolution photos (5MB→300KB range).
- PNG (has alpha/transparency): `sips -Z 1920 file.png` (resize only if >1920px wide) — sips has no lossy PNG quantization, so recompression alone barely helps; resizing oversized screenshots is the main lever. ~50% reduction typical.
- Rule of thumb cap: 1920px on the longest side is plenty for a slide (full-bleed 1080p slide never needs more).

## Repackage
- `zip -r -X -q new.pptx .` from inside the extracted folder (exclude `.DS_Store`).
- Validate before overwriting: `python3 -c "from pptx import Presentation; Presentation('new.pptx')"` confirms the zip/XML relationships are intact (python-pptx is installed on this Mac). Also render a QuickLook thumbnail (`qlmanage -t -o`) of the repackaged file as a final visual smoke test.

## Skipped this time (low value / risk)
- Pruning unused slideLayouts (found 98 of 118 unused, but only 4.5MB total vs 470MB — not worth the corruption risk of manual XML surgery via zip/rels editing on a live collaborative file). Only worth doing if layout count itself is the complaint, not file size.

See also [[feedback_pptx_visual_qa_method]] for the qlmanage-not-AppleScript visual QA pattern, and the global filename-versioning rule for the backup-copy naming.

**2026-10-14 注意**: 再zipでファイル名を列挙するとcustomXml等が漏れる→ [[feedback_pptx_repack_include_all_parts]] の手順で全エントリを入れ、検査してから渡す。
