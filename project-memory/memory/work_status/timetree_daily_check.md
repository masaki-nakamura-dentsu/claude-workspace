# TimeTree/同期 日次自動チェック

## 2026-08-09T07:33:00+09:00
Status: done
What: 日次無人チェックジョブ実行。TimeTree🏠カレンダーの「父夜いない」登録漏れなし(60日先まで29件の夜予定候補を確認、golf/モンゴル旅行/ベトナム出張は既知の例外パターンとして妥当に除外)。Facebook同期は22h55m経過でstale閾値(24h)未満のため回復スクリプト未実行。メール・カレンダー同期は数分前更新で正常。SyncDaemonも稼働中(前日レポートの停止懸念は解消)。問題なしのため通知は送信せず。レポート: ~/TimeTreeCheck/reports/report_2026-08-09.md
Next: —

## 2026-08-13T07:40:00+09:00
Status: done
What: 日次無人チェックジョブ実行。TimeTree🏠カレンダーの「父夜いない」登録漏れなし(60日先まで23件の夜予定候補を確認、いずれも登録済みか、モンゴル出張9/17-25・ベトナム出張10/1として妥当に除外)。tt_scrape_weeks.jsが共有ボットブラウザのpages()[0](Gmailタブ)を誤って掴む既存バグに遭遇したため、既存TimeTreeタブを探して使う安全版(tt_scrape_weeks_safe.js)をその場で作成して回避(他タブへの干渉なし)。Facebook・メール・カレンダー同期はいずれも直近30分以内更新で正常、回復スクリプト実行は不要だった。問題なしのため通知は送信せず。レポート: ~/TimeTreeCheck/reports/report_2026-08-13.md
Next: tt_scrape_weeks.jsの本体(pages()[0]決め打ち)を次回触るタイミングでtt_scrape_weeks_safe.js相当の既存タブ検索ロジックに恒久修正しておくと安全(現状は都度safe版をその場で作る運用)。

## 2026-08-15T07:10:00+09:00
Status: done
What: ユーザー依頼によりTimeTree同期を手動チェック(8/13以降、日次無人ジョブのレポートが途絶えていた)。ログ確認の結果、無人ジョブ失敗の原因は「週間利用上限到達(You've hit your weekly limit)」と判明 — [[continuous_data_capture_setup]]に根本原因として追記済み、コード側の問題ではないため修正不要。共有ボットブラウザ(9227)がconnectOverCDPでハングしていたため再起動して復旧(ログイン状態は維持)。TimeTree🏠カレンダーとOutlook実スケジュール(calendar_events.json)を8/3〜11/8の範囲で突合し、10/1(ANA便)・10/23(荒木さん飲み会)・11/6(ベトナム交流会)の3件を実質的な「父夜いない」登録漏れ候補として検出、ユーザーに登録要否を確認中。9/17-25のモンゴル出張は「父モンゴル？」の複数日イベントで概ねカバー済みと判断(ただし週表示スクレイピングの制約で終了日までの完全な網羅は目視未確認)。
Next: ユーザーの回答待ち — 3件の登録可否。あわせて、次回このファイルを触るセッションでtt_scrape_weeks.jsの恒久修正(safe版へのマージ)を検討。

## 2026-08-15T07:40:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。20件の夜の予定候補中、5日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-15T07:42:13+09:00
Status: done
What: 無人日次チェック(Python版)実行。20件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-15T08:15:00+09:00(人間セッション)
Status: done
What: ユーザーの回答を受け、10/23・11/6に「父夜いない」「🍙父ランチいらない」を登録(10/1は不要と判断され見送り)。さらにユーザー依頼で日次無人チェックのアーキテクチャを刷新: `claude -p`ベースの`daily_check_prompt.md`(タスク2・3は`~/SyncDaemon`と重複、タスク1もLLM判断が実質不要)を廃止し、`~/TimeTreeCheck/timetree_check.py`という純Pythonスクリプトに置き換え(`run_daily_check.sh`から直接呼び出し、Claudeトークン消費ゼロ)。あわせてTimeTree週表示スクレイピングの`--lndlxo2`(複数日イベントのスパン幅)を発見し、`天晴・満天長崎`や`父モンゴル？`のような複数日イベントの全期間を正しく認識できるよう`tt_scrape_weeks.js`を修正(旧`tt_scrape_weeks_safe.js`のタブ選択ロジックもここに統合し、重複ファイルを解消)。手動実行で検証済み(上の2件のログがその実行記録)、修正後は10/1(ユーザー判断待ちの1件)のみが残ることを確認。詳細は[[continuous_data_capture_setup]]・[[timetree_web_automation]]に記録済み。
Next: 次回7:30の実launchd起動で無人動作を確認(まだ手動実行でしか検証していない)。

## 2026-08-16T07:30:51+09:00
Status: done
What: 無人日次チェック(Python版)実行。20件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-17T07:31:37+09:00
Status: done
What: 無人日次チェック(Python版)実行。20件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-18T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。19件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-19T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。19件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-20T07:56:53+09:00
Status: done
What: 無人日次チェック(Python版)実行。19件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-21T07:38:32+09:00
Status: done
What: 無人日次チェック(Python版)実行。17件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-22T07:30:15+09:00
Status: done
What: 無人日次チェック(Python版)実行。16件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-23T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。16件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-24T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。19件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-25T07:36:09+09:00
Status: done
What: 無人日次チェック(Python版)実行。19件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-26T07:30:26+09:00
Status: done
What: 無人日次チェック(Python版)実行。17件の夜の予定候補中、4日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-27T07:30:36+09:00
Status: done
What: 無人日次チェック(Python版)実行。16件の夜の予定候補中、9日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-28T07:38:03+09:00
Status: done
What: 無人日次チェック(Python版)実行。15件の夜の予定候補中、8日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-29T07:49:32+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: ERROR page.goto: net::ERR_INTERNET_DISCONNECTED at https://timetreeapp.com/calendars/JHwx6a86DdDo
Call log:
  - navigating to "https://timetreeapp.com/calendars/JHwx6a86DdDo", waiting until "domcontentloaded"


Next: —

## 2026-08-30T07:37:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。14件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-08-31T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。15件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-01T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。14件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-02T08:00:23+09:00
Status: done
What: 無人日次チェック(Python版)実行。13件の夜の予定候補中、13日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-03T07:30:25+09:00
Status: done
What: 無人日次チェック(Python版)実行。13件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-04T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。19件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-05T07:33:14+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-06T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-07T07:30:28+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-08T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-09T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-10T08:05:47+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-11T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-11T07:37:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-12T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-13T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-14T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-15T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。24件の夜の予定候補中、4日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-16T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。27件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-17T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。26件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-18T07:30:59+09:00
Status: done
What: 無人日次チェック(Python版)実行。25件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-19T07:30:23+09:00
Status: done
What: 無人日次チェック(Python版)実行。26件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-20T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。26件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-21T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。26件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-22T07:30:23+09:00
Status: done
What: 無人日次チェック(Python版)実行。30件の夜の予定候補中、5日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-23T07:57:16+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: ERROR page.goto: net::ERR_INTERNET_DISCONNECTED at https://timetreeapp.com/calendars/JHwx6a86DdDo
Call log:
  - navigating to "https://timetreeapp.com/calendars/JHwx6a86DdDo", waiting until "domcontentloaded"


Next: —

## 2026-09-24T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。27件の夜の予定候補中、5日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-25T07:32:42+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: ERROR page.goto: net::ERR_INTERNET_DISCONNECTED at https://timetreeapp.com/calendars/JHwx6a86DdDo
Call log:
  - navigating to "https://timetreeapp.com/calendars/JHwx6a86DdDo", waiting until "domcontentloaded"


Next: —

## 2026-09-26T07:31:31+09:00
Status: done
What: 無人日次チェック(Python版)実行。24件の夜の予定候補中、6日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-27T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。25件の夜の予定候補中、7日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-09-28T07:34:38+09:00
Status: done
What: 無人日次チェック(Python版)実行。27件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-29T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。26件の夜の予定候補すべて登録済みまたは既知の理由で除外、問題なし。
Next: —

## 2026-09-30T07:30:19+09:00
Status: done
What: 無人日次チェック(Python版)実行。25件の夜の予定候補中、1日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-01T08:11:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: chrome did not come back after restart (first failure: ERROR page.goto: Timeout 30000ms exceeded.
Call log:
  - navigating to "https://timetreeapp.com/calendars/JHwx6a86DdDo", waiting until "domcontentloaded"

)
Next: —

## 2026-10-02T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。27件の夜の予定候補中、5日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-03T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。27件の夜の予定候補中、5日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-04T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。28件の夜の予定候補中、6日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-05T07:37:48+09:00
Status: done
What: 無人日次チェック(Python版)実行。31件の夜の予定候補中、8日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-06T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。30件の夜の予定候補中、8日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-07T07:31:24+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: ERROR locator.click: Error: strict mode violation: locator('button:has-text("今日")') resolved to 2 elements:
    1) <button type="button" class="_1fj3li70">今日</button> aka locator('[data-test-id="calendar-pagination"]').getByRole('button', { name: '今日' })
    2) <button type="button" class="jmccnr1">…</button> aka getByRole('button', { name: '今日の予定を教えて' })

Call log:
  - waiting for locator('button:has-text("今日")')


Next: —

## 2026-10-08T08:03:27+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: ERROR browserType.connectOverCDP: Timeout 30000ms exceeded.
Call log:
  - <ws preparing> retrieving websocket url from http://127.0.0.1:9227


Next: —

## 2026-10-09T08:37:42+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: ERROR page.goto: Timeout 30000ms exceeded.
Call log:
  - navigating to "https://timetreeapp.com/calendars/JHwx6a86DdDo", waiting until "domcontentloaded"


Next: —

## 2026-10-10T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。28件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-11T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。28件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-12T07:30:54+09:00
Status: done
What: 無人日次チェック(Python版)実行。28件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-13T07:30:19+09:00
Status: done
What: 無人日次チェック(Python版)実行。28件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-14T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。27件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-15T07:30:21+09:00
Status: done
What: 無人日次チェック(Python版)実行。26件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-16T07:34:13+09:00
Status: done
What: 無人日次チェック(Python版)実行。25件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-17T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。24件の夜の予定候補中、3日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-18T07:30:45+09:00
Status: done
What: 無人日次チェック(Python版)実行。スクレイピング失敗: e="button" class="_1fj3li70">今日</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
      - waiting 100ms
    29 × waiting for element to be visible, enabled and stable
       - element is not visible
     - retrying click action
       - waiting 500ms


Next: —

## 2026-10-18T07:34:54+09:00
Status: done
What: 無人日次チェック(Python版)実行。24件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-19T07:49:30+09:00
Status: done
What: 無人日次チェック(Python版)実行。24件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-20T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。23件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-21T07:38:59+09:00
Status: done
What: 無人日次チェック(Python版)実行。21件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-22T07:30:22+09:00
Status: done
What: 無人日次チェック(Python版)実行。20件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-23T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。19件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-24T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-25T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-26T07:30:19+09:00
Status: done
What: 無人日次チェック(Python版)実行。18件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-27T07:30:54+09:00
Status: done
What: 無人日次チェック(Python版)実行。17件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち

## 2026-10-28T07:30:20+09:00
Status: done
What: 無人日次チェック(Python版)実行。16件の夜の予定候補中、2日で「父夜いない」登録漏れ候補を検出、レポート保存済み。
Next: ユーザーの登録可否確認待ち
