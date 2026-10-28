---
name: kgikpi_export_20261023
description: 2026-10-23 KGI/KPI定期保存の403失敗と復旧
metadata:
  type: project
---

## 2026-10-23 10:05 KGI/KPI PDF保存 403失敗→復旧(会社Mac)
- Status: done
- 事象: 09:40の定期実行でPDF書き出しは成功、SharePointアップロードのみ HTTP 403(Access is denied)。10/22は15:40に成功、10/22午前はPDF 0 bytes・ネット未接続・download timeout等で失敗が続いた(いずれも当日中に再試行で回復)。
- 診断: Botブラウザ(9226)のSharePointセッションは有効、フォルダ権限は継承中止のまま・中村に追加権限あり。権限剥奪ではなく一過性の認証エラー。
- 対応: `--force` 再実行で KGIKPIレポート_20261023.pdf 保存成功。次枠(11:40〜)は成功済みでスキップされる。
- 再発時: 403はまず再実行。続くならBotブラウザのSharePointセッション(Cookie)切れ、次にフォルダ権限を疑う。
