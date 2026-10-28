---
name: feedback-agency-os-readability-via-structure-not-html
description: Agency OSの読みやすさ改善はHTML出力では解決しなかった(2026-10-19)。ChatGPTは同梱コードを使わず手書き要約HTMLを作り、本体回答も崩れた。ひと手間の変換ページも「少し改善程度」と評価
metadata:
  type: feedback
---
ChatGPT SkillにHTML出力を指示(常時→依頼時、変換コード同梱)したが4回とも手書きHTML・内容欠落。常時指示は通常回答のCHECKLIST/URLも崩した(ただし一部はInstantモードが原因)。貼り付け変換ページ(GBC-Knowledge/tools/AgencyOS_HTML変換.html)は動くが、中村さん評価は「少し改善程度で、ひと手間かけて使うか疑問」→撤回。2026-10-19 中村さん判断: HTML対応は「保留」(将来再検討あり)。回答の型は現状で可、修正不要。

**Why:** 長大SKILL.mdでは出力形式の追加指示が守られにくく、本体品質を下げる。利用者に追加作業を求める仕組みは使われない。
**How to apply:** 読みやすさは回答本体の構成(結論先出し・見出し・表)で改善する。追加の出力形式や手作業ツールを提案する前に、利用者の手間と本体品質への影響を先に評価する。[[feedback_agency_os_no_length_cap]] [[agency_os_deploy_tools]]
