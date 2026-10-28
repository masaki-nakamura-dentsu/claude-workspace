# 個人Mac(ICPTokyo2022)宛てタスクキュー

会社Mac(d14461)側のClaude Codeが、個人Mac側にやってほしい作業をここに追記する。
個人Mac側は**セッション開始時に自動でこのファイルを確認**する(README.md参照、
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

---

## [2026-09-08T16:15] task-001 — reports_pipeline_personalにSalesforceレポート3本を追加
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し (Salesforce自動DLパイプライン、[[sf_reports_qbr_download_automation]]参照)
Status: done
Instruction: |
  会社Mac側 `~/SalesforceExport/reports_pipeline/reports_config.py` の `REPORTS` に
  以下3本を追加済み(計21本)。個人Mac側フェイルオーバー用
  `~/SalesforceExport/reports_pipeline_personal/reports_config.js` の
  `REPORTS` にも同じ3本を追記して計21本に揃えてください(folder名・id完全一致):

  ```js
  { folder: "（QBR集計用）月別_貢献利益（仕掛）_v2.1_確度A", id: "00OfP00000Kz63NUAR" },
  { folder: "（QBR集計用）月別_貢献利益（仕掛）_v2.1_確度B", id: "00OfP00000Kz6D3UAJ" },
  { folder: "（QBR集計用）月別_貢献利益（仕掛）_v2.1_確度C", id: "00OfP00000Kz6JVUAZ" },
  ```

  会社Mac側で3本とも単体ダウンロード実機テスト済み(2026-09-08、成功・正しいサブフォルダに保存確認済み)なので、
  個人Mac側では設定ファイルへの追記のみでよい(改めてのダウンロードテストは任意、
  やる場合は`download_all_reports.js`の単体実行で1本だけ試せば十分)。
Result:

---

## [2026-09-08T16:40] task-002 — reports_pipeline_personalから不要レポート3本を削除
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し (Salesforce自動DLパイプライン、[[sf_reports_qbr_download_automation]]参照)
Status: done
Instruction: |
  ユーザーから「もう不要」との指示があり、会社Mac側`reports_pipeline/reports_config.py`の
  `REPORTS`から以下3本(2026-09-07追加の「仕掛」項目分割版_A/_B/_C)を削除済み。
  個人Mac側`reports_pipeline_personal/reports_config.js`の`REPORTS`からも同じ3本を
  削除してください(folder名・idで特定):

  ```js
  { folder: "（QBR集計用）月別_貢献利益（仕掛）_v2.1_A", id: "00OfP00000KuV0nUAF" },
  { folder: "（QBR集計用）月別_貢献利益（仕掛）_v2.1_B", id: "00OfP00000KuV5dUAF" },
  { folder: "（QBR集計用）月別_貢献利益（仕掛）_v2.1_C", id: "00OfP00000KuVC5UAN" },
  ```

  注意: task-001で追加を依頼した`_確度A/_確度B/_確度C`(id `00OfP00000Kz63NUAR`等)とは
  別物なので消さないこと。既存のダウンロード済みファイル(`Salesforce書き出し/`配下の
  該当サブフォルダ)はそのまま残してよい、今後のダウンロードだけ止めればよい。
Result:
  [2026-09-08] (誤記) reports_config.jsに3本追記完了、計21本に一致 — これはtask-001の結果の誤転記。

  [会社Mac側から2026-09-09追記: 上記Resultはtask-001(3本"追加")の結果と同一文面で、
  本タスク(3本"削除")の実施内容と一致していません。Statusもpendingのままのため、
  未処理として扱ってください。実行時は本Instructionの「削除」内容と実際の変更を
  突き合わせてからResult/Statusを更新してください。]

  [2026-09-09 個人Mac側で実施: reports_config.jsから`_A/_B/_C`(id 00OfP00000KuV0nUAF /
  00OfP00000KuV5dUAF / 00OfP00000KuVC5UAN)の3本を削除。`_確度A/B/C`(id 00OfP00000Kz63NUAR等、
  task-001分)は残存を確認済み、誤って消していない。既存ダウンロード済みファイルは削除していない。
  残REPORTS件数は18本(21本→3本削除)。]

---

## [2026-09-09T18:50] task-003 — 個人Mac側フェイルオーバーにも「移動時間対策の保険」を追加
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し (Salesforce自動DLパイプライン、[[sf_reports_qbr_download_automation]]参照)
Status: done
Instruction: |
  ユーザーから「個人Macでも同様の移動時間対策の保険をかけて欲しい」との依頼(会社Mac側
  の対応を受けての横展開依頼)。背景:

  会社Mac側で2026-09-09に2件の問題を修正済み:
  1. `download_all_reports.py`の`save_as()`後にダウンロードが実は0バイト/破損していた
     のに「OK」と誤判定するバグを発見(Chromeがダウンロードを内部的にキャンセル/ブロック
     しても例外を出さないケースがある)。`validate_download(dest)`関数(サイズ0チェック+
     `zipfile.is_zipfile()`によるxlsx形式チェック)を追加し、既存のリトライ機構
     (`download_one_report_with_retry`)に回収させるようにした。詳細は[[sf_reports_qbr_
     download_automation]]の「2026-09-09(続き): 16:45枠で16本が「OK」判定だが実は0バイト
     の空ファイルだった不具合」参照。
  2. 会社Mac側は11:15/16:45の固定時刻(StartCalendarInterval)実行のため、その時刻に
     Macが閉じていると取りこぼしても自動リトライしない弱点があった。ユーザーが「夕方は
     移動時間でMacを開いていない可能性がある」と指摘し、16:45枠向けに18:15(1.5時間後)
     リトライジョブ(`retry_1815_if_missed.py`+`com.nakamura.sfreports1815retry.plist`)
     を新設(既存の11:15枠向け13:00リトライと同じパターン)。

  個人Mac側でお願いしたいこと(該当ファイルは`~/SalesforceExport/reports_pipeline_personal/`
  配下、会社Mac側からは直接見えないためこちらで内容の詳細確認・実装をお願いします):

  a) **0バイト/破損ダウンロードの検証ロジック移植**: `download_all_reports.js`の
     ダウンロード保存直後(会社Mac版`validate_download`に相当する箇所)に、サイズ0チェック
     と、xlsxはzip形式なので先頭バイトが正しいzipマジックナンバー(`PK`で始まるか)等の
     簡易検証を追加し、不正なら例外を投げて既存のリトライ/並列処理のエラーハンドリングに
     回収させてください(Node.js版に適したzip検証ライブラリ or 先頭バイトチェックで可)。

  b) **フェイルオーバー自身の「移動時間対策」**: 個人Mac側は既に20分間隔ポーリング
     (`failover_check.js`、`com.nakamura.sfpersonalfailover.plist`)で「会社Macが未実行
     なら代行する」設計になっており、固定時刻式ではないため会社Mac版と全く同じ「+1.5時間
     リトライ」の形は不要なはずですが、1点確認・修正をお願いします:
     `failover_state.json`に「処理済みスロット」を記録する際、**そのスロットでの代行実行
     自体が失敗した場合でも「処理済み」として記録してしまっていないか**を確認してください。
     もし失敗時も処理済みマークされる実装であれば、それは「会社Macが閉じていて即座に
     リトライされない」問題の個人Mac版と同じ穴です(会社Mac側の18:15リトライがこの穴を
     塞いだのと同じ理由)。失敗時は処理済みマークせず、次の20分ポーリングで自然に再試行
     されるように修正してください(=ユーザーの「移動時間対策の保険」の意図に最も近い対応)。

  実装後、簡単な動作確認(単体レポートでの検証ロジック発火テスト、または既存ログの目視
  確認で十分)ができたらResultに記録してください。
Result:
  [2026-09-09 個人Mac側で実施完了]

  a) `download_all_reports.js`に`validateDownload(dest)`関数を追加(`downloadOneReport`内、
     `download.saveAs(dest)`直後に呼び出し)。サイズ0チェック+zip先頭シグネチャチェック
     (ローカルファイルヘッダ`PK\x03\x04`または空アーカイブ`PK\x05\x06`)。不正なら例外を投げ、
     既存の`downloadOneReportWithRetry`(最大3回)に回収させる。ライブラリ追加なし。
     実データxlsx(27808バイト)で正常判定、0バイトファイル・非zipファイルで正しく例外を
     投げることを単体テストで確認済み(構文チェック`node -c`も通過)。

  b) `failover_check.js`のバグを確認・修正: 修正前は`execSync(...download_all_reports.js)`が
     失敗(例外)しても、catchブロックでログ出力するだけで、その外側で無条件に
     `state.last_handled_slot`を保存していた(=代行実行が失敗しても「処理済み」と誤記録
     される穴が実在)。修正後は`state.last_handled_slot`の保存をtryブロック内・execSync成功時
     のみに移動。失敗時(1件でもNGでexit非0、またはFATAL)は状態を保存せず、次の20分ポーリング
     で自然に再試行される(会社Mac側18:15リトライと同じ意図を、個人Macの20分ポーリング設計
     の中で実現)。

  実機での本番ダウンロード実行テストは未実施(次回定時実行またはフェイルオーバー発火時に
  実地検証)。ログファイルの目視確認で十分との指示だったため、コードレベルの検証(構文
  チェック+単体ロジックテスト)を実施した。

---

## [2026-09-10T12:53] task-004 — 会社Mac側の同時実行事故対策(プロセスロック/前倒しスキップ/確認スキップ)を個人Mac側にも移植
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し (Salesforce自動DLパイプライン、[[sf_reports_qbr_download_automation]]参照)
Status: done
Instruction: |
  2026-09-10朝、ユーザーが「外出前に定時ダウンロードを前倒しで手動実行して」と依頼。
  11:13に手動実行を開始したところ、11:15の会社Mac定時実行(launchd)が同時に起動し、
  両プロセスが同じ共有ブラウザ(port 9226)の同じコンテキストに接続してダウンロード
  イベントを奪い合い、後発の定時実行側が0バイトファイルを14件も量産する事故が発生した
  (先発の手動実行は18/18成功、後発の定時実行は4/18成功・14件が空ファイル)。
  既存の`validate_download`(2026-09-09追加)は空ファイルを検知してリトライはするが、
  「2プロセスが同時に同じブラウザを取り合う」根本原因は解消しなかった(3回リトライしても
  もう一方のプロセスが動いている間は奪い合いが続くため)。

  会社Mac側`download_all_reports.py`に以下3点を実装済み(コードは
  `~/SalesforceExport/reports_pipeline/download_all_reports.py`参照、
  会社Mac側からはこのファイルの現物を直接渡せないため、下記の設計意図を個人Mac側
  Node.js版で同じ趣旨で実装してください):

  1. **プロセス排他ロック(0KBバグの根本対策)**: `pipeline.lock`ファイルにPIDを書き込み、
     起動時に既存ロックのPIDが生きていれば「他のインスタンスが実行中」と判断して
     即座に終了(何もダウンロードしない)。生きていない/不正な内容なら古いロックとみなし
     上書きして続行。終了時(成功/失敗問わず)は必ずロックを解放。
     個人Mac版`download_all_reports.js`にも同じ仕組み(`pipeline.lock`、`fs.existsSync`+
     プロセス生存確認は`process.kill(pid, 0)`が同等)を追加してください。会社Macとの
     二重実行(会社Mac定時実行中に個人Macのfailoverが誤発火する等)はブラウザのCDPポートが
     そもそも別(9226 vs 9227)なので直接の競合は起きないはずですが、**個人Mac内で
     ユーザーが手動実行した瞬間に、ちょうど`failover_check.js`の20分ポーリングが重なって
     `download_all_reports.js`を二重起動してしまうケース**への対策として同様に有効です。

  2. **`--scheduled`フラグ + 前倒し実行済みスロットのスキップ**: 会社Mac版はlaunchdからの
     定時実行にのみ`--scheduled`を付与し、このフラグがある時だけ「代表レポート
     (REPORTS[0])が直前スロット時刻以降に既にダウンロード済みなら前倒し実行済みとみなし
     スキップ」する判定を追加しました。個人Mac側は元々`failover_check.js`が「代表レポート
     フォルダの最新ファイルmtimeがそのスロット時刻以降か」を見てから
     `download_all_reports.js`を起動するかどうか判断する設計なので、**同種のスキップ判定は
     既に`failover_check.js`側に存在している可能性が高い**です。念のため実装を確認し、
     もし「会社Macで前倒し実行済み(=ファイルmtimeが更新済み)」のケースを正しくスキップ
     できているか確認してください。抜けがあれば会社Mac版と同じ考え方(直前スロット時刻
     以降にファイルがあればスキップ)で補ってください。

  3. **手動実行時はTeams確認(3分待ち)を省略**: 会社Mac版は`--scheduled`が無い場合
     (=ユーザーが直接`python3 download_all_reports.py`と明示的に依頼して実行する場合)、
     `ask_before_download`(自分宛てTeamsチャットへの事前アナウンス+3分待ち)を呼ばない
     ように変更しました(「明示的にダウンロードをお願いする場合は待ち時間は不要」という
     ユーザー指示)。個人Mac側`download_all_reports.js`の`askBeforeDownload`呼び出しにも
     同様のフラグ分岐(例: `--scheduled`引数の有無、またはfailover経由かCLI直接実行かの
     判定)を追加し、ユーザーがCLIから直接手動実行する場合は確認をスキップして即座に
     開始するようにしてください。`failover_check.js`から呼ぶ場合(自動実行)は従来通り
     確認を残してください。

  実装後、簡単な動作確認(ロックファイルが競合時に正しく他方をスキップさせるか、
  `--scheduled`無しでの単体実行が即座に開始するか、を単体テストレベルで確認)ができたら
  Resultに記録してください。実機での多重起動テストまでは必須ではありません(会社Mac側も
  次回定時実行での実地検証待ちの段階です)。

  4. **(追加、2026-09-10) ~/Downloadsへの副次コピー問題の根本修正**: ユーザーから
     「~/Downloadsに自動化由来のファイルが溜まっている、不要なら消して」との指摘があり、
     調査したところ、共有ボットブラウザ(CDP接続の実Chrome)経由でのダウンロードは
     `download.save_as(dest)`で指定フォルダへ複製されるだけで、**ブラウザ自身が既定の
     ダウンロード先(~/Downloads)に保存した元ファイルはそのまま残り続けていた**ことが
     判明(72件・約18MBが蓄積、6月〜9月10日分を確認・削除済み)。会社Mac側は
     `download_all_reports.py`/`download_step1_export.py`/`download_step2_enter_code.py`
     の全`save_as()`呼び出し後に`download.delete()`(Playwrightの、ブラウザ側の元ファイルを
     削除するAPI。保存先destには影響しない)を追加して解決した。個人Mac側
     `download_all_reports_personal.js`(Node.js版Playwright)の`download.saveAs(dest)`
     呼び出し箇所にも、直後に`await download.delete()`(try/catchでベストエフォート、
     失敗してもパイプラインは止めない)を追加してください。個人Mac側の共有ボット
     ブラウザ(port 9227)でも同じCDP接続方式のため、同じ現象(~/Downloadsへの蓄積)が
     起きている可能性が高いです。ついでに個人MacのローカルなDownloadsフォルダも
     既存の蓄積分があれば同様のファイル名パターン(レポート名+`-YYYY-MM-DD-HH-MM-SS.xlsx`)
     で確認・削除して構いません。
Result:
  [2026-09-10 個人Mac側で実施完了]
  1. プロセス排他ロック: `pipeline.lock`をディレクトリ直下に追加。起動時に既存ロックの
     PIDを`process.kill(pid,0)`で生存確認、生きていれば即`exit 1`(何もせず終了)、
     死亡/壊れていれば上書きして続行。`main()`の`.then()/.catch()`両方+`SIGINT`/`SIGTERM`
     ハンドラで確実にロック解放。単体テスト9ケース全パス(生存PID拒否/死亡PID上書き/
     壊れた内容上書き/解放後ファイル削除)、実ファイルでの二重起動テストも確認済み。
  2. 前倒しスキップ判定: `failover_check.js`を確認した結果、代表レポートのmtimeが
     直前スロット(11:15/16:45)+30分猶予以降なら`last_handled_slot`記録でスキップする
     判定が既に正しく実装済みと判明。コード変更不要。
  3. 手動実行時のTeams確認省略: `--from-failover`フラグを新設、`failover_check.js`側の
     起動コマンドに付与。`download_all_reports.js`は`FROM_FAILOVER`が真の時のみ
     `askBeforeDownload()`を呼ぶ(手動CLI実行時はスキップ・即開始)。
  4. `~/Downloads`副次コピー: `download.saveAs(dest)`直後に`try/catch`で
     `await download.delete()`を追加。既存の蓄積ファイル6件(約878KB)も確認の上削除済み。
  構文チェック(`node -c`)両ファイルOK。実機での多重起動・本番ダウンロードテストは未実施
  (次回定時実行での実地検証待ち)。

---

## [2026-09-10T13:38] task-005 — Chrome Remote Desktop導入＋個人WindowsへのWOL設定
Project: (プロジェクト横断・個人環境設定。関連する既存メモリなし、新規作業)
Status: done
Instruction: |
  ユーザーからの要望: 会社Mac(d14461)から個人Windowsを離れた場所からWake on LAN(WOL)で
  起動できるようにしたい。会社Macと個人Windowsは別LANのため直接WOLは届かない。そこで
  「会社Mac → (Chrome Remote Desktopで遠隔操作) → 個人Mac → (同一LAN内からWOL送信) →
  個人Windows」という経路にする方針。個人Macは自宅で個人Windowsと同一LANにいる前提。

  個人Mac側でやってほしいこと:

  1. **Chrome Remote Desktopのセットアップ**: 個人MacにChrome Remote Desktop(リモート
     デスクトップ機能、ホスト側)を導入・有効化し、会社Macから接続できる状態にする。
     Googleアカウントでのペアリングが必要なため、ユーザー本人の操作(認証・PIN設定等)が
     必要な箇所はその場で止めて、ユーザーに直接依頼すること(自動化しきれない部分)。

  2. **個人WindowsのWOL事前設定確認**: 個人WindowsをLAN経由で起こせるようにするための
     設定(NIC側のWOL有効化、Windowsの「高速スタートアップ」無効化、BIOS/UEFI側のWOL
     有効化)が済んでいるか確認。未設定ならユーザーに手順を案内する(Windows側のBIOS設定は
     Claudeから直接操作不可のため、ユーザーに作業してもらう箇所は具体的な手順書として渡す)。

  3. **個人Macから個人WindowsへWOL送信できる状態を作る**: 個人WindowsのMACアドレスを
     確認した上で、個人Mac側に`wakeonlan`コマンド(Homebrewで導入可)またはPython製の
     マジックパケット送信スクリプトを用意し、動作確認(実際にWindowsをスリープ/シャット
     ダウンさせて個人Macから起動できるかテスト)まで行う。

  4. **経路全体の動作確認**: 会社MacからChrome Remote Desktop経由で個人Macを操作し、
     そこから個人WindowsをWOLで起動できることを一度通しでテストする(可能なタイミングで)。

  ユーザーは現在会社にいて、帰宅後(個人Mac・個人Windowsが同一LANになるタイミング)に
  本格対応する想定。個人Macセッションが立ち上がった際、まずはできる範囲(Chrome Remote
  Desktopの導入、wakeonlanコマンドの用意、手順確認等)を自動で進めてよい。BIOS設定など
  物理操作が必要な箇所はユーザーに確認・依頼すること。
Result:
  [2026-09-10 個人Mac側で着手]
  - wakeonlanコマンドをHomebrewで導入済み(`brew install wakeonlan`)。
  - Chrome Remote Desktop Host(`brew install --cask chrome-remote-desktop-host`)導入は
    ユーザーに確認の上「進める」で承諾を得たが、実行時にsudoパスワードが必要でCLIから
    自動実行できないと判明(`sudo: a terminal is required to read the password`)。
    ユーザー本人にターミナルで`brew install --cask chrome-remote-desktop-host`を
    実行してもらう必要あり(sudoパスワード入力+完了後ログアウト/ログイン要)。
  - 個人WindowsのMACアドレス確認・WOL設定状況確認、Google アカウントでのペアリングは未着手
    (帰宅後・同一LANタイミングで対応)。

  [2026-09-10 続き・完了]
  - Chrome Remote Desktop: ユーザーが手動で`brew install --cask chrome-remote-desktop-host`
    実行→ログアウト/ログイン完了。初回ペアリングは「リモートサポート」タブ(一時コード方式)
    で行われ永続化されないことが判明したため、「リモートアクセス」タブでの再設定を依頼、
    完了。remotedesktop.google.com/access上でこのMacがオンライン表示されることを確認
    (`org.chromium.chromoting.broker`のroot権限プロセス起動を確認)。
  - 個人WindowsのWOLは既に設定済みと判明(iPhoneアプリ「Wolow」で運用実績あり)。
    ユーザーがそのアプリの設定画面スクリーンショットを共有し、MACアドレス
    `2C:F0:5D:D8:02:6F`を取得(ホスト名`DESKTOP-RYZEN5950`、LAN内IP`192.168.0.11`)。
    ※アプリ側のIP欄`113.147.123.63`は外出先(セルラー)からのWOL用に使っている router
    のWAN側公開IP経由の転送設定と推測、同一LAN内から送る個人Mac側では使わず
    ローカルブロードキャスト`192.168.0.255`宛てに送信する方式を採用。
  - 個人Macは`192.168.0.16`で同一LAN上にあることを確認。`wakeonlan -i 192.168.0.255 -p 9
    2C:F0:5D:D8:02:6F`で実機WOLテストを実施、送信約10秒後に`192.168.0.11`へのping応答を
    確認し起動成功。
  - 経路(会社Mac → Chrome Remote Desktopで個人Macへ接続 → 個人Macから上記wakeonlan
    コマンドを実行 → 個人WindowsがWOLで起動)が完成・実機確認済み。
Next: なし。会社MacからWindowsを起こしたい場合は、CRDで個人Macに接続後
  `wakeonlan -i 192.168.0.255 -p 9 2C:F0:5D:D8:02:6F`を実行すればよい。

---

## [2026-09-11T17:10] task-006 — 会社Mac側の16:45枠誤スキップ恒久バグ修正を個人Mac側にも移植・同種のバグが無いか確認
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し (Salesforce自動DLパイプライン、[[sf_reports_qbr_download_automation]]参照)
Status: done
Instruction: |
  ユーザーから「夕方の定時ダウンロードがキャンセルされた」と報告があり、会社Mac側
  `~/SalesforceExport/reports_pipeline/download_all_reports.py`の
  スロットスキップ判定(`already_done_for_slot`、2026-09-10導入)に恒久バグを発見・修正した。

  **バグの内容**: `SLOT_DEFS`が`(16, 45): (11, 15)`(=16:45枠は「11:15以降にファイルが
  あれば実行済み」とみなす)という定義になっていた。これだと**16:45枠自身の判定が、
  無関係な11:15枠(当日朝の正常実行)や13:00補助リトライの成功ファイルまで
  「16:45枠は完了済み」の証拠として誤って拾ってしまう**構造的な欠陥があり、11:15枠が
  毎日正常終了する限りほぼ必ず16:45枠(および同じ判定を通る18:15補助リトライ)を
  誤スキップしてしまう。2026-09-10は16:45launchdの起動が遅れ(16:59)許容誤差(±10分)
  の外だったため偶然発現しなかったが、2026-09-11は11:15枠の1本が失敗→13:00補助
  リトライがフル再実行→その成功ファイルが16:45枠の判定を誤って満たし、実際に
  16:45定時実行がスキップされた(実害発生)。

  **会社Mac側の修正内容**: mtime時間窓からの推測をやめ、`slot_state.json`
  (`{"date": "2026-09-11", "completed": ["11:15", "16:45"]}`のような形式)に
  「どのスロットが実際に完了したか」を明示記録する方式に変更した。
  - `already_done_for_slot(slot_key)`: この状態ファイルの`completed`リストに
    スロットラベル(`"11:15"`/`"16:45"`)が入っているかだけを見るシンプルな判定に変更。
  - `mark_slot_done(slot_key)`: `--scheduled`実行が1件以上成功した場合のみ、
    `main()`の末尾でこの状態ファイルに記録する。日付が変わっていれば自動リセット。
  - `SLOT_DEFS`は`(11, 15), (16, 45)`という単純なタプルに簡素化(時間窓定義が不要になった)。

  **個人Mac側でお願いしたいこと**:

  1. **まず確認**: `reports_pipeline_personal/download_all_reports.js`自体(会社Mac版
     `download_all_reports.py`に相当するファイル)に、同種の「代表レポートのmtimeが
     ○○以降かどうかでスロット完了を判定する」ロジックが存在するか確認してください。
     2026-09-10のtask-004完了報告(本ファイルの当該Result参照)では、「前倒しスキップ判定は
     `failover_check.js`側に既に正しく実装されている(スロット時刻+30分猶予で判定)」と
     報告されていたが、これは「会社Macが代わりに実行したかどうか」を見るfailover起動判定
     であって、**今回バグがあった「16:45枠の完了を11:15枠の成功で誤検知する」という
     "別スロットとの混同"のパターンとは別物**の可能性がある。`failover_check.js`と
     `download_all_reports.js`の両方について、「あるスロット向けの完了判定が、別スロットの
     成功実績を拾ってしまう作り」になっていないか改めて点検してください
     (特に、複数のスロット定義がある場合に「直前スロット以降」のような相対的な時間窓を
     使っていないか、が今回のバグパターンの核心)。

  2. **同種のバグが見つかった場合**: 会社Mac版と同じ考え方(状態ファイルへの明示記録方式)
     で修正してください。Node.js版なので、例えば`slot_state.json`を
     `fs.readFileSync`/`fs.writeFileSync`で読み書きし、日付が変わっていれば
     リセットする、という同じ設計で構いません。

  3. **同種のバグが無いと判明した場合**: 誤検知の心配が無い理由(設計上どう回避されて
     いるか)を簡潔にResultへ記録してください。個人Mac側は元々20分間隔ポーリング式
     (固定時刻の`--scheduled --slot`という概念自体が無い)ため、そもそも今回の会社Mac版
     特有の設計(11:15/13:00/16:45/18:15という4つの起動契機が同じ判定関数を共有する
     構造)に起因するバグである可能性もあり、その場合は「対象外」という結論で構わない。

  実装(または「対象外」の結論)ができたらResultに記録してください。実機での多重起動
  テストまでは必須ではありません(会社Mac側も次回16:45定時実行での実地検証待ちの段階です)。
Result:
  [2026-09-11 個人Mac側で点検完了 — 対象外(同種バグ無し)と判断]

  `download_all_reports.js`自体にはスロット完了判定ロジックは存在しない(grep該当なし)。
  スロット判定は`failover_check.js`のみに存在し、以下2点の理由で会社Mac版と同じ
  「別スロットの成功実績を誤って拾う」パターンには該当しないと確認:

  1. `latestExpectedSlot()`が返す`slot`(例: 今日の16:45)そのものを、その回の完了判定の
     閾値として直接使っている(`latestMtime >= slot`)。会社Mac版`SLOT_DEFS`のように
     「16:45枠 → 11:15を閾値とする」といった“別スロットの時刻を借りてくる”マッピングが
     存在しないため、11:15枠の成功ファイル(mtimeが11:15台)が16:45枠の判定
     (`>= 16:45`)を満たすことは構造的にありえない。

  2. `slotKey(slot)`が「11:15」「16:45」のような曜日非依存ラベルではなく、スロット瞬間の
     フルISOタイムスタンプ(例: `2026-09-11T02:15:00.000Z`)を使っているため、
     `state.last_handled_slot`は必ず「その日その回」に一意に対応する。会社Mac版のような
     日替わりリセットや「同じラベルの使い回し」による混同の余地もない。

  個人Mac側は元々20分ポーリング式で「11:15/13:00/16:45/18:15という4つの起動契機が
  同じ判定関数を共有する」会社Mac特有の構造自体が無いため、今回のバグはそもそも
  発生しうる設計になっていない。コード変更なし。

## [2026-09-16T15:25] task-007 — 外貨判定アプリ(CurrencySort)の開発基盤をビルド確認・実機テスト
Project: Software/CurrencySort
Status: done
Instruction:
  会社Mac(d14461)側で、iPhoneアプリ「CurrencySort(外貨スキャン)」の開発基盤一式を
  新規作成した(SwiftUI + SwiftData、Vision frameworkによるオンデバイスOCRで外貨の
  国・通貨を判定するアプリ。空港の外貨小銭を国ごとに仕分けて寄付する用途)。
  会社MacにはXcode本体が未インストール(Command Line Toolsのみ)でビルド・実機確認が
  できないため、Xcode/Homebrewが揃っている個人Macで以下をお願いしたい。

  背景: このタスクはユーザー(中村さん)からの明示依頼「個人MacのClaude Codeでやって
  もらうよう指示書を残しておいて」に基づく。既にgitリポジトリとして初期化・コミット済み
  (`Software/CurrencySort/`配下、Dropbox経由で個人Macにも同じ内容が同期されている
  はずなので、pull等は不要でそのまま作業できる)。

  1. **プロジェクト生成**: `Software/CurrencySort/` で `xcodegen` が無ければ
     `brew install xcodegen` を実行し、その後 `xcodegen generate` で
     `CurrencySort.xcodeproj` を生成する(project.ymlが正、.xcodeprojはgit管理外)。
  2. **ビルド確認**: `CurrencySort.xcodeproj` を開き、`Signing & Capabilities` で
     Apple ID(無料アカウントで可)のチームを設定した上でビルドが通るか確認する。
     特に以下のファイルは会社Mac側でUIKit(iOS SDK)が無く構文チェックしかできて
     いないため、意味的なエラーが出ていないか重点的に見てほしい:
     - `Sources/CurrencySortApp/Views/CameraPreviewView.swift`
       (`AVCapturePhotoOutputPhotoDelegate`の`nonisolated`メソッド内で
       `@MainActor`のプロパティへ`Task { @MainActor in ... }`経由でアクセスする
       実装。Swift 6の厳格な並行性チェックで警告/エラーになる可能性あり)
     - `Sources/CurrencySortApp/Views/ScanResultSheet.swift`、`ScanView.swift`
       (UIImage/UIViewRepresentable等、iOS SDK依存)
     - `Sources/CurrencySortApp/CurrencySortApp.swift`の`.modelContainer(for: ScanRecord.self)`
       やのSwiftDataまわりの記法
     ビルドエラーが出た場合は、可能な範囲で修正して問題ない(シンプルな型/並行性まわりの
     修正が中心と想定される)。
  3. **実機テスト**: カメラを使うためシミュレータでは撮影機能を確認できない。
     お手持ちのiPhoneをUSB接続し、実機ビルド・実行してカメラ撮影〜判定〜保存〜履歴〜
     国別集計の一連の画面遷移が動くか確認する。
     可能であれば実際の外貨紙幣(手元にあるもの)を撮影し、OCR判定の精度も見てほしい
     (`Resources/currencies.json`に34通貨分のキーワード辞書があるが、実紙幣で外れる
     場合はそこに追記して精度を上げてよい)。
  4. **修正・追記した内容はgitコミット**する(このプロジェクトは既にgit管理下、
     `.gitignore`で`*.xcodeproj/`と`Generated-Info.plist`は除外済みなので
     xcodegen生成物は気にせずコミットしてよい)。
  5. 詳細な手順・アーキテクチャ説明は `Software/CurrencySort/README.md` に記載済み
     なので先にそちらを参照。

  完了したら、ビルドが通ったか/どんな修正をしたか/実機での動作確認結果/OCR精度の
  所感を下のResultに記録してください。
Result:
  [2026-09-16 個人Mac側で着手・ビルド確認まで完了]

  1. Dropbox同期: `Software/CurrencySort`がこのMacに現れるまで指示投入から約12分かかった。
     さらに同期後もファイルが`com.dropbox.placeholder`（オンラインのみ）状態で中身0バイト
     だったため、`open -g`で各ファイルを開いて実体をダウンロードさせてから作業開始
     （CLAUDE.md記載のDropboxプレースホルダ対応標準手順通り）。

  2. Xcode本体: この個人Macにも実は未インストールだった（Command Line Toolsのみ、
     READMEの前提と食い違い）。ユーザー承認の上でXcode 27.0(3.8GB)を導入。
     `mas install`はApple側の大容量アプリ再ダウンロードAPI制限で
     「このApple Accountでは再ダウンロードできません」エラーが出て失敗、
     App Storeアプリ(GUI)経由でユーザーに手動インストールしてもらい解決。
     ライセンス同意(`sudo xcodebuild -license`)もユーザーに手動実行してもらった
     （sudoパスワードが必要でCLIから自動化不可、CRD導入時と同じ制約）。

  3. xcodegen導入・`xcodegen generate`実行: 成功、`CurrencySort.xcodeproj`生成済み。

  4. ビルド確認: `xcodebuild -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build`
     （Signing Team未設定でもコンパイル確認できる形）で実行。
     **実際にビルドエラーを1件発見・修正**:
     `Sources/CurrencySortApp/Views/CameraPreviewView.swift`の
     `extension CameraController: AVCapturePhotoOutputPhotoDelegate`が誤り
     （そのような型は存在しない）。正しくは`AVCapturePhotoCaptureDelegate`。
     修正後、**BUILD SUCCEEDED**を確認。他の懸念箇所
     （SwiftData `.modelContainer`、UIImage/UIViewRepresentable周り、
     `Task { @MainActor in ... }`のパターン）は全て問題なし
     （project.ymlで`SWIFT_VERSION: "5.0"`指定のため、Swift 6厳格並行性チェックは
     そもそも該当せず懸念不要だった）。
     修正はコミット済み（リポジトリのgit identityがこのMac未設定だったため
     ローカルのみ`user.name`/`user.email`を設定してコミット）。

  5. 実機テスト: **未実施**。iPhoneのUSB接続とSigning & Capabilitiesでの
     Apple IDチーム設定が必要だが、ユーザーが外出中のため後日対応。
     シミュレータ実行（カメラ非対応のため撮影機能自体は確認不可）は今回は
     行わず、ビルド確認のみで区切った。

  Next: ユーザー帰宅後、iPhone接続→Signing Team設定→実機ビルド・実行
  →カメラ撮影〜判定〜保存〜履歴〜国別集計の動作確認、可能なら実紙幣でOCR精度確認。
  完了時にStatusをdoneに更新すること。

  [2026-09-17 実機テスト完了・全項目Status: done]

  iPhone(iPhone 16 Pro、名称"iPhonemn")をUSB接続、Xcodeで無料Apple ID
  (maxakisan@gmail.com)をサインイン、Signing & CapabilitiesでTeam設定、
  iPhone側でDeveloper Mode有効化・開発者証明書の信頼、を経て実機ビルド・
  インストール・起動まで到達。ここから実際にユーザーに撮影してもらいながら
  対話的にデバッグし、**4件の実バグを発見・修正**（すべてコミット済み、
  詳細は[[currencysort_app_project]]参照）:

  1. 撮影画像がEXIF回転情報(`imageOrientation`)を失ったまま`.cgImage`を
     Visionへ渡しており、OCRが横倒し画像を処理していた
     （orientationを焼き込んだCGImageに正規化して解決）
  2. カメラが`.builtInWideAngleCamera`固定でマクロ(近接)撮影に切り替わらず、
     紙幣・硬貨へ近づくとピントが合わなかった
     （`.builtInTripleCamera`優先の仮想デバイス選択に変更して解決）
  3. OCRが拾った1〜2文字の短い断片が複数通貨のキーワードに偶然部分一致し、
     一致度25%で無関係な国が5件並ぶ現象が発生
     （3文字未満のテキストをマッチング対象から除外して解決）
  4. ベトナムドン等、`currencies.json`のキーワードがASCII表記("VIET NAM")
     なのに実機OCRは実際のダイアクリティカルマーク付き("VIỆT NAM")で
     返すため不一致になっていた
     （`.folding(options: .diacriticInsensitive, ...)`で正規化して解決）

  診断のため、結果画面に撮影画像のサムネイルと（候補ゼロ時のみ）OCR認識
  生テキストを表示するデバッグ表示も追加（README記載の「実際の手持ち紙幣で
  試して外れる場合はキーワード追記」という運用方針に沿う恒久機能として維持）。

  実機で最終確認できたこと:
  - インド紙幣(500ルピー): 一致度100%
  - ベトナム紙幣(20,000ドン): 一致度100%（修正前は0件だった）
  - 保存→履歴タブ→国別集計タブの一連の流れも正常動作確認済み
  - 硬貨(2ユーロ)はOCRが文字を1件も検出できず判定不可 — これは
    バグではなくOCRベース方式の既知の限界（刻印文字は低コントラスト・
    湾曲していて検出が難しい、README記載のTODO「硬貨対応の強化」の
    対象。今回はスコープ外、対応する場合はCore ML画像分類の検討が必要）。

  Status: done。今後さらに通貨キーワードの拡充や硬貨対応が必要になれば
  新規タスクとして立てること。

  [2026-09-17 続き: 硬貨のCore ML画像分類対応+重大バグ修正]
  ユーザー依頼「画像特徴から通貨判別」に対応。詳細は[[currencysort_app_project]]参照。
  要点: World Coins dataset(32カ国)+EuroCoinDataset(ユーロ23カ国別デザイン)で
  硬貨用Core ML分類器を学習(テスト精度95.7%)。実機で3回前後連続スキャンすると
  iOSにOOM Kill(メモリ不足強制終了)される重大バグを発見・修正
  (原因: OCRと画像分類を並列実行しピーク時メモリが重なっていた→順番実行に変更)。
  7回連続スキャンでクラッシュしないことを確認済み。紙幣用の予備分類器
  (BankNote-Net)はコストに見合わず削除、OCR+硬貨分類のシンプルな構成に整理。
  全変更コミット済み・README更新済み。

## [2026-10-05T09:00] task-008 — HDY定点観測の予備系(フェイルオーバー)launchdを個人Macに設置
Project: 中村正樹/Work/GBC_戦略企画部/GBC経営企画グローバル戦略分析／競合分析など/競合分析/HDY定点観測 (memory: hakuhodo_overseas_intel_monitoring)
Status: done
Instruction: |
  会社Macで博報堂DYグループ海外動向の自動収集(主系)を構築済み。個人Macに予備系を入れる。
  コードはDropbox同期済み: <上記Project>/hdy_monitor/ (run.sh / run.py)。README.md 参照。
  1. python3 で `import pandas, openpyxl` が通るか確認(無ければ pip install pandas openpyxl。venvは同期外に)
  2. 手動テスト: `run.sh backup` を実行 → 会社Macが動いていれば何もせず終了するのが正常
     (`python3 run.py --role backup --only tdnet` で通信だけ確認可。個人Macはプロキシ不要)
  3. ~/Library/LaunchAgents に2つ作成し launchctl load:
     - com.nakamura.hdymonitor.backup : /bin/zsh <Project>/hdy_monitor/run.sh backup 、StartInterval 10800
     - com.nakamura.hdydigest.backup  : /bin/zsh <Project>/hdy_monitor/run.sh backup --digest 、月曜 9:30
       (会社Macが8:45に作っていれば何もしない)
  4. ログは ~/hdy_monitor_logs/。完了したら Result に記入し、memory の hakuhodo_overseas_intel_monitoring にも追記。
Result:
  [2026-10-05 個人Mac] blocked: Work/GBC_戦略企画部/GBC経営企画グローバル戦略分析／競合分析など/ が個人Macに存在しない(同期完了後も無し=選択型同期の対象外とみられる)。hdy_monitor/ を読めないため未着手。python3(Homebrew)に pandas 未導入。ユーザーに選択型同期の有効化を依頼中。
  [2026-10-05 11:06 個人Mac] done。
  - ユーザーがフォルダを 競合分析/HDY定点観測/ に配置(「2026年_博報堂研究」階層なし)。中身は online-only だったため open -g でDL。
  - /opt/homebrew/bin/python3 (3.14) に pip --user --break-system-packages で pandas 3.0.6 / openpyxl 3.1.5。
  - run.sh backup → 主系稼働中のため無出力で終了(正常)。--role backup --only tdnet → 50件取得/新規0、通信OK。
  - ~/Library/LaunchAgents に com.nakamura.hdymonitor.backup(StartInterval 10800, RunAtLoad) と com.nakamura.hdydigest.backup(月曜9:30) を作成・load。launchctl list で両方 exit 0。
  - 注意: 個人Mac側でHDY定点観測フォルダを「オフラインで利用可能」にしておかないとSmart Syncでオンライン専用に戻りうる。

## [2026-10-05T10:05] task-014 — Salesforceフェイルオーバーの朝スロットを11:15→9:00に変更
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し ([[sf_reports_qbr_download_automation]]参照)
Status: done
Instruction: |
  ユーザー依頼(2026-10-05)により、会社Mac側の定時実行を「平日11:15/16:45」→「平日9:00/16:45」に変更済み
  (download_all_reports.pyのSLOT_DEFS、launchd plist、retry_1300_if_missed.pyの対象スロットを9:00に)。
  個人Mac側 ~/SalesforceExport/reports_pipeline_personal/failover_check.js の朝スロット定義(11:15)を
  9:00に変更してください(30分猶予→9:30以降に会社Mac未実行なら代行、の想定)。夕方16:45は変更なし。
  変更後、ドライラン等で判定が正しいことを確認し、Resultに記入。
Result:
  [2026-10-05 16:20 個人Mac] failover_check.js の SLOT_TIMES を [11,15]→[9,0] に変更(バックアップ failover_check_bak_20261005.js)。ロジックの単体ドライランで、本日16:17時点の直近スロット=09:00、代表フォルダの最新ファイル10:47 → 完了済み判定(代行しない)。10/6 9:20→09:00スロット、17:30→16:45、土曜→金曜16:45を確認。
  別件で判明: launchd経由だとexecSyncの`node`がPATHに無く「node: command not found」で代行実行が毎回失敗している(今日11:45以降の失敗ログはこれ)。→ 16:20にユーザーの承認を得てprocess.execPathに修正済み。今日の9:00スロットは完了済み判定でstateに記録した。

## [2026-10-15T11:05] task-015 — 個人Macフェイルオーバーに遠隔停止フラグを追加
Project: 中村正樹/Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し (Salesforce自動DLパイプライン、[[sf_reports_qbr_download_automation]]参照)
Status: done
Instruction: |
  背景: 2026-10-15、会社Macが部分再実行中なのに個人Mac(自宅で操作不可)が欠けた分の補完を
  繰り返し、ユーザーが止めたくても会社Macから止める手段が無かった(ユーザー承認済みの改修依頼)。

  `~/SalesforceExport/reports_pipeline_personal/failover_check.js` の main 冒頭(判定・DL処理より前)に
  以下を追加してください:
  1. Dropbox上の停止フラグ
     `<Dropboxルート>/中村正樹/.claude-sync/claude_relay/personal_failover_pause`
     が存在すれば、ログに「停止フラグあり: スキップ」と1行出して何もせず終了(exit 0)。
     DL・Teams確認・attempt_count加算もしない。
  2. フラグの中身に `until=YYYY-MM-DDTHH:MM` 行があれば、その時刻を過ぎたら無視して通常動作に戻る
     (消し忘れ対策)。中身が空なら手動で消すまで停止。
  3. フラグが0バイトのDropboxプレースホルダ(com.dropbox.placeholder)でも「存在=停止」として扱う。
  作業前に `failover_check_bak_20261015.js` としてバックアップ。launchd設定は変更不要。
  検証: フラグあり/なし/until過去/until未来の4パターンで判定関数を単体テスト、
  その後 run_failover_check.sh を1回実行してフラグ無しで通常判定になることを確認しResultに記入。
  ※ 編集は許可済みスクリプトの編集にあたるため、自動モードで実行不可なら手順をユーザーに渡すこと。
Result:
  [2026-10-17 11:07 個人Mac] failover_check.js に停止フラグを追加(バックアップ failover_check_bak_20261015.js)。main冒頭で
  .claude-sync/claude_relay/personal_failover_pause を探し、あればログ「停止フラグあり(...): スキップ」で即終了(DL・Teams・attempt_count加算なし)。
  中身に until=YYYY-MM-DDTHH:MM(ローカル時刻)があれば期限後は無視。空・0バイトplaceholder・読込不可はすべて停止扱い。
  単体テスト: なし→通常/空→停止/until過去→通常/until未来→停止/読込不可→停止 すべて期待通り。
  実フラグ(until未来)を置いて run_failover_check.sh → スキップ、削除して再実行 → 通常判定(10/16 16:45スロット処理済み)を確認。
  使い方(会社Macから): 止める→ echo "until=2026-10-20T18:00" > .claude-sync/claude_relay/personal_failover_pause / 再開→ ファイル削除。

---

## [2026-10-17T18:40] task-016 — Windows側SSH設定の完了に伴うMac側の接続先ユーザー変更+疎通確認
Project: 中村正樹/ (ルート)。[[home_network_setup]] windows_inbox task-018 の対になるタスク
Status: done (2026-10-17 personal Mac)
Instruction: |
  背景: windows_inbox task-018(個人MacからWindowsを遠隔シャットダウン)をWindows側で実施中。
  その過程で中村さんから「ログインユーザーは maxak ではなく maxakisan にしたい」と変更指示があり、
  Windows側に **maxakisan という管理者アカウントを新規作成**しました(2026-10-17実施済み、
  SID ...-1003、Administratorsグループ所属を確認済み)。
  そのため **Mac側の ~/.ssh/config が `User maxak` のままだと接続できません**。

  なお、Windows側のSSH設定本体(OpenSSH Server導入/鍵認証化/鍵登録/FW制限)は、
  Windows側Claude Codeの自動モード安全フィルタ(Unauthorized Persistence)に阻まれて
  Claudeからは実行できなかったため、**中村さんが管理者ターミナルで手動実行中**です。
  **【2026-10-17 18:55 追記】Windows側の手順[0]〜[5]は全て完了しました。着手可能です。**
  - sshd = Running/Automatic、port22 LISTEN確認済み(0.0.0.0:22 と [::]:22)
  - PasswordAuthentication no / PubkeyAuthentication yes
  - administrators_authorized_keys に鍵1行(115B, BOM無し)、icacls で Administrators:F/SYSTEM:F
  - FW RemoteAddress = 192.168.0.0/24, 100.64.0.0/10 のみ
  - 注意1: FWルールのProfileが **Private のみ**。Windows側が今接続中のaterm-2563e2-aはPrivate判定なので通る。
  - 注意2: **Windows側にTailscaleは未導入**。よって接続は**同一LAN(192.168.0.11)からのみ**可能。
    外出先からの遠隔シャットダウンは現状できない(必要ならTailscale導入が別途必要)。

  やってほしいこと:
  1. ~/.ssh/config の Host win-home ブロックの User を maxak → maxakisan に変更:
       sed -i '' 's/User maxak$/User maxakisan/' ~/.ssh/config
       grep -A3 'Host win-home' ~/.ssh/config    # User maxakisan になったか確認
     (Host win-home = 192.168.0.11 / IdentityFile ~/.ssh/id_ed25519_windows はそのまま)
  2. 疎通確認: `ssh win-home hostname` → **DESKTOP-RYZEN59** と返れば成功。
     初回は host key の確認プロンプトが出るので yes。
     失敗する場合の切り分け:
       - Permission denied (publickey) → Windows側の administrators_authorized_keys の
         内容/権限(icacls)を疑う。公開鍵は id_ed25519_windows.pub と一致必須
       - Connection refused → Windows側で sshd が起動していない(Get-Service sshd)
       - Connection timed out → FWのRemoteAddress制限がLANを含んでいない可能性
  3. .claude-sync/Scripts/windows_power/win_power.sh 内に `maxak` 決め打ちの箇所が
     あれば maxakisan に修正(Host別名 win-home 経由なら修正不要の想定だが要確認)。
  4. シャットダウンの実動作テストは、中村さんに「今Windowsを落としてよいか」を確認してから。
     Windows側task-018のResultに「疎通確認のためWindowsは起動したままにする」と書いてあるので、
     勝手に落とさないこと。
  5. **【2026-10-17 19:10 追記 — Tailscale導入済み。外出先からも使えるようにしてください】**
     Windows側にTailscaleを導入・ログイン完了しました(v1.104.1、サービスRunning/Automatic)。
     - Windowsのtailnet名/IP: **desktop-ryzen5950 / 100.100.64.40**(アカウントは maxakisan@ でMacと同一tailnet)
     - Tailscaleアダプタの NetworkCategory = Private なので、SSHのFWルール(Profile=Private)が適用され通る
     - Windows内から `Test-NetConnection 100.100.64.40 -Port 22` = True、`tailscale ping macbookmn` = 11msで応答確認済み
     そこで ~/.ssh/config を **LAN用とTailscale用の2系統**にしてください(外出先はLAN IPに届かないため):
       Host win-home        # 自宅LAN内から(高速)
         HostName 192.168.0.11
         User maxakisan
         IdentityFile ~/.ssh/id_ed25519_windows
       Host win-ts          # 外出先から(Tailscale経由)
         HostName desktop-ryzen5950   # または 100.100.64.40
         User maxakisan
         IdentityFile ~/.ssh/id_ed25519_windows
     疎通確認は **両方**行うこと: `ssh win-home hostname` と `ssh win-ts hostname`(ともに DESKTOP-RYZEN59)。
     win_power.sh も、LAN内で失敗したらTailscale側(win-ts)にフォールバックする作りにしておくと
     自宅/外出先を意識せず使えます(任意、中村さんに確認の上)。
  6. 完了したらこのtask-016のResultに結果を記入し、Teams Webhookで一報。

Result: |
  2026-10-17 個人Macで実施。~/.ssh/config をバックアップ(~/.ssh/config.bak_20261017)してから変更。
  - Host win-home の User を maxak → maxakisan に変更
  - Host win-ts(HostName desktop-ryzen5950, User maxakisan, 同じ鍵)を新しく追加
  - 疎通確認: ssh win-home hostname / ssh win-ts hostname ともに DESKTOP-RYZEN5950 を返した(host keyは両方登録済み)
  - win_power.sh: maxak を決め打ちしている箇所はなし(HOST="win-home" の別名を使う)→修正不要。
    LAN→Tailscaleの自動切り替えは未実装(ファイルの読み取りが自動モードで拒否されたため。必要なら中村さんの許可を得て対応)
  - シャットダウンの実動作テストは未実施(勝手にWindowsを落とさない)


---

## [2026-10-17T19:30] task-017 — 外出先からWindowsを起動できるようにする(raspiをWoL中継役に)
Project: 中村正樹/ (ルート)。[[wol_setup_status]] [[windows_ssh_remote_access]] windows_inbox task-018の続き
Status: done (2026-10-17 personal Mac)
Instruction: |
  背景: 外出先からWindows(desktop-ryzen5950)をTailscale経由でシャットダウンできるようになったが
  (windows_inbox task-018)、**起こす手段が無い**ため「落としたら帰宅まで使えない」状態。
  中村さんから「また外出先から起動できるようにして」と依頼(2026-10-17)。

  方針: **ルーター(HGW-BL500HM)の管理パスワードは不要**。WoLをインターネット越しに飛ばす
  (=ポート開放)のは自宅インフラ非公開の方針に反するため採らない。代わりに
  **常時稼働している raspi をtailnet内のWoL中継役**にする:
    外出先 → Tailscaleでraspiにssh → raspiがLAN内にマジックパケットをブロードキャスト → Windows起動
  これならポート開放ゼロ、ルーター設定ゼロで済む。

  【Windows側は確認済み・変更不要】(Windows側Claudeが2026-10-17に検証)
  - MACアドレス: **2C:F0:5D:D8:02:6F** (Realtek PCIe 2.5GbE Family Controller #2、有線)
  - LAN IP 192.168.0.11 / tailnet desktop-ryzen5950 (100.100.64.40)
  - `*WakeOnMagicPacket=1` / `S5WakeOnLan=1`(シャットダウン状態からの起動を許可) /
    `PnPCapabilities=0` / `HiberbootEnabled=0`(高速スタートアップ無効) /
    `powercfg /devicequery wake_armed` にNICが列挙済み
  → OS側は完全に準備済み。残るリスクはBIOS/UEFI側のみ(下記5参照)。

  やってほしいこと:
  1. raspi(tailnet: raspi / 100.96.219.107、LAN: 192.168.0.16)にsshし、WoL送信ツールを入れる:
       ssh raspi 'sudo apt-get update && sudo apt-get install -y wakeonlan'
     (wakeonlanが無ければ etherwake でも可。etherwakeの場合はsudoとインターフェース指定が必要)
  2. raspi上に送信スクリプトを置く(例 ~/wake_windows.sh):
       #!/bin/bash
       wakeonlan 2C:F0:5D:D8:02:6F
     chmod +x して、`ssh raspi '~/wake_windows.sh'` で呼べることを確認。
  3. Mac側のラッパーを整備: .claude-sync/Scripts/windows_power/win_power.sh に `wake` サブコマンドを追加
     (または win_wake.sh を新設)。中身は実質 `ssh raspi 'wakeonlan 2C:F0:5D:D8:02:6F'`。
     既存の shutdown 系サブコマンドと揃えた使い勝手にすること。
     あわせて、shutdown側も **LAN(win-home)で失敗したらTailscale(win-ts)にフォールバック**する作りに
     しておくと自宅/外出先を意識せず使える(task-016の追記参照)。
  4. **実動作テスト**(中村さんの許可を取ってから。Windowsが落ちるため):
     a. 中村さんに「今Windowsを落として起動テストしてよいか」を確認
     b. `ssh win-home 'shutdown /s /t 0'` でシャットダウン
     c. 1〜2分待ってから `ssh raspi '~/wake_windows.sh'`
     d. 30〜60秒後に `ssh win-home hostname` が通れば **成功**
     e. Tailscale経由でも効くか確認(Macのtailnetからraspi経由で起こす = cと同じ経路なのでOK。
        厳密な外出先テストは、Macのwi-fiを切ってiPhoneのテザリングにする等で後日)
  5. **起動しなかった場合の切り分け**(ここが本命のリスク):
     - raspiから `ping 192.168.0.11` が落ちている状態でマジックパケットを送っているか確認
     - **最有力の原因はBIOS/UEFI**。ASUS/MSI等の設定で以下を中村さんに確認してもらう:
         * `ErP Ready` / `ErP S4+S5` を **Disabled** に(有効だとS5でNICへの給電が切れWoL不可)
         * `Power On By PCI-E/PCI Device` または `Resume By PCI-E Device` を **Enabled**
         * (MSIなら Settings > Advanced > Wake Up Event Setup)
       この項目は中村さんが再起動してBIOSに入る必要があるため、Claudeからは変更できない。
     - スリープ(S3)からは起きるがシャットダウン(S5)からは起きない場合も上記ErPが原因。
       暫定運用として「シャットダウンではなくスリープで落とす」(`rundll32 powrprof.dll,SetSuspendState 0,1,0`)
       という回避策もある。中村さんに選んでもらう。
  6. ★★【必須: 起こしただけではOllamaが動かない — Windows側Claudeが2026-10-17に発見】
     Ollamaは常駐サービスではなく、**タスクスケジューラ `Ollama_LAN_Serve`** で起動している。
     その実行プリンシパルが **UserId=maxak / LogonType=Interactive** のため、
     **maxak が対話ログオンしていないと起動しない**(5分間隔のウォッチドッグも同様に動かない)。
     → **WoLで起こしただけでは Ollama(11434)が上がらず、Macからの要約・照合は失敗する。**
       (sshd と Tailscale はサービスなので自動復帰する。Ollamaだけが上がらない)

     対策: wakeスクリプトに「起動後にOllamaを叩き起こす」ステップを入れること。
     sshが通るようになってから以下を実行する(maxakisanで入ってもOK):
       ssh win-ts "powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\maxak\ollama_serve_lan.ps1"
     このスクリプトは中で OLLAMA_HOST=0.0.0.0:11434 と OLLAMA_MODELS=D:\ollama_models を
     明示セットしているので**実行ユーザーのプロファイルに依存しない**(検証済み):
       - モデル実体は D:\ollama_models (21.4GB)。ACLは Authenticated Users:Modify /
         BUILTIN\Users:ReadAndExecute なので **maxakisan からも読める**
       - スクリプト冒頭に `Get-Process ollama` のガードがあり、**既に起動済みなら何もしない
         (冪等)**。毎回呼んで構わない
     起動確認: `curl -s http://desktop-ryzen5950:11434/api/tags` が200でモデル一覧を返すこと
     (LAN内なら http://192.168.0.11:11434/api/tags)。

     恒久対応の選択肢(中村さんに提案し判断を仰ぐこと。今回は上記のwakeスクリプト側対応で足りる):
       タスク `Ollama_LAN_Serve` を「ユーザーがログオンしていなくても実行する」(S4U)に変更し
       AtStartupトリガーを追加すればログオン不要で自動復帰する。ただし
       **Windows側Claudeは自動モードの安全フィルタ(Unauthorized Persistence)で
       スケジュールタスクを変更できない**ため、中村さんの手動実行が必要
       ([[feedback_automode_blocks_persistence_setup]])。

  7. 結果をこのtask-017のResultに記入し、Teams Webhookで一報。
     成功したら [[wol_setup_status]] のメモリを「ルーター経由は不要、raspi中継で解決済み」に更新すること
     (現メモリは「ルーターの管理パスワード不明で保留中」のままなので要修正)。


Result: |
  2026-10-17 個人Macで実施(中村さんの許可を得てWindowsを停止→起動テスト)。
  - ラズパイ側は既に準備済みだった: wakeonlan導入済み、WoL中継 wol-http.service(Tailscale内 :8090 /wake/windows)が稼働中。win_power.sh wake もこれを使う。apt導入は不要
  - Mac ~/.ssh/config に Host raspi(100.96.219.107, User masaki, ~/.ssh/id_ed25519)を追加
  - 実テスト: ssh win-home 'shutdown /s /t 0' → 50秒でping停止 → さらに40秒後にラズパイから停止を確認 → curl $RELAY/wake/windows → 70秒で ssh win-home hostname が DESKTOP-RYZEN5950 を返した。BIOS変更は不要(S5から起動OK)
  - Ollama: 起動直後は応答なし(想定どおり)。ssh経由で ollama_serve_lan.ps1 を実行してもssh切断で子プロセスが止まり起動しない → WMI(Win32_Process.Create)で切り離して起動する方式に変更し成功。qwen3.8:27b の生成も確認
  - 新規スクリプト Scripts/windows_power/win_wake_full.sh: 起動→sshが通るまで待つ(win-home→win-tsの順)→Ollama起動→11434の応答確認。起動中のときに実行してOKを確認
  - 残課題: Tailscale経由(desktop-ryzen5950:11434)ではOllamaに届かない(Windows FWのOllamaルールがLANのみと推定)。外出先からOllamaを使うならWindows側でFWに100.64.0.0/10を追加。win_power.sh本体の読み取りは自動モードに拒否されたため未変更。恒久対応(Ollama_LAN_ServeをS4U+AtStartupへ)は未提案のまま

## [2026-10-19T10:45] task-019 — Agency OS月次更新(アレココ・CCS→Skill・Dify自動反映)のlaunchd登録
Project: 中村正樹/Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/GBC-Knowledge
Status: done
Instruction: |
  中村さん依頼(10/19): 毎月第1営業日にアレココ目録・CCSカタログを作り直し、ChatGPT Skill(Agency OS)とDifyへ自動反映。
  スクリプトは会社Macで作成済み: GBC-Knowledge/tools/monthly_update.sh(使い方は先頭コメント)。
  個人Macで行うこと:
  1. 前提確認: ~/arekoko_files・~/arekoko_pages がある / python3 で jpholiday, pymupdf, python-pptx, docx, openpyxl が import できる
     (足りなければそのpythonの絶対パスを PY として plist に入れる)/ 9231(dentsu-work-bot)・9229(chatgpt-work-bot)が起動中 / win_power.sh status。
  2. 試走: tools/monthly_update.sh --force --no-deploy(反映しない)。ログ output/monthly_update/run_YYYYMMDD.log。
     差し替え用_YYYYMMDD_auto に変更ファイルが出ること、Windowsが最後にシャットダウン予約されることを確認。
  3. ~/Library/LaunchAgents/com.nakamura.agencyosmonthlyupdate.plist を作成: ProgramArguments=/bin/bash <monthly_update.sh絶対パス>、
     StartCalendarInterval 平日(Weekday1-5)9:00、RunAtLoadなし、EnvironmentVariables に PATH(/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin)・必要なら PY、
     StandardOut/Err は ~/AgencyOSMonthlyUpdate/ に。launchctl bootstrap し、launchctl print で runs = 0 を確認。
     auto modeで拒否されたら中村さんにターミナル用コマンドを渡す。
  4. 初回本番は 2026-11-02(月)9:00。9231/9229 が落ちていると ERROR 通知で止まる設計。
  会社Mac側は確認だけのジョブ com.nakamura.agencyosmonthlycheck(9:30)が別にある。今月の更新が始まっていなければ、会社Macから下記5の仕組みで実行を依頼してくる。
  5. 【10/19追加】会社Mac→個人MacのClaude Codeへの直接指示: 中村さんにターミナルで
     bash "$HOME/ICPTokyo2022 Dropbox/中村正樹/.claude-sync/Scripts/mac_direct/install.sh"(パスは実際のDropbox場所に合わせる)
     を実行してもらう(launchd com.nakamura.macdirect、KeepAlive。auto modeでは登録を拒否されるので手で)。
     確認: 会社Macから send.sh --wait-min 5 "pwdとhostnameを返して" → 個人Macのホスト名が返る。
  6. 会社MacのOllamaは10/19にアンインストール済み。要約は自宅Windows(win_power.sh)だけで行う。
Result: |
  2026-10-19 中村さんがターミナルで試走・install_monthly_update.sh を実行。launchd登録済み(runs=0)、試走は変更なしで正常終了。mac_direct も登録・往復確認済み。

## [2026-10-20T00:00] task-020 — iPhoneからのRemote Control待受(claude rc)をlaunchdで自動起動
Project: 中村正樹(Dropboxワークスペース直下)
Status: done
Instruction: |
  中村さん依頼(10/20): iPhoneのClaudeアプリ(Codeタブ)から個人MacのClaude Codeへ新規セッションを立てられるよう、claude remote-control を常駐させる。会社Macは設定済み(メモリ claude_remote_control_iphone.md 参照)。
  1. 作業フォルダ(~/"ICPTokyo2022 Dropbox/中村正樹"、実在パスを確認)で一度 claude を起動しtrust承認済みか確認(ホームでは rc 不可)。`which claude` で絶対パス確認。
  2. ~/ClaudeRC/run_rc.sh: PATH設定→作業フォルダへcd→ exec /usr/bin/caffeinate -is <claude絶対パス> remote-control
  3. ~/Library/LaunchAgents/com.nakamura.claude-rc.plist: RunAtLoad+KeepAlive, ThrottleInterval 60, Stdout/Err ~/ClaudeRC/rc.log。launchctl bootstrap gui/$(id -u)。
     手動の claude rc が同フォルダで動いていると "already served" で落ちるので先に止める。auto modeで登録拒否されたら中村さんにターミナル用コマンドを渡す。
  4. 確認: tail ~/ClaudeRC/rc.log に待受表示 → iPhone「Code」タブに個人Macが出て、新規セッションで pwd が作業フォルダを返す。
Result: |
  2026-10-20 中村さんがターミナルで ~/ClaudeRC/run_rc.sh + com.nakamura.claude-rc(RunAtLoad/KeepAlive, log ~/ClaudeRC/rc.log)を登録。iPhone Codeタブから接続確認OK。

## 2026-10-21 context_warn.py 欠落でプロンプトがブロックされる件
Status: done (2026-10-21 本人がcpで解決)
同期済みsettings.jsonのUserPromptSubmit hookが ~/.claude/context_warn.py を呼ぶが、個人Macに実体がない。
実行: `cp "<Dropbox>/.claude-sync/Scripts/hooks/context_warn.py" ~/.claude/context_warn.py`
確認: 適当なプロンプトを送り、hookエラーが出なければOK。

## [2026-10-23T18:00] task-023 — Euromonitor 過去3年レポートの一括ダウンロード(契約終了前)
Project: Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/Euromonitor_レポート保存_20261023/
Status: pending
Instruction: |
  会社Macが移動で閉じるため、残りを個人Macで実施。ユーザーは個人MacのブラウザでEuromonitorにログイン済み(個人Macの共有bot browser=port 9227。ログイン状態を確認し、切れていたら本人に依頼)。
  まず同フォルダの README_引き継ぎ.md を読む(API調査結果・未了事項・注意点が全部ある)。調査スクリプトは同フォルダ内(node。playwrightは個人Macの環境のものを使う)。
  手順: ①業界ごとに一覧を取り直して総件数確定 → ②1件でDownload操作を自動化して確認 → ③downloads/ に保存(ファイル名 YYYYMMDD_種別_タイトル)→ ④ダウンロード結果.md に件数・失敗を記録。
  総件数が数千件規模など大量なら、実行前に件数内訳(業界×種別)をユーザーに示して範囲を確認する。認証トークンはファイルに保存しない。使ったタブは閉じ、フォーカスを奪わない。
Result:

## [2026-10-23T18:30] task-025 — Euromonitor DL: 個人Mac側の bulk.js を停止する(重複回避)
Project: Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/Euromonitor_レポート保存_20261023/
Status: done
Instruction: |
  個人Macが960番目より古い側まで処理していたため、会社Mac担当分(960〜末尾)と321件重複した(同名上書きでファイルの重複はなし、通信が無駄になっただけ)。ユーザー指示により個人Macの担当を止める。
  1. 個人Macで動いている bulk.js を停止する(`pkill -f bulk.js`)。新規に再実行しない。
  2. downloads/ のファイルは消さない。dl_progress.jsonl も触らない。
  3. 停止後、Result に停止時刻と dl_progress.jsonl の成功件数を書く。
  残りの未完了(2台の記録合算で約120件、Opinion/Briefing中心)は会社Macが処理している。完了後の集計(ダウンロード結果.md)は個人Mac側が担当(会社Mac用_実行手順.md の記載どおり)。
Result:
2026-10-23 18:23 会社Macから mac_direct 経由で確認済み。個人Macのbulk.jsは既に停止(ブラウザが閉じて自然終了)、残プロセス0。dl_progress.jsonl 成功1303件。再実行しない。
追記 2026-10-23 18:30 個人Mac: 18:23の停止確認後、task-025を見落として18:25頃にbulk.js(k=0,2)を再起動してしまった(約20件を追加DL、同名ファイルは既存スキップ/上書きなし)。18:29に pkill -f bulk.js で停止、残プロセス0。dl_progress.jsonl 成功1321件(行数1332)。以後再実行しない。

## [2026-10-26T10:00] task-026 — Euromonitorアーカイブのアレココ Tool/21 への格納(準備済み、アップロードは要許可)
Project: Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/Euromonitor_レポート保存_20261023/
Status: done (2026-10-28 中村さん確認: 格納完了)
Instruction: |
  会社Macで格納用フォルダを準備済み。まず `アップロード準備_20261026/引き継ぎ_個人Macへ_20261026.md` を読む(経緯・格納先・B案の方針・未了・検証方法あり)。
  1. ユーザーに、SharePoint容量(追加約2.5GB)とライセンス確認が済んでいるかを聞く。
  2. 済んでいれば、許可を得てから、アレココ DocApp の Tool/21 の中に新規フォルダ「Euromonitorアーカイブ_20261023」を作り、`Euromonitorアーカイブ_20261023/` の中身をその中へアップロードする(PPTは含めない、Tool/21 の既存ファイルは触らない)。URL: https://esq365.sharepoint.com/sites/GBCarekoko/DocApp/Forms/AllItems.aspx?id=%2Fsites%2FGBCarekoko%2FDocApp%2FTool%2F21&viewid=c0b616e6%2Df3bd%2D4faa%2D88bb%2D119433bf7ac0
  3. 件数(3,700+索引)とhtml表示を検証し、Resultに記録。
Result: 2026-10-26 個人Mac: Dropbox全件DL後、OneDrive同期フォルダ Tool/21/Euromonitorアーカイブ_20261023 へコピー(3,703件、フォルダ別件数一致)。クラウド同期完了とWeb上の検証は未了。
