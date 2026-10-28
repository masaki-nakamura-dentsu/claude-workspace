---
name: feedback-agency-os-is-chatgpt-skill-not-gpt
description: Agency OSはChatGPTのCustom GPT(GPT Builder)でもClaude Skillでもなく、ChatGPT側の「Skill」機能である。混同すると誤った確認手順・誤ったプラットフォーム前提で回答してしまう。
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5263b134-8bec-4c40-a940-cf80b9d6bb7a
  modified: 2026-09-14T07:18:17.025Z
---

**Agency OSはChatGPTの「Skill」機能で作られている。「GPT」(GPT Builder/Custom GPT)でも、Claude(claude.ai)のAgent Skillsでもない。**
同じ取り違えが3回発生している:
1. 2026-09-03: Custom GPTと誤認([[gbc_intelligence_engine_project]]内「訂正— これはCustom GPTではなくChatGPT Skill」の記録)
2. 2026-09-14(あるセッション): 再び「GPTを編集」「/gpts/mine」を案内→中村さんに「なんでGPTの話が出てくるのですか」と指摘
3. 2026-09-14(別セッション): SKILL.mdの安全性レビュー警告についての質問で、確認せずにいきなり**Claude(claude.ai)のEnterprise Skill security scanning**の話だと決め打ちしてWebSearch/WebFetchまで行い、見当違いの回答をした。中村さんが「いまはChatGPTのSkillを使って構築しています」と訂正して発覚。このプロジェクトの[[gbc_intelligence_engine_project]]には「別のChatGPT Skill「Agency OS」」と明記されており、確認すれば防げた誤りだった。

**Why**: 用語が紛らわしい(SKILL.mdのfrontmatterやSkillという単語自体はClaude Skillの慣習と同じ形式のため、つい"GPT"や"Claude"の文脈で考えてしまいがち)。しかし関わりうるプラットフォームは3つある——ChatGPTの「Custom GPT」(GPT Builder経由、`chatgpt.com/g/...`、Instructions欄+Knowledge欄)、ChatGPTの「Skill」(`chatgpt.com/skills/editor/...`、SKILL.md本体+`references/`+ルート直下のデータファイル群)、Claude(claude.ai)の「Agent Skills」(構造はChatGPT Skillに酷似——SKILL.mdのfrontmatter形式もほぼ同じ——だが安全性スキャン機能・Enterpriseガバナンス・エラーメッセージの文言が別物)。Agency OSは2番目(ChatGPT Skill)。3番目のケース(2026-09-14)では、SKILL.mdという語だけでClaude側の話だと即断し、確認質問を挟まずWeb調査まで進めてしまった——[[feedback_verify_against_ground_truth]]・[[feedback_extract_from_project_files_before_asking]]が言う「断定前に一次情報を確認する」を怠った具体例。

**How to apply**: 次にAgency OS(またはSKILL.md、または「Skillで警告が出た」等の相談)に触れる際は、
1. まず[[gbc_intelligence_engine_project]]で「これはChatGPT Skillである」という既存の事実を確認してから動く。プラットフォーム(ChatGPT Custom GPT / ChatGPT Skill / Claude Agent Skills)のどれかを、ユーザーの発言や過去メモリで確認する前に決め打ちしない。曖昧なら質問してから調べる。
2. 「GPTを編集」「GPT Builder」「/gpts/mine」等のCustom GPT用語・導線を絶対に使わない。
3. 確認・反映作業は直接このURLを案内する: `https://chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080`(変わっていたら[[gbc_intelligence_engine_project]]の2026-09-04追記を参照、または中村さんに最新URLを確認)。
4. ファイル構造は`references/`=Agency OS自身の動作定義ドキュメントのみ、GBCデータパック(cases_*.md等)はSkillルート直下にフラット配置——[[gbc_intelligence_engine_project]]の2026-09-03エントリに実際のツリー図あり、SKILL.md編集時は毎回このパス構造を確認すること。
5. ChatGPT Skillの安全性スキャンは「即利用可/Needs Review(要レビュー、UI上の承認ボタンで解除可、承認しても使用自体は継続できる)/Blocked(使用不可)」の3段階。SKILL.mdの文言をどう調整してもNeeds Reviewが消えないことがある(2026-09-14に実例: プライバシー配慮無効化っぽい文言を書き換えても警告は残った)——これは個人名・内部URLをそのまま出力する設計自体が構造的にフラグされている可能性が高く、文言修正より先にUI上の「承認」ボタンの有無を案内する方が早い。
