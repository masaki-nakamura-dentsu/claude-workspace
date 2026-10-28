---
name: feedback_ai_tips_slide_title_hyperlink_is_jissirei_url
description: GBC週刊AI Tips発信文言の下書きで使う「実施例」URLは、対象PPTXスライドのタイトル文字列に埋め込まれたハイパーリンクから取得する
metadata: 
  node_type: memory
  type: feedback
  modified: 2026-09-15T23:06:35.848Z
  originSessionId: 298f596f-add3-494d-8ae0-3b2b0fcb8b97
---

[[gbc_weekly_report_kimura_dmd_project]]の週次AI Tips Teams発信文言を下書きする際、本文中の「実施例: <URL>」行に入れるリンクは、ユーザーが手動で用意するのではなく、**対象PPTX（例: `AI_Tips2026年9月分.pptx`）の該当スライドのタイトルテキストに設定されているハイパーリンク先URL**そのもの。2026-09-16、3スライド目「AIペルソナで顧客像を仮想化」のタイトルにChatGPT会話リンク（`https://chatgpt.com/c/...`）がhlinkClickとして埋め込まれていることが判明し、それが実施例リンクだった。

**Why**: 初回の下書きでは実施例URLが手元にないと判断し「出典：」表記のみで代替したが、ユーザーから実際はPPTXのタイトルリンクをそのまま使っていると指摘された。

**How to apply**: 今後この発信文言を下書きする際は、まずPPTXを展開（unzip）し、対象スライドXML（`ppt/slides/slideN.xml`）内の`r:id`（hlinkClick）を`_rels/slideN.xml.rels`で解決してターゲットURLを取得し、それを「実施例:」行に使う。ユーザーに聞いたり「出典」表記で済ませたりする前に、まずこの抽出を試みる。
