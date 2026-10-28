---
name: feedback-powerbi-ui-label-accuracy
description: "In Power BI Service instructions, use exact ribbon/button labels as Masaki reports them, not remembered/assumed names"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3fddbbf3-3ad0-40e2-8042-a83559aa15a8
  modified: 2026-09-05T09:06:11.747Z
---

When giving Power BI Service click-path instructions, use the exact UI label Masaki has confirmed, not a plausible-sounding one from memory. Concrete case (2026-07): repeatedly instructed "「セマンティック モデルを開く」→「クエリの編集」" to open Power Query, but the actual button is labeled **「データの変換」**, not "クエリの編集". He had to correct this more than once before it was fixed in [[powerbi_migration_gbc_dashboard]].

**Why:** Wrong button names cost him a lookup/hunt each time, and he shouldn't have to keep re-correcting the same label. This specific path was corrected TWICE (2026-07): first "クエリの編集" → "データの変換", then again to add the missing intermediate step — full correct path is **「セマンティック モデルを開く」→「クエリ」→「データの変換」** (a ribbon group labeled "クエリ" containing the "データの変換" button, not a single "データの変換" button directly off the semantic model screen).

**How to apply:** When a user corrects a UI label/button name in this project, immediately fix it everywhere it appears in project memory (grep for the old label across memory files), not just acknowledge it in chat. Going forward, prefer whatever exact label a screenshot or the user's own words most recently confirmed over a remembered generic term.

**Power BI Desktop (2026-09-05, [[powerbi_cover_dashboard_project]])**: 積み上げ横棒グラフに予算などの定数線(参照線)を追加する正しい手順は「ビジュアルを選択→視覚化ペインの「分析」タブ(ペンのアイコン)→「X軸の定数線」→フィールドに対象メジューを指定」。以前「Analyticsタブ→一定の線を追加」という曖昧な表現で案内したが不正確だった。

**重要な再発事例(2026-09-05)**: `貢献_年別推移`ページのスライサー不具合を調査中、「対話の編集」の場所をDesktop版のリボン構成(書式タブ)を前提に繰り返し案内してしまい、正樹さんに「何度も言いますが、私はブラウザ版のPowerBIなのでリボンで「書式」というのはありません」と強めに訂正された。実際に共有されたスクリーンショットでは、Power BI Service編集画面のリボンは「ファイル/ビュー/閲覧表示/モバイルレイアウト/セマンティックモデルを開く」のみで、Desktop版の「書式」「モデリング」「挿入」タブは存在しない。**教訓**: 正樹さんは主にPower BI **Service(ブラウザ版)**で作業しており、Desktop版のリボン構成(書式/モデリング/挿入タブ)をそのまま前提にした案内は繰り返し外れる。UI操作を案内する前に、まず「今どちらを使っているか」「リボンに何が見えているか」を確認してから手順を組み立てること。ブラウザ版で見えているリボンタブの実際の並びは上記の通り(2026-09-05時点)。

**一般化(2026-10-12週次レビューで追記)**: 「Power BIは常にブラウザ版(Service)前提で手順を書く」というルールは [[feedback_powerbi_browser_only]] に独立させた。
