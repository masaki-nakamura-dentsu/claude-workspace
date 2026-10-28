---
name: globalq_2026_07_report
description: "Global Q access analysis report for July 2026 — generated, QA'd, done"
metadata: 
  node_type: memory
  type: work_status
  status: done
  date: 2026-08-05
  originSessionId: e6c84660-666a-4ff9-afa6-ec2fea9c2802
  modified: 2026-08-05T05:12:21.204Z
---

## 2026-08-05
Status: done

7月分の Global Q アクセス分析レポート (`GlobalQ_access_report_2026_07.pptx`) を [[globalq_access_report_workflow]] のパイプラインで生成。

- 元データ: OneDrive の7月分PowerQuery処理済みExcel(当日11:05更新分)
- PV=13,442 / UU=2,522 / YTD PV=88,614 / YTD UU合計=12,128 / 最多アクセス日=2026-07-15
- `build_report.py` にバグを発見・修正: ヒートマップスライドの図形名が、テンプレートが「一度でも本スクリプトで生成されたpptx」だと `オブジェクト6`(OLE)ではなく `Table 6`(ネイティブ表)になっており、KeyErrorで停止していた。フォールバック追加で解消(スクリプトに恒久反映済み)。
- qlmanage で表紙・サマリ・ヒートマップ・Appendixスライドを目視QA、問題なし。

### 追記(同日、続きの依頼): 全期間PV/UU推移スライドを追加
ユーザーがTableauの「運用開始(2019年11月)〜現在」のPV折れ線・UU棒グラフのスクリーンショットを提示し、レポートにも追加してほしいと依頼。
- `aggregate.py` に `full_history_monthly()` を追加(2019-11〜対象月を月次集計、検証済みロジックを流用)。値はTableauのグラフ形状と完全一致を目視確認(2020年4月ピーク9,393PV、2021年4月ピーク2,667UU、2025年9月ピーク19,869PV、2025年8月欠測=Tableau側も同じNULL、など)。
- `build_report.py` に `ensure_history_slides()` を追加し、YTDスライドの直後(4,5枚目)に「月別PV推移(全期間)」「月別UU推移(全期間)」を新規挿入。来月以降はこの2枚が既に存在する状態でテンプレートを引き継ぐため、自動的にデータ更新のみで済む(スライド再作成なし)設計。詳細は [[globalq_access_report_workflow]] に記載。
- 生成中にバグ発見・修正: UU側の「過去最多」箇条書きがPVの数値を誤表示(history[peak_uu_ym][0]をUUとして表示していた→[1]に修正)。
- 最終的に14枚構成のpptxを再生成、全スライドをqlmanageで目視QA、問題なし。
- 保存先: `Global Q/11_アクセス分析レポート/アクセス分析レポート/GlobalQ_access_report_2026_07.pptx`、生成後 `open` で自動オープン済み。
- KNOWN_MONTHLY辞書に7月実績を追記済み(スクリプト内・メモリ内両方)。

### 追記(同日、続きの依頼): 生ログ2種をTableauFileフォルダへ自動コピー
ユーザーから「今後はレポート作成時に、その月の生ログ2ファイルも `Global Q/7_アクセスログ／メール設定/LogFiles:TableauFile` へ同時にコピーしてほしい(Tableauでそのまま開けるように)」と依頼。
- 7月分は既にユーザー側で手動コピー済みだったことを確認(diff -qで完全一致)。
- `aggregate.py` に `raw_log_source_files()`(日付範囲名ファイル+PowerQuery処理済みファイルの2つを特定)と `copy_raw_logs_for_tableau()`(同名同サイズなら skip、冪等)を追加。`build_report.py` の `main()` 末尾で自動呼び出しするよう恒久組み込み済み。来月以降は手作業不要。詳細は [[globalq_access_report_workflow]]。
