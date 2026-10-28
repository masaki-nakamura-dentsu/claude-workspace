---
name: chatgpt-clear-recommend-custom-instructions-test
description: ChatGPTカスタム指示で「新しいチャットを勧める(/clear相当)」を再現する検証(2026-10-22)。91往復でも発動せず、テーマは見送り
metadata:
  type: project
---

GBC局員向けAI Tips案として、ChatGPTのカスタム指示（英語）に「会話が長い/話題が変わる/忘れが出たら新しいチャットを勧め、要約と最初の文を出す」を入れて検証した。

**結果（2026-10-22）**: 指示は読み込まれている（原文を引用できた）が、25往復・91往復（同一話題、長文貼り付け約30回）でも一度も発動せず。最初の決定事項（日程・会場・担当・人数・予算）は最後まで正答＝劣化なし。ChatGPTは往復数を数えられず、文脈も大きいため自発提案は成立しにくい。

**判断**: 本人は「このテーマは見送り」。合言葉方式(Handoff)は本人が気づけないので不可、話題切替トリガーも不要と判断。Tipsにするなら「ChatGPTは長くても劣化しにくい。話題が変わったら自分で新チャット」程度。

**検証手法メモ**: 共有bot browser(9226)で chatgpt.com にログイン済み。`?temporary-chat=true` でもカスタム指示は効く。2026-10の入力欄は `div.ProseMirror[role=textbox]:visible`、送信は `button[aria-label="送信"]`、応答は `main` の innerText 差分で取る（`data-message-author-role` は使えない）。関連: [[chatgpt_web_automation]] [[shared_bot_browser]]
