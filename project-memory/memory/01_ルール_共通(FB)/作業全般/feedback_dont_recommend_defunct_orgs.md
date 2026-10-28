---
name: feedback-dont-recommend-defunct-orgs
description: When building a people/organization directory from a source that mixes current and historical entries, never surface the historical/unmatched portion as a hedged recommendation — exclude it outright. A hedge doesn't fix "this may no longer exist."
metadata:
  node_type: memory
  type: feedback
  originSessionId: unknown
  modified: 2026-09-15T08:08:49.317Z
---

**Rule**: when a directory-building task (contacts, departments, experts, organizations) has a "current, authoritative" sub-source and a "broader but unverified/historical" sub-source, never design the historical portion to be surfaced to the end user as a hedged lead ("this may have changed, please verify"). If it can't be confirmed current, exclude it from recommendations entirely — keep it only as a non-user-facing historical record.

**Why**: built `global_department_index.md` for [[gbc_intelligence_engine_project]]'s Agency OS Skill from two sources — a SharePoint index page (Part 1, current/official) and its underlying Excel registration history (Part 2, entries not matched to the current page — could be renamed, reorganized, or simply dissolved). Initial design hedged Part 2 ("verify before contacting") rather than excluding it, reasoning that a caveat was enough due diligence. Nakamura-san corrected this directly: "もうなくなってしまった組織もあるので、それは案内しないで下さい" (some of these organizations don't exist anymore — don't guide people to them). The flaw: there's no reliable way to tell "renamed, findable under a new name" apart from "genuinely dissolved" from the data alone, so a hedge just launders an unverifiable recommendation into a verified-sounding one — the user still has to do real work to find out it was a dead end, and a caveat doesn't prevent that cost.

**How to apply**: the next time a task asks to route someone to a person/team/organization from a mixed-confidence source, ask up front (or infer from the source's own structure) whether the non-authoritative tier should be (a) shown with a hedge, or (b) excluded outright — don't default to (a) just because "hedging" feels like the responsible middle ground. If the non-authoritative tier's failure mode is "the user contacts something that no longer exists" (not just "the info might be stale"), default to exclusion, not hedging — that failure mode isn't something a caveat sentence actually prevents. This generalizes beyond this one file: [[topic_expert_index]]'s Part 3 (Teams-inferred candidates) is a different case where hedging is the right call, because its failure mode is "this person might not actually be the best contact" (a soft miss), not "this destination doesn't exist" (a hard miss) — the distinction is which failure mode the caveat can actually prevent.
