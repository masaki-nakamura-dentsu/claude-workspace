---
name: f_jci_import_rules_20261026
description: JCIインポートの運用ルール(削除依頼=競合中止・完了不成立、事業区分はPython算出、クライアント補完、新規フェーズ反映の2段階目)
metadata:
  type: feedback
---

JCI(日系ピッチ)インポートで2026-10-26にユーザーから指示されたルール。実装は `build_import_csv.py`（旧版は `_archive/build_import_csv_before20261026.py`）。

- **削除依頼(`<削除依頼>`)は削除しない**。重複のため「競合中止・完了不成立」で処理する＝フェーズ`Incomplete（完了・不成立）`＋獲得グループ`なし（競合中止）/None (Pitch cancelled)`（例: GBC__c a1hfP00000ADVZh）。更新CSVに自動で出る。新規シート側の削除依頼は登録しない。
- **事業区分の抜け原因**: BD部シートの事業区分は提供サービスからのExcel数式(LET/TEXTJOIN)で、openpyxl data_only で読むと計算キャッシュが無い行は空になる（202610新規20件中9件）。**Why:** キャッシュ依存だった。**How to apply:** `BUSINESS_CATEGORY_RULES` で提供サービスからPython側で必ず算出する（Creative→クリエイティブ等。Excel数式と同じ規則）。
- **クライアント抜け**: BD部がクライアント欄を空にして備考にだけ書くケースがあり、要確認レポートにも出ていなかった。クライアント欄が空なら備考名でマッピング照合、それでも不明なら要確認レポートに必ず出す。マッピング表(2026/06/11時点)に無い取引先は電通総研に更新依頼。
- **新規のフェーズ**: 新規登録は必ず`New（新規）`になるため、新IDマップ(`--new-id-map`)指定の2段階目で`親案件_新規フェーズ反映_<label>.csv`(更新用)を出し、New以外のフェーズ(進行中受注済み/完了成立/完了不成立)を更新し直す。これを親案件_新規登録の後にインポートする。

関連: [[gbc_salesforce_pitch_import_csv_automation]]
