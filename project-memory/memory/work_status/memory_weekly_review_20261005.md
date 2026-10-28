---
name: memory-weekly-review-20261005
description: 2026-10-05分の週次メモリレビュー実施記録(手動運用6週目)
metadata:
  type: project
---

# 週次メモリレビュー 2026-10-05

[[memory_weekly_review_automation]]の手動運用フロー(headlessブロックのため対話セッションで実施)、6週連続。ユーザー依頼「今週のメモリ週次レビューを手動で実施して」により会社Mac(d14461)で実施。

## 実施内容
1. **バックアップ**: `_backups/20261005/`に全263ファイル+work_status(214件)をコピー(launchd自動バックアップは未生成だったため新規作成)。
2. **新規ファイル確認**(前回20260928バックアップとの差分、13件): dentsu_google_workspace_gcp_restriction / feedback_artifact_js_runtime_check / feedback_auto_mode_blocks_shared_file_overwrite / feedback_dify_retrieval_starvation_causes_fabrication / feedback_example_not_scope / feedback_exhaust_access_routes_before_giving_up / feedback_generation_time_diagram_fabrication / feedback_home_infra_no_public_exposure / feedback_jci_pitchlist_check_against_bd_original / feedback_non_disclosed_vs_zero / feedback_verify_xlsx_output_not_just_python_totals / gbc_credentials_slide_bank_project / hakuhodo_overseas_intel_monitoring。
3. **重複チェック**: xlsx検証系(verify_xlsx_output / xlsx_recalc_type_check / openpyxl_formula_sheet_extend)、Dify捏造系2件、relay系2件(claude_relay_system / mac_handoff_relay)を比較 — いずれも別事象・別粒度で真の重複なし。
4. **索引整合性**: リンク切れ0件。索引漏れ3件を発見・追加(mac_handoff_relay / personal_windows_wol_via_crd / powerbi_cover_dashboard_project)。
5. **相互リンク補完**: feedback_dify_retrieval_starvation_causes_fabrication → feedback_generation_time_diagram_fabrication への逆リンクを追加(片方向のみだった)。
6. 削除: 0件。

## 結果
索引漏れ3件修正+相互リンク1件追加。MEMORY.md 88行で健全。

## 追記: 個人Mac(ICPTokyo2022)launchd自動実行分 (2026-10-05)
- 会社Macで本日分を実施済みだったが、Dropbox同期前に個人Macのlaunchdジョブが起動(skip-guardが`_backups/20261005/`を未検知)。
- 本実行で`_backups/20261005/`へcpしたところDropbox競合コピー5件(MEMORY / ai_teams_weekly_digest / cas_csv_download_automation / feedback_ai_tips_content_curation_criteria / feedback_d14461_pip_needs_corporate_proxy)が発生 → 原本とバイト一致を確認のうえ削除し、会社Mac作成のバックアップ状態(263件)に戻した。
- 同期完了後の本体を再確認: MEMORY.md 89行、リンク切れ0件、索引漏れ0件(feedback_handoff_include_verification_prompt / hakuhodo_overseas_intel_monitoring も索引済み)。
- 重複統合・削除・新規メモリ作成: なし(二重処理回避のため)。
- 改善余地: 両Macで同日実行される場合、Dropbox同期遅延でskip-guardが効かないことがある。起動前にDropbox同期待ち、または work_status/memory_weekly_review_<今日>.md の存在チェックを追加するとよい。
