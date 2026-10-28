---
name: feedback-powerbi-track-own-instructions
description: "Don't ask the user to re-report structure/parameters Claude itself set (originally Power BI table/column structure; generalized 2026-08-23 to all automation params — see global CLAUDE.md rule)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3fddbbf3-3ad0-40e2-8042-a83559aa15a8
  modified: 2026-08-22T21:48:02.948Z
---

When guiding Masaki through Power BI Service changes (he executes clicks in the browser via [[powerbi_migration_gbc_dashboard]] / [[powerbi_migration_gbc_dashboard_koken]] work), do not ask him to confirm or re-describe table/column structure that Claude itself already instructed him to create earlier in the session (e.g. asking "what columns does the 四半期 table have?" when Claude told him to build it with exactly those columns).

**Why:** He said explicitly (2026-07-13): "基本的にあなたに言われたとおりに作っているので、あなた自身がどう作ったのかを必ず覚えておいて指示をしてください。私が再度確認するのは無駄なプロセスです。あなたの言うとおりにやらなかった場合は私から伝えます。" — he follows instructions as given, so re-confirming is wasted process. If he deviated from an instruction, he will say so himself.

**How to apply:** Track what tables/columns/measures/relationships were created via Claude's own prior instructions within the session (and check project memory across sessions) and reference that directly in the next instruction, rather than asking "what does X look like now?" as a first move. Still okay to ask when: (a) something could plausibly have been built differently than instructed (ambiguous step, multiple valid UI paths), or (b) a screenshot/report suggests the actual state diverges from what was instructed — in those cases, asking is warranted and he wants it (he explicitly said he may sometimes be wrong and wants to be asked when that's a real possibility).

**Recurred 2026-07-15** during the 地域/市場/事業区分 slicer rollout to trend pages: Claude asked to re-see DAX for measures (`売上金額_合計`, `売上総利益率`) it had itself specified earlier in the same conversation, and separately a compaction summary dropped a page's measure roster, prompting more re-asks. Masaki's response was pointed: check this memory file (and the wider project memory) BEFORE asking, and proactively write down newly-learned measure/page structure as soon as it's revealed so it survives future compactions and is available in other chats too — see the detailed measure rosters now logged in [[powerbi_migration_gbc_dashboard]]. Treat "I don't have this in context right now" as a cue to read memory first, not a cue to ask the user.

**Recurred again same session, different flavor**: when giving copy-paste DAX for new measures, Claude gave the DAX text but left out which table to add it to, forcing Masaki to ask ("前も言いましたがどこのテーブルが良いかまであなたの方で提案してください"). Rule going forward: **every new-measure instruction must proactively state the target table**, using the established convention already documented in [[powerbi_migration_gbc_dashboard_koken]] ("new measures go in whichever table already holds their closest sibling measures") — e.g. a `_M` display variant of `売上総利益_合計` goes in `Raw YTD` because that's where `売上総利益_合計` itself lives. Never make him ask "which table?" as a follow-up.

**Generalized to a global rule (2026-08-23)**: cross-session log analysis (7/23–8/23) found the same failure mode recurring outside Power BI — e.g. Masaki asking in unrelated sessions "カレンダーのバックアップ期間って今何年でしたっけ" and "メール/カレンダーの更新頻度って今どうなってましたっけ" about sync jobs Claude itself had configured. The PowerBI-only scope of this memory was too narrow. This is now a standing rule in `~/.claude/CLAUDE.md` (global preferences file): whenever Claude sets/changes any automation parameter in any project, write it to project memory immediately so a later "what was this set to?" gets answered from memory, not bounced back to the user. Everything above still applies as the concrete PowerBI case history/evidence for that global rule.
