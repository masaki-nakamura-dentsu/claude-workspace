# launchd同期ジョブ(email/calendar/Teams)の健全性チェックと修正

## 2026-07-30T13:30（JST目安）
Status: done
What: ユーザー依頼により、`com.nakamura.emailsync`/`com.nakamura.calendarsync`/`com.nakamura.teamsdaemon`の3つのlaunchdジョブを点検。
- `launchctl list | grep nakamura`：3件とも登録済み（teamsdaemonはPID常駐、他2件はhourly one-shot）。
- 各plistの`ProgramArguments[0]`はいずれも`which python3`の実パス（`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`）と一致、`RunAtLoad`/`StartInterval`も設計通り。plist自体に問題なし、reload不要。
- `~/OutlookExport/sync_power_automate_export.py`：2026-07-29 09:51更新版（RETRY_COUNT=5のリトライ処理入り）になっていることを確認。手動実行して28件新規マージ成功、正常動作。
- ただし`com.nakamura.calendarsync`は最終終了コード1で異常発覚。`sync_calendar_export.py`はOneDriveロック（`OSError: Errno 11`）発生時に**リトライ後も失敗すると1ファイルの読み込み失敗でスクリプト全体がクラッシュ**する設計だったため、2026-07-26以降ほぼ毎時間クラッシュし続け、`PowerAutomateExport/Calendar/`にスナップショットCSVが367件も未処理のまま滞留、`calendar_events.json`は2026-07-29 18:44から更新停止していた。
- 修正: `sync_calendar_export.py`の`main()`ループで`read_snapshot()`呼び出しを`try/except OSError`で囲み、失敗したスナップショットは警告表示のうえスキップ（削除せず次回実行で再試行）するよう変更。メール側スクリプトで既に採用済みの「1件失敗してもクラッシュせず次回に持ち越す」パターンに合わせた。
- 修正後に手動実行し、滞留していた367件を1パスで正常処理（新規1件・更新1048件・変化なし356613件）、`calendar_events.json`は13,828件・2017-07-02〜2036-06-03に更新、スナップショットフォルダも最新1件まで正しくプルーニングされた。
- Teamsデーモンは稼働確認済み（PID生存、直近ポーリング完了ログあり、`teams_messages.jsonl`に2026-07-30 04:00 UTC＝13:00 JST時点の新着メッセージを確認）。
- [[continuous_data_capture_setup]]に今回の調査内容と修正を追記済み。
Next: 特になし（当時）。ステップB（Power Automateカレンダーフローの恒久設定への切り替え）は引き続きユーザー側の未対応事項として残っていた。

## 2026-07-31T08:11〜（このMac=d14461、ユーザー依頼による再調査）
Status: in progress
What: ユーザーから、この`Resource deadlock avoided`が2026-07-29/30に2回・毎回100件超の未処理ファイルを溜めて再発している件と、「20分間隔の定期実行が初回のRunAtLoad以降1回も再発火しない」件（ICPTokyo2022 Mac側で新規ジョブ作成時に発見）の両方について、本格調査を依頼された。このMac（d14461、起動直後・稼働26分）で調査：
- **基本確認**: `launchctl list`で3ジョブとも登録済み。`launchctl print`：calendarsync/emailsyncとも`run interval = 3600秒`（1200秒ではなく、ICPTokyo2022側の変更がまだこちらに反映されていなかった）、**両方とも`runs = 1`**。teamsdaemonはStartIntervalなし（常駐デーモン、RunAtLoad+KeepAlive=false設計で正常）。3ジョブとも`ProgramArguments[0]`は`which python3`の実パスと完全一致、plist自体に構文的な問題なし。
- **`runs=1`の真因を特定**: emailsyncは今朝の起動時（7:46起動）に走り、7:51に正常終了（`last exit code=0`、`新規メールなし`で完了）——想定通り。一方**calendarsyncは7:46に起動したプロセス(PID 1433)が、調査開始時点（8:11）から追加で30分以上経過しても一度も新しいログ行を出力せず、`ps`上は生存し続けていた**（最終的に33分40秒生存を確認して`kill`）。ログファイルの`stat`で最終更新時刻を見ると前日7/30 16:47のまま——つまり今朝のこの実行は、**最初の1ファイルの`open()`呼び出しの時点で、例外も出さずに永久にブロックしていた**（リトライ処理が想定する「Errno 11が出て15回×10秒以内に解消する」パターとは全く別物）。`ps`はstate=S（sleep/待機）のまま。`lsof -p`では対象ファイルのFDは掴んでおらず、`sample`のスタックも`_PyEval_EvalFrameDefault`止まりで詳細不明——ただしI/O待ちで大半の時間CPUを使っていないことは確認。
- **多重起動は原因ではないと確認**: `ps aux`で確認した限り、`sync_calendar_export.py`/`sync_power_automate_export.py`とも常に1インスタンスのみ稼働。ユーザーが懸念していた「前回の実行が終わる前に次が起動して同じファイルを取り合う」という多重起動パターンは、少なくとも今回の観察時点では発生していなかった。
- **OneDrive側の健康状態に実際の異常を発見**: `brctl status`が`self-check failed; error: BRCloudDocsErrorDomain Code=141 "Access denied"`を返す——このMacのOneDrive File Provider（CloudDocs連携）自体が不健全な状態にあることを示す独立した証拠。同じ古いファイル（前日1時台作成、19時間以上経過）を、ハング中のプロセスとは別に手動のPythonワンライナーで読んだところ**一瞬で正常に読めた**——つまり「ファイルが恒久的にロックされている」わけではなく、**起動直後のある種のタイミング/状態でだけ、`open()`が例外も返さず無限にブロックすることがある**というのが実態に近い。メール側（614+38件の未処理.txtが同様に残存）は同じ朝の実行で複数のErrno 11をログに残しつつも5分で完走しており、症状の重さに差がある（カレンダー側のCSVは1ファイル数MBと大きい点、または処理順で最初に当たったファイルの状態次第という可能性）。
- **「20分/1時間に1回しか発火しない」の説明**: launchdは同一ジョブの多重起動をしない設計のため、上記のように前回の実行プロセスが例外も出さず永遠にハングし続けると、次のStartIntervalが来ても新しいインスタンスは起動されない（`runs`カウンタも増えない）。ユーザーがICPTokyo2022側で見た「runs=1のまま」も、同一の仕組み（別原因のハングであれ、実行時間がStartIntervalを超えて詰まっているのであれ）が働いている可能性が高い——launchdのスリープ/レジューム自体の不具合というより、**ジョブ本体が終了しないことの二次的な症状**と考えるのが最も筋が通る。
  - 注: `log show`によるlaunchdの起動履歴の直接確認は、`log`がzshのビルトインに掩蔽されている点（`/usr/bin/log`を使う必要あり）を回避した後も「Could not open local log store: Operation not permitted」でブロックされた（Full Disk Accessが必要、ユーザー側の許可操作が必要なため未実施）。
- **恒久対策として実装済み（コード変更、まだ検証中）**: `sync_calendar_export.py`の`read_snapshot()`と`sync_power_automate_export.py`の`read_text_with_retry()`を、単純なtry/exceptリトライから「`multiprocessing.Process`で1回の読み込み試行ごとにサブプロセスを立て、`READ_TIMEOUT_SECONDS`（カレンダー20秒/メール15秒）で強制`terminate()`/`kill()`する」方式に書き換えた。狙いは、例外を投げずに無限にブロックするケースでもスクリプト本体が確実に前進・終了できるようにすること（単なるリトライ回数・待機時間の調整では原理的に対処不能なため）。カレンダー側は`RETRY_COUNT`を15→5、`RETRY_DELAY_SECONDS`を10→5に短縮（サブプロセスタイムアウト自体が新しい上限になったため）。
- **plist修正**: `com.nakamura.calendarsync.plist`/`com.nakamura.emailsync.plist`の`StartInterval`を3600→1200秒に変更（ICPTokyo2022 Macと統一、バックログが溜まる前により頻繁にリトライさせる狙い）。teamsdaemonはStartIntervalなしの常駐設計のため変更なし。**まだ`launchctl`でreloadしていない**（手動での動作検証を先に完了させてから行う）。
Next: (1) 修正版`sync_calendar_export.py`を手動実行し、巨大バックログ（今朝時点で99件超）を今度こそハングせずに完走できるか確認する（バックグラウンドで実行中、8:20開始）。(2) 同様に修正版`sync_power_automate_export.py`も手動実行して回帰がないか確認する。(3) 両方確認できたら`launchctl unload`→`load`でplist変更（StartInterval=1200）を反映し、1200秒以上経過を待って`runs`が2以上に増え、かつプロセスがハングせず終了していることを確認する。(4) `brctl status`の`Access denied`自体（OneDrive File Providerの不健全な状態）はスクリプト側の対策では解決しないため、ユーザーにOneDriveアプリの再起動または再サインインを検討してもらうよう案内する。(5) 確認が取れ次第[[continuous_data_capture_setup]]・[[power_automate_gotchas]]にも今回の根本原因（真のハング、Errno11の再試行では対処不能）を追記する。

## 2026-08-03T09:31〜 ICPTokyo2022側の2つの追加発見をd14461機で確認・対応
Status: done
What: ユーザーから、ICPTokyo2022機で判明した2つの追加原因（(A)`/usr/bin/python3`がplatform binaryでTCCがFile Provider経由フォルダへのアクセスを無言拒否する問題、(B)ハング対策のmultiprocessing.Process自体がlaunchd経由だと機能しない問題→signal.alarm方式に変更）がd14461機にも当てはまるか確認・修正を依頼された。
- **(A)は該当なし**: calendarsync/emailsync plistの`ProgramArguments[0]`は最初から`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`（python.org版、platform binaryではない）で、`/usr/bin/python3`は使われていなかった。TCCログでの裏付けはFull Disk Access権限がなく今回も確認不可（`log show: Operation not permitted`）。
- **(B)の対応版（signal.alarm方式）はDropbox経由の共有ファイルとして既にこのMacにも同期済み（8/2 10:19付）だったが、実際に`launchctl kickstart -k`で強制実行したところ、同一ファイルで160秒以上進捗なしのハングが再現することを確認**（SIGALRMが自プロセス宛の信号のため、OneDrive File Provider内部のMach/XPC待ちには割り込めない可能性が濃厚）。別プロセスからの`kill -9`は即座に効くことを確認し、「外部からのSIGKILLは効くが自己シグナルは効かない」ことを実証。
- **3度目の修正として、`multiprocessing.Process`ではなく`subprocess.run(..., timeout=)`（posix_spawnベース）に書き換え**（calendar/email両スクリプト）。理由: multiprocessingは複雑なspawn/pickle経路を通るため権限継承が壊れた可能性が高く、subprocessはより単純で標準的なプロセス生成のため。
- **検証**: 対話実行で355件のバックログを6分8秒でハングなく完走（13,844件に更新）。`launchctl kickstart -k`でも両ジョブ即成功。さらに**実際の20分間隔の自然発火を2サイクル分（09:53〜10:33、約40分）監視**し、両ジョブとも`runs`が正常増加(3→4→5)、各実行のetimeは1分未満、`last exit code=0`、stderrログへの新規追記もゼロ（クラッシュなし）——一部の新着ファイルは想定通りErrno 11で一時失敗したが、リトライ→次回持ち越しのグレースフルな処理で完結し、プロセス全体のハング・クラッシュには至らなかった。
- **Teamsデーモンは対象外と確認**: python3パスは元から`/Library/Frameworks/Python.framework/...`で問題なし、OneDriveにも依存しない設計。`teams_messages.jsonl`が7/31から更新停止していた点は、ユーザーから「土日祝もシャットダウンしているので想定通り」と説明があり解決（バグではない）。
- [[continuous_data_capture_setup]]に今回の詳細（3度目の根本原因・修正・検証結果、土日祝シャットダウンの補足）を追記済み。
Next: 特になし。今回の検証は「バックログが実際に存在する状態での自然発火」という、7/31の検証より厳密な条件で行えたため、信頼度は高い。次に同様の症状が出た場合は、まず`ps`でプロセスの異常な生存時間を確認し、それでもハングするようなら根本原因はさらに別（File Provider自体の`brctl status` Access denied状態）にある可能性を疑うこと。

## 2026-07-31T08:47〜 検証完了
Status: done
What: 上記の修正を全て検証完了。
- 手動実行: `sync_calendar_export.py`は99件超のバックログを**2分50秒でハングせず完走**（13,830件・2017-07-02〜2036-06-03に更新、フォルダも正しく1件までプルーニング）。`sync_power_automate_export.py`も正常完了（5件追記）。
- `launchctl unload`→`load`でplist変更（StartInterval 3600→1200秒）を両ジョブに反映。
- **約22〜23分後、両ジョブとも`runs`が1→2に正常に増加したことを実測確認**（08:45calendarsync, 08:46emailsync）。`last exit code = 0`、`state = not running`（ハングして残っていない）、`ps aux`にも該当プロセスは残存なし。calendarsyncの2回目実行ログには`skip`（Errno 11）が1件も出ておらず、完全にクリーンな状態に復帰。
- 結論: 「Resource deadlock avoidedが150秒のリトライでも解消しない」問題と「定期実行が1回しか発火しない」問題は**同一の根本原因**（OneDriveの読み込みが例外も出さず無期限にハングし、launchdが同一ジョブを多重起動しないため次のスケジュールが永久に来ない）で説明がつき、両スクリプトにサブプロセス+ハードタイムアウト方式を実装したことで解消したことを実測で確認した。
- 未対応で残るのは「なぜOneDriveの読み込みがこのMacで時々無期限にハングするのか」というOneDrive自体の健全性問題（`brctl status`が`self-check failed: Access denied`を返す）——スクリプト側の対策で症状は解消したが、根本のOneDrive側の不調自体は直していない。ユーザーには次にOneDriveの調子が悪いと感じた時、OneDriveアプリの再起動・再サインインを検討するよう伝えた。
- [[continuous_data_capture_setup]]・[[power_automate_gotchas]]に今回の根本原因・修正内容を追記済み。
Next: 特になし。次にこのMacでOneDriveの様子がおかしい（`brctl status`がAccess deniedを返し続ける等）と感じたら、OneDriveアプリの再起動/再サインインを検討する。ICPTokyo2022側の「runs=1のまま」も同じ根本原因（プロセスがハングして次のスケジュールが来ない）である可能性が高いので、次にそちらを触る時は同じ観点（`ps`でプロセスが異常に長く生存していないか）で確認するとよい。
