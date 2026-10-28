---
name: feedback-pptx-repack-include-all-parts
description: pptxを解凍→画像圧縮→再zipするときは全エントリ(customXml/docMetadata含む)を入れ、元と部品一覧の一致・XML/参照検査をしてから渡す。PowerPointで「修復」エラーを出した
metadata:
  type: feedback
---
2026-10-14 Nidec提案書の圧縮で、再zipを `zip ... '[Content_Types].xml' _rels docProps ppt` と4つだけ指定し、customXml/ と docMetadata/ を落とした。PowerPointで開くと「コンテンツに問題が見つかりました。修復…」が出て、ユーザーが作業を止めた。日付版 _20261014_03 は壊れたまま(使わない)。

**Why:** [Content_Types].xml や _rels が存在しない部品を指すと、PowerPointは修復ダイアログを出す。python-pptxでは開けてしまうので、python-pptxの読込テストだけでは検出できない。

**How to apply:** 再zipは `zip -X -D OUT '[Content_Types].xml'` → `zip -r -X -D OUT . -x '[Content_Types].xml'`(全エントリ、ディレクトリ項目なし)。渡す前に (1)元と namelist が一致 (2)全XMLがパースできる (3).rels の内部参照先が全て存在 (4)全部品の拡張子かPartNameがContent_Typesにある、を検査し、QuickLookで数枚描画する。雛形=Work/Client/Nidec/作業履歴フォルダ/compress_pptx.sh。[[pptx_filesize_reduction_technique]] の手順もこの点を補う。
