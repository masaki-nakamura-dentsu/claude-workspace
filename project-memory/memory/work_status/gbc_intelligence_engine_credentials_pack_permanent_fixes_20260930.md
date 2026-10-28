# GBC Intelligence Engine: クレデンシャル機能 恒久対策2件(宿題1・2)

## 2026-09-30T06:53:59Z
Status: done(コード側の対策は完了、Dify再アップロード+再テストは中村さん待ち)
What: 前セッション(2026-09-30前半、[[gbc_intelligence_engine_project]]参照)で
残った宿題1(Dify検索の恒久対策)・宿題2(generate_agency_os_pack.pyのDBスキーマ
不整合)を実装。
- 宿題1: `credentials_source/fetch_integrated_report_facts.py`の
  `net_revenue`正規表現がゆるすぎ(59ページ中7ページに誤ヒット、UEFA/AI事例等の
  無関係な地の文が「売上高」カードとして混入)だった実データ上のバグを発見・修正
  (見出し数値に隣接する箇所のみに限定→p.3の1件のみに正常化)。あわせて
  `EXCERPT_CONTEXT_CHARS`を500→250字に縮小(実測で67,000名/1,197.5十億円/
  Japan42%等/120カ国、全ての核心数値が窓内に残ることを確認済み)。
  `generate_credentials_facts_pack.py`のファイル冒頭説明文(「取得方法・更新」の
  開発者向けメタ情報を含む4段落、1,434字)も491字に短縮(取得方法の詳細は
  スクリプト側のコメントに残し、Agency OSへの回答生成には不要と判断し削除)。
  結果、`credentials_facts_01.md`の会社概要ファクトカードが12件→6件(無関係な
  net_revenue系6件を除去)に整理された。ローカルの`output/agency_os_pack/`は
  更新済みだが、ChatGPT Skill/Dify双方へは中村さんの手動再アップロードが必要
  (既存の役割分担を踏襲)。
- 宿題2: `migrate_v2_schema.py`を本番DB(`output/knowledge_index.db`)に
  `--allow-production`で適用(事前にコピーで試験実行→問題なし確認済み、本番も
  バックアップ後に実行)。300件のStage A/Bサンプルのみ追加更新(既存14,597件は
  NULLのまま無変更、設計通りの追加型)。これにより`generate_agency_os_pack.py`の
  クラッシュ原因(`v2_quality_bucket`列が無いことによるKeyError)が解消し、
  poc/full両モードとも全Validation項目OKで生成できることを確認済み。QUARANTINE
  21件が正しく除外され、以前手動削除した汚染カード3件も再生成後も正しく非表示の
  ままであることを確認。ローカルの`output/agency_os_pack/`(POC)はこの修正込みで
  再生成・上書き済み(旧版は`_backups_20260930/`にバックアップ)。`agency_os_pack_full`
  は初めての生成試験のみ実施(`/tmp`、未デプロイ)。FULL DB本実行(残14,597件への
  Stage A/B適用、qwen3.8:27b・Windows機・約80時間)は今回のスコープ外のまま
  (別途中村さんの判断待ち)。
- バックアップ一式は`GBC-Knowledge/_backups_20260930/`
  (`credentials_facts_01.md.bak_20260930`/`company_facts.json.bak_20260930`/
  `knowledge_index.db.bak_20260930`/`agency_os_pack.bak_20260930/`)。
Next: (1)中村さんに`credentials_facts_01.md`をChatGPT Skill・Dify両方へ
再アップロードしてもらい、会社規模数値の検索テストを再実施(元の宿題「Dify再
テスト結果確認」はこの再アップロード後に持ち越し)。(2)Difyワークスペースの
プラン期限対応状況の確認。(3)Phase 2(ブランド紹介拡張等)着手要否の相談。

## 2026-09-30T07:10:00Z(同日続き、中村さんが再アップロード完了→自らhitTestingで再検証)
Status: done(検証完了、恒久対策にはコード修正だけでは不十分と判明)
What: 中村さんが`credentials_facts_01.md`をDifyへ再アップロード完了と報告。
共有ブラウザ(port 9226)経由でDifyの検索テスト(hitTesting)ページに直接アクセスし、
2026-09-29に実際に事故を起こしたのと同一の広いクエリ、および「電通グループの
従業員数と売上高を教えてください」という直接的なクエリの両方でTop10チャンクを
確認。**結果: 今回のコード修正(ノイズ除去・冒頭説明文短縮)後も、見出し数値
(67,000名/1,197.5十億円/地域別%/120カ国)を含むカードはどちらのクエリでも
Top10に一切入らなかった**(その代わりに財務目標KPI・経営理念NORTHSTAR・
組織図・マネジメントチーム氏名等、同じファイル内の他セクションが上位を占めた)。
credentials_facts_01.mdが113.9k words(会社規模ファクト以外に受賞歴・ブランド・
年表・組織・理念・経営戦略・マネジメントチームを含む12軸の統合ファイル)である
ため、TopK=10の上限下では狭い数値カードが同じファイル内の他セクションとの
競合に負け続けることを実データで確認。**結論: コード側のノイズ除去は必要な
前提条件だったが、それだけでは不十分で、事前セッションから提案されていた
「事前抽出固定注入」(CASE/海外駐在員と同じ、検索を経由せずワークフローに
直接注入する方式)が実際に必要と確定**。
中村さんの代わりに準備できる範囲として、注入用のテキストブロックを
`credentials_source/company_scale_fixed_injection_block.txt`に作成済み
(SKILL_Dify_for_paste.mdの既存2ブロックと同じ書式、検証済み数値5項目)。
Difyキャンバスへのノード追加・配線(既存のCASE/海外駐在員ノードと同じパターンで
複製)は、既存の役割分担(キャンバス操作は中村さん担当)により未実施。
アプリ一覧から「GBC Agency OS」ワークフロー編集画面への直接URL遷移は
DOM調査でも数回のクリック試行でも解決できず(SPAの内部ルーティングが
通常のhref/onClick検出では特定できなかった)、これ以上のGUI操作の深追いは
トークン消費に見合わないと判断し中断。
Next: 中村さんに(1)`company_scale_fixed_injection_block.txt`の内容を確認、
(2)Difyキャンバスで既存のCASE/海外駐在員ノードと同じ構成のノードをもう1つ
追加・配線、(3)SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.mdの冒頭に3つ目の
【事前抽出】ブロックとして追記(中村さんの公開作業と合わせて実施)、してもらう
よう依頼する。
