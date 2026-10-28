# GBC Intelligence Engine: 元データURL付与 + 局員プロフィール統合 (2026-08-18)

## 2026-08-18T19:15
Status: done(今日の範囲としては完了。次回以降に続きあり)
What: 前日構築したSQLite統合検索(doc_cards+case_records)に(1)元データへの
直接URLを付与(SharePointは既存evidence.url活用、Salesforceは新規レポート
「GBC全履歴_知見集約用」にGBC案件/Items:ID列を追加して取得、元の週報レポートは
変更せず保護)、(2)FTS5の日本語トークナイズ不良(「英国」2文字クエリが引けない)
を発見しLIKEベースの検索に切り替え、(3)SharePoint「今週の注目局員」局員紹介
ページ(海外経験・趣味情報、39名分)を新規スクレイピングしstaff_profilesテーブル
として統合。3ソース統合・URL付き・LIKE検索(数十ms)が完成形。
Next: 検索インターフェースの本格化(現状CLIのみ)、Salesforce/局員データの
定期更新の自動化、が次回候補。中村さんにまだ未確定と伝達済み。
