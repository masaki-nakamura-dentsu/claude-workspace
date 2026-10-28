---
name: qbr-2026q2-null-join-troubleshooting
description: "2026-07-30 QBR Q2 session — root-caused and fixed NULL 案件名/市場/事業区分 in '1. QBR_CAS実績' and full-width-kana inconsistency in '4. QBR_貢献実績' Tableau workbooks; what's fixed vs still open"
metadata: 
  node_type: memory
  type: project
  modified: 2026-07-30T06:01:53.565Z
  originSessionId: 52b76e27-dfb0-4aa9-950c-26a01c69765c
---

Follow-on to [[qbr_0708_rollback_tableau]] and [[qbr_2026q2_bridge_chart_and_tableau_pitfalls]]. Masaki noticed NULLs and a full-width-kana outlier in the QBR Q2 Tableau dashboards and asked to resolve them.

## Issue 1: NULL 案件名/市場/事業区分 in `1. QBR_CAS実績 V1.0.twb` ("Actual List (Q)" worksheet, titled "当四半期実績 案件上位一覧")
Data model: `Raw YTD`(actuals) —[受発注ヘッダNo]→ `Crosstable`(bridge) —[案件ID]→ `（設定突合用）SF案件リスト`(Salesforce item detail: 案件名/部署/地域/市場/事業区分). クライアント名 comes via a separate, independent join (`Raw YTD.クライアント名` = `List.クライアント名※5000件`) — this is why NULL rows still show a client name: that field survives even when the Crosstable→SF chain breaks.

For 2026Q2, 22 revenue rows (across ~10 distinct 受発注ヘッダNo) failed the Crosstable→SF join. Root causes, memorize by category since they look identical in the dashboard but need different handling:
1. **True Crosstable data-entry typo** (only 1 confirmed instance): a trailing full-width space (`　`) appended to the 案件ID in `Prep_CAS X SF Crosstable.xlsx` row 443 (資生堂ジャパン, header 202312609004). Fixed directly in the live file (Tableau has an absolute path reference to this exact filename — rename-with-date-suffix is NOT an option for files a `.twb` connects to; back up under a dated copy instead, then edit the original in place).
2. **Looked like a typo, WASN'T** (important correction — I got this wrong initially): カネボウ化粧品 6 headers, all pointing to `a1hGA00000A1GZT`/`a1hGA00000AG0ZT`. I flagged these as likely copy-paste ID errors (nearest valid SF id was `a1hGA00000A0GZT`, 1-2 edit distance, but wrong market — Thailand vs the rows' actual マレーシア/韓国/ベトナム). Masaki checked the true master source (`☆受発注設定リスト/☆【2026】受発注設定リスト<date>.xlsx`, sheet `受発注設定リスト`, cols `受発注ヘッダNo.`/`案件ID`) and confirmed these IDs are **correct** — the real cause is the same as category 3 below. **Lesson: always check `☆受発注設定リスト` (the actual order-registration master) before concluding a bridge-table ID is a typo** — string-similarity to a valid ID is not evidence of a typo when a definitive master source exists.
3. **SF案件リスト export genuinely missing the record** (confirmed root cause for カネボウ 6 headers + originally also アメックス 1 + タカラトミー 2): the referenced Salesforce ID is verified correct against `☆受発注設定リスト` but simply doesn't exist anywhere in `Prep_SalesforceAllRecord.xlsx` (checked both the processed sheet and `_Original`, case-insensitively) — not fixable by editing local files, needs a fresh/broader Salesforce export. Masaki refreshed `Prep_SalesforceAllRecord.xlsx` mid-session (5,166→5,233 rows) and it fixed one item (タカラトミー Anime India) but did NOT bring in the カネボウ/タカラトミー-freight/アメックス IDs — Masaki is now asking the Salesforce report owner directly why these specific records are excluded from the export.
4. **Legitimate non-project sentinels** (not bugs, don't chase): `受発注ヘッダNo` = `振替原価`/`調整`/`不明`/`(空白)` (internal accounting-adjustment entries, no real 案件 to link — 5 such rows total in Raw YTD) and Crosstable `案件ID` = literal `SF登録無し`/`SF案件該当なし`/`中止` (deal was genuinely never registered in / was cancelled in Salesforce). These will always show NULL in this join and that's correct behavior, not a defect.

### Disposition as of session end
- ✅ 資生堂 (whitespace typo) — fixed.
- ✅ アメックス H10-2606024753 — Masaki supplied the correct id `a1hfP000007Le1d` (verified present in SF list), applied to Crosstable.
- ⏸️ タカラトミー 2 headers (インド輸送費往路, ¥53,964+¥26,250) — Masaki said leave as-is, amount too small to chase.
- ⏳ カネボウ化粧品 6 headers (net ~¥1.66M across headers) — Masaki is asking the Salesforce/report owner why `a1hGA00000A1GZT`/`a1hGA00000AG0ZT` aren't in the SF案件リスト export. Waiting on that answer before further action.
- All fixes applied directly to the live-referenced files (`Prep_CAS X SF Crosstable.xlsx`), dated backup made first (`_20260730.xlsx`), then the [[openpyxl_empty_v_tag_corruption]] empty-`<v>` fix re-applied after every save (this file has ~6,628 formula cells across its 2 sheets, so the corruption risk is real, not hypothetical).

## Issue 2: full-width クライアント名 outlier in `4. QBR_貢献実績 V1.0.twb`
"セイコーグループ株式会社" showed full-width while every other client name in the same chart was half-width katakana. Different data model from Issue 1 — this workbook joins `貢献実績` to `List`/`List - Project` via classic physical LEFT JOINs (not Tableau relationships): `クライアント名（調整後）` normally comes from `List` sheet col E (formula `=SUBSTITUTE(SUBSTITUTE(ASC(A2),"(株)",""),"株式会社","")`, i.e. half-width-kana + strip corporate suffix). When that's null/blank (deal has no client match), a Tableau calc falls back to `月別見込親案件: 案件名/Item title（調整後）`, sourced from `Client Name_CAS_SF_FY22 TO DATE.xlsx`'s `List - Project` sheet col C (normally `=ASC(B_)`, half-width only, suffix kept).

Root cause: in the 2026-07-27 session ([[qbr_0708_rollback_tableau]]), when manually filling in real client-name shorthands for client-less deals in `List - Project` col C, the value for "Seiko TH Mediaﾋﾟｯﾁｻﾎﾟｰﾄ" (row 2170) was typed as literal full-width text (`セイコーグループ株式会社`), overwriting the `=ASC(B_)` formula and breaking the half-width convention. Found and fixed a **second** identical instance in the same column while checking (row 612, `トヨタ自動車株式会社`→`ﾄﾖﾀ自動車株式会社`, Toyota Fortuner pitch deal) — not reported by Masaki, found by grep-style scan of the column for other non-formula cells containing corporate-suffix tokens. Both fixed directly in `Client Name_CAS_SF_FY22 TO DATE.xlsx` (dated backup `_20260730.xlsx` made first, empty-`<v>` fix re-applied — this file also has formula cells, ~hundreds).

See [[feedback_check_surrounding_rows_before_manual_entry]] for the standing lesson Masaki gave in response to this: check neighboring rows' convention before typing literal values into a spreadsheet, and this applies to me even more than to him.

## Reusable technique
For "why is this Tableau field NULL/wrong" questions in this GBC data ecosystem generally: read the `.twb` XML directly (`grep` for the worksheet's `<datasource-dependencies>` and either `<relationships>` (Tableau logical relationships — NULLs happen because the relationship graph doesn't guarantee a match) or `<relation ... type='join'>` (classic physical joins — same idea but check join type: left/inner) to find the exact join keys, then reproduce the join in Python over the local `.xlsx` mirrors to find the specific failing rows. `☆受発注設定リスト/☆【20XX】受発注設定リスト<date>.xlsx` (sheet `受発注設定リスト`, header row **2** not 1) is the authoritative master for 受発注ヘッダNo↔案件ID↔クライアント/件名 — check it before assuming a bridge-table ID is wrong.
