---
name: feedback_home_infra_no_public_exposure
description: 自宅インフラ(ラズパイ等)はインターネット公開を避け、会社Macも使える経路を優先する
metadata:
  type: feedback
---

自宅ラズパイの設計で、Tailscale Funnel(合言葉付きの公開URL)を提案したら「インターネットに出すのは抵抗がある」と却下された（2026-09-29）。また、個人Macだけに頼る取り込み方式も「リスクを感じる、会社Mac起動時にも取り込めるべき」と却下された。

**Why:** セキュリティ面の心理的な抵抗があること。単一のマシンに依存する構成を避けたいこと。
**How to apply:** 自宅サーバーの機能は Tailscale内/LAN内 に閉じるのを既定にし、公開案は最初から出さない。マシン間の連携を設計するときは、会社Mac(d14461)がTailscale導入不可である点を前提に、両Macで動くかを最初に確認する。移設の手間に見合う価値がなければ「移さない」も選択肢として明示する（web_tips_collectorは移設見送り）。関連: [[home_network_setup]]
