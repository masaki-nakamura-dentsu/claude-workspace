---
name: feedback_sync_check_scope
description: "'同期確認して' type requests cover email + calendar + Teams + Facebook Messenger together as one topic, not just email/calendar"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ac8045b6-6dee-4de2-8f92-3f40483d2d01
  modified: 2026-08-01T23:13:00.350Z
---

When the user asks to check whether sync/data capture is working ("メールやカレンダーなどなど。同期がうまく行っているかを確認して" or similar), treat **email (Outlook), calendar, Teams messages, and Facebook Messenger** as one combined scope by default — check all four, not just the ones explicitly named.

**Why**: stated explicitly by the user (2026-08-02) after a session where Claude checked email/calendar/Teams but the user then had to separately ask about Facebook Messenger. The user said future sync-check requests should be understood to include Facebook Messenger in the same breath.

**How to apply**: see [[continuous_data_capture_setup]] for email/calendar/Teams pipeline details and [[facebook_messenger_export_setup]] for the Facebook pipeline. When asked to check sync health, check the launchd job status/logs and actual data freshness for all four channels in one pass, not sequentially across multiple user prompts.
