---
name: mac-windows-ime-dictionary-migration
description: "How Masaki's Mac IME word-registration dictionary was migrated to Windows, incl. the encoding bug that breaks MS-IME import"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4f789a7a-7cf8-4a24-be87-6fd1e96c77fd
  modified: 2026-08-07T02:59:58.620Z
---

Completed 2026-08-07 on the d14461 (会社) Mac. Task: migrate macOS 単語登録/ユーザー辞書 to Windows.

## Key facts discovered
- This Mac uses **Google 日本語入力** (Mozc-based), not the macOS-standard Kotoeri IME. User dictionary lives at `~/Library/Application Support/Google/JapaneseInput/user_dictionary.db` — a proprietary binary/protobuf format, not readable directly (not real SQLite despite the extension).
- Export path: Google日本語入力の辞書ツール →「管理」→「エクスポート」→ produces a **UTF-8, no-BOM**, tab-separated text file (`よみ\t単語\t品詞`).
- Target on Windows was the standard **Microsoft IME ユーザー辞書ツール** (not Google日本語入力 for Windows).

## The bug and fix
Importing the raw Mac export into MS-IME's 「テキストファイルからの登録」 failed on nearly every line with `品詞の指定を確認してください`. Root cause: MS-IME's importer reads BOM-less text as Shift-JIS/ANSI, so the UTF-8 bytes (including the 品詞 field itself) get corrupted into mojibake and no longer match any recognized 品詞 label — this fires even for trivially valid entries.

Fix applied (see conversion done inline in that session, not saved as a standalone script):
1. Re-encode the export to **UTF-16LE with BOM**, CRLF line endings — this is what MS-IME's importer actually expects for Unicode text, and it's also required to preserve non-JIS characters (this dictionary had Cyrillic entries like "МФК PHOTOS" that Shift-JIS/CP932 cannot represent at all).
2. Remap 品詞 labels that exist in Google日本語入力 but not in MS-IME's vocabulary: bare `姓` → `人名(姓)`, bare `名` → `人名(名)`. Other labels (`名詞`, `短縮よみ`, `顔文字`) are shared and need no change.

Result: reimport succeeded, confirmed working by user.

## Reusable takeaway
Any future Mac→Windows (or Windows→Mac) user-dictionary migration on this Mac should assume: (a) check which IME is actually in use before assuming macOS-standard Kotoeri — [[gbc_department_move_2026]]-style "verify before assuming" applies here too, (b) MS-IME's text import needs UTF-16 BOM, not UTF-8, (c) 品詞 vocabularies differ across IME vendors and non-ASCII (Cyrillic etc.) entries need Unicode-safe encoding to survive the round trip.
