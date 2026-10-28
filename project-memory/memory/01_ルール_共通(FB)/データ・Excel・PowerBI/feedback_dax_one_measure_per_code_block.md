---
name: feedback-dax-one-measure-per-code-block
description: "When giving Power BI DAX measures to paste into the browser editor, each measure must be its own separate code block, never multiple measures concatenated in one block"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8b70ac3f-94cb-4b45-8381-cf4a095bf70f
  modified: 2026-09-04T08:33:07.022Z
---

Stated explicitly 2026-09-04, GBC Power BI cover-dashboard work: 「今後、一つ一つコピペできるようにあなたの回答を行って(コピーボタンを押すと全部コピーされてしまう)」

**Why**: the Claude Code chat UI's copy button copies an entire code block at once. The Power BI Service web DAX editor cannot accept multiple `名前 = 式` measure definitions pasted into one measure box (known platform limitation, see [[powerbi_jci_pitch_status_chart]] pitfall #4 — "複数メジューの一括貼り付け不可"). When Claude bundled 2+ measures into a single fenced code block, Masaki's one-click copy grabbed all of them together and the paste failed / had to be manually split, wasting a round trip.

**How to apply**: whenever handing over DAX measures (or any other snippet meant for one-at-a-time paste into a UI that only accepts one unit per paste — same logic would apply to Power Query M steps, etc.), put **exactly one measure per fenced code block**, even if that means many short consecutive code blocks in one message. Never concatenate multiple `名前 = 式` measures into a single block for the sake of a shorter message. This is a durable formatting rule for this project going forward, not a one-time fix.

See also [[feedback_token_conscious_powerbi]] (Masaki does the hands-on Power BI Service work himself, Claude gives copy-paste-ready DAX + click paths) — this memory refines exactly how that DAX should be formatted.
