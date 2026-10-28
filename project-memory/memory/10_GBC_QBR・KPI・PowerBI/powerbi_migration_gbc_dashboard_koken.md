---
name: powerbi-migration-gbc-dashboard-koken
description: "New \"貢献利益\" (contribution profit) initiative within the GBC Power BI dashboard migration — data source research and build plan"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3fddbbf3-3ad0-40e2-8042-a83559aa15a8
  modified: 2026-09-07T03:58:11.914Z
---

Follow-on to [[powerbi_migration_gbc_dashboard]]. After finishing the 売上総利益 (gross profit) pages (Q_前年比 / 月別_前年比 / 年別推移), Masaki asked to build an equivalent 3-page set for **貢献利益** (contribution profit — GBC's department doesn't book its own P&L profit but "contributes" to other overseas dentsu offices' P&L, so this is a cross-charge/attribution metric, not the same as 売上総利益).

## Source files (local mirror paths, same OneDrive folder as before)
- `.../QBR作成/GBC 貢献実績_FY22 TO DATE.xlsx` — sheet **`貢献実績`**, 26 columns (not 19 — early inspection with `row[:20]` truncated and missed the last 6, causing a wasted round of back-and-forth; always print full header length before concluding columns are missing).
- `.../QBR作成/GBC 貢献見込_LATEST.xlsx` — sheet **`貢献見込`**, identical 26-column schema to the actual file.
- Both share: `年度`, `月`, `確度` (A/B/C/X — actual file has this full spread too, NOT just "confirmed" rows), `月別見込親案件: GBC貢献度/Attrib. Ratio`, `月別見込親案件: GM確認/Confirmed`, `Group売総/Revenue (JPY)`, `月別集計用/GBC貢献売総(A)/Att.Rev(A)(JPY)`, `月別集計用/GBC貢献売総(AB)/Att.Rev(AB)(JPY)`, `月別見込親案件: 月別集計用/GBC貢献売総(ABC)/Att.Rev(ABC)(JPY)`, `GM承認/Auth.`, `月別集計用/GBC貢献売総(計上)/Attrib. Rev(Rec.)(JPY)`, `DATEVALUE`.

## Value-column methodology (reverse-engineered from 3 old Tableau workbooks in the same folder: `4. QBR_貢献実績 V1.0.twb`, `5. QBR_貢献見込 V1.0.twb`, `6. QBR_貢献実績+見込 V1.0.twb`)

**実績 (actual) → use `月別集計用/GBC貢献売総(計上)/Attrib. Rev(Rec.)(JPY)` directly, summed with NO further 確度 filtering.**
Verified by reading actual cell values: this column = `Group売総 × Attrib.Ratio` **if `GM承認/Auth.` = TRUE, else 0** — i.e. gated purely on GM sign-off/authorization, completely independent of the 確度 (A/B/C/X) tag. The dedicated actual-only Tableau workbook confirms this via a calculated field `確度（実績集計用） = "Actual"` (hardcoded — no confidence filtering applied at all for the actual report). Do NOT filter this column by 確度; the (計上) column already encodes the correct "is this booked/authorized" logic on its own.

**訂正(2026-09-07、[[qbr_koken_ratio_kakudo_filter_bug_20260907]]で発覚)**: 上記の「GM承認だけで決まり確度とは完全に無関係」という記述は不正確だった。実データ(`GBC 貢献実績_FY22 TO DATE.xlsx`)で確度×GM承認をクロス集計すると、確度=B/C/XでGM承認=Trueの行が29件(全期間)存在するが、その全てで計上額(Att.Rev計上)は0円だった。つまりこの列は実質的に「確度=A **かつ** GM承認=True」の場合のみ非ゼロになる。実績合計(分子)を出すだけなら確度フィルタの有無で結果は変わらない(上記の結論自体は引き続き正しい)が、**「貢献度%」= 計上額/Group売総 のような比率を計算する場合、分母(Group売総)に確度=Aフィルタを掛けると指標の意味が変わってしまうので絶対にやってはいけない**(見込み案件全体の想定規模に対する進捗率 → 確定案件内だけの計上率に変質し、比率が約1.7倍に跳ね上がる実例が発生した)。

**見込 (forecast, confidence-stacked) → use raw `Group売総 × Attrib.Ratio` per row, summed and grouped by `確度` as the stack legend** — same pattern as the existing 売上総利益 forecast chart (`見込_合計` measure grouped by `CAS見込[確度]`). Tableau's own `貢献売総` calculated field is exactly `IF Group売総=0 THEN NULL ELSE Group売総 * Attrib.Ratio END`, and the forecast-only workbook builds confidence-band series (`見込A = IF 確度="A" THEN 貢献売総 ELSE 0`, etc.) on top of that raw value — do NOT use the pre-baked (A)/(AB)/(ABC) columns for the stacked-by-確度 chart, since those are cumulative/inclusive (AB includes A+B) rather than mutually-exclusive per band, which would double count if used as stack segments. Compute the raw per-row product directly instead (either as a Power Query custom column or a DAX calculated column).

## Build plan (agreed 2026-07-13, not yet started)
Decided to finish ALL data import/modeling first (raw table import, Power Query, column renames/relationships mirroring the `Raw YTD`/`CAS見込` pattern) before building any of the 3 report pages, then build Q別/月別/年別 pages together at the end, reusing all the DAX/measure/relationship patterns already validated for 売上総利益 (see breakthroughs and gotchas logged in [[powerbi_migration_gbc_dashboard]] — cardinality direction ("一対多" not "多対一"), VAR names must be ASCII, TREATAS for client-slicer cross-filtering instead of physical relationships, axis-max headroom multipliers, etc. — all directly reusable here).

## Progress update (2026-07-13 session 2) — 貢献_年別推移 done, 貢献_Q別推移 in progress

Both `貢献実績`/`貢献見込` tables imported, merged with `クライアント名変換`, relationships to `四半期`/`月` built (cardinality "一対多" per the breakthrough in [[powerbi_migration_gbc_dashboard]]). Core measures built: `貢献実績_合計`, `貢献度平均`, `貢献見込_合計`, `貢献実績_前年合計`, `貢献度平均_前年`, `貢献実績_全期間合計`, `貢献度平均_全期間`, unified stack measure `貢献積み上げ値` (branches on disconnected legend table `凡例_貢献実績見込` values `実績`/`A`/`B`/`C`), all using the `ISFILTERED`+`ALL` pattern to fix TREATAS client-slicer bugs (same as 売上総利益's `見込_合計`). `貢献_年別推移` page complete.

**`貢献_Q別推移` page — chosen design**: NOT a single combo chart. Two separate overlaid visuals (前年専用グラフ: plain columns `貢献実績_前年合計` + line `貢献度平均_前年`; 今年専用グラフ: stacked columns `貢献積み上げ値` w/ legend `凡例_貢献実績見込[項目]` + line `貢献度平均`), manually position-matched (全般→プロパティ X/Y/幅/高さ) and manually offset with increased category-gap spacing so bars sit side-by-side per quarter, with the front visual set to ~60% transparency. This was necessary because: 2-level axis (Quarter × 年ラベル) had uncontrollable spacing and single-line zigzag problems; two stacked measures in one "積み上げ" chart get summed together instead of clustering. X-axis labels use calculated columns `四半期[四半期表示_前年]` = `"前年" & Quarter` and `四半期[四半期表示_今年]` = `"選択年" & Quarter` (NOT "今年" — user caught that "今年" is wrong when a non-current year is selected via the 計上年 slicer; "選択年" is accurate since it's relative to whatever year is picked). Both new columns sort-by `QuarterSort`.

**Axis max sync**: created `貢献軸_最大値_Q` / `貢献率軸_最大値_Q` measures in `貢献実績` table (MAXX over quarters of the larger of 前年/今年 totals, ×1.15 and ×1.3 headroom respectively — same pattern as `グラフ軸_最大値_月` etc. in [[powerbi_migration_gbc_dashboard]]), bound to both charts' Y-axis max via the format pane's fx/"フィールドの値" conditional-formatting binding. This is dynamic (recalculates when 計上年 slicer changes) — a **fixed numeric axis max is wrong** here since the underlying totals change per selected year.

**Measure placement convention established**: new measures go in whichever table already holds their closest sibling measures (e.g. all 貢献実績-derived axis/total measures live under the `貢献実績` table, even ones that reference `貢献見込` too) — not a separate dedicated measures table. User explicitly asked to be told this reasoning going forward rather than re-asked each time.

**計上組織名 slicer cross-filter bug (found 2026-07-13, partially fixed)**: same root cause as the client-slicer TREATAS bug — `貢献実績_合計` etc. only had TREATAS logic for client, not org, so the `計上組織名` slicer didn't filter the 貢献 pages at all. Fix pattern: since `IF(cond, CALCULATETABLE(...), ALL(...))` (an IF returning a table) throws the same "TREATAS argument must be a table expression" error as the old CALCULATE/CALCULATETABLE bug, do NOT try to branch at the table-VAR level — instead branch the whole CALCULATE call via nested scalar-returning `IF`s (4 branches: client-only-filtered / org-only-filtered / both-filtered / neither), each a separate full `CALCULATE(...)` call. Applied to `貢献実績_合計`, `貢献度平均`, `貢献実績_前年合計`, `貢献度平均_前年`, `貢献実績_全期間合計`, `貢献度平均_全期間`, `貢献見込_合計`.

**Org code text-mismatch discovered while testing**: `Raw YTD[計上組織名（調整後）]` slicer only offers 6 values: `AP1, AP2, AP3, BD, SP1, SP2`. But:
- `貢献見込[月別見込親案件: 部署名/Dept.]` has every value suffixed with "部" (`AP1部`, `BD部`, etc.) — **fixed** by adding calculated column `貢献見込[組織名_調整後] = SUBSTITUTE('貢献見込'[月別見込親案件: 部署名/Dept.], "部", "")` and repointing `貢献見込_合計`'s TREATAS to that column instead of the raw one.
- `貢献実績[月別見込親案件: 部署名/Dept.]` has extra/different codes: `BD1, BD2, GS1, GS2, NB1, NB2, NS, SK` (not suffixed, just genuinely different code set from Raw YTD's 6). **Confirmed with user (2026-07-13)**: `BD1`/`BD2` are legacy sub-codes of `BD` that should now roll up into `BD` (used to be split, now reported as one). `GS1/GS2/NB1/NB2/NS/SK` are fully deprecated org codes that no longer exist as of the 2026 fiscal year (so they naturally won't appear when 計上年=2026 is selected) — user confirmed these do NOT need to be added as new slicer options, they just need to keep counting correctly in the "すべて" (unfiltered) grand total, which the existing `OrgIsFiltered`-conditional-branch design already guarantees (TREATAS is skipped entirely when the org slicer has no selection, so these rows are never dropped in that case).

**NOT YET DONE (next session, starting point)**: add `貢献実績[組織名_調整後]` calculated column:
```
組織名_調整後 = 
SWITCH(
    '貢献実績'[月別見込親案件: 部署名/Dept.],
    "BD1", "BD",
    "BD2", "BD",
    '貢献実績'[月別見込親案件: 部署名/Dept.]
)
```
then repoint the TREATAS calls in `貢献実績_合計`, `貢献度平均`, `貢献実績_前年合計`, `貢献度平均_前年`, `貢献実績_全期間合計`, `貢献度平均_全期間` (all 6, in the `貢献実績` table) from `'貢献実績'[月別見込親案件: 部署名/Dept.]` to `'貢献実績'[組織名_調整後]`. This should also resolve the "実績の合計が合っていない" discrepancy the user flagged, since some 実績 rows (BD1/BD2) were being silently excluded whenever a specific org was selected due to the code mismatch.

After that: verify org-slicer totals reconcile correctly on `貢献_Q別推移`, then carry the same TREATAS+org pattern to `貢献_年別推移` (whose measures currently only got the client-branch treatment — need to check if it already went through the same 4-branch org fix or still needs it), then build `貢献_月別推移` reusing the two-overlaid-chart technique validated on `貢献_Q別推移`.
