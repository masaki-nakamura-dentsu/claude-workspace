# 週次業務報告(Salesforce)ドラフト作成 + メール自動同期の不具合対応 + カレンダー取り込み基盤構築

## 2026-07-23T17:45（JST目安）
Status: done
What: ユーザーから今週分のSalesforce業務報告ドラフト依頼。Teams/メール履歴と[[gbc_department_move_2026]]を突き合わせて既存案件の更新候補・新規登録候補を提示。その過程でユーザーがPower Automateのフロー実行履歴（全件成功）とClaudeが見ていた`parsed_emails.jsonl`（2026-07-15で停止）の食い違いを指摘。調査の結果、フロー自体は正常でOneDriveの`PowerAutomateExport/{Inbox,SentItems}/`には最新分まで届いていたが、マージ用スクリプト`sync_power_automate_export.py`が7/15以降手動実行されておらず放置されていたのが原因と判明（[[continuous_data_capture_setup]]参照、詳細記載済み）。353件を手動同期して復旧、さらに`~/Library/LaunchAgents/com.nakamura.emailsync.plist`を新規作成し`launchctl load`で1時間おきの自動同期をセットアップ（読み込み確認済み）。あわせてInboxの###FROM###バグが修正済みであることも確認。メール分（7/20-7/23、190件超）を踏まえて業務報告を再構成し、GBC利益スプリットアプリの正式運用開始案内、Global Q「グローバル対応部署紹介」の更新作業、社員食堂コラボ企画の生存確認、Salesforceインポート実績を追加。
Next: ユーザーがSalesforceへ実際に反映。

## 2026-07-23T18:10（JST目安・続き）
Status: done
What: ユーザーから「メールの集約フォルダはどこか」の質問に回答（`~/OutlookExport/parsed_emails.jsonl`が本体、OneDrive `PowerAutomateExport/{Inbox,SentItems}` が着地点、1時間毎同期で更新）。続けて、旧手動エクスポートの生`.eml`フォルダ（`.claude-sync/data-export/OutlookExport/{Inbox,SentItems}`、計1.9GB・5,749件）を削除してよいか相談され、既にparsed_emails.jsonlに取り込み済み（1件だけ解析失敗でロスト、添付ファイル等の原本は失われる点を明示）である旨を説明。ユーザー承諾を得て`osascript`経由でFinderのゴミ箱に移動（`rm`ではなく安全な形で実施、削除後に元フォルダから消えたことを確認）。
続けて、メールだけでなく**スケジュール（Outlookカレンダー）**もClaudeが理解できるようにしてほしいとの依頼。メールと同じPower Automate→OneDrive→Pythonのアーキテクチャを踏襲し、以下を構築:
- OneDrive着地フォルダ`~/Library/CloudStorage/OneDrive-電通/PowerAutomateExport/Calendar/`を作成
- Dropbox共有フォルダに`CalendarExport`を新設し`~/CalendarExport`をシンボリックリンク化（最初からクロスMac対応、後日の移行作業が不要な設計）
- `~/CalendarExport/sync_calendar_export.py`（最新スナップショットCSVのみパースしてJSON化、古いCSVは自動削除。メールの手作り区切り文字と違い`Create CSV table`ネイティブアクション＋`csv.DictReader`でエスケープ問題なし）
- `~/CalendarExport/POWER_AUTOMATE_SETUP_CALENDAR.md`：ユーザーがPower Automateポータルで構築するための手順書（繰り返しトリガー1時間毎→Get calendar view of events (V3)→Create CSV table→OneDrive ファイルの作成、直近3日〜60日先のスナップショット方式）
- `~/Library/LaunchAgents/com.nakamura.calendarsync.plist`を作成・`launchctl load`済み（1時間毎、動作確認済み＝現時点では「スナップショットなし」と正しく報告）
[[continuous_data_capture_setup]]に新セクション追加済み。
Next: **ユーザー側のアクション待ち** — Power Automateポータルで`POWER_AUTOMATE_SETUP_CALENDAR.md`の手順に沿ってフローを作成してもらう必要あり（Claudeはポータルを直接操作できない）。次回セッションで`~/CalendarExport/calendar_events.json`にデータが入っているか確認すること。

## 2026-07-23T18:20（JST目安・続き）
Status: done
What: ユーザーから、カレンダー取得範囲を「直近3日〜60日先」から**「直近30日前〜1年先（365日）」**に広げてほしいとの依頼（先々の予定も多いため）。`POWER_AUTOMATE_SETUP_CALENDAR.md`内の`addDays`式（開始: `-30`、終了: `365`）と説明文を修正、[[continuous_data_capture_setup]]の該当記述も同期して更新。まだPower Automateフロー自体は未作成（ユーザー側作業待ち）なので、ローカルのPythonスクリプト側に変更は不要（フローの`Get calendar view`アクション設定のみに影響）。
Next: 変わらず、ユーザーがPower Automateポータルでフローを作成するのを待つ。作成時はこの新しい日数（-30/365）で設定してもらう。

## 2026-08-23T10:45(JST目安)
Status: done
What: ユーザーから「`PowerAutomateExport/Inbox`と`SentItems`はもう不要なら削除したい」と質問。調査の結果、まだ現役のメール自動取り込み受け皿と回答(削除しないよう案内)。ただし調査中に同期停止(8/13以降`parsed_emails.jsonl`未更新、1,342件滞留)を発見。同日別セッションでcalendar側も同じ症状(OneDrive File Providerハング)が起きて解決済みだったことが判明——今回はdaemon再起動だけでは直らず、OneDrive.appの完全再起動(ユーザー承認済み)が必要だった。応急バックフィルスクリプト(per-file timeout+全体900秒予算)を2回実行し、Inbox 1239→3件・SentItems 103→0件まで解消、315件を`parsed_emails.jsonl`に新規反映(7225→7854行)。通常のsyncdaemonも正常サイクルに復帰済み。詳細は[[continuous_data_capture_setup]]の2026-08-23後続セクションに記録。
Next: なし(完了)。次回同じ症状が出たら、まずdaemon再起動→ダメならOneDriveアプリ再起動、の順で試す。
