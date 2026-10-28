---
name: mac-disk-space-cleanup-technique
description: "How to diagnose macOS \"system data\" bloat via du breakdown, what's safe to delete, and OneDrive/CLI eviction limitations — from the 2026-08-23 ICPTokyo2022 cleanup"
metadata: 
  node_type: memory
  type: project
  originSessionId: 43b12ded-6845-4d35-95fd-e758420a726a
  modified: 2026-08-23T01:11:28.151Z
---

## Diagnostic method that works
`df -h` alone is misleading (root volume vs `/System/Volumes/Data` differ). Drill down with `du -sh ~/Library/Caches/* ~/Library/Application\ Support/* ~/Library/Group\ Containers/* | sort -rh`, then recurse into whichever top entries are large. Also check `/private/var/folders/<hash>/<hash>/` (per-user temp dir — has `T`, `C`, and sometimes a large `X` subfolder).

## Recurring pattern: this Mac refills fast
2026-08-19: freed 79GB→119GB (see `work_status/disk_cleanup_icptokyo2022.md`). By 2026-08-23, free space had dropped back to just **10GB** — a ~109GB loss in 4 days. Root cause not fully isolated, but confirmed contributors this time: Adobe After Effects cache regrew to 26GB, Adobe Camera Raw cache to 8GB, and a **12GB Chrome `code_sign_clone` temp buildup** (see below) that hadn't existed on 8/19. Worth treating disk space as something to spot-check periodically on this machine rather than assume stays fixed after a one-time cleanup.

## Chrome `code_sign_clone` — a fast, silent accumulator
`/private/var/folders/<hash>/<hash>/X/com.google.Chrome.code_sign_clone/` grew to 12GB by itself (just `.DS_Store` + temp binaries inside). This is macOS's Gatekeeper code-signing verification clone mechanism, and it's plausibly driven by how often new Chrome processes/profiles get spawned — this user runs heavy Chrome-based browser automation across many projects (see [[shared_bot_browser]], [[feedback_reduce_browser_automation_tokens]]). Completely safe to `rm -rf` (it's inert temp data; also clears on reboot, just doesn't get cleared otherwise). Worth checking this path first next time disk space complaints come up — it's an easy, zero-risk, high-yield win.

## OneDrive: no reliable CLI way to force "online-only" eviction
- `brctl evict` does **not exist** as a subcommand — `brctl` is Apple's own iCloud/CloudDocs ("bird") control tool and doesn't apply to third-party File Provider extensions like OneDrive.
- `fileproviderctl` exists and has `dump`/`diagnose`/`check`/`repair` subcommands but **no eviction command** — and `fileproviderctl dump` (with no domain arg) **hung for 2+ minutes** and had to be killed. Don't run it bare again; if needed, pass a specific domain/provider argument, and give it a short timeout.
- The only user-facing lever is Finder → right-click a file/folder → "ダウンロードを削除" (Remove Download). Confirmed via `stat -f "%b"` (block count) that this does NOT evict content immediately — it just flags the item as evictable. Sampled 49 files in a folder the user had done this to; only 1 had actually been evicted (0 blocks) days apart from the request, the other 48 were still fully materialized. Actual reclaim happens lazily, driven by macOS's own storage-pressure/purgeable-space logic, not by the Finder click itself.
- **Conclusion**: if the user wants OneDrive space back *now*, this doesn't reliably deliver — set expectations that it's a "when the OS gets around to it" mechanism, not an on-demand one. Don't attempt to force it by touching the underlying `~/Library/Group Containers/UBF8T346G9.OneDriveStandaloneSuite/` files directly — that's OneDrive's live sync database and could corrupt sync state.

## What was done 2026-08-23 (this session)
Freed ~12GB with user's explicit go-ahead: deleted the Chrome `code_sign_clone` temp folder (12GB) and Chrome's on-device AI model cache `OptGuideOnDeviceModel`/`OptGuideOnDeviceClassifierModel` (8GB — logical dedup with above, net effect measured via `df` was +12GB). User explicitly declined further action for now (Adobe caches ~34GB, Homebrew/pip ~1GB, Chrome "File System" site data 8.8GB of unidentified origin, and forcing OneDrive eviction) — said no rush, fine to let the OS handle OneDrive automatically. Free space at end of session: 21GB (up from 10GB at start).

## 2026-09-27 再発（空き17GB）
AEキャッシュ26G再成長（旧版26.3フォルダに溜まる）、code_sign_clone 6.3G再成長。新規判明: Dropbox内Lightroomフォルダに旧カタログ残骸（`Lightroom-2-v15-4.lrcat-data` 11G・`v13-3 Helper.lrdata` 5.9G・Dropbox競合コピーlrcat 5.1G）。現行カタログは `Lightroom-2-v13-5.lrcat`。Dropbox内削除は全マシンに波及するので要承認。
2026-09-27実施: 上記Lightroom残骸+AE+code_sign_clone+brew/pip削除で空き17→62GB。**CurrencySortMLは削除禁止**(ユーザー明言)、Downloadsは本人が整理する方針。ms-playwrightはキャッシュでなくブラウザ本体なので「安全なキャッシュ」扱いしないこと。
「システムデータ」肥大の隠れ要因: スワップ(`sysctl vm.swapusage`、2026-09-27に稼働17日で22GB)→再起動で解放。`diskutil apfs list`のVMボリューム容量で確認。iPhoneバックアップ(~/Library/Application Support/MobileSync)はTCCで`Operation not permitted`になり中身を確認できない→設定画面「iOSファイル」ⓘから削除を案内。macOS(約49GB)はシステム+Preboot+Recoveryで削減不可。
