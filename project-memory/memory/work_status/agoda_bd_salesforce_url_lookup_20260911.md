# Agoda重複案件/BD部数字確認 Salesforce URL照会

## 2026-09-11T00:00:00+09:00 (概算)
Status: done
What: ユーザーから「BD部の数字で確認が必要なもの(2025年の貢献利益の件と、1月〜3月で案件がダブっている件)のSalesforce URL」を聞かれた。メモリ([[qbr_powerbi_case_collision_investigation_20260910]])には経緯の記述はあったがレコードURLは未保存だったため、共有ブラウザ(port 9226、Salesforceログイン済み)でその場検索して特定。
- Agoda Media AOR重複(BD部、2026年1月〜3月で期間重複): 小池和雄さん作成分(2025/10〜2026/03) https://dgx.lightning.force.com/lightning/r/a1hGA00000A0GcSYAV/view 、新保泰史さん作成分(2026/07〜) https://dgx.lightning.force.com/lightning/r/a1hfP000005geW5QAI/view
- BD部の2025年度貢献実績(前年度実績)667M vs 874M乖離([[kpi0909_bd_zenendo_jisseki_error_20260910]])は特定の案件レコード1件に紐づくものではなく、部署集計の突合問題だったため、単一のSalesforce URLはない旨をユーザーに回答。参考として部署別レポート「BD部」(00O7F00000AyTigUAF)のURLを案内。
検索手法は[[salesforce_adhoc_record_search_technique]]に新規保存。

## 2026-09-11T00:30:00+09:00 (概算)
Status: done
What: 正樹さんが両件とも確認を取った結果を報告。(1) 2025年度貢献実績667M vs 874Mの乖離 → Power BI側(667M)が正しく、同僚のExcel数字(874M)が誤りと確定。[[kpi0909_bd_zenendo_jisseki_error_20260910]]に確定事項を追記済み。(2) Agoda Media AOR重複登録 → そのままでOKという業務判断で決着、統合等の対応不要。[[qbr_powerbi_case_collision_investigation_20260910]]に解決確定を追記済み。
続けて、`2026パイプライン 0910.xlsx`のG18/G21修正を提案したところ、正樹さんから「まだ修正しなくてよい、同僚が次回更新時に自分で直す」と明示的な指示。Claude側からは能動的に触らない方針を[[kpi0909_bd_zenendo_jisseki_error_20260910]]に追記済み。
Next: なし、両件クローズ。xlsx修正は同僚の対応待ち(Claude側アクションなし)。
