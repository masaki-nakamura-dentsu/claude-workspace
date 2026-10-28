# 新勤務データ: 太田さん(新担当)からのPredictions (Update)手動追加可否の質問に回答案
- Date: 2026-10-14
- Status: done
- 2609ファイルで確認: T/V列はPredictions(Update)のF列(combined_data)をY列キー(=CONCAT(F,A,B,K,I,C,H): 負担組織+JU+作業領域+社員名+扱組織+作業詳細+得意先)でXLOOKUPし、C(事業区分)/D(受益者)を返す。シートは29,653行、最終更新は2024年分のまま。
- _infer_missing_juekisha.pyはPredictionsを読まず末尾に追記するだけ(A列が埋まった最終行の次)。手動追加と競合しない。前月ファイルを複製して翌月を作るので追記は引き継がれる。
- 回答案: 手動追加OK。注意=A列必須・F列は区切りなしで完全一致(作業詳細の表記が変わると効かない)・ユニットNO未登録が原因ならJuekisha Table登録が本筋。
