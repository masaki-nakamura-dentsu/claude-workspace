---
name: qbr-cas-mikomi-source-report
description: GBC CAS見込_LATEST.xlsx / GBC CAS実績+見込_COMBINED.xlsxのForecastシート更新に使う正しいSalesforceレポートの特定方法。名前が紛らわしい貢献利益系v2.1と混同しないための注意
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b649a20-47dd-4bb5-8e3e-96d1f8aaed5d
  modified: 2026-09-06T00:44:23.566Z
---

## 紛らわしい罠: 「（QBR集計用）月別_貢献利益（仕掛）_v2.1」≠ CAS見込のソース

2026-09-06のQBR8月分更新で、[[cas_csv_download_automation]]/[[sf_reports_qbr_download_automation]]の自動DLパイプラインが持ってくる「（QBR集計用）月別_貢献利益（仕掛）_v2.1」(Salesforceレポート00O7F00000AycilUAB、[[qbr_2026q3_cas_koken_july_update]]で貢献見込・貢献実績COMBINEDのソースとして使ったもの)を、名前が似ているという理由でCAS見込のソースとして誤って使ってしまった。列に「GBC貢献売総(A)/(AB)/(ABC)」はあるが「GBC取設定/SETTEI TO(JPY)」列が無く、既存のCAS見込_LATEST.xlsxの列と一致しないのに気づかず、確度A列の値を代用してしまい、中村さんに訂正された。

**正しいソース**: マニュアル`(Manual) GBC QBR_Tableau20260401.docx`13行目に明記された「QBR集計用）月別_設定利益（仕掛）_v2.1」、Salesforceレポート**00O7F00000Ayt1TUAR**(`https://dgx.lightning.force.com/lightning/r/Report/00O7F00000Ayt1TUAR/view`)。列に`GBC取設定/SETTEI TO(JPY)`(16列目)と`GBC設定売総/SETTEI Rev(JPY)`(17列目)が両方あり、これがCAS見込_LATEST.xlsxとCOMBINEDのForecastシート双方の列と完全一致する。**このレポートは[[sf_reports_qbr_download_automation]]の自動DLパイプライン(reports_config.py)には登録されていない**——2026-08-25以降、山本高之さんが代替として「月別見込（設定売総/取設定 X 部署）」という部署×年月のピボットレポート2本を試作しパイプラインに追加したが(中村さんとの2026-08-25〜08-27のTeamsやりとり参照)、これらはピボット集計で案件ID・クライアント名・確度の内訳が無く、CAS見込_LATEST.xlsxの明細フォーマットには使えない。中村さんはこれを明確に却下し、都度00O7F00000Ayt1TUARを手動エクスポートする方式を指示した。

## 列マッピング(2026-09-06確定)

ソース(00O7F00000Ayt1TUAR、B列+D〜Q列=17列、C列はスペーサーなのでスキップ):
1 GBC案件ID, 2 案件ID, 3 クライアント, 4 案件名, 5 部署, 6 商流, 7 地域, 8 市場, 9 関係会社, 10 事業区分, 11 年度, 12 月, 13 確度, 14 フェーズ, 15 活動項目, **16 GBC取設定/SETTEI TO(JPY)**, **17 GBC設定売総/SETTEI Rev(JPY)**

- `GBC CAS見込_LATEST.xlsx`の`CAS見込_Original`(値のみ、17列そのまま)と`CAS見込`(**数式シート**——`=CAS見込_Original!A2`参照+ASC変換+C列だけXLOOKUP、S列=DATEVALUEの数式。値で直接上書きしてはいけない、[[feedback_openpyxl_formula_sheet_extend]]参照)の両方を更新。
- `GBC CAS実績+見込_COMBINED.xlsx`のForecastシート「売上総利益」列 ← ソース17列目`GBC設定売総/SETTEI Rev(JPY)`(マニュアル85行目に明記された対応、TOではなくRevの方を使う)。

## フィルタ条件

マニュアル11行目「年度と月のフィルターで過去の月のものを除外」——実務上は「年度=当年 AND 月>=実行月」。2026-09-06実行時は`年度=2026 AND 月>=9`で244件。ソースの生データには2024〜2026年の全期間(A/B確度のみ、検索条件で絞り込み済み)が含まれるので、必ずフィルタしないと過去分まで見込に混入する。
