# JCIピッチ 11月依頼用 更新依頼シート作成 (2026-10-27)
Status: done
- openpyxlは `python3 -m pip install openpyxl` で既定python3(3.14 Framework)に再導入
- 最新SFデータ: ~/SalesforceExport/reports_pipeline の download_one_report を共有ブラウザ(9226)で呼び id=00OfP00000Cq0rRUAR / folder="APAC Pitch - List All_v1.31" をDL(承認不要で即DL)→ AllpitchList_Original へコピー
- `python3 update_pitch_list.py` 実行(約2分): 458行→429行削除、残り約29行(先月10月依頼用は約31行で妥当)
- 出力: BD部集約_JPターンアラウンド/11月依頼用　日系ピッチ案件リスト20261027.xlsm
- 前回のExcel固まりは、起動直後のダイアログ/フリーズが原因だった(Excel終了後は正常)

## 追補 (同日)
- ユーザーが列幅調整済みの11月依頼用ファイルを上書き保存 → AQ6(a1hGA00000A0Qd1)の行をExcelで削除(元ファイルに直接)
- Format/日系ピッチ案件リストフォーマット依頼ver20261027.xlsm を新規作成(AO=32.33, AP=34.5。他列は変更なし)。update_pitch_list.py は最新verを自動選択
- update_pitch_list.py に削除後の行高さautofit(6行目〜残り最終行)を追加(bak_20261027あり)
