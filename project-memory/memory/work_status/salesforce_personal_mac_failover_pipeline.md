# Salesforceレポート個人Macフェイルオーバーパイプライン構築

## 2026-09-06T00:55:00Z
Status: done
What: ユーザーからSalesforceレポートURL5件の自動ダウンロード追加依頼。既存の会社Mac(d14461)QBRパイプライン(`~/SalesforceExport/reports_pipeline/reports_config.py`)と照合し、4件は登録済み・1件(`00O7F00000Ayt1TUAR`「（QBR集計用）月別_設定利益（仕掛）_v2.1」)が新規と判明。続けてユーザーから「会社Macが動いていない場合は個人Macでも実行したい」との追加依頼があり、個人Mac(ICPTokyo2022)側に新規フェイルオーバー環境`~/SalesforceExport/reports_pipeline_personal/`を構築(`reports_config.js`/`download_all_reports.js`/`failover_check.js`/`run_failover_check.sh`)。共有ブラウザ(port 9227)経由でSalesforce Authenticator承認フローを含め9レポート全件を実機テストして成功を確認。launchd(`com.nakamura.sfpersonalfailover.plist`、20分間隔ポーリング)を登録し、会社Mac定時実行(平日11:15/16:45)から30分の猶予後、保存先Dropboxフォルダの最新ファイル日時をチェックして未実行なら個人Macが代行する仕組みを構築・動作確認済み。
Next: 次回平日の会社Mac定時実行(11:15/16:45)後、正常に「既に完了済み」判定でスキップされるか、および実際に会社Macが止まっていた場合に正しくフェイルオーバー実行されるかを`failover_log.txt`で継続観察。

## 2026-09-10T18:00
Status: in progress
What: セッション開始時にpersonal_mac_inbox.mdのtask-004(pending、会社Mac側の同時実行事故対策の移植)を自動検知、Statusをin_progressに更新。実装(プロセス排他ロック/前倒しスキップ確認/手動実行時のTeams確認省略/download.delete()追加)をバックグラウンドagentに委託し実行中。
Next: agent完了後、変更内容を確認しinboxのResultに記入、Statusをdoneに更新。

## 2026-09-10T18:15
Status: done
What: task-004完了。プロセス排他ロック(pipeline.lock)、Teams確認省略(--from-followerフラグ)、download.delete()追加、~/Downloads蓄積ファイル削除を実装・テスト済み。前倒しスキップ判定は既存実装で対応済みと確認。inboxのStatus/Resultを更新済み。
Next: 次回定時実行(平日11:15/16:45)での実地検証待ち。
