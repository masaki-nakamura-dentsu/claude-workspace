---
name: feedback-check-latest-state-before-citing-blockers
description: 過去メモリの「ブロック中/未解決」を現状として断言しない。最新の本番切替記録やユーザーの実感と突き合わせてから言う
metadata:
  type: feedback
---
2026-10-06、HDY定点観測でSalesforce依存の相談を受けた際、`powerbi_gbc_dashboard_current_state`内の古い記述(2026-08-07時点「Service側SF OAuthが未承認で自動更新不可」)を現状として回答し、ユーザーに「既に1日2回自動更新している」と訂正された。同じメモリ群には08-19〜25に`GBC__c`直結へ本番切替済みの記録もあり、突き合わせれば気づけた。

**Why**: 長期プロジェクトのメモリは古い「Still open」行が残りやすく、新しい解決記録と混在する。古い方を拾うと誤った制約をユーザーに伝え、不要な代替案まで提案してしまう。

**How to apply**: 「〜はまだできない/承認待ち」と言う前に、同じテーマのメモリで日付が新しい記述(本番切替・完成・検証済み)を必ず検索し、矛盾があれば新しい方を優先するか、断定せず「記録上は〜だが現状はどうか」とユーザーに確認する。関連: [[feedback_verify_against_ground_truth]] [[powerbi_gbc_dashboard_current_state]]
