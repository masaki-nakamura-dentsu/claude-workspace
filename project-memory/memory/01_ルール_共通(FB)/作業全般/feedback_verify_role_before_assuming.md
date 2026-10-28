---
name: feedback_verify_role_before_assuming
description: "Don't assume the user still owns/drives a project or account just because a past memory or old thread says so — roles change (handoffs, reorgs); verify against recent data and keep the work-overview memory current"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b8fb3d93-93e1-4986-955c-081a6878f921
---

On 2026-07-15 the user corrected an incident-report-style task list where Claude treated him as actively CC'd-but-passive on the Cybozu Malaysia (Kintone) account, when in fact he'd handed it off to 杉内威允 (Takenobu Sugiuchi) around 2026-07-01 and was now genuinely just occasionally consulted. His feedback: *"あなたはまだ私のやっていることをちゃんと理解していないようです... 現状を正しく理解してください... 改めて過去のやり取りなどを洗い出して、私の業務内容を事細かに理解し、ちゃんと記憶してください。そして新しいメールや新しいチャット内容を使ってその記憶を常にアップデートしてください。"*

**Why**: he moved departments in April 2026 and his project portfolio shifts over time (handoffs, new initiatives picked up, old ones winding down). A snapshot understanding goes stale — assuming an old assignment is still current, or a CC'd thread means active ownership, produces confidently wrong analysis (e.g. wrong task lists, wrong "who does what" framing in drafted docs).

**How to apply**:
- [[gbc_department_move_2026]] is the canonical "what is he actually working on right now" memory — read it before making any claim about his role in a project/thread, and don't rely on older/other memories or a single old thread in isolation.
- When email/Teams data reveals a role change (handoff language like "先週から...案件に入りました", "移管", explicit "後任" mentions, or a project simply going quiet in his direction while continuing elsewhere), update that memory immediately — don't wait to be asked.
- When analyzing "what needs my action" from his inbox/Teams (e.g. task list requests), check To/Cc position (primary recipient vs CC) as a first-pass signal, but corroborate with the actual current-ownership memory rather than assuming CC = passive or To = active, since forwarded/habitual CC chains don't reliably indicate current responsibility either.
- This is a standing, continuous-maintenance expectation, not a one-time fix — treat every session's fresh email/Teams data as a chance to catch drift in the work-overview memory.

See [[feedback_verify_against_ground_truth]] for the broader "check the authoritative source before asserting" pattern this is one case study of.
