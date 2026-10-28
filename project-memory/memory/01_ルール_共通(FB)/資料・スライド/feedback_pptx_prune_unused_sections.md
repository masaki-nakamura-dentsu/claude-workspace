---
name: feedback-pptx-prune-unused-sections
description: "Standing rule — when building/editing PowerPoint files, proactively strip unused template slide layouts (\"セクション\") to keep file size down, without being asked each time"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 86655793-9c0c-4cdd-867b-e20342b361f7
  modified: 2026-08-17T07:30:33.952Z
---

When a pptx is built from a large template (e.g. [[dentsu_pptx_template]], which ships 70+ slide layouts under one master, each often carrying its own multi-MB background image), don't leave all the unused layouts sitting in the saved file. Proactively prune slide layouts that aren't actually used by any slide in the deck, by default — don't wait for the user to notice the file size and ask.

**Why:** Stated explicitly 2026-08-17 (AI活用PJ_アンバサダーキックオフ deck) after the user asked to compress an already-delivered 41MB pptx. Removing 67 unused layouts (out of 70) cut it to 33MB with zero visual/content change. The user then generalized this to a standing rule: "今後も同じですが私が依頼しない限り、セクションは削除してください" — going forward, prune unused sections/layouts by default unless told to keep them all.

**How to apply:** After building a pptx (via python-pptx) from any multi-layout template, before considering the file done:
1. Determine which slide_layout names are actually referenced by slides in the final deck.
2. For the slide master, remove every `sldLayoutId` not in that used set (`master.part.drop_rel(rId)` + remove the `sldLayoutId` element from `sldLayoutIdLst`).
3. Save — python-pptx's package writer automatically drops now-unreferenced layout parts (and their unique media, e.g. per-layout background art) on save; no manual zip surgery needed for this step (verified empirically: 70→3 layouts auto-pruned the corresponding `slideLayoutN.xml` parts from the saved zip).
4. Re-render via qlmanage (per [[feedback_pptx_visual_qa_method]]) to confirm nothing broke before calling it done.

This does NOT extend to compressing/downscaling legitimately-used content (e.g. embedded photos) — that changes visual fidelity and should only be done if asked. Pruning unused template layouts is pure dead-weight removal with zero visual impact, which is why it's safe to do by default.

## 追記 2026-10-21: PowerPointの「セクション」(sectionLst)も必ず削除
電通テンプレの `ppt/presentation.xml` には `<p14:sectionLst>` が入っており（Intro / Title slides / Contents slides / Section dividers / Text layouts …）、サンプルスライドを消してもセクション名だけが残る。ユーザー指摘「電通フォーマットを使う時、元々入っていたセクションが残ってしまっている。今後はすべて削除」（常設ルール）。

**How to apply**: 電通テンプレから作る pptx は、保存前に必ず `presentation.xml` の extLst 内 `p14:sectionLst` を丸ごと削除する（該当 `<p:ext uri="{521415D9-36F7-43E2-AB2F-B90AF26B5E84}">` ごと除去）。python-pptx なら `prs.part._element` から `.//{http://schemas.microsoft.com/office/powerpoint/2010/main}sectionLst` を探して親 ext を remove。新たに独自のセクションを作るのは本人が頼んだときのみ。保存後 `unzip -p … ppt/presentation.xml | grep -c sectionLst` が 0 であることを確認する。レイアウト削除（上記）と併せて毎回実施。
