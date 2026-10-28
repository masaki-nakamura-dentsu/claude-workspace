---
name: feedback_avoid_excessive_background_polling
description: 長時間かかるバックグラウンド処理(bash background task、同期処理など)を待つ際、ps aux/tail等での進捗確認を頻繁に繰り返さない — 完了通知を信頼して待つ
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 67e0e2c6-4e87-48b8-a712-543b0adbcae3
  modified: 2026-08-23T00:50:34.384Z
---

長時間のバックグラウンドタスク(大量ファイル処理、同期スクリプトなど)を待っている間、`ps aux`やログの`tail`で進捗を確認するのは1回のツール呼び出しごとにトークンを消費する。2026-08-23のOneDriveカレンダーCSV整理セッションで、10分程度で終わるはずの処理を何度も(8回以上)ポーリングしてしまい、ユーザーから「このマージ作業は本来トークンを消費しているか」と聞かれる場面があった。

**Why**: バックグラウンドプロセス自体(Bashのrun_in_background、別プロセスとして動くPython等)はOSレベルで動作しトークンを消費しないが、Claude側からの確認(ps aux、cat、tail等のツール呼び出し)は毎回課金対象。ScheduleWakeupやタスク完了通知の仕組みがあるのに、待ちきれずに手動でBashを挟んで様子見すると、その分だけ無駄にトークンを使うことになる。

**How to apply**: 
- バックグラウンドタスクを`run_in_background: true`で開始したら、完了通知(task-notification)が来るまで基本的に何もしない。
- どうしても中間状態を確認したい場合でも、`ScheduleWakeup`の間隔を長め(数分〜10分単位)に取り、間に手動のBash確認を挟まない。
- 処理時間の見積もりが不確かな場合(今回のようにOneDriveのファイル読み込みがネットワーク/File Provider依存で振れ幅が大きいケース)は、こまめに様子を見たくなるが、それこそが最もトークンを浪費するパターンだと自覚する。
- [[feedback_reduce_browser_automation_tokens]](ブラウザ自動操作でのスクリーンショット節約)と同じ「トークン意識」の原則の、バックグラウンドプロセス版。

より広い括りは[[feedback_token_conscious_practices]]参照(2026-08-31統合)。
