# 利益スプリットアプリ データソースエラー(2026-09-14)

## 2026-09-14T01:08:59Z
Status: done
What: 利益スプリット登録アプリで「'{318B4A06-2710-4AF6-9FD5-19D8F280EEB1}'の表が見つかりません」エラーが発生し局員から報告。調査の結果、Excelファイル自体は無傷で、Power Apps側のExcelデータソース(SplitRequests/DeptMaster)接続が破損していたと判明(9/11の[[profit_split_app_headerno_month_collision_bug]]恒久修正後、動作確認未実施のまま3日放置していたのが一因の可能性)。ユーザーがaiconアカウントでPower Apps Studioを開き、両データソースを削除→再追加(再リンク)してエラー解消を確認。project memory `profit_split_app_datasource_reconnect_20260914.md` に原因・対処・教訓を記録済み。
Next: — (ユーザー側で保存・公開、公開後のテスト登録、局員への展開は対応予定)
