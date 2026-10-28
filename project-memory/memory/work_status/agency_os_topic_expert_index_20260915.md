# Agency OS Topic Expert Index追加

## 2026-09-15T00:28:30Z
Status: in progress
What: SharePoint「GBC-アレココ」の部署別担当者一覧(法務/契約管理/出張/設定リクエスト等)を
Playwright(共有ブラウザ、DOMテキスト抽出、スクリーンショット不使用)でスクレイピングする
スクリプトと、中村さんから直接提供されたチーム別エキスパートリスト(AI開発/インバウンド/
IPコンテンツ/Salesforce/PowerBI等)を統合した新規experts/topic_expert_index.mdを
GBC-Knowledge/output/agency_os_pack/に追加。SKILL.md(ローカル控え)にRequirement H
「該当するTopic/Task Expertを必ず紹介する」を追加。詳細は[[gbc_intelligence_engine_project]]。
Next: (1)実際のAgency OS拠点(ChatGPT/Dify/GBC Business)へのアップロードは中村さんが
月次運用で実施予定。(2)Part1(SharePoint)は月次ルーチン相乗りで確定。(3)Teams全履歴からの
暗黙エキスパート抽出は個人Windows機のOllama(qwen3.8:27b)で本格実施する方針が確定したが、
会社Macから192.168.0.11へ接続不可だったため、claude_relay(windows_inbox.md)のtask-013として
Windows側Claude Codeセッションへ中継依頼済み(pending、対象データteams_export_source/に
コピー配置済み)。次回は同タスクのStatus/Resultを確認してからMarkdown統合・SKILL.md反映へ進む。

## 2026-09-15T01:05Z
Status: done
What: Part1(SharePoint)/Part2(手動リスト)の統合ファイル作成・SKILL.md/README.md反映・
Teamsマイニングのtask-013中継依頼、まで完了。詳細は[[gbc_intelligence_engine_project]]。
Next: task-013完了後にレビュー・統合(次回セッション)。

## 2026-09-15T01:15Z
Status: done
What: 中村さんの依頼で claude_relay/README.md の記述ズレ(2026-09-11の許可制訂正が
未反映)を修正。仕組み自体はグローバルCLAUDE.mdに既に明記済みで、3台ともsymlink
同期済みのため追加設定は不要という結論。詳細は[[mac_handoff_relay]]。
Next: —

## 2026-09-15T01:20Z
Status: in progress
What: 中村さんがWindows側task-013の完了待ちであることを確認(応答のみ、作業なし)。
Next: Windows側task-013完了後、teams_implicit_expert_candidates.jsonをレビューし
topic_expert_index.md/SKILL.mdへ統合する。

## 2026-09-15T01:40Z
Status: done
What: Windows側task-013(Teams全履歴からの暗黙エキスパート抽出、405件)の結果をレビューし、
generate_topic_expert_pack.pyを拡張してtopic_expert_index.mdのPart 3として統合完了。
氏名の名寄せは厳密に同一フルネームの表記ゆれのみ統合し、姓のみの言及は誤同定回避のため
別セクションに分離。SKILL.md/README.mdにPart1/2(断定可)とPart3(machine推定、要留保)の
性格の違いを明記。詳細は[[gbc_intelligence_engine_project]]。
Next: 実際のAgency OS拠点(ChatGPT/Dify/GBC Business)へのアップロードは中村さんが
月次運用で実施予定。本タスク一式はこれで完了。

## 2026-09-15T02:00Z
Status: in progress
What: 中村さんが topic_expert_index.md をレビュー・大幅トリム(51KB→8.3KB、Part3の
局員に無関係な項目を削除)。「今後は本人の履歴を含めなくてよい」との指示を受け
extract_implicit_experts.pyにEXCLUDED_PERSONS_NORMALIZEDを追加し将来の抽出から除外。
MANUAL_TEAM_EXPERTS辞書も中村さんの修正(田上浩次郎/山内康弘)に合わせて更新。
ChatGPT Skill/Dify両方への反映方法を案内する回答を準備中。
Next: ChatGPT Skill editor(chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080)
とDify(console.dj-dify.dentsu.jp、GBC Agency OSアプリ)への実アップロードは中村さん
自身が実施予定。

## 2026-09-15T02:25Z
Status: done
What: 「法務担当」への捏造回答(架空の「佐藤真理」)を調査。ChatGPT Skillエディタを
ブラウザ自動操作で直接調査し、データ(topic_expert_index.md/SKILL.md)は正しく保存済みと
確認。原因は保存忘れ+非Thinkingモデル(Instant)使用時の検索ツール不呼び出し(2026-09-11の
既知バグ再発)と特定。Thinkingモデルに切り替えて正しい回答(佐多茜、出典付き)を再現確認。
詳細は[[gbc_intelligence_engine_project]]。
Next: 中村さんに原因と対策(Thinkingモデル使用)を報告。Dify側の更新はまだ未実施。

## 2026-09-15T02:45Z
Status: done
What: 中村さんの指摘でSKILL.md(ChatGPT)/SKILL_Dify.md(Dify)の分岐を見落としていたと
判明。SKILL_Dify.mdに同じ変更(bucket一覧・Withholding・How to use・Requirement H・
月次更新セクション、計7箇所)を個別パッチとして適用、Dify専用差分は維持。
feedback_agency_os_skillmd_multi_deployment_sync.mdとして教訓を保存。
Next: 中村さんにSKILL_Dify.mdの内容をDifyのLLMノードSYSTEM promptへ反映してもらう。

## 2026-09-15T03:10Z
Status: done
What: 中村さんが実際のDify system prompt全文を貼付。ローカルSKILL_Dify.mdより先に
進んでいた3点(事前抽出変数注入ブロック2つ・Markdown出力注意・0件誤報告防止ルール)を
発見しSKILL_Dify.mdに統合(679行)。Dify貼り付け専用のfrontmatter除去版
SKILL_Dify_for_paste.md(659行)を新規作成し、これを開いてユーザーに提示。
Next: 中村さんがSKILL_Dify_for_paste.mdの内容をDifyのLLMノードへ貼り替え、
topic_expert_index.mdもナレッジベースに追加してテストする。

## 2026-09-15T03:40Z
Status: done
What: KNOWLEDGEカード引用時のURL欠落バグを調査・修正。render_knowledge_card()の
Source位置をヘッダーへ移動(CASEカードと同じ構造に統一)、既存生成済みMarkdown
16,397件(POC+FULL)へfix_knowledge_source_placement.pyで後処理適用、整合性確認済み。
DB自体(v2_quality_bucket列欠落)のフルパイプライン再実行は別課題として保留。
詳細は[[gbc_intelligence_engine_project]]。
Next: 中村さんが修正済みknowledge_*.md(POC、7ファイル)をChatGPT/Dify両方に
再アップロード。DBスキーマ不整合の解消も次回検討。

## 2026-09-15T04:15Z
Status: done
What: Dify「GBC Agency OS」のワークフローを調査し、4データセット(メイン16件/
cases_global_01.md系4件/cases_apac_01.md単独/overseas_staff_index単独)が
知識検索1-4ノード→LLM3 CASES抽出・LLM4駐在員抽出という事前抽出アーキテクチャに
それぞれ接続済みと確定。中村さんが「重複整理」を打診したが、削除すると事前抽出が
壊れるため今回は現状維持に決定。ファイル別のアップロード先対応表を
[[gbc_intelligence_engine_project]]に記録済み。
Next: 中村さんが修正済みファイル(knowledge_*.md 6件→メイン、knowledge_untagged_01.md→
cases_global_01.md系データセット)をDify/ChatGPT両方にアップロードすればこのタスク一式は完了。

## 2026-09-15T05:00Z
Status: done
What: ChatGPT Skillのknowledge_*.md 7ファイル差し替えを実施。隠しinputへの直接
setInputFiles()では削除は反映されるがアップロードが永続化しない不具合に遭遇し、
一時的に7ファイル全滅の状態を作ってしまった(ヒヤリハット)。filechooser方式に
切り替えて1件ずつreload確認しながら全7ファイル復旧、SOURCE欄付きで正常内容・
重複なし・全33ファイル整合性確認済み。教訓はfeedback_web_file_upload_use_filechooser_not_hidden_input.mdに保存。
Next: なし。本タスク一式(topic_expert_index追加+KNOWLEDGE URL修正+ChatGPT/Dify反映)完了。

## 2026-09-15T05:10Z
Status: done
What: 中村さんがDify側の修正版knowledge_*.md反映を自身で完了。ChatGPT/Dify両方への
反映が完了し、本タスク一式(topic_expert_index追加・KNOWLEDGEカードURL欠落修正・
両プラットフォーム反映)は完了。
Next: なし。

## 2026-09-15T05:30Z
Status: done
What: SKILL_Dify.mdの長さ整理をChatGPT版と同じ手法(経緯説明をchangelog.mdへ、
重複記述を統合)で実施。679行/49,000文字→265行/31,600文字。機能面の欠落なし(grep
検証済み)。changelog.mdに4エントリ追加。貼り付け用SKILL_Dify_for_paste.md(252行)
を生成し提示。
Next: 中村さんがDifyのLLMノードSYSTEM promptをこの新しい圧縮版に差し替え、動作確認。
