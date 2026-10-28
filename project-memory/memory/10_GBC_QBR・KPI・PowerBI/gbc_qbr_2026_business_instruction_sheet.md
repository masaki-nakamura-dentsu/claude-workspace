---
name: gbc-qbr-2026-business-instruction-sheet
description: "【GBC】26年度業務指示書 (annual KGI/KPI tracking workbook) — structure, Q2 update methodology, and the GBC実績・見込数字 reference file's data-quality issues found while updating it"
metadata: 
  node_type: memory
  type: project
  modified: 2026-09-06T07:23:36.086Z
  originSessionId: cc64e5ab-3b2b-493d-9622-597e1ccdd273
---

Follow-on to [[qbr_0708_rollback_tableau]], different task: updating `【GBC】26年度業務指示書_20260727.xlsx` (path: `.../QBR_2026Q2/`) with FY26 Q2 (April–June) actuals. This is GBC's annual KGI/KPI scorecard against the department's 示達 (assigned budget/targets), tracked quarterly.

## Workbook structure (per-checkpoint sheets)
Each fiscal year has one sheet per checkpoint: `FYxx Q1進捗` (Q1 only), `FYxx Q1-2進捗` (cumulative H1/上期, called "Q2進捗" for FY26 — Masaki's own shorthand, same cumulative-H1 role), `FYxx Q1-3進捗` (cumulative 9mo), `FYxx Q1-4実績` (full year). Each has the same row layout:
- Row3 KGI: 売総予算の達成 (CAS/設定売総 vs 示達予算)
- Row4 KGI: 貢献利益予算の達成 (= 売上総利益 − 人件費 − 営業費 − MSF − 減価償却)
- Row5 KPI: 貢献売総10%増 (グループ売総×GBC貢献度 attribution revenue)
- Row6 KPI: dentsuプロダクト・サービス実施件数
- Row7 KPI: グローバル人財育成 (text status, no numbers)
- Row8 KPI: dJIBクライアント事業拡大 (dJIB売総予算)
Columns: I=年間目標, K=期内計画(target), L=期内実績(actual), M=`=L/K`計画比. Row5/6 also have P:S columns = Q1/Q2/Q3/Q4 incremental-share weights (sum to 1, derived from prior-year same-quarter actual÷prior-year full-year actual) — extend K5/K6 for a cumulative-H1 sheet via `=I5*(P5+Q5)` / `=P6+Q6` (sum the relevant quarters' shares), not just P5/P6 alone (which is Q1-only).

## Q2 (2026-07-27) update — data sources per row
- **Row3/4 (KGI)**: primary source is the GBC実績・見込数字 reference file (OneDrive `.../GBC戦略企画部_GBC設定実績・見込/`), sheet `進捗 対示達`, "累計" section (rows 12-15 for 売上総利益, rows 43-46 for 貢献利益) — pull the "6月" column for H1-cumulative. This file's `貢献利益` calc is itself a live formula chain: `='進捗対示達'!row9(売上総利益) - '営業費 '!row9 - MSF!row9 - '人件費 '!row9 - 減価償却!row9`, and row9 in each cost sheet is `実績＋見込`.
- **Row5 (貢献売総 KPI)**: 実績 = sum of `貢献実績+見込_COMBINED.xlsx`'s Actual-sheet rows tagged `確度="Actual"`, **summed with NO date/month restriction at all** — confirmed directly from the Tableau workbook `6. QBR_貢献実績+見込 V1.0.twb`'s calculated field: `IF [確度]="Actual" THEN [貢献売総] ELSE 0`. This matters because GM承認 can tag a *future*-dated row as already-confirmed/actual (e.g. Agoda, Acecook had future months pre-approved) — so "実績" here is a running total across the whole year, not "months elapsed so far." Do NOT use a `月<=6` filtered sum for this row — that undercounts. Final Q2 value used: 1,064,644.956(千円), giving 103.9% achievement vs the H1 target.
  - **【2026-09-06修正・要注意】** この節の"Actual-sheet"の`貢献売総`列は、当時は`Att.Rev(A)`(確度A列、GM承認と無関係に値が入る)ベースで構築されていた。だが2026-09-06の検証で、同僚のSalesforce直接検索による公式値(2026年=1,295,626,390円)との突合の結果、**QBRの「貢献実績(計上済)」として正しいのは`Att.Rev(計上)`(Attrib. Rev(Rec.)、GM承認と完全連動)列であり、Att.Rev(A)は誤り**と判明した(詳細・検証手順は[[qbr_powerbi_tableau_verification_20260906]])。上記の¥1,064,644,956(2026-07時点のQ2値)がAtt.Rev(A)ベースだったかAtt.Rev(計上)ベースだったかは未確認 — もしこの業務指示書の数値を今後更新する際は、必ずAtt.Rev(計上)ベースで再計算し、過去のこの値との整合性(または不整合の理由)を確認すること。「GM承認済み未来月を前倒しで実績扱いする」という運用思想自体は変わらないが、それを反映する列がAtt.Rev(A)ではなくAtt.Rev(計上)である点を混同しないこと。
- **Row6 (件数)**: from pipeline workbook's `KPIxxxx` sheet, `電通プロダクト/サービス` section, cell `C60`-equivalent (「26年実績」total for 局全体) — was 28 as of 0708 snapshot for Q2.
- **Row8 (dJIB)**: no source found this session; left blank. **User is obtaining this now (as of 2026-07-27) — check back for the number before considering this workbook "done".**

## GBC実績・見込数字 reference file — data-quality issues found and fixed (2026-07-27)
Canonical filename convention for this recurring per-quarter file: `GBC実績・見込数字（2026年度）_update<YYYYMMDD>（Q<n>終了時点）.xlsx` (matches prior years' `_final...` pattern), living in `.../GBC戦略企画部_GBC設定実績・見込/` (OneDrive root, not the `QBR作成` subfolder). The original `_update20260722（Q2終了時点）.xlsx` had **stale April-June data** in multiple sheets, discovered because Masaki noticed the 業務指示書 numbers looked off vs. the pipeline. Fixed version was saved as a new dated file, **`GBC実績・見込数字（2026年度）_update20260727（Q2終了時点）.xlsx`** (Masaki's own rename, replacing an intermediate `..._20260722（Q2終了時点）.xlsx_20260727.xlsx` I had produced) — **this is the current canonical file**; the untouched `_update20260722` original is kept alongside it, not deleted.
- `人件費 `/`営業費 ` sheets: row9 (実績＋見込) for G:I (Apr-Jun) were literally formulas `=G8`/`=H8`/`=I8` (i.e. just echoing the budget row, never updated with real data) — fixed using `2026パイプライン 0708.xlsx`'s own `営業費1-6`/`人件費1-6` sheets (which had genuine Apr-Jun actuals). Real MSF Apr/May/Jun (-85000/-85000/-87174) came from 荒川さん directly via Teams (no email/Teams search turned up MSF actuals — 荒川さん is the MSF owner, ask him directly next time).
- `サマリー（月別見込・予算）` sheet row7 (取設定/部門売上) and row8 (売上総利益/部門利益): Apr-Jun values were **wrong AND didn't even match** the equally-wrong Apr-Jun values hardcoded into `進捗 対示達`'s own row9 — i.e. two independently-stale, mutually-inconsistent sets of numbers in the same workbook. Fixed both from `Rev YTD_Pivot 0708` (売上総利益 grand-total row) and `社提出見込み数字0710` sheet (取金額 row) in the pipeline workbook, and **restored the broken formula link** in `進捗対示達`!G9:I9 back to `='サマリー（月別見込・予算）'!G8/1000` etc. (matching how Jan-Mar already worked) instead of leaving hardcoded stale numbers.
- **Confirmed Jan-Mar (Q1) data in this reference file was NOT stale** — matched pipeline exactly for both 取設定 and 売上総利益. The staleness is specifically an Apr-Jun/Q2-not-yet-synced issue, not a general data quality problem with the file.
- A dated copy `..._20260727.xlsx` was made before editing (per standing versioning rule); original untouched.

## CRITICAL bug: openpyxl corrupts xlsx files with formula-only cells on every save
Every file this session that was saved via openpyxl and contained formula cells with no cached value ended up with `<c ...><f>...</f><v></v></c>` — an **empty `<v></v>` tag**, which is invalid OOXML and makes Excel show "問題が見つかりました。回復しますか？" on next open. This is NOT a one-time glitch — **it recurs on every openpyxl save of the same file** (confirmed: re-saving the already-once-fixed 業務指示書 via openpyxl reintroduced the exact same 345 occurrences). Affected essentially every xlsx this session that used formulas (業務指示書: 345, GBC実績・見込数字: 668, Client Name_CAS_SF_FY22 TO DATE: 3693, 2026パイプライン 0708 highlighted copy: 1589). Files where I wrote literal computed values instead of formulas (貢献実績/貢献見込/COMBINED rollback files) were unaffected.

**Fix pattern** (must be re-applied after every openpyxl `.save()` on any file containing formulas without cached values, until a better workaround is found):
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
**Whenever editing an existing xlsx with openpyxl in this or any future project, run this fix immediately after every `wb.save()`** — don't wait for the user to report a broken-file dialog. Verify with a zip-level `<v></v>`/`<v/>` count = 0 before telling the user a file is ready.

When the user hit this and reported the Excel repair dialog, I could not drive Excel via AppleScript/System Events to auto-click "はい" — Terminal/osascript lacks Accessibility permission on this Mac and granting it requires a GUI System Settings action (didn't pursue further, see [[feedback_avoid_mfa_churn]]-style caution about not fighting permission walls). The user manually clicked "はい", let Excel self-repair, and re-saved — this is the reliable fallback: **when openpyxl corruption is suspected and my XML patch doesn't fully resolve it, ask the user to let Excel repair-and-resave rather than continuing blind XML archaeology.**

## Current status (2026-07-27, end of session)
`【GBC】26年度業務指示書_20260727.xlsx` (canonical filename, confirmed by user — the once-corrupted version was deleted, the Excel-repaired version renamed to this exact name) has rows 3-7 complete for Q2; row8 (dJIB) blank pending data from the user's ongoing conversation with the dJIB owner. Once that's supplied, this workbook is essentially done for the Q2 cycle.
