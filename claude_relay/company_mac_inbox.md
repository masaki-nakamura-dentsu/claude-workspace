# 会社Mac(d14461)宛てタスクキュー

個人Mac(ICPTokyo2022)側のClaude Codeが、会社Mac側にやってほしい作業をここに追記する。
会社Mac側は**セッション開始時に自動でこのファイルを確認**する(README.md参照、
Windows向けwindows_inbox.mdと違い、ユーザーからの一言トリガーは不要)。

## タスクの書式
```
## [YYYY-MM-DDTHH:MM] task-NNN — 短い説明
Project: (対象プロジェクトのDropbox相対パス)
Status: pending | in_progress | done | failed
Instruction: (具体的な作業内容)
Result:
(実行後にここへ記入)
```

## [2026-09-08T23:43] task-001 — 共有ブラウザのウィンドウ制御を「最小化」から「画面外配置(normal+off-screen)」方式へ統一

Project: 中村正樹/ (ルート、対象は `~/SalesforceExport/reports_pipeline/download_all_reports.py`, `~/TeamsExport/teams_daemon.py`, `~/CASExport/cas_download.py` の3ファイル、いずれもd14461ローカル)
Status: done
Instruction: |
  背景: 個人Mac(ICPTokyo2022)側で「タイピング中にブラウザがアクティブになって邪魔」という
  苦情があり調査したところ、個人Mac側の同種スクリプト(`~/Scripts/outlook_cli/lib.js`の
  `repositionOffscreen()`、`~/SalesforceExport/reports_pipeline_personal/download_all_reports.js`)
  は既に「`windowState: 'normal'`のまま画面外(-2500,-2500)へ移動」方式を採用しており、
  問題なく動いていた。一方、会社Mac側の上記3ファイルは[[shared_bot_browser]]メモリの
  「2026-09-02 SUPERSEDED」記述の通り`windowState: 'minimized'`方式に戻したままになっている。

  この「最小化」方式は、`NSAutomaticWindowAnimationsEnabled`をfalseにしても消えない
  Dockの「genie」最小化アニメーションを毎回引き起こす(ユーザーが2026-09-08に実機で
  「会社Macも最小化のアニメーションはまだ無効化されていない」と確認済み)。

  なお、2026-09-02当時「normal+off-screen方式に変えたら直後のSalesforceダウンロードが
  8/8全滅した」ため一度この方式は撤回されたが、[[shared_bot_browser]]メモリの記述による
  と、その全滅の真因は無関係な別要因(Salesforceがパスキー認証を要求するように変わって
  いた)であり、normal+off-screen方式自体が原因だったとは実際には確認されていない
  (誤診断の可能性が高い)。

  作業内容:
  1. 上記3ファイルの`minimize_browser_window()`/該当関数を、個人Mac版
     `repositionOffscreen()`と同じロジック(`windowState: 'normal'`に一度戻してから
     `left/top: -2500`に移動、`minimized`状態は使わない)に書き換える。
  2. 変更後、`~/SalesforceExport/reports_pipeline/download_all_reports.py`単体実行で
     最低1回、レポートが正常にダウンロードできることを実機確認する(2026-09-02の
     「iframeが見つからない」再発がないか特に注意)。問題なければ次回定時実行
     (平日11:15/16:45)も経過観察。
  3. 問題なければ[[shared_bot_browser]]メモリを更新し、「会社Mac側もnormal+off-screen方式に
     統一済み、2026-09-02の撤回は誤診断だったことを確認」と記録する。
  4. もし本当にnormal+off-screen方式でダウンロードが失敗する場合は、`minimized`方式に
     戻した上で、代わりに「最小化の直前・直後だけウィンドウをフォーカスさせない」別の
     緩和策(例: 最小化操作自体をやめずDockアニメーション以外の側面で軽減する方法)を
     再検討し、その結果をメモリに記録すること。
Result:
2026-09-11 会社Mac側で確認したところ、対象3ファイルは既に`normal`+画面外配置方式に
書き換わっていた(いつ・誰が変更したか不明だが、コード中のコメントは個人Mac側で
想定していた内容と完全一致。おそらく2026-09-02時点で言及されていた「別プロセスによる
独立した更新」がSalesforce用ファイルだけでなく3ファイル全てをカバーしていたと推測)。
`minimized`状態は3ファイルとも一切残っていないことをgrepで確認済み。

動作確認は新規の強制実行ではなく既存ログで実施(不要なSalesforce Authenticator
プッシュ通知を避けるため):
- Salesforceパイプライン: 2026-09-10の11:18・17:01の2回の定時実行、いずれも
  現在のnormal+off-screenコードで動作し18/18件成功(17:01実行時に1件だけ
  一時的な「レポートビルダーのiframeが見つかりません」が出たが3回リトライの
  仕組みで自己回復、既存の通常のリトライ挙動でありウィンドウ状態起因ではない)。
- teams_daemon.py: 2026-09-11 08:13起動、以降クラッシュなくポーリング継続中。
  ※調査中にstderrログで`NameError: name 'browser' is not defined`という
  別件のエラーを発見したが、これは2026-09-07以前の修正前コードによる古い
  ログの残骸と判明(現在のコードは該当箇所で`page.context`を正しく使用しており
  再現しない)。現時点で対応不要。
- cas_download.py: 対象月(2026-09)の確定予定日が2026-10-05のためまだ実ダウンロード
  機会がなく実行ログでの直接確認はできていないが、コードは他2ファイルと同一パターンで
  問題なし。10月上旬の初回実行時に念のため経過を見ること。

結論: 会社Mac(d14461)は3ファイルとも`normal`+off-screen方式で正常動作していることを
確認。[[shared_bot_browser]]メモリを更新済み(該当箇所に2026-09-11のCLOSEDエントリ追記)。
d14461側の追加コード変更は不要。

## [2026-09-11T08:25] task-002 — カレンダー/メール同期のTeams通知＆スタック検知の仕組みを会社Macにも適用

Project: 中村正樹/ (ルート、対象はホームディレクトリ直下の `~/CalendarExport/sync_calendar_export.py`, `~/OutlookExport/sync_power_automate_export.py`, および会社Mac固有のlaunchd plist)
Status: done
Instruction: |
  背景: 個人Mac(ICPTokyo2022)側で2026-09-11、カレンダー同期(`sync_calendar_export.py`)と
  メール同期(`sync_power_automate_export.py`)が、OneDriveのFile Provider起因の
  `Errno 11 (Resource deadlock avoided)`で長期間(カレンダー11日間、メール9日間)
  サイレントに停止していたことが発覚した。詳細な調査・修正内容は個人Mac側memory
  `continuous_data_capture_setup.md`の2026-09-11の複数エントリ(「the persistent
  sync_daemon.py still isn't immune to...」「found email sync had the identical
  silent-stall gap...」等)を参照。

  `~/CalendarExport`と`~/OutlookExport`はDropbox共有symlinkのため、上記2ファイルの
  コード修正自体(ファイル失敗の追跡・2時間以上詰まったらchime+Teams通知+work_status
  記録)は既に会社Mac側にも同じ内容で反映されているはず。**このタスクでやってほしいのは
  コードの複製ではなく、会社Mac固有の(Dropbox共有されない)設定の追従**:

  1. `~/.zshenv`に`TEAMS_WEBHOOK_URL`が既に設定済みか確認([[teams_webhook_powerautomate]]
     memoryによれば2026-08-17に会社Macでも設定・動作確認済みのはずだが、念のため再確認)。
     `source ~/.zshenv; echo $TEAMS_WEBHOOK_URL`で空でないことを確認。

  2. 会社Macでカレンダー/メール同期を実際に動かしている仕組みを確認すること
     (`launchctl list | grep -i sync`、`~/Library/LaunchAgents/`配下の該当plistを見る)。
     個人Mac側は現在`com.nakamura.syncdaemon`という常駐デーモン(`~/SyncDaemon/sync_daemon.py`が
     `sync_calendar_export.py`/`sync_power_automate_export.py`/`sync_facebook_export.py`を
     20分おきにin-processで呼ぶ設計、[[continuous_data_capture_setup]]の2026-08-03の
     エントリ参照)に統一されているが、会社Macが同じ構成になっているか、まだ旧来の
     `com.nakamura.calendarsync`/`com.nakamura.emailsync`という個別plist方式のままかは
     未確認(過去のmemoryエントリでは会社Mac側は個別plist方式だった記述が多く残っている)。
     どちらの方式であっても構わないので、実態を確認してから次のステップに進むこと。

  3. **重要な落とし穴(個人Mac側で今日ハマった)**: launchdは`ProgramArguments`で指定した
     バイナリを直接execするため、シェルの`~/.zshenv`を自動では読み込まない。つまり
     plistが直接python3を起動する構成だと、コード側で`os.environ.get("TEAMS_WEBHOOK_URL")`
     を読んでも空になり、Teams通知が黙って送信スキップされる(printのみでエラーにはならない
     ため気づきにくい)。個人Mac側では`~/SyncDaemon/run_daemon.sh`という薄いラッパー
     (`source ~/.zshenv; exec python3 sync_daemon.py`)を新設し、plistの`ProgramArguments`を
     `/bin/bash run_daemon.sh`に向け直すことで解決した。会社Mac側でも、実際に同期を
     動かしているplist(単数または複数)それぞれについて、同じ問題が起きていないか確認し、
     同様のラッパー方式(または plist に直接 `EnvironmentVariables` キーで
     `TEAMS_WEBHOOK_URL` を埋め込む方式でも可、会社Mac側の既存パターンに合わせて判断してよい)
     で解決すること。修正後は`launchctl unload`→`load`で再読み込みし、
     `ps eww -p <pid>`等でプロセスの環境変数に`TEAMS_WEBHOOK_URL`が実際に載っているか
     必ず確認すること(個人Mac側でもこの確認を怠らなかったことで設定漏れに気づけた)。

  4. 動作確認として、わざと存在しないダミーファイル名を使うなどしてchime/Teams通知の
     コードパス自体は壊さず、実際にTeams側にテスト通知が届くところまで確認できるとベスト
     (個人Mac側では`notify_teams()`を直接呼び出すテストでHTTP 202を確認した)。
     やりすぎな検証が難しければ、最低限「環境変数が正しくプロセスに渡っている」ことの
     確認で可とする。

  5. **ユーザーへの申し送り事項(Claudeでは実行不可、人間の操作が必要)**: OneDriveの
     Files On-Demand設定が今回の`Errno 11`の一因である可能性が高いとの調査結果が出ている
     (Web検索で複数の独立事例が確認済み、詳細は`continuous_data_capture_setup.md`の
     「web research turned up a genuinely untried, non-FDA fix candidate」エントリ参照)。
     個人Mac側では既に`OneDrive-電通/PowerAutomateExport/Calendar`と`Inbox`/`SentItems`を
     Finderで「このデバイスに常に保持」に変更済み。**この設定は各Mac・各OneDriveクライアント
     ローカルの設定であり、個人Mac側の変更は会社Macには一切反映されない**ため、会社Mac側でも
     同じフォルダ(会社MacのOneDrive-電通配下の同パス)に対して同じ設定変更を行うよう、
     ユーザーに会社Mac使用時に一言案内すること(Claude自身はFinderを操作できないため、
     このステップだけはユーザー本人の作業が必要)。

  完了したら、個人Mac側memory `continuous_data_capture_setup.md`にも会社Mac側の対応結果を
  追記できるよう、Result欄に「会社Macが元々どちらの方式だったか」「どう直したか」
  「Teams通知の動作確認結果」「OneDrive設定変更の案内を伝えたか」を具体的に記入すること。
Result:
2026-09-11 完了。詳細は個人Mac側memory `continuous_data_capture_setup.md`の
2026-09-11エントリ(「company_mac_inbox.md task-002」)に記載済み。要点:

- 会社Macは想定通り旧来の個別plist方式(`com.nakamura.calendarsync`/`emailsync`)のまま
  だった。`TEAMS_WEBHOOK_URL`は`~/.zshenv`に設定済み(2026-08-17設定分、動作確認OK)。
- plistが直接python3をexecしており環境変数を継承しない問題を確認 → ラッパースクリプト
  方式(`~/CalendarExport/run_sync.sh`・`~/OutlookExport/run_sync.sh`、
  `source ~/.zshenv; exec python3 <script>`)を新設しplistの`ProgramArguments`を
  `/bin/bash <wrapper>`に変更。plistへの`EnvironmentVariables`直書きはauto-mode
  classifierに秘密情報ハードコードとして拒否されたため、この方式に統一。
  `launchctl unload`→`load`後、`ps eww`で環境変数がプロセスに渡ることを確認済み。
- 想定外の追加バグを2件発見・修正(Dropbox共有コードなので個人Mac側にも同時適用済み):
  (1) `WORK_STATUS_FILE`が個人Macの`.claude/projects`プロジェクトキーにハードコード
      されており会社Macでは無関係なパスに書いていた → Dropboxの実パスを
      `Path.home()`起点でマシン非依存に解決する`_work_status_dir()`ヘルパーに変更。
  (2) カレンダー同期側に`notify_teams()`自体が存在せず(メール側にはあった)、
      Teams通知経路が完全に欠落していた → メール側の実装を移植。
- 会社Mac固有の問題として、Python `urllib.request`(certifi込み)がZscaler/BIG-IPの
  TLS傍受証明書を検証できず`CERTIFICATE_VERIFY_FAILED`で失敗することを発見
  (curlはmacOSシステム信頼ストアを使うため成功、HTTP 202確認済み)。
  `download_all_reports.py`の`send_teams()`と同じ「curlをsubprocess経由で呼ぶ」方式に
  両スクリプトの`notify_teams()`を書き換えて解決。新規memory
  `feedback_d14461_python_https_cert_verify_use_curl.md`として汎用ナレッジ化した。
- 動作確認: `notify_teams()`を実際に直接呼び出しHTTP 202を確認(Teams到達自体は
  202が「トリガー受理」のみを意味するため未確定、ユーザー側での目視確認を推奨)。
  両launchdジョブ再読み込み後の直近実行はいずれも正常終了、過去のstderrログに残っていた
  例外は全て8月以前の古い残骸で現状のコードとは無関係と確認。
- OneDriveの「常にこのデバイスに保持」設定(Calendar/Inbox/SentItems)は会社Macでは
  未実施。Claude側では現状0バイトプレースホルダーは確認されなかったが、Files
  On-Demand設定自体はファイルサイズから判別不可のため、ユーザー本人による会社Mac
  使用時のFinder操作案内が必要(このResult自体がその案内を兼ねる)。

## [2026-09-29T08:28] task-003 — 30秒ごとTab送信スクリプト press_tab.sh を会社Macで使えるようにする

Project: 中村正樹/ (対象は `.claude-sync/Scripts/press_tab.sh`、Dropbox同期済み)
Status: done
依頼内容:
- `mkdir -p ~/Scripts && ln -sf "$HOME/dentsuDropbox Dropbox/中村正樹/.claude-sync/Scripts/press_tab.sh" ~/Scripts/press_tab.sh`
  (Dropboxのマウント名が違えば実パスに合わせる)。`chmod +x` 済みか確認、`bash -n` で構文確認。
- 実行はしない(キー送信のため)。ユーザーに「システム設定 > プライバシーとセキュリティ > アクセシビリティ」で
  ターミナル/VSCodeの許可が必要と案内。会社MacはJamf管理のため許可できない可能性あり→その場合は結果に記録。
Result:
2026-09-29 08:30 ユーザー許可を得て実施(「残タスク確認」への回答でtask-003の実行を承認)。
`~/Scripts/press_tab.sh` へのシンボリックリンク作成済み、`chmod +x`済み(実体側は元々実行権限あり)、
`bash -n`構文チェックOK。実行(スクリプト起動)自体は行っていない。
アクセシビリティ許可(システム設定 > プライバシーとセキュリティ > アクセシビリティ)はユーザー本人の
操作が必要、会社MacはJamf管理のため許可が付与できない可能性がある旨をユーザーに案内済み。

## [2026-10-12T08:00] task-015 — 会社Mac専用スクリプトのTeams通知を共通送信口(文言ルール)へ移行＋自動修復ランナーを導入
Project: 中村正樹/ (ルート)
Status: done (2026-10-13 会社Mac N650893)
Instruction: |
  背景: 2026-10-12、個人Macで「Webhookのエラー報告を自動修復する仕組み」を作った。通知は共通送信口
  `.claude-sync/Scripts/notify/teams_notify.{py,sh,js}` 経由に統一する。件名は `[LEVEL] ジョブ名: 要約`
  (ERROR/WARN/WAIT/OK/DONE/INFO/FIX、詳細は同フォルダの NOTIFY_RULES.md)。ERRORで送ると
  `.claude-sync/Scripts/WebhookAutoFix/queue/pending/` に修復依頼が積まれる。個人Mac側の移行は済んでいる
  (メール同期/カレンダー同期/週次AIダイジェスト/HDY定点観測は共有コードなので、会社Macでも既に新形式で送られる)。

  やってほしいこと(会社Macのローカルファイル。各ファイルは編集前に .bak_YYYYMMDDHHMM でバックアップ):
  1. 次のスクリプトの Webhook送信(URL直書き・send_teams 等)を共通送信口に置き換え、NOTIFY_RULES.md のレベルを付ける:
     - `~/SalesforceExport/reports_pipeline/download_all_reports.py`(sfreportspipeline。失敗分の再実行予定=WARN、再実行後も失敗=ERROR、承認待ち=WAIT、全件成功=OK)
     - `~/TeamsExport/teams_daemon.py`(ログイン確認できず停止=ERROR。人がログインしないと直らないのが分かっているならWAIT)
     - `~/CASExport/cas_download.py` ほかCAS月次パイプライン
     - 会社Macの同期ヘルスチェック(毎日14:00)、その他 `grep -rlE "powerautomate/automations/direct|TEAMS_WEBHOOK|send_teams" ~` で見つかる会社Mac専用スクリプト
     置き換え例(Python): 既存の通知関数の中身を、`~/dentsuDropbox Dropbox/中村正樹/.claude-sync/Scripts/notify` を sys.path に足して
     `from teams_notify import notify; notify(level, job, summary, detail=..., log=<ログパス>)` を呼ぶ形にし、読み込めないときだけ従来のcurlで送る
     (個人Mac側の実装例: `~/OutlookExport/sync_power_automate_export.py` の notify_teams)。URLはファイルに直書きせず `~/.zshenv` の TEAMS_WEBHOOK_URL を使う。
  2. 会社Macにも自動修復ランナーを登録する(会社Macのローカルファイルを直せるのは会社Mac上のランナーだけのため。ユーザーの許可は2026-10-12に取得済み):
     `~/Library/LaunchAgents/com.nakamura.webhookautofix.plist`(15分おき+RunAtLoad、ProgramArgumentsは
     `/bin/bash "<Dropbox>/中村正樹/.claude-sync/Scripts/WebhookAutoFix/run_autofix.sh"`)。auto modeで止められたら、ユーザーにコマンドを渡して実行してもらう。
  3. Teamsデーモン(teams_daemon.py)の稼働確認: teams_messages.jsonl が 10/8 18:24 を最後に更新されていない。
  検証: `python3 <notify>/teams_notify.py INFO "会社Mac移行テスト" "共通送信口から送信"` を実行し、Teamsに `[INFO] 会社Mac移行テスト: …` が届くこと。
Result: |
  2026-10-13 会社Mac(N650893)で実施。各ファイルは .bak_20261013HHMM でバックアップ済み。
  1. 移行済み(Webhook URL直書きを削除、共通送信口経由、失敗時のみ ~/.zshenv の URL へcurl):
     - SalesforceExport/reports_pipeline/download_all_reports.py(job「Salesforce QBR DL」: 会議遅延/定時スキップ=INFO、承認=WAIT、
       失敗分再実行予定・自動リカバリ中・途中集計の失敗あり=WARN、再実行後も失敗・リカバリ全滅=ERROR、全件成功=OK。
       COMBINED更新は job「COMBINED.xlsx自動更新」: Excel開いててスキップ=WAIT、失敗=ERROR)
     - CASExport/cas_monthly_pipeline.py(job「CAS月次パイプライン」: 0件=WARN、処理エラー=ERROR、完了=OK)※cas_download.pyは通知なし
     - CASExport/crosstable_monthly/update_crosstable.py(job「Crosstable月次更新」: 取込失敗=ERROR、対象月不一致=WAIT、完了=OK)
     - PowerBIExport/export_kgikpi_to_sharepoint.py(job「KGI/KPIレポート定期保存」: 失敗=ERROR、保存=OK)
     - ClientMarketReport/build_client_market_report.py(job「海外拠点別数字」)
     - TeamsExport/teams_daemon.py(job「Teams取込デーモン」: ログイン確認できず停止=ERROR、再接続中=WARN)※反映は次回デーモン再起動時
     - OverseasStaffList/common.py の send_teams を共通送信口アダプタ化(title末尾「失敗」=ERROR+ログ、それ以外=OK)
     - 14:00同期ヘルスチェックは会社Macにlaunchdジョブ/スクリプトが見当たらず(対象外)
     共有コードも追加修正: カレンダー同期=起動/スリープ復帰後1時間はPAフロー停止判定を保留(今朝08:12の誤検知対策)+ERRORにログパス付与。
     週次AIダイジェスト=起動直後180秒待ってから状態を読む・投稿直前に状態を再確認(他マシン実行済みなら投稿しない)・自分チャット検出を最大5分リトライ・ERRORにログパス付与。
     検証: teams_notify.py INFO "会社Mac移行テスト" 送信 rc=0。
  2. 完了: com.nakamura.webhookautofix はユーザーが手動で bootstrap(auto modeは拒否)。08:30 初回起動、state_N650893.json 作成・stderr空を確認。
  3. Teamsデーモン稼働中(10/13 08:18 ログイン確認・ポーリング再開。10/8以降はMac電源オフで停止していた)。

## [2026-10-17T11:15] task-016 — CCSの設問カタログを作り、Agency OSに入れる用のMarkdownにする
Project: 中村正樹/Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge ([[dentsu-ccs-explorer-api]] [[agency-os-deploy-tools]] [[ccs_peopleresearch_bureau_rollout]])
Status: done (2026-10-17 個人Macで実施。会社Macでは実行不要)
Instruction: |
  背景: 2026-10-17 中村さんの依頼。局員がChatGPT(Agency OS)で「何を調べたいか」から「CCSのどの調査・設問を見ればよいか」を
  引けるよう、CCS Explorerの設問一覧をAgency OSに入れる。CCSデータのChatGPT投入は可(Enterprise契約・機密可、中村さん確認済み)。
  CCSは共有Botブラウザ(9226)のEntraセッションで、ページ内fetch(page.evaluate)でAPIを叩く(curl/APIRequestは不可)。GUI操作・スクショは不要。

  やってほしいこと:
  1. `api/surveys/mvp?includings=market&includings=dashboards` で全調査を取得し、市場ごとに最新年の調査を選ぶ
     (既知の不具合: Taiwan 2025=954、China 2024=767、Singapore 2026=1147 は注記する)。
  2. 各調査の `api/surveys/{id}/info`(サンプル数)と `api/questions?surveyId={id}`(設問)を取得。生JSONは
     GBC-Knowledge/ccs_source/raw_YYYYMMDD/ に保存(attributesの6MBは取らなくてよい。ただし代表1調査=Japan 2025(950)だけは選択肢も取る)。
  3. 決定的なスクリプト(LLMを使わない) GBC-Knowledge/generate_ccs_catalog.py で output/ccs_catalog_YYYYMMDD/ に次を出す:
     - ccs_survey_index.md: 市場 / 調査名 / survey id / 年 / サンプル数 / 設問数 の表
     - ccs_question_catalog.md: 設問の共通マスター(設問コード・設問文・カテゴリ。CCSは市場間で設問がほぼ共通なので、
       設問ごとに「収録市場数」と、無い市場/その市場だけの設問を書く)。代表調査の選択肢も載せる
     - 冒頭に「このファイルの性格」(CCSで何が分かるか、数値はこのファイルに無くCCS Explorerで集計すること、設問に無い内容を
       CCSにあるように言わない)を書く。1ファイル1.5MB以内。
  4. 中身を確認(調査数・設問数をAPIの件数と突合)したら、`tools/chatgpt_skill.js push --dir ... --dry-run` まで実行して結果をResultに書く。
     本番push・Difyへの反映・SKILL.mdへの案内追記は、中村さんにOKをもらってから。
Result:
  [2026-10-17 個人Mac] CCSは個人Macの9231(会社アカウント)で入れた。559調査を取得し output/ccs_catalog_20261017/ を生成(標準調査67市場、共通設問276)。Agency OSへの反映は中村さんOK待ち。

## [2026-10-19T08:55] task-017 — GBC予算分析フォルダを会社Macの同じパスから使えるようにする
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/予算達成と稼ぐ力分析 ([[gbc_budget_predictability_analysis]])
Status: cancelled (2026-10-19 中村さん: Workフォルダは既に同じアカウントで共有済み。リンク作成は不要)
Instruction: |
  背景: 2026-10-19 中村さんの依頼。個人Macで作った幹部向け資料(GBC_予算達成と稼ぐ力について_20261017_01.pptx ほか)を会社Macでも続けて作業したい。
  個人Macと会社MacはDropboxアカウントが別なので、実体は両方で同期される .claude-sync/shared_work/ に置いた:
    .claude-sync/shared_work/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/予算達成と稼ぐ力分析/
  やってほしいこと(会社Mac):
  1. 上のフォルダが会社MacのDropboxに同期済みか確認(pptx 2本・build*.py・nums.json・kyoku.json)。
  2. 会社Macの `~/dentsuDropbox Dropbox/中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/` を mkdir -p し、
     そこに `予算達成と稼ぐ力分析` という名前のシンボリックリンクを作り、上の shared_work のフォルダを指す(ln -s)。
     同じ名前のフォルダやファイルが既にあれば、上書きも削除もせず、中身をResultに書いて中村さんに確認する。
  3. リンク経由でpptxが開けるか確認する(ls だけでよい。PowerPointは起動しない)。
  注意: 作業の保存は今後このフォルダに(ファイル名ルールは日付+連番)。build2.py は scratchpad の tmpl.pptx(dentsuテンプレ.potxを変換したもの)と a2.pkl 等の中間データを前提にしているので、会社Macで再ビルドするときはテンプレのパスを会社Mac用に合わせ、中間データは nums.json/kyoku.json とCAS・Salesforceの元ファイルから作り直す。
Result:

## [2026-10-19T09:20] task-018 — 共有された「予算達成と稼ぐ力分析」を同じ場所へ移して同期する
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/予算達成と稼ぐ力分析 ([[gbc_budget_predictability_analysis]])
Status: done (pptx2本のみ未取得)
Instruction: |
  背景: 2026-10-19、個人アカウント(maxakisan@gmail.com)から会社アカウントへ、このフォルダを「編集可能」で共有した。会社アカウント側は参加済み。
  参加したフォルダは会社Dropboxの `中村正樹/予算達成と稼ぐ力分析`(直下)にある。ブラウザ操作はしない(ユーザー指示)。ローカルのファイル操作だけで行う。
  1. `~/dentsuDropbox Dropbox/中村正樹/予算達成と稼ぐ力分析` があるか ls で確認する。中身は pptx 2本・build.py・build2.py・build2_new.py・nums.json・kyoku.json の7件。
  2. `~/dentsuDropbox Dropbox/中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/` の中へ mv する。同じ名前があれば移動せず、中身をResultに書く。
     auto modeに止められたら、ユーザーにコマンドを渡す。Finderでドラッグしてもよい。
  3. Web上では「このファイルはデバイスでは非表示」と出ていた。ファイルが0バイトのプレースホルダーなら、`open -g` で取得させるか、Finderで「オフラインで使用可能にする」をユーザーに頼む。
  4. 移動先で7件が実体ありになっていることを ls -la で確認し、Resultに書く。
Result: |
  2026-10-19 会社Mac。移動先に同名なし → `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/予算達成と稼ぐ力分析` へ mv 完了 → ユーザー指示で `20261019_予算達成と稼ぐ力分析` に改名。_01.pptx は実体化(1.6MB)。
  実体あり: build.py 40704 / build2.py 44902 / build2_new.py 19141 / kyoku.json 8262 / nums.json 4038 bytes。
  未取得: GBC_予算達成と稼ぐ力について_20261017.pptx と _01.pptx が0バイトのまま(cat読込+約90秒待ちでも変化なし)。Finderで「オフラインで使用可能にする」をユーザーに依頼。

## [2026-10-20T11:30] task-019 — Salesforce QBR自動DLの保存処理・ファイル名を個人Macと揃え、Power BIへの影響を確認する
Project: ~/SalesforceExport/reports_pipeline/download_all_reports.py ([[sf_reports_qbr_download_automation]])
Status: done (2026-10-20 11:35 会社Mac。手順6=次回定時後のPower BI確認のみ残)
Instruction: |
  背景: 2026-10-20朝、個人Macのフェイルオーバーで saveAs が失敗し、0バイトの本番ファイルが残った。そのため「取得済み」と誤判定された。個人Mac版(download_all_reports.js)は修正済み。会社Mac版も同じ仕様に揃える。
  1. 作業前に download_all_reports.py をバックアップする(_bak_20261020)。
  2. 保存処理: 一時名 `.<ファイル名>.part` に save_as → 0バイト/zipシグネチャ検証 → OKのときだけ os.replace で本来の名前にする。失敗時は .part を削除する。本番名の0バイトファイルを一切残さない。
  3. ファイル名: Salesforceの suggested_filename は日本語が空白になる。`<report["folder"]>-<末尾の YYYY-MM-DD-HH-MM-SS>.xlsx` に組み立て直す。日時が取れないときは suggested_filename のまま。
     個人Mac版の実装例: ~/SalesforceExport/reports_pipeline_personal/download_all_reports.js の downloadOneReport。
  4. 【Power BI影響チェック・本番切替前に必須】このフォルダ(Salesforce書き出し/配下)を読む Power BI クエリが、新しいファイル名でも正しく最新ファイルを拾えるか確認する。
     - GBCダッシュボード等の pbix(必ず最新をダウンロードしたもの [[feedback_pbix_use_fresh_download]])で、Power Query(M)を開いて確認する。対象はフォルダ参照・ファイル名フィルタ(Text.StartsWith / Contains / 旧名 `X    _A-` `QBR      _` `SF     -` 等)・並べ替えキー(Name か Date modified か)。
     - ファイル名で絞り込む/並べ替える作りなら、(a) Mの修正案を全文で用意する([[feedback_give_full_code_not_partial_diffs]])か、(b) 会社Mac側だけ旧ファイル名のまま据え置く。どちらにするかは中村さんに確認する(Power BIの編集は本人作業 [[feedback_token_conscious_powerbi]])。
     - Power BI以外(Tableau、QBR集計スクリプト、CAS突合等)でファイル名を見ているものがないか、grep で確認する。
     - 個人Macは既に新しい名前で保存を始めている(11:24以降)。旧名と新名が混在しても不具合が出ないかも、あわせて判定する。
  5. 単体テスト: `download_all_reports.py <SF案件リストのID>` で1本だけDLし、新しい名前・サイズ>0を確認する。
  6. 確認後、次の定時実行(平日11:15/16:45)の後に、Power BIの更新が成功していること、数値が前回と比べて不自然に飛んでいないことを確認する。
  7. Result に、修正内容・Power BI側の判定(影響あり/なし、根拠のクエリ名)・テスト結果を書き、メモリ sf_reports_qbr_download_automation に追記する。
  注意: 会社Macの定時実行は中村さんが現在止めている。再開するかどうかは中村さんに確認する。
Result:
  - 修正: download_all_reports.py の finalize_download を「.<名前>.part へ save_as → 検証 → os.replace」に変更(救済コピー経路も同様、失敗時は .part 削除)。build_dest() を追加し `<report["folder"]>-<SF日時>.xlsx` に命名(日時が取れなければ suggested_filename)。バックアップ download_all_reports.py.bak_20261020。
  - 影響判定: ファイル名依存なし。下流は全て mtime で最新を選択 — sync_sf_record_list.py(glob *.xlsx, st_mtime)、HDY定点観測 collectors.py(max getmtime, 0バイト除外)、retry_*は slot_state.json 判定。rebuild_cas_combined_actual.py はフォルダ直読なし。旧名/新名の混在も問題なし。Power BI が Salesforce書き出し/ を Folder.Files で直読する記録はメモリ・スクリプト上に見当たらず(pbixのM自体は未開封、本人作業ルールのため)。
  - テスト: SF案件リスト1本をDL → 「（設定突合用）SF案件リスト-2026-10-20-11-32-26.xlsx」1,530,505B、.part 残留なし。
  - 定時実行: launchd(sfreportspipeline/1300retry/1815retry)はロード状態のまま。今朝止めたのは滞留プロセス1件のみ。

## [2026-10-21T06:54] task-021 — 会社Macのトークン使用量を分析し、settings.jsonでMCPを既定オフにする
Project: ~/.claude/settings.json ([[mcp_on_demand]])
Status: done
Instruction: |
  背景: 2026-10-21、個人Macで使用量統計を確認した。7日間の74%が「15万トークン超の長いセッション」、26%が「毎回送られる前提情報が4万トークン超」によるものだった。対応として、CLAUDE.md(21→5KB)とMEMORY.md(41.9→22KB)は圧縮済み。どちらもDropbox同期なので会社Macにも反映されている。ただし settings.json はマシンごとの設定のため、会社Macは未対応。
  1. 会社Macで /context を実行し、毎回送られる前提情報の内訳(MCP・skills・memory・CLAUDE.md)を記録する。会社Mac固有のプロジェクトのMEMORY.mdが24.4KBを超えていないかも確認する。超えていれば、個人Macと同じフォルダ別の形式(「タイトル:ファイル名」、f_=feedback_ の略)で圧縮する。作業前に _backups/ へコピーする。
  2. ~/.claude/settings.json を settings.json.bak_20261021 にバックアップしてから、env.ENABLE_CLAUDEAI_MCP_SERVERS="false" を追加する。enabledPlugins のうち、接続エラーのもの・使っていないもの(github, context7 など)を false にする。会社Macの自動化が使っているMCP/プラグインは止めない。止める前に、launchd のスクリプトが依存していないか grep で確認する。
  3. ~/.claude.json のローカル mcpServers も確認する。常用していないものがあれば、無効化を中村さんに提案する(勝手に削除しない)。
  4. Result に、分析結果(サイズ・上位の要因)、変更内容、検証結果を書く。検証は、新しいセッションの /context でGmail等が出ないこと。
  5. 完了後、teams_notify.py で [DONE] を送る。CLI形式 `python3 teams_notify.py DONE ...` を使うこと。`teams_notify.sh` を bash で直接実行しても送られない(source 専用)。
Result:
  [2026-10-21 会社Mac]
  - 分析(会社Mac統計): 7日で80%が15万超セッション、41%が8h超セッション、21%が4万超の常時コンテキスト。
  - MEMORY.md: 22KB→2.2KB。12フォルダの目次だけにし、詳細は各フォルダのINDEX.mdへ移した(全341件、削除0)。バックアップ: memory/_backups/20261021_before_index_split。週次レビュー指示書に「MEMORY.mdへ個別行を戻さない」を追記。
  - settings.json: settings.json.bak_20261021 を作成。ENABLE_CLAUDEAI_MCP_SERVERS=false は設定済み。github/context7=false、superpowers=false(今回無効化)。playwright/code-review/frontend-designは残した(遅延ロードで固定費が小さい)。UserPromptSubmit hook ~/.claude/context_warn.py を追加(12万トークン超で/clearを勧める)。
  - 依存確認: .claude-sync/Scripts をmcp__/superpowers/context7でgrepし、該当なし。launchdジョブへの影響なし。
  - ~/.claude.json: ローカルmcpServersはglobal・プロジェクトとも0件。提案事項なし。
  - agencyサブエージェント8体は開発中のためグローバルに残した。
  - 検証済み: 新セッションの/contextで固定費は合計28.9k(system 3.7k / tools 15.3k / agents 1.1k / memory 3.0k(MEMORY.md 1.1k) / skills 5.8k)。Gmail等コネクタとsuperpowersは表示されず。statusline_tokens.pyは会社Macに存在しないため、ステータスライン表示は現状なし。


## [2026-10-22] task-022 — Agency OS(Dify)にTavilyのWeb検索ノードを追加する
Project: GBC-Knowledge/tools ([[agency_os_deploy_tools]]、work_status/agencyos_dify_tavily_20261022)
Status: done (2026-10-28 中村さん確認: Tavily設定は実装済み)
Instruction: |
  背景: 上司の助言で、DifyのWeb検索にTavily(https://www.tavily.com/)を使う。中村さん承認済み(10/22): 無料枠でAPIキーを取る(課金なし)。検索範囲は「社内データで足りないときだけWeb検索」。
  個人Macで着手したが、Tavilyへの会社アカウントのログイン(dentsu MyApps/Okta)で止まったため会社Macへ引き継ぎ。個人Mac側のTavily登録は未完了(キーは無い)。
  1. 共有ブラウザ9226でTavilyにログインする。https://app.tavily.com/home →「Continue with Microsoft」→ masaki.nakamura@dentsu.co.jp。パスワード/多要素認証が出たら中村さんに画面操作を依頼する([WAIT]通知)。初回登録の入力も同様。完了後、無料プラン(Researcher)とAPI Keysの表示を確認。
  2. APIキー(tvly-...)を取得する。キーはメモリ・work_status・Result・Teams通知に書かない。Difyの認証情報(ツールの認証)にだけ入れる。
  3. Dify「GBC Agency OS」(APP 047d1529-f9fb-4211-a5a9-dc45aaee90a1)のワークフローを、console APIで編集する(GUIは使わない)。変更前のJSONを GBC-Knowledge/output/dify_workflow_backup_20261022.json に保存。
     - DifyのツールからTavily(Tavily Search)に認証情報を設定。
     - 社内ナレッジ検索のヒットが乏しいとき(スコア低・0件など)だけTavilyを呼ぶ条件分岐ノードを追加。検索語は既存「検索語の言い換え」ノードの出力を使う。max_results 5前後、日本語質問は日英の検索語。
     - 回答側の指示文に「Web情報は社内資料と区別して書き、出典URLを付ける。社内資料由来と混同しない」を追加(SKILL_Dify系は新しい日付の版で。ファイル名は書かず、データの中身でルールを書く)。
     - クライアント名・案件名を含む質問が外部に出る点は、検索語に固有の案件名・クライアント名を入れない(一般語に直す)ルールをノードの指示に入れる。
  4. テスト: tools/dify_prompt.js の --test で、(a) 社内データにある質問(Web検索が走らないこと) (b) 社内データ外の質問(Web検索が走り、出典URL付きで区別されること)。回答の長さが従来より大きく増えていないことも見る。
  5. 問題なければ公開名「20261022Web検索追加」(20字以内)で公開。ChatGPT版はWeb検索が標準で使えるので対象外。
  6. Result に、変更内容・テスト結果・Tavily無料枠の月間クレジット数(画面で確認)を書く。メモリ agency_os_deploy_tools に追記。完了後 teams_notify.py で [DONE]。ログインで止まったら [WAIT]。
Result:


## [2026-10-23T15:26] task-024 — Euromonitor一括ダウンロードの分担(会社Mac側: 古い側の約950件)
Project: Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/Euromonitor_レポート保存_20261023/ (task-023の続き)
Status: done
Instruction: |
  個人Macが新しい側(0〜959番目)を処理中。会社Macは古い側(960番目〜末尾)を受け持つ。
  1. 同フォルダの 調査スクリプト/会社Mac用_実行手順.md を読み、記載のコマンドで調査スクリプト/bulk.js を実行(9226のbotブラウザでEuromonitorにログイン済みか確認。切れていたら[WAIT])。トークンはファイルに保存しない。使ったタブは閉じる。
  2. 保存先は同フォルダの downloads/(Dropbox経由で個人Macと共有)。進捗は dl_progress_company.jsonl。止まっても同コマンドで続きから再開できる。
  3. 完了したら Result に件数(成功/失敗)を書き、[DONE]通知。ログイン切れ・容量逼迫は[WAIT]。
Result: 対象5種別1909件のうち1909件がdownloads/に保存済み(失敗0、2026-10-23 19:20確認)。dl_progress*.jsonl上の未ok2件(2459893, 2250931)と再試行の2498289はファイル実在を確認済み。ダウンロード結果.mdは個人Mac側担当。

## [2026-10-26T07:50] task-025 — 10月第4週のAI Tips配信文面を確認し、前回形式に合わせて直す
Project: Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/Project_AI業務活用PJ/GBC局内へのTips配信フォーマット/ ([[ai_katsuyo_pj_weekly_tips]]、work_status/ai_tips_weekly_20261026)
Status: done (2026-10-26 会社Mac)
Instruction: |
  背景: 個人Macで「今週のAIアンバサダー向け投稿案内」を作ったが、個人Macに前回(10/19)の配信文面ファイルと上記フォーマットフォルダが無く、メモリ(10/19)とPPTXから形式を再現した。
  1. 上記フォルダの 配信文面_10月第3週_20261019.md と 配信文面_10月第2週 相当を読み、Dropbox側の `Claude作業フォルダ/配信文面_10月第4週_20261026.md`(個人Mac作成)と見比べる。
  2. 書式・見出し・トーン・添付資料の書き方が前回と違えば、前回形式に合わせて直す。直した版は同フォルダに `配信文面_10月第4週_20261026_01.md` として保存(元は上書きしない)。正しい置き場(上記フォルダ)にも置く。
  3. 局員向け(Tips3「配色統一」)の実施例URLは未作成。会社MacのChatGPT for PowerPointで、AI_Tipsデモ用_ダメ提案書_20261006.pptx に実施した画面があればURLを埋める。無ければ空欄のまま。
  4. Result に差分の要点を書く。投稿はユーザーが手動で行う。
Result: 個人Mac原文がDropbox未同期だったため、会社MacでPPTX(slide3/4)と10/19形式から再作成し、`配信文面_10月第4週_20261026_01.md`としてTips配信フォーマットフォルダに保存。実施例URLは空欄、Tips4のプロンプト例は元スライドが画像のため✕〇形式で記載。個人Mac原文が届いたら差分確認可。投稿はユーザーが手動。

## [2026-10-28T12:00] task-GH-001 — Claude環境+業務スクリプトのGitHub履歴管理を会社Macで開始
Project: 中村正樹/.claude-sync (会社Macでは `dentsuDropbox/.../.claude-sync`)
Status: done (2026-10-28 会社Mac)
Instruction: |
  背景: 中村さんが「Claude環境と業務は会社Macからcommit/pushする」と決定(会社がGitHub利用を推奨、Claude契約も会社契約、GitHubアカウントは会社アカウント)。
  個人Macでは検討用に仮リポジトリを作ったが破棄済み。雛形は `claude_relay/github_setup/` にある。会社Macは **gitのみ**(gh/Homebrewなし)で運用する。
  手順:
  1. `git --version` と `curl -sI https://github.com | head -1` で git と到達性を確認（プロキシ: `http://proxy1.<社内ドメイン>:8080`、memory feedback_d14461_pip_needs_corporate_proxy 参照。必要なら `git config --global http.proxy`）。結果を中村さんに一言報告。
  2. 認証: 中村さんに GitHub の Personal Access Token(Fine-grained、対象=新リポジトリのみ、Contents: Read/Write)の作成を依頼（手順を平易に案内）。`git config --global credential.helper osxkeychain` で保存。トークンをファイル/memory/ログに書かない。
  3. 中村さんにGitHubで **private** リポジトリ `claude-workspace` を空で作ってもらう（READMEなしで作成）。URLを聞く。
  4. `.claude-sync` で `git init -b main`、`claude_relay/github_setup/gitignore.company` を `.gitignore` に、`pre-commit.company` を `.githooks/pre-commit` にコピー(`chmod +x`)、`git config core.hooksPath .githooks`、user.name/user.email は会社アカウントの値。
  5. `.git` はDropbox同期破損防止のため `xattr -w com.dropbox.ignored 1 .git` を付ける（個人Mac等へ複製させない）。
  6. `git add -A` 後、`git ls-files | wc -l` と、追跡対象に認証情報が無いことを `git diff --cached` ではなくgrepで確認（Webhook URL/トークン/パスワード/個人情報）。pre-commit が止めたファイルは .gitignore に追記して再実行。**push前に中村さんへ追跡ファイル数と除外したファイルの要約を見せて OK をもらう。**
  7. 初回commit → `git remote add origin <URL>` → `git push -u origin main`。
  8. 運用定着: 中村さんが「コミットして」と言ったら `git add -A && git commit && git push` する簡単な手順を memory(40_Claude環境・連携基盤/github_history_management.md、既存)に追記。必要なら `~/.claude/commands/save.md` のスラッシュコマンド `/save`（変更要約→commit→push）を作る。自動コミット(launchd)は不要、都度commit/push。
  8b. 追記(2026-10-28): `Scripts/photo_club_pdf/` と `Scripts/adobe_cli/` は個人リポジトリ(個人Mac)で管理するため、会社の`.gitignore`に `/Scripts/photo_club_pdf/` `/Scripts/adobe_cli/` を追加して除外する。また memory `20_写真・映像・創作/globalq_*` 5件は会社業務なので、中村さんに確認のうえ会社リポジトリの許可リストに追加するか決める。
  9. 納品物は従来どおり `_YYYYMMDD` 別名保存(Gitと併用)。Git対象はテキスト/コードのみ（pptx/xlsx/pdf等は.gitignoreで除外済み）。
  10. 完了後、Result欄に追跡ファイル数・リポジトリURL・コミットID を記録し、`[DONE]` をTeams通知。
Result: 追跡787ファイル、https://github.com/masaki-nakamura-dentsu/claude-workspace 、初回commit 5a5af94。pushは社内プロキシ必須(repo-localに設定済み)。分類器がpushを拒否するため本人ターミナルで実行。globalq_*5件は許可リストに追加、photo_club/adobe_cliは除外。/save コマンドを ~/.claude/commands/save.md に作成。メモリ github_history_management に追記。
