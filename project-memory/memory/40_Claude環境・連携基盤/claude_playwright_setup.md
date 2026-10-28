---
name: claude-playwright-setup
description: Playwright (Node.js) を永続インストールしたブラウザ自動化環境。フォーム送信・ファイルアップロード(POST)自動化に使う。
metadata: 
  node_type: memory
  type: project
  originSessionId: eea13e91-5b88-4a60-8f67-b84eb6a6d4ee
  modified: 2026-08-04T06:11:17.954Z
---

`~/.local/share/claude-playwright/` に Playwright を永続インストール済み(2026-08-04)。
Dropboxフォルダの外・セッションscratchpadの外にあるので、セッションをまたいで再インストール不要で使い回せる。

## 構成
- Node.js v24.13.1 / npm v11.8.0 (システムにインストール済み、`/usr/local/bin`)
- `~/.local/share/claude-playwright/package.json` + `node_modules/playwright` (v1.60.0)
- Chromiumブラウザ本体も同ディレクトリ内 `node_modules/playwright-core/.local-browsers/` に同梱済み
  (`chromium-1223`, `chromium_headless_shell-1223`) — `PLAYWRIGHT_BROWSERS_PATH` を設定しなくても
  自動的にここを見つけて動く(env var不要、確認済み)。
- 雛形スクリプト: `submit_form_template.js`、セットアップ手順・注意点は `README.md` に記載。

## 使い方
```bash
cd ~/.local/share/claude-playwright
node your_script.js   # require('playwright') するだけでよい
```

## 詰まった点(次回参考)
- `npx playwright install chromium` が社内ネットワークのTLS証明書検証で
  `UNABLE_TO_GET_ISSUER_CERT_LOCALLY` により失敗することがある(1回目は成功、2回目は失敗した)。
- 対処: 一度でも `~/Library/Caches/ms-playwright/` にダウンロード成功していれば、
  そのフォルダを `node_modules/playwright-core/.local-browsers/` へ手動コピーすれば動く
  (`INSTALLATION_COMPLETE` マーカーの有無で完全性を確認できる)。
- Playwrightのデフォルト`chromium.launch()`は headless時に `chromium_headless_shell` を要求するため、
  フルChromiumだけでなくheadless-shellのビルドもコピーが必要だった。

## Why
[[user]] からの依頼: フォーム送信・ファイルアップロードを自動化したい。Dropbox外・恒久的な場所に置いて
再インストール不要にしたいという明示的な要望があった。

## How to apply
今後このユーザーからブラウザ自動化(フォーム入力、ファイルアップロード、スクレイピング等)の依頼が来たら、
まずこの環境が使えないか確認する。再インストール不要、`cd ~/.local/share/claude-playwright && node script.js`
で即使える。
