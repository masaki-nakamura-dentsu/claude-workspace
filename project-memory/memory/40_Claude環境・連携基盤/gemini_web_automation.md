---
name: gemini-web-automation
description: Working recipe to drive Gemini's web UI (gemini.google.com) via Playwright + Chrome debug-port attach for NanoBanana image generation — new chat, file attach, prompt submit, image capture
metadata:
  node_type: memory
  type: reference
  originSessionId: fc9a2fff-4ac2-4c64-8ec5-4fd6c0f41f81
  modified: 2026-08-07T04:10:24.034Z
---

Confirmed working end-to-end 2026-08-06, same session as [[chatgpt_web_automation]] — user explicitly asked to have Gemini/NanoBanana available the same way going forward, after previously giving up on it (see [[gemini_nanobanana_setup]] — the API route hit a billing wall, and the user found manually pasting into the Gemini UI too much friction, so they'd switched entirely to ChatGPT). Direct browser automation removes that friction the same way it did for ChatGPT.

**Architecture**: identical pattern to [[chatgpt_web_automation]] / [[google_maps_list_save_automation]] — normal non-automated Chrome with a dedicated profile + debug port, user logs in once, Playwright attaches via `connectOverCDP`.

**Launch** (separate profile/port from the ChatGPT one — different Google account host):
```bash
mkdir -p "$HOME/.chrome-profiles/gemini-bot"
open -na "Google Chrome" --args --remote-debugging-port=9225 \
  --user-data-dir="$HOME/.chrome-profiles/gemini-bot" --lang=ja-JP \
  --no-first-run --no-default-browser-check "https://gemini.google.com/app"
```

**Key differences from ChatGPT's automation that matter**:
- Composer: `div.ql-editor[aria-label="Gemini へのプロンプトを入力"]` — a Quill-based contenteditable, not a plain div like ChatGPT's. Click + `.type()` works the same way; still defensively clear first (`Control+A`+`Backspace` if non-empty).
- Send button: `button[aria-label="プロンプトを送信"]`.
- New chat: `page.goto('https://gemini.google.com/app')`.
- **File attach has no static `input[type=file]` in the DOM** (unlike ChatGPT's `input#upload-photos`) — must click `button[aria-label="アップロードとツール"]`, then click the `"ファイルをアップロード"` menu item, which triggers a real OS file-picker. Handle via Playwright's `page.waitForEvent('filechooser')` **before** clicking, then `fileChooser.setFiles([...])` on the resolved chooser object.
- **Generated images render inside an iframe**, not the top-level page (`page.frames().find(f => f.url().includes('/app/'))` — the frame whose URL contains `/app/<chat-id>`, distinct from the outer `gemini.google.com/app` page and a couple of unrelated Google auth/widget iframes also present). Query `frame.locator('img')`, not `page.locator('img')`.
- **Downloading the result**: the image `src` is a `blob:https://gemini.google.com/...` URL. Fetching it via `frame.evaluate(fetch(...))` (the technique that worked for ChatGPT's `estuary/content` URLs) **failed here** — `TypeError: Failed to fetch`, even when evaluated in the correct frame, likely because the blob was already revoked by the time of the fetch attempt (Gemini's app may release the object URL once the image is otherwise cached/rendered). **Working fix instead: `await imgLocator.screenshot({path: ...})`** — a plain Playwright element screenshot of the `<img>`, which doesn't depend on the blob URL still being alive. Simpler and more robust than the fetch approach; consider using this method for ChatGPT too if its `estuary/content` fetch ever starts failing similarly. Known cosmetic side-effect: the element screenshot can catch a small overlay toolbar (share/copy/download icons) in the top-right corner if it's rendered on hover-over — crop it out or trigger the screenshot when the toolbar isn't showing if a clean image is needed.
- No separate "image generation mode" toggle was found in the model picker (only text-model tiers: Flash/Thinking/Pro as of 2026-08-06) — just ask for an image in the prompt text directly and it generates one under whichever model is selected.

**Verified working**: submitted a plain "generate an image of X" text prompt (no reference images attached in this test) to a fresh chat, image appeared after ~18s, captured cleanly via element screenshot.

**How to apply**: whenever a task calls for generating/editing images via Gemini/NanoBanana directly, reuse this setup rather than falling back to "write a prompt for the user to paste manually." If the debug-port Chrome from a prior session is still running (check `curl -s http://127.0.0.1:9225/json/version`), skip straight to `connectOverCDP` — login persists in the profile dir.

**Update 2026-08-07 — prefer the download button over element screenshot**: with multi-image reference prompts (e.g. 3 attached reference photos + a long instruction prompt), Gemini's UI can render a floating "prompt preview" card (with an expand icon and send arrow) that visually overlaps the bottom portion of the generated image in the viewport — this is real painted overlap (confirmed both via `img.screenshot()` and via manual crop-by-bounding-box), not a coordinate bug, so no amount of scrolling/cropping math fixes it. **Fix**: hover the generated `<img>` (`await img.hover()`) to reveal the on-image toolbar, then click `button[aria-label="フルサイズの画像をダウンロード"]` inside the same iframe, wrapped in `Promise.all([page.waitForEvent('download'), frame.locator(...).click()])`, then `download.saveAs(path)`. This downloads the actual full-resolution PNG (e.g. 1024×1024) with zero UI overlap — cleaner and higher-res than any screenshot approach. Use this as the default extraction method going forward instead of element screenshot; only fall back to element screenshot if no download button is found on hover.

**Also confirmed**: the profile's saved login can silently expire/log out between sessions even though the profile dir still has cookies — always verify with a quick `text=ログインしてください` check (or screenshot) before assuming a prior session's login is still valid, and ask the user to log in manually in the visible (non-headless) Chrome window if it isn't. Also, `connectOverCDP` can return multiple open tabs at the same URL (e.g. one logged-in, one stale/logged-out) — when picking a page from `context.pages()`, filter by checking for the logged-out marker text rather than assuming `pages[pages.length-1]` is the right one.

**2026-10-07 update (d14461)**: Gemini is now logged in on the shared browser port 9226 (user logged in manually; old gemini-bot/9225 profile was logged out — don't use it). UI changes: attach = `button[aria-label="アップロードとツール"]` → `button[aria-label^="ファイルをアップロード"]`; first upload shows a rights-consent dialog (`button[aria-label^="同意"]`) and the filechooser only fires after re-clicking upload. Image tool chip: menu item `画像を作成` (chip "画像" then shows in composer). In 思考モード, a long JSON scene prompt to the Global Q Gem returned a *text prompt* ("Text-based AIのため画像を直接描画できません") instead of an image; a follow-up "この場でNano Bananaで画像を1枚生成して" in the same chat produced the image (~1-2 min). Download via hover + `button[aria-label*="ダウンロード"]` + download event worked (1536x2730 png). Follow-up edit requests in the same chat keep layout well but re-render speech-bubble text and can introduce new typos (e.g. 「時間時間」→「完成祝め祝い」) — after 2 fix rounds, prefer manual text fix in Photoshop over more regenerations.
