# pdf_shrink.py 会社Macセットアップ

## 2026-08-23T23:45:59Z
Status: done
What: 会社Mac(d14461)にpdf_shrink.pyをセットアップ。~/Scripts/pdf_shrink.pyはDropbox同期本体へのシンボリックリンクで対応済みだったが、Ghostscriptが未導入かつbrewも未導入・ユーザーに管理者権限なし(sudo不可)と判明。root不要のmicromamba(自己完結バイナリ)経由でconda-forgeからGhostscript 10.07.1を導入し、~/.local/bin/gsにリンクして解決。実PDFで動作確認済み(3.2MB→1.2MB)。[[pdf_shrink_tool]]に手順・回避策を追記済み。
Next: —
