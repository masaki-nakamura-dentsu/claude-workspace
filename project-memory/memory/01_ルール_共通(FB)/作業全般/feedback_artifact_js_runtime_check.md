---
name: feedback-artifact-js-runtime-check
description: Artifactの手書きJSを編集/追記する際は、node --checkの構文チェックだけでなく、最小限のDOMスタブで実際に実行するReferenceErrorチェックも必須。2026-09-30にダッシュボード全体が空表示になる事故が発生し判明。
metadata:
  node_type: memory
  type: feedback
  originSessionId: unknown
  modified: 2026-09-30T01:45:16.748Z
---

**Artifactの`<script>`を手書きで編集・追記した後は、`node --check`による構文チェックだけでなく、
最小限のDOMスタブ(`document.getElementById`/`createElement`等をモック)を使って`new Function(script)()`
で実際に実行し、ReferenceError(未宣言変数の参照)が出ないことを確認してから公開すること。**

**Why**: 2026-09-30、[[anime_ip_search_dashboard_project]]で「提案ブリーフ」タブを追加した際、
`const PITCH_BRIEFS = BUNDLE.PITCH_BRIEFS || {};`という宣言をせずに`Object.keys(PITCH_BRIEFS || {})`
と未宣言のbare識別子をいきなり参照してしまった。`node --check`では「SYNTAX OK」と表示され、この種の
バグ(構文的には正しいが実行時に未定義変数を参照する)は検出できない。この未宣言変数参照が
スクリプトのトップレベルで実行されたため、そこでReferenceErrorが発生してスクリプト全体の実行が
停止し、**それより後ろにあった既存の描画関数呼び出し(renderRanking/renderDetail/renderReport等)も
連鎖的に一切実行されなくなり、ダッシュボードの主要タブがすべて空表示になった**。ユーザーからの
スクリーンショット付き報告で発覚するまで気づけなかった。

**How to apply**: Artifactの既存JSに新しいコードブロックを追記・挿入する際は、必ず以下の手順を踏む:
1. `node --check extracted_script.js`で構文エラーが無いことを確認(従来通り)
2. 加えて、`document.getElementById`/`createElement`/`createElementNS`/`querySelectorAll`等を返す
   最小限のモックオブジェクトを用意し、`new Function(script)()`で実際に実行する
3. 実行時に投げられた例外が`ReferenceError`かどうかを判定する。ReferenceErrorは未宣言変数参照の
   実バグとして必ず修正する。TypeError等(DOMスタブが不完全なために起きる、実際のブラウザでは
   発生しないエラー)は許容してよい
4. 再利用可能な検証スクリプト例は`anime_ip_search_dashboard_project`の作業ディレクトリに
   `dom_stub_check.js`として保存済み、同種の構造(BUNDLE埋め込み型の単一HTMLファイル)のArtifactでは
   流用可能

このチェックを省略すると、「構文チェックは通ったのでこれで大丈夫」という誤った安心感のまま、
実際には壊れたページを公開してしまうリスクがある。特に新機能追加時(既存コードへの単純な文言修正
ではなく、新しい変数・関数を導入する変更)は必ずこの実行時チェックを行うこと。
