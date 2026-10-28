# カレンダー同期スタック調査(2026-09-11)

## 2026-09-11T07:55:00+09:00
Status: done
What: ユーザーから「9/30, 10/7, 10/14, 10/28, 11/5の夜の予定がTimeTreeチェックに反映されない、Outlook読み込みかTimeTree登録どちらの問題か」と質問。調査の結果、Outlook側の問題と判明: `com.nakamura.syncdaemon`(永続デーモン)のカレンダー同期が2026-08-31から11日間、同じ5件のスナップショットCSVで`Errno 11`エラーを毎サイクル起こし続け、`calendar_events.json`が完全に停止していた。対話的に`sync_calendar_export.py`を実行しバックログ解消(新規63件・更新172件)。9/30(澤本会19:00)と11/5(サンドアート演奏19:00)はOutlookに存在(今回復旧)。10/7, 10/14, 10/28はOutlook・TimeTree双方に該当する夜予定が一切存在せず、単に情報未記録と判明。
Next: 10/7・10/14・10/28の予定内容についてユーザー回答待ち。9/30・11/5のTimeTree登録要否もユーザー確認待ち。

## 2026-09-11T08:10:00+09:00
Status: done
What: ユーザーから「Outlook同期不良を本格的にデバッグしてほしい」と依頼。11日間100%失敗という決定論的なパターンを確認、TCC.db直接読取は権限拒否で不可。`sync_calendar_export.py`に「特定スナップショットが2時間以上読めない場合にchime+work_status(blocked)で警告」する仕組みを追加(既存ロジックのバグを単体テストで発見・修正済み、本番実行で正常動作確認済み)。
Next: 根本原因の追加調査待ち。

## 2026-09-11T08:30:00+09:00
Status: done
What: ユーザーから2つの依頼: (1)TimeTree登録漏れ候補をTeams Webhookでも通知する、その際の判断の伝え方も明記する (2)Outlook同期問題をWeb検索含めて広く再調査、フルディスクアクセスは最終手段とする。
対応(1): 既存の`TEAMS_WEBHOOK_URL`(~/.zshenv、teams_webhook_powerautomate memory参照、新規PowerAutomate構築不要)を`timetree_check.py`に`notify_teams()`として統合。`run_daily_check.sh`に`source ~/.zshenv`を追加。テスト送信でHTTP 202確認済み。Teams通知本文に「判断はTeams返信ではなくClaudeとのチャットで伝えてください」と明記。
対応(2): Web検索の結果、xlwings/rdiff-backup/duplicacy等の独立プロジェクトで同一症状が広く報告されている既知のOneDrive-macOS問題と判明。Microsoft Q&Aに「Files On-Demand/Free Up Spaceが原因、フォルダを「このデバイスに常に保持」に変更すると解消」という実例あり — FDA不要の未試行の対策として最有力と判断、ユーザーに提案。
Next: ユーザーがTeams通知を受信できたか確認、OneDriveのFiles On-Demand設定を試すかどうかの判断待ち。

## 2026-09-11T08:20:00+09:00
Status: done
What: ユーザーからTeams通知の受信確認と、Calendarフォルダを「このデバイスに常に保持」に変更した旨の報告。並行してsyncdaemonのログを確認したところ、メール同期(`sync_power_automate_export.py`)も同一のErrno 11問題で2026-09-02から9日間・520件(Inbox457+SentItems63)スタックしていたことを発見。ユーザーも独自に同じバックログに気づき、Inbox/SentItemsフォルダも「このデバイスに常に保持」に変更済み。対話実行でバックログ解消(517件マージ)。カレンダー同期で作成した警告の仕組み(chime+Teams+work_status)を`sync_power_automate_export.py`にも移植。さらに、常駐デーモン(`com.nakamura.syncdaemon`)はlaunchdから直接python3を起動する構成のため`~/.zshenv`のTEAMS_WEBHOOK_URLを読み込めていなかったことが判明、`~/SyncDaemon/run_daemon.sh`というラッパーを新設しplistを変更、再読み込みして環境変数が正しく渡ることを確認済み(1サイクル正常完了)。Inbox内に3件、旧形式(IDマーカーなし)のためスキップされ続ける無害な孤立ファイルを発見(2026-07頃の残骸、緊急性なし)。
Next: 「このデバイスに常に保持」設定変更が実際にErrno 11を解消するか、数日間の自然発生を観察して確認。

## 2026-09-11T08:35:00+09:00
Status: done
What: ユーザーから「会社Macでも同じ仕組みにして」と依頼。`~/CalendarExport`/`~/OutlookExport`はDropbox共有symlinkのため、`sync_calendar_export.py`/`sync_power_automate_export.py`のコード修正自体は既に会社Mac側にも自動反映されているはず。ただし`~/SyncDaemon/run_daemon.sh`(新設ファイル、Dropbox外)とlaunchd plist、および会社Mac固有のOneDrive「このデバイスに常に保持」設定はDropbox共有されないため、`.claude-sync/claude_relay/company_mac_inbox.md`にtask-002として詳細な引き継ぎタスクを投入(会社Macの実際の同期アーキテクチャ確認→同様のラッパー方式適用→動作確認、およびOneDrive設定変更をユーザーに案内する旨を含む)。次回会社Macでのセッション開始時に自動的に拾われる想定([[mac_handoff_relay]])。
Next: 会社Mac側セッションでのtask-002実行結果待ち。ユーザーには会社Mac使用時にOneDriveの「このデバイスに常に保持」設定を手動で行うよう伝達済み。
