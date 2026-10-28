---
name: feedback_company_account_services_any_machine
description: dentsuアカウントで入る社内Webサービス(CCS等)は会社Mac専用と決めつけない。個人Macの9231で入れる
metadata:
  type: feedback
---
2026-10-17、CCSを「会社Macのブラウザでしか入れない」と判断して会社Mac向けにタスクを回したら、中村さんに「個人Macからでも masaki.nakamura@dentsu.co.jp でログインすればよいだけ」と指摘された。

**Why:** メモリに「d14461の9226で入れる」とだけ書いてあり、それを唯一の経路と読んだ。実際は会社アカウントの作業ブラウザが個人Macにもある([[browser-account-routing]] の9231)。
**How to apply:** dentsuアカウントで入るサービスは、まず今いるマシンの会社アカウント用ブラウザ(個人Mac=9231、会社Mac=9226)で試す。マシンをまたぐ依頼にするのは、そのマシンにしか無いもの(ローカルファイル、そのマシン専用のlaunchd等)のときだけ。
