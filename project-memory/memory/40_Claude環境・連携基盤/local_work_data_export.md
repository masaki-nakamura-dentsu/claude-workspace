---
name: local_work_data_export
description: "Local exports of the user's Outlook email and Teams chat history for analyzing work content; where the files are and how to regenerate them"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a9fd5356-af22-433a-9320-ae156d74d4ec
  modified: 2026-07-27T09:53:24.626Z
---

The user's Outlook (New Outlook for Mac, org-managed, no classic-mode toggle available) and Teams chat history have been exported locally so Claude can read and analyze them across sessions (e.g. for performance review writing, work summaries).

## Email export
- Parsed data: `~/OutlookExport/parsed_emails.jsonl` — one JSON object per line: `file, folder (Inbox/SentItems), subject, from, to, cc, date (ISO), body`.
- Coverage: **2026-01-01 onward, kept current automatically** — see [[continuous_data_capture_setup]]: a Power Automate flow drops new emails into OneDrive as they arrive, and `sync_power_automate_export.py` merges them into this file hourly via launchd (`com.nakamura.emailsync`, fixed 2026-07-23). If this file ever looks stale, check whether the sync job is still running before assuming the flow itself broke.
- Source `.eml` files (dragged manually out of Outlook by the user, since New Outlook has no AppleScript/API access and Power Automate premium licensing was blocked) live in `~/OutlookExport/Inbox/` and `~/OutlookExport/SentItems/`.
- Parser script: `~/OutlookExport/parse_emails.py` — rerun after the user drags more `.eml` files in to refresh `parsed_emails.jsonl` and `summary.txt`.
- To extend coverage (e.g. a new date range), the user must manually select+drag messages from Outlook into those folders (see [[outlook_export_method]] for why — New Outlook blocks AppleScript/Graph API/Power Automate premium; drag-to-Finder is the only self-service route found).

## Teams export
- Parsed data: `~/TeamsExport/data/teams_messages.jsonl` — one JSON object per line: `chat (name), mid (epoch-ms message id), author, date (ISO), text`.
- Coverage as of 2026-07-13: messages from 42 chats/channels (out of ~133 items in the left rail — some are non-chat shortcuts/empty, a handful of deeply-nested channels failed to click near the end of the run), cutoff at 2026-01-01, 2423 messages total. Heaviest: 山本高之(315), ワークフロー(240), 山田桂太(200), 日系クライアントピッチヒアリング(145), 【GlobalQ】2026定例会(125).
- Built via Playwright browser automation against teams.microsoft.com (not the desktop app) — Chrome (`channel="chrome"`, the system-installed one, since Playwright's bundled Chromium download fails on the corporate network's TLS-intercepting proxy).
- Scripts in `~/TeamsExport/`: `login.py` (interactive login into a persistent Chrome profile at `browser_profile/`), `scrape_teams.py` (the full scraper — waits for login, walks the `[data-tid="simple-collab-dnd-rail"]` chat tree, clicks each leaf `role="treeitem"`, scrolls `[data-tid="message-pane-list-viewport"]` to top repeatedly collecting `[data-tid="chat-pane-message"]` elements until hitting the cutoff date or no more new messages).
- **Important**: dentsu's SSO does not persist across separate browser process launches — every fresh `launch_persistent_context` call requires the user to re-login interactively (password + MFA) in the opened Chrome window, even though it's the same profile dir. Only stays logged in within one continuous script run. Budget ~10min per login for MFA.
- To extend/redo: rerun `scrape_teams.py` (adjust `CUTOFF_DATE` at the top). It's slow (~30min for a full pass over 42 active chats) — run in background and monitor `~/TeamsExport/data/scrape_log.txt`.

## Using this data
Both files are plain JSONL, safe to `grep`/`python3 -c "import json..."` filter by date/chat/folder without loading everything into context at once. See [[gbc_department_move_2026]] for the work-context this data has already been used to analyze.

**Caveat when filtering "sent by the user"**: `folder == 'SentItems'` alone is unreliable — many items in Sent are forwards (FW:) where the visible top text was authored by someone else. Filter on `from` actually containing `masaki.nakamura@dentsu.co.jp` instead.

**Teams `author` field — corrected 2026-07-27, was previously described as always-null**: checked directly (4,518 total records) and found ~25% (1,116) have a populated `author` (top senders: 中村正樹 275, plus various colleagues) — NOT null on every record as previously believed. Coverage is just partial/inconsistent, likely because Teams' own UI (which the scraper reads from the DOM) only labels the sender's name on the first message of a consecutive run from that person, not every message — so a null author does NOT reliably mean "unknown/unattributed," it may just mean "same sender as the message above." **Never infer sender/recipient direction from the `chat` field alone (that's just which 1:1/group conversation the message lives in, not who sent it) — always check the actual `author` field on that specific record before reporting who said what to whom.** Getting this backwards inverts the entire meaning of a message (confirmed the hard way — misread a message Masaki sent *to* someone as if it were the reverse). See [[feedback_verify_message_direction]].

Used to build [[user_writing_style]] — a profile of the user's actual email writing style for drafting messages "in his voice".
