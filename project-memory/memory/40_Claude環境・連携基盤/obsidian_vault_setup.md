---
name: obsidian-vault-setup
description: Obsidianのvault=このmemoryフォルダ(Dropbox実体)。作業メモはObsidian形式で残す(2026-10-20設定)
metadata:
  type: reference
---
2026-10-20 個人Mac(ICPTokyo2022)でObsidianを設定。
- vault実体: `中村正樹/.claude-sync/project-memory/memory`(~/.claude/projects/.../memory はここへのsymlink)。Claudeのメモと同一データをObsidianで閲覧・編集できる。
- 登録先: `~/Library/Application Support/obsidian/obsidian.json` に id `c1aude0memory001` で追加し open=true。ユーザーが最初に作った vault `中村正樹/Obsidian/Obsidian`(ようこそ.mdのみ)は登録を残したまま非オープン。
- `.obsidian/` 設定はmemoryフォルダ直下(Dropbox同期されるので他Macでも同じvaultとして開ける。会社Macは同フォルダを「フォルダをvaultとして開く」で登録が必要)。
- 書き方ルール: 作業メモ・work_statusはObsidianで読みやすいMarkdownに。関連メモは `[[name]]` リンク(Obsidianのwikiリンクとしても機能)。日付は YYYY-MM-DD。

## フォルダ構成(2026-10-20 作業別に整理)
01_ルール_共通(FB)/{資料・スライド, ブラウザ・自動化, データ・Excel・PowerBI, 写真・映像・クリエイティブ, 作業全般} / 10_GBC_QBR・KPI・PowerBI / 11_GBC_Salesforce・業務自動化 / 12_AI活用PJ・AgencyOS / 13_提案・クライアント案件 / 20_写真・映像・創作 / 30_個人・家族 / 40_Claude環境・連携基盤。MEMORY.md・work_status/・_backups/ は直下。
- 新しいメモは該当フォルダに作り、MEMORY.mdのリンクは `フォルダ/ファイル.md` 形式で書く(空白・括弧はURLエンコード)。
- 整理前の全ファイルは `_backups/20261020_before_folder_reorg/` に保存。
