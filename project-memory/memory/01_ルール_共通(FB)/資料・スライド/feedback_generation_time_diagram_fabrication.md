---
name: feedback-generation-time-diagram-fabrication
description: A distinct fabrication pattern from retrieval-starvation — when an LLM is asked to render sparse sourced data as a visual (org chart, flow diagram), it can invent extra boxes/labels/organizational names to make the diagram look richer/more complete, then falsely caption the result as sourced from the internal pack. Retrieval was correct; the embellishment happens at generation time.
metadata:
  node_type: memory
  type: feedback
  originSessionId: unknown
  modified: 2026-09-30T06:35:14.524Z
---

**Rule**: verifying that an LLM correctly *retrieved and quoted* source data (e.g. it passed a COMMON KNOWLEDGE TEST MODE text query cleanly) is not sufficient evidence that a *generated artifact* (a slide, diagram, chart) built from that same data will also stay accurate. Test the build step separately, with its own verification, even right after a clean retrieval test.

**Why**: confirmed 2026-09-30 in [[gbc_intelligence_engine_project]] (Agency OS credentials-deck feature). A card in the Pack described a plain 3-step flow ("電通本社(日本) → CR制作チーム/メディア・アクティベーションチーム → 対象国：メディア、アクティベーションチーム"). Asked as a text question ("In-Out体制について教えて"), the Skill answered this correctly and verbatim, citing the source. In the same session, asked next to "turn this into a slide," it produced a 5-box, 4-stage org-flow diagram inventing specific organizational unit names ("BP局/DJN", "GBC PMO", "1CRP/5CRP", "カラ・J/PR") and named process stages ("①Brief/Scope②Teaming③Localize④Execute/Report") that appear nowhere in the source card — while still captioning the slide "出典：社内GBC Knowledge Pack / Global Department Index" as if it were sourced. This is mechanistically different from the retrieval-starvation fabrication documented in [[feedback_dify_retrieval_starvation_causes_fabrication]] (where the correct data never made it into context at all) — here the correct, sparse data *was* available and had just been quoted correctly moments earlier; the embellishment happened because building a "professional-looking" diagram from only 3 known elements apparently invites the model to fill in more boxes/labels to make the visual feel complete, rather than rendering the sparse-but-accurate version.

**How to apply**:
1. When adding LLM-driven diagram/slide-generation instructions (whether for Agency OS or any other Skill), explicitly state: render only the entities/labels/steps the source data actually names; a diagram that looks sparse because the source is sparse is correct, and padding it with invented parties or stage names to look fuller is a fabrication exactly as serious as inventing a wrong statistic — even though it happens during a generation/build step rather than a text-retrieval step.
2. Don't treat "it passed the retrieval test" as covering the build step too — if the workflow both retrieves data AND renders it into a visual artifact, test both stages independently. A clean text-QA pass and a subsequent "now make this a slide" request in the same conversation can diverge sharply.
3. A concrete tell to watch for: any diagram/slide whose element count or specificity noticeably exceeds what a one-paragraph source card could plausibly justify (e.g. 5 labeled boxes with jargon-y unit names from a 3-sentence source) — that mismatch in richness is itself a signal worth checking against the actual source text before trusting the artifact.
