---
name: outlook-cli
description: "Outlook CLI `outlook`(~/Scripts/outlook_cli/) — Outlook Web(2026-08-12以降outlook.cloud.microsoftの新UI)をブラウザ自動化で操作、送信/一覧/検索/既読取得に対応。2026-08-11構築、2026-08-12に新UI対応・他人宛て送信検証・会社Mac(d14461)展開まで完了(両Mac動作確認済み)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 699a846e-5f8b-4a9f-8769-903afe771b8e
  modified: 2026-09-28T01:02:52.294Z
---

2026-08-11、ICPTokyo2022(このMac)で構築。New Outlook for Macはアプリ内AppleScript/Graph APIが使えない([[local_work_data_export]]で既知)ため、[[teams_cli]]と同じ発想でOutlook Web (`outlook.office.com`)をPlaywright+CDPのブラウザ自動操作で叩く方式。[[shared_bot_browser]]のこのMac用共有ボットブラウザ(port 9227, `~/.chrome-profiles/timetree-bot`)にタブとして相乗りし、専用プロファイルは作らない。

**構成** (`~/Scripts/outlook_cli/`, `~/.local/bin/outlook`にシンボリックリンク):
- `lib.js` — 共有ロジック(接続・ログイン確認・検索・一覧取得・既読メッセージの件名/差出人/日時/本文取得・新規メール作成・宛先/CC/BCC入力・件名/本文入力・添付・送信・下書き破棄)。
- `login.js`/`list.js`/`read.js`/`send.js` — サブコマンド本体。`outlook`がbashディスパッチャ。

**コマンド**:
```
outlook login                                     ログイン状態確認・初回ログイン
outlook list [検索文字列] [--limit N]              受信トレイ一覧 or 検索結果(既定15件)
outlook read <index> [--search "検索文字列"]        list の [番号] を開いて本文表示
outlook send --to a@x [--to b@y] [--cc c@z] --subject "件名" [--attach /path] [--dry-run] "本文"
```
`--to`/`--cc`/`--bcc`は複数回指定可。本文は最後の引数か標準入力。`--dry-run`は入力欄に反映するだけで送信せず、自動で下書きを破棄する。

**ログインは実質ノーコストだった**: [[shared_bot_browser]]の過去の知見(Salesforce SAMLセッションはTeamsに引き継がれず別ログインが必要だった)から、Outlookも別ログインが要ると想定していたが、実際はTeamsが既にログイン済みの同一プロファイルで`outlook.office.com`を開いたところ、`login.microsoftonline.com`→`myapps.dentsu.com`のパッシブSSOリダイレクトが**対話操作なしで**完了し、そのまま受信トレイが開いた。サービスによってSSO引き継ぎの有無が異なる(protocol/cookieドメイン次第)ので、新しいサービスを繋ぐ際は「別ログインが要る」と決め打ちせず、まず`connect()`してみてダメなら`login`で対話ログインを促す、の順で試すのが安全。

**実装上の既知の罠(いずれも実機で踏んで修正済み)**:
1. **新規メール作成時、本文欄には既に署名(氏名・会社名・メールアドレス)が自動挿入されている。** 単純に`click()`してから`type()`すると、クリック位置がたまたま署名テキストの途中(実例: `masaki.nakamura@den`と`tsu.co.jp`の間)に来ることがあり、本文が署名の真ん中に挿入されて壊れる。**対策: bodyをクリックした直後に`Meta+ArrowUp`でカーソルを先頭に移動してから入力し、入力後に`Enter`を2回押して署名を下に押し出す**(`lib.js`の`fillBody`参照)。
2. **検索中は上部の検索ボックスの`placeholder`属性が空文字になる**(値が入っているため)。`getByPlaceholder('検索')`で掴もうとすると検索中の状態遷移で見失う。`aria-label="メール、会議、ファイルなどを検索します。"`は検索中も不変なので、そちらで掴むこと(`getByLabel`)。
3. **検索結果0件のときはメッセージ一覧の`[role="listbox"][aria-label*="メッセージ一覧"]`自体がDOMに存在しない**(「何も見つかりませんでした」画面に置き換わる)。ここを「ログインできていない」と誤診断しないよう、`ensureLoggedIn`のログイン判定は検索ボックスの存在(常に表示される)を見る設計にした。メッセージ一覧の有無で判定するのは検索コマンド側(`listMessageItems`)だけにする。
4. **宛先/CC/BCCフィールド**: `aria-label="宛先"`/`"CC"`/`"BCC"`のcontenteditable divに直接。トグルなしで常時表示されている(旧OutlookのCC/BCC表示ボタンは無い)。アドレス入力後は`role="listbox"][aria-label="受信者の選択"]`のサジェストが出るので`Enter`で確定。
5. **添付ファイル**: 「添付ファイル」ボタン→メニュー項目「このコンピューターから選択」をクリックすると同時に`page.waitForEvent('filechooser')`でネイティブファイル選択をインターセプトし`setFiles(path)`。実機で242バイトのテキストファイルが正しく添付・送信されることを確認済み。
6. **下書き破棄**: 「破棄」ボタンを押すと、本文に何か入力済みの場合は「メッセージの破棄」という確認ダイアログ(OK/キャンセル)が追加で出る。`discardCompose()`はこの確認ダイアログも自動でOKする。
7. **ディスパッチャースクリプトのシンボリックリンク越しの実行**: `~/.local/bin/outlook`は`~/Scripts/outlook_cli/outlook`へのシンボリックリンク。bashの`${BASH_SOURCE[0]}`だけで`dirname`を取ると symlink 先ではなくリンク自体のディレクトリ(`~/.local/bin`)になってしまい`node: Cannot find module`になる。`readlink -f`で実体パスに解決してから`dirname`する必要がある(このMacの`readlink`は`-f`対応、[[teams_cli]]の`teams`ディスパッチャは同じ問題を抱えたまま未修正の可能性があるので、そちらを symlink 経由で使う場合は同様の修正が要るかもしれない)。

**2026-08-11に実機テスト済み**: `outlook login`(ログイン済み判定)、`outlook list`(受信トレイ一覧・キーワード検索とも正常)、`outlook read <index>`(件名・差出人・日時・本文取得、検索経由でも動作)、`outlook send`(自分宛てにテキストのみ送信、添付ファイル付き送信、`--dry-run`で未送信確認)を実施。テスト送信した2通(`[テスト] Outlook CLI 動作確認`、`[テスト2] Outlook CLI 本文修正確認`)はテスト後に削除(ゴミ箱に移動、完全削除はしていない)。**他人宛ての実送信テストは行っていない**([[teams_cli]]と同じ方針 — 誤送信リスクを避けるため自分宛て/dry-runのみで検証)。

**How to apply**: 今後Outlookのメール送信・検索・閲覧の依頼が来たら、まず`outlook login`で接続確認してから使う。件名や本文に個人情報・機密情報が入る送信は、実行前に内容を本人に一度提示してから送るのが安全(このCLI自体には確認プロンプトは無い)。

**添付ファイルのダウンロード(2026-09-02追加、`outlook_cli`本体のサブコマンドではなくアドホックスクリプト)**: `list.js`/`read.js`には添付DL機能が無いが、`download_attachment3.js`など未整備の実験スクリプトが`~/Scripts/outlook_cli/`に残っている。正式コマンド化はされていないが、`lib.js`の`connect`/`ensureLoggedIn`/`search`/`openMessageAt`を使い、開いたメッセージ内の`[aria-label*=".xlsx"]`(拡張子は対象に応じて変更)でチップを掴み、`chip.click({button:'right'})`で右クリックメニューを出し、`role="menuitem"`の「ダウンロード」をクリック→`page.waitForEvent('download')`→`download.saveAs(path)`で保存できることを実機確認済み(受発注設定リスト.xlsxのDLで成功、[[qbr_crosstable_monthly_update_process]]参照)。実行時は`export NODE_PATH="$HOME/.local/share/claude-playwright/node_modules"`が必要(outlookディスパッチャは内部でこれを設定しているが、直接lib.jsをrequireする自作スクリプトでは明示的に設定すること)。今後同種の依頼(メール添付をダウンロードして処理)が来たら、この手順をベースに使い捨てスクリプトを都度書けばよい。**2026-09-28、.csv添付でも再確認**([[gbc_salesforce_pitch_import_csv_automation]]のエラーレポートCSV取得時): `[aria-label*=".csv"]`系のセレクタが効かない場合があり、その時は`page.getByText('26 KB', {exact:true})`のようなファイルサイズ表示(添付チップ内に必ずあり、他と重複しない)を起点に`boundingBox()`で中心座標を取得→`page.mouse.click(cx, cy, {button:'right'})`で右クリック、が確実。**注意点**: 検索結果一覧のプレビュー行にも同じ添付名がハイライト付きで表示されており、`getByText(ファイル名)`だと一覧側にヒットして本文側(読みたい方)を掴めないことがある（メッセージ本体を右クリックしてしまい、添付メニューではなくメール自体の「ダウンロード(EML/MSG)」メニューが出る誤操作を繰り返した）。ファイルサイズ表示のように読みたいメール本文にしか出ない文字列を起点にする方が安全。座標は`boundingBox()`が返す値がそのまま`page.mouse.click()`に渡せるCSS px(devicePixelRatio換算不要、換算すると逆にズレる)。

**会社Mac(d14461)への展開(2026-08-11)**: [[photoshop_illustrator_cli_setup]]と同じパターンで`~/Scripts/outlook_cli/`の実体をDropbox `中村正樹/.claude-sync/Scripts/outlook_cli/`に移動し、このMacの`~/Scripts/outlook_cli`はそこへのシンボリックリンクに変更済み(同期後も動作確認済み)。同フォルダに`install.sh`を追加(実行すると`~/Scripts/outlook_cli`と`~/.local/bin/outlook`のシンボリックリンクを作り、`~/.zshrc`のPATHも必要なら追記)。d14461側で実行:
```bash
"/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/Scripts/outlook_cli/install.sh"
```
**重要な注意点 — `lib.js`のPORT/PROFILE_DIRはこのMac(ICPTokyo2022, port 9227, `~/.chrome-profiles/timetree-bot`)決め打ち。** [[shared_bot_browser]]によればd14461の共有ボットブラウザはport 9226・プロファイルは`/Users/d14461/SalesforceExport/browser_profile`と別物なので、install.sh実行後にd14461の`lib.js`冒頭の`PORT`/`PROFILE_DIR`をそのMacの実際の値に書き換える必要がある(install.shはこれを自動化せず警告を出すだけ)。またPlaywright実行環境([[claude_playwright_setup]]の`~/.local/share/claude-playwright`)がd14461にまだ無ければ先にそちらを導入すること。ログインセッション自体はMacごとに別(Dropboxはコードだけ同期、ブラウザのcookieは同期しない)なので、d14461でも`outlook login`は初回に別途試す必要がある(ただしこのMacでは対話操作なしでSSOが通ったので、d14461でも同様に無風で通る可能性がある — 上記の「ログインは実質ノーコストだった」参照)。

**依頼プロンプトをTeams自分チャットに送付済み(2026-08-11)**: [[teams_cli]]の`teams send --self`で、上記のセットアップ手順(install.sh実行→Playwright確認→lib.jsのPORT/PROFILE_DIR書き換え→`outlook login`→`outlook list`→結果報告)をまとめたプロンプトを自分宛てTeamsに送信済み。同じ自分チャットに以前あった別件(会社Mac同期健全性チェックのセットアップ依頼)の古いメッセージは、本人の指示で送信前に削除した(Teamsメッセージの削除はUI右クリック→「削除」、確認ダイアログは無く即座に「このメッセージは削除されました」表示に変わる — 元に戻す操作も可能)。このパターン(個人Mac側で準備→Dropboxに設置→Teams自分チャットに手順プロンプトを送る→会社Mac側のセッションがそれを見て実行)は今後も他のツールの会社Mac展開で再利用できる。

**2026-08-12: OutlookのWeb UIが`outlook.office.com`から`outlook.cloud.microsoft`(新Fluent UIリボン)へ移行し、`attachFiles`が壊れていたのを修正。** [[gbc_weekly_report_kimura_dmd_project]]での他人宛て送信テスト(木村剛さんへのdry-run下書き作成)で発覚: 添付ボタンが「ホーム」タブになく「挿入」タブの中に移動しており、`getByRole('button', { name: '添付ファイル' })`もタイムアウトするようになっていた(このロールでは掴めない — ボタン要素はカスタム属性`label="添付ファイル"`を持つが、Playwrightのaccessible name計算には乗らない模様)。**修正**: `attachFiles()`が先に`getByRole('tab', { name: '挿入' }).first()`をクリックしてから`page.locator('button[label="添付ファイル"]').first()`で掴むように変更済み(`lib.js`)。ログイン判定(`ensureLoggedIn`の検索ボックス`aria-label`頼み)・宛先/CC/BCC欄・件名/本文欄・送信ボタンは新UIでも実地確認上そのまま機能した(壊れていたのは添付だけ)。**他人宛て実送信テストも初めて実施**(dry-runで木村剛さんtkimura@dentsu.co.jp宛、宛先/件名/本文/添付すべて正常に下書き反映を確認、送信はしていない)。

**2026-08-12: 会社Mac(d14461)への実展開・動作確認完了。** `install.sh`実行 → シンボリックリンク作成は無風で成功。Playwright環境(`~/.local/share/claude-playwright`)は既にd14461にも導入済みだったため追加作業不要。

**重要な設計変更 — `lib.js`のPORT/PROFILE_DIRをMac判定で自動化した。** 当初の想定(install.shのガイド文言通り、d14461側で`lib.js`のPORT/PROFILE_DIRを直接書き換える)は誤りだった: このファイルはDropbox実体を両Macがシンボリックリンクで共有している**同一ファイル**なので、片方のMac用の値に固定書き換えすると、Dropbox同期後にもう一方のMacが壊れる。**修正**: `fs.existsSync("${HOME}/SalesforceExport/browser_profile")` の有無でMacを自動判定するようにした(このディレクトリはd14461のSalesforce自動化専用でICPTokyo2022には存在しない)。真ならd14461用(`PORT=9226`, `PROFILE_DIR=~/SalesforceExport/browser_profile`)、偽なら個人Mac用(`PORT=9227`, `PROFILE_DIR=~/.chrome-profiles/timetree-bot`)。**今後この方式のツールをもう一方のMacへ展開する際は、最初からこの自動判定パターンを使うこと(値を手で書き換えさせる設計は再発防止のため避ける)。**

**d14461側のログイン挙動はICPTokyo2022と異なった**: ICPTokyo2022では既存Teams SSOセッションが無風で引き継がれたが、d14461の共有ボットブラウザ(port 9226, `SalesforceExport/browser_profile`)では引き継がれず、`myapps.dentsu.com`のSSOサインイン画面で停止した。ユーザーに前面化したブラウザで手動SSO/MFAを完了してもらってから`outlook login`で再確認 → 成功。`outlook list`で受信トレイ7件の取得も確認済み(件名・差出人・時刻・プレビューとも正常)。

**セットアップ中に判明した誤解**: ユーザーは「Teamsのブラウザが既に立ち上がっている」と認識していたが、実際にはd14461上には自動化用ブラウザが2系統ある: (1) port 9226・`SalesforceExport/browser_profile` = [[shared_bot_browser]]が指す本来の共有ボットブラウザ(Outlook/Salesforceはこちら)。(2) `TeamsExport/browser_profile`(`--remote-debugging-pipe`接続) = `teams_daemon.py`(継続的Teamsデータ収集、[[continuous_data_capture_setup]]参照)専用ブラウザで、パイプ接続のため外部スクリプトから乗り入れ不可・触ると収集デーモンが壊れるリスクがある。ユーザーに確認の上、Outlookはport 9226側で進めることで合意。**ユーザーから新たな依頼: 今後teams_daemon.pyのTeams収集機能をCLI化し、shared_bot_browser(port 9226)経由に統合したい(そうすれば真に「1ブラウザに統合」できる) — Outlook CLI完了後の別タスクとして着手予定。**

**2026-10-12**: 個人Macではアカウント別ブラウザ方針([[browser_account_routing]])により、9227(timetree-bot)から会社用 **9231(dentsu-work-bot)** に移行した。

**予定表への登録(2026-10-14追加、CLI未実装・アドホック)**: `https://outlook.cloud.microsoft/calendar/deeplink/compose?subject=..&startdt=2026-10-27&enddt=2026-11-06&allday=true&location=..` を新規タブで開くと件名・日付・場所が入った作成フォームが開く(終日の enddt は翌日=排他)。本文は `div[role="textbox"][contenteditable="true"]` の last をクリック→`keyboard.insertText`。添付は `button[aria-label="添付"]`→menuitem「このコンピューターから選択」+filechooser。**罠: 添付直後に `browser.close()` するとアップロードが完了せず添付が消える**→ファイル名/「KB」表示が本文に出るまで待つ。保存は「保存」ボタンでフォームが閉じる。確認は週ビューで `[aria-label*="件名"]`(aria-labelに終日/Free等が入る)、ダブルクリックで詳細を開き添付名を確認。カレンダーの `/view/week/YYYY/MM/DD` URLは日付が無視されるので `button[aria-label^="次の週"]` で移動。
