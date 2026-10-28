---
name: feedback-openpyxl-formula-sheet-extend
description: openpyxlで既存Excelシートに行を追加/入れ替えるとき、数式・書式・外部リンクを壊さないための3つの注意点。QBR用ファイル群(CAS見込・貢献見込等)の月次更新で繰り返し起きた
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b649a20-47dd-4bb5-8e3e-96d1f8aaed5d
  modified: 2026-09-06T00:44:50.069Z
---

2026-09-06のQBR8月分データ更新([[qbr_cas_mikomi_source_report]]、[[qbr_2026q3_cas_koken_july_update]]参照)で、`GBC CAS見込_LATEST.xlsx`等をopenpyxlで更新した際に3つの不具合を出し、中村さんに都度指摘されて直した。**次回以降、Excelファイルへの行追加/データ入れ替えをopenpyxlで行う前に、この3点を先にチェックすること。**

## 1. 「集計シート」が値ではなく数式かどうかを必ず確認する

`GBC CAS見込_LATEST.xlsx`の`CAS見込`シートは一見データ行に見えたが、実際は`=CAS見込_Original!A2`のような参照式+ASC変換+一部XLOOKUPの数式シートだった(貢献見込・貢献実績側は逆に値のみのシートで、ファイルによって方式が違う)。確認せずに値を直接書き込んで数式を破壊してしまった。

**How to apply**: 新しいデータを流し込む前に、そのシートの既存行(特にA2セル)の`.value`を見て、文字列が`=`で始まっていないか必ず確認する。数式シートなら、テンプレート行の数式文字列を`re.sub(r'(?<!\$[A-Z])(?<=[A-Z])2(?![0-9])', str(new_row), tmpl)`のように**絶対参照($付き)は変えず相対参照の行番号だけ**置換して伸ばす。

## 2. 新規セルは既存行のnumber_formatを引き継がない

openpyxlで`ws.cell(row=i, column=j, value=v)`は真っさらな書式(General)のセルを作る。日付列(DATEVALUE)やカンマ区切り数値列は、既存の代表行(例: row2)から`.number_format`を読み取って明示的にコピーしないと、日付が数値のまま表示されたり、`yyyy-mm-dd h:mm:ss`のような望まない書式になる。

**How to apply**: データ書き込みループの中で、テンプレート行の各列のnumber_formatを事前に辞書化しておき、新しい行の同じ列に必ず適用する。特にDATEVALUE列は要注意(このQBRファイル群では複数箇所で書式崩れが放置されていた——`mm-dd-yy`/`yyyy/m/d;@`/`yyyy-mm-dd`など、ファイルごとに「正しい」書式が違うので、そのファイルの他の行に合わせる)。

## 3. 外部リンク(externalLink)がある場合、openpyxl保存でExcel拡張メタデータが失われることがある

`GBC CAS見込_LATEST.xlsx`のC列はSharePoint上の別ファイルへのXLOOKUP参照を持つ外部リンクがあり、openpyxlで保存すると`xl/externalLinks/externalLink1.xml`内のExcel 2021+拡張ネームスペース(`xmlns:xxl21=...`)が失われ、Excel側で「外部参照が壊れている」ように見える不具合が起きた(基本構造`<externalReferences>`要素やrelsは保持されるので気づきにくい)。

**How to apply**: 外部リンクを持つファイルをopenpyxlで保存した後は、保存前のバックアップから`xl/externalLinks/`配下のファイルをzip直接操作(`zipfile`でファイル単位に読み書き)で復元するのが確実——`openpyxl.load_workbook`→再保存では直せない。
