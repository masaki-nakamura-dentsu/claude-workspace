---
name: profit-split-app-datasource-reconnect-20260914
description: "利益スプリット登録アプリ(Power Apps)で2026-09-14に「'{GUID}'の表が見つかりませんでした」エラーが発生、Excelデータソース(SplitRequests/DeptMaster)の削除→再追加で解決"
metadata: 
  node_type: memory
  type: project
  originSessionId: c6504d5a-857e-4723-832d-7152265c3887
  modified: 2026-09-14T01:06:29.244Z
---

## 事象(2026-09-14)

利益スプリット登録アプリで「ネットワークからのデータ取得でエラーが発生しました: 名前 '{318B4A06-2710-4AF6-9FD5-19D8F280EEB1}' の表が見つかりませんでした」というエラーが発生。局員(藤井さん以外)から報告、中村さんも再現確認(アプリを開き案件名→スプリット前部署/金額を入力する段階で発生)。9/11に[[profit_split_app_headerno_month_collision_bug]]の恒久修正(「登録」ボタンOnSelect数式の複合キー化)を実施して以降、動作確認(TEST-0911)をしないまま放置していた期間に発生。

## 原因

Excelファイル(`GBC_アレココ - サイトドキュメント/設定関連/GBC利益スプリット管理表.xlsx`)内のテーブル自体(`SplitRequests`, `DeptMaster`、xr:uidはそれぞれ`{00000000-000C-0000-FFFF-FFFF00000000}`/`{00000000-000C-0000-FFFF-FFFF01000000}`)は正常に存在し、報告されたGUIDとは一致しなかった。つまりExcelファイル側の破損ではなく、**Power Apps側が保持しているExcel Online (Business)コネクタのテーブル参照(SharePoint/OneDrive側の内部テーブルID)が古くなっていた**とみられる。Power Apps Studioでデータソースの「更新」操作自体もエラーになったため、接続そのものが壊れていたことが裏付けられた。9/11の数式編集作業中に接続がどこかで切れた可能性が高いが、具体的なトリガーは未特定。

## 解決

aiconアカウントでPower Apps Studio編集画面を開き、データソース一覧から**SplitRequests**と**DeptMaster**(いずれもExcel Online (Business))を削除→「データを追加」で同じファイル・同じテーブル名で再追加。数式(ドロップダウンのItems、LookUp等)はテーブルの表示名で参照されているため書き直し不要で、再追加のみでエラー解消を確認済み。

## 教訓

- 「'{GUID}'の表が見つかりません」系のエラーは、Excelファイル/テーブル自体の破損ではなく**Power Apps側のデータソース接続(テーブル参照)の破損**を疑うこと。切り分けは「データソースの更新操作自体がエラーになるか」で判断できる。
- 直し方は該当データソースの削除→同名で再追加(数式の書き直しは通常不要)。
- **Power Apps Studioで数式(特にLookUp/データソース関連)を編集した後は、その場でプレビュー実行して動作確認するまでを一連の作業とすること** — [[profit_split_app_headerno_month_collision_bug]]の9/11修正でTEST-0911による確認が「実施待ち」のまま放置され、3日後に本番でエラーが表面化した。次回以降、Power Apps Studioでの修正作業は同日中にプレビュー確認まで完了させる。
