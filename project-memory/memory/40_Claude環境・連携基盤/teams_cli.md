---
name: teams-cli
description: "Teams CLI at ~/Scripts/teams_cli/ — send Teams messages (self-chat + arbitrary chats) via browser automation, built 2026-08-09"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0d980f60-2004-4715-968d-223870b8ae90
  modified: 2026-08-10T23:25:40.771Z
---

Built 2026-08-09 on ICPTokyo2022 (this personal Mac) after the user asked to "develop a Teams CLI" (TeamsのCLIを開発して). Scoped down via a clarifying question to: sending messages (to self-chat, and to an arbitrary existing chat by name) — not reading/searching history, which is already covered separately by the exported `~/TeamsExport/data/teams_messages.jsonl` (see [[local_work_data_export]]).

**Architecture**: same debug-port-Chrome + Playwright `connectOverCDP` pattern as [[chatgpt_web_automation]] / [[gemini_web_automation]] / [[timetree_web_automation]], reusing [[claude_playwright_setup]] (`~/.local/share/claude-playwright`, scripts require `NODE_PATH=~/.local/share/claude-playwright/node_modules` since the CLI files live outside that installed package's own directory). Runs against `teams.microsoft.com/v2` (the new Teams web UI, not the desktop app).

**Important — shares the single bot browser, does not launch its own.** Initially built with its own dedicated `teams-bot` profile/port 9228, but the user immediately flagged this as violating the [[shared_bot_browser]] "one browser, many tabs" rule (they noticed two separate Chrome windows: TimeTree's and Teams'). Corrected same session: killed the 9228 process, deleted the `~/.chrome-profiles/teams-bot` dir, and logged Teams into the existing `timetree-bot` profile (port 9227) as a second tab instead — see [[timetree_web_automation]]'s 2026-08-09 update for the full story. `lib.js` now hardcodes `PORT=9227` / `PROFILE_DIR=~/.chrome-profiles/timetree-bot`. **If ChatGPT/Gemini ever get migrated into this same shared browser, do NOT let Teams automation regress back to a separate profile — always point at whatever port is currently documented as the shared browser in [[shared_bot_browser]].**

**Files** (`~/Scripts/teams_cli/`):
- `lib.js` — shared logic: `connect()` (attaches to the shared browser, auto-launches it if not running), `ensureLoggedIn()`, `findChatLeaves()`, `openChat(page, name)`, `getComposeBox()`, `typeMessage()`, `clickSend()`.
- `login.js`, `list.js`, `send.js` — the three subcommands' entry points.
- `teams` — bash dispatcher (`teams login|list|send`), exported as the user-facing command. Not yet added to `$PATH`; invoke via full path `~/Scripts/teams_cli/teams` or the user can alias it.

**Usage**:
```
teams login                              # check/prompt login (opens the shared browser if needed)
teams list [filter substring]            # print chat names (for picking an exact --to target)
teams send --self "本文"                  # send to own self-chat
teams send --to "宛先名" "本文"           # send to a named chat — exact match first, else substring
teams send --to "宛先名" --dry-run "本文" # types into the compose box but does NOT click send (safe test)
```
Multi-line messages: pass a literal newline inside the quoted arg, or pipe via stdin (`echo -e "L1\nL2" | teams send --self`).

**Key selectors (as of 2026-08-09, Teams web v2, may drift — this is a Fluent UI React app with hashed CSS classes, so prefer `data-tid`/`role`/`aria-label` over class names)**:
- Chat/channel rail: `[data-tid="simple-collab-dnd-rail"]`, each entry `[role="treeitem"]`. The rail mixes chats AND channels AND group-header treeitems in one flat tree — **leaf detection matters**: a treeitem with no nested `[role="treeitem"]` inside it is an actual clickable chat/channel; the group headers (e.g. "お気に入り") are treeitems too but contain all their children's treeitems nested inside, so naive `hasText` substring matching against the whole rail will match the oversized parent group first unless you filter to leaves. `findChatLeaves()` in `lib.js` does this filtering — reuse it rather than re-deriving.
- Self-chat identified by the leaf text containing the literal substring `(あなた)`.
- Message compose box: `[data-tid="ckeditor"]` (a contenteditable div, not a real textarea/`role=textbox`) — there can be multiple `ckeditor` elements in the DOM (e.g. inactive thread-reply boxes); `getComposeBox()` picks the first *visible* one.
- Send button: `button[data-tid="sendMessageCommands-send"]` (aria-label "送信 (⌘ Return)"). Used instead of pressing Enter directly, to avoid any ambiguity between plain-Enter-sends vs Shift+Enter-newlines depending on Teams' current keybinding settings.
- Multi-line composing: type each line via `page.keyboard.type()`, press `Shift+Enter` between lines (not `\n` inside a single `.type()` call, which Teams may interpret as an immediate send attempt).

**Ambiguous-recipient safety**: `openChat()` requires an exact leaf-text match first; if none, falls back to substring match; if the substring match is still ambiguous (e.g. `--to "Yamada"` matching both "山田 桂太 Keita Yamada" and a "Yamada、Yamamoto" group chat), it throws listing all candidates rather than guessing — confirmed working via a live test. This exists specifically because a wrong-recipient send is hard to reverse and visible to others; don't relax this matching logic without an equally strong safeguard in place.

**Verified working end-to-end 2026-08-09**: `teams list` (122 chats/channels enumerated), `teams send --self` (real message delivered and visible in the self-chat), `teams send --to "山田 桂太" --dry-run` (correct chat opened, text typed into the compose box, confirmed via screenshot, not sent, cleared afterward) — deliberately did NOT send a real test message to an actual colleague, only self-chat and dry-run were used to avoid an unwanted real message landing in someone else's chat during testing.

**Not built (explicitly out of scope this round, per the user's answer to the scoping question)**: reading/searching chat history from the CLI, and starting a brand-new chat with someone not already in the rail (`openChat` only finds existing chats/channels). If asked for either later, extend `lib.js` rather than starting a new tool — the browser/session plumbing is already there.

## 2026-08-11: two real bugs found and fixed — `teams send` was completely broken until this session

`teams send --self` started failing with `locator.waitFor: Timeout 5000ms exceeded` waiting for the send button — on every attempt, including a short one-word test message, so not a length/flakiness issue. Root cause turned out to be **two separate bugs**, both fixed in `lib.js`:

1. **`typeMessage()`'s clear-existing-draft step used `Control+A`, which does nothing in Chrome on macOS** (Select All there is `Meta+A`/⌘A — `Control+A` in a text field is more like an Emacs-style "move to line start" binding, not select-all). Every prior "existing text" branch silently failed to select anything, so `Backspace` deleted at most one character while the new message got typed on top — confirmed via direct DOM inspection: a stuck draft from earlier failed attempts had grown to **3000+ garbled characters** and repeated `Control+A`+`Backspace` loops (even 15x) didn't shrink it at all, while a single `Meta+A`+`Backspace` cleared it to 0 instantly. Fixed by switching to a platform-aware key (`process.platform === 'darwin' ? 'Meta+A' : 'Control+A'`).
2. **`clickSend()`'s button selector had drifted**: `button[data-tid="sendMessageCommands-send"]` no longer matches anything — live inspection found the real button now has `data-tid="newMessageCommands-send"` (same `aria-label="送信 (⌘ Return)"` though). This is exactly the drift risk flagged in this file's original notes ("Fluent UI React app with hashed CSS classes... may drift"). Fixed by trying a list of candidate selectors in order (`newMessageCommands-send` → `sendMessageCommands-send` → generic `button[aria-label*="送信"]`) instead of one hardcoded `data-tid`, so future drift degrades gracefully instead of hard-failing.

**Verified fixed end-to-end**: after both fixes, `teams send --self "..."` succeeded on the first try, confirmed via screenshot (message delivered intact, compose box empty afterward, no leftover garbled draft).

**Lesson for future web-automation scripts written from this Mac**: don't assume `Control+A` is select-all — always use a platform-aware key, or test the actual keyboard shortcut behavior in the target app before hardcoding it. Also: when a locator-based click fails with a timeout, check whether the *element itself* still exists at all (`locator(...).count()`) before assuming it's a timing/visibility issue — here the count was truly 0, not just slow to appear.

## Message deletion (2026-08-11, done ad-hoc via a throwaway script, not yet added to the CLI itself)

Needed to delete a specific old self-chat message (a superseded "setup this on the company Mac" prompt, replaced by a new one — see [[outlook_cli]]). Found the working pattern by trial: locate the message via `[data-tid="chat-pane-message"]` (match by its text), then `.click({ button: 'right' })` on the bubble itself opens a `role="menuitem"` context menu with a「削除」item. Clicking it deletes immediately with **no confirmation dialog** — the bubble is replaced in-place by "このメッセージは削除されました。元に戻す" (undo is available from that placeholder). **The hover-revealed "その他のメッセージ オプション" button (`data-tid="message-actions-menu-hidden-button"`) was unusable — repeated pointer-events-intercepted timeouts even with `force: true`. Right-click was reliable on the first try; prefer it over that hover button for any future message-action automation here.**

If `teams delete` ever becomes a real subcommand, lift this right-click → 削除 pattern into `lib.js` rather than re-deriving it.

**2026-10-12**: 個人Macではアカウント別ブラウザ方針([[browser_account_routing]])により、9227(timetree-bot)から会社用 **9231(dentsu-work-bot)** に移行した。
