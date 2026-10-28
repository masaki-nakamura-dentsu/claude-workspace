
- 2026-10-20 SF自動DL確認: 会社Mac9時枠未実行→個人Macフェイルオーバー4回とも0/18失敗(saveAs ENOENT/ブラウザclosed)。0バイト1件。Status: done(確認のみ)
- 11:23 個人Macで手動実行→18/18成功(1本は再実行で回収)。0バイト1件削除。原因: 共有ブラウザ(9231)が落ちていた。Status: done
- 11:25 修正: 個人Mac download_all_reports.js 保存を.part→検証→renameに、ファイル名を「レポート名-日時.xlsx」に。単体テストOK。bak_20261020あり。会社Mac版は未修正。Status: done
- 11:30 company_mac_inbox task-019 投入(会社Mac版修正+PowerBI影響チェック)。
