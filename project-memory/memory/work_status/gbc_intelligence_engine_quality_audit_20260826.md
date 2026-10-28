# GBC Intelligence Engine — Knowledge Card品質監査(300件サンプル)

## 2026-08-26T16:30:00+09:00
Status: done
What: 中村さんから、Agency OS Knowledge Pack(前セッションで生成)のKnowledge Cardに
「元資料に無い解釈・一般化・推奨行動の混入」「数値/単位/通貨/年月の抽出誤り」の
懸念があるとの指摘。全14,897件をいきなり再生成せず、まずリスクベースで300件を
抽出して監査するよう明示指示があった(既存DBは読み取り専用・変更禁止)。

`audit_select_sample.py`を新規実装し、doc_cards 14,897件から7つのリスクカテゴリ
(numeric/market_country/success_story/credential_source/mass_source/
strong_action/untagged、各floor=30件)で層化抽出+数値/単位/通貨/年号の
機械的整合性チェックを実施(`audit_sample.json`)。mass_sourceの閾値は当初15
→実データの93%が該当してしまい無意味と判明→100に調整(21ファイル・36%に
絞り込み)。数値チェックで16件が自動フラグされ、うち人手検証で真の不整合5件・
チェッカー自体のバグ(万/百万混同・カンマ境界)5件・評価不能6件と判明。

その後、約280/300件を**人手で1件ずつevidence_quoteと生成4フィールド
(knowledge/why_it_matters/when_to_use/action)を突き合わせて精読**。
主要発見: Knowledgeフィールド自体はおおむね元資料に忠実だが、WHY/WHEN/ACTIONの
体感8〜9割が元資料に無い一般化・因果断定・プレゼクリプティブな推奨を含む
(1件の成功事例→再現可能な法則であるかのような一般化、という依頼書が
懸念していたパターンそのものを多数確認)。ACTIONフィールドにヘッジ表現
(「可能性がある」等)を含むカードはサンプル300件中わずか1件(0.3%)という
機械的集計も取得。重大な捏造例も複数発見(北米重み付け「25倍」の計算誤り
[実際は5倍]、根拠皆無の「9年ぶり」という年号捏造、調査に無いターゲット層
[都市部中高年層]の創作、著作権フッターのみのevidence_quoteから実在しない
Philips撤退の物語を生成、等)。RECMA(511件生成元)等の競合ランキング表由来
カード群では、evidence_quoteが表の1行断片のみで年度/表題等の文脈が
保存されていないという構造的欠陥も発見。Negative Knowledge(失敗/訴訟/
規制違反)は300件中1件(電通五輪談合起訴の件)のみ確認、しかも通常の
ポジティブなACTION推奨テンプレートに押し込められ「制裁による強制是正」
という文脈が失われていた=TYPE:LESSON/FAILURE型が存在しないことの実証。

`knowledge_quality_audit.md`として8項目(問題タイプ別件数/具体例/原因/
pipeline修正案/schema変更案/expected improvement/再生成コスト/FULL DB適用
判断)をまとめて報告済み。既存DB(`output/knowledge_index.db`)はmd5/mtime
とも変更なしを確認済み(読み取り専用接続のみ使用)。

Next: 中村さんが監査結果を確認し、(1)新パイプライン(SOURCE FACT/
INTERPRETATION分離・evidence_quote拡張・数値Quality Gate・ヘッジ整合性
チェック)を300件サンプルに試作適用してRegression Testで比較する、
(2)FULL DB(14,897件)への適用要否を判断する、のいずれに進むか待ち。
中村さんの明示指示により、この監査結果を見るまでは全件再生成を開始しない。
