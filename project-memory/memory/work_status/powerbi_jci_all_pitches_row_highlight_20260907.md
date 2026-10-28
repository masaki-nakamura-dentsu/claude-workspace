# PowerBI: JCI_All_Pitches(内訳) 前月作成案件の行ハイライト

## 2026-09-07T00:00:00Z
Status: done
What: 正樹さんの依頼で、JCI_All_Pitches(内訳)ページの明細テーブルに「前月作成の案件行を薄いオレンジで網掛け」する機能を設計。JCI_Pitch_Base既存のCreatedDate列を使い、DAX計算列`行背景色_前月作成`(前月初〜今月初未満なら色、それ以外は白)を提案→初回は日本語VAR名(今月初/前月初)でDAXパーサーの構文エラー発生→VAR名を英数字(ThisMonthStart/LastMonthStart)に変更して解決。各列のセルの要素→背景色→フィールド値で本列を指定する手順を案内。正樹さんが色を#FBF2CB(薄い黄~オレンジ系)に決定・適用し、作業完了。
Next: —
