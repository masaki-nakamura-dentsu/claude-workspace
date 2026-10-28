---
name: feedback-trace-to-source-files-to-save-tokens
description: 画像の目視突合より前に、元ファイル(Illustrator/pptx等)をテキストベースでたどれないか確認する
metadata: 
  node_type: memory
  type: feedback
  modified: 2026-08-28T20:07:14.856Z
  originSessionId: ce1ebe76-bcd5-4bdf-b49e-6f9e7a3fe580
---

完成物(PDF等)から情報を読み取る前に、元になった編集用ファイル(Illustrator .ai、pptx、設計ファイルなど)をテキストベースで確認することでトークンを節約できないか、まず検討する。

**Why**: ユーザーから明示指示(2026-08-27、[[subway_photo_booklet_project]]の見積もり更新作業)。実例: 小冊子の確認用PDFから「どの写真が使われているか」を特定するのに、最初はPDFを10ページ画像化してClaudeに読ませ、透かしクレジット名と候補写真を目視突合した(画像を十数枚読む=高コスト、ユーザーから[[feedback_confirm_before_image_heavy_work]]の指摘を受けた直後)。その後ユーザーが元のIllustrator(.ai)ファイル一式を渡してくれたところ、.aiファイルは実体がテキストベースで、リンク画像のファイルパス(`stRef:filePath`等のXMPタグ)がプレーンテキストとして埋め込まれていた。`strings file.ai | grep .jpg`のようなテキスト検索だけで、画像を1枚も開かずに使用写真を完全に確定できた。

**How to apply**: 「このPDF/画像から何が使われているか確認して」のようなタスクで、対応する元ファイル(Illustrator/pptx/InDesign/Figma等の編集用ソース)が存在する場合は、先にその元ファイルをテキストベースで調べられないか試す(`strings`/`grep`でリンクパス・メタデータを抽出、pptxならpython-pptxでテキスト/notes抽出等)。本質は「PDF vs 元ファイル」の形式差ではなく「画像として見る必要があるか、テキストとして読めるか」——元ファイルにテキストの手がかりがなければ結局画像化が必要になる点は留意。ユーザーに元ファイルの所在を尋ねる、または既にプロジェクトフォルダ内にあれば自分で探しにいくのが望ましい。[[feedback_confirm_before_image_heavy_work]]と対で運用: 画像を開く前に、まず元ファイルのテキスト情報で代替できないか確認するのが第一選択。

より広い括りは[[feedback_token_conscious_practices]]参照(2026-08-31統合)。
