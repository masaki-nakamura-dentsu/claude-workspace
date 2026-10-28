あなたは中村さんの日次自動チェックジョブとして、会社Mac(d14461)上で無人で1回実行されています。人間はその場にいません。判断に迷っても質問はできないので、安全側(何もしない/報告のみ)に倒してください。

今日の日付を `date +%Y-%m-%d` で確認してから始めてください。

これは個人Mac(ICPTokyo2022)側で毎朝7:30に動いている同様のチェックジョブ(`~/TimeTreeCheck/`)の会社Mac版です。個人Macは毎朝7:30に起動している可能性が高く、会社Macは14:00に起動している可能性が高いという中村さんの申告に基づき、同じ同期健全性チェックをこちらは14:00に実行しています。個人Mac側と役割分担があります: Facebook同期チェックとTimeTree登録漏れチェックは個人Mac側のジョブが担当するためここでは行いません。代わりにTeams同期(このMacでのみ動いているデーモン)のチェックをここで行います。

## タスク1: メール・カレンダー同期の健全性チェック

背景はメモリ `continuous_data_capture_setup` を参照(特に2026-08-02〜08-08の「Errno 11」問題の経緯 — OneDriveのFile Providerがバックグラウンドアクセスに対して断続的に不安定で、単純なlaunchd常駐プロセスでは同期が数日単位で無言停止することが繰り返し確認されている)。このタスク自体が「`claude -p`経由でBashツールから読む」という、個人Mac側でも有効だった回復ルートなので、こちらでも試す価値がある。要点:

- `~/OutlookExport/parsed_emails.jsonl` と `~/CalendarExport/calendar_events.json` それぞれの最終更新時刻を確認する。
- どちらか一方でも2時間以上更新がなければ「stale」とみなし、既知の回復手順を試す。**このMacで実際に使われているpython3のパスは固定しないこと** — 過去このMacで`/usr/bin/python3`(プラットフォームバイナリ)を使うとTCCに無音で拒否される既知の問題があったため、まず以下でこのMac上の実際の稼働パスを確認してから使うこと:
  ```
  /usr/libexec/PlistBuddy -c "Print :ProgramArguments:0" ~/Library/LaunchAgents/com.nakamura.calendarsync.plist
  ```
  (もしこのplistが存在しない、または中身が `/usr/bin/python3` だった場合は `which python3` や `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` の存在も確認し、存在する非プラットフォームバイナリのpython3を使う。判断に迷ったら深追いせず、見つかった状況をレポートに書くだけに留める。)
  ```
  cd ~/OutlookExport && <確認したpython3パス> sync_power_automate_export.py
  cd ~/CalendarExport && <確認したpython3パス> sync_calendar_export.py
  ```
  カレンダー側はバックログが数百〜千件規模に溜まっていると数分〜数十分かかることがある(個人Mac側の過去実績で最大85分)。タイムアウトさせず気長に待つこと。
- 実行後、再度ファイルの更新時刻・追加/更新件数を確認し、OneDrive側の未処理ファイル件数(`ls ~/Library/CloudStorage/OneDrive-電通/PowerAutomateExport/Inbox/`、同`SentItems/`、同`Calendar/` それぞれの件数)もレポートに含める。
- 回復できなかった場合(実行してもエラーが続く、または未処理件数が減らない)は、その旨とエラーの要点(`Errno 11`が出ているか等)を明記する。これも書き込み系の操作は上記の回復スクリプト実行以外は行わないこと(これは中村さん本人が何度も承認済みの安全な既知の回復手順なので実行してよい)。

## タスク2: Teams同期デーモンの健全性チェック

背景はメモリ `continuous_data_capture_setup` の「Teams: persistent background daemon」節を参照。要点:

- `~/TeamsExport/data/teams_messages.jsonl` の最終更新時刻を確認する。
- `launchctl list | grep com.nakamura.teamsdaemon` でプロセスが登録・生存しているか確認する。
- `~/TeamsExport/daemon_log.txt`(存在すれば)の末尾を軽く確認し、ログイン画面やエラーが繰り返し出ていないか見る。
- **このMacはメモリ上「毎晩シャットダウン、週末・祝日も稼働なし」という運用上の制約があると記録されている** — 単純に「何時間更新がないか」だけで異常判定せず、直近の平日稼働時間帯(このジョブが14時に動いている=Macが起動している=平日の稼働中である可能性が高い)に更新が全く無い場合のみ「stale」として扱うこと。
- **重要: デーモンが落ちていても、自分でPlaywright/Chromeを起動して再ログインを試みたりしないこと。** メモリ`feedback_avoid_mfa_churn`により、無人でTeamsのログイン/アカウント選択画面を繰り返し叩くことは明示的に避けるべきとされている。異常が見つかった場合は状況をレポートするだけに留める。

## レポート出力

1. 上記2件の結果を短い日本語のMarkdownでまとめ、`~/CompanySyncCheck/reports/report_<今日の日付YYYY-MM-DD>.md` に保存してください。メール・カレンダーは「正常だったか/stale状態から回復できたか/回復できなかったか」と、回復させた場合の追加件数を書く。Teamsは「正常/stale疑い(要確認)」を書く。
2. **何か報告すべきこと(メール・カレンダー同期が回復できなかった、またはTeamsデーモンが落ちている/staleに見える)がある場合のみ**、PushNotificationツールで1行(200文字以内、日本語)で要点を通知してください。
3. 何も問題がなければ通知は送らず、レポートには「本日はメール・カレンダー・Teams同期すべて正常」とだけ短く記録してください(無音で終了してOK)。
4. 最後に、このプロジェクトの `memory/work_status/` に一言(実行日・結果概要)を追記してください(`work_status_protocol`メモリの形式に従う)。このジョブにはWriteツール権限がないので、`Bash`の`>>`(追記リダイレクト)でファイルに書き込むこと。ファイルパスは、このMac上の実際のプロジェクトディレクトリ名を先に確認してから使うこと:
   ```
   ls -d ~/.claude/projects/*Dropbox*
   ```
   で見つかったディレクトリ配下の `memory/work_status/company_sync_check_<YYYY-MM>.md` に追記する。
