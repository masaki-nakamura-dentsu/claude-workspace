---
name: feedback_kgikpi_blank_anken_means_crosstable_lag
description: KGIKPIの案件別内訳で(空白)が急増したら、まず月次Crosstable更新(受発注設定リスト)の未反映を疑う
metadata:
  type: project
---
2026-10-07、CAS実績_案件別内訳の売総ランキングで(空白)が47.0Mでトップに。原因は9月CAS実績は取込済みなのに【９月】受発注設定リスト(10/2受信)が [[qbr_crosstable_monthly_update_process]] でCrosstableに未反映だったこと。案件名は Raw YTD の PQ で 受発注ヘッダNo→CAS_SF_Crosstable→SF案件リスト の結合で付くため、ヘッダ未登録=案件名・部署名・地域・市場も空白になる。
**Why:** CAS実績取込([[cas_csv_download_automation]])とCrosstable更新が別運用で、後者がオンデマンド実行のため月初に遅れが出る。
**How to apply:** 診断は `~/PowerBIExport/pbix/q.py` で案件名空白×計上年×ヘッダNoをDAX集計([[gbc_kpikgi_sharepoint_export]]の技法)→ローカルCrosstableにヘッダNoがあるか確認。恒常的な小口空白(「SF登録無し」行、振替原価)は仕様。Python は /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 (playwright入り)を使う。

## 追記 2026-10-07
- PBIのデータ更新はBotブラウザのトークンで `POST /groups/{ws}/datasets/{id}/refreshes` が通る(`~/PowerBIExport/pbix/refresh.py start|status`、所要約6分)。
- 案件ランキング系の「テーブルと棒グラフの順位が違う」は (1) 確度別行 vs 案件合計の粒度差、(2) 案件別ブレンド値のSELECTEDVALUE(案件ID)が同名複数IDでBLANK化、の2種。後者はSUMX(VALUES(案件ID))化で解消(修正版DAX: Claude作業フォルダ/KGIKPIレポート_案件ランキング不一致/)。
- PBIデータセットのスケジュール更新: 平日10:00/17:00 JST(有効)。
- 「前月を自動選択するスライサー」は月テーブルに TODAY() ベースの「前月」ラベル列を追加する方式で提案(2026-10-07)。DEFINE COLUMN(クエリ内列)で検証すると、FILTER(ALL('Raw YTD'))の拡張テーブル上書きが効かず数値がずれる→クエリ内列のテスト固有の挙動。月ラベルのコピー列でも同じずれが出ることで確認。実モデル列で確認すること。
- 2026-10-07 前月自動選択は実装済み(ユーザー適用): 月[月選択]計算列 + 年は非連結計算テーブル「年選択」(年ラベル「前月の年」)+3メジャーのSelectedYearをCOALESCEで年選択優先に。年スライサーをRaw YTD[計上年]のまま「前月の年」列を作るとFILTER(ALL('Raw YTD'[計上年]))で外れず前年値が消えるため非連結テーブル方式にした。
- KGIKPIアプリの初期表示がレポート保存状態と違う場合は、(1)アプリ未更新 (2)閲覧者ごとの永続的フィルター を疑う(2026-10-07、指標スライサーは全ページCAS売総保存済みだった)。
