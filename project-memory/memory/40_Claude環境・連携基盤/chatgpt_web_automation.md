---
name: chatgpt-web-automation
description: Working recipe to drive ChatGPT's web UI via Playwright + Chrome debug-port attach — new chat, file/image attachment, prompt submit, poll for image generation, download result
metadata:
  node_type: memory
  type: reference
  originSessionId: fc9a2fff-4ac2-4c64-8ec5-4fd6c0f41f81
  modified: 2026-10-15T08:07:43.816Z
---

Confirmed working end-to-end 2026-08-06 (4/4 image generations succeeded, first request in [[toyota_india_aot_hyryder_project]] where the user explicitly asked to have ChatGPT operated directly rather than handing prompts off for manual running).

**Architecture**: same pattern as [[google_maps_list_save_automation]] — a normal, non-automated Chrome instance with a remote-debugging port and dedicated profile dir, logged into by the user like any regular browser, then attached to via Playwright's `chromium.connectOverCDP()`. Uses the pre-installed environment in [[claude_playwright_setup]] (`~/.local/share/claude-playwright`, `node script.js`).

**Launch**:
```bash
mkdir -p "$HOME/.chrome-profiles/chatgpt-bot"
open -na "Google Chrome" --args --remote-debugging-port=9224 \
  --user-data-dir="$HOME/.chrome-profiles/chatgpt-bot" --lang=ja-JP \
  --no-first-run --no-default-browser-check "https://chatgpt.com"
```
Profile persists — a returning session can skip login entirely by reusing the same profile dir + port (check `curl -s http://127.0.0.1:9224/json/version` to see if it's already running).

**Login check**: `page.locator('body').textContent()` and check for "Log in"/"ログイン" — don't try to infer from cookies.

**Key selectors (as of 2026-08-06, ChatGPT web, may drift)**:
- Composer: `div#prompt-textarea` — a contenteditable div, not a real `<textarea>`. Click + `.type(text, {delay: 5})`.
- **Always clear before typing**: check `(await editable.innerText()).trim()`, if non-empty do `Control+A` then `Backspace` first. A leftover string from earlier DOM exploration silently prepended onto a real prompt once because this wasn't done.
- File attach input: `input#upload-photos` (`accept="image/*"`, `multiple`). `setInputFiles([path1, path2, ...])` works directly — **no need to click the "+"/attach button first**, Playwright can set files on a hidden input.
- Send button: `button[aria-label="プロンプトを送信する"]` (Japanese UI; English UI likely `aria-label="Send prompt"` — verify live if UI language differs).
- New chat: just `page.goto('https://chatgpt.com/')`.

**Detecting generation completion** — poll every ~8s, timeout 3–4 min:
```js
const mainText = await page.locator('main').innerText();
const thinking = mainText.includes('思考中') || mainText.includes('生成中');
const imgs = await page.locator('main img').all();
// find the largest-rendered img whose src contains 'estuary/content'
// (NOT 'oaiusercontent' — that's a wrong guess, doesn't appear on this endpoint)
// filter out small thumbnails (uploaded references render ~128x128)
```
Done when `!thinking` and a matching image's bounding-box area exceeds a threshold (e.g. >100000 px²).

**Downloading the result** — `context.request.get(url)` on the image URL times out (wrong session context). Fix: fetch from *inside* the page:
```js
const base64 = await page.evaluate(async (url) => {
  const resp = await fetch(url);
  const buf = await resp.arrayBuffer();
  let binary = '';
  const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}, imageUrl);
fs.writeFileSync(outPath, Buffer.from(base64, 'base64'));
```

**Timing observed**: each image generation took ~30–50s and succeeded first try (no retries) using the established prompt formula — attach a clean angle/pose reference image, attach a *cropped, text-free* design reference, explicitly instruct "reproduce this exact design, do not reinterpret."

**How to apply**: whenever a task calls for generating images (or otherwise interacting) via ChatGPT's web UI directly rather than just drafting prompts for the user to run, reuse this exact setup. If the debug-port Chrome from a prior session is still running (check the port), skip straight to `connectOverCDP` — login persists in the profile dir.

**Parallel generation (confirmed working 2026-08-07, [[feedback_parallel_tab_image_generation]])**: multiple `context.newPage()` tabs against the same debug-port browser, each doing its own `goto('https://chatgpt.com/')` → new chat → prompt → poll → download, run concurrently fine with a worker-pool of ~4. Ran 15 image generations this way (4 concurrent) successfully. One failure mode observed: after roughly 12-15 generations in one session, ChatGPT shows a rate-limit modal (`#modal-conversation-history-rate-limit`) that intercepts pointer events, causing the composer click to time out (`locator.click: Timeout 30000ms exceeded ... subtree intercepts pointer events`). Fix: check for/wait out that modal (~60s) and reload before retrying the send — not a permanent failure, just a burst throttle.

**New gotchas found 2026-08-27 ([[ai_katsuyo_pj_weekly_tips]] Tips-verification session, dedicated `chatgpt-bot` profile port 9224, not yet migrated to shared browser)**:
- **Multi-line prompts typed via `.type()` can submit early**: if the prompt string contains a literal `\n`, Playwright's `.type()` sends a raw `Enter` keypress for it, and ChatGPT's composer submits on plain Enter (Shift+Enter is needed for a line break). This silently splits one intended message into two separate sends, corrupting the conversation (the second fragment appears as an unrelated follow-up user turn). **Fix**: split the prompt on `\n`, type each line with `.type()`, and press `Shift+Enter` between lines instead of embedding `\n` in the typed string. A real end-user pasting the same multi-line prompt (Cmd+V) is unaffected — paste doesn't fire per-character keydown events — so this only matters for typing automation, not for the copy-paste usage the Tips are designed for.
- **Composer draft can get cross-contaminated between chats on the same account**: even after `Control+A`+`Backspace` and starting a brand-new chat (`page.goto('https://chatgpt.com/')` + fresh `newPage()`), the composer sometimes ends up containing leftover text from a different, unrelated prior prompt (observed: another test's prompt text got prepended; separately, unrelated content from a months-old unrelated project surfaced via ChatGPT's persistent cross-chat "memory" feature). Root cause not fully confirmed — likely an account-level unsent-draft sync and/or the "reference memory" feature, not a per-tab/local-storage issue, since fresh `Page` objects were still affected. **Mitigation used**: after send, check the rendered length of the composer/typed text against expected length and retry if it doesn't match; for slide-quality screenshots, crop the output to the assistant's response only (excluding the user's echoed prompt bubble) so composer contamination never appears in the final artifact — show the exact prompt via a separately-authored text/code box instead of relying on the screenshot to prove the input.
- **Rate limiting**: heavy automated testing (15-20+ prompts within roughly an hour on one account) triggers a `#modal-conversation-history-rate-limit` overlay ("リクエストの頻度が高すぎます...数分待ってから、もう一度お試しください") that blocks the composer and can persist through several 60s backoff retries — budget 5-10+ minutes of cooldown, not just one retry, and check `page.locator('#modal-conversation-history-rate-limit').count()` before typing/after streaming completes (it can also appear *after* a response finishes, obscuring it, not just before sending).
- Separately, the account's **image-generation weekly credit cap** can be hit independently of the above (message: "現在、画像生成の利用上限に達しています...クレジットを追加するか、[date]までお待ちください") and text responses can silently fall back to a lighter "Instant" model after hitting a usage cap — check for these messages in the response before assuming a screenshot represents full-capability output.

**Share feature behavior (dentsu Enterprise workspace, confirmed 2026-09-11, [[gbc_intelligence_engine_project]])**: the conversation-header "共有する" button is a single click, no confirmation dialog — it immediately copies a link to the clipboard and shows a toast ("リンクをクリップボードにコピーしました / リンクはワークスペースメンバーにのみ表示されます。"). The link (`chatgpt.com/share/e/...`) is workspace-scoped, not public. Opening it (even as the same/owner account) shows a "これは共有されたChatGPTのチャットのコピーです。メモリには追加されません。" banner plus a "会話を報告する" link, but **there is no native comment/annotation feature** — selecting text only shows "ChatGPTに質問する" / "書き始める" options, nothing comment-related. To read the copied link back out of the clipboard in a Playwright script: `context.grantPermissions(['clipboard-read','clipboard-write'], { origin: 'https://chatgpt.com' })` then `page.evaluate(() => navigator.clipboard.readText())` — a plain `evaluate` without granting permissions first can silently fail or throw. Also note: `browser.newContext()` over an existing `connectOverCDP()` connection did NOT produce an isolated/incognito context in this environment (new pages landed in the same default context, same login) — don't rely on it for testing a logged-out/external viewer's perspective; that would need a genuinely separate profile or account.

**Account mixing on the shared bot browser (2026-09-17, [[currencysort_app_project]] app icon generation)**: on the personal Mac's shared browser (port 9227, `timetree-bot` profile), navigating to chatgpt.com showed logged-out, and triggering Google sign-in got stuck on the personal Gmail account chooser (the profile has mixed personal/work Google identities from other automations) — the CDP connection to that browser then started timing out entirely (`connectOverCDP: Timeout 30000ms exceeded`) even after killing the stuck script, suggesting a blocking native picker/modal can wedge the whole remote-debugging port, not just the one page. **Fix used**: rather than fighting the stuck shared-browser state, launched a brand-new dedicated Chrome profile+port specifically for this (`~/.chrome-profiles/chatgpt-work-bot`, port 9229) so the work Google account (masaki.nakamura@dentsu.co.jp) could log in cleanly with zero risk of colliding with other identities already in the shared profile — this matches the documented exception in [[shared_bot_browser]] ("only use a genuinely separate profile if there's a real conflict... needing two different logged-in identities for the same service at once"). **How to apply**: if a shared-bot-browser ChatGPT/Google-login attempt hangs on an account picker or the CDP port stops responding, don't keep retrying the same profile — spin up a fresh dedicated profile on a free port instead of debugging the wedged one.

**2026-09-29 addition — composer/send/stop/response selectors all drifted again (company Mac d14461, port 9224 chatgpt-bot), confirmed working recipe as of this date ([[ai_katsuyo_pj_weekly_tips]] Tips-deck screenshot capture)**:
- Composer is no longer `div#prompt-textarea` — it now has **no id at all**, just `[contenteditable="true"]` with class `ProseMirror`. Use `page.locator('[contenteditable="true"]').first()`.
- Send button aria-label is now simply **`"送信"`** (not `"プロンプトを送信する"`). It only appears once the composer has text — check `button[aria-label="送信"]`, not a fixed selector present at page load.
- Stop-while-streaming button aria-label is now simply **`"停止"`** (not `"ストリーミングの停止"`). Poll `page.locator('button[aria-label="停止"]').count() === 0` to detect completion — checking for `"思考中"`/`"生成中"` substrings in `main`'s innerText is unreliable and caused a screenshot to be taken mid-stream (captured a half-finished response with the stop button and a "…" cursor visible) in one case, and a screenshot taken after only ~2s of a still-thinking response with almost no content in another. Give the stop button ~2s to appear after clicking send before starting the poll loop (it doesn't appear instantly).
- No more `article[data-turn="assistant"]` elements at all. The assistant's response now renders under an **sr-only (visually hidden) heading** `<h4 data-conversation-role="assistant">`. To screenshot just the assistant's answer (excluding the echoed user prompt bubble, matching the established practice in this memory of cropping to answer-only): `page.locator('h4[data-conversation-role="assistant"]').last().locator('xpath=ancestor::div[@data-content-search-unit-key][1]')` — this ancestor div wraps exactly the one assistant message, not the whole turn (which also includes the user's message above it, found by walking further up to a `[data-turn-key]` div).
- These are UI-only changes; the CDP-attach / profile-persistence / rate-limit / composer-contamination mechanics documented above are unaffected and still apply.

**How to apply**: selectors on this page churn every few weeks — before reusing any selector from this memory, do a quick live check (`page.locator(...).count()`) rather than trusting it blindly, especially for the composer/send/stop/response-container selectors which have now drifted twice (2026-08-27 and 2026-09-29).

**2026-10-15 addition (company Mac d14461, port 9226, dentsu Enterprise account) — Custom GPT nav terminology and useful direct URLs, captured for [[ai_katsuyo_pj_weekly_tips]]'s lecture PPTX screenshots**: the sidebar no longer has a "GPTを探索する" entry — there's now a dedicated top-level nav item simply labeled **「GPT」** that leads to `/gpts/mine` ("マイGPT" page with a "GPTを作成する" card). `/gpts/editor` opens the GPT creation/edit screen directly (two tabs: 作成する/構成, a live プレビュー pane). Other confirmed working direct URLs: `/scheduled` (Scheduled Tasks list + "新規タスク" button — note `/settings/connectors` and `/schedules` both redirect elsewhere, use `/scheduled` exactly), `/settings/plugins-settings` (Settings → 連携 → プラグイン — this is where Connectors/Apps live now, confirmed this dentsu Enterprise workspace already has SharePoint, Outlook Email, Outlook Calendar, and Teams connectors installed and listed here). This confirms Custom GPTs are mid-migration toward the "Plugins" naming (per [[ai_katsuyo_pj_weekly_tips]]'s Oct 2026 web research on the OpenAI-announced retirement plan) — the GPT creation flow itself still says "GPT", but Settings groups it under "連携 → プラグイン" alongside Connectors, suggesting both concepts are converging into one "Plugins" system. When screenshotting any of these pages for user-facing material, crop out the sidebar's "ピン留め"/"プロジェクト"/"最近の項目" lists (real chat/project names, e.g. actual client-code project names) and the Scheduled Tasks list (real task names appeared, e.g. competitor-monitoring task titles) — crop to just the header/button chrome being demonstrated, not the account's actual content.

**Also useful for verifying/searching YouTube URLs (2026-08-06, [[toyota_india_aot_hyryder_project]])**: in this environment, `WebSearch` doesn't reliably surface small/niche YouTube videos, and both `WebFetch` and plain `curl` fail against `youtube.com` (network-restricted). The same debug-port Chrome session reused for ChatGPT works fine for this too — `page.goto('https://www.youtube.com/watch?v=<id>')` to check a specific video exists (read `page.title()` and the description via `ytd-watch-metadata #description, #description-inline-expander`), or `page.goto('https://www.youtube.com/results?search_query=' + encodeURIComponent(query))` and iterate `ytd-video-renderer` locators (`#video-title` for title+href, `#channel-name` for channel) to find candidates. This is the reliable way to confirm a YouTube URL is real and matches its claimed content before citing it anywhere — don't cite a YouTube URL found only via WebSearch snippet text without this kind of direct verification, since a plausible-looking title in a snippet is not proof the video/ID actually exists.

**2026-09-25 personal Mac (port 9229, chatgpt-work-bot) notes**: (1) Session had silently expired — the UI still rendered as logged-in (sidebar, "中村正樹 Enterprise") but every `/backend-api/*` call returned 403 and sent prompts sat forever as an empty `result-streaming` placeholder with a `c/WEB:...` URL. Detect via `page.evaluate(() => fetch('/backend-api/conversations?offset=0&limit=1').then(r=>r.status))` — 200 = usable. Fix was a user re-login (bring window on-screen, poll that endpoint until 200, then minimize again). (2) Launch this bot with `--disable-renderer-backgrounding --disable-backgrounding-occluded-windows --disable-background-timer-throttling` so a minimized window still renders/streams; `page.screenshot` times out while minimized.
