# 個人Mac Salesforceバックアップを dentsu.co.jp 用ブラウザ(9231)へ切替 (2026-10-12)
Machine: 個人Mac(ICPTokyo2022) / Status: done
- download_all_reports.js を dentsu-work-bot / port 9231 に変更済み、Teams事前確認は9227に別接続。
- dentsu-work-bot のMyAppsログイン切れ → 画面表示してユーザーにログイン依頼中。ログイン後: 単体テスト→画面外に戻す→本日9:00枠の欠け分補完を確認。
- 完了(09:41): ユーザーログイン→単体テスト成功→本日9:00枠を補完(16/17→残り1本補完で18/18)。ブラウザは画面外に戻した。
- 追加(10:00頃): ユーザー指示でブラウザをアカウント別に使い分けるルールと作業対応表を browser_account_routing.md に記録。9227に残る会社アカウント作業(Teams/Outlook CLI/GBC週報/Dify)は未移行。
- 追加(10:20頃): ユーザー了承で会社アカウント作業(Teams CLI/Outlook CLI/GBC週報/AIダイジェストbackup/SF事前確認/Dify)を9231へ一括移行。ユーザーが3サービスにログイン、teams list・outlook listで確認済み。
- 追加: ユーザーがターミナルで teams list を実行し動作確認完了(2026-10-12)。
- セッション終了(2026-10-12): 学び(RunAtLoad再読込の手順、Teams新URL)をメモリに保存済み。
