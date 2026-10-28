---
name: teams-self-chat-autopost
description: "Reusable script to post messages into Masaki's own Teams self-chat via the shared bot browser; currently scoped to auto-posting every response during the Power BI Desktop / Salesforce migration task"
metadata: 
  node_type: memory
  type: project
  originSessionId: d4c639f0-5e2e-444f-aef8-00fa7bd9a949
  modified: 2026-08-07T06:59:02.450Z
---

Built 2026-08-07 because Masaki is working on Power BI Desktop inside a Windows 365 virtual PC (via Windows App on Mac) and clipboard copy/paste between the Mac (where this chat runs) and the remote Windows session doesn't work reliably (likely blocked by the Microsoft Purview DLP agent on the Mac — see the Windows App clipboard troubleshooting earlier in that session). Posting responses into his own Teams chat lets him read them from the Teams client inside the Windows 365 session without needing clipboard sharing at all.

**Scope**: Masaki asked for this "このPower BI Desktop作業に限り" — limited to this Power BI Desktop / Salesforce object-connector migration task specifically, not a general standing rule for all future work. Don't auto-post responses from unrelated tasks/projects unless he asks again.

**Refined 2026-08-07 same session**: not literally every response — only post content that's actually worth copy-pasting (concrete instructions, formulas/code, confirmed findings, decisions) since he's reading this from the Windows 365 VM's Teams client as a substitute for clipboard sharing. Skip short acknowledgements or pure back-and-forth chatter. Use judgment per turn rather than a fixed rule of thumb.

**Script**: `~/TeamsExport/post_self_chat.py` — `python3 post_self_chat.py "message"` (or pipe via stdin). Connects to the shared bot browser (see [[shared_bot_browser]], port 9226) which must already have a Teams tab open and logged in; does not launch or close any browser itself. Finds the chat list item containing "あなた" (marks the self-chat) and sends via the message compose box, using `Shift+Enter` per line then a final `Enter` to send (plain `fill()` doesn't work reliably on Teams' rich-text contenteditable box).

**Verified working** 2026-08-07 with a test message that appeared correctly in the self-chat.

**Related**: this reuses the SAME browser/profile as [[powerbi_migration_gbc_dashboard]]'s Salesforce object investigation — Teams was added as a second logged-in tab in that browser per [[shared_bot_browser]], rather than a separate dedicated profile.
