# SF QBRレポート自動ダウンロードパイプライン構築

## 2026-08-26T16:20:00+09:00
Status: done
What: GBC QBR用Salesforceレポート7本(月別見込×2、貢献利益v2.1/2.2/2.3、SF案件リスト、APAC Pitch)を1日2回(平日11:15/16:45、PowerBI更新の15分前)自動ダウンロードするlaunchdパイプラインを構築。既存の`~/SalesforceExport/`(単一レポート用Playwrightスクリプト)を土台に、7本ループ+レポート別サブフォルダ保存+本人確認コード自動処理へ汎用化。実機テストで7件全て成功(1本目のみ確認コード要、以降は即時DL)。トークン消費ゼロで無人稼働する設計(Claudeは今回の構築のみ)。詳細は per-project memory `sf_reports_qbr_download_automation.md`。
Next: launchd経由での本番初回実行(本日16:45枠)の結果を`pipeline_log.txt`とTeams通知で確認。

## 2026-08-26T16:20:30+09:00
Status: done
What: ユーザー依頼で、過去(2026年4〜8月)にルート直下に散らばっていた手動DL済みSalesforceファイル35件を、ファイル名パターン(`_v2.1`/`_v2.2`/`_v2.3`/`APAC Pitch`/`SF`接頭辞)で機械判別し、対応するレポート別サブフォルダへ全件移動(未分類0件)。
Next: —

## 2026-08-26T16:47:00+09:00
Status: done
What: ユーザーからGmailカレンダー(maxakisan@gmail.com)の更新スケジュール予定も反映してほしいとの依頼。既存の「[自動実行] GBCダッシュボード(PowerBI)スケジュール更新」予定(11:30/17:00、15分間、平日繰り返し)と同じ形式で、新規に「Salesforceレポート自動ダウンロード」予定(11:15/16:45)を追加するicsファイルを作成し送付。以前作ったicsがスクラッチパッド(セッション終了で消える一時ディレクトリ)にしかなく残っていなかったことが判明したため、[[automation_schedule_overview]]の運用ルールを改訂: 今後は`Claude作業フォルダ/自動化タスクスケジュール/`に実ファイルとして保存する方式に変更。
Next: ユーザーがGoogleカレンダーの「インポート/エクスポート」機能で実際にインポートし、意図通り2件追加されるか確認待ち。セッションはここで終了。

## 2026-09-02T09:35:00+09:00
Status: done
What: ユーザーから、会議中の画面共有中にSalesforceダウンロードの表示が邪魔になるとの指摘。`~/SalesforceExport/reports_pipeline/download_all_reports.py`の`reposition_offscreen`関数を、従来の画面外(-3000,-3000)退避からCDPの`windowState: minimized`による実際のウィンドウ最小化に変更(失敗時のみ画面外退避にフォールバック)。共有ブラウザ(port 9226)に接続して実機で最小化動作を確認済み(normal→minimized)。
Next: 次回の定期実行(平日11:15/16:45)で実際の挙動を確認。

## 2026-09-02T09:50:00+09:00
Status: done
What: ユーザーから「Salesforce以外でも、操作が不要な作業は常に最小化して実行するように」との標準ルール指定。同じ共有ブラウザ(port 9226)を使う他の無人自動化を洗い出し、`~/CASExport/cas_download.py`(従来ページ表示後5秒待ってから画面外退避していたのを、new_page直後に最小化するよう修正)と、常駐デーモン`~/TeamsExport/teams_daemon.py`(従来ウィンドウ非表示処理が一切無く、常時起動なので最も影響が大きい箇所だったと判断、ログイン確認後に最小化する処理を追加)、`~/TeamsExport/scripts/weekly_ai_digest.py`(既存の画面外退避をminimized優先に格上げ)を修正。全てpy_compileで構文確認済み。標準ルールとして per-project memory `feedback_browser_automation_standing_practices.md`(ルール1に統合)と`shared_bot_browser.md`に記録。ChatGPT/Gemini bot、Google Maps、TimeTree、JCIピッチリスト、GBC Smart-KINMU、SF週報用スクリプト、teams_cliは今回は未着手(次に触る/使うタイミングで同様に適用する方針を記録)。
Next: —

## 2026-09-04T15:00:00+09:00
Status: done
What: ユーザーから「自動ダウンロードが失敗している、認証がスマホ通知になっていないのでは」との報告。調査したところ実際には2つの別問題が重なっていた。(1) `download_all_reports.py`のバグ: 2026-09-02のAuthenticator切替対応は「エクスポートを押した後に別タブで検証画面が開く」パターンのみ想定しており、「レポートを開いた瞬間に同じページがそのまま検証画面(`UnifiedPasskeyVerificationUi`等)にリダイレクトされる」パターンを未対応で、存在しないレポートビルダーiframeを探し続けてタイムアウトしていた(9/4 11:15枠は8本全滅)。さらに「別の検証方法を使用してください」リンクのhref形式が検証画面のバリエーションにより`javascript:srcUp(...)`(TempCodeVerificationUi)と通常の相対パス(UnifiedPasskeyVerificationUi)の2種類あり、後者は未対応だった。両方修正し`approve_verification_and_download()`ヘルパーに統合。(2) 運用面: iPhoneのSalesforce Authenticator通知がサイレント配信になっており承認に気づけず、5分タイムアウトが発生していた(ユーザーに通知設定の見直しを依頼)。加えてユーザーから「QRコード画面をちゃんと閉じずに進めているのでは」との指摘があり実機調査した結果、検証画面ロード時にネイティブのパスキー(WebAuthn)UIが自動的に呼ばれ`#overlay`(backdrop-filter:blur、pointer-events:auto)が常時表示されることを確認したが、スクリプトはこのページ上で一切クリックせずhref属性を直接読んで`goto()`しているため実害はなかった(次の検証方法選択ページにはoverlayが存在せず、`elementFromPoint`で実際に正しい要素がクリック対象になることも確認済み)。念のためユーザー要望で`select_salesforce_authenticator()`冒頭にEscapeキー送信を追加。修正後、14:41の手動実行で8/8成功(所要2分弱、通知も正常着信)。
Next: 次回定時実行(16:45枠以降)で無人稼働時も安定するか継続観察。iPhone側の通知設定変更(サイレント→即時)をユーザーが実施したかは未確認。

## 2026-09-08T06:00:00+09:00〜06:27:00+09:00
Status: done
What: 会社Mac側に2026-09-07に追加された「レポート9本」と「ダウンロード前Teams確認機能」を、個人Macフォールバックパイプライン(`~/SalesforceExport/reports_pipeline_personal/`)に移植。
1. `reports_config.js`にレポート9本を追加し計18本に(会社Mac側と完全一致)。
2. `download_all_reports.js`に`askBeforeDownload()`(Teams自分宛てチャットへの事前アナウンス→3分待機→自動開始)をNode.js移植。`teams_cli/lib.js`のセレクタを流用。
3. 個人Mac共有ブラウザ(port 9227)のSalesforce/Teams両セッションが切れていたため、ユーザーに2回に分けて再ログインを依頼(自動化のバグではなく単純なセッション失効)。
4. 実機検証完了: 18本フルパイプライン全件成功。Teams確認機能単体テストも成功(確認メッセージが実際に自分宛てチャットに投稿され、3分間無返信→自動的にダウンロード開始まで確認)。Teamsタブ操作失敗時にダウンロードを止めないフォールバックも実機で確認済み。
5. per-project memory `sf_reports_qbr_download_automation.md`を更新し、会社Mac・個人Mac双方が18本+Teams確認機能で揃った状態を記録。
Next: なし(完了)。次回定時実行(launchd、20分間隔ポーリング)で無人稼働時の安定性を継続観察。

## 2026-09-08T06:35:00+09:00〜07:00:00+09:00
Status: done
What: ユーザーから「ダウンロード時間短縮のため並列処理にできないか」との依頼。個人Mac版`download_all_reports.js`に並列ダウンロード(1本目は逐次実行→残りをworker pool方式で並列化)を実装。並列度5は18本中16本成功(2本がタブ強制終了で全滅)、並列度3では17→18/18成功と安定したため並列度3を採用(所要時間は逐次169秒→並列101〜121秒、約30〜40%短縮)。
途中、ユーザーから「ダウンロードのたびにブラウザウィンドウがアクティブになり作業の邪魔になる」との指摘。原因はcontext.newPage()がウィンドウを強制前面化する既知の挙動(個人Mac版にはこの対策が未実装だった)。`~/Scripts/outlook_cli/lib.js`の実績ある対策(画面外退避+元アプリへのフォーカス復帰)を移植し解消。フォーカス対策込みの最終実機テストで18/18成功を確認。
per-project memory `sf_reports_qbr_download_automation.md`を更新済み。
Next: フォーカス対策の体感確認はユーザー待ち。会社Mac版Python(`reports_pipeline/download_all_reports.py`)は今回未変更(逐次のまま) — 同様の並列化要望が出たら移植を検討。

## 2026-09-09T08:00:00+09:00〜08:50:00+09:00
Status: done
What: ユーザーから3件の依頼を順次対応。(1) 新規Salesforceレポート3件のURL追加依頼 → 実体は「（QBR集計用）月別_貢献利益（仕掛）_v2.1」の確度別(A/B/C)分割版と判明(id: 00OfP00000Kz63NUAR等)、`reports_config.py`に追加(21本)、単体実機テスト全件成功。個人Mac側への反映は新設した[[mac_handoff_relay]]の`personal_mac_inbox.md` task-001で依頼(→同日中に個人Mac側で自動実行・完了確認済み、cross_machine_relay_task001_and_windows_extension.md参照)。(2) 逆に2026-09-07追加の「仕掛項目分割版_A/_B/_C」(00OfP00000KuV0nUAF等)が不要になったとの指示 → `reports_config.py`から削除(18本に)、個人Mac側への削除依頼をtask-002として投入。(3) 確度A/B/Cの3レポート限定でダウンロード後に自動フォーマット(T/U/V/W列に桁区切り、各部小計行をFFFB00でハイライト)する依頼 → `xlsx_post_process.py`を新設し`download_all_reports.py`に組み込み、既存17ファイルに即時適用+新規ダウンロードでの実機テスト両方成功確認。
Next: task-002(個人Mac側の3本削除)のResultが実は誤って task-001と同じ内容("3本追記")のまま書かれておりStatusもpendingのままだった(詳細は[[mac_handoff_relay]]参照) — 次回個人Macセッションで正しく削除処理されるか要確認。確度A/B/Cフォルダに旧レポートのファイルが混在している件もユーザー未確認のまま。

## 2026-10-26T17:50:00+09:00
Status: done
What: 「SFデータがDLできなかった様子」の原因調査(変更なし)。9:00枠は設定売総X部署が「エクスポートメニューのトリガーボタンが見つかりません」×2→「Page.goto: Download is starting」で3回失敗したが5分後の再実行で18/18成功・COMBINED更新済み。16:45枠は日系ターンアラウンド打合せ(〜17:30)で遅延待機に入り、直後の「ベオグラード万博 行催事制作定例」(17:30-18:30, showAs=tentative)を会議中と判定して待機継続(最大90分=18:15で強制開始)。カレンダーexport(CalendarExport/calendar_events.json)は10/11で更新停止(15日古い)。
Next: 会議判定でtentativeを除外するか/カレンダーexport更新停止の復旧をユーザーに提案。

## 2026-10-27
Status: done
What: ユーザー依頼「会議後に取り直す」を実装(会社Mac `reports_pipeline/download_all_reports.py`、バックアップ `.bak_20261027`)。変更点: (1) 会議待機の90分上限と会議中強制開始を廃止し、会議が空くまで待つ(当日21時で打ち切り、スロット未完了のまま終了しTeams WARN)。(2) 5分以内に次の会議が始まる隙間では開始しない(lookahead)。10/26の17:30連続会議で動作確認(17:26→18:30待ち、18:20→18:30待ち、18:40→開始可)。個人Macは現状維持・失敗時はTeams通知のみの方針(ユーザー決定、10/26)。会議判定自体(tentative含む)は正しいとユーザー確認済み→変更しない。
Next: カレンダーexport(CalendarExport/calendar_events.json)が10/11で更新停止。復旧は未着手。
