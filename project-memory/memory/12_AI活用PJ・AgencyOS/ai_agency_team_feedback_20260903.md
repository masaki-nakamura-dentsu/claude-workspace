---
name: ai-agency-team-feedback-20260903
description: "「Agent OS」フィードバック対応時に誤って~/AIAgency(別物のClaude Code製/agency)を先に直してしまった件の記録。本命は[[gbc_intelligence_engine_project]]内のChatGPT「Agency OS」Skill"
metadata: 
  node_type: memory
  type: project
  originSessionId: 150e7c22-5285-4234-ab28-53e2cfae349a
  modified: 2026-09-03T01:35:05.642Z
---

**重要な訂正(同日中に判明)**: このメモリの対応は、ユーザーが実際にフィードバックした
対象を誤認して行ったもの。ユーザーが最初「Agent OSのフィードバック」とだけ言い、
テスト会話のChatGPT共有リンクが403で読めなかったため、このセッションは類似の
名前を持つ別物 `~/AIAgency`(Claude Code nativeの`/agency` subagent群、
[[ai_agency_team_build]]参照)を対象と誤って推測し、以下の対応をしてしまった。
その後ユーザーがPDFで実際のテスト会話を貼り付け、本当の対象はGBC知見集約プロジェクト
(`GBC-Knowledge/generate_agency_os_pack.py`が生成するKnowledge Packを読む、
ChatGPT Custom GPT「gbc-ai-agency」、自称「Agency OS」)だったと判明した。
**正しい対応の詳細は[[gbc_intelligence_engine_project]]の「2026-09-03: 
「Agency OS」ChatGPT Skillのテストフィードバック対応」セクションを参照。**
このメモリ自体は「誤認して~/AIAgencyに加えた変更の記録」として残す
(その変更自体は無駄ではなく`~/AIAgency`の実際の改善にはなっているが、
今回のフィードバックの対象ではなかった、という点に注意)。

---

2026-09-03、ユーザーが `/agency` を使ったテスト(架空案件でのやり取り、ChatGPT上で実施・共有リンクは403で本文取得不可)を経て、以下5点のフィードバックを出した:
1. 関連事例をURL付きで表示してほしい
2. 案件に沿ったチェックリスト(確認事項・注意点)を必ず出す
3. 出力後にユーザー自身が分析を進める際に使えるツールと、どの工程で使うべきかのアドバイスを入れる
4. ツール以外の一般情報・データソースも教えてほしい
5. 例: 米国案件なら米国のケイパビリティ資料・広告事情を必ずURLで参照できるようにする

対応内容(実ソースは `~/AIAgency`、`~/.claude/agents/*.md` と `~/.claude/commands/agency.md` はそこへのsymlink):
- `~/AIAgency/.claude/agents/researcher.md`: 事例引用時のURL必須化、出力に「Related Cases(関連事例)」「Reference Sources(参照データ・資料)」セクションを追加。海外案件では当該国の広告市場データとケイパビリティ資料を必ず探す指示を追加。
- `~/AIAgency/reference/tools_and_sources.md`(新規): 市場データ/生活者調査/デジタル競合分析/事例アーカイブ等のカテゴリー別ツール一覧と、国別の一般情報の探し方(公開情報はWeb検索、ケイパビリティ系は`競合分析/`等のDropbox内資料もGrep/Globで確認)をまとめた共有リファレンス。researcherと最終提案の両方から参照される設計。
- `~/AIAgency/.claude/commands/agency.md`: 最終提案フォーマットに「17. CHECKLIST」(案件固有の確認事項・注意点。各サブエージェントのASSUMPTIONやRISKSを横断して拾う)と「18. TOOLS & FURTHER ANALYSIS」(ツール名を羅列せず、何が得られるか/どの工程で使うか/URLをセットで書く)を追加。「2. WHAT WE FOUND」でresearcherの事例URLを引き継ぐ指示も追加。
- `~/AIAgency/CLAUDE.md`: 構成説明に`reference/`を追記。
- ローカルgit commit済み(`1aa1a29`)。push・遠隔共有はしていない。

**Why**: ユーザーは提案書を受け取った後、自分でも裏付け調査・分析を続けることが多く、その際の起点(事例の出典、使えるツール、確認すべき論点)が提案書に無いと毎回ゼロから探すことになっていた。

**How to apply**: 次回`/agency`実行時、最終提案にCHECKLIST/TOOLS & FURTHER ANALYSISが実際に出るか、事例にURLが付くかを確認する。ツール一覧(`reference/tools_and_sources.md`)は使うたびに実在確認済みのものを追記していく設計なので、空リストのまま放置しない。関連: [[ai_agency_team_build]](別プロジェクトのmemory、`~/.claude/projects/-Users-d14461/memory/`配下 — 構築経緯・symlink方式・過去のworkspace上書き事故の詳細はそちら)。
