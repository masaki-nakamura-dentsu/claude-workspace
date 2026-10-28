# QBR CAS売総レポート作成・Tableau/PowerBI数字不一致調査

## 2026-09-09T09:00:00+09:00
Status: in progress
What: CAS売総_実績見込vs予算MonthlyReportの8月版作成を依頼された。既存pptxの構成(全8スライド)を調査、スライド2/3/5/6はTableau書き出し画像でClaudeからは作成不可、スライド4/7はCOMBINED.xlsxから再現可能と切り分け。
Next: スライド4/7の表を再現するか、ユーザーの回答待ち。

## 2026-09-09T14:00:00+09:00
Status: in progress
What: ユーザーがTableau更新中にPowerBIとの数字不一致を報告。`8. CAS実績_見込比較 V1.0.twb`の「案件ランキング」チャートでNULL案件名バグと重複計上バグ(セブン/資生堂等4クライアントペア、2022-2025年で¥36,278,393)を発見・修正。`GBC CAS実績+見込_COMBINED.xlsx`から189重複行を削除し、2025年実績がRaw YTD(436M)と一致することを確認。
Next: Power BIと同じSalesforce案件名粒度でのランキング再構築(SF案件リスト経由の新ファイル`GBC CAS実績+見込_COMBINED_SF案件名版.xlsx`作成、twb接続先差し替え)。

## 2026-09-10T12:00:00+09:00
Status: blocked
What: Power BI側の「案件別ランキング(実績+見込ブレンド)」チャート(`案件別ブレンド値`メジュー)でも実績過少表示バグを発見。DAX計算列ALL()バグ→年フィルタ欠落→110組のSalesforce案件ID大文字小文字衝突(18桁→15桁切り詰めが原因)、と3段階で原因を掘り下げ。応急のEXACT()修正では`案件_Dim`自体のID誤り起因の症状が直らないと判明し、本格対応(18桁化、Power BI内3箇所+外部update_crosstable.py 1箇所)の必要性を確認したが未着手。ユーザーは「本当にこれが原因か確証がない」と懐疑的で、根拠(なぜ今まで顕在化しなかったか、なぜTableauは無事か)を説明済み。詳細は[[qbr_powerbi_case_collision_investigation_20260910]]参照。ユーザーはここで新しいチャットに移行する意向。
Next: 新セッションで、他の衝突ペアでの再現検証か(B)の段階的着手を相談してから対応開始。
