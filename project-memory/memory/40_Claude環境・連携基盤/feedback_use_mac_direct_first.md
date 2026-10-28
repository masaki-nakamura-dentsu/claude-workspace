---
name: feedback-use-mac-direct-first
description: 会社Macから個人Macへの依頼は、まず mac_direct(send.sh)で直接送る。inbox.md(許可待ち)は最後の手段
metadata:
  type: feedback
---
2026-10-23 Euromonitor DLで、個人Macのbulk.js停止を最初 personal_mac_inbox に書いてしまい、ユーザーに「直接止められるシステムを作ったはず」と指摘された。[[mac_direct_instruction]] の `.claude-sync/Scripts/mac_direct/send.sh --wait-min N "指示"` なら送った時点で実行され結果も返る(約1分)。
**Why:** inbox は個人Macで次のセッション開始まで読まれず、止めたい作業には間に合わない。
**How to apply:** 個人Macへの停止・確認・実行依頼はまず send.sh。長時間ジョブの起動やlaunchd登録だけはauto modeで拒否されるのでユーザーのターミナルへ。inboxは「ユーザー許可が要る/急がない」依頼用。
