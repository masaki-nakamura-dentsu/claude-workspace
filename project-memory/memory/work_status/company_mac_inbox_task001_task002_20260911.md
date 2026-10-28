# 会社Mac(d14461) company_mac_inbox.md task-001/task-002処理

## 2026-09-11T09:06
Status: done
What: 「hello」に応答(company_mac_inbox.md未確認のまま——本来は自動確認すべきだった、ユーザーに指摘されて修正済み)。続けてユーザー指示で同inboxを確認しtask-001(共有ブラウザのminimized→normal+off-screen統一)・task-002(カレンダー/メール同期のTeams通知+スタック検知の会社Mac適用)の2件pendingを検出、両方in_progressに更新して着手。
Next: task-001/task-002を実施する

## 2026-09-11T09:20
Status: done
What: task-001完了。会社Macの対象3ファイル(download_all_reports.py/teams_daemon.py/cas_download.py)は既にnormal+off-screen方式に書き換わっており(誰が直したか不明、おそらく2026-09-02の「別プロセスによる独立更新」)、minimized状態は残っていないことをgrepで確認。9/10の2回のSalesforceパイプライン定時実行(18/18成功)とteams_daemonの継続稼働ログで動作確認。新規の強制実行はMFA churn回避のため行わず既存ログで検証。shared_bot_browserメモリにCLOSEDエントリ追記、inbox Status: done。
Next: task-002に着手

## 2026-09-11T10:15
Status: done
What: task-002完了。TEAMS_WEBHOOK_URLは~/.zshenv設定済みを確認。会社Macは想定通り個別plist方式(com.nakamura.calendarsync/emailsync)のままで、launchdが環境変数を継承しない問題を確認→ラッパースクリプト方式(run_sync.sh)に変更、plist ProgramArgumentsを/bin/bash経由に修正、launchctl unload/loadで再読込、ps ewwで環境変数到達を確認。加えて想定外の2バグを発見・修正(Dropbox共有コードのため個人Mac側にも波及): (1) WORK_STATUS_FILEが個人Macのプロジェクトキーにハードコードされ会社Macで無関係パスに書いていた問題→マシン非依存の解決ロジックに変更、(2) カレンダー同期にnotify_teams()自体が存在しなかった問題→メール同期の実装を移植。さらに会社Mac固有の新発見として、Python urllib.request(certifi込み)がZscaler/BIG-IPのTLS傍受証明書を検証できずCERTIFICATE_VERIFY_FAILEDで失敗する問題を発見、curl経由のsubprocess呼び出しに書き換えて解決(HTTP 202確認済み)。新規memory feedback_d14461_python_https_cert_verify_use_curl.mdを作成。continuous_data_capture_setup.mdとinbox Resultに詳細記録済み、inbox Status: done。ユーザーへの申し送り(OneDriveの「常にこのデバイスに保持」設定を会社MacのCalendar/Inbox/SentItemsにも設定する必要あり)は本セッションの応答内で案内済み、Finder操作自体は未実施(ユーザー本人作業)。
Next: — (ユーザーがOneDrive設定を実施すれば完全クローズ)

## 2026-09-11T10:30
Status: done
What: task-002の副産物として、同じTEAMS_WEBHOOK_URL/SSL証明書検証バグが他に3ファイルにもあることが判明。`~/CASExport/cas_monthly_pipeline.py`は既にcurl方式で対応済みだった(既知問題として認識されていたことを確認)。`~/TeamsExport/teams_daemon.py`の`notify_teams_webhook()`(urllib、しかも`except: pass`で失敗が完全に無音)と`~/OverseasStaffList/common.py`の`send_teams()`(requestsライブラリ、同じくcertifi経由で失敗)の2件は未対応だったため同じくcurl方式に修正。teams_daemonは常駐プロセスのため`launchctl kickstart -k`で再起動(共有ブラウザへの再接続のみで再ログイン不要、正常復帰を確認)。feedback_d14461_python_https_cert_verify_use_curl.mdに対応済みファイル一覧を追記。
Next: —
