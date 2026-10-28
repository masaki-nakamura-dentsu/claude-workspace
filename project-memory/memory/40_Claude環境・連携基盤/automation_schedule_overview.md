---
name: automation_schedule_overview
description: 個人Mac/会社Mac/PowerBI上の全自動化タスクの実行スケジュール一覧(固定時刻もの+常時ポーリングもの)。Outlook登録用ICSの元ネタ、次回スケジュール確認時はまずここを見る
metadata: 
  node_type: memory
  type: project
  originSessionId: 24064df7-8ad4-4237-9afc-6c145606ca8d
  modified: 2026-08-26T07:51:44.303Z
---

2026-08-24、Outlook予定表登録用の.icsファイルを作るために両Mac+PowerBIの全自動化ジョブを棚卸しした結果。関連: [[personal_sns_management_project]] [[memory_weekly_review_automation]] [[continuous_data_capture_setup]] [[ai_teams_weekly_digest]] [[cas_csv_download_automation]] [[powerbi_migration_gbc_dashboard]]

## 固定時刻で動くタスク(ICSに登録済み)

**個人Mac(ICPTokyo2022)**
- `com.nakamura.timetreecheck` — 毎日7:30、TimeTree登録漏れチェック(Python直書き)
- `com.nakamura.memoryweeklyreview` — 毎週月8:30、Claudeメモリの重複統合レビュー
- `com.nakamura.snsdraft` — 毎週月・木8:00、個人SNS下書き自動生成 → **2026-08-24、本人の指示で停止済み**(`launchctl`で停止し`disabled/`フォルダへ退避、スクリプト本体は削除していない)

**会社Mac(d14461)**
- 会社Mac側の同期ヘルスチェック — 毎日14:00、メール/カレンダー同期状況+Teamsデーモン生存確認(個人Macの7:30チェックと対、Teams再起動はしない)
- `com.nakamura.sfreportspipeline` — 平日**9:00**/16:45(2026-10-05に朝枠を11:15→9:00へ変更、ユーザー依頼。補助リトライは朝9:30(旧13:00)・夕18:15)、GBC QBR用Salesforceレポート7本を自動ダウンロード([[sf_reports_qbr_download_automation]])。PowerBIのGBCダッシュボード更新(11:30/17:00)の15分前に実行し、更新前のSalesforceデータをスナップショット保存。2026-08-26構築、Gmailカレンダー(maxakisan@gmail.com)にも同時刻の予定を追加登録済み。
- 社内AI関連Teams週次ダイジェスト(`com.nakamura.aiteamsdigest`) — **設定方式が記憶上で食い違い、未確定**。(a)2026-08-18の記録は「StartInterval=21600(6時間おき)+スクリプト内部6日ガード」、(b)2026-08-19の記録は「StartCalendarIntervalで月曜8:00固定」。次回d14461に直接アクセスするセッションで`plutil -p ~/Library/LaunchAgents/com.nakamura.aiteamsdigest.plist`を実行して実際の設定を確認し、このメモを更新すること。ICSでは(b)想定で月曜8:00としてある。

**PowerBI Service(クラウド側、Macとは独立)**
- GBCダッシュボードのスケジュール更新 — 毎週月〜金、11:30と17:00 JST(Salesforceデータソース含む)

## 常時ポーリング系タスク(固定時刻なし、ICS非対応)

**個人Mac(ICPTokyo2022)**
- `com.nakamura.syncdaemon` — 単一常駐プロセス(KeepAlive+RunAtLoad)、20分おきループでOutlookメール同期・カレンダー同期・Facebook Messenger同期の3つをまとめて実行

**会社Mac(d14461)**
- Outlookメール・カレンダー同期 — 個別launchdジョブ(`emailsync`/`calendarsync`)、20分おき(StartInterval=1200)。個人Macのような単一プロセス統合(syncdaemon化)がd14461にも適用済みかは未確認。
- Teams監視(`teams_daemon.py`) — Playwrightで常駐ブラウザ(共有ボットブラウザport 9226経由)を保持し30分おきにポーリング、`~/TeamsExport/data/teams_messages.jsonl`に蓄積。ログインがMFA絡みで人手が必要になる場合あり([[feedback_avoid_mfa_churn]])。
- CAS月次実績自動取込パイプライン — 20分おきポーリング、「3/6/9/12月分は翌月の第3営業日、それ以外は翌月の第2営業日」の確定を検知した回だけ実処理(月1回相当だが固定日ではない)

## 除外したもの(実際には自動化されていない)
- 「GBC週報×知見まとめ→木村DMD送付」— 水曜夜の本番自動実行は2026-08-24時点で未着手(残作業)、実際に走っているタスクではないため今回のICSには含めていない

## How to apply
「週次/月次/常時で動いているタスクをまとめて」と聞かれたら、まずこのメモを見てから両Macのlaunchctl/plistで裏取りする(このメモ自体も裏取りの積み重ねなので、d14461側は特に鮮度に注意)。

## ICSファイルの運用(2026-08-26改訂)
以前は「個人Macのスクラッチパッドで都度再生成・再送」としていたが、**スクラッチパッドはセッション終了とともに消える一時ディレクトリ**であることが判明(2026-08-26、以前作った予定登録用icsをユーザーが見つけられず、誤ってGmailカレンダーに直接インポート済みのイベントを開いてしまう事故が発生)。**運用変更**: 今後はどちらのMacで作業していても、Dropbox上の`Claude作業フォルダ/自動化タスクスケジュール/`に実ファイルとして保存する(スクラッチパッドではなく)。SendUserFileはこのVSCode拡張環境で見えないことがある([[feedback_senduserfile_not_visible_in_vscode]])ため、SendUserFile送付と併せてこのDropboxパスへの保存・パス案内を必ず行う。GoogleカレンダーへのインポートはGoogle Calendar側の「設定→インポート/エクスポート」から行う(icsファイルをFinderでダブルクリックするとOutlookが既定アプリとして開いてしまい、意図しない結果になるため避ける)。

**追記 2026-10-05**: 会社Mac `com.nakamura.hdymonitor`(3時間おき、HDY海外動向収集)・`com.nakamura.hdydigest`(月曜8:45 Teams週報)を追加。個人Mac予備系は relay task-008。詳細 [[hakuhodo_overseas_intel_monitoring]]

**追記 2026-10-06**: Power Automate(aicon)「競合社定点観測(HDY)_定期更新」— 毎日 9:30/12:30/15:30/18:30 JST にPowerBIセマンティックモデル「競合社定点観測(HDY)」を更新。詳細 [[hakuhodo_overseas_intel_monitoring]]
- 2026-10-19 Agency OS月次チェック(com.nakamura.agencyosmonthlycheck、毎月第1営業日9:30、会社Mac)
- 教訓: 会社Macのlaunchdは 8:30〜21:30 の間に置く(21:45自動シャットダウン、朝8時台起動)。それ以外の時刻の予定は実行されない。
- 2026-10-19 Agency OS月次: 個人Mac 9:00(アレココ・CCS)/会社Mac 9:30確認・14:00(dentsu.dot等)。com.nakamura.agencyosmonthlyupdate(.company)
