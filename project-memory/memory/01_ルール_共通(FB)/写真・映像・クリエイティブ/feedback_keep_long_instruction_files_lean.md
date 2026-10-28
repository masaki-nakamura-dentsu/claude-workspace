---
name: feedback-keep-long-instruction-files-lean
description: "When maintaining a long system-prompt-style instruction file (ChatGPT Skill SKILL.md, Custom GPT instructions, etc.), keep the operative rules short and move incident-history/rationale text to a separate changelog — don't let \"added on DATE, from incident...\" narratives accumulate inline."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5263b134-8bec-4c40-a940-cf80b9d6bb7a
  modified: 2026-09-14T05:38:00.042Z
---

**Rule**: when adding or strengthening a rule in a long-lived instruction file that an LLM re-reads every turn (a ChatGPT Skill's `SKILL.md`, Custom GPT instructions, a Claude Skill, etc.), write the rule itself tightly and put any backstory ("added 2026-09-14, from a live incident where...") into a separate changelog/reference file instead of inline. Also actively consolidate: if the same requirement ends up restated in multiple sections over time, merge them into one canonical statement rather than letting duplicates pile up.

**Why**: In [[gbc_intelligence_engine_project]]'s Agency OS Skill, repeated incident-driven patches each appended a full narrative paragraph justifying the new rule. By 2026-09-14 `SKILL.md` had grown to 646 lines / ~42,500 characters (~10-14K tokens) — roughly 5x a typical ChatGPT Custom GPT instructions-field limit — with the same "internal search + dentsu format always required" message independently restated in three different places. The user (Masaki Nakamura) suspected this length itself was contributing to the model skipping mandatory steps and inventing an undefined "ライトSTANDARD" mode, since rules buried mid-document suffer from the well-known "lost in the middle" attention effect regardless of any hard platform limit. Restructuring (moving all incident narratives to a new `changelog.md`, consolidating duplicate restatements into one "Always-on constraints" block, compressing multi-paragraph rules into tight bullets) cut the file to 236 lines / ~27,000 characters with zero loss of behavioral requirements, and the user confirmed the next live test worked correctly.

**How to apply**: Going forward, whenever fixing a bug in any of this user's long-lived instruction files (not just Agency OS — this generalizes to any Custom GPT instructions, other Claude Skills, or similar system-prompt-style documents built for this user), default to: (1) write the new/changed rule as a short, direct, imperative statement with no backstory; (2) put the "why"/incident description in a dedicated changelog file the model doesn't need to re-read every turn; (3) periodically check whether the same requirement has drifted into being restated in multiple places and consolidate. If a file is already long (multiple hundred lines / tens of thousands of characters) and behaving unreliably, proactively suggest a length/duplication audit rather than only patching the specific reported symptom.
