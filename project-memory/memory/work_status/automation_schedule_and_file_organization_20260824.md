# 自動化タスクスケジュール棚卸し・Outlook用ICS作成・ファイル整理

## 2026-08-24T23:00:00+09:00
Status: done
What: (1) 個人SNS下書き自動生成(com.nakamura.snsdraft)を本人の指示で停止(launchctl停止+plistをdisabled/へ退避)。(2) 両Mac(個人/d14461)+PowerBI Serviceの全自動化ジョブを棚卸しし、Outlook予定表インポート用ICSファイルを作成([[automation_schedule_overview]]参照)。(3) CAS月次実績自動取込の確定日をjpholidayで実際に計算し、今後18ヶ月分を個別イベントとしてICSに登録(「だいたい月初」の目安表記から正確な日付に変更)。(4) AI関連Teams週次ダイジェストのスケジュール方式(6時間おきポーリング vs 月曜8:00固定)が記憶上で食い違っており未確定のまま残した。(5) Dropboxルート直下に散らばっていたClaude作成ファイルを`Claude作業フォルダ/<タスク名>/`配下に整理([[feedback_claude_work_folder_organization]])。(6) SendUserFileがこのVSCode拡張環境で本人に見えない不具合を確認、Dropbox実パスへの直接コピー方式に切替([[feedback_senduserfile_not_visible_in_vscode]])。
Next: 次回d14461に直接アクセスするセッションでcom.nakamura.aiteamsdigest.plistの実際の設定(StartInterval vs StartCalendarInterval)を確認し、[[automation_schedule_overview]]とICSを更新すること。ICSのCAS個別イベントは18ヶ月分のみのため、期限が近づいたら同じjpholiday手法で追加分を生成すること。
