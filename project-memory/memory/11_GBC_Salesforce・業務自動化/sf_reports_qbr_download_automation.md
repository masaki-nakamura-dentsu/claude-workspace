---
name: sf-reports-qbr-download-automation
description: "GBC QBR用Salesforceレポート18本(2026-09-08に確度別分割3本追加→仕掛分割3本削除で正味変わらず、会社Mac・個人Mac両側とも反映済み)を1日2回(平日11:15/16:45)完全headlessで自動ダウンロードするlaunchdパイプライン。トークン不要、会社Mac(d14461)が本体、個人Mac(ICPTokyo2022)に同一レポート群の20分間隔ポーリング式フェイルオーバーあり(会社Mac未実行時のみ代行)。ダウンロード前Teams自分宛て確認(3分待ち→自動開始)を実装・実機検証済み。2026-09-09: 0バイト空ダウンロードを「OK」と誤判定する不具合を会社Mac版で発見・修正、個人Mac版にも同種の検証ロジックとfailover状態記録バグ修正を横展開済み(task-003)。2026-09-11: 16:45枠のスロットスキップ判定が11:15枠/13:00リトライの成功ファイルを誤検知し恒常的に16:45枠(道連れで18:15リトライも)をスキップしてしまうバグを発見、slot_state.json明示記録方式に修正(会社Mac版のみ、個人Mac側は未確認)"
metadata:
  node_type: memory
  type: project
  originSessionId: 5e61ff0e-1c0b-4f78-80f2-8ce143e68c5d
  modified: 2026-09-30T06:15:19.489Z
---

2026-08-26構築。目的: PowerBIのGBCダッシュボードが1日2回Salesforceデータを取り込んでいるが、過去のSalesforceデータ状態に戻れるよう、取り込みタイミングに合わせてSalesforceレポートをスナップショット保存したい、という依頼から。[[powerbi_migration_gbc_dashboard]] [[automation_schedule_overview]]（PowerBIスケジュール更新: 平日11:30/17:00 JST）が根拠。

## 対象レポート(8本、レポート名=保存先サブフォルダ名)
保存先ルート: `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し/`
- 月別見込（設定売総 X 部署）: 00O7F00000Ay7SrUAJ
- 月別見込（取設定 X 部署）: 00O7F00000Ay7SqUAJ
- （QBR集計用）月別_貢献利益（仕掛）_v2.1: 00O7F00000AycilUAB
- （QBR集計用）月別_貢献利益（仕掛）_v2.2: 00OGA00000CkNMN2A3
- （QBR集計用）月別_貢献利益（実績）_v2.3: 00OfP00000AlBNFUA3
- （設定突合用）SF案件リスト: 00OfP00000ARvMIUA1
- APAC Pitch - List All_v1.31: 00OfP00000Cq0rRUAR
- （パイプライン報告用）月別_貢献利益（仕掛）_v1.0: 00OfP00000KS6oXUAT (2026-08-27追加。元レポート00O7F00000AycilUAB=「（QBR集計用）月別_貢献利益（仕掛）_v2.1」を複製し、示達/前年度実績/前年比を削除、確度A/B/C別＋GM承認/Auth.(GBCGMauthorize__c)=TRUEのA(承認実績)を出すマトリックス列グルーピングに変更したカスタムレポート)

一覧は `~/SalesforceExport/reports_pipeline/reports_config.py` の `REPORTS`/`TARGET_ROOT`。レポートを追加/削除する場合はここを編集するだけでよい。

## 仕組み(トークンゼロで動く)
`~/SalesforceExport/reports_pipeline/download_all_reports.py` を launchd (`com.nakamura.sfreportspipeline`, StartCalendarInterval 平日11:15と16:45=PowerBI更新の15分前) が呼ぶ。1回の実行で7レポートを順に:
1. [[shared_bot_browser]]の共有ブラウザ(d14461, port 9226, `~/SalesforceExport/browser_profile`)に接続、無ければ起動。BIG-IP VPNも念のため起動([[cas_csv_download_automation]]と同じ`ensure_bigip_connected`パターンを踏襲)。
2. 各レポートURLへ遷移 → 「追加アクション - 編集」→「エクスポート」→確認ダイアログの「エクスポート」ボタンをクリック([[salesforce_report_download_automation]]の既存フローと同じセレクタ)。
3. 即時ダウンロードされればそのまま保存。本人確認コードが要求された場合は、**同じPlaywrightセッション内でOutlook Webのタブを直接操作**して`noreply@salesforce.com`の「Salesforce で ID を確認」メールを検索・本文からコード抽出・入力・ダウンロード。[[feedback_salesforce_verification_code_standing_permission]]で承認済みの「Salesforceエクスポートの確認コードは毎回許可なく自分でメールを読んで入力してよい」という標準ルールの適用。
4. 保存ファイル名はSalesforceの`suggested_filename`をそのまま使用(レポート名+ダウンロード日時が既に埋め込まれている)ため、実行のたびに新規ファイルとして蓄積され、**過去分は自動的に上書きされない**(=これが「過去のデータに戻れる」の実体)。
5. Teams Webhook([[teams_webhook_powerautomate]])で成功/失敗件数を通知。ログは`~/SalesforceExport/reports_pipeline/pipeline_log.txt`。

## 重要な設計判断: `outlook` CLIを子プロセスとして呼ぶ方式は不採用
最初はメール確認コード取得に既存の`outlook` CLI(Node.js、`~/Scripts/outlook_cli/`)を`subprocess`で呼ぶ設計だったが、実機テストで**同じCDPポート(9226)に自分のPythonスクリプトが接続したまま`outlook`を並行起動すると、`outlook list`が毎回60秒タイムアウトする**ことが判明(単独実行時は数秒で成功するため、これは競合/リソース枯渇によるもの)。**解決策**: 別プロセスを呼ばず、`outlook_cli/lib.js`と同じセレクタ(`メール、会議、ファイルなどを検索します。`のsearchボックス、`[role="listbox"][aria-label*="メッセージ一覧"]`、`[aria-label="メッセージ本文"]`)を`download_all_reports.py`内に直接Python移植し、既存の`context`(同一Playwrightセッション)でOutlook Webタブを操作するように変更。これで安定動作を確認済み(2026-08-26、7件全て成功)。**今後、同じ共有ブラウザに接続する複数の自動化を1つのスクリプト内で組み合わせる場合は、外部CLIをsubprocess経由で呼ぶのではなく、必要なセレクタを直接移植する方式を優先すること**(同時アクセスの資源競合を避けるため)。

## 検証済み結果(2026-08-26)
1本目のみ本人確認コードが要求され(コード取得〜入力まで自動で完走)、以降6本は即時ダウンロード(デバイス信頼が短時間内は有効な様子)。7件全体で約80秒。過去に手動ダウンロードしてあった同名ファイルとサイズ感が一致(例: APAC Pitch 145KB、SF案件リスト約1.48MB、v2.3約500KB)しており、内容も妥当と判断。

## launchd設定
`~/Library/LaunchAgents/com.nakamura.sfreportspipeline.plist`。`StartCalendarInterval`に平日(Weekday 1-5)×2時刻(11:15, 16:45)=10エントリ。PowerBIの実際の更新時刻(11:30/17:00)の15分前に設定し、ダウンロードが完了してからPowerBI側が取り込む形にした(両者は数分〜十数分ズレても実務上問題ない想定)。ログ: `launchd_stdout.log`/`launchd_stderr.log`(いずれも`~/SalesforceExport/reports_pipeline/`配下)。2026-08-26 16:13にload確認済み(`launchctl list`にexit code 0で表示)。

## 失敗時リトライ(2026-08-27追加)
`download_all_reports.py`にレポート単位のリトライを実装済み。`download_one_report`は`try/finally`で開いたページ(通常ページ+確認コードページ)を必ず閉じるように整理し、新設の`download_one_report_with_retry`が最大`RETRY_COUNT=3`回まで試行(失敗ごとに`RETRY_DELAY_S=20`秒待機)。`main()`のループはレポートごとに独立してtry/exceptしたまま変更なし(1本のリトライが他レポートを止めない)。3回とも失敗した場合のみNG扱いでTeams通知・`pipeline_log.txt`に記録。

## 2026-09-02更新: 本人確認方式がメールコード→Authenticator承認に変更
dentsu側のSalesforceセキュリティ要件が変わり、確認画面のデフォルトが「Salesforceシステム管理者から取得した仮のコード」入力(`TempCodeVerificationUi`)に変わった。ユーザー確認により、「別の検証方法を使用してください」→「Salesforce Authenticator」を選ぶと、ユーザーのiPhoneにpush通知が届き、そこで「承認」を押すだけでよい(コード入力不要)ことが判明。これに合わせて`download_all_reports.py`から旧来のOutlook Web自動操作によるメールコード読み取り・入力ロジック(`get_outlook_page`/`read_latest_salesforce_code`/`get_fresh_salesforce_code`)を削除し、`select_salesforce_authenticator()`で検証方法を切り替えたうえでTeams通知を送り([[teams_webhook_powerautomate]])、`AUTH_APPROVAL_TIMEOUT_MS=300000`(5分)でダウンロード開始(=承認完了)を待つ方式に変更した。[[feedback_salesforce_verification_code_standing_permission]]の「メールを自分で読んでよい」という標準許可は実質失効。

**2026-09-03検証済み**: 共有ブラウザ経由で実機テスト実施。「Salesforce Authenticator」という文言は選択肢一覧に完全一致で存在し、`get_by_text("Salesforce Authenticator", exact=True)`でヒットすることを確認。ただし当初のコードには不具合があった — 「別の検証方法を使用してください」リンクは`href="javascript:srcUp('/_ui/...')"`形式で、Playwrightの`.click()`では実際のページ遷移が発火しなかった（原因: javascript:スキームhrefのネイティブ実行は`.click()`のイベントディスパッチだけでは起きない）。修正: hrefを取得・URLデコードし、`srcUp('...')`の引数(相対パス)を正規表現で抽出、`page.goto(origin + path)`で直接遷移する方式に変更済み(`select_salesforce_authenticator()`に反映)。Authenticatorを選ぶと`ToopherVerificationFinishUi`ページ(「モバイルデバイスを確認」)に遷移し、iPhoneへpush通知が届き、ユーザーが承認すると`expect_download`が正常に発火してダウンロードが完了することをエンドツーエンドで確認済み。

## 2026-09-04: 検証画面の別バリエーション(UnifiedPasskeyVerificationUi)に未対応だった実害バグ2件を修正
9/4朝11:15枠が8本全滅(「レポートビルダーのiframeが見つかりません」)。実機調査の結果、検証方式がセッションのたびに変わっており(TempCodeVerificationUi/UnifiedPasskeyVerificationUi/TotpVerificationUi/ToopherVerificationFinishUiなど複数バリエーションが確認されている)、このとき遭遇したのは**レポートを開いた瞬間、`page.goto(url)`自体が同じページ内でそのまま検証画面`UnifiedPasskeyVerificationUi`にリダイレクトされる**パターンだった。従来のコードは「エクスポートボタンを押した後に別タブで検証画面が開く」パターンしか想定しておらず、`get_builder_frame()`が存在しないiframeを30秒待ち続けてタイムアウトし、検証処理に一切入れずに毎回失敗していた。加えて、この`UnifiedPasskeyVerificationUi`画面の「別の検証方法を使用してください」リンクは、9/3に確認した`javascript:srcUp(...)`形式ではなく**通常の相対パスのhref**(`/_ui/identity/verification/policy/VerificationStartUi/e?...`)であることが判明し、旧`srcUp`専用の正規表現パースが失敗していた。

**修正内容**(`download_all_reports.py`):
1. `download_one_report()`で`page.goto(url)`直後に`VERIFY_FRAGMENT in page.url`をチェックし、その場でリダイレクトされているケースを検知したら即座に検証フローへ入るようにした(従来の「新規タブ出現待ち」ロジックとは別経路)。
2. 検証成功後のダウンロード待ち処理を`approve_verification_and_download()`ヘルパーに切り出し、上記の即時リダイレクト経路と、従来の(エクスポート後に別タブが開く)経路の両方から呼べるように統合。
3. `select_salesforce_authenticator()`のリンク解析を、`href`が`javascript:`スキームなら`srcUp()`引数を正規表現抽出、そうでなければ`href`をそのまま相対パスとして使う、の両対応に変更。

**ネイティブパスキー(WebAuthn) overlayについて(実害なしと判断)**: `UnifiedPasskeyVerificationUi`ページには常時`<div id="overlay" class="overlay">`(`backdrop-filter: blur(4px)`, `pointer-events: auto`, 全画面固定)が存在し、これはページロード時にブラウザネイティブのパスキー(WebAuthn)UIが自動的に呼ばれていることを示すと見られる(ユーザーが目視した際に「QRコードの画面が出る」と報告した対象は恐らくこれ)。ただしスクリプトはこのページ上で一切`.click()`しておらず(「別の検証方法を使用してください」リンクは`get_attribute("href")`でDOM経由読み取りのみ→`goto()`で直接遷移)、overlayによるクリック妨害の実害は確認されなかった。遷移先の「検証方法を選択してください」ページにはoverlayが存在せず、`elementFromPoint()`で「Salesforce Authenticator」テキスト中央の最前面要素が実際にその文字列自身であることも確認済み(クリックは正しい対象に当たっている)。念のためユーザー要望で`select_salesforce_authenticator()`冒頭に`verify_page.keyboard.press("Escape")`を追加(ネイティブダイアログが残っていた場合の保険)。

**運用面の並行課題(コードの不具合ではない)**: 上記2バグ修正後の初回再実行では、Authenticatorのpush通知が**iPhone側でサイレント配信**になっており、5分(`AUTH_APPROVAL_TIMEOUT_MS`)以内にユーザーが気づけずタイムアウトした。iOS設定(設定→通知→Salesforce Authenticator→即時配信/バナー/サウンドON、集中モードの許可リストに追加)の見直しをユーザーに依頼。**重要な運用上の性質**: 認証は1回のパイプライン実行(8レポート)につき通常1回のみ必要で、一度承認されると同一ブラウザセッション内では残りのレポートは即時ダウンロードされる(デバイス信頼が短時間有効になる)。よって最初の1本さえ承認できれば残り7本は自動で流れる。

**2026-09-04 14:41実機再検証**: 上記全修正込みで手動実行、8/8成功・所要2分弱・通知も正常着信(ユーザー確認済み)。次回以降の定時実行(平日11:15/16:45)で無人稼働時の安定性を継続観察中。

## 2026-09-06: レポート追加(9本目)、および個人Mac(ICPTokyo2022)側フェイルオーバーパイプライン新規構築

ユーザーからSalesforceレポートURL5件の追加依頼があり、既存8本と照合した結果、4本(SF案件リスト/v2.3/APAC Pitch/v2.2)は登録済み、**1本が新規**と判明: `00O7F00000Ayt1TUAR`「（QBR集計用）月別_設定利益（仕掛）_v2.1」(既存の「貢献利益」v2.1とは別の「設定利益」レポート)。会社Mac側`reports_config.py`の`REPORTS`にこの1本を追加する必要がある(このメモリを書いている個人Mac側からは会社Macのファイルを直接編集できないため、会社Mac側セッションでの追記が必要 — 未実施の場合は次回会社Macセッションで反映すること)。

続けてユーザーから「会社Macが動いていない場合、個人Macでも実行するようにしたい」と依頼があり、**個人Mac(ICPTokyo2022)に完全に独立したフェイルオーバー環境を新規構築**(Python版ではなくNode.js/Playwright版、[[claude_playwright_setup]]の永続環境を利用):

### 構成(`~/SalesforceExport/reports_pipeline_personal/`、個人Mac限定)
- `reports_config.js` — 9レポート全件(会社Macと同一ID)。`TARGET_ROOT`は**会社Macと全く同じDropbox共有パス**(`.../Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し`)なので、両Macからの出力が同じフォルダ群に集約される(ファイル名にSalesforceのdownload日時が入るため衝突なし)。
- `download_all_reports.js` — 会社Mac版と同じロジック(iframe内「追加アクション - 編集」→「エクスポート」、検証要求時はSalesforce Authenticator選択→push通知承認待ち)をNode.js/Playwrightで再実装。個人Macの共有ブラウザ(port 9227、`~/.chrome-profiles/timetree-bot`、[[shared_bot_browser]])に接続。9レポート全件、実機テストで成功(初回1本は検証要求→Authenticator承認→ダウンロード成功、残り8本はデバイス信頼により即時ダウンロード)。
- `failover_check.js`/`run_failover_check.sh` — 会社Mac側の定時実行(平日11:15/16:45)から30分の猶予後、代表レポート(先頭)フォルダの最新ファイルのmtimeがそのスロット時刻以降かをチェックし、無ければ「会社Mac未実行」と判定して`download_all_reports.js`をフル実行。`failover_state.json`に処理済みスロットを記録し二重実行を防止。
- `com.nakamura.sfpersonalfailover.plist` — **CASパイプライン([[cas_csv_download_automation]])と同じ20分間隔ポーリング方式**(`StartInterval=1200`、`StartCalendarInterval`の固定時刻式は不採用)。理由: 固定時刻式はMacがスリープ中だと取りこぼしを自動リトライしないという既知の弱点があるため、フェイルオーバー用途ではポーリング式の方が適切と判断。ロード済み・exit code 0で稼働確認済み(2026-09-06)。

### 技術的発見(個人Mac版実装時に判明、会社Mac版コードにも当てはまる可能性あり)
- **レポートビルダーiframeの検出はframe名ではなくURLで行うべき**: 会社Macメモリは「frame name matching `lightningReportApp.app`」としていたが、実機確認では`frame.name()`は`builder-<timestamp>-<random>`という動的な値で、`lightningReportApp.app`は**URLの一部**(`.../reports/lightningReportApp.app?reportId=...`)としてのみ出現した。`f.url().includes('lightningReportApp.app')`で検索する方が確実。
- **「別の検証方法を使用してください」リンクの`href`属性は、`javascript:srcUp('...')`形式の場合、内部の`'`がブラウザの`getAttribute()`経由だと`%27`にエンコードされた状態で返ってくることがある**(例: `javascript:srcUp(%27%2F_ui%2F...%27)`)。素の正規表現`/srcUp\('([^']+)'\)/`だとマッチしないため、**先に`decodeURIComponent(href)`してから正規表現マッチする**必要がある(個人Mac版`extractSrcUpTarget()`で対応済み)。
- 検証画面`UnifiedPasskeyVerificationUi`で、ユーザーがブラウザネイティブのパスキー(WebAuthn)QRコードダイアログを目視することがあるが、スクリプトはこのダイアログを操作せず(DOM経由でリンクhrefを読むだけ)、無視して問題ない(実害なしと確認済み、[[shared_bot_browser]]の既存記載と同じ現象)。

## 2026-09-07: レポート9本追加(計17本)、ダウンロード前のTeams確認機能を追加

ユーザーからレポートURL9件の追加依頼。IDプレフィックス`00OfP`の新規レポートで、3本(`KuV0n`/`KuV5d`/`KuVC5`)は本人確認(`UnifiedPasskeyVerificationUi`)経由でのみ名前取得できた。実体は既存レポートの「_A/_B/_C」分割版:
- 月別見込（設定売総 X 部署）_A/_B/_C: `00OfP00000KuUb0UAF` / `00OfP00000KuVonUAF` / `00OfP00000KuVyTUAV`
- 月別見込（取設定 X 部署）_A/_B/_C: `00OfP00000KuWL3UAN` / `00OfP00000KuWRVUA3` / `00OfP00000KuWWLUA3`
- （QBR集計用）月別_貢献利益（仕掛）_v2.1_A/_B/_C: `00OfP00000KuV0nUAF` / `00OfP00000KuV5dUAF` / `00OfP00000KuVC5UAN`

会社Mac側`reports_config.py`の`REPORTS`に追加済み(計17本)。**個人Mac側`reports_pipeline_personal/reports_config.js`はこのセッションから直接編集できないため未反映** — 次回個人Macセッションで同じ9本を追記すること(前回2026-09-06の1本追加時と同じパターン)。

### ダウンロード前確認機能(新規)
「ダウンロードの時にいつも作業の邪魔になる」という要望を受け、`download_all_reports.py`の`_run_pipeline()`冒頭に`ask_before_download(context)`を追加。処理:
1. 共有ブラウザの既存Teamsタブ(`teams.microsoft.com`)を探し、自分とのチャット(`...(あなた)`)を開く。
2. 現在のメッセージ数を記録してから「Salesforceレポートのダウンロードを開始します。作業の邪魔になる場合はこのチャットに何か返信してください。3分以内に返信がなければそのまま自動的に開始します。」を投稿。
3. 3分間、5秒間隔でメッセージ数の増加(=返信)をポーリング。返信を検知したら即座に、無ければ3分経過後に、いずれにせよダウンロードを開始する。

**設計上の重要な注意**: これは「返信内容を解釈してキャンセルする」機能ではない — 返信の有無に関わらず最終的には必ずダウンロードを開始する。目的はブラウザが不意に動き出すことの事前アナウンスと、返信すれば早められる猶予を与えること。もしユーザーが将来「返信内容(拒否等)でキャンセルできるようにしたい」と言ったら、この関数の拡張が必要(現状は未実装)。
Teamsタブが見つからない/操作失敗時は例外を握りつぶしてログに残し、ダウンロード自体は止めない(既存の`send_teams`失敗時と同じ「通知は失敗してもパイプラインは止めない」方針)。

**実機検証済み(2026-09-07 10:03〜10:09)**: 実際にTeams自分宛てチャットに確認メッセージが投稿され、3分間返信がなかったため自動開始→17本全て成功(所要約5分半、うち3分は確認待ち)。9本追加分もすべて正しいサブフォルダに保存されたことをファイル一覧で確認済み。

## 2026-09-07(同日追記): 未反映だった「設定利益」v2.1の1本を追加(計18本)

2026-09-06のメモリで「会社Mac側`reports_config.py`への追加が未実施」と記録されていた`00O7F00000Ayt1TUAR`（QBR集計用）月別_設定利益（仕掛）_v2.1(既存の「貢献利益」v2.1とは別レポート)を、ユーザーからの再依頼で追加。単体ダウンロードで実機検証済み(2026-09-07 12:26、正しいサブフォルダに保存確認)。これで会社Mac側は本来意図されていた18本全てが揃った状態になった。

## 2026-09-08: 個人Mac側フェイルオーバーパイプラインに、会社Macの2026-09-07変更(レポート9本+Teams事前確認)を反映

会社Mac側`reports_config.py`は2026-09-07時点で18本(既存8本+同日追加9本+設定利益v2.1)が揃っていたが、個人Mac側`reports_pipeline_personal/reports_config.js`は9本(既存8本+設定利益v2.1のみ、2026-09-07追加分9本が未反映)のままだった。このセッションで以下を実施:

1. **`reports_config.js`に9本追加、計18本に**(会社Macと完全一致のID/フォルダ名): `（QBR集計用）月別_貢献利益（仕掛）_v2.1_A/_B/_C`、`月別見込（設定売総 X 部署）_A/_B/_C`、`月別見込（取設定 X 部署）_A/_B/_C`。
2. **`download_all_reports.js`にダウンロード前Teams確認機能(`askBeforeDownload`)をNode.js移植**: 会社Mac版Python(`ask_before_download`)と同じロジック(共有ブラウザの既存Teamsタブ→自分とのチャットを開く→現在のメッセージ数を記録→事前アナウンス投稿→5秒間隔×3分ポーリングで返信検知→検知/未検知いずれもダウンロード開始)。セレクタは[[teams_cli]]の`~/Scripts/teams_cli/lib.js`(`[data-tid="simple-collab-dnd-rail"]`でチャット一覧、`(あなた)`で自分とのチャット判定、`[data-tid="ckeditor"]`が入力欄、送信ボタンは`newMessageCommands-send`→`sendMessageCommands-send`→`aria-label*="送信"`の3段フォールバック)をそのまま移植・流用。Teamsタブが見つからない/操作失敗時は例外を握りつぶしログに残すのみで、ダウンロード自体は止めない設計(会社Mac版と同じ方針)。

**実機検証の過程で判明した副次的な事実**: 個人Mac共有ブラウザ(port 9227、[[shared_bot_browser]])のSalesforce SSOセッションとTeamsセッションが両方とも切れていた(自動化のバグではなく、単純な長期未使用によるセッション失効)。ユーザーに画面上へブラウザを表示して再ログインを依頼し、両方復旧。

**実機検証結果(2026-09-08)**:
- 18本フルパイプライン: 全件成功(初回のみSalesforce Authenticatorのpush承認が必要、以降17本は即時DL、所要約3分半)。
- Teams確認機能単体テスト(`node download_all_reports.js <reportId>`で1本のみ指定): 自分宛てチャットに「Salesforceレポートのダウンロードを開始します。作業の邪魔になる場合はこのチャットに何か返信してください。3分以内に返信がなければそのまま自動的に開始します。」が実際に投稿されることを確認。3分間無返信→ログに「3分経過、返信なし。ダウンロードを開始します。」と記録され自動的にダウンロード実行・成功。
- フォールバック動作(Teamsタブ操作失敗時にダウンロードを止めない)も、Teamsセッション切れの状態で偶発的に実機確認できた(`locator.waitFor: Timeout`をキャッチしログ記録した上でダウンロードは正常続行)。

これで会社Mac・個人Mac双方が同一の18本+ダウンロード前Teams確認機能で揃った状態になった。

## 2026-09-08(続き): レポート3本追加(計21本)

ユーザーからレポートURL3件の追加依頼。いずれも`00OfP`プレフィックスの新規レポートで、実体は既存の「（QBR集計用）月別_貢献利益（仕掛）_v2.1」の確度別(A/B/C)分割版と判明(タイトルから直接取得、確認画面を経由せず即座に判明):
- （QBR集計用）月別_貢献利益（仕掛）_v2.1_確度A: `00OfP00000Kz63NUAR`
- （QBR集計用）月別_貢献利益（仕掛）_v2.1_確度B: `00OfP00000Kz6D3UAJ`
- （QBR集計用）月別_貢献利益（仕掛）_v2.1_確度C: `00OfP00000Kz6JVUAZ`

注意: 既存の`_A/_B/_C`(2026-09-07追加、`00OfP00000KuV0n`等)は「（QBR集計用）月別_貢献利益（仕掛）_v2.1」の**仕掛/示達等の項目分割**版であるのに対し、今回の`_確度A/_確度B/_確度C`は**確度別**の分割版で別物。フォルダ名を`_確度A`のように区別して命名し、既存の`_A`と衝突しないようにした。

会社Mac側`reports_config.py`の`REPORTS`に追加済み(計21本)。3本とも単体テストで実機ダウンロード成功、正しいサブフォルダに保存確認済み(2026-09-08 16:02〜16:03)。個人Mac側への反映は[[mac_handoff_relay]]の自動引き継ぎキュー(`personal_mac_inbox.md` task-001)で依頼済み。

## 2026-09-08(続き): レポート3本を削除(計18本に戻る)

ユーザーから「（QBR集計用）月別_貢献利益（仕掛）_v2.1_A/_B/_C」(2026-09-07追加、`00OfP00000KuV0nUAF`/`00OfP00000KuV5dUAF`/`00OfP00000KuVC5UAN`)の3本が不要になったとの指示があり、会社Mac側`reports_config.py`の`REPORTS`から削除(21本→18本)。既存のダウンロード済みファイルは削除せず、今後のダウンロードのみ停止。個人Mac側`reports_pipeline_personal/reports_config.js`への同じ削除依頼を[[mac_handoff_relay]]の`personal_mac_inbox.md` task-002として投入済み(次回個人Macセッションで自動的に拾われる想定)。

**注意**: 同日追加した「確度A/B/C」分割版(`00OfP00000Kz63NUAR`等)とは別物 — こちらは削除対象ではなく残っている。

## 2026-09-09: 確度A/B/C限定でダウンロード後の自動フォーマット処理を追加

ユーザー依頼: 「確度A/B/C」の3レポートに限り、ダウンロード後に自動で
(1) T/U/V/W列(Group売総・GBC貢献売総A/AB/ABC、いずれも金額列)に桁区切り`#,##0`、
(2) 各部の小計行(B列が`小計`のレコード)をFFFB00(黄色)でハイライト、
を適用してほしいとの依頼。

**実装**: `~/SalesforceExport/reports_pipeline/xlsx_post_process.py`を新設。
`KAKUDO_FORMAT_REPORT_IDS`(3レポートのID)に含まれるレポートのみ、
`download_all_reports.py`の`download_one_report_with_retry()`内でダウンロード
成功直後にopenpyxlで後処理(`apply_kakudo_formatting`)を適用する設計にし、
他の15レポートには一切影響しない。フォーマット処理が失敗してもダウンロード
自体は成功扱いにする(ログに警告のみ記録、パイプライン全体は止めない)。

**小計行の判定について**: レポートの実データを確認したところ、部署ごとの
集計行はB列(部署名列)に`小計`、C列に`合計`という2段のラベルが入っており、
全部署合算の最終行だけB列が`合計`(グランドトータル)になっている。ユーザーの
「各部ごとの合計行」という表現は、複数ある「各部」という言葉から**部署単位の
`小計`行**を指すと解釈し、単一の`合計`(グランドトータル)行は対象外とした
(もし全体合計行も含めたい場合は`xlsx_post_process.py`の判定条件を`in ("小計", "合計")`に変更するだけでよい)。

**実機適用結果(2026-09-09)**: 3フォルダに既存保存されていた17ファイル全件に
即時適用、全件成功確認済み。パイプラインへの組み込み(単体ダウンロードテスト)も
実施中(会社Mac、`personal_mac_inbox.md`への同機能の横展開は未依頼 — 必要なら
個人Mac側`download_all_reports.js`にも同じロジックを移植する必要がある)。

**発見した別件(未対応の要確認事項)**: 「確度A/B/C」の3フォルダの中に、
2026-09-07付のファイル(旧・仕掛項目分割版`_A/_B/_C`、id`00OfP00000KuV0nUAF`等、
今回削除依頼したレポート)も混在していることに気づいた。本来は別レポート
(別ID)なので別フォルダに保存されるはずだが、現状同じフォルダに同居している
— いつ・誰が(会社Mac側の操作ではない)フォルダを統合/リネームしたのかは
不明。実害としては、フォーマット処理自体はどちらの由来のファイルにも
問題なく適用できたが、**データの出自が混ざっている状態は本来おかしい**ため、
ユーザーに確認・整理が必要な可能性がある。

## 2026-09-09: 「月別見込（設定売総 X 部署）_A/B/C」限定で書式自動化＋過去月列削除を追加

ユーザー依頼: 確度A/B/Cと同様の書式(桁区切り+小計ハイライト)に加えて、この3レポートは
「前月までの数字は使えない」ため、ダウンロード時に当月より前の年月列を削除し、合計列も
それに合わせて再計算してほしいとの依頼(対象は`月別見込（設定売総 X 部署）_A/_B/_C`、id
`00OfP00000KuUb0UAF`/`00OfP00000KuVonUAF`/`00OfP00000KuVyTUAV`のみ、他の`_A/_B/_C`系
レポート — 例えば`月別見込（取設定 X 部署）_A/B/C`や確度A/B/C — は対象外)。

**実装**: `xlsx_post_process.py`に`apply_forecast_trim_formatting`と
`FORECAST_TRIM_REPORT_IDS`(上記3レポートIDのみ)を追加。処理内容:
1. シート内で`年月 →`という文字列を探して見出し行を特定(ハードコードせず動的検出)。
2. 見出し行の値が`\d{6}`(YYYYMM)形式の列を年月列、`合計`の列を合計列として検出。
3. `datetime.now()`の年月より小さい年月列を`ws.delete_cols()`で削除(列インデックスは
   降順に処理して安全にシフト)。
4. 削除後、見出し行より下の各行について、合計列の値を「残った年月列だけの合計」で
   再計算 — ただし**元の合計セルが数値だった行、または残り年月列のいずれかが数値だった
   行のみ**再計算する(下記バグ参照)。
5. 残り年月列+合計列に`#,##0`、各部小計行(B列=`小計`)をFFFB00でハイライト
   (確度A/B/Cと同じ仕組みをそのまま流用)。
既存の`apply_if_target()`ディスパッチ(`download_all_reports.py`から呼ばれる唯一の
エントリポイント)にIDセットを追加しただけなので、パイプライン本体のコード変更は不要。

**実装中に発生し即座に修正したバグ**: このレポートは見出し行の直下(row15)に、各年月列
繰り返しの「メジャー名ラベル行」(例: 'GBC設定売総/SETTEI Rev(JPY) 合計:'という文字列が
年月列の数だけ、かつ**合計列にも**繰り返し入っている)が存在する。当初の再計算条件が
「残り年月列に数値がある、**または**合計列の元の値がNoneでない」だったため、この
ラベル行の合計セル(文字列)が「Noneでない」に該当してしまい、再計算結果の0(数値)で
上書きされてラベルが消える事故になった。**修正**: 条件を「残り年月列に数値がある、
または合計列の元の値が**int/float**である」に変更(文字列は対象外)。既に処理済みだった
25ファイル全件(2フォルダ分、_B/_C計18件)がこのバグの影響を受けていたため、壊れた
ラベルセルを「同じ行の隣接年月列に残っている同一文字列」から復元する形で個別に修復し、
グランド合計行の再計算値を実データと突合して全件正常を確認済み(2026-09-09)。

**実機適用結果(2026-09-09)**: 3フォルダに既存保存されていた計27ファイル全件に適用・
検証済み。当初、Excelで開いていた2件(`_A`フォルダ内、ロックファイル`~$...`の存在で
検知しスキップ)を除く25件に先行適用し、同日中にユーザーがExcelを閉じた後、残り2件も
処理して27件全件完了。処理時点(2026-09-09、9月)を基準に202601〜202608列を削除し、
202609〜202612+合計列のみ残る形になっている。

**未対応**: 個人Mac側`reports_pipeline_personal/download_all_reports.js`にはこの新機能
(確度A/B/Cの`apply_kakudo_formatting`含め)は移植されておらず、Python版
(`reports_pipeline/`, 会社Mac)のみの対応。

## 2026-09-09(続き): 対象を5レポート追加(計8レポートに)

ユーザーから「月別見込（取設定 X 部署）」の無印/_A/_B/_Cと、「月別見込（設定売総 X 部署）」
の無印(確度A/B/C込みの合算版)にも同じ自動処理(桁区切り+小計ハイライト+過去月列削除+
合計再計算)を適用してほしいとの追加依頼。列構造(`年月 →`見出し行、YYYYMM形式の年月列、
`合計`列、B列の`小計`/`合計`ラベル)を実ファイルで確認したところ「設定売総」版と完全に
同一(メジャー名のみ`GBC取設定/SETTEI TO(JPY)`か`GBC設定売総/SETTEI Rev(JPY)`かの違い)
だったため、既存の`apply_forecast_trim_formatting`をそのまま流用可能と判断。

`xlsx_post_process.py`の`FORECAST_TRIM_REPORT_IDS`に以下5件を追加(計8件):
- 月別見込（設定売総 X 部署）(無印): `00O7F00000Ay7SrUAJ`
- 月別見込（取設定 X 部署）(無印): `00O7F00000Ay7SqUAJ`
- 月別見込（取設定 X 部署）_A: `00OfP00000KuWL3UAN`
- 月別見込（取設定 X 部署）_B: `00OfP00000KuWRVUA3`
- 月別見込（取設定 X 部署）_C: `00OfP00000KuWWLUA3`

既存保存済み69ファイル(5フォルダ、ロックファイルなし=全件Excel未使用だったため
スキップ無し)全件に即時適用済み。全件についてラベル行の文字列が保持されているか、
グランド合計セルが残り年月列の実データ合計と一致するか、小計行にFFFB00ハイライトが
付いているかを機械的に検証し、69件全て異常なしを確認済み(2026-09-09)。

## 2026-09-08(続き): 個人Mac版を並列ダウンロード化+ウィンドウのフォーカス奪取対策

ユーザーから「1本ずつ順番に落ちているが、時間短縮のため並列化できないか」との依頼。`download_all_reports.js`(個人Mac版のみ、会社Mac版Pythonは変更なし)を以下のように変更:

**並列化の設計**: 全レポートをいきなり並列で投げるのではなく、1本目だけ逐次実行してから残りを並列化する2段構成にした。理由: Salesforce Authenticatorのpush承認は「デバイス信頼」が確立するまでの最初の1回だけ必要で、複数レポートを同時に投げるとpush通知が同時多発しかねないため。`downloadReportsConcurrently(context, reports, concurrency)`がworker pool方式(`nextIndex`をインクリメントしながら各workerが次のレポートを取得)で実装、workerごとに`WORKER_STAGGER_MS`だけ開始をずらして一斉に`page.goto`が走らないようにしている。

**並列度の実機チューニング**: 18本全件の実機テストを複数回実施し、以下の結果から並列度3を採用:
- 並列度5、stagger 800ms: 16/18成功(2本が3回リトライ全滅、`page.waitForTimeout: Target page, context or browser has been closed`エラー) — 複数の重いLightningレポートビルダーiframeを同時ロードした際、共有ブラウザのタブが強制終了されたとみられる。
- 並列度3、stagger 1500ms: 17/18→18/18(2回実機テスト、いずれも既存のリトライ機構(最大3回、20秒間隔)で最終的に全件回収)。
- 所要時間: 逐次実行(旧方式)が18本で約169秒だったのに対し、並列度3では約101〜121秒(Teams確認3分の待ち時間は除く)。約30〜40%短縮。
- 結論: 並列度5は速いが不安定、3が実用上の妥協点。`page closed`系のエラーは既存のリトライロジックで自然に回収されるため実害は小さいが、並列度をこれ以上上げるとリトライでも回収しきれない可能性がある。

**副作用として発覚したウィンドウのフォーカス奪取問題**: ユーザーから「ダウンロードのたびに共有ブラウザのウィンドウがアクティブになり、作業中の入力が中断される」との指摘。原因は[[shared_bot_browser]]に既出の既知挙動 — `context.newPage()`がウィンドウを強制的に`windowState: "normal"`に戻し前面化する(`goto()`/`click()`など既存ページの操作では起きない)。個人Mac版`download_all_reports.js`にはこれまでこの対策が一切入っていなかった(会社Mac版Pythonにはreposition_offscreen/get_frontmost_app等の対策が2026-09-02から入っていたが、個人Mac版Node.js移植時に移植漏れだった)。並列化でレポートごと・リトライごとに`newPage()`が頻発するようになったことで問題が顕在化した可能性が高い。

**修正**: `~/Scripts/outlook_cli/lib.js`で実績のある対策パターン(`repositionOffscreen`/`getFrontmostApp`/`restoreFrontmostApp`)をそのまま移植し、`newPageWithFocusGuard(context)`としてラップ。`downloadOneReport()`内の`context.newPage()`をこれに置き換え、newPage()の直前にフォアグラウンドアプリを記録→ウィンドウ生成後すぐ画面外(-2500,-2500)へ退避→記録したアプリへフォーカスを戻す、を毎回実行するようにした。実機テスト(並列度3+この対策込み)で18/18成功を確認、ユーザーへの作業中断は解消想定(挙動自体は目視確認依頼中)。

## 2026-09-09: ブラウザ接続切断による全滅事故と自動リカバリ追加

朝11:15の定時実行が18本全滅(11:15〜12:39の84分間、全レポートが
"BrowserContext.new_page: Target page, context or browser has been closed"
で失敗)。ユーザーが「Salesforceの自動ダウンロードが上手くいかなかったよう」と
報告して発覚 — パイプライン自体には失敗を検知して自発的に再試行する仕組みが
無かったため、ユーザーが気づくまで放置される状態だった。原因はブラウザ
(共有ボットブラウザ、port 9226)のCDP接続が実行中に切れたこと(真因は未特定 —
Chrome自体はその後も9226で生きていたため、プロセスクラッシュではなく
コンテキスト/接続レベルの切断とみられる)。従来のレポート単位リトライ
(3回・20秒間隔)は同じ死んだコンテキストに向かって`new_page()`し続けるだけで
無意味だった。ブラウザ自体は生きていたため、その場で`python3 download_all_reports.py`
を手動再実行したところ18/18成功(12:41〜12:53)。

ユーザー依頼「全滅時の自動リカバリを追加して」を受け、`download_all_reports.py`に
以下2点を実装(構文チェック済み、次回定時実行で実地検証待ち):

1. **`BrowserState`クラスによるCDP接続の自動再接続**: レポート単位リトライの
   各試行前に`browser.is_connected()`で接続の生死を確認し、切れていれば
   `ensure_shared_browser_running()`(Chrome自体の起動確認)を経てCDP再接続する。
   `download_one_report_with_retry(context, report)`のシグネチャを
   `download_one_report_with_retry(state: BrowserState, report)`に変更。
   これが今回の事故の直接原因への根本対策(次回同じ切断が起きても、リトライの
   1回目で再接続され2回目以降は正常成功する見込み)。
2. **全滅時のみパイプライン全体を自動再実行**: `_run_pipeline()`が
   `(ok_count, ng_count, total)`を返すよう変更し、`main()`が
   `ok_count == 0`(全滅)の場合のみ5分待ってパイプライン全体を再実行
   (`TOTAL_FAIL_RECOVERY_COUNT=2`、最大2回=合計3試行)。1件でも成功すれば
   打ち切り(個別リトライで吸収済みと判断)。3回連続全滅の場合のみTeams通知して
   諦める(無限リトライは避けた)。リカバリ再実行時はダウンロード前のTeams確認
   (`ask_before_download`)をスキップ(`is_recovery`引数で制御、3分待ちの
   繰り返しを避けるため)。

**未対応**: 個人Mac側`reports_pipeline_personal/download_all_reports.js`
(Node.js版)にはこの自動リカバリロジックは移植されていない。同様の全滅事故が
個人Mac側フェイルオーバーで起きた場合の対策は今回の対象外。

## 2026-09-09(続き): 13:00補助リトライを追加(昼の移動時間対策)

ユーザーから「昼の時間は移動時間に引っかかる可能性が高く、その間は会社Macが
閉じている。もし昼前(11:15)の更新が動いていなかった場合、13時にも更新トライ
するようにして」との依頼。11:15の定時実行はStartCalendarInterval方式のため、
会社Mac自体が閉じていて起動できなかった場合は取りこぼしても自動リトライしない
(既存の「未検証・今後の注意点」参照) — 上記の`BrowserState`/全滅時リカバリは
あくまで「起動はできたが失敗した」場合の対策であり、「そもそも起動できなかった」
ケースには効かないため、別途の保険として追加。

**実装**: `~/SalesforceExport/reports_pipeline/retry_1300_if_missed.py`を新設。
代表レポート(`REPORTS[0]`)の保存先フォルダを見て、最新ファイルのmtimeが
今日の日付でなければ「11:15分が未実行」と判断し`download_all_reports.py`を
フル実行する。既に本日分がある(=11:15が起動できていた)場合は何もしない
(二重実行防止のロジックは[[sf_reports_qbr_download_automation]]の個人Mac
フェイルオーバー`failover_check.js`と同じ「代表フォルダのmtineチェック」方式)。
新規launchdジョブ`com.nakamura.sfreports1300retry.plist`(平日13:00、
既存の11:15/16:45ジョブとは別のLabelで独立稼働)としてload・稼働確認済み
(2026-09-09、`launchctl list`にexit code 0で表示)。

**構文チェック済み、実地検証はまだ** — 実際に会社Macが閉じた状態で11:15を
跨いだケースでの動作確認は今後の課題。

## 2026-09-09(続き): 16:45枠で16本が「OK」判定だが実は0バイトの空ファイルだった不具合を発見・修正

ユーザーから「ダウンロードしたのに0KBがいくつかある」と報告(当初ユーザー自身は「後処理が必要なファイルかも」と推測していたが、これは誤り — 0バイトは単純にダウンロード失敗で、post-processing対象かどうかとは無関係)。

**実態**: 16:45枠の実行で18本中、最初の2本(無印の「月別見込」2本)だけ実データで成功、残り16本は`pipeline_log.txt`に「OK」と記録されていたにもかかわらず実ファイルが0バイトだった。`xlsx_post_process.py`の後処理対象(確度A/B/C、設定売総/取設定のA/B/C)では「File is not a zip file」という警告ログが出ていたため発覚。後処理対象外のレポート(v2.2/v2.3/SF案件リスト/APAC Pitch/v1.0/設定利益v2.1等)は後処理自体が走らないため警告も出ず、0バイトのまま「成功」扱いで見過ごされていた。

**根本原因(推定)**: このセッションでは実行中にユーザーが「動いてない」→「認証したけど動いてない気がする」と報告する場面があり、1本目のSalesforce Authenticator承認が5分タイムアウトに間に合わず(試行1失敗)、試行2で成功した経緯があった。この遅延承認絡みの混乱の直後から、Chromeのダウンロード機構が内部的にキャンセル/ブロックされる状態に入ったとみられる(3本目で明示的に`Download.save_as: canceled`エラーが1回発生、その後はエラーなしで0バイトファイルが量産された)。Playwrightの`download.save_as()`は、ブラウザ側でダウンロードがキャンセルされていても例外を出さずに空ファイルを作ってしまうことがある、という新しい既知の失敗モード。

**恒久対策(実施済み、会社Mac版`download_all_reports.py`のみ)**: `validate_download(dest)`関数を追加し、`save_as()`直後にサイズ0チェック+`zipfile.is_zipfile()`によるxlsx形式チェックを実施。不正な場合は例外を出し、既存のリトライ機構(`download_one_report_with_retry`、最大3回)に回収させるようにした。これで今後同じ不具合が起きても「OK」と誤判定されず、自動リトライで正しいファイルに置き換わるはず(構文チェック済み、次回定時実行で実地検証待ち)。

**その場の応急対応**: `~/SalesforceExport/reports_pipeline/`にある`REPORTS`/`TARGET_ROOT`と`BrowserState`/`download_one_report_with_retry`を再利用し、当日フォルダ内で0バイトだったファイルだけを判定して再ダウンロードするワンオフスクリプトをスクラッチパッドに作成・実行。16本全て実データで再取得に成功し、空ファイルは削除済み(2026-09-09 17:09-17:12)。

**未対応**: 個人Mac側`reports_pipeline_personal/download_all_reports.js`(Node.js版)にはこの検証ロジックは移植されていない。同様の不具合が個人Mac側フェイルオーバーで起きた場合は今回の対象外(移植が必要)。

## 2026-09-09(続き): 夕方(18:15)補助リトライを追加(移動時間対策、13:00版の夕方版)

ユーザーから「夕方も定時ダウンロードが成功していない場合、そのタイミングの1時間半後に再トライして。夕方に移動時間があってMacを開いていない可能性があるため」との依頼。[[sf_reports_qbr_download_automation]]の11:15枠向け13:00リトライ(`retry_1300_if_missed.py`)と同じ発想の、16:45枠向け版。

**13:00版との違い(判定ロジック)**: 13:00版は「今日の日付のファイルが1つもなければ11:15が未実行」で足りた(その時間帯にはまだ何も走っていないはずだから)。しかし18:15版で同じ「今日の日付か」判定を使うと、11:15分または13:00リトライ分のファイルが既に今日の日付で存在するため「実行済み」と誤判定してしまう。そこで**「代表レポート(REPORTS[0])の最新ファイルのmtimeが今日の16:45以降か」**で判定するように実装(`retry_1815_if_missed.py`の`downloaded_since_1645()`)。16:45以降の実績が無ければ会社Macが閉じていたと判断し、`download_all_reports.py`をフル実行する。

**実装**: `~/SalesforceExport/reports_pipeline/retry_1815_if_missed.py`新設(13:00版と同じ二重実行防止パターン)。launchdジョブ`com.nakamura.sfreports1815retry.plist`(平日18:15、Label以外は13:00版と同構成)を新規作成・load・稼働確認済み(2026-09-09、`launchctl list`にcom.nakamura.sfreports1815retryが表示)。ドライラン実行で「本日は16:45分の実績があるためスキップ」という正しい判定を確認済み。

**未検証**: 実際に会社Macが16:45を跨いで閉じていた状況での動作確認はまだ(次回そのような日を待つか、意図的にテストする必要がある)。

**2026-09-09(続き)**: ユーザーから「個人Macでも同様の移動時間対策の保険をかけて欲しい」と依頼があり、[[mac_handoff_relay]]の`personal_mac_inbox.md`にtask-003として投入済み(会社Mac側からは`reports_pipeline_personal/`の内容が直接見えないため)。個人Mac側は既に20分間隔ポーリング式フェイルオーバーのため会社Mac版と同じ「+1.5時間」形は不要と判断し、代わりに(a)0バイト検証ロジックの移植、(b)`failover_state.json`が「代行実行自体の失敗」も「処理済み」と誤記録していないかの確認・修正、の2点を依頼した。

**2026-09-09 個人Mac側で実施完了(task-003)**: (a) `reports_pipeline_personal/download_all_reports.js`に`validateDownload(dest)`を追加(`download.saveAs(dest)`直後)。サイズ0チェック+zip先頭シグネチャ(`PK\x03\x04`/`PK\x05\x06`)チェック、不正なら例外を投げ既存の3回リトライに回収。ライブラリ追加なし、単体テストで動作確認済み。(b) `failover_check.js`に会社Mac版と同種のバグを実際に発見: `execSync`失敗時もcatch外で無条件に`state.last_handled_slot`を保存していた。修正し、保存をtryブロック内(成功時のみ)に移動。失敗時は状態を保存せず次の20分ポーリングで自然に再試行される。実機での本番ダウンロード実行での検証はまだ(次回定時実行/フェイルオーバー発火時)。

## 2026-09-10: 前倒し手動実行と定時実行の同時競合による0KBバグを特定・修正、~/Downloads蓄積の根本原因も解消

ユーザーが「外出前なので定時ダウンロードを前倒しで手動実行して」と依頼。11:13に
`python3 download_all_reports.py`を手動実行したところ、2分後の11:15に定時実行(launchd)
が別プロセスとして起動し、**同じ共有ブラウザ(port 9226)の同じコンテキストに2つの
Playwrightプロセスが同時接続してダウンロードイベントを奪い合い**、後発の定時実行側が
0バイトファイルを14件(18本中)量産する事故になった。既存の`validate_download`(2026-09-09
追加)はリトライはするが、もう一方のプロセスが動き続けている間は奪い合いが解消しない
ため無力だった。パイプラインログの時刻を突き合わせて2プロセス同時実行を確定させた。

**修正1(0KBバグの根治): プロセス排他ロック**。`pipeline.lock`にPIDを書き込み、起動時に
既存ロックのPIDが生きていれば即座に終了する仕組みを追加(`acquire_lock`/`release_lock`)。

**修正2: `--scheduled`フラグ+スロット単位のスキップ判定**。launchd plistの
ProgramArgumentsに`--scheduled`を追加し、このフラグがある時だけ「代表レポート
(REPORTS[0])が直前スロット(11:15枠なら当日0時から、16:45枠なら11:15以降)に既に
ダウンロード済みなら前倒し実行済みとみなしスキップ」する判定(`get_matching_slot`/
`already_done_for_slot`、`SLOT_DEFS`)を追加。`retry_1300_if_missed.py`/
`retry_1815_if_missed.py`も呼び出し時に`--scheduled --slot 11:15`/`16:45`を付与するよう修正。

**修正3: 手動実行時はTeams確認(3分待ち)を省略**。`--scheduled`が無い(=ユーザーが直接
CLIから明示的に依頼した)実行では`ask_before_download`を呼ばないよう`_run_pipeline`の
シグネチャに`ask_confirmation`引数を追加。「明示的に依頼する場合は待ち時間不要」という
ユーザー指示を反映。

## 2026-09-14: 「1件でも成功していればスロット完了」判定の実害が発生・「全件成功」基準に修正

2026-09-11のslot_state.json化(上記)は「どのスロットが完了したか」の混同は解消したが、
**「完了」の定義自体が「1件でも成功していればOK」のままだった**ため、2026-09-14朝の
11:15枠でネット瞬断(`ERR_INTERNET_DISCONNECTED`)を機に18本中13本が「ダウンロード
されたファイルが空です」で全滅(5本のみ成功)したにもかかわらず、`mark_slot_done`が
呼ばれてスロット完了記録され、**13:00補助リトライが「11:15分が実行された形跡あり」
として正当な再試行を誤ってスキップする**実害が発生(ユーザーからの「今日の昼のダウンロード
は全部できていますか」という質問で発覚)。この時点で13本を手動ワンオフスクリプト
(`REPORTS`から失敗13本のIDだけ絞り込み、`BrowserState`/`download_one_report_with_retry`
を再利用)で再取得し18/18成功、0バイト残骸39件を削除して当日分は復旧。

**根治**(`download_all_reports.py`/`retry_1300_if_missed.py`/`retry_1815_if_missed.py`):
1. `mark_slot_done`を呼ぶ条件を`ok_count > 0`から`total > 0 and ng_count == 0`(全件成功)
   に変更。
2. `retry_1300_if_missed.py`/`retry_1815_if_missed.py`が独自に持っていたmtime推測ロジック
   (「代表レポートに今日の日付のファイルがあるか」「16:45以降のmtimeか」)を廃止し、
   `download_all_reports.py`本体の`already_done_for_slot()`(slot_state.json、全件成功のみ
   記録)を直接importして参照する方式に統一。これで判定ロジックが1箇所に集約された。

**副次修正: `finalize_download`の検証失敗パスがdest/ブラウザ側どちらも未削除だった件**。
`validate_download`が0バイト等で例外を出した場合、(a)保存先destに0バイトファイルが
残り続け(今回39件蓄積)、(b)さらに`download.delete()`が呼ばれる前に例外送出されるため
ブラウザの既定ダウンロード先(`~/Downloads`)にも実体ファイルが残り続けていた(今回38件・
6.4MB、いずれも2026-09-14当日分のみ、[[sf_reports_qbr_download_automation]]で既出の
2026-09-10 `~/Downloads`蓄積バグの再発/取りこぼしパス)。`finalize_download`の失敗パスに
(a) dest.unlink()、(b) download.delete()の両方を追加し、以後どちらの経路にも残骸が残らない
ようにした。加えて`cleanup_empty_files()`(全レポートフォルダの0バイトファイルをパイプライン
開始時に自動削除)を新設し、`main()`の`ensure_bigip_connected()`直前に組み込んだ — 過去の
残骸が万一残っていても次回実行時に自動一掃される安全網。

**動作確認中の自己ミス**: `retry_1815_if_missed.py`の新ロジックを確認するつもりで
`python3 retry_1815_if_missed.py`を直接実行したところ、ゲート判定が正しく「16:45枠は
未完了」を返したため、スクリプトがそのまま**実際のフルパイプライン(18本の重複ダウンロード)
を起動してしまった**(13:24:18「パイプライン開始」)。ログ監視で即座に気づき`TaskStop`で
停止、BIG-IP接続確認/Teams確認メッセージ送信/実ダウンロードのいずれにも到達する前に
止められたことをログで確認済み。stale化した`pipeline.lock`も削除。**教訓**: 実行すると
副作用(ブラウザ操作・Teams通知・実ダウンロード)を伴うスクリプトの「ロジックだけ」を
確認したい時は、スクリプト本体を実行せず、対象関数(`already_done_for_slot`等)を
`python3 -c "from module import func; print(func(...))"`のように単体importして呼ぶこと。

**未対応**: 個人Mac側`reports_pipeline_personal/`(Node.js版)には今回の一連の修正
(全件成功判定・0バイト即削除・`~/Downloads`側delete漏れ・`cleanup_empty_files`相当)が
未移植。次回個人Macセッションで確認・移植が必要。

**実地検証待ち**: 次回以降の16:45定時実行/18:15補助リトライで新ロジックが正しく機能するか
(構文チェックと`already_done_for_slot()`の単体呼び出し確認のみ済み)。

**副次発覚・修正: `~/Downloads`への副次コピー蓄積**。上記事故の残骸(0バイトファイル
42件、対象フォルダから削除済み)を調査中、`~/Downloads`直下にもSalesforce自動化由来の
xlsxファイルが72件(約18MB、6月〜9月10日分)蓄積しているのを発見。原因は
**Playwrightの`download.save_as(dest)`は指定先へファイルを複製するだけで、CDP接続の
実ブラウザが既定のダウンロード先(~/Downloads)に保存した元ファイルはそのまま残る**仕様
だったこと(Playwrightが自前で起動したブラウザなら内部一時ディレクトリで完結するが、
`connect_over_cdp`で接続する既存の共有ブラウザではブラウザ自身の既定挙動が使われるため)。
ユーザーは選択肢の中から「根本修正」を選択。`save_as()`成功・検証OK後に
`download.delete()`(Playwrightの、ブラウザ側の元ファイルを削除するAPI。保存先destには
無関係)を呼ぶ`finalize_download()`ヘルパーを新設し、`download_all_reports.py`の2箇所の
save_as呼び出しを置き換え。同じ`save_as`パターンを持つ`download_step1_export.py`
(業況見通し用)・`download_step2_enter_code.py`(旧メールコード方式、現在は参考保存のみ)
にも同様に`download.delete()`を追加し、会社Mac側の全ダウンロードスクリプトで解消済み。

**未対応**: 個人Mac側`reports_pipeline_personal/`(Node.js版)には上記の3修正+
`download.delete()`相当の対策が未移植。`personal_mac_inbox.md`にtask-004として
詳細instruction込みで投入済み(pending)。個人Mac側の共有ブラウザ(port 9227)も同じ
CDP接続方式のため、同じ`~/Downloads`蓄積が起きている可能性が高い。

**未検証**: 次回16:45の定時実行でスキップ判定・確認省略ロジックの実地検証が必要
(構文チェックのみ済み)。

## 未検証・今後の注意点
- ウィンドウのフォーカス奪取対策は実装・DL成功は確認したが、「実際にユーザーの作業が中断されなくなったか」はユーザー自身の体感確認待ち。会社Mac版Python(`download_all_reports.py`)には元々`reposition_offscreen`/`get_frontmost_app`/`restore_frontmost_app`が入っているため、個人Mac版固有の修正だった。
- 並列化は個人Mac版(`reports_pipeline_personal/download_all_reports.js`)のみに適用。会社Mac版Python(`reports_pipeline/download_all_reports.py`)は今回変更していない(逐次実行のまま)。同様の要望が出た場合は会社Mac側にも同じ設計(1本目逐次→残り並列度3)を移植すること。
- **launchd経由での初回本番実行はまだ観測していない**(2026-08-26の稼働開始日当日の16:45枠が最初の実ジョブ実行になる想定)。`pipeline_log.txt`とTeams通知で結果を確認すること。
- **Macがスリープ/シャットダウン中だった場合、`StartCalendarInterval`は取りこぼしを自動リトライしない**(CASパイプラインのような20分おきポーリング式ではなく固定時刻式のため)。オフィスでMacを開いたままにしておく前提。取りこぼしが頻発するようなら[[cas_csv_download_automation]]と同様のポーリング+状態ファイル方式への切り替えを検討。
- 本人確認コードが複数レポートで同時に必要になった場合(即時ダウンロードできる「デバイス信頼」の持続時間が短い場合)、1回の実行で複数回コード待ち(最大150秒×回数)が発生し得る — 実行時間が伸びる可能性はあるが、フロー自体は各レポートで独立して自己完結しているため問題なく動くはず。
- 過去(2026年4月〜8月)に手動でダウンロードして`Salesforce書き出し/`直下に置かれていたファイル35件は、2026-08-26に全てサブフォルダへ移動済み(ユーザーからの依頼で実施)。判別方法: Salesforceの`suggested_filename`は日本語部分がスペースに置換され英数字部分だけ残る仕様(例:「（QBR集計用）月別_貢献利益（仕掛）_v2.1」→`QBR      _        _v2.1-...xlsx`)なので、ファイル名中の`_v2.1`/`_v2.2`/`_v2.3`/`APAC Pitch`/`SF`(接頭辞)で機械的に判別・振り分け可能だった。未分類0件。移動先: v2.1→11件、v2.2→6件、v2.3→13件、SF案件リスト→8件(元々7件+本日分1件)、APAC Pitch→2件(元1件+本日分1件)。「月別見込」2レポートは過去の手動DL実績が無かった(新規追加分)。

## 2026-09-11: 16:45枠が恒久的に誤スキップされるバグを発見・修正

ユーザーから「夕方の定時ダウンロードがキャンセルされた、11:30頃と13:00頃の実行が原因では」と報告。ログ調査で2026-09-10導入の`already_done_for_slot`(スロットスキップ判定)に設計ミスを発見: `SLOT_DEFS`が`(16, 45): (11, 15)`(=16:45枠は「11:15以降にファイルがあれば実行済み」とみなす)となっていたため、**16:45枠自身の判定が、無関係な11:15枠(当日朝の正常実行)や13:00補助リトライの成功ファイルまで「16:45枠は完了済み」の証拠として拾ってしまう**構造的バグだった。11:15枠が毎日正常終了する限りほぼ必ず16:45枠を誤スキップする(タイミングが±10分の許容誤差窓に入った時だけ発現)。2026-09-10当日は16:45launchd起動が16:59と遅れ許容誤差外だったため偶然発現せず、2026-09-11は11:15枠の1本(月別見込・設定売総無印)が失敗→13:00補助リトライがフル再実行→その成功ファイルが16:45枠の判定を誤って満たし、16:45定時実行が実際にスキップされた(ログ: `[2026-09-11T16:45:07] 定時実行スキップ`)。さらに18:15補助リトライも同じ`already_done_for_slot(16:45)`を通るため、放置すれば18:15リトライも同じ理由で無力化するところだった。

**根治(`download_all_reports.py`)**: mtime時間窓からの推測をやめ、`slot_state.json`(`{"date": "...", "completed": ["11:15", "16:45"]}`)にスロット単位の完了を明示記録する方式に変更。`already_done_for_slot(slot_key)`はこのJSONの`completed`リストを見るだけになり、`mark_slot_done(slot_key)`を`main()`末尾(`--scheduled`実行が1件以上成功した場合のみ)で呼ぶ。これにより「どのスロットが実際に完了したか」が構造的に一意になり、他スロットの成功ファイルとの混同が起きなくなった。`SLOT_DEFS`は`(11, 15), (16, 45)`という単純なタプルに簡素化(時間窓定義が不要になったため)。

**その場の対応**: 手動フル実行(`--scheduled`なし、確認省略)で本日分の夕方データを取得、18/18成功(17:00:25完了)。18:15補助リトライは`downloaded_since_1645`(REPORTS[0]の最新ファイルmtimeが16:45以降か)で判定するため、この手動実行の成果物により自然にスキップされる想定(state.json経由の連携は不要)。

**未対応**: 個人Mac側`reports_pipeline_personal/`に同種のスロットスキップ判定が移植されているかは今回未確認(既存メモリに記載なし=おそらく未実装)。[[mac_handoff_relay]]の`personal_mac_inbox.md`にtask-006として詳細instruction込みで投入済み(pending)。

**2026-09-11 個人Mac側点検完了(task-006、対象外と判断)**: `download_all_reports.js`自体にはスロット完了判定ロジックが無い(grep該当なし)。判定は`failover_check.js`のみに存在し、(1)`latestExpectedSlot()`が返すその回の`slot`自身を閾値に使う設計(会社Mac版`SLOT_DEFS`のような「別スロットの時刻を借りる」マッピングが無い)、(2)`slotKey()`がラベルでなくスロット瞬間のフルISOタイムスタンプで日替わり混同の余地が無い、の2点により同種バグの構造的リスクなしと確認。コード変更なし。

**実地検証待ち**: 次回以降の16:45定時実行/18:15補助リトライで新ロジックが正しく機能するか(構文チェックのみ済み)。

## 2026-09-11: パイプライン完了後にCOMBINED.xlsx自動更新を連鎖実行(フェーズ2)

[[qbr_combined_xlsx_rebuild_20260911]]の一部。「（設定突合用）SF案件リスト」を既にこのパイプラインが毎回DLしていることを利用し、`download_all_reports.py`の`main()`末尾(ダウンロード成功/失敗を問わず、`restore_frontmost_app`の後)に`run_combined_rebuild_sync()`を追加。Excel(`Prep_SalesforceAllRecord.xlsx`/`COMBINED.xlsx`等)が開いていないことを`osascript`で確認した上で、`~/CASExport/sync_sf_record_list.py`(SF案件リスト最新ファイル→`Prep_SalesforceAllRecord.xlsx`同期)→`~/CASExport/rebuild_cas_combined_actual.py`(`GBC CAS実績+見込_COMBINED.xlsx`全量再構築)をsubprocessで順次実行。Excel使用中はスキップしTeams通知。単体テストのみ済み、実際のlaunchd定時実行での動作は次回以降に確認要。個人Mac側フェイルオーバー(`reports_pipeline_personal/`)には移植していない(対象ファイルが全てd14461ローカルのため)。

## 2026-09-29: 共有相手のダウンロード不可報告 → ファイルは正常、原因は相手側クラウド同期と診断

ユーザーから「バックアップを共有している別の人がダウンロードできないと言われた」との相談(対象:（パイプライン報告用）月別_貢献利益（仕掛）_v1.0フォルダの`...-2026-09-28-16-47-12.xlsx`、相手のスクリーンショットはWindowsのクラウドファイルエラー`0x80070185`「クラウド操作が失敗しました」)。調査手順: (1)`pipeline_log.txt`/Teams通知ログで該当ファイルが同日16:47に正常生成された成功実行の一部と確認、(2)実ファイルのサイズ(5,725B)とzip妥当性(`zipfile.is_zipfile`)を検証し破損なしと確定。結論: ソース側は正常、原因は相手端末のローカルクラウド同期(OneDrive/Dropboxが共有するWindows Cloud Files APIの汎用エラー、ファイル内容とは無関係)。

**副次的な気づき**: `Salesforce書き出し/`フォルダ全体が過去分を意図的に削除しない設計のため、2026-08-26の運用開始以来**599ファイル・117MBまで蓄積**(確認時点)。この蓄積が、相手側が一括ダウンロードする際の汎用クラウドエラーの誘因になっている可能性がある(スクリーンショットでは丸ごとフォルダの一括ダウンロードキューが表示されていた)。今後同種の「共有相手がダウンロードできない」報告があれば、まず自動パイプライン側のログでファイル自体の正常性を確認し、次にこのフォルダ肥大化を疑うとよい。恒久対策(古いスナップショットの定期整理等)は今回未実施・ユーザーからの依頼も無し。

## 2026-09-16: COMBINED.xlsx自動更新が毎回`ModuleNotFoundError: No module named 'openpyxl'`で失敗するバグを発見・修正

ユーザーから「ダウンロードが止まっている感じがする」と確認依頼。実際にはパイプライン自体は正常完了していた(16:45枠は18本中17成功、「月別見込（設定売総 X 部署）」1本のみdownloadイベントタイムアウトで3回リトライ全滅)が、調査の副産物として上記(2026-09-11追加)の`run_combined_rebuild_sync()`が呼ぶ`sync_sf_record_list.py`が11:23枠・17:02枠とも`ModuleNotFoundError: No module named 'openpyxl'`で失敗し続けていたことを発見。

**根本原因**: `run_combined_rebuild_sync()`内の`subprocess.run(["python3", str(script)], ...)`がインタプリタをバイナリ名`"python3"`のみで指定していた。plist本体は`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`(openpyxl等インストール済み)をフルパスで起動しているが、launchdが渡す最小限のPATH(`/usr/bin`優先)の下ではこの`subprocess.run`呼び出しがApple標準の`/usr/bin/python3`(3.9.6、openpyxl未インストール)に解決されてしまっていた。対話シェルで`python3`を叩くと正しい方(openpyxlあり)に解決されるため、この不一致は普段の手動確認では再現せず、launchd経由の定時実行でのみ発現していた。

**修正**: `["python3", str(script)]` → `[sys.executable, str(script)]`に変更(`sys`は既存import済み、追加インポート不要)。今動いている自分自身のインタプリタの絶対パスを使うことで、PATH解決に依存しなくなった。修正後、当該インタプリタで`sync_sf_record_list.py`を手動実行し正常終了(COMBINED.xlsx同期成功)を確認済み。次回定時実行(11:15/16:45)で自動的に反映される想定、実地検証はまだ。

**失敗していた1本の応急対応**: `BrowserState`/`download_one_report_with_retry`を直接importするワンオフスクリプトで「月別見込（設定売総 X 部署）」(id `00O7F00000Ay7SrUAJ`)単体を手動再ダウンロードし成功(2026-09-16 17:58、zip検証OK)。

**教訓**: launchd/cron等の非対話実行からsubprocessで別のPythonスクリプトを呼ぶ際は`"python3"`のような裸のコマンド名ではなく`sys.executable`(自分自身のインタプリタの絶対パス)を使うこと。対話シェルでの動作確認だけでは、PATH解決の違いによるこの種の不具合は再現しない。個人Mac側`reports_pipeline_personal/`にはこの`run_combined_rebuild_sync()`相当の機能自体が無い(対象ファイルが全てd14461ローカルのため、[[qbr_combined_xlsx_rebuild_20260911]]参照)ので移植対象なし。

## 2026-09-30: ~/Downloadsに59件・約8.9MB蓄積を発見、真因は「download.save_as()が空コピーを作る」かつ「download.delete()がその実ファイルを消せない」の合わせ技と判明・修正

ユーザーから「~/Downloadsにダウンロードファイルが溜まっている」との相談。2026-09-14に「解消済み」と記録していた~/Downloads蓄積バグ([[qbr_combined_xlsx_rebuild_20260911]]の前段、上記2026-09-14セクション参照)が、実は**異常系(検証失敗)のケースで再発していた**ことが判明。

**発端**: 本日11:15の定時実行が`pipeline_log.txt`上は「成功0件/失敗18件」の全滅、18本全てが「ダウンロードされたファイルが空です」で3回ずつリトライ後に諦めていた(11:15〜11:41)。5分後の自動リカバリも間に合わず、最終的に13:41の2回目リカバリで18/18成功。

**調査で判明した真因**: 11:15枠の「失敗」時に~/Downloadsへ残っていた実ファイル(例: `QBR      _        _v2.1-2026-09-30-11-24-01.xlsx`、103,354バイト)を検証したところ、**zipファイルとして完全に正常**で、かつ13:41に最終的に正規フォルダへ保存された成功ファイルと**バイトサイズが完全一致**していた。つまり:
1. ブラウザ(共有ボットブラウザ)自身はこの時点で既に正常にダウンロードを完了させていた。
2. しかし`finalize_download()`内の`download.save_as(dest)`が、ブラウザの書き込み完了を待たずに**0バイトの不完全なコピーをdestへ作ってしまう**タイミング問題を起こしていた(`connect_over_cdp`で接続した既存Chromeとの組み合わせ特有とみられる — 2026-09-09に「Chromeがダウンロードを内部的にキャンセル」と推定していたのは誤りで、実際はキャンセルされておらず単にsave_as()のコピーが不完全だっただけだった)。
3. `validate_download(dest)`がこの0バイトを検知して例外を出し、パイプラインは「本当に失敗した」と誤判定→18本×最大3回の無駄なリトライ→全滅扱いという連鎖を起こしていた。
4. さらに、この失敗パスで呼んでいた`download.delete()`(2026-09-14追加分)は例外を出さないものの、**ブラウザ側の実ファイル(~/Downloadsの完全なコピー)を実際には削除できていなかった**(CDP接続の既存Chromeでは、ダウンロード履歴上の記録を消すだけで実ファイルには効かないケースがあると推定)。これが「NGログなのに~/Downloadsに正常なファイルが溜まる」の直接原因。

**根治(`download_all_reports.py`)**: `finalize_download()`を修正し、
1. `DEFAULT_DOWNLOAD_DIR`(`~/Downloads`)に`download.suggested_filename`と同名のファイルがあるかをフォールバックとして確認する処理を追加。`validate_download(dest)`が失敗した場合、まずこのフォールバックを検証し、**有効ならそれを正解としてdestへ`shutil.copy2()`で複製・救済**してから成功扱いで返す(無駄なリトライ・全滅を防ぐ)。
2. 救済の成否によらず`_cleanup_browser_original()`という共通ヘルパーを新設し、`download.delete()`を呼んだ**後に必ず`fallback.unlink()`で~/Downloads上の実ファイルも直接削除**するようにした(delete()単体が効かない場合への保険)。
3. 単体テスト(モックの`FakeDownload`でsave_as()の空コピー再現+本物の失敗ケースの両方)で、救済ロジックとクリーンアップの両方が意図通り動くことを実ブラウザなしで確認済み([[feedback_verify_gating_logic_without_running_full_script]]の方式)。

**実施した後始末**: ~/Downloadsに溜まっていた59件(約8.9MB、2026-09-16〜2026-09-30分)を、全件zipとして有効かつ正規保存先フォルダに同等の正常ファイルが既に存在することを確認した上でユーザー承認を得て削除済み。

**未検証**: 修正後のコードは構文チェック・単体テストのみ済みで、実ブラウザでの本番実行(次回11:15/16:45枠)での動作確認はまだ。個人Mac側`reports_pipeline_personal/download_all_reports.js`(Node.js版)には同種の救済ロジック・二重クリーンアップは未移植 — 同じ`connect_over_cdp`方式のため同じ問題が起きうる、次回個人Macセッションで移植要否を確認すること。`download_step1_export.py`/`download_step2_enter_code.py`(業況見通し用、手動トリガーのみ)にも同じ`download.delete()`依存の弱点があるが、今回は自動パイプライン側のみ修正(手動トリガーで発生頻度が低いため優先度を下げた、必要なら同様の修正を移植可能)。

## 2026-10-05: 朝枠を11:15→9:00に変更(ユーザー依頼「朝と夕方のバックアップに、朝は9時」)
- 会社Mac: `download_all_reports.py`の`SLOT_DEFS=(9,0),(16,45)`、`retry_1300_if_missed.py`の`SLOT_KEY=(9,0)`/`--slot 09:00`、`com.nakamura.sfreportspipeline.plist`の11:15→9:00(平日5エントリ)。unload/load済み。バックアップ`*.bak_20261005`。
- 13:00(朝枠の補助リトライ)・16:45・18:15は据え置き。PowerBI更新(11:30/17:00)は変更なし。
- 個人Macフェイルオーバー(`failover_check.js`)の朝スロット変更はrelay task-014で依頼(pending)。
- Gmailカレンダー: 予定はICSインポート方式で、Claude側から直接編集不可(会社Macの共有ブラウザはdentsu-work-botでGmail未ログイン)。改訂ICS `Claude作業フォルダ/自動化タスクスケジュール/salesforce_reports_schedule_add_20261005.ics`(同UID・SEQUENCE:1、朝9:00〜9:15)を作成、ユーザーに手動反映を依頼。
- **同日追記**: 朝枠の補助リトライを13:00→**9:30**に変更(ユーザー依頼)。Label/ファイル名は`com.nakamura.sfreports1300retry`/`retry_1300_if_missed.py`のまま(名前は旧時刻、中身は9:30)。9:00実行がまだ走っていればpipeline.lockで9:30側は起動しない。Gmailカレンダーはユーザー自身で変更済み。
- 現行スケジュール: 平日 9:00本番 → 9:30補助 / 16:45本番 → 18:15補助。
- **2026-10-05 手動実行結果**: 17/18成功。「月別見込（設定売総 X 部署）」のみ1本目でAuthenticator承認が3回とも5分タイムアウト→NG。
- **2026-10-05 ユーザー要望**: 「Macが開いていないときも自動実行したい、作業状況に左右されるのはサステナブルでない」。本質的な依存はMacだけでなく毎回のAuthenticator承認(人の操作)。候補: (A)Salesforceレポート登録(購読)+添付→Outlook→Power Automateクラウドで保存、(B)SF管理者に接続アプリ(OAuth)申請→APIで無人取得。ユーザーの方針判断待ち。
- **2026-10-05 失敗分の自動再実行を追加**(ユーザー依頼「今後も取れなかったものがあれば再実行するように」): `main()`で一部失敗(ok>0かつng>0)時、5分待って失敗レポートのみ再実行(`PARTIAL_RETRY_COUNT=2`/`PARTIAL_RETRY_DELAY_S=300`)。`_run_pipeline`は`reports`/`tag`引数と失敗リストを返すよう変更。最終的に全件揃えばslot完了記録。モックテストで動作確認済み、実地は次回定時実行で。バックアップ`download_all_reports.py.bak_20261005_01`。個人Mac版(Node.js)には未移植。
- 同日10:33 単発再実行で「月別見込（設定売総 X 部署）」取得成功→本日分18/18揃った。
- **2026-10-05 Mac非依存化の検討続き**: ユーザー回答「レポート登録(購読)は本数上限で全18本は不可」→案A却下。ユーザー提案「既存のSalesforce↔PowerBI接続を利用できないか」。PowerBI GBCダッシュボードはSalesforceオブジェクトコネクタ(`Salesforce.Data`、GBC__c直結)でService上スケジュール更新済み([[powerbi_gbc_dashboard_current_state]])。提案: Power Automateクラウドフロー(定期)→Power BIコネクタ「データセットに対してクエリを実行」(DAX EVALUATE)→CSV化→OneDrive/SharePoint保存。注意: 出力はレポート形式xlsxではなくGBC__c生データ(PBI整形後)、鮮度はPBI更新時刻依存、PAクエリ上限(10万行/100万値/15MB)。Salesforce Reportsコネクタは2000行制限があるので18本のレポート再現には不向き。ユーザーに「用途=データ状態の記録か/レポート形式ファイル自体が必要か」を確認中。
- **2026-10-05 用途判明**: 共有相手(PC操作に不慣れ)がこのレポート形式xlsxを見ながら自分で別レポートを作っている→**レポート形式の維持が必要**。PowerBI生データCSV全面置換は不可。次の提案: 相手が実際に使うレポートを特定→その数本だけ登録(購読)+添付→PA保存で同形式をクラウド化、残りはPowerBI経由データ記録+Macパイプライン補助、恒久策は接続アプリ申請。使用レポートの特定をユーザーに依頼中。
- **2026-10-05 確定事項**: Salesforceのレポート登録上限は**1人7件**。共有相手は**18本すべて**使用。→登録方式は1人では不可(3人で分担なら理論上可、1日1回)。推奨: Power BIの時と同じSalesforce管理者チームに接続アプリ(OAuth/API)を申請(前例: [[powerbi_migration_gbc_dashboard]] 2026-07-15のOAUTH_APPROVAL_ERROR対応)。実行場所(PA Premium HTTP or 常時稼働機)は承認後に決める。ユーザーの方針回答待ち。

**2026-10-05 スケジュール変更**: 会社Macの定時実行を平日11:15/16:45 → **9:00/16:45** に変更(会社Mac側で対応済み)。個人Macの `failover_check.js` の SLOT_TIMES も [9,0]/[16,45] に合わせた(relay task-014、バックアップ `failover_check_bak_20261005.js`)。このメモ内の「11:15」は古い記述。**修正済み(2026-10-05 16:20、ユーザー承認後)**: launchd経由だと `failover_check.js` の execSync で `node` がPATHに無く(`/bin/sh: node: command not found`)、代行実行が毎回即失敗する。execSync を `process.execPath`(/usr/local/bin/node)に変えて修正した。launchdと同じPATHで、旧コードは失敗・新コードは成功することを再現確認済み。

## 2026-10-09: 個人Macフェイルオーバーで1本だけ失敗した場合の扱い
- フェイルオーバーは代表レポート(REPORTS[0]=月別見込（設定売総 X 部署）)のmtimeだけで完了判定するため、代表以外の1本が失敗しても次回ポーリングで「処理済み」となり**自動再試行されない**。その場合は `cd ~/SalesforceExport/reports_pipeline_personal && NODE_PATH=~/.local/share/claude-playwright/node_modules /usr/local/bin/node download_all_reports.js <レポートID>` で単体再取得できる(手動実行扱いでTeams事前確認なし、約20秒)。10/9にSF案件リスト(00OfP00000ARvMIUA1)をこれで回収済み。
- Salesforce書き出し各フォルダに並ぶ0バイトxlsxは、会社Mac側のダウンロード分が個人MacではDropboxオンライン専用(com.dropbox.placeholder)になっているだけ。破損と誤認しないこと。
- 10/9は会社Macの定時ファイルが2枠とも無かった(会社Mac停止の可能性)。

## 2026-10-09(続き): 個人Macフェイルオーバーを「全本そろうまで補完」方式に改修(ユーザー依頼)
背景: 10/9は会社休業日で会社Mac未起動→個人Mac代行で17/18、SF案件リストだけ欠けたが自動再試行されなかった。
- `failover_check.js`: 完了判定を代表1本のmtime→**全18本それぞれ**「スロット時刻以降の有効xlsxがあるか」に変更(`missingReports()`)。0バイトでも`com.dropbox.placeholder`付き(会社Mac保存分のオンライン専用)は有効扱い。
  - 全本欠け→従来どおり`--from-failover`でフル実行(Teams事前確認あり)
  - 一部欠け→`--retry-missing <欠けたID…>`で欠けた分だけ実行(事前確認なし)
  - 実行後はexit codeでなくファイル有無で再判定し、全部そろったら処理済み
  - 同一スロットの試行上限 `MAX_ATTEMPTS_PER_SLOT = 9`(20分間隔×9≒3時間)。超えたら欠けたレポート名をTeams通知(1回のみ)して次スロットまで停止。状態は`failover_state.json`の`attempt_slot`/`attempt_count`。
  - 会社Macが一部しか取れなかった場合も、猶予30分後に個人Macが欠けた分を補完する。
- `download_all_reports.js`: `--retry-missing`フラグ追加、検証NG(0バイト/非zip)ファイルは削除するよう変更(完了判定の誤認防止)。
- バックアップ: `failover_check_bak_20261009.js` / `download_all_reports_bak_20261009.js`。
- 検証: 判定関数の単体テスト(完了/プレースホルダ/一部欠け/全欠け)OK、本番`run_failover_check.sh`1回実行で「全18本そろっています」判定OK。実際の補完ダウンロード発火は次回欠けが起きた時に初確認。
- 会社Mac版(Python)は同種の弱点が残っている可能性あり(未確認)。

## 2026-10-12: 個人Mac版のSalesforce用ブラウザを dentsu.co.jp 専用に分離(ユーザー指示)
- ユーザー指示: 共有ブラウザ(9227/timetree-bot)はGmail系ログインなので、Salesforceバックアップは dentsu.co.jp 用ブラウザで行うこと。
- `download_all_reports.js`: `PORT=9231`、`PROFILE_DIR=~/.chrome-profiles/dentsu-work-bot`(2026-09-06にChromeの「d.co.jp」プロファイルから複製したもの)。未起動なら `open -g -na` + `--window-position=-2500,-2500` で自動起動。ポート9228はpowerautomate-bot/aicon-botが使用済みのため9231を採用。
- ダウンロード前のTeams自分宛て確認(`--from-failover`時のみ)は、Teamsログイン済みの共有ブラウザ(`TEAMS_PORT=9227`)に別接続して実施。
- バックアップ: `download_all_reports_bak_20261012.js`。
- 10/12 9:30の代行(旧設定9227)は0/18「iframeが見つかりません」。dentsu-work-botもMyApps(myapps.dentsu.com)のSSOが切れており、パスワード入力が必要だった(ユーザーにログイン依頼)。
- ユーザーがログイン後、単体テスト成功(初回のみAuthenticator push承認あり)。続けて10/12 9:00枠を新しい補完方式で実行: 1回目16/17(v2.3のみ失敗)→2回目で欠けた1本だけ取得し「全18本そろいました」→処理済み。**欠けた分だけ補完する動作を実機で確認済み**(10/9改修分の初検証)。
- dentsu-work-botのMyAppsセッションが切れたら、同じくiframe未検出で全滅する。その時はウィンドウを画面に出してユーザーにパスワードログインを依頼し、終わったら画面外(-2500,-2500)へ戻す。

## 2026-10-14: 会議遅延判定のタイムゾーンバグ修正
`calendar_events.json`の`start`/`end`はUTC(`timeZone:'UTC'`)なのに、`find_current_teams_meeting_end()`がそのままローカル時刻として比較していたため、夜の「大船会」(17:00-20:30 JST=08:00-11:30 UTC)を朝9:00枠で会議中と誤判定し、11:30まで遅延させた。`_event_time_local()`を追加し、`startWithTimeZone`(なければ`start`をUTC扱い)を`astimezone()`でローカルに変換して比較するよう修正。9:00→なし、17:30→20:30終了と判定されることを検証済み。バックアップ: `download_all_reports.py.bak_20261014`。当日は待機プロセスをkillして手動実行(引数なし=会議待機なし)、18/18成功。**カレンダーJSONの時刻を使う他の自動化も同じUTC扱いに注意。**

## 2026-10-14: 手動実行後に9:30補助リトライが二重実行した件
9:00定時を(会議誤判定のため)killして`--scheduled`なしで手動実行→全件成功でも`slot_state.json`に09:00が記録されず、9:30リトライがフル再実行。`main()`末尾を修正し、手動実行でも全件成功なら`--slot`指定または直近経過スロット(SLOT_DEFS中で現在時刻以前の最後)を完了記録するようにした。**今後、定時枠の代わりに手動実行する場合もこれで補助リトライは自動スキップされる。**

## 2026-10-15: 個人Macフェイルオーバーを遠隔で止める手段がない
- 9:00枠がネット切断で15/18→部分再実行で10:56に18/18。その間、個人Mac(自宅、操作不可)が欠けた分の補完を繰り返し、ユーザーが「止めたい」と依頼。
- 会社Macからは`reports_pipeline_personal/`が見えず、停止フラグも無い。止める唯一の方法は会社Mac側で全18本をそろえること(個人Macは次回ポーリングで「全そろい」判定して停止)。
- 改善案はユーザー承認済み(10/15)→ relay task-015で個人Macへ依頼(pending)。フラグは `.claude-sync/claude_relay/personal_failover_pause`(until=YYYY-MM-DDTHH:MM で期限付き可)。会社Macから止めたい時は `touch` で作る。
- 部分再実行の`time.sleep(300)`中にMacがスリープすると、その分だけ再実行が遅れる(今回 9:57予定→10:49)。
- 2026-10-17: failover_check.js に遠隔停止フラグ追加(task-015)。`.claude-sync/claude_relay/personal_failover_pause` があればスキップ、`until=YYYY-MM-DDTHH:MM`で期限付き。

## 2026-10-20 朝の全滅と手動回収
会社Mac停止中→個人Macフェイルオーバー4回0/18(共有ブラウザ9231不在でbrowser closed/saveAs ENOENT)。手動実行は `NODE_PATH=~/.local/share/claude-playwright/node_modules node download_all_reports.js [ID]`(NODE_PATH無しだとplaywright not found)で18/18回収。0バイトファイルをfailoverが取得済み扱いする穴あり(要修正・未対応)。
2026-10-20修正(個人Mac版のみ): 保存は一時名.partに書いて検証OK時だけrename(0バイト本番ファイルを残さない)。ファイル名は`<レポート名>-<SF日時>.xlsx`に変更(従来は日本語が空白化)。会社Mac版download_all_reports.pyは旧仕様のまま。

## 2026-10-20: 会社Mac版も .part 保存+ファイル名統一(relay task-019)
- `finalize_download`: `.<名前>.part`に保存→検証→`os.replace`。`build_dest()`で`<report["folder"]>-<SF日時>.xlsx`。バックアップ`download_all_reports.py.bak_20261020`。単体テスト(SF案件リスト)成功。
- 下流は全てmtimeで最新選択のためファイル名変更の影響なし(sync_sf_record_list.py / HDY collectors.py / retry系はslot_state.json)。
- 当日朝: 会社Macのネット断で9:00枠失敗→手動実行が個人Macフェイルオーバーと同時実行になり空ファイルNG多発。**両Mac同時実行は避ける**(片方を止める)。最終的に個人Macで18本揃った。

## 2026-10-27 会議待機の仕様変更(会社Mac)
会議中は強制開始せず空くまで待つ(21時打切り)+5分以内に次会議が始まる隙間では開始しない。ユーザー方針: 個人Macフェイルオーバーは残すが、離席で機能しにくいので失敗時はTeams通知のみ。会議判定(tentative含む)は正しいとユーザー確認済み。カレンダーexportが10/11で停止中(要復旧)。
