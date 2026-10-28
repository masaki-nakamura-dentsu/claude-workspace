---
name: feedback-pptx-use-real-example-photos
description: "Standing rule: proposal/report materials should include actual example photos wherever possible, not just text/charts — and photos must be shown clearly (no circular crop hiding detail, no contradictory/unrepresentative examples)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08c80e0c-bfb3-4666-856b-deb9e3b9cbaa
  modified: 2026-09-02T07:27:47.651Z
---

Whenever building a proposal, report, or any material that references real-world examples (competitor photos, reference images, past work), include the actual photos themselves — not just a text description or a summary chart. This applies across all projects, not just photography-specific ones.

**Why**: Explicitly stated as a standing rule (2026-09-02, [[ikeda_coaching_profile_photo_project]]) after a coaching-profile-photo proposal deck used real photos, but in a way the user still flagged as inadequate: (1) photos were combined into a single 3x3 grid image dropped into a layout's circular PICTURE placeholder — the circular crop cut off the corners of the grid, making individual photos hard to distinguish; (2) the curated "high-price tier" example set was chosen mechanically (top-N by price) without checking each photo actually matched the claimed pattern — one included photo (small森田真也, a clothes-rack/wardrobe background) visually contradicted the slide's own claim that high-price coaches use plain/solid backgrounds, which read as a logical inconsistency to the user.

**How to apply**:
1. Prefer real photos over grid-montage-crammed-into-one-placeholder. If a layout's picture placeholder applies a mask (circular crop is common for "headshot"-style layouts in the [[dentsu_pptx_template]]), either place each example photo as its own separate rectangular picture shape (not relying on the masked placeholder), or pick a layout without a masking crop.
2. Hand-curate example photos, don't just sort-and-slice by a metric (price, date, etc.). Open and actually look at each candidate before including it as an example of a claimed pattern — an image that contradicts the point being made (even if it technically ranks in the top N) undermines the argument and should be swapped for a genuine match or explicitly noted as an exception.
3. Label each individual example photo (name/price/whatever identifying context) so the reader can tell them apart, rather than relying on a single caption under a whole grid.

**2026-10-12追記**: 市場調査系の資料でも、文字と数字だけだと「市場の様子が分からない」と指摘された(CC大阪ホーチミン資料)。現地の写真やサイト画面を最初から入れる。画像の入手は Wikimedia Commons API(ライセンス・作者をテキストで取得) + ヘッドレスPlaywrightでのサイト撮影 + 記事内画像の取得で行い、画像の確認は一覧1枚にまとめて読む。

関連: [[pptx_visual_first_policy]]
