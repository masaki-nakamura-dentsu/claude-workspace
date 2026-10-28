---
name: feedback-verify-against-ground-truth
description: "Consolidated pattern (2026-08-24 memory review) across 6 separate incidents: don't assert a fact, type a value, or claim a system's state from inference/memory/batch-generalization — check the authoritative source first, every time, not just when something feels uncertain"
metadata:
  node_type: memory
  type: feedback
  originSessionId: memory-weekly-review-20260824
  modified: 2026-08-24T00:44:27.000Z
---

Six separate incidents across unrelated projects (financial reporting, Teams/email, role tracking, stock-photo licensing, spreadsheet entry, Mac sync claims) all share the same root failure mode: stating something as true — a number's meaning, a message's sender, a person's current role, a license status, a formatting convention, a sync/config state — based on inference, plausible-sounding assumption, or generalizing from a nearby known-good case, instead of checking the one authoritative source that would have given the real answer directly.

**Why this is a standing pattern, not six unrelated mistakes:** in every case the authoritative source was available and checkable in seconds (a message's `author` field, a spreadsheet's neighboring cells, an official total, a canonical role-tracking memory, the image being license-checked, `ls -la` on a symlink) — the error was never lack of access to ground truth, it was substituting an assumption for the lookup. This is a bias worth naming explicitly so it gets caught before acting/speaking, not just after a correction.

**How to apply — before stating a fact or entering a value, ask "did I actually check this, or did I infer/assume/generalize it?"**:
- Before naming who sent/asked something → read the message's own `author`/`from` field, never infer from chat/thread name.
- Before typing a value into a shared spreadsheet by hand → check a few neighboring rows for the formatting convention in force.
- Before reporting a discrepancy in financial/reporting numbers → cross-check against the official summary total; the same-looking label can mean different things in different files.
- Before classifying/rating items in a batch (photo licenses, content curation, etc.) → verify each one individually against its own source; don't extrapolate "3 of 4 were X, so the 4th probably is too."
- Before stating whether a role/ownership/system-sync state is still current → re-check against the canonical live source (e.g. [[gbc_department_move_2026]] for roles, `ls -la` + [[dropbox_config_sync]] for sync state) rather than an older memory or thread in isolation.
- If the authoritative source is genuinely ambiguous or unavailable, say so explicitly rather than guessing — an admitted unknown is safer than a confident wrong answer, since the user may act on it.

**Source incidents (originals kept in place, not deleted — see each for full detail):**
- [[feedback_verify_against_official_totals]] — misjudged what "確度A" meant in QBR financial files twice before checking the official total.
- [[feedback_verify_message_direction]] — reported a Teams message backwards (inferred sender from chat name instead of the `author` field).
- [[feedback_verify_role_before_assuming]] — assumed the user still owned a handed-off project because an old memory said so.
- [[feedback_verify_stock_license_per_image]] — mis-tagged a stock photo's license by generalizing from other photos in the same batch instead of checking it individually.
- [[feedback_check_surrounding_rows_before_manual_entry]] — typed a client name full-width into a column that was silently half-width-kana-only by convention, without checking neighboring rows first.
- [[feedback_check_dropbox_sync_before_claiming_isolated]] — twice stated Mac-to-Mac memory/config sync didn't exist without running `ls -la` to check the actual symlink state (recurred even after the first correction).
- [[feedback_verify_dates_computationally]] (added 2026-09-06) — the date/weekday-specific case: read a weekday off a screenshot instead of computing it, misjudging a recurring meeting's day.
- (added 2026-09-29, teams_daemon debugging) — diagnosed a scraping tool's mass click-failures as "the new Teams UI virtualizes the chat list" purely from the symptom pattern (only ~65 of 158 tagged elements found), reported that conclusion to the user, and got approval to build a scroll-and-collect fix around it — before actually re-querying the live DOM for the *total* leaf-item count. When later testing the fix, a full re-query showed all 233 items were present in the DOM the whole time; the real cause was React remounting list items on reorder, silently stripping the injected `data-scrape-index` attribute. The "virtualization" story was plausible and matched the visible symptom, but a 30-second CDP query (`querySelectorAll` for the full list, no filter) would have shown it was wrong immediately. See [[teams_daemon_cli_migration_todo]] for the full incident.

This file is the "why does this keep happening across such different domains" umbrella; the individual files above remain the concrete case studies and stay independently useful when a similar situation recurs in their specific domain. **Applies to code/DOM debugging too, not just data facts**: before naming a root cause for a bug (not just a data fact), re-check the actual live state directly (full unfiltered query, not just re-confirming the failing path) rather than pattern-matching the symptom to the most plausible-sounding explanation.

**関連(2026-10-12週次レビューで追記)**: メモリ内の古い「未解決/ブロック中」記述を現状として断言しない件は [[feedback_check_latest_state_before_citing_blockers]] を参照(メモリそのものも一次情報と突き合わせる対象)。
