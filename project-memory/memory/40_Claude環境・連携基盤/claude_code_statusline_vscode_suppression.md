---
name: claude-code-statusline-vscode-suppression
description: ターミナルCLIのstatusLineはVS Code統合ターミナル(IDE連携モード)では表示されず、独立したターミナル.appでのみ表示される
metadata: 
  node_type: memory
  type: project
  originSessionId: c5f07fe2-7956-4cf0-b246-d052d894126a
  modified: 2026-08-22T03:36:11.814Z
---

## 事象

`~/.claude/settings.json` に `statusLine`(カスタムコマンドでトークン数/コストを常時表示する機能)を設定しても、**VS Codeの統合ターミナルパネル内で`claude`を起動した場合は表示されない**。`/status`で確認すると「IDE: Connected to VS Code extension version X.X.X」と出ており、拡張とのコンパニオン(IDE連携)モードで動いていることが分かる。

一方、**VS Codeを介さない独立した「ターミナル.app」で`claude`を起動すると、同じ設定でstatusLineが正常に表示される**(2026-08-22に実機確認済み)。

## Why

VS Code統合ターミナルでclaudeを起動すると自動的にIDE連携(コンパニオン)モードに入り、この状態では拡張側のUI(コンテキストバー等)と重複を避けるためか、ターミナルTUI側のカスタムstatusLineフッターが意図的に抑制される仕様と推測される(設定ファイル自体は正しく読み込まれていた — `Setting sources: User settings`)。

## How to apply

- ユーザーがターミナルCLIの`statusLine`(トークン数/コスト常時表示)を使いたい場合は、**VS Codeを介さない独立したターミナルアプリ**(Launchpad/Spotlightから「ターミナル」を開く)で`claude`を起動するよう案内する。
- VS Code統合ターミナルやVS Code拡張のチャット画面では、代わりに入力欄下部のコンテキストインジケーター(常時)と`/usage`コマンド(オンデマンド詳細)を使う。
- 関連設定: statusLineスクリプトは `.claude-sync/Scripts/statusline_tokens.py`(Dropbox同期)に実体があり、`~/.claude/statusline_tokens.py`からシンボリックリンクで参照する構成([[dropbox_config_sync]]と同じパターン)。他Macで使うには同様のシンボリックリンクをそちらでも作成する必要がある。
