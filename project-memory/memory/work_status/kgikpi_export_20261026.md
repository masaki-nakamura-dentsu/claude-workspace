---
name: kgikpi_export_20261026
description: 2026-10-26 KGI/KPI定期保存のPDF 0 bytes失敗と復旧・リトライ追加
metadata:
  type: project
---

## 2026-10-26 10:15 KGI/KPI PDF 0 bytes失敗→復旧(会社Mac)
- Status: done
- 事象: 09:40/09:42の定期実行が「PDFサイズが小さすぎます(0 bytes)」で失敗。同事象は10/22にも3回。ダウンロード自体は発火するが中身が空になる断続的な不具合。
- 対応: launchdと同じPython3.14で `--force` 再実行→ KGIKPIレポート_20261026.pdf 保存成功。(システムのpython3にはplaywrightが無いので手動実行も `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` を使う)
- 恒久対策: export_pdf を1回の起動内で最大3回(60秒間隔)リトライ。バックアップ `.bak_202610261012`。
- 再発時: リトライでも0 bytesが続くなら、Power BI側のエクスポート不調(レポート描画/Botブラウザ再起動)を疑う。
