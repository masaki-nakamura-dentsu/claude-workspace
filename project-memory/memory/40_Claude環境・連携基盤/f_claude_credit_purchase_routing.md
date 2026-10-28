---
name: f_claude_credit_purchase_routing
description: Claudeのクレジットを案内・購入するときは、Console(API)とclaude.ai(サブスク使用クレジット)を区別して案内する
metadata:
  type: feedback
---

2026-10-22、ClaudeCodeのクレジットを購入したが claude.ai の使用量画面に反映されなかった。購入先が Console（platform.claude.com、API クレジット）だったため。

**Why:** Console のクレジットは API 課金専用で、Pro サブスクでログイン中の Claude Code や claude.ai 使用量には使われない。案内する側が購入先の違いを明示しなかった。

**How to apply:**
- クレジット購入を案内するときは、必ず2種類を区別する。
  - claude.ai 設定 > 使用量 > 「使用量を追加購入」: Pro 枠を超えたときに使う使用クレジット。サブスクログインのまま Claude Code でも消費される。
  - Console(platform.claude.com) Billing: API クレジット。Claude Code では `/logout` → `/login` で Console account を選ぶか ANTHROPIC_API_KEY が必要。
- 購入前に、どちらの用途か（サブスクのまま使いたいか、API 課金に切り替えるか）を確認し、URLもそれに合わせて案内する。
- 枠不足時のみ API に切り替える運用。CLAUDE.md/memory/settings/hooks は切替後も引き継がれる。claude.ai コネクタは影響の可能性あり。

関連: [[mcp_on_demand]]
