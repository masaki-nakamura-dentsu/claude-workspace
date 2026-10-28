---
name: feedback-verify-message-direction
description: "Always confirm who actually sent a Teams/email message (not just which conversation it's in) before describing what it means — getting sender vs. recipient backwards inverts the meaning entirely"
metadata: 
  node_type: memory
  type: feedback
  modified: 2026-07-27T09:53:39.820Z
  originSessionId: cc64e5ab-3b2b-493d-9622-597e1ccdd273
---

Misread a Teams message on 2026-07-27: found a message in the "塚口 和之 Kazuyuki Tsukaguchi" 1:1 chat quoting the 業務指示書 KGI/KPI table and asking about dJIB Q2 numbers, and reported it to Masaki as "塚口さんが中村さんに尋ねている" (Tsukaguchi asking Masaki). The record's `author` field actually said `中村正樹` — it was Masaki asking Tsukaguchi, the exact opposite direction. Masaki caught it and corrected me.

**Why this happened**: I inferred sender from the `chat` field (the name of the 1:1 conversation) instead of checking the record's own `author` field. The chat name only tells you *whose conversation this is*, not *who sent this particular message* — in a 1:1 chat either party's messages carry the same chat name.

**How to apply**: before stating who said/asked/reported something from a Teams or email record, explicitly read and state the `author`/`from` field of that specific message — never infer it from the chat/subject name, thread context, or what would "make narrative sense." If `author` is null (common in this Teams export, see [[local_work_data_export]]) and direction genuinely can't be determined, say so explicitly rather than guessing — a wrong direction is worse than an admitted unknown, since the user may act on the (inverted) meaning (e.g. thinking they're still owed an answer when they actually owe one, or vice versa).

Masaki's own words on this: "送信者や受信者など間違えると全く違う意味になるので今後間違えないように注意してください" (getting sender/recipient wrong completely changes the meaning — be careful not to repeat this).

See [[feedback_verify_against_ground_truth]] for the broader "check the authoritative source before asserting" pattern this is one case study of.
