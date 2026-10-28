---
name: power-automate-gotchas
description: "Growing list of real Power Automate platform limitations and gotchas (Set Variable self-reference, text+chip string-template trap, literal-only booleans, 5000-item array cap, SharePoint internal vs display field names, designer-UI edits that silently fail to persist, package import breaking webhook-style trigger registrations, select/filter rejected at runtime). Check before building/debugging any Power Automate flow."
metadata:
  type: reference
  originSessionId: session-2026-07-26-calendar-pagination
  modified: 2026-09-28T10:25:00.000Z
---

Discovered 2026-07-25/26 while building a Do-until pagination loop for [[continuous_data_capture_setup]]'s calendar sync flow. Not calendar-specific — applies to any Power Automate cloud flow. Check this before assuming a "cannot update variable" or "invalid type" error is a data problem; it's very likely one of these two platform quirks instead.

## 1. "Set variable" (変数の設定) cannot self-reference the variable it's updating

Writing `union(variables('X'), newData)` or `add(variables('X'), 1)` as the value of a "変数の設定" action that targets `X` itself fails at save time.

- For numbers: explicit error `Self reference is not supported when updating the value of variable 'X'`
- For arrays/objects: **same root cause, but a much more confusing error** — `The variable 'X' of type 'Array' cannot be initialized or updated with value of type 'String'`. This misled us for a long time; there was nothing wrong with the data, the self-reference itself is what's rejected.

**Fix**: use the dedicated non-self-referencing actions instead of Set Variable:
- Numbers → **「変数の値を増やす」(Increment variable)** — has its own 名前/値 fields, no self-reference needed
- Arrays → **「Apply to each」+「配列変数に追加」(Append to array variable)** — iterate the new items and append one at a time; also not self-referencing under the hood

## 2. Mixing hand-typed text with a dynamic-content chip in the same field builds a STRING TEMPLATE, not an expression

If you type literal text (e.g. `select(`) into a field, then insert a dynamic-content chip via the picker, then type more literal text (e.g. `, removeProperty(item(), 'body'))`), Power Automate does **not** evaluate this as a function call. It treats the whole field as a string template — the literal text stays literal, and the chip gets JSON-stringified and concatenated in place. Confirmed by inspecting a Compose action's raw output: it began with the literal characters `select([{...` — the word "select(" was never parsed as a function, just echoed back as text.

This is almost certainly the actual root cause of most "cannot update with value of type String" errors during this session, not any data-size or type problem.

**Fix — two safe patterns, never mix them**:
- (a) A field containing **only a bare chip, nothing else typed** — totally fine, this is normal usage (e.g. "現在のアイテム" alone in an Append-to-array-variable's 値 field)
- (b) A field containing an **entire hand-typed expression with zero chips**, referencing other actions via `outputs('ActionName')?['body/value']` or `body('ActionName')?['value']` — typed as pure text

For (b): first rename the target action to a short ASCII name via 「…」→「名前の変更」(e.g. `GetCalendarView` instead of the default `イベントのカレンダー ビューの取得 (V3)`) — referencing an un-renamed action with spaces/parens/Japanese in its name by hand is itself error-prone (wrong escaping → "無効な参照が含まれています" / invalid reference errors). Also: click into the field and explicitly invoke the ⚡/fx expression-mode icon before typing — a plain textbox can otherwise just store what you type as a literal string without ever evaluating it as a formula (a related trap: typing a formula directly into a Compose action's 入力 field without opening fx mode caused the output to echo back the literal typed text verbatim, unevaluated).

## 3. Boolean variables: never assign a computed expression directly

Even a syntactically-correct `equals(x, y)` assigned directly as a "変数の設定" value for a Boolean-typed variable can get rejected at save time with `有効なブール値を入力してください` (please enter a valid boolean value), for reasons that were never fully isolated (possibly a design-time type-inference limitation, possibly related to #2 above compounding).

**Fix**: use a **「条件」(Condition)** action to branch on the comparison, and in each branch, assign the variable a **literal** `true` or `false` (typed as plain text, not a formula) — never a computed expression.

## 4. Array variables cap out at 5000 items — hard limit, not a bug

Even after fixing #1 (using Append-to-array-variable instead of self-referencing Set Variable), accumulating a large paginated result into a single array variable will eventually fail with:

`The number of array items in variable 'X' reached the limit: maximum '5000' and actual '5000'.`

This is a real, undocumented-until-you-hit-it platform ceiling — nothing to do with data correctness. Hit this in the calendar backfill when one date-range chunk turned out to contain 8000+ events.

**Fix**: don't accumulate at all. If the end goal is writing data out (to a file, a table, etc.), write each page **as soon as it's fetched**, inside the pagination loop, rather than building up one big in-memory array and writing once at the end. Concretely for a Do-until pagination loop: move whatever "create file"/"write row"/etc. action you have to *inside* the loop, operating on just that page's data (a bare chip reference to the current page's array, per rule #2 above), instead of on an accumulator variable. If downstream consumers need one combined dataset, merge the resulting multiple output files in a *separate* step/script outside the flow (this is exactly what `sync_calendar_export.py` does — it already processed "however many snapshot files are pending" per run, so switching from 1 file/run to dozens of files/run required zero changes on that side).

This also **simplifies** the flow, not just works around a limit: no accumulator variable, no Apply-to-each nesting — just Get-page → write-page → increment/loop.

## 5. Self-reference restriction also blocks string-concatenation accumulators inside Apply to each — even with concurrency forced to 1

Re-confirmed 2026-08-01 while building [[powerautomate_attendance_summary_project]]: a "変数の設定"(Set Variable) inside an "Apply to each" doing `concat(variables('まとめ本文'), ..., item()?['氏名'], ...)` to build up a summary string one item at a time hit the exact same `Self reference is not supported when updating the value of variable` error as rule #1 above — this time for a **string**, not a number/array. Explicitly turning on the loop's "コンカレンシー制御"(concurrency control) and setting it to `1` (as the loop's own settings dialog suggests doing) did **not** fix it.

**Better fix — skip the loop entirely**: when the end goal is "one string built from formatting each item in an array", use a single expression combining `select()` (map each item to a formatted string) and `join()` (concatenate with a separator), with zero loop and zero variable self-reference:

```
join(select(outputs('GetItemsAction')?['body/value'], concat(item()?['氏名'], '　開始(', coalesce(item()?['始業形態'], ''), ') ', coalesce(item()?['始業時刻'], ''))), '<br>')
```

This is simpler than the array-append workaround in rule #1 (no Apply-to-each nesting at all) and should be the default first choice whenever the accumulation target is a formatted string, not a raw array of objects.

## 6. Renaming an action breaks hand-typed `outputs('OldName')` references elsewhere — silently, until save

Renaming an action via 「…」→「名前の変更」only auto-updates references that were **inserted via the dynamic-content picker** (chips). Any reference typed by hand inside an `fx` expression — in another action's field, or inside a sibling **Condition's own comparison expression** — keeps the literal old name as plain text and does not get updated. The flow still looks fine in the designer until you save, then you get `'Xの入力パラメーターに対して、Yへの有効な参照を含めるには、直してください'` (or, if the checker doesn't catch it immediately, a save-time `InvalidTemplate` error naming the stale action).

The trap compounds because an action can be referenced from **multiple, non-obvious places** — not just the field that visibly needs its output, but also a `Condition` action's own left-hand comparison expression that happens to use `length(outputs('ActionName')?['body/value'])`. Missing even one reference produces a fresh error after each partial fix, making it look like the fix "isn't working."

**Fix**:
- Before renaming an action that's already referenced elsewhere, grep the exported flow's `definition.json` for every occurrence of `outputs('OldName')` (or `body('OldName')`) first, and fix all of them in the same pass.
- When manually retyping a Japanese action name inside an expression, copy-paste the exact name (from the rename box) rather than retyping it — full-width vs half-width space mismatches from IME input are a common invisible cause of "invalid reference" errors that look identical to a genuine stale-name bug.
- If an action is referenced from 3+ places and manual fixup is getting error-prone, it's often faster to just revert the rename and leave that one action's name as-is, rather than keep chasing every reference by hand.

## 7. "コードの表示"(Peek code) is view-only in this tenant — can't paste JSON back in

Confirmed 2026-08-06 while updating [[gbc_business_trip_management_powerbi]]'s approval flow: unlike some Power Automate tutorials assume, this tenant's Peek code panel on an action lets you view the raw JSON but not edit/paste it back. Don't propose "add a placeholder action, then paste replacement JSON via Peek code" as a shortcut here — it will not work. Fall back to describing each field (To/Subject/Body) in terms of the dynamic-content picker, ideally telling the user to copy-paste body text from an already-working sibling action (dynamic-content chips survive copy/paste between text boxes in the designer) rather than re-picking every field by hand.

**Useful related technique that DOES work**: exporting a flow as a package (⋯ → エクスポート → パッケージ (.zip)) and having it shared back gives a `definition.json` inside the zip that's fully readable (plain Logic-Apps-schema JSON, no login/Desktop needed) — this is the fastest way to see a flow's *exact* current structure (action order, hard-coded values like a fixed approver email, field-ID mappings) instead of asking the user to screenshot every step. Same trick works for `.pbix` files: they're plain ZIP archives (PBIR-format reports have human-readable `Report/definition/**/*.json`; the `DataModel` itself is a compressed VertiPaq binary and not readably, but report/visual structure is fully inspectable this way even with no Power BI Desktop on Mac).

## 8. Typing a function expression directly into a Condition builder's value field saves it as a STRING LITERAL, not an evaluated formula

Confirmed 2026-08-11 while building [[gbc_business_trip_management_powerbi]]'s reminder loop. Unlike a plain text field, a Condition (条件) action's comparison value box *looks* like it accepts a typed formula (e.g. `or(equals(dayOfWeek(utcNow()),0),equals(dayOfWeek(utcNow()),6))`), and it even renders back to you inside the box without error. But checking the read-only コードビュー afterward shows it was saved as `"equals": ["or(equals(...))", ""]` — a quoted string, never evaluated — and the flow checker flags it as `有効な条件ステートメントを入力してください`.

**Fix**: click the small **fx icon** at the field's edge (distinct from the ⚡ dynamic-content icon) to open the dedicated expression-editor popup, type the formula there, and click **「追加」(Add)**. Only then does コードビュー show it correctly `@`-prefixed (e.g. `"@or(equals(...))"`), confirming it's a real expression. This is a stricter version of rule #2 above — that rule covers plain hand-typed-text fields; Condition value fields need the fx popup specifically, plain typing silently fails validation instead of just working.

## 9. Parallel branches sharing a fork point don't guarantee execution order — even if one references the other's output by name

If two actions both have `runAfter` pointing at the same upstream action (i.e. they're siblings at a fork, rendered as parallel lanes in the new designer), one branch referencing `outputs('OtherBranchAction')` in a hand-typed/chip expression will often still *look* fine (Condition fields don't validate this — see rule #2/#6), but a stricter UI-bound field like a `For each`'s "前のステップから出力を選択します" (foreach source, a literal previous-step picker, not a free-text field) will hard-error with `パラメーターが無効です — '前のステップから出力を選択します' は必須です`, because the picker only allows selecting from actions that are structural ancestors, not parallel siblings.

This happened after replacing a blocking "Start and wait for an approval" with "Create an approval" + "Wait for an approval completion", where the flow's original downstream `Condition` (approve/reject email logic, containing a `For each` over approval responses) got accidentally wired as a *third parallel sibling* of the new Wait action instead of running after it — a real race condition, not just a lint nit, since the Condition's own `outputs('Wait_action')?['body/outcome']` check could evaluate before that action even finished.

**Fix**: open the downstream action's **設定(Settings) tab → この後に実行する(Run after)** section → **+ セクションを選択する** → check the actual action it should wait for (and optionally uncheck the old fork-point dependency, since it's now transitively satisfied). This is the only reliable way to add/change a `runAfter` structural dependency via the UI — there's no drag-and-drop equivalent that reliably works via browser automation (mouse-down-move-up on an action header just pans the canvas instead of grabbing the node). After fixing, verify via コードビュー that the JSON `"runAfter"` key names the correct action, and re-check that any strict UI-bound fields (like For each's source picker) that were erroring now resolve without needing the rule-#2-style manual-text-typing workaround.

## 7. `item()?['表示名']` also needs the SharePoint internal field name — not just `$filter`, and the designer UI can silently fail to persist a fix to this specific kind of field

Rule #6 above already covers `$filter` OData query strings needing the internal name (e.g. `OData__x65e5__x4ed8_` for a column displayed as `日付`). The **same requirement applies to `item()?['...']` property access** anywhere an item from a SharePoint "Get items" result is read in an expression — inside a Condition's comparison, inside `select()`/`filter()`, etc. Using the display name (`item()?['終業時刻']`) silently evaluates to `null` for every row (not an error), which is a nasty failure mode: `empty(item()?['終業時刻'])` is always `true`, so a completion-detection condition like "did everyone finish" never fires, with no error anywhere to point at it. Get the exact internal name from a working write action (`item/OData__x...` parameter keys in `項目の作成`/`項目の更新`) or from the raw JSON returned by "Get items", not from the display name.

**Separately, and more surprising**: while fixing this in [[powerautomate_attendance_summary_project]], one specific field — the left-hand comparison operand of a `条件` (Condition) nested inside an `Apply to each` — **would not persist** through the normal edit flow (open chip → 式 tab → edit in the Monaco editor → click 更新 → 保存), even though every step of that flow reported success (correct text visible before clicking 更新, panel closed cleanly, flow saved with "保存済み" and zero errors) and a *different* field (a `変数の設定` value elsewhere in the same flow) saved correctly using the exact same procedure. Re-exporting and inspecting the raw JSON after each attempt was the only way to catch this — the UI gave no indication anything was wrong. Repeated retries (4+ attempts, including scrolling into view before clicking, waiting longer, moving the mouse away before the click) all failed to persist for this one field specifically.

**Working fix**: export the flow's package (「…」→ エクスポート → パッケージ(.zip)), edit `definition.json` inside it directly (plain string replacement of the broken expression), re-zip preserving the exact folder structure (`manifest.json` + `Microsoft.Flow/flows/manifest.json` + `Microsoft.Flow/flows/<guid>/{apisMap,connectionsMap,definition}.json`), then re-import via マイフロー → インポート → **パッケージのインポート (レガシ)** (not "ソリューションのインポート (Dataverse)"), upload the zip, confirm the existing flow resource shows インポートの種類 = **更新**, click インポート. This bypassed whatever the designer-UI bug was and the fix was confirmed present in a fresh export afterward. **When a designer-UI edit to one specific field refuses to persist across multiple careful attempts while other, similar edits in the same flow work fine, stop retrying the UI and go straight to the export→edit-JSON→reimport-as-update path** — it's more reliable and, for a single-line fix, actually less back-and-forth than continued UI trial and error.

**Token-cost note**: driving the designer UI via Playwright screenshots (open field → screenshot → click → screenshot → verify → screenshot...) is expensive — each screenshot is a full-resolution image read. The export/edit-JSON/reimport path needs almost no screenshots and is both cheaper and more reliable for anything beyond a trivial single-field tweak. Prefer it by default when Claude is asked to make the Power Automate edit directly (as opposed to guiding the user through the designer themselves, where this doesn't apply).

## 8. ⚠️ "パッケージのインポート(レガシ)" can permanently break a webhook-style trigger's external registration — even a byte-for-byte re-import of a previously-working export

**Unconfirmed root cause, but high-confidence based on reproduced symptoms** (2026-08-13, [[powerautomate_attendance_summary_project]]): a flow using the Teams connector's `TeamsCardTrigger` (`type: Request`, `kind: ApiConnection`, tied to a `CardTypeId`) stopped firing entirely after using 「パッケージのインポート(レガシ)」→ 更新 to push a JSON-edited fix. No errors anywhere — clicking the button in Teams produced zero reaction, and the flow's run history showed no new runs at all (not even failed ones), meaning the trigger itself was never being invoked.

Attempted fixes that did **not** work:
- Re-importing an *earlier, previously-known-working* export (from before the edit that supposedly broke it) as an "update" — still broken. This is the critical clue: if the JSON content were the problem, an old known-good export should have fixed it. It didn't, which points to something **outside the JSON** — most likely the trigger's Teams-side subscription/webhook registration — being what actually broke.
- Explicitly re-selecting "use existing connection" for both related connection resources during the import wizard (rather than leaving them as "select at import time").
- Toggling the flow off then on again.

**Working theory**: `TeamsCardTrigger`-style triggers likely register a subscription with Teams/Bot Framework at flow-save time through the normal designer save path (or through whatever original wizard provisioned the flow — this particular flow's origin was never established, see [[powerautomate_attendance_summary_project]]). A package import bypasses that registration step even though it writes an identical trigger definition into the flow, leaving the flow "on" and syntactically correct but never actually invoked.

**Recommended approach if this happens again**: do **not** reach for package export/import to fix or roll back a flow with this trigger type. Instead:
1. Prefer the designer's own in-place version history / restore-a-previous-save feature (if the flow has one — check 詳細/履歴) over export-then-reimport, since that keeps the flow as the same live resource rather than something resembling a delete-and-recreate.
2. If a single field's designer-UI edit won't persist (rule #7) but the trigger is this webhook style, weigh the risk: a JSON-edit-and-reimport might fix the one field but silently break the trigger's live registration in a way that isn't visible until someone actually tests it in production. For a **production flow already receiving real traffic**, this risk may not be worth taking for a single-field fix — consider leaving the field broken (with a documented workaround) rather than reimporting, or test the reimport-and-recovery cycle on a **copy** of the flow first.
3. As a last resort, recreating the trigger from scratch via whatever UI originally provisioned it (e.g. Teams' own "Workflows" app card-creation wizard) may be the only way to re-establish the external registration — but this is invasive and its blast radius on other flows/cards sharing the same `CardTypeId` is unknown.

**✅ Confirmed working fix (2026-08-13, d14461)**: none of the above three were actually needed. The real fix was much lighter — on the trigger action itself, open **「…」(more commands) → マイ コネクション (My connections) section** (not the flow-level "詳細 → 接続" panel's connection list, which only offers deleting a connection reference and had no visible effect on the trigger — the designer kept showing the trigger as still connected even after deleting it there). In the trigger's own "…" menu, under マイ コネクション: click **「+ 新しい接続を追加する」(Add new connection)** to create a genuinely new Teams connection resource for the same account (aicon@dentsu.co.jp), then click the newly created connection to select it for this trigger (replacing the old one), then save via the designer's normal **保存** button (never package import). This round-trips through the designer's real save path, which is exactly the code path theorized above to register the Teams-side webhook subscription. Verified: new runs started appearing in the 28-day run history within seconds of a real button press in Teams, on the very first attempt — no trigger deletion/recreation, no downstream reference rewiring, and the SharePoint connection was left untouched throughout.

## 10. `select`/`filter` (higher-order, `item()`-based collection functions) rejected at runtime with "function is not defined" — even with verified-correct syntax and data

Confirmed 2026-09-28 while rebuilding [[cas_setting_request_powerautomate_flow]]'s 宛先/BCC to read from a SharePoint Excel table instead of hardcoded strings. An expression like:

```
join(select(outputs('GetNotifyList')?['body/value'], item()?['メールアドレス']), '; ')
```

failed at runtime with `InvalidTemplate: Unable to process template language expressions ... 'The template function 'select' is not defined or not valid'` — even after:
- Verifying byte-for-byte (via flow package export → `definition.json`) that the stored expression has zero invisible/full-width characters, correct `@`-prefix, and balanced parens.
- Confirming (via the action's own successful run output) that the upstream data really is a plain array of objects with exactly the referenced keys (`メールアドレス` etc.) — not null, not mis-shaped.
- Trying the same expression first in `filter(...)` (same error, naming `filter` instead), then in a dedicated **Compose** action instead of "Initialize variable" (same error persisted) — ruling out both "wrong action type" and "bad data" as causes.

Root cause not isolated (looked like a genuine platform/tenant quirk specific to this flow, not a syntax or data problem) — but the pattern is: whatever the *outer* higher-order collection function is (`select` or `filter`), it gets reported as "not defined", while non-lambda functions (`join`, `concat`, `equals`, `outputs`, `item`) used elsewhere in the same expressions work fine.

**Fix that reliably worked**: stop using `select`/`filter` inline entirely. Replace with the classic **Apply to each + Append to string variable** loop pattern instead:
1. Initialize the target variable as an empty string literal (`""`) — no expression.
2. `Apply to each` over `outputs('GetX')?['body/value']` (via dynamic content, not typed).
3. Inside the loop, **文字列変数に追加 (Append to string variable)** with value `concat(item()?['列名'], '; ')` (plain `concat`+`item()`, no `select`/`filter`).

This produces a harmless trailing separator (e.g. `a@x.com; b@x.com; `) which mail-address fields tolerate fine. Slower/more verbose than `join(select(...))` but avoids the mystery function-rejection entirely — prefer this pattern by default in any flow where `select`/`filter` throws this error, rather than re-debugging the same dead end.

## Full reference example (verified working end-to-end 2026-07-26)

A pagination loop combining all four fixes above — see [[continuous_data_capture_setup]] for the complete calendar-specific flow this was built for, and `POWER_AUTOMATE_SETUP_CALENDAR.md` (in the Dropbox-synced CalendarExport folder) for the exact step-by-step build instructions with all expressions. Final verified result: 13,806 events backfilled across ~19 years with no data loss.
