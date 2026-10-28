---
name: claude-relay-system
description: Mac(会社/個人)↔個人Windows間、および会社Mac↔個人Mac間(2026-09-08拡張、[[mac_handoff_relay]]参照)で、Claude Codeセッション同士が非同期にタスクをやり取りするDropbox同期ファイルベースの汎用中継システム。使い方・運用ルール
metadata:
  node_type: memory
  type: reference
  originSessionId: 402fa28d-f94d-4fa2-8114-e95c5305eca1
  modified: 2026-09-08T07:17:20.767Z
---

## 何のためのシステムか
Remote Control等によるセッション間の直接メッセージ機能が使えない環境で、
「Mac側のClaudeがWindows側のClaudeに作業を依頼し、結果を受け取る」ことを
中村さんの手動コピペ中継なしで行うための仕組み。2026-08-17、
[[gbc_intelligence_engine_project]]のWindows(RTX3090)側backfill作業を
依頼する過程で構築した。**特定プロジェクト専用ではなく、どのプロジェクトの
作業依頼にも使い回せる汎用インフラ。**

## 場所
`中村正樹/.claude-sync/claude_relay/`(Dropbox同期、会社Mac/個人Mac/個人Windows
いずれからもアクセス可能な共有フォルダ[[dropbox_config_sync]]配下)
- `README.md` — プロトコル説明
- `windows_inbox.md` — タスクキュー本体。Mac側Claudeが追記、Windows側Claudeが
  拾って実行しStatus/Resultを書き戻す

## タスクの書式
```
## [YYYY-MM-DDTHH:MM] task-NNN — 短い説明
Project: (対象プロジェクトのDropbox相対パス)
Status: pending | in_progress | done
Instruction: (具体的な作業内容)
Result:
(実行後にここへ記入)
```
1ファイルに時系列で追記していく。過去のタスクは削除せず履歴として残す。

## 起動方式: 手動トリガー(2026-08-17に/loopポーリングから変更)
当初`/loop 5m`でWindows側に定期ポーリングさせていたが、**空振りのたびに
トークンを消費し、履歴が伸びるほど1回あたりのコストも増える**ことが
問題になり中止した。現在の運用:
1. Mac側Claudeが`windows_inbox.md`にタスクを追記
2. 中村さんがWindows側Claude Codeセッションに一言だけ伝える:
   「windows_inbox.md を確認して」
3. Windows側はその一言をきっかけに該当ファイルを開き、`Status: pending`の
   タスクを実行してStatus/Resultを書き戻す

即応性より低トークンを優先する中村さんの明示判断([[feedback_reduce_browser_automation_tokens]]
と同系統の「無駄な定期実行を避ける」志向)。**もし将来またポーリング方式に
戻す場合も、最低20〜30分間隔を推奨**(README.mdに非推奨の参考手順として残してある)。

## Teams Webhook通知(2026-08-17追加)
中村さんはWindows機をあまり見ていないため、Windows側Claudeは以下の場面で
必ずTeams Webhookで一報するルールにした([[teams_webhook_powerautomate]]の
既存Webhook・`run_worker1.ps1`の`Send-TeamsMessage`と同一URLを再利用):
- AskUserQuestion等でユーザーの判断が必要な時
- タスクの完了・失敗を報告する時
- 長時間処理の開始・完了

**注意**: このルールをREADMEに追記したタイミングによっては、既にタスクを
実行中のWindows側セッションが古い版のREADMEしか読んでおらず、その回だけは
通知が飛ばない可能性がある(実際に2026-08-17のtask-001実行時に発生。念のため
中村さんが直接Windows側に一言伝えて確実にした)。ルール変更直後の1回目は
念のため直接申し添えるのが安全。

## 二重実行事故の教訓(2026-08-17)
中村さんがWindows機のチャット窓を2つ同時に開いて、それぞれが独立に
「フル実行に進んでOK」という同じ過去の指示を実行してしまい、同じmanifest
ファイルを取り合う競合が発生した(データ破損は無かったが、混乱と無駄な
二重処理が発生)。**教訓**:
- Windows側には「新規実行前に同種のプロセスが既に動いていないか必ず確認する」
  ことをタスク内で毎回明示する
- Mac側も、既に完了・進行中の内容を古い前提のまま重複してタスク登録しない
  よう、キューに新タスクを書く前に直近のResultを確認する
- なお後日、「python.exeが2つ見える」こと自体はこのプロジェクトの
  venv構成(親プロセスが子プロセスとしてPythonを起動する)による正常な
  状態である可能性も判明した。プロセス数だけで二重実行と断定せず、
  親子関係(ParentProcessId)まで確認するのが確実

## タスク追記時の順序事故(2026-08-27)
`windows_inbox.md`にtask-009を追記する際、Editツールのold_stringに
「対応者: Windows側Claude Code(2026-08-27実施)\n\n---\n\n## [timestamp] task-008」
という文字列を指定したところ、この「対応者: ...(2026-08-27実施)」という
定型の締めくくり文言が複数タスク(task-006/007/008)で繰り返し登場するため、
意図と異なり**1つ前のtask-007の直後・task-008の直前**に新タスクが挿入されて
しまい、時系列が壊れた(task-009が08:14付なのにtask-008(07:29付)より前に
並ぶ)。**教訓**: 時系列の追記型ログ(このファイルに限らず)にEditで挿入する際、
old_stringが持つ「直前の定型文」だけを頼りにすると、同じ定型文が複数箇所に
存在するファイルでは意図しない箇所にマッチすることがある。次のいずれかで防ぐ:
(1)ファイル末尾への追記はEditではなくシェルの`cat >>`を使う、
(2)Editを使う場合は最後のタスク番号のヘッダ行そのもの
(`## [直近のtimestamp] task-NNN — ...`)をold_stringに含めて一意にする、
(3)追記後は必ず`grep -n "^## \["`等でタスク番号の並び順を確認する。
今回は発見後、Pythonスクリプトでブロックを切り出し正しい位置(ファイル末尾)へ
移動して修正した。

## 2026-09-08: 会社Mac⇔個人Mac方向に拡張(自動チェック方式)

ユーザーから「指示しなくてもお互いのMac間で作業の引き継ぎができる仕組みを」との
依頼を受け、`company_mac_inbox.md`/`personal_mac_inbox.md`を新設。Windows版と違い
**手動トリガー不要の自動チェック方式**にした(このDropboxワークスペースでは
会社Mac/個人Macとも日常的にセッションが立つため、セッション開始時の1回読みは
新規ポーリングにならずコストがほぼゼロ、という判断)。グローバルCLAUDE.mdに標準
ルールとして明記。詳細・設計判断・初回動作テストの経過は[[mac_handoff_relay]]参照。
