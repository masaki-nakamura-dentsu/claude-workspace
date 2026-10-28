---
name: feedback-token-conscious-powerbi
description: "User wants to do Power BI Service browser-UI work himself going forward (not Claude), specifically to reduce token consumption on click-by-click/screenshot-heavy tasks"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d7f53e41-8432-433c-aba7-837be4ddc097
  modified: 2026-09-29T06:14:45.515Z
---

Stated explicitly 2026-08-17, mid-conversation, right after a long CAS-automation build: 「あなたが作業をするとトークンの消費が激しいのでやっぱり私の方で作業をするようにしよかなと思います」— decided to take over the hands-on Power BI Service work himself (see [[powerbi_migration_gbc_dashboard]] for the project this applies to) rather than have Claude drive the browser through it.

**Why**: driving Power BI Service (or similar click-heavy web UIs) via browser automation/screenshots is token-expensive — lots of round-trip screenshots/DOM dumps per small UI step. He noticed the cost and wants to change how the work gets split.

**How to apply**:
- Default to giving DAX formulas, click-path instructions, and explanations as text for him to execute himself, rather than reaching for browser automation on Power BI Service (or similarly UI-heavy, low-automation-value tools) unless he explicitly asks Claude to drive it.
- Tips already given when this came up, worth repeating if he asks again: split unrelated topics into separate sessions rather than one long thread (old context re-processes every turn), ask for narrow/targeted screen info rather than "show me everything," skip spawning research subagents for small lookups.
- This is a preference about *how much of the hands-on execution Claude does*, not a withdrawal from the project — still help with planning, DAX, troubleshooting explanations, etc., just don't default to operating the browser for him now.
- Not an absolute ban — if he explicitly asks Claude to drive the browser for a specific Power BI step again, that's fine; this is a default-mode change, not a hard rule against ever doing it.

See [[feedback_token_conscious_practices]] for the broader cross-project pattern this is one instance of (2026-08-31統合).

**Recurred 2026-09-29 ([[gbc_business_trip_management_powerbi]] fix session)**: mid-investigation, after Claude had already used the shared bot browser to (a) search Power Automate's flow list for a daily "表示対象更新" flow and (b) start navigating to Power BI Service to check whether a "新しい列" button exists before giving instructions, the user interjected twice — first a soft check on the Power Automate browsing ("何度も試しているようですが、私の方で確認したほうが良ければ言って下さい"), then a direct stop on the Power BI Service attempt ("わざわざあなたがPowerBI開く必要ありません" / "言葉で伝えて下さい"). **Key refinement**: earlier browser use in the *same* conversation (reading a flow-export zip the user handed over, or one round of searching a flow by name) does not imply standing permission to keep reaching for the browser for the *next* step (checking a UI button exists) — each new browser excursion should be re-judged against this rule, especially once the conversation has shifted from "diagnose what's broken" to "how do I do X" (the latter phrasing is itself a signal the user wants the text/click-path answer, not Claude driving). When uncertain whether a specific UI label/button exists (e.g. whether calculated columns are addable via Power BI Service web modeling for a Pro-only tenant), it's better to give the best-known instructions with an explicit "if this button isn't there, tell me and we'll find another way" caveat than to open the browser just to verify the label first.
