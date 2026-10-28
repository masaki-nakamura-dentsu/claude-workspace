## 2026-08-21 セッション: クライアント名_調整後 突合漏れの根本対応 + 検証用クエリ削除

**Status: done**

1. 検証用クエリ5件(`貢献実績_SF_TEST`/`貢献実績_SF_TEST_合計チェック`/`貢献実績 合計チェック`/`貢献実績_SF_TEST_2`/`貢献実績用_2`)を正樹さんが削除・保存、エラーなし確認済み。
2. `クライアント名_調整後`の突合漏れ(CAS見込 272行中82行のみマッチ、8/19発見)を根本対応。DAXクエリビューでCAS見込の未マッチクライアント名59件を抽出→正規化突合で51件自動解決→残り8件を正樹さんと個別確認→マスタファイル`Client Name_CAS_SF_FY22 TO DATE.xlsx`に59行追加+既存2行修正(NCSOFT CORPORATION→NC CORPORATIONへ統合)。openpyxl保存バグ対策(fix_empty_v+Excel再計算パス)を実施し、他シートの数式キャッシュ無傷を確認済み。

詳細はproject memory `powerbi_migration_gbc_dashboard.md`末尾「`クライアント名_調整後`突合漏れの根本対応 完了」節を参照。

**次回**: Power BIスケジュール更新後、DAXクエリ`EVALUATE SUMMARIZECOLUMNS('CAS見込'[月別見込親案件: クライアント/Client], 'CAS見込'[クライアント名_調整後])`を再実行し空欄が減ったか確認(未実施)。
