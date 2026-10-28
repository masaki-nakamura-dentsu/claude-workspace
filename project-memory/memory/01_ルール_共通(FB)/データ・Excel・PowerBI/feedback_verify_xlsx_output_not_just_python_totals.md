---
name: feedback-verify-xlsx-output-not-just-python-totals
description: openpyxlで作ったxlsxは保存後に読み戻し/LibreOffice再計算で実セル値を検証する（Python側の集計だけで完了報告しない）
metadata:
  type: feedback
---
2026-10-04 ベトナム出張経費一覧の初版で、行書き込みの列オフセットずれにより金額がJ列でなくK列に入り、Excel上の円換算・合計が全て0になっていた。完了報告はPython内の別計算の合計で行っており気づかなかった（ユーザー修正依頼時に発見）。
**Why:** スクリプト内の検算は出力ファイルの正しさを保証しない。
**How to apply:** xlsx生成後は必ず (1) 先頭数行をopenpyxlで読み戻して列位置確認、(2) LibreOffice headlessでcsv変換し数式の計算結果を確認してから報告する。関連 [[feedback_xlsx_recalc_type_check]]
