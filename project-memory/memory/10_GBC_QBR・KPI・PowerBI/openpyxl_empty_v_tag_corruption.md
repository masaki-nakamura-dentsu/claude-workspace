---
name: openpyxl-empty-v-tag-corruption
description: "openpyxl silently corrupts any xlsx it saves if the file has formula cells with no cached value — Excel then shows a 'repair this file?' prompt. Applies to any project, not just GBC."
metadata: 
  node_type: memory
  type: reference
  modified: 2026-09-02T07:37:42.924Z
  originSessionId: cc64e5ab-3b2b-493d-9622-597e1ccdd273
---

**Symptom**: after editing an .xlsx with openpyxl (setting cell values/formulas, `wb.save()`), the user opens it in Excel and gets "'...xlsx' の一部の内容に問題が見つかりました。可能な限り内容を回復しますか？" (repair prompt).

**Root cause**: for any formula cell that has no cached value (either a formula openpyxl itself just wrote, or a pre-existing formula whose cached result openpyxl doesn't preserve), openpyxl serializes it as `<c ...><f>...</f><v></v></c>` — an empty `<v></v>` element. This is invalid OOXML (a numeric-type cell's value tag must either be omitted or contain an actual number). Confirmed this recurs on **every** openpyxl save of the same file, not a one-off — re-saving an already-"fixed" file reintroduces it. openpyxl itself and zipfile-level checks won't flag this (`openpyxl.load_workbook` opens it fine, zip integrity is fine) — only Excel's stricter validation catches it.

**Fix** — patch immediately after every `wb.save()`, before considering the file done:
```python
import zipfile, shutil, re
def fix_empty_v(path):
    tmp = path + ".tmp_fix.xlsx"
    zin = zipfile.ZipFile(path); zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.startswith('xl/worksheets/sheet') and item.filename.endswith('.xml'):
            text = data.decode('utf-8')
            text = re.sub(r'(</f>)<v\s*/?>\s*</v>', r'\1', text)
            text = re.sub(r'(</f>)<v/>', r'\1', text)
            data = text.encode('utf-8')
        zout.writestr(item, data)
    zin.close(); zout.close()
    shutil.move(tmp, path)
```
Verify by counting `<v></v>`/`<v/>` occurrences across `xl/worksheets/sheet*.xml` — must be 0 before telling the user the file is ready.

**Workaround/avoidance**: writing literal computed values instead of formulas avoids the bug entirely (files edited that way this session were unaffected) — prefer that when the formula's result can be computed in Python anyway and live-formula linkage isn't essential.

**If the XML patch doesn't fully resolve the repair prompt**: don't keep guessing at other XML causes — ask the user to click "はい"/let Excel self-repair and re-save, then continue editing that Excel-repaired file. Confirmed this works reliably; I could not drive Excel's repair dialog via AppleScript/System Events myself (Terminal lacks Accessibility permission on this Mac, granting it needs a manual System Settings action — didn't push further on this, see [[feedback_avoid_mfa_churn]] for the general "don't fight permission walls solo" pattern).

First encountered/fixed during [[gbc_qbr_2026_business_instruction_sheet]] work, but this is an openpyxl library behavior — applies to any future project involving programmatic xlsx edits with formulas, not GBC-specific.

**New symptom found 2026-07-27 (not just Excel repair prompts)**: this same corruption also breaks **Tableau's excel-direct connector**, which reads cached formula values rather than live-recalculating (like openpyxl, unlike Excel itself). In `Client Name_CAS_SF_FY22 TO DATE.xlsx` (GBC QBR folder), the `List` sheet's `クライアント名（調整後）` column is formula-driven (`=SUBSTITUTE(SUBSTITUTE(ASC(A_row),"(株)",""),"株式会社","")`) and had **all 1,033 formula cells** missing cached `<v>` values — Excel recalculates and displays them fine on open (so a user visually inspecting the file sees no problem), but Tableau saw NULL for every one, cascading into a NULL-fallback bucket that Tableau then rendered as a garbage float (`9.88131e-324`, i.e. 2× the smallest denormalized double) instead of "Null" in a legend. Fix was identical to the standard one: open in real Excel, confirm correct values display, then Cmd+S (no edit needed) — this re-caches the formula results into the XML.

**Root of this specific recurrence**: `docProps/app.xml`/`core.xml` showed `Application: Microsoft Excel Compatible / Openpyxl 3.1.5`, `lastModifiedBy: ＡＩ コンシェルジュ Concierge Ai`, modified same-day — a separate automation tool ("AIコンシェルジュ") that Masaki doesn't directly control is periodically re-saving files in this GBC QBR folder via openpyxl, reintroducing this bug. **This will keep recurring** unless that tool changes its save method or someone re-saves via real Excel afterward each time. Worth proactively checking `docProps/app.xml` for `Openpyxl` whenever a QBR file behaves oddly in Tableau/Power BI.

**Folder-wide scan done 2026-07-27** (`.../GBC戦略企画部_GBC設定実績・見込/QBR作成/`, method: compare `data_only=True` vs `data_only=False` reads via openpyxl, count formula cells where the cached value is `None`): besides the `List`/`List - Project` sheets above (now fixed), also found missing-cache formula cells in `Prep_SalesforceAllRecord.xlsx` (19% of 123,960), `GBC CAS実績_FY22 TO DATE.xlsx`'s `Raw YTD` sheet (9% of 88,665 — but the money columns `売上総利益`/`売上金額`/`原価金額` and all key columns were almost entirely intact, only descriptive columns like `サービスカテゴリレベル1/2名`/`備考` were affected, so real dashboard impact was minimal), and `Prep_CAS X SF Crosstable.xlsx`'s `Check` sheet (100% of 1,910, likely a QA-only sheet). User re-saved all of these via Excel same day to clear the caches.

## CRITICAL — I (Claude) repeated this exact bug three days later, 2026-07-30, despite this memory existing
During a QBR troubleshooting session I edited `Prep_CAS X SF Crosstable.xlsx` and `Client Name_CAS_SF_FY22 TO DATE.xlsx` several times with openpyxl, ran the `fix_empty_v` patch above after each save (as the memory's "Fix" section instructs), and moved on. Several turns later the user refreshed Tableau and **most クライアント名 values had turned into literal `0`** across the whole `Actual List (Q)` table — not just the cells I'd intentionally changed. Root cause: **the `fix_empty_v` patch above only stops Excel's repair-prompt dialog — it does NOT restore a usable value for Tableau.** It deletes the empty `<v></v>` entirely, leaving formula cells with **no value tag at all**. Excel recalculates transparently on open (so a human never notices), but Tableau's excel-direct connector reads the raw stored `<v>`, sees nothing, and — worse than plain NULL — this can get inferred as a numeric column and rendered as `0` once enough cells in the sampled range are typeless. This happened to **every** formula cell in both files (thousands), not just the ones I touched, because `fix_empty_v` runs across the whole sheet XML.

**Corrected, complete procedure — both steps are mandatory, `fix_empty_v` alone is not a fix, it's step 1 of 2:**
1. `fix_empty_v` (above) immediately after `wb.save()` — this only prevents the invalid-XML repair-prompt error, nothing else.
2. **Force a real recalculation pass before telling the user the file is ready or before any Tableau refresh happens**, since openpyxl never recalculates and LibreOffice/soffice is not installed on this Mac (checked 2026-07-30) so `soffice --convert-to` isn't available as a headless option. Microsoft Excel.app **can** be driven for this specific purpose without Accessibility permission (the earlier "couldn't automate Excel" note above was specifically about clicking a *repair-dialog button* via System Events UI scripting, which does need Accessibility — this is different: telling Excel to open/save/close a file that's already valid XML needs only Apple Events/Automation permission, which was already granted on this Mac):
   ```bash
   osascript -e 'tell application "Microsoft Excel" to open (POSIX file "/absolute/path/to/file.xlsx")'
   sleep 10   # longer for bigger files (~7000 rows / ~1400 formulas took ~15s to be safe)
   osascript -e 'tell application "Microsoft Excel" to save active workbook'
   osascript -e 'tell application "Microsoft Excel" to close active workbook saving no'
   ```
   `calculate active workbook` as a separate explicit AppleScript command errors (`-50` parameter error, dictionary doesn't take a workbook argument that way) — don't bother with it; opening a workbook with automatic calculation mode (Excel's default) already recalculates it before you even issue `save`, so the plain open→wait→save→close sequence above is sufficient. Verify by re-checking `<f>...</f><v` (with a real value following) is present for previously-empty cells, and that the specific values you care about read back correctly via `openpyxl(data_only=True)`.

**Standing rule going forward**: any time `fix_empty_v` is applied to a file, immediately follow with the Excel open/save/close recalculation pass in the same turn — never leave a file in the "valid XML but no cached formula values" state, even briefly, since that state is invisible in Excel itself and only surfaces later as silent bad data in Tableau/PowerBI. Do not consider the file "done" until both steps are confirmed.

## Recurrence 2026-08-04: hit the exact same bug building [[gbc_smart_kinmu_automation]], caught before delivery this time

While building `make_gbc_cleansed.py` / `_infer_missing_juekisha.py` (a monthly pipeline that opens a large multi-sheet workbook via openpyxl, writes some cells, and saves), ran the same before/after diff this memory recommends (`empty_v` / `nonempty` counts per `xl/worksheets/sheetN.xml`) as a matter of habit before declaring the scripts done — good thing, because it would have shipped broken otherwise. Numbers: the real production input file's Format sheet had `nonempty=10499` cached formula values (N:W columns, ~1500 rows); after running it through my own script's `wb.save()`, the same sheet had **`nonempty=0`, `empty=16385`** — every single formula cell in the *entire* workbook lost its cache, not just the ~13 columns (A:M) the script actually touched. This confirms the memory's core claim in the strongest possible terms: openpyxl drops cached formula values workbook-wide on any `wb.save()`, regardless of which cells were edited.

**Fix packaged as a reusable module this time**: `_xlsx_recalc_fix.py` (in the GBC Smart-KINMU folder, but written generically enough to copy into any other project) exports `fix_and_recalc(path, wait_seconds=45)`, combining exactly the two steps this memory prescribes — `fix_empty_v_tags()` (the same regex patch) then `force_excel_recalc()` (the same open→sleep→save→close AppleScript sequence, wait time scaled up to 45s here because one sheet has ~30,000 rows). Verified end-to-end: `nonempty` on the Format sheet went from 0 back to 10492 (vs. the original 10499 — the ~7-row gap is real data differences, not leftover corruption), and a real downstream formula column (`W`, the pass/fail check) read back real 0/1 integers for all 816 data rows, not blanks or errors.

**Design decision worth remembering**: when a pipeline has *multiple* scripts that each independently open+save the same workbook via openpyxl (here: one script generates the file, a second script re-opens it to add more rows), call `fix_and_recalc` at the end of **every** script's own save, not just the last one in the chain — each `wb.save()` re-corrupts the whole workbook again, so relying on "the last script in the pipeline will clean it up" breaks the moment someone runs an earlier script standalone (which is a real, intended use case here, not hypothetical). The ~45s Excel round-trip per script is a acceptable cost for a monthly-cadence pipeline; don't try to skip it "for one of the two scripts" as a speed optimization.

## New gotcha 2026-09-02: `force_excel_recalc`'s AppleScript close can silently no-op, leaving stale cache on disk despite a "success" return

While running `_xlsx_recalc_fix.fix_and_recalc()` on `Prep_CAS X SF Crosstable.xlsx` (adding 59 rows, see [[qbr_crosstable_monthly_update_process]]), the function returned `ok=True` and printed the success message, but re-reading the saved file (`data_only=True`) showed **every** formula cell in the workbook — not just the new rows — had `None`/no cached `<v>` at all (confirmed via raw XML: `<f>LEN(C2)</f>` with no `<v>` following, for a row that pre-dated this session's edits). Checked `osascript -e 'tell application "Microsoft Excel" to get name of every workbook'` afterward and the file was **still open** in Excel — the `close active workbook saving no` step in `force_excel_recalc` had not actually taken effect, even though its own `subprocess.run` reported `returncode == 0`. Live cell values inside the still-open workbook were correct (queried via `value of range "G2406"` → `14.0`, matching expectation) — so Excel *had* recalculated correctly; the recalculated state just never made it to disk because the save/close sequence didn't complete as expected.

**Fix that worked**: manually re-ran just the last two AppleScript steps (`save active workbook` then, after a few seconds' pause, `close active workbook saving no`) as separate calls (not back-to-back in the same function without a pause) — this time the workbook actually closed (`every workbook` returned `missing value` after), and re-reading the file showed all formula cells correctly cached (row 2: `12,15` restored; new rows: `14,15` each).

**How to apply**: after calling `fix_and_recalc`/`force_excel_recalc` and it reports success, don't trust the return value alone for a file this important (esp. one Tableau reads by cached value) — verify by either (a) `osascript ... get name of every workbook` returns empty/doesn't include the target file (confirms it actually closed), or (b) re-open the saved `.xlsx` with `openpyxl(data_only=True)` and spot-check that a known formula cell (old and newly-added) has a real non-None value. If either check fails, just re-issue `save active workbook` + wait + `close active workbook saving no` again — a second attempt after the workbook has had more idle time tends to succeed. Consider adding a short `sleep` between save and close inside `_xlsx_recalc_fix.py` itself if this recurs.

**New sub-quirk found, not previously documented**: fixing the empty-`<v>` corruption doesn't guarantee every formula column resolves *correctly* — a formula with a **hardcoded VLOOKUP range that doesn't reach newly-appended rows** (e.g. `VLOOKUP(E12,'Juekisha Table'!$E$3:$G$477,...)` when a new row was appended at 478) will legitimately evaluate to `#N/A` after a real recalculation, and that's *correct* Excel behavior, not a caching bug — don't misdiagnose a hardcoded-range limitation as the same empty-`<v>` issue just because both surface as "wrong-looking values after openpyxl edits." Distinguish them by checking whether the cell has a real formula error (`#N/A`, computed by Excel) vs. a missing/empty `<v>` tag (pre-recalculation artifact) in the raw XML.
