---
name: globalq_2026_08_report
description: "Global Q access analysis report for August 2026 — generated, bug fixed, QA'd, done"
metadata: 
  node_type: memory
  type: work_status
  status: done
  date: 2026-09-08
  originSessionId: 459a9e29-16bd-41a2-9e5a-7ef18b25c357
  modified: 2026-09-08T06:31:29.438Z
---

## 2026-09-08
Status: done

8月分の Global Q アクセス分析レポート (`GlobalQ_access_report_2026_08.pptx`) を [[globalq_access_report_workflow]] のパイプラインで生成。

- 元データ: OneDrive の8月分PowerQuery処理済みExcel(当日13:55更新分)、8/1〜8/31フルカバー確認済み
- PV=6,181 / UU=1,342 / YTD PV=94,795 / YTD UU合計=13,470 / 最多アクセス日=2026-08-06
- 7月(PV 13,442)から大幅減だが、生データが31日分フルカバーしていることを確認済みで、パイプラインの不具合ではなく実際の減少と判断。
- `build_report.py` に恒久バグを発見・修正: テンプレートが既に14枚構成(全期間推移スライドを内包)の場合、`ensure_history_slides()`がin-place更新するためスライド物理位置が2つずれ、以降のハードコードされたスライドインデックス(`slides[4]`〜`slides[11]`)が全てズレて`KeyError`になっていた。7月生成時は旧12枚テンプレートからの初回挿入だったため気づかれず、今回が14枚テンプレートを使う初めての実行だったため発覚。`ensure_history_slides()`がpre-existing/insertedを bool で返し、`main()`側で `off = 2 if pre_existing else 0` を計算して以降の全インデックスに加算する形で恒久修正。詳細は [[globalq_access_report_workflow]]。
- 全14スライドをqlmanageで個別分割サムネイル生成し目視QA、全て正常(円グラフ2枚は既知のqlmanageレンダリング欠落で空表示になるだけ、データ自体は正常)。
- KNOWN_MONTHLY辞書に8月実績を追記済み(スクリプト内・メモリ内両方)。
- 生成後 `open` で自動オープン済み。
- 保存先: `Global Q/11_アクセス分析レポート/アクセス分析レポート/GlobalQ_access_report_2026_08.pptx`(パス訂正: 中村正樹直下ではなく `Work共有作業系/戦略企画部/Global Q/` 配下)。
