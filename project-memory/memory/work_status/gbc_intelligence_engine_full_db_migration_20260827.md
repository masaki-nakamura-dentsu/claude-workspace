# GBC Intelligence Engine — FULL DB適用の移行設計

## 2026-08-27T(個人Mac)
Status: waiting(中村さんの論点確認待ち)
What: task-008(数値グラウンディング精度改善)完了を受け、中村さんが「FULL DB適用の
可否を本格検討」を選択。検討の過程で、新Pipeline(Stage A/B)が旧Pipelineと
スキーマそのものが違う(action不生成・tags不生成等)という、80時間の処理を無駄に
しかねない未解決の論点を発見。いきなり実行せず、`GBC-Knowledge/full_db_migration_design.md`
という設計文書を作成した(推奨方針: 置き換えでなく追加型(v2_*列追加)のスキーマ移行、
ダウンストリーム4ファイルの改修範囲を特定)。詳細は
[[gbc_intelligence_engine_project]]の2026-08-27追記分参照。
Next: 中村さんに`full_db_migration_design.md`末尾の4つのオープンな論点
(tags/country等の優先順位、has_fact=Falseの扱い、QUARANTINEカードの検索露出可否、
gpt_integration再アップロードのタイミング)を確認してから、マイグレーションスクリプト
実装→300件試験→FULL DB実行(qwen3.8:27b、Windows機、約80.7時間)の順に進める。

## 2026-08-27T(同日続き、4論点決定)
Status: done(論点決定は完了、次は実装フェーズへ)
What: `full_db_migration_design.md`の4つのオープンな論点を中村さんと1つずつ確認し
全て決定(①既存タグ/属性値を維持 ②has_fact=Falseは未検証バッジ ③QUARANTINEは
検索・Agency OS Packから除外 ④gpt_integration再アップロードはAgency OS Packと同時)。
設計文書に反映済み。
Next: マイグレーションスクリプト(ALTER TABLE + output_v2 jsonl→doc_cards UPDATE)の
実装から再開。実装後は既存300件サンプルで試験→問題なければFULL DB本実行
(14,597件残、qwen3.8:27b、Windows機、SSD接続、約80時間)。

## 2026-08-27T(同日続き、実装・検証完了)
Status: done(マイグレーション実装・300件検証まで完了、次はFULL DB本実行の可否確認)
What: `migrate_v2_schema.py`新規実装+`search.py`/`webapp/app.py`/
`gpt_integration/query_report.py`/`generate_agency_os_pack.py`の4ファイル改修。
本番DBのコピーで300件サンプルを migrate→4ファイル全てQUARANTINE除外・UNVERIFIED
バッジ・新フィールド優先表示が正しく動くことを実データで確認(Agency OS Pack POC
生成の全Validationも通過)。本番ファイルは一切変更していない(コピー上でのみ検証)。
詳細は[[gbc_intelligence_engine_project]]の2026-08-27追記分参照。
Next: 中村さんにFULL DB本実行(qwen3.8:27b、Windows機、SSD接続、約80.7時間)へ
進んでよいか確認してから着手。完了後はmigrate_v2_schema.pyを本番DBに適用→
Agency OS Pack再生成+gpt_integration同時再アップロード、の順。

## 2026-09-30T06:53:59Z
Status: done(300件サンプル分の本番適用のみ完了、FULL DB本実行は引き続き未着手)
What: `migrate_v2_schema.py --allow-production`を本番DBに適用完了(バックアップ後、
コピーでの試験実行→問題なし確認の上で実行)。`generate_agency_os_pack.py`が
クラッシュしていた根本原因(`v2_quality_bucket`列の不存在)を解消し、poc/full
両モードの再生成・全Validation通過を確認。詳細は新規ログ
[[gbc_intelligence_engine_credentials_pack_permanent_fixes_20260930]]参照。
Next: FULL DB本実行(残14,597件、qwen3.8:27b・Windows機・約80時間)は今回未着手の
まま、引き続き中村さんの判断待ち。
