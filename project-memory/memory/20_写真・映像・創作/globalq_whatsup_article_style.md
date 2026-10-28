---
name: globalq-whatsup-article-style
description: Global Q「What's up 海外拠点 オフィス・日常のリアルレポート」記事化の型と保存場所
metadata:
  type: project
---
駐在員から届くネタpptxを、公開済み記事の文体で原稿化する連載(第8回UK小関さん、第9回タイ中島さん=2026-10-15原稿化)。
- 型: タイトル「what's up <国>」/ キャッチ「〇〇 ー From Dentsu <拠点>」/ 氏名・所属 / ※レポートは<年月>時点 / 「皆さん、こんにちは。」で自己紹介+仕事外の過ごし方+「私目線のレポートを」/ 見出し付き本文(会社紹介「〜って、どんな会社？」等) / 中盤に「ここで、Global Q編集部から突撃リクエスト！　🍴〇〇さんのランチ事情、教えてください！🍴」/ 「〜の今のトレンドや空気感」小見出し3つ / 「最後に、dentsu Japanの皆さんへ」で締め。です・ます、一人称、軽い「！」や「、、」可。
- 公開ページはSharePoint globalonedentsu/SitePages、ログイン要→共有ブラウザ(9226)で innerText 取得できる。
- 保存先: Work共有作業系/戦略企画部/Global Q/4_格納コンテンツ関連情報/2.2_What's up海外拠点(インタビュー)/オフィス・日常のリアルレポート（2024- ）/第N回_氏名_国/ 。過去は AI記事化_完成原稿.docx 形式。写真はpptxのキャプションを［写真］行として本文中に配置。
Related: [[globalq_access_report_workflow]]
- 写真入りWordはpptxのppt/media画像を1200pxに縮小してpython-docxで挿入(原寸だと40MB→縮小で約4MB)。会社Macのvenv ~/.venvs/docwork(python-docx, pillow, pymupdf)。LibreOfficeでの確認は游ゴシックが無く和文が消えるが配置確認には使える。
- 第9回タイ(中島さん)最新版は AI記事化_原稿_20261015_02.md/.docx(原文寄り・写真22枚入り)。2026-10-15に編集者確認へ。オフィス内/Pink Garden写真は未着。
- ChatGPTでやる場合の指示: pptx添付+過去記事本文を貼付(SharePointはChatGPT不可)、「同じ構成・文体で」「原文の言い回しを残し要約・言い換えしない」「ネタに無い事実を足さない」「キャプションは［写真］で」。
