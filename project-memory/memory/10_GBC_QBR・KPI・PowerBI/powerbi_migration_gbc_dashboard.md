---
name: powerbi-migration-gbc-dashboard
description: Progress and technical setup of the Tableau→Power BI migration for the GBC数字管理レポート dashboard
metadata: 
  node_type: memory
  type: project
  originSessionId: 3fddbbf3-3ad0-40e2-8042-a83559aa15a8
  modified: 2026-08-26T05:24:06.779Z
---

Masaki is migrating a Tableau-based GBC業績分析 dashboard to Power BI, working entirely in **Power BI Service via browser on a Mac** (no Power BI Desktop — Desktop doesn't run on macOS). Previously consulted ChatGPT for this (history in `20260709PowerBI_数字ダッシュボード開発/ChatGPTの相談内容20260709.pdf`); now continuing with Claude, one step at a time, with Claude doing all research/investigation itself and giving copy-paste-ready DAX + precise click paths.

## Data sources (important — two different locations exist)

- **Live production data Power BI actually reads from**: `aicon@dentsu.co.jp` shared OneDrive account (a team-shared account created specifically so the dashboard doesn't break if Masaki leaves/loses access — deliberate design choice, not an accident). Path: `https://esq365-my.sharepoint.com/personal/aicon_dentsu_co_jp/Documents/戦略企画部/GBC数字分析関連資料/`
  - `GBC CAS実績_FY22 TO DATE.xlsx` → sheet **"Raw YTD"** is the main fact table Power BI imports. Columns: 計上組織名（調整後）, 受発注ヘッダNo, クライアント名, 件名, 計上年, 計上四半期, 計上月, 社内受注元組織／発注先名, サービスカテゴリレベル1名/2名, 備考, 売上金額, 原価金額, 売上総利益, DATEVALUE.
  - `Client Name_CAS_SF_FY22 TO DATE.xlsx` → sheet **"List"**, col A = 元クライアント名, col E = クライアント名（調整後）, 1249 rows, no dupes/blanks. Used as a lookup to map raw client names to cleaned names.
- **A separate, similarly-named local mirror** exists under Masaki's own OneDrive at `/Users/d14461/Library/CloudStorage/OneDrive-電通/GBC戦略企画部_GBC設定実績・見込/QBR作成/` (same filenames). **This is NOT what Power BI reads from live** — don't assume it's the same file; if inspecting data structure, prefer confirming against the actual M-code query in Power Query (visible via error dialogs / "詳細情報") over assuming the local mirror matches.

## Report structure built so far (all in one page, "GBC数字管理レポート")

- KPI cards: 売上金額_合計, 原価金額_合計, 売上総利益_合計
- Right chart: combo (column+line) — X axis `QuarterLabel`, columns = `指定年_動的`/`指定年の前年_動的` (renamed 指定年/指定年の前年), lines = `売上総利益率`/`売上総利益率_前年`. Percentage format set on the rate measures via semantic-model measure properties.
- Indicator switching: disconnected table `指標選択` (values: 売上総利益/売上/原価) + slicer bound to `指標選択[指標]`. Dynamic measures use `SWITCH(SELECTEDVALUE('指標選択'[指標]), ...)`.
- Year-over-year pattern: since `計上年` slicer is directly bound to `Raw YTD[計上年]` (not disconnected), `SELECTEDVALUE('Raw YTD'[計上年])` works for "current" and `-1` for "prior year" — no Date table needed, just plain CALCULATE+FILTER+ALL on the 計上年 column.
- `クライアント名_調整後` slicer added via Power Query merge (Raw YTD ⋈ クライアント名変換 on クライアント名=元クライアント名, left outer, expanded クライアント名_調整後 + D13クライアント).
- Left "全期間" (always full-history, ignores 計上年 filter) chart was built then **removed** per user's decision — instead planned as a **separate page later**, reusing measure `指定指標_全期間 = CALCULATE(SWITCH(SELECTEDVALUE('指標選択'[指標]), ...), ALL('Raw YTD'[計上年]))` (already created, unused for now).

## UI quirks learned about this specific Power BI Service version (no classic ribbon)

- No "書式" ribbon tab exists in this UI; "相互作用の編集" (Edit Interactions) could **not be located anywhere** (checked ビュー menu, right-click, "..." overflow, visual selected — genuinely seems unavailable in this version). Workaround: use disconnected-table + DAX (ALL/SELECTEDVALUE) patterns instead of relying on Edit Interactions to make one visual ignore a page-level slicer.
- Adding measures/tables: "セマンティック モデルを開く" (in report ribbon) → opens a full modeling ribbon (データ, クエリ, 新しいメジャー, 新しい列, 新しいテーブル, etc.) — this is the entry point for all DAX work, distinct from the report canvas.
- Power Query editing: from the same "セマンティック モデルを開く" screen → ribbon "クエリ" button opens Power Query Online.
- **Cross-source privacy level errors** (merging 2 Excel files from the same OneDrive account still triggers "プライバシー設定が異なるため結合できません"): the Service's dataset "設定" page → "データ ソースの資格情報" section is **read-only status display only, no working edit button** in this version. The actual fix is: reload the page to force Power Query to prompt re-authentication → in the "データ ソースへの接続" dialog that appears, set **プライバシー レベル → 組織用** (was defaulting to "なし"). This can also be reached via Power Query ホームタブ → "ソースの管理".

## 見込(forecast)機能 — 実装済み

Added a forecast display to the "Q_前年比" page. Source: `CAS見込` table imported from `GBC CAS見込_LATEST.xlsx` (sheet "CAS見込", on yamada_keita's OneDrive — see URL under 実績データ note below), column `GBC設定売総/SETTEI Rev(JPY)` renamed to `見込売総`. Calculated column `四半期 = "Q" & QUARTER('CAS見込'[DATEVALUE])`. Relationship: `CAS見込[四半期]` (many) → `四半期[Quarter]` (1), active.

Key measure (uses `ALL('四半期')` inside a VAR specifically to avoid a bug where filtering the shared `四半期` dimension by an axis value with no matching Raw YTD rows — e.g. a future quarter — collapses `SELECTEDVALUE('Raw YTD'[計上年])` to blank, since `四半期` also relates to Raw YTD and the relationship narrows Raw YTD's row set to zero for that quarter):
```
見込_合計 = 
VAR SelectedYear = CALCULATE(SELECTEDVALUE('Raw YTD'[計上年]), ALL('四半期'))
RETURN
IF(
    SELECTEDVALUE('指標選択'[指標]) = "売上総利益",
    CALCULATE(
        SUM('CAS見込'[見込売総]),
        FILTER(
            ALL('CAS見込'[年度]),
            'CAS見込'[年度] = SelectedYear
        )
    )
)
```
Lesson: **VAR names in this browser DAX editor must be ASCII/English** — Japanese VAR names (e.g. `選択年`) throw a parser syntax error ("無効なトークン") even though the rest of the DAX supports Japanese identifiers fine elsewhere (measure/table/column names in Japanese work normally).

Chart: stacked column, X axis = `四半期[Quarter]` (dimension table, "データのない項目を表示する" enabled so Q1/Q2 show even with no data), Y = `見込_合計`, legend = `CAS見込[確度]` (values A/B/C plus an unexplained 4th "X" category — flagged to user, not yet resolved, ask about it when convenient).

Axis sync: added `グラフ軸_最大値` measure (MAX of per-quarter 実績 `指定年_動的` and per-quarter `見込_合計`, both via `ALLSELECTED('四半期')`) bound to the Y-axis maximum (via the format pane's fx/conditional-formatting binding) on BOTH the actual combo chart and the forecast stacked chart, so the two share a scale. The two visuals are positioned to exactly overlap (matched X/Y/width/height in 全般→プロパティ), with the forecast chart's background set to 100% transparent so it sits "underneath" the actual chart visually (actual chart happened to end up frontmost by default — "move to front" wasn't found in this UI, so instead the back visual's background was made transparent, which achieves the same visual effect).

## 見込のクライアントフィルター連動 — 未解決、来週続き (as of 2026-07-10)

Goal: make the `クライアント名_調整後` slicer (bound to `Raw YTD[クライアント名_調整後]`) also filter the 見込 forecast chart, whose data lives in the separate `CAS見込` table.

**First attempt failed and was reverted**: a direct relationship `Raw YTD[クライアント名_調整後]` ↔ `CAS見込[クライアント名_調整後]` (after merging `クライアント名変換` into `CAS見込` via Power Query, same pattern as Raw YTD) caused the ENTIRE forecast chart to go blank — not just fail to filter. Cause: `Raw YTD` and `CAS見込` were already connected indirectly via `四半期`, so adding a second, direct relationship created a cycle in the relationship graph, and Power BI silently deactivated the existing `四半期`↔`CAS見込` relationship to resolve it. Fix: deleted the direct relationship, which restored the forecast chart.

**Current approach (in progress)**: build a proper shared dimension table instead of a direct relationship, to avoid the cycle:
```
クライアント_Dim = 
DISTINCT(
    SELECTCOLUMNS(
        FILTER(
            'クライアント名変換',
            'クライアント名変換'[クライアント名_調整後] <> BLANK()
        ),
        "クライアント名_調整後", TRIM('クライアント名変換'[クライアント名_調整後])
    )
)
```
Plan: relate `クライアント_Dim[クライアント名_調整後]` (1) → `Raw YTD[クライアント名_調整後]` (many) and → `CAS見込[クライアント名_調整後]` (many), both single-direction from Dim outward, then repoint the existing slicer from `Raw YTD[クライアント名_調整後]` to `クライアント_Dim[クライアント名_調整後]`.

**Blocker**: relationship creation keeps failing with "列 "" (テーブル "") には重複する値 "" が含まれています" (duplicate value on the "1" side) even after adding `<> BLANK()` filtering and `TRIM()` — tried both, error persists identically both times, including after recreating the table from scratch. The garbled/empty quotes in the error message (table name and value both show as blank placeholders) suggest either a stale-cache/not-fully-saved-model issue, or a genuine but hard-to-spot near-duplicate in `クライアント名変換[クライアント名_調整後]` (e.g. case-variant duplicates like "NTTデータ" vs a differently-cased version, which `TRIM` wouldn't catch). Not yet resolved.

**Resolved (2026-07-13) — abandoned the relationship approach entirely.** The "重複する値" relationship-creation error persisted even after confirming via DAX Query View that `クライアント_Dim` had zero duplicates (even case-insensitively), across table recreation, full browser restart, and using "リレーションシップの管理" instead of drag-and-drop — strongly suggesting a Power BI Service platform-level bug/glitch rather than a real data issue, not worth chasing further. Also noticed via the slicer search box that `Raw YTD[クライアント名_調整後]` itself contains near-duplicate values that render identically (e.g. two separate "資生堂" entries) — likely invisible whitespace/Unicode differences that DAX's `TRIM()` doesn't catch (it only strips ASCII space, not full-width U+3000 etc.) — another reason physical-key-based relationships were fragile here.

**Final working solution**: gave up on a physical relationship and filtered `CAS見込` directly from inside the `見込_合計` measure using **TREATAS**, which doesn't require uniqueness on either side:
```
見込_合計 = 
VAR SelectedYear = CALCULATE(SELECTEDVALUE('Raw YTD'[計上年]), ALL('四半期'))
VAR SelectedClients = CALCULATETABLE(VALUES('Raw YTD'[クライアント名_調整後]), ALL('四半期'))
RETURN
IF(
    SELECTEDVALUE('指標選択'[指標]) = "売上総利益",
    CALCULATE(
        SUM('CAS見込'[見込売総]),
        FILTER(
            ALL('CAS見込'[年度]),
            'CAS見込'[年度] = SelectedYear
        ),
        TREATAS(SelectedClients, 'CAS見込'[クライアント名_調整後])
    )
)
```
Two lessons baked into this final version:
1. Same "shared dimension narrows both fact tables" bug as `SelectedYear` originally had (see above) — `SelectedClients` also needed `ALL('四半期')`-wrapping, since without it, filtering the chart's Quarter axis to a future quarter (no Raw YTD rows) collapsed `VALUES('Raw YTD'[クライアント名_調整後])` to an empty table, blanking the whole measure for every quarter.
2. **`CALCULATE` vs `CALCULATETABLE`**: this browser DAX editor's live type-checker statically infers `CALCULATE(...)` as always scalar-returning, even when wrapping a table function like `VALUES()` — throwing "TREATAS 関数に対する引数 '' にはテーブル式が必要ですが、文字列式または数値式が使用されました" when a `CALCULATE`-wrapped table VAR is passed to `TREATAS`. Fix: use `CALCULATETABLE` explicitly whenever a VAR needs to hold a table (as opposed to `CALCULATE` for scalar VARs like `SelectedYear`).

The `クライアント_Dim` calculated table and its (never-succeeded) relationship attempt are still sitting in the model, unused — safe to delete if the model is cluttered, but harmless to leave.

**Also confirmed this session**: unsaved REPORT-canvas changes (new visuals, formatting, positioning) can be lost if the browser session drops before an explicit save — happened once, had to redo the forecast chart + axis-sync + overlay from scratch. Semantic model changes (measures/tables/relationships, edited via "セマンティック モデルを開く") survived that same incident fine. **Recommend saving frequently (Cmd/Ctrl+S) during report-canvas work specifically.**

## Breakthrough (2026-07-13): the real cause of ALL the "duplicate value" relationship errors

Root cause found while building a parallel `月` (month) dimension table for a new monthly-breakdown page: in this Power BI Service relationship-creation dialog, the **"テーブルから" (table dragged from) is the "多" (many) side, and "テーブル表示" (table shown alongside) is the "一" (1) side** when "多対一 (*:1)" is selected — i.e. the OPPOSITE of the intuitive reading. Every prior relationship attempt in this project (the abandoned `クライアント_Dim` ↔ Raw YTD/CAS見込 relationships, and initially this `月` ↔ Raw YTD one) was dragged from the intended "1" side (dimension table) to the intended "many" side (fact table) while leaving cardinality on "多対一 (*:1)" — which silently inverted the roles, making the fact table (with legitimately many repeated values) get validated as the "1" side, hence the endless "duplicate value" errors. **Fix: when dragging dimension→fact, change the cardinality dropdown to "一対多 (1:*)" instead of leaving the default "多対一 (*:1)".** This resolved the `月`↔Raw YTD relationship instantly with no other changes needed.

This means the `クライアント_Dim` approach (abandoned in favor of TREATAS, see above) might actually have worked fine with this one dropdown change — not revisited since TREATAS already works, but worth knowing if a future physical-relationship need comes up for client name.

## 月別_前年比 page — built 2026-07-13

Duplicated `Q_前年比` → renamed `月別_前年比`. Mirrors the quarter page but broken out by month.

- New `月` calculated table (DATATABLE, 月番号 1-12 + 月ラベル "1月".."12月", sort-by-column 月ラベル→月番号), same pattern as `四半期`.
- Added `月番号` calculated columns: `Raw YTD[月番号] = MONTH('Raw YTD'[計上月])`, `CAS見込[月番号] = MONTH('CAS見込'[DATEVALUE])`.
- Relationships `月[月番号]` (1) → `Raw YTD[月番号]` / `CAS見込[月番号]` (many) — cardinality had to be explicitly set to **「一対多 (1:*)」**, not the default "多対一 (*:1)", per the breakthrough above.
- Before this, found and removed genuine fully-blank trailing rows in Raw YTD's Power Query (filtered out blanks on 件名/DATEVALUE) — worth checking if similar blank-row issues resurface elsewhere.
- `見込_合計` generalized to clear both `四半期` and `月` filters (`ALL('四半期'), ALL('月')` in both VARs) so the same measure works correctly on both pages regardless of which axis table is filtering.
- New axis-sync measures mirroring the quarter ones, parameterized on `月` instead: `グラフ軸_最大値_月`, `利益率軸_最大値_月`. Also added a **headroom multiplier (`* 1.15`)** to both value-axis-max measures (`グラフ軸_最大値`, `グラフ軸_最大値_月`) and a **`* 1.3`** multiplier to both rate-axis-max measures (`利益率軸_最大値`, `利益率軸_最大値_月`) — without this, bars/lines touched the top of the chart and data labels got clipped.
- Both charts on the new page had X axis swapped from `四半期[Quarter]` to `月[月ラベル]`, "データのない項目を表示する" re-enabled, and Y-axis-max fx rebound to the `_月` measure variants.

## 案件別内訳ページ — built 2026-07 (new page: `案件別内訳`)

Masaki wanted a deal-level breakdown table for 売上総利益: 案件名/クライアント名/部署名/地域/市場/事業区分/売上総利益/比率, filterable by 年度・Quarter・部署名・クライアント名・地域・市場・事業区分. Problem: `Raw YTD` (the 売上総利益 source) has none of 部署名/地域/市場/事業区分/案件名 — those live in Salesforce data, keyed by `案件ID`, while Raw YTD is keyed by `受発注ヘッダNo` (CAS system). The two systems track different things: **CAS** = actually-booked revenue (`受発注ヘッダNo`), **Salesforce** = both future/pipeline revenue (設定売総見込) AND all 貢献売総 (実績+見込), keyed by `案件ID`. One Salesforce 案件ID can have multiple CAS 受発注ヘッダNo (confirmed correct by user, not a data bug).

**Bridge files** (found via Masaki, both mirrored under his personal OneDrive at `.../GBC戦略企画部_GBC設定実績・見込/QBR作成/`, also accessible via aicon@dentsu.co.jp):
- `Prep_CAS X SF Crosstable.xlsx` sheet `Crosstable`: columns `Year of 設定日`, `Month of 設定月`, `受発注ヘッダNo.`, `案件 ID/Item ID`, `得意先名`, `受発注ヘッダ件名`, `Check 1`, `Check 2`. 2,339 rows / 2,050 unique 受発注ヘッダNo — the ~216 apparent duplicates are almost all (210) the same 受発注ヘッダNo↔案件ID pair repeated across different 設定月/年 rows (harmless); only 6 keys genuinely map to 2 distinct 案件ID (negligible, one side is often literally "中止"/cancelled).
- `Prep_SalesforceAllRecord.xlsx` sheet `（設定突合用）SF案件リスト` (NOT the `_Original` variant): keyed by `案件 ID/Item ID`, has `GBC案件/Items: 案件名/Item title`, `部署名/Dept.`, `地域/Region`, `市場/Market`, `事業(業務)区分/Business category`, plus revenue columns already used elsewhere (`GBC設定売総/SETTEI Rev(JPY)`, `GBC貢献売総(計上)`, etc — not needed for this page).

**Import**: both loaded into Power BI via the established "Web API" connector pattern (URL with `:x:/r/` prefix and `?query` suffix stripped) from yamada_keita's OneDrive (same pattern as `GBC CAS見込_LATEST.xlsx` — this is normal for this project, several source files live on yamada_keita's OneDrive not just aicon's). Query names: `CAS_SF_Crosstable`, `SF案件リスト`.

**Gotcha — repeat of the CALCULATE/type bug family, this time in Power Query**: `受発注ヘッダNo`/`受発注ヘッダNo.` contains BOTH pure numbers (old bookings, e.g. `202201615338`) AND text-prefixed IDs (newer bookings, e.g. `H10-2601026335`). Power Query's **auto-generated initial "変更された型" step** (right after "昇格されたヘッダー数") guesses a single type for the whole column from the sample — it guessed number — so all the `H10-` text rows became `[Error]` immediately at that step. Adding a LATER explicit "convert to text" step does NOT fix this, because you can't convert an already-errored cell — the error just propagates through every subsequent step. **Fix**: edit the ORIGINAL auto "変更された型" step directly (select it in 適用されたステップ, edit the `Table.TransformColumnTypes(...)` formula in the formula bar, change that one column's type from `Int64.Type` to `type text`), not add a new step after it. Had to do this on BOTH `CAS_SF_Crosstable`'s `受発注ヘッダNo.` and `Raw YTD`'s own `受発注ヘッダNo` (the latter had the exact same latent bug, previously unnoticed since nothing had tried to type-check/merge on it before).

**Power Query steps built (all inside the `Raw YTD` query)**:
1. Fixed `受発注ヘッダNo` type to text at the source-level auto step (see above).
2. In `CAS_SF_Crosstable`: selected `受発注ヘッダNo.` + `案件 ID/Item ID` columns → 重複の削除 (dedupes on just that column pair via `Table.Distinct`, keeps all other columns from the first-seen row — user wanted to keep all original Crosstable columns for potential future reuse, so did NOT do "他の列の削除" first).
3. Merge 1: `Raw YTD` ⟵ `CAS_SF_Crosstable` on `受発注ヘッダNo` = `受発注ヘッダNo.`, 左外部, expand only `案件 ID/Item ID`.
4. Merge 2: `Raw YTD` ⟵ `SF案件リスト` on `案件 ID/Item ID` = `案件 ID/Item ID`, 左外部, expand `GBC案件/Items: 案件名/Item title`→`案件名`, `部署名/Dept.`→`部署名`, `地域/Region`→`地域`, `市場/Market`→`市場`, `事業(業務)区分/Business category`→`事業(業務)区分`.
5. Result: rows with no Salesforce match (mostly older 2022 deals) show blank for these 5 new columns — expected, not a bug.

**New measure** (in `Raw YTD` table, % of slicer-filtered total, works in a table visual without special TREATAS handling since everything is now native columns on one table):
```
売上総利益比率 = 
DIVIDE(
    SUM('Raw YTD'[売上総利益]),
    CALCULATE(SUM('Raw YTD'[売上総利益]), ALLSELECTED('Raw YTD'))
)
```
Formatted as Percentage, 1 decimal.

**Page `案件別内訳`**: 7 slicers bound directly to native `Raw YTD` columns (`計上年`, `計上四半期`, `部署名`, `クライアント名_調整後`, `地域`, `市場`, `事業(業務)区分` — no TREATAS needed, unlike the 貢献 pages' client/org slicers, because these are now all columns on the same physical table as the measure). Table visual: `案件名`, `クライアント名_調整後`, `部署名`, `地域`, `市場`, `事業(業務)区分`, `売上総利益`, `売上総利益比率`. Verified working: total row showed 1,629,611,626円 / 100.0%.

**Known follow-up (not yet done)**: Masaki wants to eventually discuss a more efficient long-term approach to bridging CAS↔Salesforce (currently a manual two-file crosstable prep) — revisit when he brings it up again.

## Direct Salesforce connector migration — started 2026-08-07

Salesforce integration was approved for Power BI (previously all manual Excel exports). Masaki installed Power BI Desktop on a **Windows 365 virtual PC** (Desktop doesn't run on macOS, so this is a new environment vs. the browser-only Service work above). Plan: replace the manual Excel-export sources one at a time with live "Salesforce レポート" connector queries in Desktop, starting with SF案件リスト.

**Source-of-truth manual found**: `/Users/d14461/Library/CloudStorage/OneDrive-電通/GBC戦略企画部_GBC設定実績・見込/QBR作成/(Manual) GBC QBR_Tableau20260401.docx` documents which Salesforce report backs each manually-updated Excel file (written for the older Tableau QBR process, but the report mapping applies equally to a live Power BI connector). Mapping:

| Excel file (manual process) | Salesforce report | Report ID / URL |
|---|---|---|
| `Prep_SalesforceAllRecord.xlsx` → sheet「(設定突合用）SF案件リスト」 | (設定突合用)SF案件リスト | `00OfP00000ARvMIUA1` — https://dgx.lightning.force.com/lightning/r/Report/00OfP00000ARvMIUA1/view?queryScope=userFolders |
| `GBC CAS見込_LATEST.xlsx` (CAS見込) | (QBR集計用)月別_設定利益（仕掛）_v2.1 | `00O7F00000Ayt1TUAR` |
| `GBC 貢献実績_FY22 TO DATE.xlsx` (貢献実績) | (QBR集計用)月別_貢献利益（実績）_v2.3 | `00OfP00000AlBNFUA3` |
| `GBC 貢献見込_LATEST.xlsx` (貢献見込) | (QBR集計用)月別_貢献利益（仕掛）_v2.2 | `00OGA00000CkNMN2A3` |
| `GBC 日系ターンアラウンド_APAC_Pitch-List...xlsx` | APAC Pitch - List All_v1.31 | `00OfP00000Cq0rRUAR` |

(Note: the unrelated `_CAS分析マニュアル20260603.docx` in `GBC設定実績・見込/CAS集計/` only covers the CAS実績 Raw YTD build pipeline — checked first, doesn't mention Salesforce reports, not useful for this connector work.)

**Progress so far (2026-08-07)**: Desktop successfully connected via データを取得→Salesforce レポート (OAuth sign-in worked with normal corporate SSO). Next: locate report ID `00OfP00000ARvMIUA1` in the Navigator, verify its columns match the existing `SF案件リスト` query's columns (部署名/地域/市場/事業(業務)区分/案件名 etc., see 案件別内訳 section above), then swap it in to replace the Excel-based query — downstream merges/bridge tables (`市場_Bridge`/`事業区分_Bridge`/`Raw YTD` merges) all key on `案件 ID/Item ID` and should keep working as long as column names are matched or renamed to match.

**Publishing plan agreed with Masaki**: don't overwrite the live production workspace directly — create a separate test workspace, add a colleague as viewer, publish there first to verify others can see it, then overwrite the production workspace report once confirmed. Also flagged for later: need to register credentials for the new Salesforce source under 設定→データソースの資格情報 (everything else currently registered under `yamada_keita_dentsu_co_jp`), test scheduled refresh (12:00/17:00 JST) after publishing, and check whether a separate Power BI アプリ needs a manual update step.

**Pivoted away from "Salesforce レポート" connector to "Salesforce オブジェクト" connector**: the Reports connector caps output at 2,000 rows (a hard limit of Salesforce's Reports & Dashboards REST API, inherited by the Power BI connector) — Masaki caught this risk before it caused silent data truncation in a financial report. The Objects connector uses standard REST/Bulk API pagination with no such cap, so all further work uses it instead. Leave "リレーションシップ列を含める" (Include Relationship Columns) **unchecked** when loading objects — the needed fields are native columns on the object itself, not via a lookup relationship, and the option only adds bloat.

**Object identified**: the report was built on custom object labeled **「GBC案件/Items」**, API name **`GBC__c`** ("GBCのPOC向けオブジェクト" per its description). Confirmed via Salesforce Setup → オブジェクトマネージャー → GBC案件/Items → 項目とリレーション (label↔API name are both shown there — the authoritative way to resolve this, since the Power BI object connector only exposes raw API names, not the friendly labels seen in reports).

**Confirmed field mapping** (report label → live object API name), verified directly against Object Manager, not guessed:
| Report column | Object field API name |
|---|---|
| 案件 ID/Item ID | `Id` (standard) |
| GBC案件/Items: 案件名/Item title | `Name` (standard) |
| 部署名/Dept. | `GBCorgChoice__c` |
| 地域/Region | `GBCArea__c` |
| 市場/Market | `GBCCountry__c` |
| 事業(業務)区分/Business category | `GBCJU__c` |

**Traps avoided**: two similarly-named decoy fields exist that are NOT the right 部署名 field — `GBCDepartmentName__c` (labeled 未使用_部署名(自動), i.e. "unused") and `GBCOrg__c` (labeled 非表示予定 部署名, i.e. "scheduled for hiding", and it's a reference/lookup type not a picklist). The correct live field is `GBCorgChoice__c`. Also note: `市場/Market`'s API name is still `GBCCountry__c` — the field was presumably relabeled from "Country" to "Market" at some point without renaming the underlying API name, so don't be misled by the name when scanning raw column lists.

**Consistency check, high confidence**: both `GBCCountry__c` (市場) and `GBCJU__c` (事業区分) are Salesforce **multi-select picklists** — this exactly matches the already-known behavior in the existing model (semicolon-delimited multi-values requiring 市場_Bridge/事業区分_Bridge, see below), confirming the mapping is correct.

**How this was actually resolved (process note for next time)**: Direct login automation to check this repeatedly popped visible Chrome windows and interrupted Masaki's other work, and repeatedly closing+relaunching a fresh browser process each time caused Salesforce's SAML relay to hang (each new process re-triggers a fresh SP-initiated SAML request that got stuck, seemingly unrelated to session cookie validity). **Fix Masaki suggested and which worked**: launch Chrome ONCE as a standalone background process with `--remote-debugging-port=9226 --user-data-dir=~/SalesforceExport/browser_profile`, then have each subsequent Playwright script `connect_over_cdp("http://localhost:9226")` to the SAME already-open browser instead of launching a new one each time — never close it between checks. Also: raw `document.querySelectorAll` misses Lightning's shadow-DOM content (nav links returned empty), but `document.body.innerText` and Playwright's own locator engine both pierce shadow DOM fine. The Analytics/sobjects REST API via same-origin `fetch()` from the page kept returning `INVALID_SESSION_ID` even while the UI itself rendered fine (session scoping mismatch, unresolved) — reading rendered page text (Object Manager UI) worked reliably where the REST API path didn't. See [[feedback_browser_automation_no_focus_steal]] and [[shared_bot_browser]] for the standing rules this produced.

**Caution — Claude misread the Power Query column preview once**: mid-verification, an off-by-one column misreading led to a wrong claim that 市場/部署名/事業区分 needed to be swapped (they didn't — the original Object-Manager-based mapping was correct all along, confirmed by re-checking row content like `市場=Indonesia;Malaysia;Philippines`, `部署名=BD2部`, `事業区分=メディア`). Masaki caught it by pointing at the live screen. Lesson: when reading a screenshot table with many similarly-styled narrow columns, verify column↔value alignment very carefully before asserting a data/label mismatch — trust the user's live-screen observation over a static re-read when they push back.

## Workspace migration & production cutover — 2026-08-07

Turned out the "production" workspace Masaki had been treating as live was actually the default **マイワークスペース** (My Workspace) — not a real shared team workspace. Since the dashboard hadn't been shown widely to the department yet, this was a good time to fix it: **renamed the just-tested verification workspace to become the real production workspace** (Power BI workspace URLs are keyed by internal GUID, not display name, so renaming doesn't break anything — no republish needed). The old My Workspace copy was kept (not deleted) with `_old` appended to its name, per Masaki's preference for keeping old versions around instead of deleting.

**Still open**: scheduled refresh (毎週月〜金, 12:00/17:00 JST — same pattern as configured in July, see スケジュールされた更新 section above) needs to be re-configured in this (renamed) workspace, since schedule config doesn't carry over from the old My Workspace automatically. Attempting to register Salesforce data-source credentials for this hit an OAuth error: `invalid_client` / `OAUTH_APPROVAL_ERROR_GENERIC` / `error_description=app+must+be+installed+into...` at `dgx.my.salesforce.com/setup/secur/RemoteAccessErrorPage.apexp`. Working theory: Power BI **Desktop**'s connection uses Masaki's own interactive session and already works fine, but Power BI **Service**'s server-to-server OAuth (needed for unattended scheduled refresh) goes through a separate Connected App that apparently isn't installed/approved for the `dgx` Salesforce org yet — a Salesforce-admin-side action, not fixable from the Power BI side. Masaki is following up with the Salesforce admin (2026-08-07); until resolved, the report works fine and can be kept current via manual Desktop refresh + republish.

## Extending Salesforce-object migration to CAS見込/貢献実績/貢献見込 — started 2026-08-07, paused mid-investigation

Masaki wants the other 3 manually-updated Excel sources (all confirmed Salesforce-sourced per the QBR manual, see table above) migrated to direct Salesforce Objects connector too: `CAS見込`, `貢献実績`, `貢献見込`.

**Found so far**: all 3 reports (`00O7F00000Ayt1TUAR`/`00OfP00000AlBNFUA3`/`00OGA00000CkNMN2A3`) share the exact same report type, shown right under the report name in edit mode: **「月別見込親案件が関連するGBC案件/Items」** — i.e. the primary/driving object for all 3 is labeled **「月別見込親案件」**, a child object with a lookup relationship up to `GBC__c` (confirmed by the `GBC案件/Items: ID` column appearing alongside many `月別見込親案件: <field>` columns in each report's field list). This object's own native fields include `年度`(Year), `月`(Month), `確度`(A/B/C confidence), plus revenue fields like `GBC設定売総/SETTEI Rev(JPY)` (CAS見込), `Group売総/Revenue (JPY)` + `月別集計用/GBC貢献売総(A/AB/ABC)/Att.Rev` + `月別集計用/GBC貢献売総(計上)` (貢献実績/貢献見込).

**RESOLVED 2026-08-09 — key architectural discovery**: 「月別見込親案件」is NOT a separate object at all. It's a **self-referencing lookup field on `GBC__c` itself**, API name **`SalesByYear_GBC_parent__c`** (confirmed via `GBC__c`'s own Fields & Relationships list: `月別見込親案件	SalesByYear_GBC_parent__c	参照関係(GBC案件/Items)`). So `GBC__c` holds BOTH the master 案件 records (already used for `SF案件リスト`) AND monthly forecast/actuals "child" records in the same table, linked to their parent via this lookup. `RecordTypeId` (standard field, confirmed present) is presumed to be how master-vs-monthly rows are distinguished — the actual Record Type name/value for "monthly" rows is still unconfirmed, check this when building the query (or just filter on `Year__c`/`Month__c` not being blank, which should isolate monthly rows equally well).

**How the Object Manager search automation finally worked** (useful for next time): plain `page.keyboard.type()` into `#globalQuickfind` silently did nothing (list stayed unfiltered) across many retries. Fix: set the value via the native property setter and manually dispatch `input`/`change` events — `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set.call(el, keyword)` then `el.dispatchEvent(new Event('input',{bubbles:true}))` — this got the LWC component to actually react. Also: guessing Lightning Setup URLs directly (`/lightning/setup/ReportTypes/home`, `/lightning/setup/CustomReportTypes/home`, `/00b` classic prefix) all 404'd — the real path to the Report Types list is only reachable by clicking through the left nav tree: 機能設定 → 分析 → レポート & ダッシュボード → レポートタイプ (each a `展開`/expand click). Object Manager's virtualized field list needs `page.mouse.move()` to position the cursor over the list before `page.mouse.wheel()` will actually scroll it — without the move-first step, wheel events were silently ignored and the list stayed on page 1 (47 items) no matter how many times it was "scrolled".

**Confirmed field mapping** (verified directly against `GBC__c`'s Fields & Relationships list, not guessed):

Native to the monthly/child row itself (no self-join needed):
| Report column | API name | Used by |
|---|---|---|
| 年度 | `Year__c` | all 3 |
| 月 | `Month__c` | all 3 |
| 確度 | `Accuracy__c` | all 3 |
| GBC設定売総/SETTEI Rev(JPY) | `GBCSettingSales__c` | CAS見込 (→見込売総) |
| GBC取設定/SETTEI TO(JPY) | `Instruction_Fixed_Amount__c` | CAS見込 |
| Group売総/Revenue (JPY) | `GBCGross__c` | 貢献実績/貢献見込 |
| 月別集計用/GBC貢献売総(A)/Att.Rev(A)(JPY) | `GBCMonthContributionGross__c` | 貢献実績/貢献見込 |
| 月別集計用/GBC貢献売総(AB)/Att.Rev(AB)(JPY) | `GBCMonthContributionGrossF__c` | 貢献実績/貢献見込 |
| 月別集計用/GBC貢献売総(計上)/Attrib. Rev(Rec.)(JPY) | `GBCMonthContributionGrossP__c` | 貢献実績のみ |
| GM承認/Auth. | `GBCGMauthorize__c` | 貢献実績/貢献見込 |
| 月別用重複確認 | `GBCMonthDupChk__c` | 貢献実績のみ |

Via parent (need self-join `GBC__c` ⟵ `GBC__c` on `SalesByYear_GBC_parent__c` = parent's `Id`) — same fields already used for `SF案件リスト`, plus a few new ones:
| Report column (`月別見込親案件: ...`) | API name |
|---|---|
| 案件 ID/Item ID | `Id` |
| 案件名/Item title | `Name` |
| 部署名/Dept. | `GBCorgChoice__c` |
| 地域/Region | `GBCArea__c` |
| 市場/Market | `GBCCountry__c` |
| 事業(業務)区分/Business category | `GBCJU__c` |
| クライアント/Client | `GBCClient__c` (参照関係→取引先/Account) |
| 商流/Business flow | `GBCCommercial_distribution__c` |
| フェーズ/Phase | `GBCPhase__c` |
| 活動項目/Activity Items | `GBCMiddleClass__c` |
| 関係会社/Partner companies | `GBCOutsideCom__c` |
| GBC貢献度/Attrib. Ratio | `GBCContributionPercent__c` |
| GM確認/Confirmed | `GBCGMConfirmed__c` |

**Note on `GBCMonthContributionGrossABC__c`**: this field exists too (labeled 月別集計用/GBC貢献売総(ABC)/Att.Rev(ABC)(JPY)) but the 貢献実績 M code references it with the `月別見込親案件:` prefix (unlike the sibling A/AB fields which are unprefixed) — worth double-checking during implementation whether that's intentional in the original report or just an inconsistency, and whether it should be pulled from the child row or the parent.

**Not yet done**: actually building this in Power Query (needs Desktop — self-join via `Table.NestedJoin(GBC__c, "SalesByYear_GBC_parent__c", GBC__c, "Id", ...)`, then filter to monthly-only rows, then split per-report field selection/renames matching the existing `CAS見込`/`貢献実績`/`貢献見込` queries' target schema). Paused here pending next Windows App session.

## CAS_SF_Crosstable date-type errors — 2026-08-07

After Desktop crashed once and the file was re-downloaded from the Service ("レポートとデータのコピー", not the live-connect option — required for continued Power Query editing), a fresh full refresh surfaced type-conversion errors in `CAS_SF_Crosstable`'s `Month of 設定月` column (some rows' manually-typed values don't parse as dates — expected given the manual's own description of this being a hand-typed/semi-automated column). **Fix**: this column (and `Year of 設定日`) turned out to be completely unused downstream — the merge into `Raw YTD` only pulls `案件 ID/Item ID` from this table — so the fix was simply changing their forced type from `type date` to `type text` in the `変更された列タイプ` step's `Table.TransformColumnTypes` call, removing the unnecessary/fragile conversion entirely rather than trying to clean the source data.

**Gotcha for editing a step's formula directly**: when replacing a step's formula via the formula bar, paste ONLY the expression (e.g. `Table.TransformColumnTypes(...)`), never the `stepName = ` prefix — pasting the full `変更された列タイプ = Table.TransformColumnTypes(...)` assignment form (as shown in the Advanced Editor's full listing) into a single step's formula bar throws `値 "..." を型 Table に変換できません` (cannot convert to type Table), since the step name binding is already handled by the UI.

**Also confirmed as a Power BI Desktop bug, not a data issue**: clicking "エラーの表示" (Show Errors) on the post-refresh "読み込み" summary dialog crashes Desktop with a `NullReferenceException` inside `KoLoadToReportDialog.OnShowErrorsClick` (confirmed via the full crash report Masaki shared, Product Version 2.153.910.0 / April 2026 release). **Don't use that button** — instead open Power Query Editor directly (データの変換) and click into the query with the error to find red "Error" cells in the preview grid directly.

**Session paused 2026-08-07 end of day** with the refresh seemingly stuck/slow after applying the type-text fix (not confirmed resolved yet — Masaki left Desktop running and shut down his Mac; Windows 365 is a persistent cloud PC so the Desktop session keeps running independently of the Mac's power state). **Next session**: check whether the refresh completed, confirm CAS_SF_Crosstable loads cleanly, then resume the CAS見込/貢献実績/貢献見込 object-API-name search above.

## 市場/事業区分 multi-value slicer fix — built 2026-07 (市場 done, 事業区分 not yet started)

Problem: `市場`/`事業(業務)区分` columns (from `SF案件リスト`, merged into `Raw YTD`) can hold multiple semicolon-delimited values per deal (e.g. `"China; Singapore"`). Masaki wanted the slicer to offer individual values (`China`, `Singapore` as separate selectable options) where selecting either one still matches/shows the combined-value deal — not a literal `"China; Singapore"` option in the slicer.

**Solution: many-to-many bridge table** (NOT modifying Raw YTD directly — splitting delimited values into multiple rows directly on Raw YTD would duplicate `売上総利益` and double-count it):
1. In Power Query, right-click `SF案件リスト` → 参照 (Reference) → new query, renamed `市場_Bridge`.
   - Note: "参照" only appears when right-clicking a query in the Power Query editor's own query list, reached via **「セマンティック モデルを開く」→「クエリ」→「データの変換」** (corrected 2026-07 twice after Masaki flagged the wrong label — first attempt "クエリの編集" was wrong, second attempt omitted the "クエリ" ribbon group step) — NOT in the Model view's table-card "..." menu, which has a different set of options (no "参照" there).
2. Keep only `案件 ID/Item ID` + `市場/Market` columns (他の列の削除).
3. Split `市場/Market` by delimiter `;` into **rows** (not columns) — 変換タブ →列の分割→区切り記号による分割→詳細設定オプションで分割先を「行」に設定. This multiplies rows (one per individual market value) while keeping `案件ID` repeated per split value.
4. Trim leading whitespace introduced by the split (e.g. `"China; Singapore"` → second value is `" Singapore"` with a leading space) — right-click the column header → 変換 → トリミング (this option is NOT in the ribbon's 変換 tab in this Power BI Service version, only via column header right-click).
5. Rename `市場/Market` → `市場`.
6. Relationship: `市場_Bridge[案件 ID/Item ID]` ↔ `Raw YTD[案件 ID/Item ID]`, built via リレーションシップの管理→新規 (not drag, more reliable). **カーディナリティ: 多対多 (*:*)**, **クロスフィルターの方向: 単一 ('市場_Bridge' によって 'Raw YTD' をフィルターする)** — this exact direction option is the second item when you open the クロスフィルターの方向 dropdown edit view (the three choices shown were: 単一 市場_Bridge→Raw YTD, 単一 Raw YTD→市場_Bridge, 双方向 — picked the first). A many-to-many relationship triggers a standard Power BI caution banner about non-unique join columns — this is expected/harmless here, not a real error, since both columns are intentionally non-unique.
   - Note: the compact "リレーションシップの管理" LIST view renders cardinality/direction as ambiguous arrow icons (`*——▶——*` etc.) that are hard to read reliably — always verify via "編集" to see the explicit dropdown text instead of trusting the list icons.
7. On the `案件別内訳` page, swapped the `市場` slicer's field from `Raw YTD[市場]` to `市場_Bridge[市場]`. Table visual itself still shows `Raw YTD[市場]` (still displays the combined `"China; Singapore"` text) — only the slicer's source field changed. **Verified working**: selecting "China" in the slicer correctly still shows deals whose combined market string includes China (e.g. `"China; Singapore"` rows appear).

`事業区分_Bridge` was built the same way and confirmed working (2026-07). Page renamed `設定実績_案件別内訳` (実績=actuals, since it's Raw YTD/CAS-sourced) to distinguish from the forecast counterpart below.

## 設定見込_案件別内訳 page — built 2026-07, mirrors the actuals page but simpler

`CAS見込` (the existing forecast table used for the `見込_合計` measure on 売上総利益 pages) is Salesforce-native and **already keyed by `案件ID`** (`月別見込親案件: 案件 ID/Item ID`) — no CAS×Salesforce crosstable bridge needed at all, unlike `Raw YTD`. It already had `クライアント名_調整後` merged in from earlier project work. Just needed:
1. Renamed 5 columns in `データの変換` (Power Query) for clarity: `月別見込親案件: 案件名/Item title`→`案件名`, `月別見込親案件: 部署名/Dept.`→`部署名`, `月別見込親案件: 地域/Region`→`地域`, `月別見込親案件: 市場/Market`→`市場`, `月別見込親案件: 事業(業務)区分/Business category`→`事業区分`.
2. Extended the EXISTING `市場_Bridge`/`事業区分_Bridge` tables (built for Raw YTD) with a second many-to-many relationship each, this time to `CAS見込[月別見込親案件: 案件 ID/Item ID]` — same cardinality/direction pattern (多対多, 単一 Bridge→CAS見込). One bridge table can and does serve both fact tables simultaneously; no duplication needed. (The relationship-creation preview showing `[null]` sample rows for CAS見込's ID column was just showing arbitrary sample rows, not an error — safe to ignore.)
3. New measure in `CAS見込` table:
```
見込売総比率 = 
DIVIDE(
    SUM('CAS見込'[見込売総]),
    CALCULATE(SUM('CAS見込'[見込売総]), ALLSELECTED('CAS見込'))
)
```
4. Duplicated `設定実績_案件別内訳` → renamed `設定見込_案件別内訳` → swapped every field from `Raw YTD`/`売上総利益`(比率) to the `CAS見込` equivalents (slicers: 年度/四半期/部署名/クライアント名_調整後/地域/`市場_Bridge[市場]`/`事業区分_Bridge[事業区分]`; table: 年度/月番号/案件名/クライアント名_調整後/確度/部署名/地域/市場/事業区分/見込売総/見込売総比率 — Masaki also added `確度` as a bonus column+slicer on this page, useful since it's forecast data). Verified: total row showed 161,629,909円 / 100.0%.

**UI label correction (2026-07, happened twice)**: the correct click-path to reach Power Query is **「セマンティック モデルを開く」→「クエリ」→「データの変換」** — not "クエリの編集" (first wrong guess) and not skipping the "クエリ" ribbon-group step (second wrong guess).

## 案件別内訳: 月をまたぐ案件の集約 + 市場/事業区分Bridgeの絞り込み漏れ修正 — 2026-07

**月範囲表示**: Masaki wanted rows collapsed to one-per-deal (not one-per-month) with the 月 column showing a compact range like "2〜4" when a deal spans multiple months. Removed the plain `月番号` column from the table and replaced with a measure (in `Raw YTD`) that computes MIN/MAX month across whatever rows are grouped by the table's other columns:
```
月範囲表示 = 
VAR MinMonth = MIN('Raw YTD'[月番号])
VAR MaxMonth = MAX('Raw YTD'[月番号])
RETURN
IF(MinMonth = MaxMonth, FORMAT(MinMonth, "0"), FORMAT(MinMonth, "0") & "〜" & FORMAT(MaxMonth, "0"))
```
Works because a table visual's measures are evaluated in the row context implied by whatever OTHER columns are in the table (案件名/クライアント名/部署名/地域/市場/事業区分/年度) — removing 月 from that grouping set is what causes same-deal-different-month rows to collapse into one, with this measure filling in the resulting range.

**Bug found via CAS×Salesforce crosstable investigation**: added 10 missing 受発注ヘッダNo entries directly into `Prep_CAS X SF Crosstable.xlsx` (rows 2341-2350, via direct openpyxl file edit since Power Query has no easy "add a row" UI) for 2026 deals that had `[空白]` 案件名 due to missing crosstable coverage, leaving 案件ID blank/highlighted yellow where unknown. **Masaki (or a colleague with edit access) later filled in several of those yellow blanks with real values** (e.g. Hello Kitty展 → `a1h7F000007KWMS`, matching the existing "サンリオキティ展" Salesforce record) or the literal text `SF登録無し` for genuinely-unregistered ones — this was NOT a bug, just manual follow-up work on the file, but caused confusion mid-session before being traced via `Table.SelectRows` filtering in Power Query.

**Root cause of "市場/事業区分 スライサーを絞ってもテーブルの絞り込みが漏れる" bug**: `市場_Bridge`/`事業区分_Bridge` are many-to-many related to `Raw YTD` via `案件 ID/Item ID`. Any `Raw YTD` row whose `案件ID` is blank (i.e. no confirmed Salesforce match — a substantial and growing portion of rows) has **no relationship path to the bridge table at all**, so it is invisible to the relationship's cross-filtering and **always displays regardless of which market/business-category is selected** in the slicer — this is standard, expected DAX many-to-many behavior (unmatched rows bypass the filter, they aren't excluded by it), not a misconfiguration.

**Fix**: added two measures on `Raw YTD` that check `CONTAINSSTRING` directly against Raw YTD's own (non-bridge) `市場`/`事業(業務)区分` text columns, and applied them as **visual-level advanced filters** (`= 1`) on the table:
```
市場一致 = 
VAR CurrentMarket = SELECTEDVALUE('Raw YTD'[市場])
VAR SelectedMarkets = VALUES('市場_Bridge'[市場])
RETURN
IF(
    NOT ISFILTERED('市場_Bridge'[市場]), 1,
    IF(ISBLANK(CurrentMarket), 0,
        IF(COUNTROWS(FILTER(SelectedMarkets, CONTAINSSTRING(CurrentMarket, [市場]))) > 0, 1, 0)
    )
)
```
(mirror `事業区分一致` using `事業区分_Bridge`/`事業(業務)区分`). This correctly excludes blank-案件ID rows once a specific market/category is selected (their own `市場`/`事業区分` text is also blank, so `ISBLANK` catches them), fixing the leak.

**UI gotcha**: a **boolean** (`TRUE()`/`FALSE()`) measure's visual-level filter card would not expand at all when clicked (no dropdown, no filter-type options, even after removing/re-adding the field and toggling its lock icon) — this may be a Power BI Service rendering bug specific to boolean measures used as advanced filters. **Fix: use integer 1/0 instead of TRUE()/FALSE()** — the filter card then expanded normally under 詳細フィルター (次の値に等しい → 1). Worth remembering for any future measure-based visual filter in this project.

## All 4 案件別内訳 detail pages complete (2026-07)

`設定実績_案件別内訳` (Raw YTD/売上総利益), `設定見込_案件別内訳` (CAS見込/見込売総), `貢献実績_案件別内訳` (貢献実績/貢献売総_計上), `貢献見込_案件別内訳` (貢献見込/貢献売総) — all built via page duplication + field-swap from the first one, reusing the same recipe end to end: 7 slicers (年度/四半期/部署名/クライアント名/(確度 on 見込 pages)/地域/市場_Bridge/事業区分_Bridge) → table with 月範囲表示 measure + per-visual-renamed columns (案件名/部署名/地域/市場/事業区分, long Salesforce-prefixed names left untouched at the model level, only display-renamed per-visual, to avoid breaking the existing 計上組織名 TREATAS measures on 貢献実績/貢献見込 which reference the long column names) → 比率 measure (% of ALLSELECTED) → `市場一致`/`事業区分一致`-pattern measures as `=1` advanced filters → ranking bar chart (横棒グラフ, or 積み上げ横棒グラフ with 凡例=確度 for the 見込 pages), sorted descending by the value measure, top 20.

Full measure roster added this arc: `月範囲表示`/`見込月範囲表示`/`貢献実績月範囲表示`/`貢献見込月範囲表示`, `売上総利益比率`/`見込売総比率`/`貢献実績比率`/`貢献見込比率`, `市場一致`/`事業区分一致`/`見込市場一致`/`見込事業区分一致`/`貢献実績市場一致`/`貢献実績事業区分一致`/`貢献見込市場一致`/`貢献見込事業区分一致` (12 total, all integer 1/0 pattern). `市場_Bridge`/`事業区分_Bridge` each now carry 4 active many-to-many relationships (one per fact table: Raw YTD, CAS見込, 貢献実績, 貢献見込), all single-direction bridge→fact.

## 地域/市場/事業区分スライサーをトレンドページに拡張 — 開始 2026-07-15

Masaki wants the 地域/市場/事業区分 slicers (already working on the 4 案件別内訳 detail tables) added to the 6 original aggregate trend pages too (`設定_年別推移`, `設定_Q別前年比`, `設定_月別_前年比`, `貢献_年別推移`, `貢献_Q別推移`, `貢献_月別推移`). Explicitly scoped down to start with just `設定_年別推移`, confirmed working, now moving through the rest one at a time.

**Key design shift from the 案件別内訳 pattern**: on the detail TABLE pages, market/business filtering was done via a visual-level advanced filter (`市場一致`=1). For these AGGREGATE pages (KPI cards, charts with no row-level grouping), that trick doesn't apply — instead, the fix is embedding `CONTAINSSTRING`-based `FILTER(ALL(...), ...)` blocks directly as extra arguments to `CALCULATE` inside the underlying `_合計`-style measures. This is a **cleaner alternative to the nested-IF-branching TREATAS pattern** used earlier for 計上組織名/クライアント名 filtering: because CALCULATE's multiple filter-table arguments are ANDed together automatically, adding N independent dimension filters this way does NOT require enumerating 2^N branches — each dimension just gets its own `FILTER(ALL(col), NOT ISFILTERED(bridge) || CONTAINSSTRING(...) )` block appended to the same CALCULATE call. Template (applied to `Raw YTD`'s `売上金額_合計`/`原価金額_合計`/`売上総利益_合計` and `CAS見込`'s `見込_合計`):
```
FILTER(
    ALL('<FactTable>'[<market column>]),
    NOT ISFILTERED('市場_Bridge'[市場]) ||
    COUNTROWS(FILTER(VALUES('市場_Bridge'[市場]), CONTAINSSTRING('<FactTable>'[<market column>], [市場]))) > 0
),
```
(same shape for 事業区分_Bridge/事業区分 and 地域_Bridge/地域). Add one such block per dimension, per fact table, inside every existing CALCULATE call in the measure (including both branches of any existing client-filter IF).

**Column name gotcha**: `Raw YTD`'s business-category column is still named `事業(業務)区分` (the Power Query rename to `事業区分` was only ever applied to `CAS見込`, not `Raw YTD`) — always reference `'Raw YTD'[事業(業務)区分]` not `'Raw YTD'[事業区分]` (the `事業区分_Bridge` table's own column is named plain `事業区分`, that part is unaffected).

**地域_Bridge table**: built via the identical bridge-table recipe as `市場_Bridge`/`事業区分_Bridge` (参照 `SF案件リスト` → keep `案件 ID/Item ID`+`地域/Region` → 列の分割→区切り記号(`;`)→行 → トリミング → rename to `地域`), then related many-to-many (単一方向 Bridge→Fact) to `Raw YTD` and `CAS見込` (extend to `貢献実績`/`貢献見込` when those pages' turn comes, mirroring how 市場_Bridge/事業区分_Bridge already reach all 4 fact tables).

**設定_年別推移 — done.** KPI cards were repointed from implicit column aggregation (`SUM('Raw YTD'[売上金額])` via drag-and-drop, displayed as "売上金額 の合計") to the explicit `売上金額_合計`/`原価金額_合計`/`売上総利益_合計` measures (which already existed in the model for other pages, just weren't used here) — this was a prerequisite since implicit aggregations can't carry the new CONTAINSSTRING filter logic. Chart's `積み上げ値` measure references `指定指標_年別` (実績 branch, itself a `SWITCH` over `指標選択[指標]` returning the 3 `_合計` measures — inherits the fix automatically, no direct edit needed) and `見込_合計` (見込 branch, edited directly). 3 slicers added: `地域_Bridge[地域]`, `市場_Bridge[市場]`, `事業区分_Bridge[事業区分]`.

**設定_Q別前年比 — in progress.** Discovered page structure (front chart = 指定年/指定年の前年 columns + 売上総利益率/売上総利益率_前年 lines; back overlaid chart = `見込_合計` stacked by 確度, same overlay-transparency technique as elsewhere in this project). Measure chain: `指定年_動的`/`指定年の前年_動的` are `SWITCH` wrappers over `指標選択[指標]` returning `売上総利益_合計`/`売上金額_合計`/`原価金額_合計` (現在) or their `_前年` counterparts; `売上総利益率_前年 = CALCULATE([売上総利益率], FILTER(ALL('Raw YTD'[計上年]), 'Raw YTD'[計上年] = SELECTEDVALUE('Raw YTD'[計上年]) - 1))` — a "wrap the already-fixed base measure in a year-shift CALCULATE" pattern. If `売上総利益_前年`/`売上金額_前年`/`原価金額_前年` follow the same wrap-the-_合計-measure convention (strongly suggested by the 売上総利益率_前年 example, not yet 100% confirmed), this whole page inherits the fix with **zero additional DAX changes** — just add the 3 slicers. Verify by testing a market/region selection against the 前年 bar before assuming done.

**Important recurring friction point (2026-07-15, explicit user feedback)**: this project is large enough that Masaki expects Claude to retain exactly which measures/columns/patterns were already established, across compactions and across chats, without re-asking to confirm structure Claude itself learned or created earlier — reinforces [[feedback_powerbi_track_own_instructions]]. When a compaction summary is thin on a specific page's measure roster, catching up by reading this memory file first (before asking the user) is the expected move; only ask when the specific measure genuinely predates any session Claude was part of.

**All 6 trend pages complete (2026-07-15)**: `設定_年別推移`/`設定_Q別前年比`/`設定_月別_前年比` needed the CONTAINSSTRING-in-CALCULATE fix described above (applied once to the shared `_合計`/`見込_合計` measures, all 3 pages inherited it for free since they reuse the same underlying measures with only the axis table swapped). `貢献_年別推移`/`貢献_Q別推移`/`貢献_月別推移` turned out to need **zero measure changes** — 市場/事業区分 slicers worked immediately once `市場_Bridge`/`事業区分_Bridge`'s pre-existing relationships to `貢献実績`/`貢献見込` (built back in the 案件別内訳 phase) were in place, because unlike `Raw YTD` (CAS-native, many rows have no confirmed Salesforce/案件ID match, causing the many-to-many "blank ID leak" that CONTAINSSTRING was built to patch), `貢献実績`/`貢献見込` are Salesforce-native tables where every row already carries a real 案件ID — so plain relationship-based filter propagation from the bridge tables just works with no leak to patch. Only gap was `地域_Bridge` itself, which (being newly built this session) initially only had relationships to `Raw YTD`/`CAS見込` — adding the same many-to-many relationship to `貢献実績[月別見込親案件: 案件 ID/Item ID]` and `貢献見込[月別見込親案件: 案件 ID/Item ID]` (単一方向 Bridge→Fact, mirroring 市場_Bridge/事業区分_Bridge) fixed it immediately. **Lesson for any future bridge table**: CAS-native fact tables (Raw YTD) need the CONTAINSSTRING measure patch; Salesforce-native fact tables (CAS見込, 貢献実績, 貢献見込) do not — relationship propagation alone suffices for those.

## スケジュールされた更新 — 設定・確認完了 (2026-07-15)

Checked the semantic model's 設定 → データ ソースの資格情報 / 最新の情報に更新 sections for the first time this project. Two findings:

1. **All data source credentials are registered under `yamada_keita_dentsu_co_jp`**, not `aicon@dentsu.co.jp` — even though `Raw YTD`/CAS実績 files physically live in aicon's shared OneDrive per the "Data sources" section above. This means Power BI's Web-connector auth token is yamada_keita's personal session (presumably he has delegated/shared access into aicon's folder), not a dedicated aicon login. Not currently broken, but **this is the account whose access/token expiry could someday break every scheduled refresh** — worth checking here first if refresh ever starts failing.
2. **スケジュールされた更新 was OFF** — had never been configured; the dashboard had only ever been refreshed manually/on-demand up to this point, despite the multi-week migration effort already invested.

**Now configured**: timezone changed UTC → (UTC+09:00) 大阪、札幌、東京; schedule enabled with 頻度=毎週, days=月〜金 only (土日除く, per Masaki: "元のデータは今後毎日更新したいのです...ただし、土日は更新する必要がありません"), two daily refresh times **12:00 and 17:00 JST** (added via "別の時刻を追加" — confirmed multiple times/day is supported, well within the Pro-license 8/day cap). Verified via manual "今すぐ更新" → completed with no errors.

## 設定_Q別前年比/月別_前年比: 前年バーが将来四半期・月で消える問題 — 解決 (2026-07-16)

Masaki reported that on `設定_Q別前年比`/`設定_月別_前年比`, the 前年(prior-year) bars/line disappeared for quarters/months where the CURRENT year has no actual data yet (only forecast) — e.g. Q3/Q4, or 7月以降. `貢献_Q別推移`/`貢献_月別推移` didn't have this problem. Root-caused and fixed in two layers:

**Layer 1 — chart architecture.** `設定`'s front chart had `指定年`(今年) and `指定年の前年`(前年) as two column series in ONE combined chart visual, unlike `貢献`'s design which uses **two fully separate overlaid visuals** (前年専用グラフ / 今年専用グラフ). When 今年 has no data for a category, sharing one visual with 前年 apparently suppresses that category's rendering entirely (Power BI clustered-column quirk). Fix: split into 2 separate visuals exactly like 貢献's pattern:
- 前年専用グラフ: only `指定年の前年_動的` (columns) + `売上総利益率_前年` (line)
- 今年専用グラフ: `積み上げ値` (already-existing measure, same "実績 branch = SWITCH per 指標, forecast branches = CAS見込 by 確度" pattern as `貢献積み上げ値`) as columns with legend `凡例_実績見込[項目]`, + `売上総利益率` (line) — this **replaces** the old separate confidence-tier-only back chart entirely (now redundant, delete it), since `積み上げ値` already merges 実績+A/B/C into one unified stacked series.
- Both positioned to exactly overlap (全般→プロパティ), frontmost visual's background transparent — same overlay technique used throughout this project.

**Layer 2 — the classic "SELECTEDVALUE collapses to blank" bug, new instance.** Even after splitting into separate visuals, 前年 still showed blank for Q3/Q4/7月+. Cause: `売上総利益_前年`/`売上総利益率_前年`/`売上金額_前年`/`原価金額_前年` computed "which year is prior" via `SELECTEDVALUE('Raw YTD'[計上年]) - 1` evaluated INSIDE a filter context already narrowed by the visual's Quarter/月 axis. When the CURRENTLY SELECTED year (e.g. 2026) has zero Raw YTD rows for that specific quarter/month (because only forecast/CAS見込 data exists there, no actual yet), `Raw YTD[計上年]`'s visible distinct-value set under that compound filter becomes empty, so `SELECTEDVALUE` returns BLANK instead of 2026 — breaking the whole "prior year" calculation for exactly the categories where current-year data doesn't exist yet. This is the **exact same root cause class** as the original `見込_合計` SelectedYear bug from early in the project (see 見込機能 section above) — a shared dimension (四半期/月) narrowing Raw YTD to zero rows collapses SELECTEDVALUE. Fix: wrap the year-lookup in a VAR using `CALCULATE(SELECTEDVALUE('Raw YTD'[計上年]), ALL('四半期'), ALL('月'))` before using it, exactly like `見込_合計`'s `SelectedYear` VAR does — applied to all 4 `_前年` measures (`売上総利益_前年`, `売上総利益率_前年`, `売上金額_前年`, `原価金額_前年`, all in `Raw YTD`). **General lesson: any measure computing "which year/period is currently selected" via bare `SELECTEDVALUE('Raw YTD'[計上年])` is at risk of this bug whenever it can be evaluated inside a category-axis context (Quarter/月) that might have zero current-year rows — always wrap with `ALL('四半期'), ALL('月')` first.**

**Layer 3 — axis-max measures missing the 前年 branch.** After layers 1-2, 前年 rendered correctly but got visually clipped (e.g. 12月's 102M rendered the same height as 10月's 83M) because `グラフ軸_最大値_月`/`グラフ軸_最大値`(Q別版) only took `MAX(今年実績, 見込)` — **前年 was never included in the axis-max calculation at all**, a pre-existing gap unrelated to layers 1-2, only exposed once 前年 started rendering its true (sometimes larger) values. Fixed by nesting a third `MAX(...)` branch for `指定年の前年_動的`/`指定年の前年_動的`(Q別) into both measures (DAX `MAX()` is 2-arg only, so `MAX(MAX(a,b),c)`). `利益率軸_最大値_月`/`利益率軸_最大値`(rate-axis versions) already included both 今年/前年 branches from the start, no fix needed there. **Lesson: any axis-max MAXX-based measure must explicitly include every series actually plotted on that axis — check it whenever a new series (like 前年) is added or its visibility changes.**

Not yet done: same 3-layer check for `貢献`'s axis-max measures (they were less obviously broken since 貢献's 前年 already always rendered, but worth spot-checking `貢献軸_最大値_月`/`_Q` for the same missing-branch gap next time that area is touched).

## 新ページ「実績+見込 vs 予算」— 構築中、未完了 (2026-07-16〜)

New page (currently named `ページ1`, not yet renamed) mirroring a mockup Masaki shared: KPI summary block + horizontal stacked bar (実績/A/B/C vs 予算 reference line) + cumulative line chart (予算_累計 vs 実績見込_累計) + monthly combo chart (積み上げ値 columns + 予算_月次 line). Design decision (explicit, 2026-07-16): 実績/見込A/見込B/見込Cは統合せず、それぞれ個別の「含む/含まない」を`凡例_実績見込[項目]`スライサーで切り替えられるようにする(既存の`積み上げ値`メジャーが元々この分岐設計だったため、これをそのまま再利用する形で実現).

**Data source found and imported**: `GBC CAS実績+見込_COMBINED.xlsx` (yamada_keita's OneDrive, **not** aicon's — a different file than the similarly-named `GBC CAS予算+期初見込_COMBINED.xlsx` which was a red herring/wrong file initially guessed), sheet **`Budget`** only (`Actual`/`Forecast` sheets skipped, duplicate of Raw YTD/CAS見込). Columns: DATEVALUE(月次), クライアント名/件名/計上組織名(全て空欄), 確度="Budget"固定, 売上総利益(=予算額). 2026年のみ12行、他は空白行(除外済み).

**Import gotcha (new, worth remembering)**: the Get Data wizard's "Web" connector (Japanese label "Webページ") required a Gateway and failed; "Web API" connector (picked per the error's own suggestion) ALSO failed with a different "組織アカウントを使用して接続を作成できません" error when given a SharePoint **share-link** URL (`:x:/r/...` format). The actually-working method (discovered by inspecting `CAS見込`'s own "ソース" step in 適用されたステップ): create a **空のクエリ (Blank Query)**, and type the M formula directly into the formula bar:
```
= Excel.Workbook(Web.Contents("https://esq365-my.sharepoint.com/personal/yamada_keita_dentsu_co_jp/Documents/<url-encoded path, NO :x:/r/ prefix, NO ?d=...&csf=... query string>.xlsx"), null, true)
```
i.e. strip the share-link down to a **direct SharePoint Documents-library path** (remove `:x:/r/` entirely, not just the query string) — this is the actual established pattern this whole project has used for every yamada_keita-hosted file, contradicting an earlier (wrong) memory note that called it "Web API connector pattern" without pinning down the exact mechanism. **Going forward: for any new yamada_keita-hosted file import, go straight to 空のクエリ + this `Excel.Workbook(Web.Contents(...), null, true)` formula — don't attempt the Get Data wizard's Web/Web API connector picker at all, it doesn't work for this tenant's SharePoint setup.**

**Table `CAS予算`** (Power Query): filtered to non-null DATEVALUE rows (12 rows, 2026 only), added calculated columns `計上年 = Date.Year([DATEVALUE])`, `月番号 = Date.Month([DATEVALUE])`. Relationship: `月[月番号]` (1) → `CAS予算[月番号]` (多), 一対多, single-direction 月→CAS予算 (standard, not a many-to-many bridge).

**Measures created so far** (8 total):
- `見込A_合計`, `見込B_合計`, `見込C_合計` (`CAS見込` table) — each `CALCULATE(SUM('CAS見込'[見込売総]), <SelectedYear via ALL('四半期')/ALL('月') pattern>, 'CAS見込'[確度] = "A"/"B"/"C")`.
- `予算_月次` (`CAS予算` table) — monthly budget respecting the (indirectly-linked) 計上年 slicer via the same SelectedYear-VAR pattern (CAS予算 has no relationship to Raw YTD/計上年 slicer directly, so every CAS予算 measure must independently re-derive SelectedYear).
- `予算_年間合計` (`CAS予算` table) — full-year total, `ALL('月')`-cleared version of the above.
- `予算_累計` (`CAS予算` table) — cumulative Jan→current-month sum, via `CurrentMonth = MAX('月'[月番号])` + `月番号 <= CurrentMonth` filter.
- `年度着地見込` (`Raw YTD` table) — `SUMX(VALUES('凡例_実績見込'[項目]), [積み上げ値])`, elegantly reuses the existing `積み上げ値` measure's per-item branching by iterating over whatever legend rows are currently visible/selected.
- `達成度_見込` (`Raw YTD` table) — `DIVIDE([年度着地見込], [予算_年間合計])`.
- `実績見込_累計` (`Raw YTD` table) — cumulative (Jan→current month) version combining actual (`[売上総利益_合計]` wrapped in month≤current filter, only included if "実績" is in the current 凡例_実績見込 selection) + forecast (looped over selected non-実績 items via SUMX, each CALCULATE'd against `CAS見込[確度]`, also month≤current filtered). Full DAX logged in transcript if needed again — this is the most complex measure of the batch, re-derive from the pattern (SelectedYear VAR + CurrentMonth VAR + conditional actual-inclusion + SUMX over selected forecast tiers) rather than guessing if it needs revisiting.

**Page created, named `予算達成トラッキング`** (renamed from `ページ1`). Progress as of 2026-07-20 session end:

1. ✅ `KPI項目` table + `KPI値` measure — built, top-left table visual working, showing correct values.
2. 🔶 Top-right 積み上げ横棒グラフ — built (値=`積み上げ値`, 凡例=`凡例_実績見込[項目]`), showing 実績/A/B/C/**X** all as segments (凡例_実績見込 apparently has an X row too, not just 実績/A/B/C as assumed — not yet flagged as a problem by Masaki, revisit if he wants X excluded). **Blocker found: this Power BI Service version's 積み上げ横棒グラフ format pane has NO 分析/定数線 (constant line) section at all** (confirmed by scrolling the full ビジュアル-tab section list: Y軸/X軸/凡例/スモールマルチプル/グリッド線/ズームスライダー/リボン/データラベル/合計ラベル/プロットエリアの背景, nothing analytics-related below that). This is a new UI limitation discovered this session — **定数線 is not available for this visual type in this tenant/version, don't suggest it again for bar charts.**
   - **Planned workaround (not yet built)**: reuse this project's established "2-visual overlay" technique (same one used for 前年専用/今年専用 chart pairs). Duplicate the stacked bar chart; on the copy, remove 凡例, set 値=`予算_年間合計` only (single plain bar, light gray color), position it to exactly overlap the original (全般→プロパティ X/Y/幅/高さ matched), send it BEHIND the stacked chart. This renders 予算 as a static-length gray backdrop bar showing the target, with the colored 実績/見込 stack drawn in front — functionally equivalent to a reference line for this "progress vs target" use case.
3. ⬜ Bottom-left cumulative line chart (`予算_累計` / `実績見込_累計`, X軸=`月[月ラベル]`) — not yet built.
4. ⬜ Bottom-right monthly combo chart (`積み上げ値` columns w/ `凡例_実績見込[項目]` legend + `予算_月次` line) — not yet built.
5. ⬜ Page-level slicers — **critical fix applied this session**: 見込A/B/C and 示達予算/達成度 initially showed BLANK (and 実績 showed an inflated all-years total, 1.4bn instead of the expected ~197M) because this new page was missing the `計上年`(→2026) and `指標選択[指標]`(→売上総利益) slicers that every other page has. Every `_合計`/`SelectedYear`-pattern measure in this project silently depends on a page-level 計上年 slicer being present (SELECTEDVALUE returns BLANK across multiple years without it), and `見込_合計`/`積み上げ値`'s A/B/C branches depend on `指標選択[指標]`="売上総利益" being pinned. **Both slicers were added and confirmed fixed the blank values** — but the `凡例_実績見込[項目]` slicer (for the actual include/exclude-per-item control that's the whole point of this page's design) has **not yet been added**.
6. ⬜ Apply the 定数線-replacement overlay technique from step 2.

**Next session starting point**: build the 予算_年間合計 background-bar overlay (step 2's workaround), then tackle steps 3/4/5 (still fully unbuilt).

## 新ページ「案件別ランキング(実績+見込ブレンド)」— 長時間デバッグの末に解決 (2026-07-24)

New page built: left panel = prior-year full-year actuals ranking (`前年実績値` measure, `Raw YTD`, TREATAS against a new `案件_Dim` table), right panel = current-year ranking blending actual-through-selected-month + confidence-tier forecast-from-selected-month, per deal, as a stacked bar (`案件別ブレンド値`/`案件別ブレンド値_合計`, `Raw YTD`).

**`案件_Dim` table**: a shared "案件" dimension (案件ID/案件名/クライアント名/部署名, built via 参照 from `SF案件リスト` + 重複の削除 on ID) needed so ONE table/chart visual could switch between showing Raw YTD-driven vs 貢献実績-driven rankings via the `指標` slicer. **Could not get a physical relationship to Raw YTD/CAS見込/貢献実績/貢献見込 working** — hit the exact same "列 ''(テーブル '')には重複する値...が含まれています" garbled-blank-quotes Power BI Service platform bug documented earlier in this file for `クライアント_Dim` (confirmed: not real duplicates, survived browser reload + full table recreation). **Resolved by abandoning relationships entirely and using TREATAS** in every measure instead (`TREATAS(VALUES('案件_Dim'[案件 ID/Item ID]), '<fact table>'[<its own ID column>])` inside CALCULATE) — this is now the established go-to move whenever a new dimension table hits this specific error signature, don't waste time re-attempting the relationship UI.

**Top N filter performance**: applying a 上位N filter (by a TREATAS-heavy measure) against `案件_Dim`'s ~2900 candidate rows was too slow to render reliably (silently blank, not an error) — even after waiting. Removed the Top N filter entirely and just used column-header/visual sort instead (for a stacked-legend chart, had to add the `_合計` measure to the **ツールヒント** field well first, since "条件の並び替え" only offers fields actually bound to the visual — sorting by the per-segment `案件別ブレンド値` instead of the deal's total gave visibly wrong order for a stacked chart). **Lesson: avoid 上位N filters driven by TREATAS-against-thousands-of-rows measures in this Power BI Service tier — use plain visual sort instead.**

**Major bug hunt — DAX calculated-column month filtering silently returns blank when combined with certain other filters.** Symptom: `案件別ブレンド値`'s forecast branch (CAS見込/貢献見込, confidence tiers A/B/C) always evaluated to blank/zero, regardless of which month was selected — even though the equivalent "actual" branch (Raw YTD/貢献実績) worked fine, and CAS見込's own aggregate totals (`見込A_合計` etc.) were independently confirmed correct. Root-caused via a long bisection (isolating: card-level aggregate math worked fine → COUNTROWS('CAS見込') returned BLANK specifically when the page's single-value 月 slicer selected one specific month → discovered CAS見込 has genuine blank/trailing rows needing the same "filter out null 年度 rows" fix Raw YTD got earlier → still broken after that fix → discovered CAS見込 forecast data legitimately only exists for months 7-12, which was a red herring, not the bug → `ALL('CAS見込')` alone correctly cleared the ambient month-slicer restriction and returned the right aggregate, but `ALL('CAS見込'[月番号])` (clearing just that one column) or any `FILTER` condition referencing `月番号` (or even `MONTH('CAS見込'[DATEVALUE])` computed fresh, bypassing the column) silently returned blank when combined with `ALL('CAS見込')` in the same CALCULATE → **final cause: the DAX calculated column `月番号` (`= MONTH('CAS見込'[DATEVALUE])`), despite its Model-view properties panel correctly showing データ型=整数, behaves as if type-incompatible in this specific comparison scenario.** Confirmed via a parallel test: adding an equivalent column via Power Query (`月番号2 = Date.Month([DATEVALUE])`, a **Power-Query-native column**, not a DAX calculated column) initially also failed — but with a *visible, explicit* error this time ("DAX 比較操作は、型 Text の値と型 Integer の値の比較はサポートしていません"), because the new custom column defaulted to Power Query's untyped "Any" (shown as the "ABC 123" icon) rather than being explicitly converted. **Fix: right-click the new Power Query column → 型の変更 → 整数, explicitly.** Once done, filtering by `月番号2` instead of the original DAX-calculated `月番号` worked immediately and correctly.

**General lesson, worth remembering project-wide**: when a DAX calculated column is used inside a `FILTER(ALL(col), ...)` or similar override pattern and mysteriously produces silent blanks (not an error) despite the column's declared type looking correct, don't keep trusting the DAX column — **switch to an equivalent Power-Query-native column instead** (`Date.Month(...)`/`Date.Year(...)` etc. in M, with an explicit 型の変更 step, never left as Any/"ABC 123" type) as the fix, rather than continuing to debug the DAX calculated column itself. This is a different, newly-discovered failure mode from the earlier-documented "duplicate value" relationship-cardinality bug and the "IF can't return a table" bug — a third distinct class of Power-BI-Service-specific gotcha for this project. If `貢献見込[月番号]`/other tables' DAX-calculated 月番号-style columns are used in future ALL()-override filtering (not just as ALLSELECTED('月') axis grouping, which seems unaffected), proactively rebuild them as Power Query native columns first rather than waiting for the same symptom to reappear.

## 新ページ「案件別ランキング(実績+見込ブレンド)」— 完成状態まとめ (2026-07-24時点)

**現状ページ名は`ページ1`のまま(未リネーム)** — 次回セッション最初の小タスクとして、分かりやすい名前(例: `案件別ランキング`)に変更することを推奨。デザイン意図: 左パネル=前年の確定実績ランキング、右パネル=当年の「選択月まで実績＋それ以降は確度別見込」をブレンドした案件別積み上げランキング。指標(売上総利益/貢献売総)をワンクリックで切り替えられ、設定(CAS)側・貢献側の両方に対応。

### ページ構成
- **スライサー(9個、すべてページ上部)**: `指標選択[指標]`(売上総利益/売上/原価/貢献売総の4択、後述の理由で貢献売総を追加済み)、`Raw YTD[計上年]`、`月[月ラベル]`(単一選択、これが「実績と見込の境目の月」を決める)、`凡例_実績見込[項目]`(実績/A/B/C/Xの個別オン・オフ)、`案件_Dim[部署名]`、`案件_Dim[クライアント名]`、`地域_Bridge[地域]`、`市場_Bridge[市場]`、`事業区分_Bridge[事業区分]`。
- **左パネル**: テーブル(`案件_Dim[案件名]`/`[クライアント名]`/`[部署名]`/`前年実績値`、上位N ではなく列ヘッダーでの通常ソート降順)+ 横棒グラフ(同じフィールド)。タイトルは固定文字列「前年案件ランキング」。
- **右パネル**: テーブル(`案件_Dim`の3列 + `案件別ブレンド値_合計`)+ 積み上げ横棒グラフ(Y軸=`案件_Dim[案件名]`、X軸=`案件別ブレンド値`、凡例=`凡例_実績見込[項目]`)。**上位Nフィルターは使わず**、`案件別ブレンド値_合計`を「ツールヒント」欄に追加した上で「条件の並び替え」で降順ソート(理由は後述のパフォーマンス項目参照)。タイトルは`右グラフタイトル`メジューにfxバインドした動的テキスト(例:「2026年案件ランキング(1〜6実績+7月以降見込)」)。

### 新テーブル: `案件_Dim`
`SF案件リスト`から参照+重複の削除(案件IDのみで実行、複数列選択したまま重複削除すると効かないので要注意)して作成。列: `案件 ID/Item ID`、`案件名`、`クライアント名`、`部署名`。**物理リレーションシップは4ファクトテーブルいずれとも確立できず**(過去に`クライアント_Dim`で遭遇したのと全く同じ「列 ''(テーブル '')には重複する値...」という空欄クォートのプラットフォームバグ、ブラウザ再読込・テーブル再作成でも直らない、実データ上は重複なしを確認済み)。**リレーションシップは諦めてTREATASのみで対応**しており、今後同じ現象が出たら即座にTREATAS方式に切り替える(このプロジェクトの標準対応としてほぼ確立)。

### 完成した全メジュー一覧(配置テーブルつき)
- `前年実績値`(`Raw YTD`) — 指標分岐+TREATAS(DealIDs)で前年(選択年-1)の実績を案件別に算出。
- `案件別ブレンド値`(`Raw YTD`) — 指標×`凡例_実績見込[項目]`(実績/A/B/C)の二重分岐。実績側は「選択月以下」でRaw YTD/貢献実績をフィルター、見込側は「選択月より大きい」でCAS見込/貢献見込をフィルター、全てTREATAS(DealIDs)で案件を絞り込み。
- `案件別ブレンド値_合計`(`Raw YTD`) — `SUMX(VALUES('凡例_実績見込'[項目]), [案件別ブレンド値])`で案件ごとの実績+見込合計(ソート・表示用)。
- `右グラフタイトル`(`Raw YTD`) — 選択年/月から動的に文言を組み立てるテキストメジュー。
- `指標選択`テーブル自体に`"貢献売総"`の4行目を追加済み。

### ハマった主な問題と解決策(次回以降も再発しうるので必読)

**① 貢献実績/貢献見込のID列を間違えていた** — CAS見込と全く同じ「子ID/親ID」の2列構造が貢献実績・貢献見込にもあり(`GBC案件/Items: ID`=行ごとの子ID、`月別見込親案件: 案件 ID/Item ID`=案件_Dimと同じ体系の親ID)、TREATASで誤って子ID列(`GBC案件/Items: ID`)を使ってしまい、指標を「貢献売総」にすると両パネルが完全に空白になった。**必ず`月別見込親案件: 案件 ID/Item ID`(親ID)を使うこと** — 今後この2テーブルのID系フィールドを扱う時は常にこの点を確認する。

**② DAX計算列がALL()での上書きフィルターと相性が悪い(新種のバグ、要記憶)** — `CAS見込[月番号]`(DAX計算列、`=MONTH([DATEVALUE])`、モデルビューの型表示は「整数」で正しく見える)を`FILTER(ALL('CAS見込'[月番号]), ...)`のような上書きフィルターで使うと、エラーは出ずに**静かにBLANK**を返す(実績側の同じパターンは問題なし、見込側の確度別集計だけ影響)。原因の切り分けに非常に長い時間がかかった(COUNTROWSでテーブル全体が0行になっていることを確認→CAS見込に空白行があることを発見して除去→それでも直らず→見込データが7月以降にしか存在しないことが判明[実はこれは正常]→`ALL('CAS見込')`(テーブル全体クリア)は効くが`ALL('CAS見込'[月番号])`(列だけクリア)や`FILTER`条件はどう書いても効かないことを特定)。**解決策: DAX計算列を諦めて、Power Query側にネイティブな列(`月番号2 = Date.Month([DATEVALUE])`)を追加し、明示的に「型の変更→整数」を適用**(追加直後は「Any」型のままで、これも別途型不一致エラーの原因になった)。`CAS見込`と`貢献見込`の両方にこの`月番号2`列を追加済み。**教訓: 今後DAX計算列(特に月/年関連)がALL()上書きフィルターで謎のBLANKを返したら、まずPower Query側にネイティブ列を作り直して型を明示変換する、というのが確立した対処法。** これはこれまでに見つかっている「多対一カーディナリティの向き逆転バグ」「IFがテーブルを返せないバグ」「空欄クォートのリレーションシップ重複バグ」とは別の、4つ目の既知の不具合パターンとして記憶しておく。

**③ 上位Nフィルターの性能問題** — `案件_Dim`の全候補(約2900件)に対してTREATASを含む重いメジューで「上位N」フィルターをかけると、待っても表示されないほど遅い(エラーにもならず単に空白)。**対処: 上位Nフィルターは使わず、列ヘッダーのクリックソート、またはグラフの「条件の並び替え」(積み上げ系グラフでは合計メジューを一旦「ツールヒント」に追加してから並び替え対象に選ぶ必要がある)を使う。**

### 次回セッションの開始ポイント
1. ページ名を`ページ1`から分かりやすい名前に変更
2. (任意)他の指標(売上/原価)への対応が必要か確認 — 現状`指標選択`は4択だが、案件別ブレンド値/前年実績値は「売上総利益」以外の`else`分岐で`[売上総利益_合計]`にフォールバックする作りなので、「売上」「原価」を選んでも売上総利益の数字が出てしまう(未対応、動作未確認)
3. まだ本日中に確認していない項目があれば都度Masakiさんに確認

## Salesforce直接接続の検討 — 開始・管理者依頼中 (2026-07-15)

Masaki asked whether the current manual Excel-export bridge (`Prep_CAS X SF Crosstable.xlsx`/`Prep_SalesforceAllRecord.xlsx`, manually exported from Salesforce and placed on OneDrive — see 案件別内訳 section above) could be replaced by Power BI's native Salesforce connector, so Power BI pulls report data directly instead of relying on manual exports.

**Findings so far**:
- Masaki's org's Salesforce **My Domain is `dgx`** (normal access URL: `https://dgx.lightning.force.com/...`; API/OAuth login domain: `https://dgx.my.salesforce.com`).
- He logs into Salesforce via **company SSO**, not a native Salesforce username/password — the plain `login.salesforce.com` connector login form fails with a generic "ユーザー名とパスワードを確認してください" error for this reason. Fix: use the custom-domain login path (`https://dgx.my.salesforce.com`) in Power BI's Salesforceレポート connector, either via the login popup's 「カスタムドメインを使用」link or by setting URL=カスタム in Power BI's データソース接続画面. This successfully routes through SSO.
- After SSO succeeds, hit a **Connected App OAuth authorization error**: `OAUTH_APPROVAL_ERROR_GENERIC` at `dgx.my.salesforce.com/setup/secur/RemoteAccessErrorPage` — this is Salesforce blocking authorization of Power BI's Connected App, not an SSO/credential problem.
- Masaki checked Salesforce Setup and **does not have access to「接続アプリケーションの OAuth 使用状況の管理」** despite otherwise having strong permissions in the org — meaning enabling this requires the separate Salesforce admin team (per Masaki: "管理は社内の別チームが行っています").
- **Status (2026-07-15): blocked on Salesforce admin team.** Masaki is sending them a request (drafted by Claude) asking them to: (1) check whether a "Power BI"/"MicrosoftPowerBI" Connected App is registered, (2) check its OAuth Permitted Users policy, (3) confirm Masaki's profile has "API の有効化" enabled. Next session: check whether the admin team responded, then resume the Salesforceレポート connector setup from where it left off (SSO+custom domain login already confirmed working, just need the Connected App authorized).
- If/when this connector works, the relevant Salesforce Report to point at (per Masaki, already exists) would replace `Prep_SalesforceAllRecord.xlsx`'s manual export — not yet identified by name/ID, ask Masaki once connectivity itself is unblocked.

## KPIカード百万表示化 — 再開 2026-07-15

**Confirmed UI fact (Masaki had already told Claude this before, re-confirmed 2026-07-15 — do not ask again)**: this project's Card visual (the "新しいカード"/KPI-style card used for all KPI tiles throughout the report) has **NO 表示単位 (Display Units) dropdown and NO "コールアウト値" section** in its format pane at all, unlike a standard Power BI Card/KPI visual. The only numeric formatting controls available are under a "データ形式" section: 設定の適用先 (which measure), 書式 (dropdown — confirmed options include at least `10進数`; カスタム was tried previously), パーセンテージ形式 (toggle), 桁区切り記号 (toggle), 小数点以下表示桁数. This is a hard UI constraint for this Power BI Service version/visual type — any fix must work within these controls (or a dedicated pre-divided measure), not assume a 表示単位 dropdown exists.

Cards currently show auto-abbreviated values (e.g. "1.10bn", "804M") even with 書式=10進数 and no custom code — this abbreviation behavior appears to be a built-in smart-default of this card visual for large numbers, not something explicitly configured via a visible toggle, which is presumably why the earlier custom-format-code attempt (`#,##0,,"M"`) produced garbled `"0bnM"` (the custom code's own /1,000,000 scaling likely stacked on top of the visual's inherent auto-abbreviation rather than replacing it).

**Resolved (2026-07-15).** Fix: don't fight the card's numeric formatting at all — make the measure return a pre-formatted **TEXT** string instead of a number, so the card has no number left to auto-abbreviate:
```
<既存メジュー>_M = FORMAT([<既存メジュー>] / 1000000, "#,##0") & "M"
```
Each `_M` measure lives in the same table as its base measure (e.g. `売上金額_合計_M`/`原価金額_合計_M`/`売上総利益_合計_M` in `Raw YTD`, `貢献実績_合計_M` in `貢献実績`). Confirmed working, no garbling, e.g. "1,099M". **One gotcha**: not every KPI card on a given page uses the same base measure — `貢献_年別推移`'s card turned out to use `貢献実績_全期間合計` (an ALL-time, 計上年-filter-ignoring variant) rather than `貢献実績_合計` used by the Q別/月別 pages, requiring its own `貢献実績_全期間合計_M` sibling measure. Always check which specific measure a given card is bound to (視覚化ペインの「値」) before assuming a shared `_M` measure applies. Rolled out to all KPI cards across `設定_年別推移`/`設定_Q別前年比`/`設定_月別_前年比`/`貢献_年別推移`/`貢献_Q別推移`/`貢献_月別推移` (percentage-format cards like `貢献度平均_全期間` were left untouched, no issue there). This closes out the long-deferred KPI millions-display issue.

## Outstanding minor issue history (superseded by section above, kept for context)

KPI card visuals do NOT respect the per-visual custom format string the same way charts do. Tried setting a card's format to カスタム with code `#,##0,,"M"` (same trick that worked for chart Y-axis/data-label 表示単位) — result was garbled `"0bnM"` text, seemingly混on top of some other stale/cached unit setting that couldn't be located (checked the measure's own model-level format property — it was plain `整数`, not the source of "bn"). Tried clearing and retyping the custom code cleanly — same result. Masaki deferred this ("保留にします") to revisit after other higher-priority items are done. Chart-level 表示単位 (百万) works fine, this is specifically a card-visual-only quirk.

See also [[notification_setup]] for unrelated session tooling notes.

## 売上総利益 実績(計上済)ズレ 11,106,923円 — root-caused & fixed 2026-07-27

On `予算達成トラッキング`(指標選択=売上総利益), the `実績(計上済)` KPI showed 208,553,147 vs Tableau/source-Excel's 197,446,224 (見込A/B/C matched fine). Ruled out in order: native duplicate 受発注ヘッダNo (2,021 headers with count>1 across all years — confirmed native to source data via direct Python read of the aicon-hosted live file, not merge-caused), data staleness (downloaded the exact live file aicon serves — byte-identical to local mirror and Tableau's extract: 197,446,224 / 1,025 rows / max date 2026-06-01 in all three), and PBI refresh/cache failure (更新履歴 showed all "完了", manual refresh made no difference).

**Actual root cause**: `CAS_SF_Crosstable`'s dedup step (`Table.Distinct`) keyed on the pair `{"受発注ヘッダNo.", "案件 ID/Item ID"}` instead of `受発注ヘッダNo.` alone. 5 headers (H10-2601045605, H10-2601045621, H10-2601045647, H10-2601026335, H10-2601012596) each map to 2–3 distinct 案件ID values, so multiple pair-rows survived dedup and each caused an extra fan-out match when later merged into `Raw YTD` (which merges on 受発注ヘッダNo alone) — exactly 32 excess 2026 rows (1,057 vs true 1,025), accounting for the full 11,106,923円 gap.

**Fix applied and confirmed**: changed the `Table.Distinct` call to `Table.Distinct(#"変更された列タイプ 1", {"受発注ヘッダNo."})` (single-column key). Verified via temporary measures (`テスト_生SUM_文字`→197,446,224, `テスト_RawYTD_2026行数_文字`→1,025) — both now match source exactly.

**Cleanup not yet done** (do at start of next session touching this area): delete diagnostic artifacts — measures `テスト_生SUM`, `テスト_生SUM_文字`, `テスト_RawYTD_2026行数`, `テスト_RawYTD_2026行数_文字` (Raw YTD table) plus older ones from an earlier 貢献売総 debugging arc (`貢献実績_マージ前確認用` query, `テスト_全行数`/`テスト_2026行数`/`テスト_マージ前行数` measures); queries `Raw YTD_重複チェック用`, `Raw YTD_マージ前確認用`. Also not yet visually re-confirmed: the actual production `実績(計上済)` KPI card on the page itself (only the temp measures were confirmed) — should already be fixed since it reads the same now-corrected `Raw YTD`, but hasn't been screenshotted post-fix.

**Useful technique validated this session**: reading Tableau `.twb` files as raw XML via grep/Bash to pull exact calculated-field formulas/datasource names is far more reliable than relying on the user's screenshots/description when cross-checking a Tableau-vs-PowerBI number — reuse this whenever such a comparison comes up again.

Unrelated but found in the same debugging arc: a separate data-corruption issue (openpyxl formula-cache breaking Tableau's display, not a Power BI bug) was found and fixed across several files in this same QBR folder — see [[openpyxl_empty_v_tag_corruption]] for details, including a scan of which files in `.../QBR作成/` were affected and to what degree.

## Browser-based Power Query editing confirmed possible — 2026-08-12

Contrary to the earlier assumption that Salesforce-object-connector query editing required Power BI **Desktop** (see "Direct Salesforce connector migration" section above), it turns out Power Query Online in the **Service browser** can fully edit these queries too — no Desktop/Windows App needed for this. Path: report → 編集 → リボン「セマンティック モデルを開く」→ 編集モードに切替(「表示中」ドロップダウン→「編集」) → ribbon「クエリ」→「データの変換」. Entering edit mode on a non-large semantic model auto-triggers a one-way conversion to "大きなセマンティック モデル ストレージ形式" (large semantic model storage format, enables version history) — this happened automatically and was confirmed with Masaki before proceeding; generally benign but worth flagging before doing this on another report.

**Full M script of any query** is visible/editable via 表示タブ→スクリプト→「クエリのスクリプト」(shows the whole `let...in` block, not just the selected step) — much faster than clicking through steps one at a time. Editing: type/paste into this script view, then click into the code and press **Ctrl+Enter to commit** — but the UI often doesn't visually refresh immediately after Ctrl+Enter (still shows "Ctrl+Enterでコミット" placeholder and old step list); switching to a different query and back forces it to redraw and reveals the commit actually succeeded. Don't conclude a commit failed just from stale-looking UI — verify via reopening.

**Danger discovered**: the Power Query editor's own "キャンセル" button, when a heavy query is still running, doesn't just cancel that one execution — it discards **all unsaved changes across the whole editor session** and drops back to Model View. Any new/edited queries not yet hit with the editor's "保存" button are lost (existing saved queries are untouched). Cost nothing this time since only new test queries were lost, but don't hit キャンセル as a way to interrupt a slow-running preview — wait it out or navigate away some other way.

**GBC__c is heavy to query via the Salesforce Objects connector**: even with `Table.SelectColumns`/`Table.SelectRows` applied early in the M chain, Power Query Online does not appear to fold these into the Salesforce request — it fetches the full object (149 columns, all rows) every time the query chain is evaluated fresh, taking **1–2 minutes per evaluation** (confirmed via the 状態/メモリ/CPU indicators in the status bar, e.g. "実行中 (1m 24s)" / "270MB" / "1.3GB"). This has real implications for scheduled-refresh duration if these become production queries — worth testing actual refresh time before committing to this design, and worth investigating whether a `Salesforce オブジェクト` connector option exists to push filtering server-side (not found yet).

## Extending Salesforce-object migration to CAS見込/貢献実績/貢献見込 — resumed 2026-08-12, blocked on data mismatch

Picked up from the "paused mid-investigation" state in the section above. Built and validated a self-join base query in Power Query Online (as a new test query, not touching production):

```
Source = Salesforce.Data("https://login.salesforce.com/", [ApiVersion=48]),
GBC__c = Source{[Name="GBC__c"]}[Data],
Account = Source{[Name="Account"]}[Data],
月別行のみ = Table.SelectRows(GBC__c, each [Year__c] <> null and [Month__c] <> null),
... Table.NestedJoin on SalesByYear_GBC_parent__c = Id (self-join to parent) ...
... Table.NestedJoin on 月別見込親案件: クライアントID = Account.Id, expand Account.Name → クライアント名 ...
```

**New discovery not in the earlier field-mapping table**: `GBCClient__c` (parent's client field, → report column "月別見込親案件: クライアント/Client") is a **lookup to Account**, not a formula/text field — the Salesforce Objects connector returns it as a raw Account `Id`, not the display name. A second self-contained join to the `Account` object (expand `Name`) is required to get the actual client name text. Verified this resolves correctly to real company names (e.g. "味の素", "Kirin VN", "Ajinomoto...").

**Bug found and fixed**: `Year__c` is a **選択リスト (picklist, i.e. text type)** in Salesforce, not a number — confirmed via Object Manager (項目とリレーション → search "年度" doesn't work via quick-find for some reason, had to scroll-search the virtualized list; found under label "年度" / API `Year__c` / データ型 "選択リスト"). A filter written as `[年度] = 2026` (numeric literal) silently returns 0 rows since the comparison never matches; must use `[年度] = "2026"` (text literal) instead. Watch for the same trap on `月` (Month__c) and other fields assumed numeric.

**BLOCKED — data doesn't match between old (manual Excel) and new (SF-direct) versions**, verified via a one-shot comparison query summing key totals from both:

| Query | 旧(Excel) 行数/合計 | 新(SF直結) 行数/合計 |
|---|---|---|
| CAS見込 (見込売総) | 249行 / 191,429,909円 | 756行 / 404,006,263円 |
| 貢献実績 (Group売総) | 2,953行 / 59,968,078,898円 | 4,365行 / 90,304,121,840円 |
| 貢献見込 (Group売総) | 239行 / 4,702,480,090円 | 4,365行 / 90,304,121,840円 |

**Root cause identified for at least part of the gap**: 貢献実績_SF_TEST and 貢献見込_SF_TEST produced **identical** totals and row counts — because the M code written for both only filtered on `Year__c <> null and Month__c <> null`, with no condition distinguishing "actuals" rows from "forecast" rows. The original Excel-sourced queries pull from two *different* Salesforce reports (実績用: report ID `00OfP00000AlBNFUA3` / 見込用: report ID `00OGA00000CkNMN2A3`) which evidently apply their own additional filter (on 確度, GM承認/Auth., RecordType, a date range, or something else not yet identified) to separate actuals from forecast — this filter was never reverse-engineered, only the shared self-join structure was. Same likely applies to why CAS見込's new version has ~3x the rows/~2x the revenue of the old one.

**RESOLVED 2026-08-12 (same session, continued) — actual filter conditions read directly off all 3 Salesforce reports.** Opened each report's 検索条件 (filter) panel in the browser (report → filter funnel icon → panel shows each condition card + the overall boolean like `1 AND 2 AND 3 AND (4 OR 5) AND 6`). All 3 reports share the exact same 6-condition shape, only the 年月 (year-month) value list differs:

1. `月別用重複確認` (child's own field, API `GBCMonthDupChk__c`) = **False**
2. `月別見込親案件: フェーズ/Phase` (parent's `GBCPhase__c`, already in the self-join) **<> ""** (not blank)
3. `年月` = a literal list of `YYYYMM` strings — this is a *contiguous range*, not a curated sparse whitelist as first suspected:
   - CAS見込 report (`00O7F00000Ayt1TUAR`): `202401`–`202612` (2 years)
   - 貢献実績 report (`00OfP00000AlBNFUA3`): `202201`–`202612` (manually extended each month per the QBR manual, currently reaches through 2026/12)
   - 貢献見込 report (`00OGA00000CkNMN2A3`): `202607`–`202612` only (rolling next-6-months window)
4. `月別見込親案件: 部署名/Dept.` (parent's `GBCorgChoice__c`) = one of: 業管, AP1部, AP2部, AP3部, SK部, SP1部, SP2部, NS部, HRM, 局付け
5. `月別集計用/部署名` — **newly identified field**, child's own, API name **`GBCParentorgChoice__c`** (formula/text) — contains one of: BD, GS, NB
   (condition 4 OR 5 — either the parent's department is in that list, or the child's own rollup-department field contains one of those codes)
6. `確度` (`Accuracy__c`) = one of: A, B, C, X, "" (blank) — **except the 貢献見込 report, whose confidence-list is A, B, C, X only (no blank)**, all others allow blank too

**Field id for "年月" itself was not pinned down** — two candidate formula fields share the display label "年月" (`YearMonth__c` and `Sales_YearMouth_Link__c`), and neither the report's filter-edit popup nor Object Manager's quick-find (label-only, doesn't match API names) resolved which one backs the report column; chasing it further (scroll-search the 94+ field virtualized list, or diff actual values of both fields in a Power Query preview) was deferred as unnecessary — **decided to reconstruct the same range test from `Year__c`+`Month__c` instead**, which are already pulled: `年月連番 = Number.From([Year__c]) * 100 + Number.From([Month__c])`, then filter `[年月連番] >= <start> and [年月連番] <= <end>`. Since the report's own 年月 list is just a contiguous YYYYMM range in every case observed, this is equivalent.

**Updated base query** (adds `GBCParentorgChoice__c` as a native child column, plus the `年月連番` calculated column; DATEVALUE construction also switched to `Number.From(...)` guards since Year__c/Month__c are text/picklist):
```
let
    Source = Salesforce.Data("https://login.salesforce.com/", [ApiVersion=48]),
    GBC__c = Source{[Name="GBC__c"]}[Data],
    Account = Source{[Name="Account"]}[Data],
    月別行のみ = Table.SelectRows(GBC__c, each [Year__c] <> null and [Month__c] <> null),
    必要な子列 = Table.SelectColumns(月別行のみ, {"Id","SalesByYear_GBC_parent__c","Year__c","Month__c","Accuracy__c","GBCSettingSales__c","Instruction_Fixed_Amount__c","GBCGross__c","GBCMonthContributionGross__c","GBCMonthContributionGrossF__c","GBCMonthContributionGrossABC__c","GBCMonthContributionGrossP__c","GBCGMauthorize__c","GBCMonthDupChk__c","GBCParentorgChoice__c"}),
    親と結合 = Table.NestedJoin(必要な子列, {"SalesByYear_GBC_parent__c"}, GBC__c, {"Id"}, "親案件", JoinKind.LeftOuter),
    親列の展開 = Table.ExpandTableColumn(親と結合, "親案件", {"Id","Name","GBCorgChoice__c","GBCCommercial_distribution__c","GBCArea__c","GBCCountry__c","GBCOutsideCom__c","GBCJU__c","GBCPhase__c","GBCMiddleClass__c","GBCContributionPercent__c","GBCGMConfirmed__c","GBCClient__c"}, {"月別見込親案件: 案件 ID/Item ID","月別見込親案件: 案件名/Item title","月別見込親案件: 部署名/Dept.","月別見込親案件: 商流/Business flow","月別見込親案件: 地域/Region","月別見込親案件: 市場/Market","月別見込親案件: 関係会社/Partner companies","月別見込親案件: 事業(業務)区分/Business category","月別見込親案件: フェーズ/Phase","月別見込親案件: 活動項目/Activity Items","月別見込親案件: GBC貢献度/Attrib. Ratio","月別見込親案件: GM確認/Confirmed","月別見込親案件: クライアントID"}),
    Accountと結合 = Table.NestedJoin(親列の展開, {"月別見込親案件: クライアントID"}, Account, {"Id"}, "取引先", JoinKind.LeftOuter),
    取引先名の展開 = Table.ExpandTableColumn(Accountと結合, "取引先", {"Name"}, {"月別見込親案件: クライアント/Client"}),
    DATEVALUE列の追加 = Table.AddColumn(取引先名の展開, "DATEVALUE", each #date(Number.From([Year__c]), Number.From([Month__c]), 1), type date),
    年月連番の追加 = Table.AddColumn(DATEVALUE列の追加, "年月連番", each Number.From([Year__c]) * 100 + Number.From([Month__c]), Int64.Type),
    列名の変更 = Table.RenameColumns(年月連番の追加, {{"Id", "GBC案件/Items: ID"}, {"Year__c", "年度"}, {"Month__c", "月"}, {"Accuracy__c", "確度"}, {"GBCSettingSales__c", "見込売総"}, {"Instruction_Fixed_Amount__c", "GBC取設定/SETTEI TO(JPY)"}, {"GBCGross__c", "Group売総"}, {"GBCMonthContributionGross__c", "月別集計用/GBC貢献売総(A)/Att.Rev(A)(JPY)"}, {"GBCMonthContributionGrossF__c", "月別集計用/GBC貢献売総(AB)/Att.Rev(AB)(JPY)"}, {"GBCMonthContributionGrossABC__c", "月別見込親案件: 月別集計用/GBC貢献売総(ABC)/Att.Rev(ABC)(JPY)"}, {"GBCMonthContributionGrossP__c", "貢献売総_計上"}, {"GBCGMauthorize__c", "GM承認/Auth."}, {"GBCMonthDupChk__c", "月別用重複確認"}, {"GBCParentorgChoice__c", "月別集計用/部署名"}, {"月別見込親案件: GBC貢献度/Attrib. Ratio", "貢献度"}})
in
    列名の変更
```
This base query WAS successfully committed and previewed correctly in the browser editor (confirmed via screenshot before the session was interrupted).

**CAS見込 target filter** (references the base above; was mid-edit when the session was stopped, ended in an "Invalid identifier" parse error due to a Ctrl+Enter commit race in the Power Query Online script editor — not a logic bug, just needs re-entering cleanly, ideally via the "詳細エディター" dialog icon in the 表示 tab rather than the inline script-view Ctrl+Enter flow which has repeatedly shown timing issues this session):
```
let
    ソース = GBC_月別_自己結合_Base_TEST,
    名前が変更された列 = Table.RenameColumns(ソース, {{"月別見込親案件: 案件名/Item title", "案件名"}, {"月別見込親案件: 部署名/Dept.", "部署名"}, {"月別見込親案件: 地域/Region", "地域"}, {"月別見込親案件: 市場/Market", "市場"}, {"月別見込親案件: 事業(業務)区分/Business category", "事業区分"}}),
    マージされたクエリ数 = Table.NestedJoin(名前が変更された列, {"月別見込親案件: クライアント/Client"}, クライアント名変換, {"元クライアント名"}, "クライアント名変換", JoinKind.LeftOuter),
    #"クライアント名変換 の展開" = Table.ExpandTableColumn(マージされたクエリ数, "クライアント名変換", {"クライアント名_調整後"}, {"クライアント名_調整後"}),
    フィルター処理された行 = Table.SelectRows(#"クライアント名変換 の展開", each
        [月別用重複確認] = false
        and [月別見込親案件: フェーズ/Phase] <> null and [月別見込親案件: フェーズ/Phase] <> ""
        and [年月連番] >= 202401 and [年月連番] <= 202612
        and (
            List.Contains({"業管","AP1部","AP2部","AP3部","SK部","SP1部","SP2部","NS部","HRM","局付け"}, [部署名])
            or ([月別集計用/部署名] <> null and (Text.Contains([月別集計用/部署名], "BD") or Text.Contains([月別集計用/部署名], "GS") or Text.Contains([月別集計用/部署名], "NB")))
        )
        and List.Contains({"A","B","C","X","", null}, [確度])
    )
in
    フィルター処理された行
```
For **貢献実績**: same shape but skip the 部署名/地域/市場/事業区分 renames (original 貢献実績 kept the raw 月別見込親案件-prefixed names, see the earlier field-mapping section), use `[年月連番] >= 202201 and [年月連番] <= 202612`, same 確度 list (includes blank).
For **貢献見込**: same as 貢献実績 but `[年月連番] >= 202607 and [年月連番] <= 202612`, and 確度 list **without** blank: `{"A","B","C","X"}` (no `""`/`null`).

**Caveat on 部署名 matching**: `[部署名]` (parent's `GBCorgChoice__c`) was treated as single-select for `List.Contains` exact-match purposes, consistent with prior sessions' understanding (only 市場/事業区分 are documented multi-select picklists) — not re-verified this session, worth a sanity check if the department-condition ends up excluding rows unexpectedly.

**Not yet done**: re-apply the CAS見込 filter cleanly (session was interrupted mid-edit), build the same for 貢献実績_SF_TEST/貢献見込_SF_TEST, re-run the `検証_合計突合_TEST` one-shot comparison query to confirm totals now match the old Excel-sourced queries within a small tolerance (some drift expected since the old Excel snapshots were taken at an earlier point in time than live Salesforce data, and the report's 年月 upper bound is manually advanced each month per the QBR manual — check current month's upper bound if the range constants above have gone stale by the time this resumes). Only after that matches should the actual production query swap + user confirmation happen.

**Session state**: all 5 test queries (`GBC_月別_自己結合_Base_TEST`, `CAS見込_SF_TEST` [currently in a broken/errored state from the interrupted edit — either fix or delete-and-recreate via 参照 next session], `貢献実績_SF_TEST`, `貢献見込_SF_TEST`, `検証_合計突合_TEST`) exist only in-editor, never hit "保存" — production model/report completely unaffected, safe to resume or abandon. The shared browser (d14461, port 9226) was left with the Power Query Online editor open on the errored CAS見込_SF_TEST query when the session stopped (user ran low on tokens, explicitly asked to stop mid-action before any further edit). The one persistent side effect from this session: the semantic model was converted to "大きなセマンティック モデル ストレージ形式" (see section above) — this is real/permanent but was confirmed with Masaki as acceptable before doing it.

## メモ運用上の注意 — 2026-08-17

このファイルは600行超あり、一度のReadでトークン上限(25000)に達して後半が切れることがある(2026-08-17に実際発生: 前半だけ読んで「自己結合から新規構築」という古い案内をユーザーに一度提示してしまい、後半[L516-616、2026-08-12の最新セッション]を読んで訂正した)。**次にこのファイルを参照して次アクションを案内する際は、必ずoffset指定で最後まで読み切ってから答えること。** 直近の状態は常にファイル末尾に追記されている(新しい記録ほど下)。

現在(2026-08-12時点)の最先端状態: 「Extending Salesforce-object migration to CAS見込/貢献実績/貢献見込」節(L526〜)が最新。自己結合ベースクエリ完成済み、6条件フィルタ解明済み、CAS見込_SF_TESTがCtrl+Enterコミット競合で壊れた状態のまま中断中。次回は詳細エディターでの再入力から。

## 重要な教訓 — クエリの「読み込み無効化→再有効化」はリレーションシップ・DAX計算列を破壊する(2026-08-18)

CAS見込_SF_TESTへの本番差し替えを「既存クエリをリネーム→読み込み無効化、新クエリを本番名にリネーム」という手順(SF案件リストの時と同じやり方のつもり)で行ったところ、保存は成功したにもかかわらずレポート側のメジューがエラーになった。原因は、**読み込みを無効化したテーブルに紐づいていたDAX計算列(`四半期`)と手動作成のリレーションシップ(`市場_Bridge`/`事業区分_Bridge`/`地域_Bridge`との多対多、`四半期`テーブルとの一対多)が消失し、読み込みを再度有効化しても復元されない**という仕様(バグ)だったため。`月番号2`↔`月`のような単純な関係はPower BIの自動検出で偶然復元されたが、それ以外は全て失われた。さらに、構造の似たテスト用クエリ同士(同じ列名を持つ)の間に、自動検出による無関係な誤リレーションシップも大量生成された。

**今後の教訓/標準対応**: 本番テーブルのデータソースだけを差し替えたい場合は、名前の入れ替えではなく、**既存の本番クエリを選択したまま、そのスクリプト(M式)の中身だけを新しいコードに丸ごと上書きする**方式を使うこと。テーブルオブジェクトの実体(=リレーションシップ・計算列の持ち主)を変えないため、理論上はこちらが安全(未検証だが次回はこの方式を採用する)。なお、この事故は`バージョン履歴`(大きなセマンティック モデル ストレージ形式で有効)による復元で無事にリカバリできた — 保存は最大5世代までしか残らないので、大きな変更の前後では保存タイミングに注意すること。

## 「見込」系データの絞り込みルール(2026-08-18に判明)

CAS見込・貢献見込をSalesforceに直結する際、生のオブジェクトデータには過去月も全部含まれているため、そのまま使うと過去の実績と二重計上になる。正しくは:
- **CAS見込**: 年月連番が「今月以降」(動的、`Date.Year(DateTime.FixedLocalNow())*100 + Date.Month(...)`)のみを対象とする。上限は元の`202612`のまま(遠い将来までの固定上限で問題ない)。
- **貢献見込**: 同じく「今月以降」だが、上限も固定6ヶ月ではなく**その年の12月まで**(`Date.Year(now)*100+12`)という動的なローリング窓が必要。8月なら5ヶ月分、11月なら2ヶ月分と年末に向けて窓が縮む。
- **貢献実績**(実績データ)はこの絞り込み不要、全期間のまま。

旧来の手動Excel更新プロセスは、毎月人力でSalesforceレポート側の「年月」フィルタ値リストを更新することでこれを実現していた。Power BI側で動的に計算するようにすれば、このSalesforceレポート自体の月次メンテナンスは(Power BI用途に関しては)不要になる。

## CAS見込/貢献実績/貢献見込 本番差し替え完了 (2026-08-19)

前節までの検証済みロジックを使い、3クエリとも「本番クエリのM式を直接上書き」方式(8/18に確立した安全な方式)で本番差し替えを完了。`GBC_月別_自己結合_Base_TEST`は恒久名`GBC_月別_自己結合_Base`にリネームし、`CAS見込`/`貢献実績`/`貢献見込`の3クエリすべてがこれを共通の`ソース`として参照する構成になった。差し替え作業中に新たに発見・解決したバグは以下の4つ(すべて次回以降の同種作業でも再発しうるので要記憶):

**① 型不一致(Text vs Integer)バグ**: `Year__c`/`Month__c`はSalesforce側で選択リスト(テキスト型)のため、リネームしただけの`年度`/`月`列もテキストのまま残る。既存の`SelectedYear`パターンの measure(`'Raw YTD'[計上年]`など整数列との比較)がこれと比較しようとして「型Textの値と型Integerの値の比較はサポートしていません」エラーになる。**対策: 各クエリの最後に`Table.TransformColumnTypes(..., {{"年度", Int64.Type}, {"月", Int64.Type}})`を必ず追加する。**

**② `月番号2`列の欠落**: 7/24に発見した「DAX計算列の月番号がALL()上書きフィルターで謎のBLANKを返す」バグの対策として、`CAS見込`・`貢献実績`・`貢献見込`の**3テーブルすべて**に`月番号2 = Date.Month([DATEVALUE])`(Power Query側で明示的にInt64型変換)が追加済みだった(過去のメモには「CAS見込と貢献見込の2つ」としか記録されていなかったが、実際には貢献実績にもあった — 新旧列名差分チェックで発覚)。**新クエリを作る際は3テーブルとも`月番号2`列を追加すること。**

**③ 誤リレーションシップ自動生成(`SalesByYear_GBC_parent__c`)**: Base自己結合の中間キー列`SalesByYear_GBC_parent__c`が、Base・3つの`_SF_TEST`テストクエリすべてに同じ列名で残っていたため、Power BIの自動検出が「多対1の1側」として誤認識し、スケジュール更新が「重複する値のため許可されない」エラーで失敗した。「リレーションシップの管理」ダイアログには該当リレーションシップが表示されない(処理失敗のため未確定状態と思われる)という紛らわしい状態だった。**対策: この列は自己結合にしか使わないので、`Base`の最終出力から`Table.RemoveColumns`で完全に除外する。加えて、検証用に作った`_SF_TEST`クエリ群は本番差し替えが終わったら都度削除し、同じ列名を持つ余計なクエリをモデルに残さない。**

**④ Salesforceパーセント型フィールドのスケール(貢献度)**: `月別見込親案件: GBC貢献度/Attrib. Ratio`(API名`GBCContributionPercent__c`)はSalesforce API経由だと0〜100の生値(例: 30%なら`30`)で返るが、旧Excelプロセスでは0〜1の小数(`0.3`)に正規化されていた。既存のDAX計算列`貢献売総 = Group売総 × 貢献度`がこの生値をそのまま使ったため、`貢献見込`の月別金額が実際の100倍に膨れ上がった(月次グラフで単月が全期間合計を超えるという明らかな兆候から発覚)。**対策: `Base`のM式の最後で`貢献度`列を`/100`する(`Table.TransformColumns`)。Salesforceのパーセント型フィールドを新規に使う際は、生値が0〜100スケールであることを前提に確認する。**

**作業中のヒューマンエラーも1件**: Baseと`貢献見込`用に別々に用意した2つのM式を、ユーザーが逆のクエリに貼り付けてしまい(`貢献見込`にBaseの中身が入る)、`月番号2`/`クライアント名_調整後`列が見つからないエラーが発生。原因は「どのクエリにどの内容を貼るか」の指示が長く紛らわしかったため — 今後は各クエリのブロックに①②のように明確な番号・宛先クエリ名を毎回つけて提示する。

**現状**: 3クエリとも保存・数値確認済み、正常。**未確認事項**: 保存時の差分更新は速かった(`貢献実績`単体で2分49秒)が、実際のスケジュール更新(12:00/17:00 JST、全体をフル再評価する可能性が高い)でどれだけ時間がかかるかは未検証。次回のスケジュール実行結果を「更新履歴」で確認し、1時間を大きく超えるようなら17:00の1回だけに減らすことを検討する。また、検証用に作った列差分チェック用の小さいクエリ群(`CAS見込列差分_...`等)の削除もまだ済んでいない可能性がある。

## ⑤ Salesforce案件IDの15桁/18桁不一致バグ (2026-08-19、既存ページで発覚)

CAS見込の本番差し替え後、既存ページ`前年実績_該当年実績+見込案件比較`(通称「案件別ランキング(実績+見込ブレンド)」、7/24構築)の`案件別ブレンド値`メジューで、見込(A/B/C)分岐が全部ゼロになる不具合が発生(上司からの指摘で発覚)。

**原因**: SalesforceのレコードIDには**15桁(大文字小文字を区別)と18桁(区別しない、末尾3桁はチェックサム)の2形式**があり、Salesforce ObjectsコネクタでGBC__cを直接取得した`Base`/`CAS見込`/`貢献実績`/`貢献見込`は**18桁形式**(例: `a1hfP000008mxPNQAY`)を返すのに対し、`案件_Dim`(`SF案件リスト`由来、こちらも同じGBC__cオブジェクトからだが2026-08-09の別セッションで構築)は**15桁形式**(例: `a1hfP00000Ds9re`)だった。`案件別ブレンド値`メジューの`TREATAS(DealIDs, 'CAS見込'[月別見込親案件: 案件 ID/Item ID])`のような案件ID同士の突合が、この桁数不一致で完全に0件ヒットしていた。

**調査手法**: `CALCULATE(COUNTROWS('CAS見込'), ALL('CAS見込'), TREATAS(VALUES('案件_Dim'[案件 ID/Item ID]), 'CAS見込'[月別見込親案件: 案件 ID/Item ID]))`のような診断用メジューでTREATASのヒット件数を確認 → 0件だったため、両テーブルの実際のID文字列をPower Queryで抜き出して目視比較し、桁数の違いに気づいた。

**修正**: 18桁は先頭15文字を取れば15桁形式に変換できる(逆方向はチェックサム計算が必要で簡単ではない)。`Base`の最終ステップに追加:
```
案件ID正規化 = Table.TransformColumns(<前のステップ>, {{"月別見込親案件: 案件 ID/Item ID", each if _ <> null then Text.Start(_, 15) else _, type text}})
```
`Base`1箇所を直すだけで`CAS見込`/`貢献実績`/`貢献見込`すべてに反映される(3テーブルとも同じ列を継承しているため)。

**教訓・今後の注意点**:
1. **Salesforceオブジェクトを起点にした新しい案件ID系の結合・TREATASを作るときは、必ず両側の桁数(15桁 or 18桁)を確認してから組むこと。** 見た目が似ているだけに気づきにくい(先頭15文字は同じ値になるため、目視でもパッと見は分かりにくいことがある — 文字数を数えるか`Text.Length()`で確認するのが確実)。
2. この`案件別ブレンド値`メジューの見込分岐も、当初は`見込_合計`/`貢献見込_合計`という別の既存メジュー(クライアント名_調整後によるTREATASを内包)を呼んでいたが、これも別のバグ(下記⑥)で機能していなかったため、`SUM('CAS見込'[見込売総])`のような直接計算に書き換えた。案件ID単位で既にTREATAS絞り込みしている以上、クライアント名での二重絞り込みは本来不要だったので、これは同時にシンプル化にもなった。

## ⑥ `クライアント名_調整後`の突合漏れ (2026-08-19、⑤の調査中に発覚)

`CAS見込`の`クライアント名_調整後`列(Salesforceの取引先名/Account.Nameと、既存の`クライアント名変換`テーブルの`元クライアント名`を突き合わせて作る列)が、272行中**82行しか埋まっていない**(約70%が空欄)ことが判明。SalesforceのAccount.Name表記が、旧来の手動突合表の表記と一致しないケースが多いため。

この列をTREATASで使っている`見込_合計`(旧来からある基本メジュー、指標選択・クライアントスライサー対応版)や`貢献見込_合計`の一部の分岐は、この突合漏れの影響で不正確になっている可能性がある。**未修正・要フォローアップ**: `クライアント名変換`テーブルの表記をSalesforceのAccount.Name基準に合わせて拡充するか、マッチングロジック自体を改善する必要がある。今回は`案件別ブレンド値`側でクライアント名TREATASを使わない形に迂回して急場をしのいだのみで、根本対応はまだ。`クライアント名`スライサーで絞り込んだときに`見込_合計`を直接参照している他のページ・メジューがあれば、同様に数字がズレている可能性がある。

## 新規ページ「設定完総_見込み整理」構築中 (2026-08-19開始)

Salesforce移行完了後、正樹さんが毎月手動で作っていた月次報告レポート(`パイプライン`フォルダの`KPI0813`シート等、日付サフィックス付きシートを毎月複製して更新する運用)をPower BIで自動化するために新規ページとして構築開始。参照元: `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/パイプライン/2026パイプライン 0812.xlsx`の`KPI`から始まる日付サフィックス付きシート群(`KPI0813`が直近、他に`KPI2500905`〜`KPI0212`まで多数の月次スナップショットあり)。「設定売総」セクション(A1〜L11あたり)が今回複製対象。「貢献売総」「電通プロダクト/サービス」など他セクションも同じシートにあるが、今回はスコープ外(必要になれば同じシートを再度参照)。

**確定した列対応**(AP1行・局全体行の数値で検証済み):
| シート列 | 意味 | Power BIメジュー |
|---|---|---|
| C(26年実績) | 当年実績 | `売上総利益_合計`(既存) |
| D(前年実績) | 前年同期間(1〜Cutoff月)実績 | `売上総利益_前年同期間`(新規) |
| E/F/H(A/B/C) | 確度別見込 | `見込A/B/C_合計_部署別`(新規、下記参照) |
| G(実績+A+B) | 累計 | `実績_AB後`(新規) |
| I(実績+A+B+C) | 年度着地見込 | `年度着地見込_部署別`(新規) |
| K(前年度実績) | 前年**通年** | `売上総利益_前年`(既存、月/四半期スライサー無しなら通年を返す) |
| L(前年比) | I÷K | `前年比_ABC`(新規) |

**前年基準の確認済み事項(正樹さん確認済み、2026-08-19)**: シートにはD9(165,451,133)とD10(164,724,603)という僅かに異なる2つの前年基準値があったが、**D9が正しい**。D10は前年に例外的にAP1部/SP1部/BD部以外の部署に利益が計上された特殊案件の調整値で、通常は発生しない。今後はD9(前年同期間実績そのもの)のみを基準にする。

**カード②「+A反映後」の金額表示**: 元シートでは「+A反映後」カードに「実績+A+B」の金額(315.4M)を誤って表示していた(パーセンテージだけ+Aの60.2%で金額は使い回し)。Power BI版では**正しい「実績+Aのみ」の金額(約281.6M)を表示するよう修正**することで正樹さんと合意。

**「先月◯◯%」のスナップショット比較は今回のPower BI自動化では実装しない**(正樹さんの意向、2026-08-19)。過去のライブデータ再計算では不可能(その時点のA/B/C見込データ自体が違うため)、毎月スナップショットを保存する別の仕組みが必要になるのでスコープ外とした。

**重大バグ発見・修正 — CAS見込との部署リレーションシップ欠如**: `見込A_合計`/`見込B_合計`/`見込C_合計`(既存)を`Raw YTD[計上組織名（調整後）]`で行区切りしたテーブルに入れると、**全部署で同じ値になる**(部署でフィルタされていない)バグが発覚。原因は`Raw YTD`と`CAS見込`の間に部署列同士のリレーションシップが存在しないため(`CAS見込[部署名]`は今まで自分自身のスライサーとしてしか使われておらず、Raw YTD側からの行コンテキストが伝播しなかった)。**対策として新規メジュー3つを追加**(`Raw YTD`テーブル):
```
見込A_合計_部署別 = 
VAR SelectedDept = SELECTEDVALUE('Raw YTD'[計上組織名（調整後）])
RETURN
IF(
    ISBLANK(SelectedDept),
    [見込A_合計],
    CALCULATE([見込A_合計], FILTER(ALL('CAS見込'), SUBSTITUTE('CAS見込'[部署名], "部", "") = SelectedDept))
)
```
(B/Cも同型)。`SUBSTITUTE(...,"部","")`は`CAS見込[部署名]`が「AP1部」でも「AP1」でも両対応できる保険(過去の`貢献見込`の部署コード"部"サフィックス問題と同種の罠を先回りして回避)。`ISBLANK`分岐により、部署フィルターが無い場面(合計行やページ全体カード)では自動的に既存の（部署非依存の）`見込A_合計`にフォールバックする設計。

これに伴い`実績_A後`/`実績_AB後`/`前年比_ABC`も部署別版を使うよう定義し直し済み。**修正後、部署別テーブルの数値がExcel(KPI0813)の値とほぼ一致することを確認済み**(小さな差分はSalesforceライブデータが8/13時点のスナップショットより新しいことによる自然なズレ)。

**全メジュー一覧**(すべて`Raw YTD`テーブルに追加、2026-08-19時点で完了):
`最新実績月番号`、`売上総利益_前年同期間`、`実績_A後`、`実績_AB後`、`前年比_ABC`、`予算_累計_今年`、`達成率_実績`、`達成率_A後`、`達成率_AB後`、`対予算率`、`対前年率`、`示達比テキスト`、`前年差`、`示達まで残り`、`見込A_合計_部署別`、`見込B_合計_部署別`、`見込C_合計_部署別`、`年度着地見込_部署別`(既存の`達成度_見込`/`予算_年間合計`も流用)。

**ページ構築の進捗(2026-08-19時点)**:
1. ✅ ページ`設定完総_見込み整理`作成、計上年スライサー(2026)配置
2. ✅ 部署別内訳テーブル完成・検証済み(行=`Raw YTD[計上組織名（調整後）]`、列=26実績/前年実績/A/B/A+B後/C/A+B+C後/前年度/前年比、合計行ON)
3. ⬜ 上部情報ボックス(未着手)
4. 🔶 KPIカード4枚 — 作業中。**視覚化の種類の罠**: 「KPI」ビジュアル(値/トレンド軸/ターゲットの3点構成)と「カード」ビジュアル(複数フィールドを1つの井戸に追加でき、それぞれ個別タイル表示される、このプロジェクトで他ページのKPIタイルに使われている方)を混同しやすい。**必ず「カード」の方を選ぶこと。** フィールドのラベルは各フィールドの▼→「名前の変更」で短縮可能(例:「達成率_実績」→「実績」)。上端の色帯を再現したい場合は別途細い四角形の図形をオーバーレイで重ねる(このプロジェクトで確立済みの重ね合わせテクニックと同じ)。
5. ⬜ 下部KPI行4枚(未着手): `予算_年間合計`(示達額)/`示達比テキスト`/`前年差`/`示達まで残り`

**次回セッションの開始点**: Step 4(KPIカード4枚、カードビジュアルへの切り替え・ラベル調整の続き)から再開。その後Step 3(上部情報ボックス)・Step 5(下部KPI行)。デザインの微調整(色帯・フォントサイズ等)は最後に回してよい。

## 「設定完総_見込み整理」ページ完成 + 月スライサーによる遡及機能実装 (2026-08-20)

Step 4〜6(KPIカード・上部情報ボックス・下部KPI行)を完成させた後、正樹さんから追加要望: 月スライサーを追加し、「6月時点で実績がどう見えていたか」等、過去に遡って実績を確認できるようにしたい。見込み(A/B/C)は過去のスナップショットを保持していないため、月選択時(自動検出された最新実績月と違う月を選んだ時)は非表示にする、という仕様で合意し実装。

**この「月による遡及」機能の実装で、合計4つの「リレーションシップ伝播フィルターが解除されない」バグを連続して踏んだ**。すべて根本原因は同じクラス(スライサーの選択が、意図した以上に広い範囲のテーブルへ伝播してしまい、`ALL()`や`FILTER(ALL(...))`で明示的にクリアしないと解除されない)だが、影響範囲がテーブルごとに違うため、都度発見・対処が必要だった:

**バグ①: `Raw YTD`とのリレーションシップ伝播** — `FILTER(ALL('Raw YTD'[月番号]), 月番号<=CutoffMonth)`という書き方だけでは、月スライサーから伝わる直接フィルタが解除されないことがある(6月を選ぶと6月単体になってしまう、7月+8月+...+12月の複数選択だと偶然「6月まで」に近い結果になり紛らわしい)。

**バグ②: `Raw YTD[月番号]`がDAX計算列だった** — 7/24に発見済みの「DAX計算列をFILTER(ALL(...))で使うと誤動作する」バグが、Raw YTDの月番号列でも再現。Power Query側にネイティブ列`月番号2 = Date.Month([DATEVALUE])`(明示的にInt64型変換)を追加して解決。CAS見込/貢献実績/貢献見込だけでなく、`Raw YTD`にもこの罠がある(今回初めて判明)。

**バグ③: `月番号2`に切り替えても直らなかった** — ①②を両方直しても、まだ単月選択で単月の値しか返らなかった。真因は「新しい列(`月番号2`)に条件を足しても、スライサーから`月`テーブル経由で伝わる**古い**`月番号`列への直接フィルタは全く別物として残り続ける」ことだった。**最終的な正しい書き方は、`ALL('月')`(ディメンションテーブル側を丸ごとクリア)+`FILTER(ALL('Raw YTD'[月番号2]), ...)`(ネイティブ列で正しい範囲を再指定)の組み合わせ。** 片方だけでは不十分。

**バグ④: `CAS見込`にも`月`テーブルとのリレーションシップがあった** — `Raw YTD`側を直しても、上部KPIカードの「+A反映後」等が実績のみと同じ値になる(A/B/Cがゼロ)バグが別途発生。原因は`CAS見込[月番号]`(こちらもDAX計算列)が`月`テーブルと直接リレーションシップを持っており、月スライサーで「7月」を選ぶと、8月以降のデータしか無い`CAS見込`が全滅(0行)になっていたため。既存の共有メジュー`見込A_合計`等は触らず、ページ専用のラッパーメジュー内で`CALCULATE([見込A_合計], ALL('月'), ...)`のように`ALL('月')`を追加して解決。

**バグ⑤(関連、月スライサーとは別件): `前年比_ABC`が古い`売上総利益_前年`を参照したまま** — テーブルの「前年度」列自体は新メジュー`売上総利益_前年度_遡及`に差し替え済みだったが、`前年比_ABC`メジューの中の分母は差し替え忘れで古いメジューのままだった(前年比が局全体1739.5%のような異常値になった)。**関連する複数のメジューを同時に修正する時、依存関係を全部洗い出さないと一部だけ直り忘れる**という教訓。

**プロジェクト全体への教訓(今後、月/期間スライサーで「遡及」「as of」的な機能を作るときは必ず確認すること)**:
1. スライサー用のディメンションテーブル(`月`/`四半期`など)と直接・間接にリレーションシップを持つ**全てのファクトテーブル**を洗い出す(`Raw YTD`だけでなく`CAS見込`/`貢献実績`/`貢献見込`/`CAS予算`等、複数ある可能性が高い)。
2. 各ファクトテーブルの「月」列がDAX計算列かPower Query列か確認する(fxアイコンの有無)。DAX計算列なら`FILTER(ALL(col),...)`単体では信用できないので、ネイティブ列を用意する。
3. 独自の絞り込みロジックを書くときは、`FILTER(ALL(FactTable[col]), cond)`だけでなく、**ディメンションテーブル側も`ALL(DimTable)`で明示的にクリアする**、の2点セットを基本形にする。
4. 複数のメジューが同じ「前年」「予算」等の概念を参照している場合、1つを新メジューに差し替えたら、**依存する全メジューをリスト化して同時に差し替える**(テーブル列だけでなく、他のメジュー内部からの参照も含めて)。

最終確認: 7月選択(自動検出月と同じ)でABC見込み表示・数値ともExcel参照値とほぼ完全一致、6月選択(過去)で実績のみ正しく遡及・見込み非表示、を確認済み。ページはほぼ完成状態。

## 追加修正3件 + 貢献売総スライサーは次回持ち越し (2026-08-20続き)

**① 実績データの「ズレ」は正常だった**: 正樹さんから「1〜7月実績がExcel(215.6M)とPower BI(214.2M)でズレている」と指摘があり、Bashで元ファイル(`~/Library/CloudStorage/OneDrive-電通/GBC戦略企画部_GBC設定実績・見込/QBR作成/GBC CAS実績_FY22 TO DATE.xlsx`)を直接調査。8/13時点のバックアップ(1,025行/197,446,224円)と現在のライブファイル(1,112行/214,185,802円、8/18 07:30更新)を突合した結果、**Power BI側(214,185,802)が正しく、Excelの215,633,242の方が古いスナップショット**と判明(パイプラインのログには自動書き込みの形跡は無く、手動保存と推測)。正樹さん本人も同じ214,185,802を確認し一致。バグではなかった。

**② 部署の表示順序の固定**: `Raw YTD`にPower Query列(DAX計算列だと循環参照エラーになるため必ずPower Query側で)`部署並び順`を追加(`if [#"計上組織名（調整後）"] = "AP1" then 1 else if ... else 99`、**列名にコロン/全角括弧等の特殊文字がある場合は`[#"列名"]`形式必須、という今日何度も出た罠がここでも再発**)。モデルビューで`計上組織名（調整後）`列を選択→プロパティ→「並べ替え列」→`部署並び順`を指定して解決。並べ替え列の設定はモデルビュー(セマンティック モデルを開く→データ タブ)のフィールド一覧から、フィールドをクリック→左のプロパティパネルを下にスクロールして見つかる(UIが分かりにくく、テーブルビジュアル内のフィールド右クリックメニューとは別物なので混同注意)。

**③ `貢献度平均`系3メジューの計算ロジックが間違っていた**: 上司から「貢献度平均が30%は高すぎるのでは」と指摘。原因は`AVERAGE('貢献実績'[貢献度])`という**単純(非加重)平均**を使っていたため、金額の小さい案件の高い貢献率に引っ張られて実態より高く出ていた。正しくは「計上済み貢献利益の合計 ÷ 元の(貢献率適用前)貢献利益の合計」という加重平均であるべきで、`DIVIDE(SUM('貢献実績'[貢献売総_計上]), SUM('貢献実績'[Group売総]))`に修正(`貢献度平均`/`貢献度平均_前年`/`貢献度平均_全期間`の3つとも、AVERAGE部分だけ差し替え、TREATAS分岐ロジックはそのまま)。**教訓: 「平均」を扱うメジューは、単純平均か加重平均かを都度確認する。特に「率」や「％」列の平均は加重平均が正しいケースが多い。**

**次回のタスク(未着手)**: 正樹さんから「設定完総_見込み整理ページに、スライサーで設定売総/貢献売総を切り替えられるようにしたい」と依頼あり。規模が大きい(現在のページの約20個のメジュー全てに指標分岐を追加する必要がある)ため、時間切れで次回に持ち越し。次回開始時の設計方針:
- 指標選択用の新しい非connectedテーブル(例: `指標選択_設定貢献`、値は"設定売総"/"貢献売総")を追加してスライサー化
- `貢献実績_合計`(既存)は内部で`ISFILTERED('Raw YTD'[計上組織名（調整後）])`ベースのTREATAS分岐を持っているため、**Raw YTDの計上組織名（調整後）を軸にした今のテーブル構造にそのまま貢献実績_合計を差し込んでも部署別に正しく効くはず**(CAS見込のような追加の部署ブリッジ実装は不要な可能性が高い、次回最初に検証すること)
- 貢献側は「貢献度」の%スケール(÷100)・貢献度平均の加重平均化など、今日直した貢献実績特有の罠を踏まえた設計にする
- 元のExcel参考画像(`KPI0813`シート、行14〜24の「貢献売総」セクション)は設定売総セクションと列構成が微妙に違う(前年実績[同期間]列が無い、示達比の代わりに「承認(実績)」列など)ので、着手前に改めて列対応を確認する

## データ更新情報(Salesforce/CAS更新日時表示)機能を追加 (2026-08-21)

正樹さんから「いつのデータか分かるようにデータ更新情報のシートを作りたい」と依頼。Salesforce系(CAS見込/貢献実績/貢献見込)とCAS実績(Excel、Raw YTD)の更新日時をそれぞれ表示する仕組みを構築。

**Salesforce更新日時**: ライブ取得のため、Power Query内で`DateTime.LocalNow()`を使えばそのまま「取得した瞬間の日時」=データの鮮度になる。新規クエリ`Salesforceデータ取得日時`:
```
let
    Source = DateTime.LocalNow(),
    テキスト = "Salesforce更新日: " & DateTime.ToText(Source, "yyyy/M/d H:mm:ss"),
    テーブル化 = #table({"Salesforce更新日"}, {{テキスト}})
in
    テーブル化
```

**CAS実績(Raw YTD)の元Excelファイル更新日時**: こちらはライブ取得ではなく手動更新されるExcelなので、「Power BIがいつ更新したか」ではなく「元ファイル自体がいつ編集されたか」を見る必要がある。SharePointメタデータ抽出は複雑なので、正樹さんの提案で**CAS実績自動パイプライン側(`~/CASExport/cas_monthly_pipeline.py`)に、実際にデータを反映した時にOneDrive上へ日時マーカーファイルを書き出す処理を追加**する方式にした:
- パイプラインに`write_last_updated_marker(ym)`関数を追加(`Workbook`をopenpyxlからimport)。`QBR作成/`フォルダ(Raw YTDと同じ、Power BI Serviceが既にアクセスできる場所)へ`CAS実績_最終更新日時.xlsx`という1シート・2行(A1=対象月,B1=値/A2=更新日時,B2=ISO日時)の小さなファイルを書き出す。`process_month()`内、file1/file2への追記完了後・work_statusログ書き込み前に呼び出す。
- Power Query側で読み込み、新規クエリ`CAS実績データ最終更新日時`:
```
let
    Source = Excel.Workbook(Web.Contents("<Raw YTDと同じURL接頭辞>CAS%E5%AE%9F%E7%B8%BE_%E6%9C%80%E7%B5%82%E6%9B%B4%E6%96%B0%E6%97%A5%E6%99%82.xlsx"), null, true),
    シート = Source{[Item="更新情報",Kind="Sheet"]}[Data],
    生の値 = シート{1}[Column2],
    日時型 = DateTime.From(生の値),
    テキスト = "CASデータ更新日: " & DateTime.ToText(日時型, "yyyy/M/d H:mm:ss"),
    テーブル化 = #table({"CASデータ更新日"}, {{テキスト}})
in
    テーブル化
```
(`シート{1}`が2行目、`Table.PromoteHeaders`は不要 — マーカーファイルは見出し行の無い単純な2行2列表のため、これを使うと「列挙内に十分な要素がなかった」エラーになる。)

**踏んだ罠**:
- Power Queryのクエリが最終的にスカラー値(文字列)を1つ返す設計だと、「値 "..." を型 Table に変換できません」エラーになる。**モデルに読み込むクエリは必ずテーブル形式で終わる必要がある**(`#table({"列名"}, {{値}})`で1行1列のテーブルに包む)。
- テスト実行時にマーカーファイルへ「今日の日付」で書き込んでしまい、実際のExcel更新日(8/18 07:30)とズレた → Bashで元ファイルの実際の`stat`更新時刻を取得し、マーカーファイルを正しい日時で上書きして解決。

**カードビジュアルの表示調整で判明した制約**: 新しい「カード」ビジュアルの書式設定には「データ ラベル」という項目名は無く「カード」という名前のセクションになっている。中身は「レイアウト/パディング/罫線/区切り線/背景/アクセント バー/影/光彩」で、**パディングを0にしても余白が完全には詰まらない**(原因不明、この視覚化タイプの既知の制約の可能性)。正樹さんは「下に余白を作るデザインで妥協する」方針に。

**状態**: 機能完成・正樹さん確認済み。カード2枚(Salesforce更新日/CASデータ更新日)を`設定完総_見込み整理`ページに配置済み。

## セッション終了 (2026-08-21) — 次は新規チャットで「新しいレポートシートを作る作業」

正樹さんが本セッションを終了し、次回は新しいチャットで「新しいレポートシートを作る」作業を開始する意向。具体的にどのシートかはこの時点でまだ聞いていない(次回チャット冒頭で確認要)。他の未完了タスク(優先度低い順ではない、次回どれから着手するかは正樹さん次第):
1. `設定完総_見込み整理`ページへの設定売総/貢献売総切り替えスライサー(規模大、8/20に持ち越し決定のまま未着手)
2. `クライアント名_調整後`の突合漏れ根本対応(CAS見込のクライアント名マッチ率が272行中82行のみ、8/19発見のまま未着手)
3. 検証用に残っている可能性のある列差分チェック用クエリ群の削除確認(8/19に指示したが完了確認していない)

## セッション完了 (2026-08-21) — 新規ページ「Rev/Sales/Cost YTD_Pivot」相当を構築、マイナス赤字表示対応済み

`CAS集計 FY26_GBC_クライアント_件名別_final20260804.xlsx`のRev/Sales/Cost YTD_Pivot3枚を代替する新規ページを構築。設計は「設定_年別推移」ページを複製し、マトリックス1枚(行=計上組織名(調整後)→クライアント名_調整後のドリルダウン、列=月[月ラベル]、値=既存メジュー`指定指標_年別`)+ 既存の`指標選択`スライサーで3ピボットを1つに統合。8スライサー(指標選択/計上年/月/計上組織名/クライアント名/地域_Bridge/市場_Bridge/事業区分_Bridge)すべて配置・正樹さん確認済み。

このページ構築の過程でAP1のデータ不整合を発見・調査・修正(詳細は[[powerbi_raw_ytd_ap1_gap_incident_20260821]])。マイナス値の赤字表示は、メジュー側カスタム書式コード(`[Red]`)がリテラル表示される不具合を回避し、visual側条件付き書式(ルール)で対応(詳細は[[powerbi_negative_red_format_quirk]])。

**今回のセッションで完了**:
- 新規マトリックスページ本体(構築・検証・赤字表示まで完了)
- AP1データ不整合の修正(215,633,242円で確定、Power BI反映済み)
- `cas_pipeline_lib.py`の`find_last_data_row()`重大バグ修正(スクラッチ検証のみ、本番未検証)

**引き続き未着手(前回2026-08-21早い時点からの持ち越し、今回未着手のまま)**:
1. ~~`設定完総_見込み整理`ページへの設定売総/貢献売総切り替えスライサー(規模大)~~ → **完了(2026-08-21同日、後続セッション)、詳細は下記新セクション参照**
2. `クライアント名_調整後`の突合漏れ根本対応(CAS見込のクライアント名マッチ率が272行中82行のみ)
3. 検証用に残っている可能性のある列差分チェック用クエリ群の削除確認 — **今回新たに`貢献実績_SF_TEST`/`貢献実績_SF_TEST_2`/`貢献実績_2`も追加で残っている、要削除**
4. 9/2の自動パイプライン初回本番実行後、`find_last_data_row()`修正が正しく機能したか確認(行数・ログ・work_statusエントリ)

## ページ名確定: `部別_月別_利益等`

前回セッション(同日早い時点)で構築した「Rev/Sales/Cost YTD_Pivot相当」の新規マトリックスページは、正樹さんが最終的に**`部別_月別_利益等`**という名前で確定させた(サイドバーのページ一覧で確認済み)。今後この名前で参照すること。

## `設定完総_見込み整理`ページ: 設定売総/貢献売総切り替えスライサー実装完了 (2026-08-21)

### Phase 0: `貢献実績`クエリをSalesforce直結(`GBC_月別_自己結合_Base`)に移行

従来`貢献実績`だけが旧Excel(`GBC 貢献実績_FY22 TO DATE.xlsx`、yamada_keita OneDrive)直読みのまま残っていた(8/19メモでは「3クエリとも移行完了」となっていたが実際は貢献実績が取り残されていた/記録の誤り)。この機会に移行。

**新M式**(貢献実績クエリ、本番差し替え済み):
```
let
    ソース = GBC_月別_自己結合_Base,
    マージされたクエリ数 = Table.NestedJoin(ソース, {"月別見込親案件: クライアント/Client"}, クライアント名変換, {"元クライアント名"}, "クライアント名変換", JoinKind.LeftOuter),
    #"クライアント名変換 の展開" = Table.ExpandTableColumn(マージされたクエリ数, "クライアント名変換", {"クライアント名_調整後"}, {"クライアント名_調整後"}),
    名前が変更された列 = Table.RenameColumns(#"クライアント名変換 の展開", {{"月別見込親案件: 部署名/Dept.", "部署名"}}),
    フィルター処理された行 = Table.SelectRows(名前が変更された列, each
        [月別用重複確認] = false
        and [#"月別見込親案件: フェーズ/Phase"] <> null and [#"月別見込親案件: フェーズ/Phase"] <> ""
        and (
            List.Contains({"業管","AP1部","AP2部","AP3部","SK部","SP1部","SP2部","NS部","HRM","局付け"}, [部署名])
            or ([#"月別集計用/部署名"] <> null and (Text.Contains([#"月別集計用/部署名"], "BD") or Text.Contains([#"月別集計用/部署名"], "GS") or Text.Contains([#"月別集計用/部署名"], "NB")))
        )
        and List.Contains({"A","B","C","X","", null}, [確度])
    ),
    月番号2の追加 = Table.AddColumn(フィルター処理された行, "月番号2", each Date.Month([DATEVALUE]), Int64.Type),
    型の変換 = Table.TransformColumnTypes(月番号2の追加, {{"年度", Int64.Type}, {"月", Int64.Type}})
in
    型の変換
```
`貢献実績`は8/18メモの「全期間のまま(絞り込み不要)」ルール通り、`貢献見込`と違って年月連番の範囲フィルタは無し。

**重要な発見**: `GBC_月別_自己結合_Base`自体が既に`Group売総`/`貢献度`(÷100スケール済み)/`貢献売総_計上`という最終列名にリネーム済み(Base内の`列名の変更`ステップ参照)。CAS見込/貢献見込のように改めてリネームする必要はない — 逆に旧Excel時代の列名(`"Group売総/Revenue (JPY)"`等)でリネームしようとするとエラーになる。

**検証方法**: Power Query上でモデルに読み込まずに`List.Sum`/`Table.Group`による集計クエリを都度作って確認(プレビュー行数上限を回避、[[feedback_powerquery_verify_via_aggregate_query]]と同じ手法)。2022〜2025年は新旧完全一致、2026年は+21.2M(ライブSalesforceが新しい)、2027年は+26.1M(旧Excelには存在しなかった翌年データ)で全差分(+47.3M)を説明できた。

**`組織名_調整後`計算列の修正が必須だった**: 移行前(旧Excel時代)は部署名が「BD1」のように無表記だったが、Salesforce直結後は「AP1部」のように"部"付き表記に変わったため、既存のSWITCH計算列(`SWITCH([月別見込親案件: 部署名/Dept.], "BD1","BD", "BD2","BD", 元の値)`)が非BD1/BD2をすべて素通りしてRaw YTDの命名(「AP1」等)と一致しなくなっていた。修正:
```
組織名_調整後 = 
VAR RawDept = SUBSTITUTE('貢献実績'[月別見込親案件: 部署名/Dept.], "部", "")
RETURN
SWITCH(RawDept, "BD1", "BD", "BD2", "BD", RawDept)
```
**この手のマスタデータ移行では、他の計算列が暗黙に前提としていた旧フォーマットが壊れていないか必ずチェックすること。**

2026年のSF_TEST検証で判明した部署別内訳(GM承認済み、NS/SKは廃止コードにつき参考): AP1=47,199,506 / AP2=331,983,393 / AP3=43,911,430 / SP1=62,456,530 / SP2=107,350,000 / BD=596,711,500 / NS=13,731,000(無視) / SK=0。6部署合計=1,189,612,359、NS込みで1,203,343,359(貢献実績_合計の値と一致、検証OK)。

### Phase 1: 指標分岐の設計方針転換(月カットオフ→シンプルな年間合計方式)

当初、設定売総と同じ「`最新実績月番号`(CutoffMonthベースの累積)」パターンを貢献実績にもコピーしようとしたが、**`自動検出_最新実績月番号`の貢献分岐が実データで12を返す**という致命的なバグに遭遇。原因: Salesforce直結後の`貢献実績`テーブルには、GM未承認の将来月(12月まで)の「空行」が最初から全部存在しており、`MAX(月番号2)`が単純に行の存在で判定すると常に12になってしまう。かつGM承認は必ずしも月順に進まない(先行承認された12月データが実在)ため、「GM承認済みの最終月」でも判定不能と判明。

**最終的な設計方針(正樹さん承認済み、2026-08-21)**: 貢献売総は「遡及機能(過去月ビュー)は不要」と割り切り、既存の`貢献実績_合計`/`貢献実績_前年合計`(2026-07-13作成、クライアント/部署TREATASロジック内蔵、`予算達成トラッキング`ページで実績確認済み)をそのまま呼び出す方式に単純化。カットオフ月ベースの累積計算は一切行わない。

### 実装した7つの部品メジュー(`設定完総_見込み整理`ページ、`Raw YTD`テーブル)

1. **`自動検出_最新実績月番号`/`最新実績月番号`**: 貢献分岐は最終的に**削除**し、8/20以前の設定専用の姿に戻した(貢献では使わなくなったため)。
2. **`売上総利益_遡及`**: 貢献分岐 = `CALCULATE([貢献実績_合計], ALL('月'))`
3. **`売上総利益_前年同期間`**: 貢献分岐 = `CALCULATE([貢献実績_前年合計], ALL('月'))`
4. **`売上総利益_前年度_遡及`**: 貢献分岐 = 同じく`CALCULATE([貢献実績_前年合計], ALL('月'))`
5. **`見込A_合計_部署別`/`見込B_合計_部署別`/`見込C_合計_部署別`**: 貢献分岐は`CALCULATE(SUM('貢献見込'[貢献売総]), ALL('月'), '貢献見込'[確度]="A", FILTER(ALL('貢献見込'), SUBSTITUTE('貢献見込'[月別見込親案件: 部署名/Dept.], "部", "")=SelectedDept))`(A/B/Cで確度文字列のみ変更)。表示/非表示ゲートは「選択月が実際の暦月(`MONTH(TODAY())`)と一致するか」で判定(設定側は`自動検出_最新実績月番号`基準のまま、指標で分岐)。
6. **`予算_累計_今年`**: 貢献分岐 = `貢献予算`テーブルを`計上年=SelectedYear && 月番号<=MONTH(TODAY())`でフィルタ(実カレンダー月で按分)。
7. **`実績_A後`/`実績_AB後`/`年度着地見込_部署別`**(上位メジュー): ゲート判定を指標で分岐(`ReferenceMonth = IF(貢献売総, MONTH(TODAY()), [自動検出_最新実績月番号])`)するよう修正。これ以外の上位メジュー(前年比_ABC/達成率系/対予算率/対前年率/示達比テキスト/前年差/示達まで残り/達成度_見込_遡及)は全て上記の組み合わせ(DIVIDE/加算)のみなので無修正で自動的に正しく動作した。

### 踏んだバグ・教訓(今後の月/指標分岐実装で必ず確認すること)

**① 共有メジューの`ALL('月')`欠落**: `貢献実績_合計`(2026-07-13作成、`予算達成トラッキング`ページ専用に作られた)には月スライサー除外のための`ALL('月')`が無かった。`貢献実績`は`月`テーブルとリレーションシップを持つため、月スライサーが選択されているページから呼び出すと想定外に月で絞り込まれてしまう。**元のメジューは直接修正せず、呼び出し側で`CALCULATE([貢献実績_合計], ALL('月'))`のようにラップして対処**(他ページへの影響を避けるため)。**教訓: 新しいページで既存の共有メジューを再利用する際は、そのメジューが元々どんなスライサー構成のページ用に作られたかを確認し、想定していないスライサー(特に月/四半期)が新ページにあれば、呼び出し側でALL()保護を追加すること。**

**② `SELECTEDVALUE`が「行コンテキストはあるがデータが無い月」でBLANKを返す罠**: `SelectedDept = SELECTEDVALUE('Raw YTD'[計上組織名（調整後）])`のような単純な部署検出が、月スライサーで「Raw YTD(CAS実績)にまだデータの無い将来月(例: 8月、今日時点で実績確定は7月まで)」を選んでいる状態だと、`Raw YTD`が(部署行コンテキスト×月フィルタ)の交差で0行になり、SELECTEDVALUEがBLANKを返す(部署名が読み取れているように見えて実は空)。**対策: `CALCULATE(SELECTEDVALUE(...), ALL('月'))`のように月フィルタを明示的にクリアしてから読み取る。** この罠は「ISFILTEREDベースの検出(貢献実績_合計方式)なら影響を受けない(月を先にALL()した上でVALUES()を取っているため)が、素朴なSELECTEDVALUEだと影響を受ける」という非対称性がある点が特に紛らわしい。デバッグ時は`診断用メジュー = SELECTEDVALUE(...)`を実際にカード/列として置いて直接値を確認するのが最も早い。

**③ ゲート判定の指標依存を見落としやすい**: `実績_A後`等の上位メジューが内部で`[自動検出_最新実績月番号]`(設定専用)を直接参照している場合、貢献売総選択時にも設定側の基準で判定されてしまい、指標分岐した下位メジュー(見込A_合計_部署別等)が正常でも上位メジューだけブランクになる。**新しい指標分岐を追加する際は、末端の部品メジューだけでなく、それを呼び出す全ての上位メジューの中に指標非依存のゲート/条件が紛れていないか確認すること。**

**設計判断**: 貢献売総選択時、`実績`(GM承認済み金額)は月スライサーの値に関わらず常に最新のGM承認状態を返す(遡及非対応、意図的な仕様)。見込(A/B/C)のみ、選択月が実際の暦月と一致する時だけ表示する(それ以外の月では非表示、設定売総と似た体験)。

### 未着手・保留

- 月選択ガイド用カード(`月選択ガイド`メジュー、指標に応じて「今は◯月を選んでください」を案内)を追加、正樹さん確認済み。
- 「指標選択を切り替えたら月スライサーも自動追従する」機能はDAXでは実現不可(スライサー間の書き込みは不可)。ブックマーク+ボタン方式を提案したが、正樹さんは今回見送り、ガイドカードのみで運用継続することに決定。
- ~~テスト用に作成した`貢献実績_SF_TEST`/`貢献実績_SF_TEST_2`/`貢献実績_2`クエリの削除が未実施。~~ → **完了(2026-08-21)**。実際には`貢献実績_SF_TEST_合計チェック`/`貢献実績 合計チェック`/`貢献実績用_2`という名前で計5件残っていた(想定と若干名前が違った)。正樹さんが削除・保存してエラーなし確認済み。

## `クライアント名_調整後`突合漏れの根本対応 完了 (2026-08-21)

[[powerbi_migration_gbc_dashboard]]の懸案⑥(CAS見込のクライアント名マッチ率が272行中82行のみ)に対応。

**手法**: Power BI DAXクエリビューで`EVALUATE SUMMARIZECOLUMNS('CAS見込'[月別見込親案件: クライアント/Client], 'CAS見込'[クライアント名_調整後])`を実行し、CAS見込の distinct クライアント名59件(未マッチ分)を取得(正樹さんに実行・結果貼り付けを依頼)。**ハマった点**: 未クォートの日本語テーブル名(`CAS見込[...]`)だとこのDAXクエリビューでパーサーエラー(`Invalid token`)になる — `'CAS見込'[...]`とシングルクォートで囲むと解決。この方言はSELECTEDVALUE等の通常メジュー内では問題にならず、DAXクエリビュー特有の模様。

**原因**: Salesforce由来のクライアント名(全角ラテン文字が多い、「◯◯株式会社」表記)と、旧来の`クライアント名変換`マスタ(`Client Name_CAS_SF_FY22 TO DATE.xlsx`、半角/略称中心)の表記ゆれ。完全な体系不一致ではなく、単純な「登録漏れ」だった(マスタの1249行中892行は既にGBC Salesforce由来のフラグが立っており、仕組み自体は機能していた)。

**マッチング手法**: NFKC正規化(全角→半角)+法人格接頭辞/接尾辞(株式会社/(株)/Co.,Ltd.等)の除去+区切り文字除去、で正規化キーを作り既存マスタと突合。59件中51件は自動解決(表記ゆれのみ)、8件は人手判断が必要(真の新規クライアント or 統合先不明)。すべて正樹さんに個別確認の上で解決(例: NC CORPORATIONが正式名でNCSOFT CORPORATIONは旧称と判明→既存マスタの2行を修正、Acecook Vietnam=既存の「ｴｰｽｺｯｸ ﾍﾞﾄﾅﾑ」バケットに統合、ARCHION/Zespri/ミズノ等はマスタに該当なし→新規クライアントとして自己参照で登録)。

**実装**: マスタファイル`Client Name_CAS_SF_FY22 TO DATE.xlsx`(`/Users/d14461/Library/CloudStorage/OneDrive-電通/AICON - 戦略企画部/GBC数字分析関連資料/`、Power BIのライブ参照元と同一)をopenpyxlで直接編集——59行追加+既存2行(NCSOFT CORPORATION×2)のクライアント名_調整後を修正。[[openpyxl_empty_v_tag_corruption]]の既知バグ(このファイルはまさに過去にこのバグを踏んだ実績あり、Listシートに1033箇所の数式セルがある)に対応するため、`fix_empty_v`パッチ→Excel実アプリでの開く/保存/閉じる再計算パスの2段階を実施。編集前に全シートの非空セル数をベースライン記録し、編集後に他シート(List - Project/Test/Test Format/D13 CL)が完全一致、Listシートが追加分(+236セル=59行×4列)のみ増加していることを確認、数式キャッシュの喪失なしと検証済み。編集前バックアップはスクラッチ領域に保存。

**次回確認事項**: Power BI側のスケジュール更新後、同じDAXクエリを再実行してクライアント名_調整後の空欄行が減っていることを正樹さんに確認してもらう(未実施)。

## 2026-08-25の未解決問題2件、解決 (2026-08-26)

前回(8/25)からの続き。詳細な診断の経緯は[[powerbi_migration_gbc_dashboard_current_state]]の§9(現在の未解決事項)に統合済み、ここでは要点のみ記録する。

**問題1(`Raw YTD`2026年合計の水増し、約210〜310万円)——解決、原因はデータバグではなくフィルター設定。**
診断の流れ: ①`SF案件リスト`自体の重複チェック→クリーン(重複ゼロ) ②`Raw YTD`の`受発注ヘッダNo`重複チェック→多数ヒットしたが、詳細を展開すると案件ID/クライアント名等は完全一致・`売上総利益`のみ異なる値で、検算が合う(CASの正規の複数会計明細行、正常なデータ構造と判明、ファンアウト仮説は却下) ③`Raw YTD`テーブル自体の`List.Sum`直接計算→215,633,242円(8/21確定値と完全一致、Power Query層は健全と確定) ④それでもレポートページの表示は217,733,077円(前回メモの「218,733,077」は恐らく誤記、正しくは217,733,077)のまま、スライサー全クリア・フィルターペインの市場/事業区分/地域基本フィルター確認・手動更新でも変わらず ⑤テーブルビジュアルの「フィルター」ペインを深くスクロールして精査したところ、`市場一致`=1・`事業区分一致`=1(no-op、ブリッジ未フィルター時は素通り設計)に加えて**`部署名`が「(空白)ではない」という基本フィルターが存在**することを発見。

**真因**: `部署名`が空欄のRaw YTD行(CASでは計上済みだが`CAS_SF_Crosstable`にまだ案件ID紐付けが無い、または紐付いた案件IDが現行`SF案件リスト`の絞り込み条件から外れている行——構造的・既知のギャップ、特定の異常案件ではない)の`売上総利益`合計が**ネットでマイナス約▲210万円**(訂正・戻し等の負の会計明細行を含むため)だった。これを除外するフィルターがかかっていたことで、「除外すると合計が減るはず」という直感に反し、**表示合計の方が真の全件合計より大きくなっていた**。`部署名`フィルターを「すべて」に変更し、215,633,242円と一致することを確認して解決。このフィルターを今後もこのページに残すか(意図的な仕様か、移行作業中に紛れ込んだものか)は次回正樹さんと要相談。

**問題2(「売総ランキング」横棒グラフが市場/事業区分スライサーに反応しない)——解決。**
原因: テーブルには`市場一致`/`事業区分一致`の詳細フィルター(=1)が設定済みだったが、**ビジュアルレベルのフィルターは各ビジュアルに個別設定が必要**で、横棒グラフには適用されていなかった(地域は元々このパッチ無しでも機能するため見落とされていた)。グラフにも同じ2つのフィルターを追加して解決、動作確認済み。

**教訓(§6として[[powerbi_migration_gbc_dashboard_current_state]]に集約済み)**:
- スライサーの「クリア」とフィルターペインの個別カードは別物、総額調査では両方を確認すること。
- 「絞り込むと合計が増える」ように見えたら、除外対象行の合計がマイナスである可能性を疑う。
- ビジュアルレベルの詳細フィルターはビジュアルごとに再設定が必要、新規ビジュアル追加時は既存ビジュアルと同じフィルター構成か確認する。

**未完了**: 横棒グラフの「上位N」(既定20件)が絞り込み時に表示件数を圧迫する問題、件数を増やす方向で相談中断(次回具体的な件数を確定)。診断用に作成した`診断 クエリ`/`診断 クエリ2`/`診断 クエリ3`とその関連リレーションシップ、および8/25からの検証用クエリ群(`検証_SF案件リスト件数比較`等)の削除が未実施。

**このセッションでの構成変更**: [[powerbi_migration_gbc_dashboard_current_state]](現状スナップショットの新規リファレンスファイル)を正樹さんの要望で新規作成。今後はこちらを一次参照先とし、このファイル(時系列ログ)には引き続き詳細な経緯・デバッグ過程を記録する形で使い分ける。

## `SF案件リスト`系のExcel脱却(Salesforce直結化) — 作業中・未完了 (2026-08-21)

`SF案件リスト_旧Excel`(→`Raw YTD`/`案件_Dim`/`市場_Bridge`/`事業区分_Bridge`/`地域_Bridge`が依存)をSalesforce直結に置き換える作業を開始。**まだ本番切り替えしていない**(`SF案件リスト_旧Excel`は無傷、ダッシュボードへの影響ゼロの状態で中断中)。

### 発見: 既存の未使用`SF案件リスト`クエリ
過去(8/7〜8/9)の未完了の移行試行の残骸として、`SF案件リスト`という名前の空のSalesforce直結クエリが既に存在(どこからも参照されていない)。これを検証用に再利用することにした。

### 踏んだ罠・教訓(この種の作業で毎回再発するので必読)

1. **DAXクエリビュー/Power Query Onlineでの日本語識別子**: DAXでは`'CAS見込'[...]`のようにテーブル名をシングルクォート必須(未クォートだと`Invalid token`)。M(Power Query)では`[#"クライアント/Client"]`のように、スラッシュ等の特殊文字を含む列名を`[...]`フィールドアクセサで参照する際は`#"..."`で囲む必要がある(未クォートだと`Invalid identifier`)。**両方ともこのプロジェクトで複数回踏んでいる最頻出バグ**。
2. **「空のクエリ」新規作成は使わない**: Power Query Online(ブラウザ版)で「新しいソース→空のクエリ」を作ると、最初に出る入力欄はM式エディタではなく単なる文字列入力欄で、複数行コードを貼ると`#!"let...#(lf)..."`という巨大な文字列リテラルとしてエスケープされてしまい、後から詳細エディターを開いても`Invalid identifier`のまま(検証済み、1行コードでも改行なしでも同じく失敗)。**対策: 既存クエリ(何でもよい)を右クリック→「複製」→複製したものを詳細エディターで編集、という経路だけを使う。** 空クエリ作成→詳細エディターの経路は今回2回とも失敗した。
3. **プレビューの行数上限を回避する集計クエリ手法**(既知、[[feedback_powerquery_verify_via_aggregate_query]]と同じ): `#table({"項目","値"}, {...})`で他クエリを`Table.RowCount`/`Table.Distinct`等で集計した結果だけを返す検証用クエリを作ると、元テーブルが何千行あっても結果は数行なので確実にプレビュー表示される。

### GBC__c(Salesforceオブジェクト)の構造に関する新知見

- `RecordTypeId`で「年度月別明細（GBC）」という値を持つ行が月別の子レコード、それ以外(かつ空でない)が案件マスタ(親)レベルの行。**旧`Year__c`/`Month__c`が空欄かどうかで判定する方法は不正確**(このプロキシ条件だと、マスタでも子でもない別種の行が紛れ込み、クライアント空欄行を大量に誤って含めてしまった)。実際の絞り込み条件は、Salesforceの元レポート「（設定突合用）SF案件リスト」(レポートID`00OfP00000ARvMIUA1`)の検索条件を直接確認して判明: `レコードタイプ <> "年度月別明細（GBC）" and レコードタイプ <> "" and 作成日 >= 2021/04/29`。
- **クライアント名を表すフィールドが複数存在し紛らわしい**: `GBCClient__c`(Accountへのルックアップ、値がIDで多くのマスタ行で空欄)、`GBCParentClient__c`(数式/テキスト、名前から「親レコードのクライアント」を返すと推測され、親を持たないマスタ行では100%空欄という結果が出た)、`GBCClientName__c`(テキスト、試したところ空欄1471件とやや改善するが依然として旧レポートの1件には遠く及ばない)。**レポート上で実際に埋まっていることを目視確認した列「月別見込親案件: クライアント/Client」の実フィールドAPI名がまだ特定できていない** — これが次回の最優先調査事項。

### RESOLVED 2026-08-24 — 「旧レポートは空欄1件のみ」という前提自体が誤りだった

前回セッション(8/21)の目標値「クライアント空欄≈0〜数件」は、旧レポートを実際に開いて数えずに立てた誤った前提だった。今回、旧Excel`Prep_SalesforceAllRecord.xlsx`シート「（設定突合用）SF案件リスト」を直接`openpyxl`で読んで空欄数を数え直した結果:

- 総行数5,233、クライアント空欄**1,468件**(「1件」ではない)
- レコードタイプ別内訳: `CLIENT`(3,602件中 空欄23件)/`PROJECT`(866件中 空欄731件)/`TASK`(764件中 空欄713件)
- つまりPROJECT/TASKタイプの案件はクライアントが元々存在せず、空欄が正常。空欄の少なさを求めるべきはCLIENTタイプに絞った場合のみ(目標≈23件)。

これで8/21の「`GBCClient__c`は空欄1830件で旧レポートの1件と乖離が大きすぎる」という却下理由が成立しなくなった(1830 vs 真の1468は、むしろかなり近い)。

**列見出しの表記も訂正**: レポート編集画面(`00OfP00000ARvMIUA1`)を直接開いて確認したところ、実際の列見出しは「月別見込親案件: クライアント/Client」ではなく、単に**「クライアント/Client」**(自己結合の親経由ではなく、`GBC__c`自身のフィールド)。Object Managerのフィールド一覧でこの表示ラベルに完全一致するのは`GBCClient__c`(参照関係→取引先/Account)のみ(`GBCParentClient__c`のラベルは「案件クライアント」、`GBCClientName__c`のラベルは「GBC CLIENT」で、いずれも「クライアント/Client」とは一致しない)。

**実データでのクロスチェック**: レポートのサンプル行(`GBC__c`レコードID`a1h7F000007JodJ`、クライアント表示="花王株式会社")のレコード詳細ページを直接開いて確認したところ、「クライアント/Client」欄(`GBCClient__c`→Account.Name)と「GBC CLIENT」欄(`GBCClientName__c`、数式`GBCClient__r.GBC_CLIENT__c` — Account側のカスタム項目`GBC_CLIENT__c`を参照)は、このレコードでは同一のテキスト「花王株式会社」を返した。つまり少なくともこのケースでは両者は等価。ただし`GBCClientName__c`は`GBCClient__c`(Accountルックアップ)がnullなら定義上必ずnullになる依存関係にあるため、空欄件数は理論上`GBCClientName__c`空欄件数 ≥ `GBCClient__c`空欄件数のはずが、8/21の実測値は逆(1471<1830)だった — これは2つのテスト時点でRecordTypeフィルタ条件が異なっていた可能性が高く、フィールド自体の優劣を示すものではないと判断。

**結論・推奨**: `GBCClient__c`(→Accountとの結合でName展開)を採用する。理由: (1)Object Manager上のラベルが「クライアント/Client」に完全一致、(2)2026-08-09にCAS見込/貢献実績の自己結合で既に確立・検証済みの同一パターン(`Table.NestedJoin`でAccount.Idと結合→Name展開)がそのまま使い回せる、(3)サンプル行で実際に旧レポートと同じテキストを返すことを確認済み。

### RESOLVED 2026-08-24 続き — CLIENTタイプの空欄超過(356件 vs 旧23件)の原因はSalesforce側の参照切れ、Power Query側のバグではない

`GBCClient__c`+Account結合を実装後、検証クエリでレコードタイプ別集計を取ったところ、CLIENT行3,643件中356件(9.8%)が空欄となり、旧ファイルの23件(0.6%)より大幅に多かった。PROJECT/TASKの空欄率は旧ファイルとほぼ同水準で正常。

**原因特定**: 空欄になっているCLIENT行のうち2件をサンプル抽出し(`GBCClient__c`の生ID値を確認、いずれも18桁・`001`始まりでAccount用IDとして正常な形式)、そのAccountレコードのURLを直接開いて確認したところ、両方とも「アクセスしようとしているレコードが見つかりませんでした。他のユーザーにより削除されたか、システムエラーが発生した可能性があります。」というSalesforceの標準エラーが出た。**つまりIDの桁数不一致([[powerbi_migration_gbc_dashboard]]で過去に経験した15桁/18桁の罠)ではなく、参照先のAccountレコード自体がSalesforce側で削除/統合済みで実在しない(dangling reference)ことが原因。**

- 旧Excelスナップショットは、これらのAccountがまだ存在していた時点でエクスポートされたため名前が解決できていた。
- 現在のライブ接続では、その後のAccount側の重複統合・削除により参照切れとなり空欄になる — **これはPower Query側の結合ロジックの誤りではなく、正しい挙動**(ライブ接続は「今のSalesforceの実態」を反映するため、旧Excelより厳密には正確)。
- 結論: 356件の空欄はそのまま許容してよい。今後もAccount統合が進むにつれて緩やかに増える可能性がある性質の数字であり、修正対象のバグではない。

### 2026-08-25 — 本番切り替え完了(5クエリの参照張り替え)、ただし2つの未解決問題が残る

`Raw YTD`/`案件_Dim`/`市場_Bridge`/`事業区分_Bridge`/`地域_Bridge`の5クエリを`SF案件リスト_旧Excel`→`SF案件リスト`(Salesforce直結)に張り替え、本番切り替え自体は完了した。ただし途中で複数のトラブルが発生し、解決までに以下の紆余曲折があった。今後同種の作業をする際の教訓として残す。

**踏んだトラブルと最終的な対処**:

1. **列名の食い違い**: `SF案件リスト_旧Excel`(Excelレポート由来、`GBC案件/Items: 案件名/Item title`のような長い列名)と新しい`SF案件リスト`(Salesforceオブジェクト直結、`案件名`のような短い列名にリネーム済み)とで列名が違うため、5クエリすべてで列名の対応表通りに書き換えが必要だった(`案件 ID/Item ID`は共通、`GBC案件/Items: 案件名/Item title`→`案件名`、`部署名/Dept.`→`部署名`、`地域/Region`→`地域`、`市場/Market`→`市場`、`事業(業務)区分/Business category`→`事業(業務)区分`、`クライアント/Client`は共通)。
2. **Claudeの指示ミスで`SF案件リスト`の中間ステップが消失**: 「末尾を差し替えてください」という曖昧な指示を出したところ、レコードタイプ絞り込み+Account結合の中間ロジックが丸ごと消え、存在しないステップ名を参照するエラーになった。**教訓: 複数ステップにまたがる複雑なクエリを何度も継ぎ足しで編集する場合は、「末尾を差し替え」ではなく必ずクエリ全文を渡して丸ごと置き換えさせること。** 曖昧な部分置換指示は特に会話が長くなった後(既存クエリの状態をClaude側が正確に把握できていない状態)で危険。
3. **Salesforceオブジェクトコネクタが同一Idを複数行返す(ページング由来と推測)**: `Table.Distinct(..., {"Id"})`(18桁の生ID)だけでは防げず、`案件ID正規化`(18→15桁変換)の**後**にも`Table.Distinct(..., {"案件 ID/Item ID"})`をもう一段階追加する必要があった。教訓: Salesforceオブジェクトを起点にするクエリでは、正規化後の最終キー列に対しても明示的にDistinctをかけるのが安全。
4. **Power BIのリレーションシップ自動検出が繰り返し不要な関係を作った**: ID形式が15桁に統一されたことで列名が一致するテーブル同士(`案件_Dim`↔`地域_Bridge`、`SF案件リスト`↔`地域_Bridge`、`事業区分_Bridge`↔`地域_Bridge`、`市場_Bridge`↔`地域_Bridge`)に対し、データ更新のたびに自動検出が意図しないリレーションシップを勝手に作成し、「重複値」エラーで更新が失敗する現象が複数回(3〜4回)発生した。いずれもモデルビューの「リレーションシップの管理」で該当行を削除して解消。**教訓: Salesforce直結クエリでID列の形式を変更・統一した後は、モデルビューで自動検出によるリレーションシップが増えていないか毎回チェックする必要がある。特にブリッジテーブル同士(市場_Bridge/事業区分_Bridge/地域_Bridge)が直接繋がってしまうケースは要注意(本来は繋がってはいけない)。**
5. **一部のリレーションシップ削除がタイムアウトで失敗**: 複数行を同時選択して一括削除するとタイムアウトすることがあった。1件ずつ個別に削除すると成功した。

**最終的に動作を確認できた点**:
- `設定実績_案件別内訳`ページのテーブル・ランキングチャートが正しく表示され、`市場`スライサーで実際に絞り込みが機能することを確認済み(Japan選択で217,733,077→93,469,324に正しく変化)。
- 心配していた「市場_Bridge等のブリッジ→ファクトテーブルへの多対多リレーションシップが消えたのでは」という懸念は杞憂で、手動再構築(12本)は不要だった(自動検出または既存のリレーションシップで機能している)。

### 未解決の問題 — 次回セッションの最優先事項

1. **`Raw YTD`の2026年合計が期待値とズレている**: `設定実績_案件別内訳`ページのテーブル合計が218,733,077円(市場スライサー「すべて」時)。8/21に確定させた正しい値は215,633,242円で、差額は約310万円。**CASデータ更新日は8/18 7:30:24(8/21の確認より前)であることを確認済みのため、新しいCAS計上による正当な増加という説明は成立しない。** つまり今回の一連の作業(Salesforce直結化)のどこかで実際に合計が水増しされている可能性が高い。疑うべき箇所: `Raw YTD`の`#"マージされたクエリ数 2"`(`SF案件リスト`との結合)で万が一まだ`案件 ID/Item ID`の重複が残っていればファンアウト(行の重複計上)が起きる。`SF案件リスト`の`重複を削除2`ステップが本当に効いているか、`Table.RowCount(SF案件リスト)`と`Table.Distinct(SF案件リスト, {"案件 ID/Item ID"})`の行数を比較して確認するところから始めるとよい。または`Raw YTD`単体(SF案件リストとの結合前)の2026年合計と、結合後の合計を比較し、結合ステップの前後どちらで金額が変わるかを特定する。
2. **「売総ランキング」チャート(`Raw YTD`の`Σ 売上総利益`使用)が`市場`/`地域`/`事業区分`スライサーで絞り込まれない**: 同じページの表形式テーブルは正しく絞り込まれるのに、このランキングチャートだけ反応しない。今回のセッション中に初めて気づかれたもので、今回の変更が原因かは未確定。視覚化ペインでこのビジュアルの「フィルター」設定(視覚エフェクトレベルのフィルター、または相互作用の編集で除外されていないか)を確認するところから始める。

### 現状のクエリ状態(2026-08-25時点)

- `SF案件リスト`: 本番採用済み。最終形は以下(RecordType絞り込み+Account結合+15桁ID正規化+2段階の重複削除):
```
let
    ソース = Salesforce.Data("https://login.salesforce.com/", [ApiVersion=48]),
    GBC__c = ソース{[Name="GBC__c"]}[Data],
    RecordType = ソース{[Name="RecordType"]}[Data],
    Account = ソース{[Name="Account"]}[Data],
    列を選択 = Table.SelectColumns(GBC__c,{"Id", "Name", "GBCArea__c", "GBCCountry__c", "GBCorgChoice__c", "GBCJU__c", "GBCClient__c", "RecordTypeId", "CreatedDate"}),
    重複を削除 = Table.Distinct(列を選択, {"Id"}),
    RecordTypeと結合 = Table.NestedJoin(重複を削除, {"RecordTypeId"}, RecordType, {"Id"}, "レコードタイプ情報", JoinKind.LeftOuter),
    レコードタイプ名の展開 = Table.ExpandTableColumn(RecordTypeと結合, "レコードタイプ情報", {"Name"}, {"レコードタイプ名"}),
    子レコードを除外 = Table.SelectRows(レコードタイプ名の展開, each [レコードタイプ名] <> "年度月別明細（GBC）" and [レコードタイプ名] <> null and Date.From([CreatedDate]) >= #date(2021,4,29)),
    Accountと結合 = Table.NestedJoin(子レコードを除外, {"GBCClient__c"}, Account, {"Id"}, "取引先", JoinKind.LeftOuter),
    取引先名の展開 = Table.ExpandTableColumn(Accountと結合, "取引先", {"Name"}, {"クライアント/Client"}),
    削除された他の列 = Table.SelectColumns(取引先名の展開,{"Id", "Name", "GBCArea__c", "GBCCountry__c", "GBCorgChoice__c", "GBCJU__c", "クライアント/Client", "レコードタイプ名"}),
    #"名前が変更された列 " = Table.RenameColumns(削除された他の列,{{"Id", "案件 ID/Item ID"}, {"Name", "案件名"}, {"GBCArea__c", "地域"}, {"GBCCountry__c", "市場"}, {"GBCorgChoice__c", "部署名"}, {"GBCJU__c", "事業(業務)区分"}}),
    案件ID正規化 = Table.TransformColumns(#"名前が変更された列 ", {{"案件 ID/Item ID", each if _ <> null then Text.Start(_, 15) else _, type text}}),
    重複を削除2 = Table.Distinct(案件ID正規化, {"案件 ID/Item ID"})
in
    重複を削除2
```
- `Raw YTD`/`案件_Dim`/`市場_Bridge`/`事業区分_Bridge`/`地域_Bridge`: いずれも`SF案件リスト`参照・新列名に切り替え済み。
- `SF案件リスト_旧Excel`: まだ削除していない(切り戻し用に残置)。
- `検証_SF案件リスト件数比較`/`検証_クライアント空欄診断`/`SF案件リスト_SF_TEST`: **未削除のまま**(今日は合計金額の異常発覚で数字確認どころではなくなったため後回しになった)。次回、上記の未解決問題1・2を解決してから削除する。

### 次回の進め方
1. 上記「未解決の問題」1(合計金額の水増し原因特定)を最優先で調査・修正。
2. 問題2(ランキングチャートのスライサー不反応)を調査。
3. 両方解決したら`部署`/`地域`/`市場`/`事業区分`スライサーの値一覧、他ページ(`設定見込_案件別内訳`等)への影響も再確認。
4. 検証用クエリ群を削除して完了。
