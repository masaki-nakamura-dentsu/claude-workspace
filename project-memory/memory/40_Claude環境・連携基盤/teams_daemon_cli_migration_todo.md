---
name: teams-daemon-cli-migration-todo
description: "DONE 2026-08-12: teams_daemon.py migrated off its own dedicated browser onto the shared bot browser (port 9226) via CDP. 2026-09-29: fixed Teams URL migration (teams.microsoft.com→teams.cloud.microsoft) login-detection bug, click-failed-on-reorder bug (data-fui-tree-item-value stable key), and silent-crash-on-page-closed bug (outer reconnect loop)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 76308553-9b7a-4873-a31e-1f3384190e69
  modified: 2026-08-12T00:33:34.895Z
---

Requested 2026-08-12 by the user, during [[outlook_cli]]'s company-Mac (d14461) rollout, as an explicit "do this next, as a separate task" follow-up — not done yet.

**Background**: on d14461 there are currently two separate automation browsers: (1) port 9226 / `SalesforceExport/browser_profile` — the real [[shared_bot_browser]] used by Salesforce, Teams self-chat posting ([[teams_self_chat_autopost]]), and now Outlook ([[outlook_cli]]). (2) `~/TeamsExport/browser_profile`, launched via Python Playwright with `--remote-debugging-pipe` (no network port) by `teams_daemon.py` (`~/TeamsExport/teams_daemon.py`) — a continuous Teams message-collection daemon feeding `~/TeamsExport/data/teams_messages.jsonl` (see [[local_work_data_export]]). Because it's pipe-connected, no external script can attach a new tab to it without going through `teams_daemon.py` itself — reusing it as-is would risk breaking the always-on capture daemon, which per [[continuous_data_capture_setup]] is already somewhat fragile (known Errno-11 issues, a daily 7:30 check job that's been failing since 2026-08-10).

**The ask**: build a Teams CLI-style tool (read/collection side, not just the existing send-only [[teams_cli]] built on ICPTokyo2022) that does what `teams_daemon.py` currently does, but through the shared bot browser (port 9226) instead of its own dedicated pipe-connected profile — so Salesforce + Teams (send AND collect) + Outlook all genuinely run in the one shared browser window, and `teams_daemon.py`'s separate browser process can eventually be retired.

**How to apply**: before starting, read `~/TeamsExport/teams_daemon.py` in full to understand its current scraping logic, schedule/trigger mechanism, and output format (must stay compatible with `~/TeamsExport/data/teams_messages.jsonl`'s existing schema, since [[local_work_data_export]] and other tools depend on it). Also check [[continuous_data_capture_setup]] for the current health status before touching anything — don't break a working (if fragile) pipeline without a tested replacement ready. This is scoped to d14461 only; ICPTokyo2022's existing send-only [[teams_cli]] is a separate, already-working tool and is a reasonable reference for the browser-interaction patterns (selectors, login handling) even though it doesn't do collection.

## DONE 2026-08-12 — migrated, verified working end-to-end on d14461

Kept the daemon's core scraping logic (nav-item exclusion list, `extract_messages`/`resolve_author`, dedup-by-`mid`, cutoff/scroll logic) **completely untouched** — only replaced how it obtains a `page`. Added `is_browser_running()`/`launch_shared_browser()`/`connect_shared_browser()` to `~/TeamsExport/teams_daemon.py`, mirroring [[outlook_cli]]'s `lib.js` `connect()` pattern (hardcoded `PORT=9226`/`PROFILE_DIR=~/SalesforceExport/browser_profile` — no cross-Mac auto-detect needed since this daemon is d14461-only). Replaced the old `p.chromium.launch_persistent_context(user_data_dir=..., channel="chrome", headless=False, ...)` call with `connect_over_cdp(CDP_URL)` against the shared bot browser, matching a Teams tab by URL or opening a new one. Never calls `browser.close()`/`context.close()` (same reasoning as the CLI scripts — this process attaches to a browser other tools depend on staying up).

**Real bug caught and fixed during verification**: the first version's "no matching tab → reuse `context.pages()[0]`" fallback (copied from `lib.js`'s existing pattern, which had the identical bug) silently **hijacked the Outlook CLI's existing tab** — since no `teams.microsoft.com` tab existed yet in the shared browser, `context.pages[0]` was the one Outlook tab already open there, and the daemon `.goto()`'d it away to Teams. This only bites once multiple *different* tools share one browser concurrently — safe when only one tool ever used the browser. **Fixed in both places** (`teams_daemon.py` and `~/Scripts/outlook_cli/lib.js`, the latter also Dropbox-shared with ICPTokyo2022): the "not found" fallback now **always** opens a genuinely new tab (`context.new_page()` / `context.newPage()`) instead of reusing an arbitrary existing page. Verified fixed: ran `outlook login` while the Teams daemon had the browser open — Outlook correctly got its own new tab, both tabs coexisted (confirmed via `/json` CDP tab listing).

**Login verified with zero manual intervention**: the `SalesforceExport/browser_profile` already had a valid Teams SSO session (residual from earlier work, e.g. [[teams_self_chat_autopost]]) — `wait_for_login()` returned true within ~1 minute of the tab opening, no MFA/account-picker prompt appeared. This is notably better than [[outlook_cli]]'s d14461 rollout the same session, which *did* need a fresh manual SSO/MFA step — Teams happened to already be authenticated in that profile, Outlook wasn't yet.

**Full deploy sequence used** (reusable pattern for similar swaps): `launchctl unload` the old plist → run the modified script manually in the background (`nohup ... & disown`) to watch one full cycle end-to-end via a log-tailing [[Monitor]] rather than blocking/polling → confirmed real output (`teams_messages.jsonl` grew by exactly the reported new-message count, 5240→5295, schema/author-field unchanged and correctly populated, zero errors in stdout) → killed the manual test process → `launchctl load` the (unchanged) plist → confirmed the daemon also cold-starts correctly under real launchd (RunAtLoad), completing its own 5-min startup delay → login → poll cycle with no intervention.

**Old `~/TeamsExport/browser_profile` (2.3GB) is now unused** — left in place, not deleted, in case a rollback is ever needed. No launchd plist changes were required (same script path, same python3 interpreter).

**Net result**: d14461 automation (Salesforce, [[outlook_cli]], Teams collection) now genuinely shares one Chrome instance (port 9226) as the user originally asked for, instead of two separate browser processes.

## 2026-09-29 — Teams Web URL移行(teams.microsoft.com→teams.cloud.microsoft)対応、click failed大量発生の根本原因特定・修正

詳細な経緯は[[teams_daemon_url_migration_20260929]](work_status)参照。要点3つ:

1. **URL移行**: MicrosoftがTeams WebのURLを`teams.microsoft.com`→`teams.cloud.microsoft`へ移行(セキュリティ強化に伴う告知あり)。ログイン判定・タブ検索が旧URL文字列のみに依存していたため、実際はログイン済みでも「ログイン未確認」と誤判定し10分でタイムアウトしていた。`teams_daemon.py`・`post_self_chat.py`とも新旧両ドメイン(`TEAMS_DOMAINS = ("teams.cloud.microsoft", "teams.microsoft.com")`)を判定するよう修正。**今後Teams側でURLがまた変わった場合、真っ先にこの判定ロジックを疑うこと。**

2. **チャット一覧のクリック失敗(大量の`click failed...Timeout 10000ms exceeded`)**: 一見「新UIでリストが仮想化された」ように見えたが、CDP経由でDOMを直接調査したところ実際は仮想化ではなく、**チャット一覧が並び替わる(最近使った順の更新等)たびにReactが要素を再マウントし、事前に注入した`data-scrape-index`連番属性が消える**ことが原因だった(233件全項目は常にDOM上に存在していた)。教訓: 位置ベースの連番をJSで注入して後から参照する方式は、動的に並び替わるリストでは壊れる。修正: `data-fui-tree-item-value`(Fluent UI/Teamsの会話固有の安定キー、アプリのデータモデル由来で再マウントしても変わらない)を取得しておき、クリック時に毎回`click_chat_by_key()`で現在のDOMから該当キーの要素を探し直してクリックする方式に変更。**同様の「一覧が並び替わるUIで位置ベースの属性を後から参照する」設計は他のスクレイピングコードでも避けること。**

3. **初期化フェーズ/poll_once実行中の`NameError`/`TargetClosedError`で無言クラッシュ・無限に同じエラーを出し続ける問題**: launchdは`KeepAlive=false`のため、プロセスが例外で落ちると自動復帰しない。また"Target page, context or browser has been closed"系のエラーは一度発生すると同じpageハンドルがそれ以降ずっと壊れたままで、30分毎に同じエラーを出し続けるだけで自己回復しないことを確認(過去ログでも同症状が繰り返し記録されていた)。修正: `main()`を外側の再接続ループ(`while True: try: ... except: sleep(60); retry`)で包み、poll_once内で"closed"を含む例外が出た場合は内側ループをbreakして即座に`connect_shared_browser`からやり直す設計に変更。予期しないエラー時はTeams Webhookでも通知するようにした。**このパターン(外側リトライループ+特定エラーでの即時再接続)は他の長時間稼働daemon(cas_download.py等)にも横展開を検討する価値あり。**

修正後、2026-09-29 10:16:10に208件中click failed 0件で「ポーリング完了: 新規153件」まで到達し、全修正の有効性を確認済み。
