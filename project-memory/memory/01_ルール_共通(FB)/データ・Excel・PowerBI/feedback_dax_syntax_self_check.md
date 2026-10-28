---
name: feedback-dax-syntax-self-check
description: "User explicitly flagged repeated DAX syntax mistakes (2026-09-10) — verify DAX/M-vs-DAX syntax mentally before sending a query for the user to run, since each round-trip costs their time"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 0641b86e-2de5-4ad8-809b-1fb68d58f3d9
  modified: 2026-09-10T11:04:33.351Z
---

During [[qbr_powerbi_case_collision_investigation_20260910]] (2026-09-10), sent the user several DAX queries in a row with avoidable syntax errors: unquoted Japanese table names in DAX Query view (already documented as a known trap in [[powerbi_gbc_dashboard_current_state]]§5-11, but repeated it twice more the same session), used M's `or` keyword instead of DAX's `||`, and got `SUMMARIZECOLUMNS` argument order wrong (filter args must precede name/expression pairs). User said directly: 「ミスが多くなっています。注意して下さい。」

**Why**: Each mistake means the user runs a broken query in Power BI, gets an opaque error, and has to paste it back — a full round-trip lost to something checkable in advance. This project's Power BI work already runs through the user (not Claude driving the browser, per [[feedback_token_conscious_powerbi]]), so every query is already an extra hop; syntax slips multiply that cost.

**How to apply**: Before sending any DAX query for the user to run (in this or any Power BI project), mentally re-check against the known DAX gotchas already catalogued in [[powerbi_gbc_dashboard_current_state]]§5 (Japanese table names need `'...'` quoting in DAX Query view; VAR names must be ASCII; `IF` can't branch on tables; M-only syntax like `or`/`each`/`let` doesn't exist in DAX — DAX uses `||`, lambda-free `FILTER`, no `let`) — and double check multi-argument function call ordering (e.g. `SUMMARIZECOLUMNS(groupBy..., filterTable, "name", expr...)`) against the real signature rather than typing from memory. A brief self-read of the query before pasting it into a reply is cheaper than a round-trip.
