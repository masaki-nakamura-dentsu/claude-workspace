# GBC Intelligence Engine — Agency OS Knowledge Pack生成機能

## 2026-08-26T15:30:00+09:00
Status: done
What: 中村さんから「ChatGPT『Agency OS』Skill向けに、knowledge_index.dbを軽量な
Markdown Knowledge Packへ変換する機能を追加してほしい。月1回のDB更新後に同じ
コマンドで再生成できる仕組みにしてほしい」との詳細依頼(25項目の仕様書付き)。
指示通り、いきなり実装せずまずDB分析を実施し`agency_os_pack_analysis.md`に
まとめた(doc_cards 14,897件・case_records 14,939件の充足率/分布/文字数等)。
分析結果に基づき`generate_agency_os_pack.py`を実装:
- doc_cardsは既存タグ体系(31値、GBCアレココ由来)で分割。国/クライアント/業種は
  充足率が低すぎ(15.8%/13.0%/27.6%)主軸に使えないと判断
- case_recordsはregion(6分類、100%充足)のみで分割。国レベル分割は対応する
  構造化列が実データに無いため不可と判断(依頼書の想定と実データの乖離を明記)
- ファイル分割は固定件数でなくバイト数ベースの貪欲パッキング(目標2MB)
- POC Pack選定は乱数不使用の決定的スコアリング(新しさ/充足率/情報量/出典)+
  層化割当(タグ/リージョンの多様性確保)
- 検証で3件のバグを発見・修正: (1) case_briefs漏洩チェックがtask_briefing_format
  テンプレート自体の正当な出典引用を誤検知→機密フィールドのみに対象を絞って修正、
  (2) sf_id(Salesforce ID)が実は一意でない(14,939件中ユニーク4,111件、最大210件が
  同一ID)と判明、CASE_IDをrow_num(重複ゼロ確認済み)に変更、(3) Markdown構造検証が
  report_text本文中の"---"文字列を誤検知→TYPE:行直前の"---"のみを見る方式に修正
- テストレポート生成時に「タイ」→「タイアップ」誤爆(2026-08-19に判明済みの既知の罠)が
  再発しているのを発見し、negative lookaheadで除外して修正
- POC(doc_cards 1,500件+case_records 2,500件、18ファイル、4.21MB)・
  FULL(全件、27ファイル、24.83MB)とも生成、全Validation項目(ファイル存在/
  0件ファイル無し/case_briefs非漏洩/manifest件数一致/Markdown構造/サイズ上限/
  ID重複無し/UTF-8可読/POC再現性)がOK。テストレポート(Malaysia/B2B・SaaS・CRM/
  Thailand・Event/Influencer/過去案件担当者の5テーマ)も想定通りの結果。
Next: 中村さんへの最終報告(分析結果・分割方法・POC/FULL件数・ファイルサイズ・
選定アルゴリズム・Validation結果・テスト結果・Agency OSへのアップロード推奨・
制約・将来のAPI化移行ポイント)を送信する。
