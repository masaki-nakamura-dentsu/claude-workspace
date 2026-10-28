---
name: feedback-verify-against-official-totals
description: "When reconciling financial/reporting data, always cross-check derived interpretations against an official summary total before reporting a discrepancy — and expect the same-looking metric (e.g. '確度A') to mean different things in different files"
metadata: 
  node_type: memory
  type: feedback
  modified: 2026-09-05T04:51:43.997Z
  originSessionId: cc64e5ab-3b2b-493d-9622-597e1ccdd273
---

During the [[qbr_0708_rollback_tableau]] task, I (Claude) misinterpreted a column's meaning twice in the same session — first guessing KPI0708's "A" column was cumulative (実績+A), then "correcting" to standalone-A after finding a matching subtotal row, before the user finally clarified the real (file-dependent) convention. Both of my own guesses were plausible-looking but wrong.

**Why**: financial reporting spreadsheets in this GBC/QBR context reuse the same short labels ("A", "確度A", "見込") across multiple files/sheets with **different actual definitions** (e.g. the source pipeline file's "A" intentionally includes past months as an actual-stand-in, while the Tableau-facing files' "A" is future-only). Nothing in the column headers signals this — it's tribal knowledge the user (or 山本さん) holds, not something derivable from the spreadsheet alone.

**How to apply**:
- When a computed/derived number doesn't match an official total, show the arithmetic explicitly (the user responded well to seeing exact figures and the mismatch spelled out) rather than silently picking one interpretation.
- But don't over-trust a numeric coincidence either (I initially treated "my sum ≈ their column" as proof of standalone-A, when actually two DIFFERENT definitional conventions across two different files can produce numbers that are each internally self-consistent but mean different things) — when the user provides a business-logic explanation for why numbers reconcile, prefer that over re-deriving from raw data, but still sanity-check it arithmetically before accepting (in this case the first "実績+A" claim genuinely didn't reconcile numerically and was worth pushing back on; the follow-up "past-A stands in for 実績" explanation did reconcile and was correctly accepted).
- Expect to have to re-apply/revert the same edit multiple times as understanding evolves (happened 3x here: filter out 1-6月 → revert → re-apply) — don't treat this as wasted work, keep the same reusable scripts/pickles around during a session so reverting is cheap.

See [[feedback_verify_against_ground_truth]] for the broader "check the authoritative source before asserting" pattern this is one case study of.

**2026-09-05追加事例([[powerbi_cover_dashboard_project]])**: JCIのWon/Lost前年比を生データ(Salesforceレポートエクスポート)から独立検算した際、最初はWonが3.5pt乖離した。原因は素朴に`GBCPhase__c`(生のフェーズテキスト)の「完了・成立 (Complete)」だけをWonとしてカウントしたが、PowerBI側は`Phase2`という派生列で「進行中/受注済み (Order Received)」もWonに含めていたため。**教訓**: フィルタ条件(部署/レコードタイプ等)が完全一致していても、生データを素朴集計するだけでは不十分——PowerBI/Tableau側で新たに作られた派生・分類列(Phase2のような)の定義を必ず先に確認してから検算すること。
