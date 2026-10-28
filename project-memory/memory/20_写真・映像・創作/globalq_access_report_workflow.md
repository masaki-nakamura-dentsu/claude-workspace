---
name: globalq-access-report-workflow
description: "How to generate the monthly Global Q access analysis PowerPoint report (replaces the old ChatGPT workflow), including the exact validated PV/UU aggregation logic"
metadata: 
  node_type: memory
  type: project
  originSessionId: 71257cc8-6d8f-4204-93b2-ab49e03b1b86
  modified: 2026-09-08T06:31:12.173Z
---

**Correction (2026-09-08): actual folder path.** This report's folder is NOT directly under the Dropbox root's "中村正樹" top level — it's nested under `中村正樹/Work共有作業系/戦略企画部/Global Q/`. Full path: `Global Q/11_アクセス分析レポート/アクセス分析レポート/` (scripts, category_master.xlsx, and all past pptx outputs live there). If a `find`/`ls` at the top level doesn't show "Global Q", look under `Work共有作業系/戦略企画部/` before assuming the folder moved or is unsynced.

Since 2026-07-13, the monthly Global Q アクセス分析レポート (previously built via a custom ChatGPT with a long instruction prompt) is built by Claude Code using a reusable Python pipeline, not manually in ChatGPT anymore.

**Why:** User wants the numbers to never drift from what Tableau shows (Tableau is the source of truth the org already trusts), and wants this handed off to Claude going forward instead of re-prompting ChatGPT each month.

**How to apply:** When asked for a new month's Global Q report, reuse the script setup below rather than re-deriving the methodology from scratch or trusting the old ChatGPT prompt's filter description (it is out of date — see below).

## Key files (all reusable month to month)

- `scripts/aggregate.py` and `scripts/build_report.py` — under `Global Q/11_アクセス分析レポート/アクセス分析レポート/scripts/` (Dropbox). `aggregate.py` has the validated PV/UU filter logic and all metric functions (top content, categories, frequency, domain, department, weekday×hour heatmap). `build_report.py` clones the previous month's pptx as a template and swaps in new numbers/charts/text, preserving the established 12-slide design.
- `scripts/category_master.xlsx` — the real Tableau category lookup (ObjectId → 大分類/中分類, 5,857 rows), extracted from inside the Tableau `.twbx` package (`Data/LogFiles 1/ページカテゴリー突合用.xlsx`, sheet `突合用`). This is the authoritative category taxonomy — do not invent categories from filenames/URLs like the old ChatGPT prompt did.
- Raw monthly source data: `/Users/d14461/Library/CloudStorage/OneDrive-電通/Log_globalonedentsu/globalonedentsu_AuditLog_PowerQueryとデコード処理_{year}年{month}月分.xlsx` (already decoded: 氏名/所属/メールアドレス/ItemType/SourceFileExtension columns).
- Yearly merged CSVs (faster load, usually a month or two behind): `Global Q/7_アクセスログ／メール設定/LogFiles_ChatGPTに読み込ませる用のデータ/統合Logデータ/globalonedentsu_AuditLog_{year}_merged.csv`. `aggregate.load_month()` checks this first and falls back to the standalone monthly file.
- The Tableau workbook itself: `Global Q/7_アクセスログ／メール設定/LogFiles:TableauFile/GlobalQ集計*.twbx` — a packaged workbook whose `Data/` folder literally contains all the monthly PowerQuery-decoded Excel files (not a Hyper extract), so the raw data is authoritative and directly matches Tableau's own source.

## Validated PV/UU definitions (confirmed exact match, 6/6 months: 2026-01 through 2026-06)

Reverse-engineered by unzipping the `.twbx` and reading the `<filter>` elements in the embedded `.twb` XML (this is far more reliable than reasoning from the old ChatGPT custom-instructions text, which turns out to be an approximation the user's previous ChatGPT sessions used and does NOT exactly match Tableau).

- **PV** = row count after excluding the 8-person editorial staff list by 氏名 (see below, 19 name-variant strings incl. brackets/case) AND keeping only rows where `SourceFileExtension` (lowercased) is one of: aspx, csv, docx, ds_store, htm, html, js, log, mp4, msg, pdf, pptx, spcolor, spfont, sptheme, txt, xlsm, xlsx, zip — OR the extension is null (real PageViewed rows). No dedup of FileAccessed vs FileDownloaded, no separate exclusion of AllItems.aspx/AllPages.aspx — Tableau counts those too.
- **UU** = distinct メールアドレス count after excluding the same 8-person list by 氏名 only — **no extension filter applied** (broader than PV; e.g. image/theme file hits count toward UU but not PV).
- **Excluded editorial staff (8 people, not 6!):** 榎本文美子, 佐藤文, 松村憲一, 西山隆, 中村正樹, 中牧莉香, 百々奈菜子, 福田麻矢. The old ChatGPT instruction prompt only listed 6 names (missing 松村憲一 and 西山隆) and separately hand-waved a "Global Q運用アカウント" email exclusion that doesn't actually appear in Tableau's filter — that was the previous month's (May) report's workaround for an imprecise match. The 8-name list above is exact and needs no such workaround.

If the exclusion list or extension whitelist ever needs re-verification (e.g. numbers stop matching Tableau), re-extract `<filter>` blocks from the `.twb` inside the latest `.twbx` rather than guessing.

**Heatmap shape-name gotcha (found 2026-08-05, fixed in script):** `build_report.py`'s slide-10 step originally looked only for a shape named `オブジェクト 6` (the original OLE-embedded Excel object from the oldest template). But once a month's report has been generated by this script, the heatmap becomes a native pptx `Table` shape named `Table 6` instead — so using that generated pptx as next month's `--template` made the old lookup raise `KeyError`. Fixed by trying `オブジェクト 6` first, falling back to `Table 6`. This is now permanent in the script, but worth knowing if the shape name ever changes again after further edits.

## Report structure

Now a 14-slide format (was 12 through the 2026-06 report; 2 slides added 2026-08-05, see below): cover, summary, current-month daily trend, YTD monthly trend (line chart, values for the trend take the known/confirmed monthly PV/UU rather than re-deriving from raw logs each time), **月別PV推移(全期間)**, **月別UU推移(全期間)**, top content (current month), top category (current month), access frequency distribution, domain breakdown, department ranking (rule-based grouping of free-text 所属, inherently approximate), weekday×hour UU heatmap (rendered as a native colored pptx table, not an embedded OLE Excel object — simpler and equally editable), まとめ, Appendix. The "Global Q更新ニュース" text boxes on the trend slide (curated site update headlines) are NOT derivable from the access logs — no automatable source was found in the Global Q Dropbox folder; leave a note that they need manual addition rather than fabricating content.

**Full-history trend slides (added 2026-08-05):** User asked, after seeing Tableau's own since-launch PV line chart and UU bar chart (2019-11〜present), to add the equivalent to the pptx report. Implemented as a permanent part of the pipeline, not a one-off:
- `aggregate.py`: new `full_history_monthly(upto_year, upto_month)` — walks every month from `FIRST_YM = (2019, 11)` forward using the existing `load_month`/`apply_filters` (same validated logic), returns an `OrderedDict[(y,m)] -> (pv, uu)`. Months with no source file (e.g. 2025-08, which is `.xlsm` not `.xlsx` so `_find_monthly_raw_file`'s glob misses it) are silently skipped — this matches a real gap Tableau's own chart also shows (its "1個のNULL" annotation), so it's a genuine data gap, not a bug worth fixing unless the user asks for that month specifically.
- `build_report.py`: new `ensure_history_slides()` called from `main()` right after the existing YTD-slide block. It searches all slides for shapes named `HistPV Chart` / `HistUU Chart`; if found (i.e. this month's template already had them, from last month's run) it just calls `update_chart` + retitles in place; if not found (first time, e.g. this month building off the old 12-slide `..._06.pptx` template) it builds two brand-new slides from scratch via `build_history_slide()` — cloned styling (not cloned XML) matching the existing single-full-width-chart template (department slide): title `Yu Gothic 20pt bold #1F4E79`, subtitle `9pt #666666`, divider line `#D9E2F3` 1pt connector, chart color `#4472C4` (same accent blue used everywhere else in the deck), bullets `10pt #333333`. PV renders as `XL_CHART_TYPE.LINE` (no markers, matches Tableau's own line style), UU as `XL_CHART_TYPE.COLUMN_CLUSTERED` (matches Tableau's bar style). New slides are inserted right after the YTD slide via direct `sldIdLst` manipulation (`move_slide()`) so they land at position 4/5 (0-indexed) every time. Category labels are blanked except at January of each year (`"2020年"` etc.) to avoid 80-month tick-label clutter, mirroring how Tableau itself only shows the year label once per year.
- Chose "extend the pipeline" over a one-off script specifically so next month's run (using this month's 14-slide output as `--template`) automatically regenerates these two slides with one more month of data, no extra steps needed — consistent with how the rest of the deck already works.
- Bug caught during first build: initial bullet text on the UU slide read `history[peak_uu_ym][0]` (the PV value) instead of `[1]` (the UU value) when reporting "past peak UU month" — a copy-paste-from-PV-bullet mistake. Fixed before delivering; worth double-checking bullet text against the actual chart values whenever touching these two slides again.

## Standing rule (added 2026-08-05): copy the month's 2 raw log files to the Tableau folder every time

User wants the two source files used for each month's report also copied to `Global Q/7_アクセスログ／メール設定/LogFiles:TableauFile` every time a report is built, so the `.twbx` workbook there can be opened directly against them (Tableau expects its own copy in that folder, separate from the OneDrive source and separate from the `統合Logデータ` merged-CSV folder used by this pipeline). The two files for a given month:
1. `globalonedentsu_AuditLog_{prev-month-end}_{month-end}.xlsx` (e.g. July 2026 → `globalonedentsu_AuditLog_2026-06-30_2026-07-31.xlsx`) — the raw undecoded audit-log export, named by date range.
2. `globalonedentsu_AuditLog_PowerQueryとデコード処理_{year}年{month}月分.xlsx` — the decoded file already used by `aggregate.load_month()`.

Both live in `RAW_LOG_DIR` (OneDrive `Log_globalonedentsu`). Implemented as a permanent pipeline step, not a manual reminder:
- `aggregate.py`: `raw_log_source_files(year, month)` computes the date-range filename from calendar month-end arithmetic and falls back to a glob-by-end-date if the exact name doesn't match; also reuses `_find_monthly_raw_file()` for file 2. `copy_raw_logs_for_tableau(year, month)` copies both (via `shutil.copy2`) into `TABLEAU_LOG_DIR`, skipping any file that already exists there with the same size (idempotent — safe to re-run `build_report.py` without duplicating work).
- `build_report.py`'s `main()` calls `ag.copy_raw_logs_for_tableau(year, month)` right after `prs.save()`, printing which files (if any) were newly copied.
- Verified for the July 2026 run: both files already matched byte-for-byte what was in the Tableau folder (user had evidently already placed them there before asking), so the copy step correctly no-op'd. Next month's run will pick up new files from OneDrive automatically with no extra steps.

Known monthly PV/UU ground truth so far (dict in `build_report.py`, extend each month): 2026-01: 9,953/1,421・02: 9,526/1,258・03: 7,751/1,262・04: 14,075/1,407・05: 16,012/2,581・06: 17,855/1,677・07: 13,442/2,522(peak day 2026-07-15, YTD PV 88,614 / UU合計12,128)・08: 6,181/1,342(peak day 2026-08-06, YTD PV 94,795 / UU合計13,470; computed via `aggregate.py` itself, no Tableau screenshot supplied — cross-check against Tableau if one surfaces later). August PV dropped sharply vs July (13,442→6,181) — genuine drop confirmed by checking the raw source file covers the full 2026-08-01〜08-31 range (31 unique days, no partial-month data issue), not a pipeline bug.

・09: 8,650/2,100(peak day 2026-09-10, YTD PV 103,445 / UU合計15,570; aggregate.py算出、Tableau画面との突合は未実施)。9月は「OOH海外事例 2026年7月.pptx」が単独でPV 3,148/UU 1,223(月間PVの約36%)、9/10〜11の山も同資料の配信によるもの。この資料はcategory_masterに未登録で「その他(未突合)」に入る。

Report file: `GlobalQ_access_report_2026_09.pptx` generated 2026-10-06 from the `..._2026_08.pptx` template. Earlier: `GlobalQ_access_report_2026_08.pptx` generated 2026-09-08 from the `..._2026_07.pptx` template.

## Bug found & fixed 2026-09-08: hardcoded slide indices broke once the template itself had the 2 history slides

`build_report.py`'s `main()` originally used literal slide-position indices (`slides[4]`, `slides[5]`, ... `slides[11]`) for the "人気コンテンツ" through "Appendix" slides — indices that were only valid for the *original* 12-slide template layout. Once `ensure_history_slides()` (added 2026-08-05) started **updating history slides in place** rather than inserting them (because the template — last month's own output — already contained `HistPV Chart`/`HistUU Chart` shapes at physical positions 4/5), every slide from "人気コンテンツ" onward was now actually 2 positions further into the deck than the hardcoded index expected. This didn't surface during the July run (template was still the old 12-slide June file, so slides were freshly *inserted*, not updated in place — first time this code path had ever been hit) — it only broke on this, the *first* run using an already-14-slide template as `--template`, immediately throwing `KeyError: 'Text 1'` on `find_shape(slides[4], "Text 1")` (which was actually the HistPV slide, not 人気コンテンツ).

**Fix (permanent, in `build_report.py`):** `ensure_history_slides()` now returns `True`/`False` (pre-existing vs. freshly-inserted), and `main()` computes `off = 2 if hist_pre_existing else 0`, applying it to every subsequent hardcoded slide index (`slides[4 + off]` through `slides[11 + off]`). This makes the script correctly handle both cases: first-ever upgrade run (old template, slides inserted, off=0) and every normal month going forward (template already 14-slide, in-place update, off=2). Verified via full 14-slide qlmanage QA of the August output — all slides populated with correct August data.

**Since this bug could only ever trigger once** (the first time a 14-slide pptx became next month's template) and is now fixed, no further action needed — but if slide content ever looks shifted/wrong again after future template-structure changes, suspect a similar hardcoded-index vs. dynamic-insertion mismatch first.

## 2026-10-06: decoding step automated (`scripts/decode_raw_log.py`)

For Sept 2026 only the raw export (`globalonedentsu_AuditLog_2026-08-31_2026-09-30.xlsx`, AuditData JSON column) arrived in OneDrive; the PowerQuery-decoded file did not exist. Reverse-engineered the PowerQuery step and validated against Aug 2026: **all 16 columns, all 13,364 rows identical**. Rules: drop rows where メールアドレス == `app@sharepoint` (NOT "氏名 is null" — that guess was wrong, it drops 110 too many); expand Id/SiteUrl/ObjectId/ItemType/ListId/ListItemUniqueId/SourceFileExtension/SourceFileName from the JSON; AuditData → "[Record]"; add `SourceFileName(decode)` = urllib unquote. Sheet name `AuditLogs`. Monthly flow is now: `python3 decode_raw_log.py --year Y --month M` (skips if decoded file exists) → add (PV,UU) to `KNOWN_MONTHLY` in build_report.py → `build_report.py --template <prev month pptx>`.

**Template-text gotcha:** build_report.py's bullet text contains canned interpretations that can be wrong for a given month (Sept: "コンテンツ人気というより利用実態の偏り" for a peak that was actually a content distribution; "PVの単純Top1は一覧ページ「<pptx名>」"; "Tableau表示値と完全一致を確認済み" even when no Tableau check happened; "前月比+N" unlabeled (it was UU)). Always read every bullet after generation and fix against the actual numbers before delivering.
