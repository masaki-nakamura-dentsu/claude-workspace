---
name: feedback-pbix-use-fresh-download
description: "Before diagnosing Power BI DAX/measure logic via pbixray, always get a freshly-downloaded .pbix from the user — a local copy from a prior session can be weeks stale and show renamed/old measure names that no longer exist live, causing wrong fixes"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f59e31aa-e666-43c9-8366-f94b36846583
  modified: 2026-09-10T04:35:07.729Z
---

2026-09-10、[[qbr_powerbi_case_collision_investigation_20260910]]の調査中、会社Macに残っていた`GBC戦略企画部_PowerBI数字管理/GBC数字管理レポート.pbix`(2026-08-07更新、約1ヶ月前)をpbixrayで解析して`案件別ブレンド値`メジューの修正コードを渡したところ、正樹さんが貼り付けた際に「'売上総利益_合計' の値を判断できません」エラーが発生した。原因は2026-09-09に別途「売上総利益→CAS売総」のリネーム作業が行われており、そのメジュー名が`CAS売総_合計`に変わっていたのに、古いpbixスナップショットにはこの変更が反映されていなかったこと。

**Why**: Power BI Serviceのブラウザ編集は都度クラウド上のセマンティックモデルを直接書き換えるが、ローカルに保存された`.pbix`ファイルは「その時点でダウンロードした」スナップショットに過ぎず、その後のService側の変更を一切反映しない。ローカルファイルの更新日時が古いほど、実際のライブモデルとの乖離リスクが大きい。

**How to apply**:
- Power BIのDAX/Power Query構造をpbixrayで調べる前に、手元に候補となる`.pbix`が複数ある(Downloads内に複数バージョン、旧作業フォルダに残骸等)場合は、必ず**最終更新日時を確認**し、直近でPower BI Service上での編集作業があった形跡があれば、古いファイルでの分析結果を「現在の状態」として断定しない。
- 可能な限り、分析の直前に正樹さんへ「最新のpbixファイルをダウンロードしてもらえますか」と頼み、そのファイルのタイムスタンプで鮮度を確認してから使う。
- 分析結果を元にDAX修正案を出す際も、"この分析は{日付}時点のスナップショットに基づいています。名前や構造が変わっていたら教えてください"と留保を添えるとより安全。
- 関連: [[feedback_give_full_code_not_partial_diffs]](同じ「外部システムの今の状態を直接見れない」という制約から生じる別のミスパターン)、[[qbr_powerbi_tableau_verification_20260906]](pbixray自体の使い方・venv構築)
