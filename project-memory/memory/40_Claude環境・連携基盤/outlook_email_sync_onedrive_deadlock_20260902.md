---
name: outlook-email-sync-onedrive-deadlock-20260902
description: "d14461(会社Mac)のメール自動同期job(com.nakamura.emailsync)が2026-08-23頃から壊れており、新着メールがparsed_emails.jsonlに反映されていない — OneDrive File ProviderのOSError: Resource deadlock avoided"
metadata: 
  node_type: memory
  type: project
  modified: 2026-09-02T08:13:04.872Z
  originSessionId: 1e53c218-bea5-4ac3-ba3d-613205a64493
---

## 症状
[[local_work_data_export]]で「hourly launchdで自動更新され常に最新」とされている`~/OutlookExport/parsed_emails.jsonl`(d14461/会社Mac)が、2026-08-23 10:41を最後に更新が止まっていた(2026-09-02時点で確認、最新メールが2026-08-20分までしか入っていない)。launchdジョブ自体(`com.nakamura.emailsync`)は生きていて20分おきに実行されているが、毎回`新規メールなし`と結論して終わっている。

## 根本原因
`~/OutlookExport/launchd_stdout.log`に大量の`OSError: [Errno 11] Resource deadlock avoided`が出ている(`sync_power_automate_export.py`がOneDriveに新着メールとして届く`.txt`ファイルを`f.read()`で読もうとして失敗、該当ファイルをskipしてしまうため)。[[continuous_data_capture_setup]]で既知の「OneDrive File Providerがlaunchd起動のプロセスからの読み込みをハングさせる/ロックする」問題の再発と思われる(同メモリでは20分間隔ジョブに`subprocess.run(timeout=)`で対処した実績があるが、`sync_power_automate_export.py`自体にはこの対処が入っていない可能性)。

## 影響
この症状に気づかず`parsed_emails.jsonl`だけを見て「メールが来ていない」と判断すると誤る。2026-09-02、青山さんからの【8月】受発注設定リストのメール(14:41受信)を探した際にこの問題を発見 — jsonlには存在しなかったが、`outlook list`(Outlook Web直接操作、[[outlook_cli]])で見つかった。

**How to apply**: 「最近のメールを確認して」系のタスクで`parsed_emails.jsonl`が数日〜数週間更新されていない場合、即座に「新着なし」と結論しない。まず`ls -la ~/OutlookExport/parsed_emails.jsonl`で更新日時を確認し、古ければ`~/OutlookExport/launchd_stdout.log`の末尾で`OSError`の有無を確認、疑わしければ`outlook list`/`outlook read`(Outlook Web CLI)で直接確認する方が確実。

## 修正済み(2026-09-02、同日中)
ユーザーから「直してください」と明示依頼があり、根本原因を特定・修正した。

**真因**: 既存の`subprocess.run(..., timeout=)`保護(2026-08-03の「Layer B第3版」)自体に見落としがあった。CPythonの`subprocess.run`実装は、タイムアウト時に`process.kill()`した直後、**無制限の`process.wait()`を内部で呼ぶ**(`_check_timeout`経由)。子プロセスがOneDrive File ProviderのuninterruptibleなXPC/Machコールでブロックされたまま死なない場合、SIGKILLは送られてもカーネルが実際に回収するまでこの`wait()`自体が無限に止まる——つまり「timeout=15秒」と書いてあっても親プロセス全体が無期限ハングしうる、という`subprocess.run`自体の設計上の穴。実機で39分・CPU使用率0%のハングを直接再現して確認(`ps`で確認、`kill -9`で強制終了)。過去5回試みた修正(multiprocessing→SIGALRM→subprocess+SIGKILL→常駐daemon→`claude -p`経由)のどれもこの具体的なメカニズムには気づいていなかった。

**修正**: `sync_power_automate_export.py`(email)と`sync_calendar_export.py`(calendar、同一パターンだったため同時に移植)の`read_text_with_retry()`/`read_snapshot()`を、`subprocess.run()`から生の`Popen`+`communicate(timeout=)`に書き換え。タイムアウト時は`kill()`した後の`wait()`にも別途`REAP_TIMEOUT_SECONDS=5`の上限を設け、それでも死なない場合は待つのをやめてその1ファイルを諦める(ゾンビ/孤児プロセスとして放置、無害)。加えてemail側には`RUN_TIME_BUDGET_SECONDS=900`(スクリプト全体の時間予算)も追加し、大量バックログでも次回実行に持ち越せるようにした。

**適用結果**: 手動実行でemail 512件・calendar 11件のバックログを完全処理(email: 3分36秒・スキップ/deadlockエラー0件、calendar: 新規276件・更新1440件)。`launchctl unload`→手動catch-up→`load`で両ジョブとも`LastExitStatus=0`で再稼働確認済み。

**教訓**: `subprocess.run(timeout=)`は「絶対にハングしない」保証ではない——同期の外側にreap用の別タイムアウトが必要。今後同種の「OneDriveタイムアウト保護」コードを書く/レビューする際は、この`process.wait()`無制限待ちの穴がないか必ず確認すること。

**横展開(2026-10-12)**: 書き込み側でも同じ `Resource deadlock avoided` が出る(HDY定点観測でaicon OneDriveへの `shutil.copy2` が失敗。[[hakuhodo_overseas_intel_monitoring]])。launchdで定期実行するジョブがOneDrive(CloudStorage)を読み書きするときは、最初から「別プロセス+timeout+回収待ちの上限」で行い、失敗しても本処理を失敗扱いにせず次回に再試行する作りにする。
