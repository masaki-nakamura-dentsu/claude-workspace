---
name: mac-handoff-relay
description: "会社Mac(d14461)⇔個人Mac(ICPTokyo2022)⇔個人Windowsの3台間でDropbox共有キューによりタスクを引き継ぐ仕組み(2026-09-08新設、同日中にWindowsも統合)。inboxの自動チェックは無指示で行うが、2026-09-11訂正により実行前にユーザー許可が必要"
metadata:
  node_type: memory
  type: reference
  originSessionId: unknown
  modified: 2026-09-11T08:15:16.887Z
---

2026-09-08、Salesforceレポート追加作業([[sf_reports_qbr_download_automation]])で
「会社Mac側`reports_config.py`は更新したが、個人Mac側`reports_config.js`は次回
個人Macセッションが立ち上がるまで反映できない」という手動引き継ぎの手間が発生し、
ユーザーから「指示しなくてもお互いのMac間で作業の引き継ぎができる仕組みを作って」と
明示依頼があり構築。

## 何が既にあったか
- [[dropbox_config_sync]]: `memory/`フォルダ自体は既に会社Mac/個人Mac間でDropbox
  symlink同期済み(2026-07-08〜)。ただし「知識・事実」の置き場であり、
  「pending/done」のような操作的な一時状態を書く場所ではない
  (MEMORY.mdの「What NOT to save」にも明記されている)。
- [[claude_relay_system]]: Mac→Windows方向の非同期タスクキュー
  (`.claude-sync/claude_relay/windows_inbox.md`)が既にあったが、**手動トリガー方式**
  (ユーザーが「windows_inbox.md を確認して」と一言言わないと拾われない)だった。
  理由は`/loop`ポーリングのトークン消費を避けるため。

## 今回作ったもの
`.claude-sync/claude_relay/`(既存フォルダ)に2ファイル追加:
- `company_mac_inbox.md` — 会社Mac(d14461)宛てタスクキュー
- `personal_mac_inbox.md` — 個人Mac(ICPTokyo2022)宛てタスクキュー

書式はwindows_inbox.mdと同じ(`## [timestamp] task-NNN` / `Project` / `Status` /
`Instruction` / `Result`)。詳細・運用ルールは`claude_relay/README.md`に集約。

## Windowsと違い「自動チェック方式」にした理由
Windowsは独立したプロジェクトとして起動されるため定期ポーリングでしかチェック機会が
無く、それがトークン消費として問題になった。一方、会社Mac/個人MacはどちらもこのDropbox
ワークスペース(`中村正樹/`)で日常的にセッションが立ち上がるため、「セッション開始時に
inboxファイルを1回読む」のは新たなポーリングではなく、**既に起きているイベント
(応答の生成)に相乗りするだけ**でコストがほぼゼロ。[[work_status_protocol]]で
「10分おき」から「毎応答」に変えた時と同じ考え方。よってMacの2台間だけは
「ユーザーの指示なしに自動実行」に踏み切った。

## 具体的な動作(グローバルCLAUDE.mdに標準ルールとして明記済み)
1. このDropboxワークスペースで作業を始めるとき、`whoami`または作業ディレクトリの
   Dropboxフォルダ名(`dentsuDropbox`→会社Mac、`ICPTokyo2022 Dropbox`→個人Mac、
   [[reference_mac_naming]])で自分がどちらのMacかを判定。
2. 自分宛てのinboxファイルの`Status: pending`タスクを確認。
3. あれば、ユーザーの指示を待たずに`Status: in_progress`にしてから実行し、
   完了後`Status`(done/failed)と`Result`を書き戻す。
4. 二重実行防止: 既に`in_progress`かつタイムスタンプが直近30分以内なら
   手を出さず、ユーザーに一言触れるだけに留める(windows_inboxの
   「二重実行事故の教訓」と同じ配慮)。
5. pendingが無ければ何も報告せず、通常の作業をそのまま進める
   (空振り報告はノイズになるため)。

## 完了通知について
既存のグローバルルール(teams_webhook — [[teams_webhook.md]]相当、d14461側は
このファイル未確認だが同種の仕組みがある前提)により、タスク完了時は基本的に
その応答自体がユーザーに見える形になる。Windows版のような「Teams Webhookで
必ず一報」は今回のMac↔Mac版には明示追加していない(会社Mac/個人Macはユーザーが
比較的頻繁に見ているという前提の違いから、今回は必須にしなかった)。もし
「Macの引き継ぎ結果にも気づきにくい」という声が出たら、windows_inbox.mdと同じ
Teams Webhook通知ルールをこちらにも追加すること。

## 初回動作テスト(2026-09-08)
このメモリを作った同じセッションで、`personal_mac_inbox.md`にtask-001として
実際の保留タスク(Salesforceレポート3本を`reports_pipeline_personal/reports_config.js`
に追記する作業)を投入した。次回個人Macセッションが立ち上がった時点で本当に
自動拾い上げされるかどうかが実地検証になる — 次回個人Macセッション時、
このメモリと`personal_mac_inbox.md`のtask-001の`Status`が実際に`pending`から
変わっているかを確認すること。もし拾われていなかった場合、グローバルCLAUDE.mdの
指示が実際にセッション開始時点で読まれ、行動に反映されているかを疑う
(仕組み自体の設計ミスというより、モデルがCLAUDE.md冒頭の長いルール一覧の中で
見落とした可能性を優先して調査する)。

## 運用上の注意点(2026-09-09発見): Result記入とStatus更新の不一致リスク

`personal_mac_inbox.md`のtask-002(不要レポート3本の削除依頼)を会社Mac側で確認したところ、
`Result`欄には既に「3本追記完了、計21本に一致」という文面が入っていたが、これは
**task-001(3本追加)の結果をそのまま複製したもの**で、task-002本来の依頼内容(3本削除)
とは一致していなかった。しかも`Status`は`pending`のままで、`done`に更新されていなかった。

**教訓**: タスク実行側は`Result`を書く際、必ずその回のタスクの`Instruction`と
突き合わせて内容が対応しているか確認してから記入すること(前タスクのブロックを
コピーして書き始めた際の消し忘れ等が原因と推測される)。**確認する側も、`Status`
だけでなく`Result`の内容が`Instruction`と整合しているかを見ること** —
`Status: pending`のままなら自動チェックの仕組み上は再実行されるので実害は
限定的だが、`Status: done`なのに`Result`が的外れ、というケースは検知できずに
見逃される恐れがあるため特に注意。

## Windowsも統合(2026-09-08、同日中)
上記の初回動作テスト実施後、ユーザーから「Windowsも同じ仕組みにして」と明示依頼が
あり、`windows_inbox.md`(従来は手動トリガー方式、[[claude_relay_system]]参照)も
同じ自動チェック方式に統一した。グローバルCLAUDE.mdの該当ルールと
`claude_relay/README.md`を更新済み。個人Macと個人Windowsは同じDropboxフォルダ名
(`ICPTokyo2022 Dropbox`)を共有するため、機種判定はユーザー名(`maxakisan`/`maxak`)
かMac/Windowsのプロジェクトキー形式差([[dropbox_config_sync]])で行う点に注意。
Windowsは独立プロジェクトとして起動されることが多く、このDropboxワークスペース内で
セッションが立ち上がった時にしか拾えないため、Mac2台に比べ実際の即応性は低くなる
可能性がある(運用上の留意点として申し送り済み、取りこぼしが目立てば手動トリガー
併用や`/loop`再検討)。

## 2026-09-11訂正: 実行前にユーザー許可を取るよう変更(自動チェックは維持)

ユーザーから「今後、個人Macも会社Macもそれぞれに対してのタスクキューがあった場合は、
実行の前にタスクの表示と実行していいかの許可を取ってください」と明示指示があり、
上記「ユーザーの指示を待たずに`Status: in_progress`にしてから実行」という設計を
訂正。**セッション開始時にinboxの`pending`タスクを自動でチェックする部分は従来通り
維持**(これ自体は新たなポーリングではなく既存イベントへの相乗りなので変更不要)。
変更点は実行の手前だけ: pendingタスクが見つかったら、その内容(id+概要)をユーザーに
提示し、実行してよいか確認してから着手する。承認が出るまで`Status: in_progress`への
更新も実行そのものも行わない。グローバルCLAUDE.mdの該当ルールも同時に訂正済み。
Windows側(`windows_inbox.md`/[[claude_relay_system]])にも同じ考え方を適用すること
(会社Mac/個人Mac/個人Windowsの3台共通ルールのため)。

## 2026-09-15: README.mdの記述ズレを修正(実質的な仕組みは既存のまま)
中村さんから「Windowsもセッション開始時に自動で残タスクをチェックする仕組みにして」と
依頼あり、確認したところ**この仕組み自体は2026-09-08(Windows含め統合)+2026-09-11
(実行前ユーザー許可)で既にグローバルCLAUDE.mdに明記済み**だった。ただし
`claude_relay/README.md`本文が2026-09-11の許可制訂正を反映しておらず、「見つかったら
ユーザーの指示を待たずにそのまま実行」という古い記述のままだったため、これを修正
(自動チェックはそのまま/実行前に許可を取る、に訂正)。CLAUDE.md自体は正しかったので
変更不要。3台ともCLAUDE.md/memoryはDropbox symlink同期済み([[dropbox_config_sync]])
なので、Windows機のsymlinkさえ生きていれば次回セッションから自動で機能するはず。
