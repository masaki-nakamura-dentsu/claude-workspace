---
name: feedback-check-surrounding-rows-before-manual-entry
description: "Before manually typing a value into a spreadsheet cell (not via formula), check neighboring rows/cells to confirm the formatting convention in force (e.g. half-width kana, stripped corporate suffixes) and match it — don't just type the literal source text"
metadata: 
  node_type: memory
  type: feedback
  modified: 2026-07-30T06:01:00.550Z
  originSessionId: 52b76e27-dfb0-4aa9-950c-26a01c69765c
---

Root-caused during a QBR NULL-troubleshooting session ([[qbr_2026q2_bridge_chart_and_tableau_pitfalls]], [[qbr_0708_rollback_tableau]]): the "セイコーグループ株式会社" client name showed up full-width in a Tableau chart while every other client name was half-width katakana. Root cause: in a prior session (2026-07-27), when manually filling in a real client-name shorthand for a client-less deal in `Client Name_CAS_SF_FY22 TO DATE.xlsx`'s `List - Project` sheet (column C), the value was typed in as plain full-width text, overwriting a cell that would otherwise have held `=ASC(B_)` — silently breaking the half-width-kana convention that every other row in that column (and the parallel `List` sheet's `クライアント名（調整後）` column, via `=SUBSTITUTE(SUBSTITUTE(ASC(A2),"(株)",""),"株式会社","")`) follows. A second identical instance (トヨタ自動車株式会社, row 612) was found in the same column during cleanup — same bug, same session, undetected until now.

**Why**: this class of data-entry bug is invisible at entry time (the cell just holds the "obviously correct" text you typed) and only surfaces later, downstream, as a cosmetic inconsistency in a dashboard — by which point the connection back to "I typed this by hand three weeks ago without checking the column's formatting rule" is easy to miss entirely.

**How to apply**: any time a value is being manually typed into a spreadsheet cell (as opposed to computed by a formula or copied verbatim from an authoritative source), check a few neighboring rows in the same column first to infer the convention in force — half-width vs full-width kana, corporate-suffix stripped vs kept, date format, casing, etc. — and match it, rather than typing the source text as-is. This applies to the user's own manual entry too (he said he'll watch for it), but especially to mine, since I don't get the same "this looks off" gut-check a human typing into their own familiar sheet would get. Worth a quick post-hoc grep across the same column for other literal (non-formula) values whenever this kind of bug is found, since — as happened here — one instance often isn't the only one.

See [[feedback_verify_against_ground_truth]] for the broader "check the authoritative source before asserting/entering" pattern this is one case study of.
