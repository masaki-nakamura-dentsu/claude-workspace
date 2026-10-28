---
name: memory_weekly_review_20260824
description: 週次メモリレビュー(2026-08-24分)をインタラクティブセッションで手動完了させた記録。今朝のheadless claude -p実行が「機密ファイル」ブロックで失敗したための代替実行
metadata:
  node_type: memory
  type: work_status
  originSessionId: 86519c28-00e1-439a-bb63-e1ecbd30d66c
  modified: 2026-08-24T00:44:27.000Z
---

Status: done

## 背景
今朝2026-08-24(月)8:30、[[memory_weekly_review_automation]]のlaunchdジョブが起動し`claude -p`のヘッドレス実行でこのプロジェクトのメモリレビューを試みたが、`memory/`ディレクトリへの書き込みが「機密ファイル」としてハーネスにブロックされ、`_backups/20260824/`のバックアップ作成のみで停止した(実処理は未適用)。中村さんの指示で、インタラクティブなClaude Codeセッション(このセッション、書き込みブロックの対象外)が代わりにレビューを完了させた。

## やったこと
1. **バックアップ検証・補完**: `_backups/20260824/`は今朝のバックアップとほぼ一致していたが、当日中に増えた3ファイル(`company_mac_no_admin_no_homebrew.md`、`work_status/memory_weekly_review_d14461_enabled_20260824.md`、`work_status/pdf_shrink_company_mac_setup.md`)が抜けていたため`cp -R`で補完し、完全一致を確認した。
2. **MEMORY.md全145行(当時)+リンク先142ファイルを全読了**。リンク切れ・ファイル欠落は無し。
3. **索引の重複解消**: `power_automate_gotchas.md`・`photoshop_illustrator_cli_setup.md`・`lightroom_cli_setup.md`の3ファイルがそれぞれMEMORY.mdに2行ずつ(古い追記と新しい追記が別々の行として残存)リンクされていたのを、各1行に統合(内容は両方の要約を保持)。
4. **feedbackメモリのパターン統合(新規ファイル2件作成、rule 5に基づく)**:
   - [[feedback_verify_against_ground_truth]] — 「断定・手打ち入力前に一次情報を確認する」という同型の失敗パターンを6件のfeedbackファイル(verify_against_official_totals / verify_message_direction / verify_role_before_assuming / verify_stock_license_per_image / check_surrounding_rows_before_manual_entry / check_dropbox_sync_before_claiming_isolated)から統合。元の6ファイルは削除せず、それぞれに新ファイルへの`[[link]]`を追記。
   - [[feedback_browser_automation_standing_practices]] — ブラウザ自動操作の標準運用6箇条(no-focus-steal / トークン節約 / MFA churn回避 / 送信先検証 / 積極活用 / 並列タブ)を6件のfeedbackファイルから統合。同様に元ファイルは削除せず`[[link]]`のみ追記。
5. **`memory_weekly_review_automation.md`のdescription修正**: 「毎週水曜夜」のまま更新されていなかったのを実際のスケジュール(毎週月曜8:30、2026-08-23変更済み)に合わせて修正。あわせて今回のheadlessブロック→インタラクティブ代替実行の経緯を本文に追記。
6. **MEMORY.mdの索引を更新**: 上記の統合・修正を反映(重複3行→3行に統合、新規2行追加)。最終行数144行(200行上限内)。全リンクが実ファイルと一致することを再確認済み。

## 削除したファイル
**0件。** 内容が完全に別ファイルへ吸収された「真の重複」は見つからなかった(想定通り、143ファイルの大半はプロジェクトごとに異なる事実であり、老朽化・完了済みを理由にした削除も行っていない)。

## 手を付けなかったもの(意図的)
- QBRクラスタ(qbr_0708_rollback_tableau / qbr_2026q2_bridge_chart_and_tableau_pitfalls / qbr_2026q2_null_join_troubleshooting / gbc_qbr_2026_business_instruction_sheet)は内容を精読したが、各セッションで異なる調査結果であり、既に`[[...]]`で適切に相互リンク済みだったため統合不要と判断。
- PPTX関連feedback群(bw_filename_suffix / dont_overwrite_open_pptx / pptx_edit_existing_not_rebuild / pptx_filename_versioning / pptx_prune_unused_sections / pptx_visual_qa_method / bilingual_single_file_pptx、計7件)はテーマは近いが各々が独立して参照される具体的ルールのため、1つに潰すと使い勝手が落ちると判断し統合対象から除外。
- 残り約128ファイルはプロジェクト種別(project-type)の個別事実、またはテーマは近くとも内容が別物のfeedbackであり、指示通り「触らない」を選択。

## 今後の課題(引き継ぎ)
`run_weekly_review.sh`のheadless `claude -p`実行が`memory/`書き込みで毎回ブロックされる問題は未解決。次回月曜(2026-08-31)実行時も同じ症状が出るか確認し、出る場合は[[feedback_unattended_global_config_edit_confirm_first]]と同様にユーザーへAskUserQuestionで回避策を相談すること(詳細は[[memory_weekly_review_automation]]参照)。
