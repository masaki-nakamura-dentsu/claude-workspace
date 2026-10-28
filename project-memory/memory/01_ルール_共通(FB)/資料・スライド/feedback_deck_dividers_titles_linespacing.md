---
name: feedback-deck-dividers-titles-linespacing
description: 電通テンプレPPTXは章ごとに扉(Section divider layout)を入れ、タイトルはテーマ名(〜について)、行間は1.3前後で読みやすくする。AIっぽさが強いと指摘された
metadata:
  type: feedback
---
GBC向けAI活用Tips資料(2026-10-23)で指摘: 「全体的にAIっぽさが強い。タイトルの作り方やデザイン、特に行間が読みにくい」「扉ページをスライドマスターの適切なデザインで入れる」。

**Why:** 結論や煽りを含むタイトル(「〜は、こう作った」「〜を、1つの形に揃える」)と、行間1.0〜1.05の詰まった本文がAI臭の主因。章の切れ目が分かりにくいと読みにくい。
**How to apply:**
- 電通テンプレから作るときは、章ごとに `Section divider-01〜06` レイアウトの扉(「01  章名」)を入れる。最後の締めは `Section divider-black`。
- タイトルは「〜について」のテーマ名。結論は本文に書く。[[f_ai_smell_avoidance]]
- 本文・カードの行間は1.3、段落後6pt。見出しだけ1.1。
- 保存前に sectionLst・未使用レイアウト・マスターの番号先頭「0」(レイアウト側も)を削除。[[feedback_pptx_prune_unused_sections]]
- 参考: Work/Client/Nidec/作業履歴フォルダ/build_gbc_tips_20261023.py
