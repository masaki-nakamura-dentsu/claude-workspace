# GBC Intelligence Engine — Stage A/B新Pipeline Regression Test(300件)

## 2026-08-26T17:30:00+09:00
Status: in progress
What: 中村さんの指示で、監査結果(knowledge_quality_audit.md)を踏まえた新Pipeline
(Stage A: SOURCE FACT抽出/Stage B: INTERPRETATION生成、RECOMMENDED ACTIONは
生成しない、Negative Knowledge型対応)を実装し、監査と同一の300件サンプルで
旧Pipelineと比較するRegression Testを開始した。FULL DB(14,897件)再生成は
まだ行っていない(中村さんの明示指示、`output/knowledge_index.db`・既存Agency OS
Packは無変更)。

作業内容:
1. 会社Mac(d14461)にOllama(qwen3:8b)を新規セットアップ(管理者権限不要、
   `~/Applications/Ollama.app`に配置、プロキシ`proxy1.dentsu.co.jp:8080`経由で
   ダウンロード。**重要**: `ollama serve`デーモン自体がプロキシ環境変数を継承する
   必要があり、CLIコマンド側にexportするだけでは`ollama pull`がタイムアウトする
   罠を踏んだ→デーモン起動前にexportし直して解決)。
2. 外付けSSD(`/Volumes/Extreme SSD/GBC_アレココ - 添付ファイル`)が接続されて
   いることを確認、元資料804ファイルにアクセス可能と判明。
3. **重大な追加発見**: 既存DBの`evidence_quote`フィールドは元資料の逐語引用
   ではなく、既にLLMによる要約・言い換えを経たテキストだった(実例:
   GBC-0001CCE23388「マテリアリティの特定プロセスにおいて、STEP1:...を行っている」
   は、元資料page15のSTEP1〜4見出し+説明文形式の実テキストを1文に圧縮した要約で、
   単純な部分文字列検索では発見できなかった)。単純な完全一致検索では300件中
   80%が元資料を特定できず、文字3-gramベースのフォジーマッチに切り替えて
   解決(`regression_pipeline_v2.py`の`locate_context()`)。
4. `regression_pipeline_v2.py`(Stage A/B呼び出し)・`regression_compare.py`
   (決定的な定量比較スクリプト)・`regression_review_build.py`
   (severe事例+リスクカテゴリ横断40件の横並びMarkdown生成)を実装。
5. テスト実行5件で確認: GBC-0007FB4A926B(監査で発見した「4語のフレームワーク名
   から効果を捏造」事例)が、新Pipelineでは元資料page35の実際の説明文
   (Predictions/Playbooks/Assessments)を正しく取得し、捏造が解消されることを確認。
   GBC-000AA12338DE(ブラジルアニメ)ではtable_title
   ("Crunchyroll's Most Popular Anime of Winter 2020 By Country")・
   country(ブラジル)・period(2020年冬)を正しく分離抽出でき、監査で指摘した
   「表由来カードの文脈欠落」問題が構造的に解消されることを実証。
6. 300件本番実行を開始(バックグラウンド、約30〜35秒/件で進行中、
   完了まで概算2.5〜3時間)。完了監視用のバックグラウンドプロセスを別途起動済み
   (300行に達するかプロセス異常終了で自動検知)。

Next: 300件完了後、`regression_compare.py`で定量比較(SOURCE FACT fidelity/
Hallucination率/Interpretation混入率/Numeric error率/Evidence completeness/
Hedge preservation率/Unsupported generalization率/Duplicate率/QUARANTINE率/
VERIFIED-USABLE比率)を算出し、`regression_review_build.py`で severe事例
(GBC-02F583/021520D99995/03576F5DA4AF/0EF7F6/11FF96397231/0007FB4A926B/
55B3529BE939/54BB3959A6F7/RECMA由来5件、全て300件サンプルに存在確認済み)+
リスクカテゴリ横断サンプルの`regression_review.md`(40件)を生成する。
最終的に`regression_report.md`として、旧vs新の定量比較・severe事例改善状況・
残存エラー・False Positive/Negative・Knowledgeとしての有用性低下有無・
新Schema実例10件・QUALITY SCORE分布・FULL DB適用可否・推定時間・
Agency OS Pack差し替え要否をまとめて報告する。**FULL再生成は中村さんが
このレポートを確認するまで開始しない**。

## 2026-08-26T17:35:00+09:00
Status: blocked(会社Mac作業中断、個人Windowsへ引き継ぎ)
What: 中村さんが会社Mac(d14461)を今日中にシャットダウンする必要があり、作業を
個人Windows(自宅RTX3090)へ引き継ぐことになった。300件中35件処理済みの時点で
バックグラウンドプロセス(`regression_pipeline_v2.py`, Ollama serve)を安全に停止
(kill、jsonl 35/35行が正常なJSONであることを確認済み、データ破損なし)。
`regression_pipeline_v2.py`はマシン固有パス(SSD_ROOT/Ollama URL/モデル名)を
環境変数化する修正を実施(`GBC_SSD_ROOT`/`GBC_OLLAMA_URL`/`GBC_OLLAMA_MODEL`、
未設定時はMac既定値にフォールバック)、Windows(ドライブレター形式のパス)でも
コード変更なしで動かせるようにした。スクリプトは中断・再開に対応済み
(`--out`ファイル内の既存IDをスキップする設計)ため、同じコマンドを再実行すれば
36件目から自動的に再開される。

最後に完了したID: GBC-0105548D6759(35/300)。個人Windows側で必要な前提条件
(Ollama+qwen3:8b、元資料SSD/GBC_アレココ - 添付ファイル 804ファイルへのアクセス、
Python依存パッケージ)をユーザーに案内済み(会話内の指示文参照)。

Next: 個人Windows側のセッションが、上記の環境変数を設定した上で
`regression_pipeline_v2.py`を再実行し、残り265件を処理→
`regression_compare.py`→`regression_review_build.py`→最終`regression_report.md`
作成、という残作業を引き継ぐ。**次にこのプロジェクトに会社Mac側で触るときは、
個人Windows側でどこまで進んだか(300件完了したか、レポート作成済みか)を
中村さんに確認してから再開すること**(前提が変わっている可能性が高いため)。

## 2026-08-26T17:45:00+09:00
Status: blocked(引き継ぎ完了、Windows側の着手待ち)
What: `.claude-sync/claude_relay/windows_inbox.md`(既存のMac↔Windows非同期
指示キュー、[[claude_relay_system]])にtask-006として詳細な引き継ぎ指示を追記した
(前提条件確認手順・再開コマンド・比較/レポート作成手順・FULL再生成を勝手に
始めない旨・完了後の報告手順を含む)。中村さんには「windows_inbox.mdを確認して」
という合図フレーズをWindows側Claude Codeセッションに伝えるよう案内済み
(この relay システムは手動トリガー方式、[[claude_relay_system]]参照)。
`regression_pipeline_v2.py`はマシン非依存の環境変数化を完了済み(コード変更不要)。
Next: Windows側がtask-006に着手し、Result欄への記入・`regression_report.md`
作成まで完了するのを待つ。会社Mac側で次に再開する際は、まずtask-006のStatusと
Result欄を確認すること。

## 2026-08-27T07:07:00+09:00
Status: waiting(task-007をWindows側へ依頼、トリガー待ち)
What: 中村さんから個人Mac側でのPJ引き継ぎ可否を問われ、状況確認したところ
個人Windows側がtask-006(300件Regression Test)を完了済みと判明
(`regression_report.md`作成済み、02:43)。要旨: 過剰一般化56%→0.7%に改善、
数値計算混入(GBC-0102B8C9F333等)という新課題を発見、FULL DB再生成は時期尚早
との結論。個人Macの環境(`~/gbc_knowledge_venv`・Ollama qwen3.8:27b)は整って
いるが外付けSSD(元資料)は未接続のため、検証系タスクは実行できず。
中村さんの指示で「レポート確認→Windows側への改善指示準備」を実施し、
`regression_pipeline_v2.py`のstage_a()を読んだ上で数値グラウンディング
チェックの実装案を設計、`.claude-sync/claude_relay/windows_inbox.md`に
task-007として追記(Status: waiting)。プロジェクト詳細メモリ
[[gbc_intelligence_engine_project]]にも同内容を追記済み。
Next: 中村さんがWindows側セッションに「windows_inbox.mdを確認して」と
声をかけ、task-007のResultが記入されるのを待つ。

## 2026-08-27T(task-007完了確認)
Status: done
What: Windows側がtask-007を完了(windows_inbox.md確認済み)。数値グラウンディング
チェック(numeric_grounding_check())を実装し、既存63件のNUMERIC_SUSPECTのうち
17件検出(long_decimal 1件=誤検知なし、not_in_context 16件=手動精査4件中3件が
誤検知)。誤検知の原因は日英月表記差・ファイル名混入・欧州式コンマ小数点の3パターン。
自動破棄でなくQUARANTINE止まりなので安全側。regression_report.md 11章に詳細追記済み、
プロジェクト詳細メモリ[[gbc_intelligence_engine_project]]にも反映済み。
Next: 中村さんに、(a)not_in_contextの精度改善(コンマ処理・ファイル名/ページ番号除外)を
先にやるか、(b)このままFULL DB(14,897件)適用の是非検討に進むか、方針を確認する。

## 2026-08-27T(精度改善を個人Mac側で実装、task-008でWindowsへ実データ検証依頼)
Status: waiting(task-008、Windowsのトリガー待ち)
What: 中村さんが「精度改善を先にやる」を選択。`regression_pipeline_v2.py`は
Dropbox同期フォルダ内にあるため、SSD不要なコード修正は個人Macで直接実施:
(1)numeric_grounding_check()にコンマ小数点(欧州式)対応、(2)ファイル名/ページ番号を
数値抽出対象から除外(正規表現+実ファイル名の丸ごと除去)。既存jsonlのデータで
近似検証し、GBC-01647E・GBC-0129FAFA0EDDの誤検知解消、GBC-0102B8C9F333・
GBC-040C75E406BD(本物の問題)の検出維持を確認(退行なし)。
Next: 実データ(本物のcontext_text)での本番同等再検証をtask-008として
windows_inbox.mdに追記済み。Windows側がトリガーされ次第、63件全件+残237件への
適用結果、GBC-01647E/0129FAFA0EDDの実データでの解消確認をResultに記録する想定。

## 2026-08-27T(task-008完了確認)
Status: done
What: Windows側がtask-008を完了(windows_inbox.md確認済み)。実データ(SSD経由)で
63件中の検出数が17件→13件に減少、依頼した2誤検知パターン(GBC-01647E/0129FAFA0EDD)は
解消確認、真陽性(0102B8C9F333/040C75E406BD)は退行なし、残237件への新規誤検知0件。
regression_report.md 12章・プロジェクト詳細メモリに反映済み。
Next: FULL DB(14,897件)適用可否の最終判断は中村さん待ちのまま変更なし。次回は
FULL適用に進むか、さらに精度改善(月表記ズレ等)を続けるか、方針確認から再開する。
