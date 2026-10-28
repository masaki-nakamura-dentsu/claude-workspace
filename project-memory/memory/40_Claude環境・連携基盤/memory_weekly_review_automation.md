---
name: memory-weekly-review-automation
description: 毎週月曜8:30にauto memory(MEMORY.md+memory/)を自動棚卸しする仕組み(2026-08-23に水曜夜→月曜朝へ変更済み)。重複統合と統合済み重複ファイルの削除のみ行い、老朽化削除はしない
metadata: 
  node_type: memory
  type: project
  originSessionId: 8e9cbaae-ac73-44e1-ada8-c4c2e424f32d
  modified: 2026-08-24T01:08:10.874Z
---

2026-08-23、中村さんから「毎セッション開始時に学びを読み込んで同じ間違いをしないように」「週に1回、他の毎週タスクと同じタイミングでメモリMDを全部見直し、古いものは削除・重複はマージ・パターンは統合してアップデートするように、個人Mac/会社Macどちらでも」という依頼を受けて構築。

## セッション開始時の読み込みについて
これは追加対応不要。`MEMORY.md`は毎セッション自動でシステムコンテキストに読み込まれる仕組みが既にあるため([[proactive_project_memory_saving]]参照)。

## 配置場所(2026-08-23 22:xx 移設、詳細は下部「訂正」参照)
`~/MemoryWeeklyReview/`ではなく、Dropbox共有フォルダ`.claude-sync/Scripts/MemoryWeeklyReview/`配下に置いてある(既存のGBCWeeklyReport/adobe_cli/outlook_cliと同じ置き場パターン)。理由: スクリプト本体・プロンプト・重複実行防止マーカー(`state/`)を全てDropbox経由で複数Mac共有するため。`~/Library/LaunchAgents/com.nakamura.memoryweeklyreview.plist`側からこのDropboxパスを直接参照する形にしてあるので、Mac個別のコピーはもう不要。

## 週次自動レビューの仕組み
- **配置場所**: `.claude-sync/Scripts/MemoryWeeklyReview/`(Dropbox経由で全Mac共有)
  - `run_weekly_review.sh`: 本体。`~/.claude/projects/*/memory/MEMORY.md`が存在する全プロジェクトを走査し、各々について`claude -p`にレビューを実行させる
  - `review_prompt_template.md`: `claude -p`に渡す指示書。`{{MEMORY_DIR}}`をsedで実パスに置換して使う
  - `logs/`: 実行ログ(`run_YYYYMMDD.log`)
- **launchd**: `~/Library/LaunchAgents/com.nakamura.memoryweeklyreview.plist`、毎週月曜8:30起動(`Weekday=1, Hour=8, Minute=30`)。当初[[gbc_weekly_report_kimura_dmd_project]]の「毎週水曜夜」に合わせて設計したが、2026-08-23に中村さんから「週報タスクは一旦停止するので、既存のMonday起動ジョブ(`com.nakamura.snsdraft.plist`、月・木8:00起動のSNS下書き生成)に合わせてほしい」と修正指示があり月曜朝に変更。snsdraftとの完全同時起動を避けるため8:00ちょうどではなく8:30にオフセット
- **claude起動方法**: `claude`はPATHに無いため、`~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude`を`sort -V | tail -1`で動的解決(バージョンアップでパスが変わっても壊れない)。`--allowedTools "Read Edit Write Bash Glob Grep"`で非対話実行

## ユーザー承認済みの制約(2026-08-23、AskUserQuestionで確認)
最初の設計案(老朽化・完了済みメモリも削除対象)はユーザーから修正指示が入った:
**削除してよいのは「重複を統合した結果、内容が別ファイルに完全吸収された元ファイル」だけ。老朽化・完了済みを理由にした単独削除は一切禁止。**
パターン一般化(似たfeedbackメモリの統合)は行ってよいが、元ファイルが完全な重複でない限り削除せず、統合後メモリへの`[[link]]`追加に留める。`review_prompt_template.md`の手順3・4・5にこの制約を明記済み。

## 安全設計
- 実行前に必ず`{{MEMORY_DIR}}/_backups/<日付>/`へ全ファイルをバックアップしてから変更する(このプロジェクトはgit管理外のため、これが唯一のロールバック手段)
- 実行結果は`[[teams_webhook_powerautomate]]`の`send_teams()`関数(`~/.zshenv`に定義済み)でTeamsに通知。成功時は変更要約、失敗時はエラー内容を通知
- **既知リスクへの対策**: [[continuous_data_capture_setup]]に記録済みの通り、`claude -p`のlaunchd定期実行はアカウントの週次利用上限に達すると"You've hit your weekly limit"のまま数日間無言で失敗し続けた前例がある。このスクリプトは出力に"weekly limit"等の文字列が含まれるかチェックし、検知したら無言で終わらせずTeams通知する設計にした(同じ「無言の失敗」を再発させないため)

## 訂正(2026-08-23、同日中): 会社Macへの「展開」は実は不要
当初「memoryはMacごとにローカルでDropbox同期外」と誤認して以下の展開手順を書いたが、[[dropbox_config_sync]]を確認した結果は逆だった。**このプロジェクトの`memory/`は`~/.claude/projects/-Users-maxakisan-ICPTokyo2022-Dropbox-----/memory` → `.claude-sync/project-memory/memory/`のシンボリックリンクで、d14461側の`-Users-d14461-dentsuDropbox-Dropbox-----/memory`も同じ物理ファイルを指す設定になっている(2026-07-13確認済み)。**
つまり個人Macのlaunchdジョブが週次で編集するのは、会社Macからも見えるのと同じファイル。**会社Macで追加の指示・設定は不要。**

唯一のリスクは「個人Macが月曜8:30に起動していない週はレビューが飛ぶ」ことだが、これへの保険として`run_weekly_review.sh`に**同一週内の二重実行防止ガード**を追加済み(`_backups/`配下の最新日付を見て5日以内ならスキップ。Dropbox越しにどちらのMacが実行したかに関わらず機能する共有マーカー)。

**2026-08-23、中村さんから「個人Macの起動が不安なので会社Macにも重ねて設置して」と依頼され、実施した。** その際、`~/MemoryWeeklyReview/`一式が丸ごとDropbox同期フォルダ外(`~/`直下)に置かれていることに気づき、`.claude-sync/Scripts/MemoryWeeklyReview/`へ移設した(mv、実行権限も再付与済み)。理由: 同期フォルダ外に置いたままだと会社Macへの展開のたびに手動コピーが要る上、後述のCLAUDE.md自動編集機能の重複実行防止マーカーがMacごとのローカルファイルのままになり、両Macが同じ週に別々にCLAUDE.mdを編集してしまう実質的な穴があった。移設によりこの穴も解消。

### 会社Macでの残作業(この1点のみ、Dropbox同期後にd14461側で実行)
`.claude-sync/Scripts/MemoryWeeklyReview/com.nakamura.memoryweeklyreview.d14461.plist`を用意済み(d14461のユーザー名・Dropboxフォルダ名`dentsuDropbox Dropbox`を前提にパス生成、[[dropbox_config_sync]]記載の命名規則通り)。d14461で以下を実行するだけでよい:
```bash
cp "$HOME/dentsuDropbox Dropbox/中村正樹/.claude-sync/Scripts/MemoryWeeklyReview/com.nakamura.memoryweeklyreview.d14461.plist" ~/Library/LaunchAgents/com.nakamura.memoryweeklyreview.plist
launchctl load ~/Library/LaunchAgents/com.nakamura.memoryweeklyreview.plist
```
d14461にも`~/.zshenv`に`send_teams()`が定義済み([[teams_webhook_powerautomate]]記載の通り2026-08-17設定済み)なのでTeams通知はそのまま動くはず。**未実施(次回d14461でセッションが動いたら確認・実行すること)。**

## 初回自動実行の確認事項(次回このメモリに触れるとき)
- 次回自然発火は2026-08-24(月)8:30。`~/MemoryWeeklyReview/logs/run_20260824.log`とTeams通知が来ているか確認する
- レビュー対象のこのプロジェクトmemory(`~/.claude/projects/-Users-maxakisan-ICPTokyo2022-Dropbox-----/memory/`)が実際にどう変更されたか、`_backups/20260824/`との差分で妥当性を確認する(意図しない大量削除がないか特にチェック)

## 追加(2026-08-23、同日中): CLAUDE.md週次改善ステップを同じジョブに相乗り
中村さんから、直前に行ったセッションJSONL履歴分析→CLAUDE.md改善(→[[feedback_powerbi_track_own_instructions]]の一般化など)を「毎週月曜の他のタスクとともに自動実行して」と依頼され、この`run_weekly_review.sh`(既存のMonday 8:30ジョブ)の末尾に新ステップとして追加した。**ユーザー承認済み(AskUserQuestionで確認): 提案止まりではなく、CLAUDE.mdへの追記まで完全自動で実行してよい。**

- **追加ファイル**(現在は`.claude-sync/Scripts/MemoryWeeklyReview/`配下、下記訂正参照): `review_claude_md_template.md`(claude -pへの指示書)、`state/claude_md_review_marker.txt`(前回実行時刻。UTC ISO8601、初期値2026-08-22T22:03:52Zに設定済み=今回の手動分析完了時刻)、`claude_md_backups/<日付>/`(編集前バックアップ置き場)
- **対象範囲を毎回全履歴でなくマーカー以降の新規セッションのみに限定**(700MB全履歴の再スキャンはコスト高のため)。`find ~/.claude/projects/*/*.jsonl -newermt <マーカー日時>`相当のロジックをテンプレート内でclaude自身に行わせる。
- **CLAUDE.mdの実体パス**は`readlink -f ~/.claude/CLAUDE.md`で毎回動的解決(このMacでは`.../中村正樹/.claude-sync/CLAUDE.md`、シンボリックリンク)。ハードコードしない。
- **安全設計は既存のmemoryレビューと同じ思想**: 編集前に必ずバックアップ、老朽化/重複を理由にした既存ルールの削除は禁止(矛盾する新事実がある場合のみ追記修正)、1回の実行での追記は最大2〜3件、根拠が薄ければ「変更なし」で終える(水増し禁止)。
- **複数Mac重複実行ガード**: マーカーファイルの更新時刻が5日以内なら他マシンが既に今週分を実行済みとみなしスキップ。

**訂正(2026-08-23、私=Claudeがこのセッションで発見・修正)**: 上記は別セッションが書いた内容で、当時`state/claude_md_review_marker.txt`は`~/MemoryWeeklyReview/`(Dropbox同期対象外のホーム直下)にあり、「CLAUDE.mdはDropbox共有だからこのスクリプト自体は個人Macだけでよい」という記述は誤りだった——マーカーがMacごとのローカルファイルのままでは、会社Macに同じ仕組みを後から入れた場合に両Macが同じ週に別々にCLAUDE.mdを自動編集してしまう(重複実行ガードが機能しない)実質的なバグがあった。このセッションで`~/MemoryWeeklyReview/`一式を丸ごと`.claude-sync/Scripts/MemoryWeeklyReview/`(Dropbox共有)へ移設し、`state/`もろとも共有化することで解消した。合わせて会社Mac用launchd plist(`com.nakamura.memoryweeklyreview.d14461.plist`)も同フォルダに用意済み。会社Macでの残作業は本メモリ上部「会社Macでの残作業」参照。
- **次回このメモリに触れるとき確認すること**: 2026-08-24(月)実行後、`~/.claude/CLAUDE.md`(実体)に意図しない追記がされていないか、`.claude-sync/Scripts/MemoryWeeklyReview/claude_md_backups/20260824/CLAUDE.md`との差分で確認する。Teams通知(タイトル「週次CLAUDE.mdレビュー完了」)が届いているかも合わせて確認。会社Macのlaunchd登録(上記コマンド)が実際に行われたかも未確認なので次回チェック。

## 2026-08-24: 初回自動実行が「sensitive file」ブロックで失敗、インタラクティブセッションで手動復旧
本日8:30のlaunchdジョブは起動したが、`claude -p`のヘッドレス実行がこの`memory/`ディレクトリへの書き込みを「機密ファイル」として拒否するガードにブロックされ、バックアップ(`_backups/20260824/`)作成のみで停止した(Teams通知は失敗として届いたはず、要確認)。中村さんの指示で、同日中にインタラクティブなClaude Codeセッション(このセッション)が代わりにレビューを完了させた——インタラクティブセッションはこの種の書き込みブロックの対象外だったため実行できた。**今回やったこと**: バックアップの補完(当日中に増えた新規ファイル2件を追加コピー)、feedbackメモリの重複パターン統合(2件の新規統合メモリ作成、[[feedback_verify_against_ground_truth]]と[[feedback_browser_automation_standing_practices]])、MEMORY.mdの索引重複(同一ファイルへの二重リンク3件)の解消、このファイル自体のdescription更新。削除は0件(真の重複ファイルなし)。詳細は`work_status/memory_weekly_review_20260824.md`参照。

**今後の課題**: `run_weekly_review.sh`のヘッドレス`claude -p`呼び出しがこの「機密ファイル」ガードに毎回引っかかる場合、自動化そのものが機能しなくなる。次回月曜実行時にも同じブロックが出るか確認し、出る場合は([[feedback_unattended_global_config_edit_confirm_first]]と同様に)ユーザーに一度AskUserQuestionで確認して回避策(実行方法の変更、権限設定の調整など)を相談すること。

## 2026-08-24 追記: ヘッドレスブロックは回避不可と確定、手動運用に方針転換
同日中に検証: `~/.claude/settings.json`(実体は`.claude-sync/settings.json`)へ`permissions.allow`で
`Edit(//Users/d14461/.claude/projects/*/memory/**)`等のルールを追加しても、実際に`claude -p`で
このディレクトリへの書き込みを再テストしたところ依然としてブロックされた(「権限が拒否されました」)。
つまりこれは`permissions.allow`では回避不可能な、対話セッション限定のハードブロックと確定した。
回避する唯一の手段は`--dangerously-skip-permissions`(全権限チェックのバイパス)だが、これは
このスクリプト全体の安全策を丸ごと外すトレードオフになるため、ユーザーはこれを避け、
**launchd自動化は維持しつつ、実処理(重複統合)は毎週ユーザーが対話セッションで手動依頼する運用に切り替えることを選択した**(2026-08-24)。

- launchd登録(個人Mac・会社Mac双方)自体は解除していない。バックアップ取得は今後も自動で走り続ける想定(実処理は失敗するが害はない)。
- ユーザー向けの手動実行トリガーとして、Outlookカレンダー(会社アカウント)に毎週月曜8:30の繰り返し予定を登録してもらう方式にした。予定のタイトル・本文(Claude Codeへの依頼文言)は
  `.claude-sync/Scripts/MemoryWeeklyReview/outlook_calendar_reminder_setup.md` にまとめてあり、ユーザー自身がOutlookへ手動登録する(このセッションでは自動登録を試みたがトークン消費が大きいためユーザーの意向で中断し、ファイル渡しに切り替えた)。
- **2026-08-24、同日中に確認**: ユーザーがOutlookカレンダーへ上記の繰り返し予定を実際に登録した(本人からチャットで報告あり)。今後このメモリに触れるときは、その予定をきっかけに毎週手動レビューが実施されているか(またはユーザーから依頼が来るか)を確認すること。

## 2026-09-07: 手動運用3週目、順調に継続中
中村さんから明示的な依頼ではなく「今週分は完了しているか」という質問がセッション開始時に来た。前回バックアップ(`_backups/20260831`)以降1週間分未実施だったため確認の上、ユーザー承認を得てこのセッションで実行。バックアップ(199+124ファイル)→全件棚卸し→重複0件・削除0件、索引漏れ1件(`bigip_zscaler_reconnect_loop_conflict.md`、8/26作成分が2回のレビューで見落とされていた)を発見・修正、という結果。詳細は`work_status/memory_weekly_review_20260907.md`参照。headlessブロックは依然未解決、手動運用のまま3週連続で機能している。次回(9/14想定)も同様に確認すること。

## 2026-10-05: 手動運用6週目
会社Macでユーザー依頼により実施。新規13件確認・重複0・削除0、索引漏れ3件追加、Dify捏造系の逆リンク1件追加。詳細は`work_status/memory_weekly_review_20261005.md`。headlessブロックは引き続き未解決のため手動運用継続。

## 2026-10-12: 手動運用7週目
個人Mac(ICPTokyo2022)でユーザー依頼により実施。この日は8:30の自動起動ログも無く(Macスリープと推定)、会社Mac側の実行記録もなかった。バックアップ533ファイル→新規24件・更新24件を確認。重複0・削除0・索引漏れ0・リンク切れ0。部分重複2組に逆リンク追加(powerbi_ui_label_accuracy→powerbi_browser_only、verify_against_ground_truth→check_latest_state_before_citing_blockers)。run_weekly_review.shは同日、通知を共通送信口teams_notifyへ移行済み([[webhook_autofix_project]])。詳細は`work_status/memory_weekly_review_20261012.md`。

## 2026-10-19: 手動運用8週目
会社Macでユーザー依頼により実施。自動起動ログなし。バックアップ622ファイル→新規44件・更新35件を確認。重複0・削除0、索引漏れ2件追加、逆リンク8箇所(前回持ち越しのpptx相互リンク含む)。詳細は`work_status/memory_weekly_review_20261019.md`。

## 2026-10-21: 週次レビューに圧縮手順を追加(中村さん依頼)
次回(10/26)から、週次レビューでMEMORY.mdとCLAUDE.mdのサイズも点検する。
- MEMORY.md: 20KB超ならフォルダ別の形式(`タイトル:ファイル名`、f_=feedback_)へ圧縮する。全件が実在すること、件数が減っていないことを確認する。([[mcp_on_demand]]の日に41.9→22KBへ圧縮したときと同じ形式)
- CLAUDE.md: 8KB超ならルールは変えずに圧縮し、経緯は [[global_claude_md_full_history]] へ移す。追記は見出しの下に1〜2行で書く(旧書式「Standing rule (added…)」は使わない)。
- 変更したファイル: review_prompt_template.md(手順6b)、review_claude_md_template.md(末尾)、outlook_calendar_reminder_setup.md(依頼文に1行追加)。各ファイルの _bak_20261021_ 版を残してある。
- Outlookに登録済みの予定本文は古いままだが、手順はテンプレートとこのメモリを参照するので、更新しなくても圧縮は実施される。
