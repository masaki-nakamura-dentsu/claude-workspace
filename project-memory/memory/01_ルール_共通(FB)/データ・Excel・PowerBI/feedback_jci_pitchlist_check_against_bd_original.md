---
name: feedback-jci-pitchlist-check-against-bd-original
description: 日系ピッチ案件リスト(JCI)で重複/インポートミスを疑う場合、最新Salesforceエクスポートだけでなく前月BD部提出ファイル(原本)とも突合すること
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c0bd0667-0e07-4b0f-89a7-bfbe566e8fc4
  modified: 2026-09-30T04:43:55.501Z
---

日系ピッチ案件リスト(JCI turnaround report)で案件の重複や不審な差分を調べる際は、`verify_against_source.py`によるSalesforce最新エクスポートとの突合だけでなく、前月にBD部から提出された原本ファイル（`BD部集約_JPターンアラウンド/BD部提出済み/`配下、例: `20260917_★9月提出用_日系ピッチ案件リスト.xlsm`）とも必ず突き合わせること。

**Why:** BD部提出ファイルが「原本」であり、そこから今月版への転記・インポート時にミスが起こり得るため。Salesforce最新エクスポートとの一致だけでは、案件が意図通り新規追加されたのか、誤って重複登録されたのかを判断できない。

**How to apply:** 見かけ上の重複（同一クライアント/ブランド/市場で案件名が酷似する2件など）を見つけたら、
1. 両方の案件IDでSalesforce最新エクスポートと突合(`Pythonインポート変換/verify_against_source.py`、AO:BU列のみ対象)。
2. 前月BD部提出ファイルの「A__既存案件」シートと「B__新規案件」シート両方を、案件ID(A) or 案件名(Bは新規のためID未付番)で検索し、片方が前月時点で「B__新規案件（→追加）」として既に提案されていたかを確認する。
3. 前月のBシートに新規提案として存在し、今月Salesforce側でIDが付番されAシートへ移動しただけであれば、重複ではなく正当な新規→既存への移行(B→A移管)。[[jci_pitchlist_deletion_condition_check_202609]]のHartz案件と同じパターン。

**実例(2026-09-30, 10月依頼用リスト):** A__既存案件シート26行目「JTI Global Branding」(a1hfP00000EcR18)と36行目「JTI Global Ploom Branding」(a1hfP00000HLoT7)が重複に見えた。前月原本`20260917_★9月提出用_日系ピッチ案件リスト.xlsm`を確認したところ、Aシート51行目に既存案件として「JTI Global Branding」、Bシート19行目に新規提案として「JTI Global Ploom Branding」(ID未付番)が別々に存在しており、今月Salesforce側でHLoT7が付番されAシートへ移動しただけと判明。重複ではなくユーザー確認済み。
