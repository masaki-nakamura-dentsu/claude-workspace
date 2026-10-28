---
name: pbix-inspect-with-pbixray
description: ダウンロードしたpbixの中身(Power Query・メジャー・リレーション・ページ構成)をDesktopなしで読む方法(pbixray+PBIRのJSON)
metadata:
  type: reference
---

会社MacにはPowerBI Desktopがないが、ユーザーがServiceから落としたpbixはDesktopなしで読める(2026-10-22 HDY定点観測で実施)。
- モデル(DataModelはXPress9圧縮): scratchpadにvenvを作り `pip install --proxy http://proxy1.dentsu.co.jp:8080 pbixray` → `PBIXRay(path)` の `.tables` `.power_query`(クエリ名とM全文) `.dax_measures` `.relationships` `.statistics`(列一覧) `.metadata`。
- レポート: pbixはzip。`Report/definition/pages/pages.json`(ページ順)、`pages/<id>/page.json`(displayName・ページフィルター)、`visuals/<id>/visual.json`(visualTypeと Entity/Property)。レポート全体フィルターは `Report/definition/report.json` の filterConfig(無ければ未設定)。
- Serviceの「ダウンロード」は2種類: レポート付き(Report/を含む)とモデルのみ(DataModelだけ)。Connections の DatasetId が同じなら同じモデル。
- 用途: 手順書を「今のモデルに追加する」形に直す前の現状確認。[[hakuhodo_overseas_intel_monitoring]]
