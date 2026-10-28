# 会社Mac(d14461) LibreOffice導入

## 2026-10-01T01:00:00Z
Status: done
What: 中村さんの指示で、pptx視覚QA(スライド画像化等)の効率化のためLibreOfficeを
会社Macへ導入。会社MacはHomebrew未導入・adminグループ非所属・sudoパスワード
対話不可という既知制約があるが、LibreOfficeは`/Applications`への書き込み権限が
無くても`~/Applications`(ユーザー所有、書き込み可)へ.appバンドルを置くだけで
動作する(.pkgインストーラ不使用、sudo不要)ことを確認し、この方式で導入した。
手順: documentfoundation.orgから`LibreOffice_26.8.0_MacOS_aarch64.dmg`を
社内プロキシ(proxy1.dentsu.co.jp:8080)経由でDL→`hdiutil attach`でマウント→
`LibreOffice.app`を`~/Applications/`へコピー→`~/.local/bin/soffice`に
シンボリックリンク(`~/.local/bin`は既にPATH済み、[[reference...]]の既存
micromambaパターンと同じ置き場所)。`soffice --version`で起動確認、
pptxスキルの`scripts/office/soffice.py`ラッパー経由でのPDF変換も実地で
成功を確認(スライドバンクPJの検証ファイルで実テスト)。
`pdftoppm`(poppler)は依然未導入のため、PDF→画像化はPyMuPDF(`fitz`)の
`get_pixmap()`で代替(既存の2026-09-30セッションの前例と同じ回避策)。
Next: 特になし。今後pptxスキルでの視覚QA(`scripts/office/soffice.py`)が
会社Macでも使えるようになった。
