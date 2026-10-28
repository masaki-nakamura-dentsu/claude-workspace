---
name: salesforce-adhoc-record-search-technique
description: 共有ブラウザ(port 9226)からPlaywright CDP接続でSalesforce内を案件名検索し、該当レコードのURL/詳細フィールドを取得する手順
metadata: 
  node_type: memory
  type: reference
  originSessionId: 623e0adf-6f95-4add-8099-8ba21d64453d
  modified: 2026-09-11T02:58:03.345Z
---

Salesforceの案件(GBC案件/Item)を名前で検索してレコードURLを特定したいとき(例: 重複登録の特定案件を探す)の手順。[[shared_bot_browser]]のd14461上の共有ブラウザ(port 9226、Salesforce SSO済み)を使う。

## 手順
1. `chromium.connectOverCDP('http://localhost:9226')` で接続、`force.com`のタブを再利用(`context.pages().find(...)`)。
2. `https://dgx.lightning.force.com/lightning/page/home` へ遷移。
3. グローバル検索ボックスはLightning Web Component(shadow DOM)の中にあり、ヘッダー上部の`input[type="search"]`は直接クリックしても反応しない(splashPage用の別の隠し要素がヒットしてタイムアウトする)。**代わりに `button[aria-label="検索"]` をクリック**すると検索ボックスが展開され、そのままキーボード入力できる。
4. `page.keyboard.type('検索したい案件名')` → 少し待つ → `Enter`。検索結果ページに遷移し、`a[href*="/lightning/r/"]` のリンクを`page.evaluate`で全部抜き出すと該当レコードのURL一覧が取れる(過去の閲覧履歴やレポートリンクも混ざるので案件名で絞り込むこと)。
5. 個別レコードの詳細(部署名/期間/金額/責任者など)は該当URL(`/lightning/r/<18桁ID>/view`)に遷移し、`page.locator('body').innerText()` でページ全文テキストを取得するのが確実(Lightningのレコード詳細はshadow DOM構造が複雑で、ラベル/値をCSSセレクタで狙い撃ちするより全文取得してテキストで拾う方が速い)。
6. 作業後は[[shared_bot_browser]]のルール通り、ウィンドウをminimizedに戻す(`Browser.getWindowForTarget`+`Browser.setWindowBounds`)。`browser.close()`/`context.close()`は絶対呼ばない。

## Why
2026-09-11、[[qbr_powerbi_case_collision_investigation_20260910]]のAgoda Media AOR重複案件(BD部、2026年1月〜3月で期間重複)のSalesforce URLをユーザーから聞かれ、メモリには説明はあってもレコードID/URLが保存されていなかった。共有ブラウザが既にSalesforceにログイン済みだったため、その場で検索して特定できた。

## How to apply
次回以降、ユーザーが「〇〇案件のSalesforce URLを教えて」のように具体的なレコードURLを聞いてきた時、メモリに保存されていなければ、まずこの手順でその場検索して答える(ユーザーに聞き返したり「メモリにありません」で終わらせない)。
