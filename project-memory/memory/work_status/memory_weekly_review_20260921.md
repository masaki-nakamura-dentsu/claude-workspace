---
name: memory_weekly_review_20260921
description: 週次メモリレビュー(2026-09-21分)の実施記録
metadata:
  node_type: memory
  type: work_status
  originSessionId: subagent-memory-weekly-review-20260921
  modified: 2026-09-21T00:00:00.000Z
---

Status: done

## やったこと
1. **バックアップ**: `_backups/20260921/`を新規作成し、`_backups`自身を除く直下の全`*.md`(243ファイル)を`cp`でコピー(初回`find -exec cp`がこの環境で0件ヒットする問題があり、glob展開`cp *.md`に切り替えて解決)。
2. **前回(2026-09-14)レビュー記録を確認**: 主要クラスタ(ブラウザ自動操作6箇条、トークン意識6事例、検証系6事例、PPTX、Mac間同期・引き継ぎ等)は既に多層統合済みで追加統合不要、との結論を確認。
3. **今回の重複調査は差分ベースで実施**: 2026-09-14以降に更新・新規作成されたファイル(22件: feedback_agency_os系2件、feedback_dont_recommend_defunct_orgs、feedback_timetree_no_specific_content、feedback_web_file_upload系、mac_handoff_relay、openclaw_setup、feedback_ai_tips_slide_title系、feedback_manga_natural_plot_logic、feedback_sudo_and_mas_install_limitations、globalq_4koma_manga_project、sf_reports_qbr_download_automation、anime_ip_search_dashboard_project、chatgpt_web_automation、currencysort_app_project、feedback_reduce_browser_automation_tokens、feedback_token_conscious_practices、mfk_photos_posting_access_gap、shared_bot_browser、feedback_executive_deck_disclosure_and_brevity、gbc_intelligence_engine_project、masaki_childhood_mexico_years、timetree_web_automation)を全て読み、既存メモリとの重複有無を確認した。
4. **MEMORY.mdの索引整合性を機械チェック**: 直下の全`.md`ファイル名(242件、MEMORY.md自身を除く)と、MEMORY.md本文中のMarkdownリンクを突合。リンク漏れは`feedback_browser_automation_no_focus_steal.md`のみだったが、これは2026-08-24統合以降「個別事例は統合先(`feedback_browser_automation_standing_practices.md`、索引済み)経由でのみ参照する」という既存方針通りの意図的な省略と判断し、追加索引はしなかった。
5. **軽微な相互参照追加(唯一の内容変更)**: `feedback_sudo_and_mas_install_limitations.md`(2026-09-16新規、「Bashツールは対話的sudo/大容量mas installを実行できない」というツール側の一般的制約)と`company_mac_no_admin_no_homebrew.md`(2026-08-23作成、「会社Macにはそもそも管理者権限が無い」という機種固有の制約)が、テーマが近いのに相互リンクが無かったため、両ファイルの末尾に一文ずつ「関連: [[...]]」を追加して違いを明記(和集合・情報欠落なし、削除なし)。

## 削除したファイル
**0件。** 真の重複は見つからず、老朽化・完了済みを理由にした削除も行っていない。

## 手を付けなかったもの(意図的)
- gbc_intelligence_engine_project.md(2296行)は突出して長いが、単一プロジェクトの時系列事実記録であり他メモリとの重複ではないため、手順3の「重複統合」の対象外として現状維持。
- globalq_4koma_manga_project.md / feedback_manga_natural_plot_logic.md は本編ノウハウとプロジェクト事実で適切に分離済み、統合不要。
- Agency OS関連の新規feedback3件(thinking model必須/SKILL.md多拠点同期/廃止組織を案内しない)はいずれも既存クラスタと異なる新規の教訓であり、無理な一般化はしなかった。

## 今後の課題(引き継ぎ)
特になし。次回(2026-09-28相当)も差分ベースの確認を継続。
