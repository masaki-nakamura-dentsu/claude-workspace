---
name: feedback-dify-retrieval-starvation-causes-fabrication
description: Dify knowledge-base retrieval has a hard Top K ceiling tied to the embedding model's max_tokens, and when a broad/multi-topic query exceeds that ceiling, the LLM can fabricate specific numbers and mislabel them as VERBATIM_QUOTE/INTERNAL FACT rather than reporting a gap — diagnose with hitTesting before trusting Pack content is at fault
metadata:
  node_type: memory
  type: feedback
  originSessionId: unknown
  modified: 2026-09-30T02:27:41.731Z
---

**Rule**: whenever a Dify app gives a wrong specific number/quote while citing it as an internal fact or VERBATIM_QUOTE, don't assume the Knowledge Pack content itself is wrong — first reproduce the exact user query in the dataset's own `hitTesting` (検索テスト) page and read what was *actually* retrieved. If the correct figure isn't among the retrieved chunks, the model fabricated it from its own background knowledge while dressing it up as sourced — a retrieval-completeness bug, not a content bug.

**Why**: confirmed 2026-09-30 in [[gbc_intelligence_engine_project]] — a broad credentials-deck request ("自動車業界の新規クライアント向けに、電通の会社紹介と実績をまとめた提案資料を作りたいです...") caused Dify to state 56,000 employees / ¥719.4bn net revenue / 22.4% Japan share, all confidently labeled "VERBATIM QUOTE(統合報告書より)" — none of which exist anywhere in the Pack (verified real values: 67,000 / ¥1,197.5bn / 42%). Hit-testing the identical query showed only 3 chunks retrieved (Top K was set to 3), two of which were generic file-header "what this file contains" blurbs rather than actual fact cards — the real company-scale cards never made it into context at all, and the model filled the gap with plausible-sounding but wrong numbers instead of saying "not found."

**The Top K ceiling is not user-configurable beyond a point**: raising Top K from 3 to 10 helped but did not fully fix it — Dify's dataset settings UI enforces a hard `max` on the Top K number input (confirmed `max="10"` in this case), described in its own tooltip as dynamically tied to the selected embedding/rerank model's `max_tokens`. You cannot type past this ceiling; the UI silently ignores the write and the value reverts on reload. Even at the ceiling, a sufficiently broad multi-topic query can still crowd out short, dense fact cards (a handful of numbers + a label) in favor of longer prose chunks that score higher on generic semantic overlap with a conversational business query — so raising Top K to its max is necessary but not always sufficient for broad "give me everything for a company overview" style requests.

**How to apply**:
1. When a Dify app produces a wrong number/quote presented as internal/sourced fact, go to that dataset's 検索テスト (hitTesting) page, paste the *exact* user query (not a keyword approximation), and check whether the correct chunk appears at all in the retrieved set before concluding the Pack content needs fixing.
2. Check the dataset's 設定 (settings) page for the current Top K and score threshold. A low default (Dify's stock default is small) is a common unexamined cause of sparse retrieval for broad queries — raise Top K toward its ceiling if the retrieved set looks thin, and check whether the score threshold (if enabled) is silently filtering out lower-scoring-but-relevant chunks.
3. Know the ceiling exists — don't keep retrying larger Top K values expecting them to save; inspect the actual input's `max` attribute (or watch for the UI reverting your typed value) to detect it quickly instead of assuming a save bug.
4. For content that must reliably appear regardless of retrieval luck (e.g., headline company-scale numbers in a credentials/company-profile use case), consider bypassing RAG retrieval entirely via a fixed "pre-extraction" injection block wired directly into the workflow's LLM node — this project's Dify app already uses this pattern for CASE data and overseas-staff data (`{{{#<node-id>.text#}}}` blocks hardcoded into the SYSTEM prompt) precisely because retrieval reliability for a small set of always-needed facts isn't worth leaving to chance.
5. A shorter, less semantically "attractive" file-header/description blurb competes less for retrieval slots against the real content chunks in the same file — if a file's own "what this file contains" preamble keeps showing up ahead of its actual data in hit-testing, consider trimming it.

Related: generation-time (not retrieval) fabrication in diagrams/slides is a separate pattern — see [[feedback_generation_time_diagram_fabrication]].
