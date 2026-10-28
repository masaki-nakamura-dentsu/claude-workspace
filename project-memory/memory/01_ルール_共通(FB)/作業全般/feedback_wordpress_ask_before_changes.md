---
name: feedback_wordpress_ask_before_changes
description: masakinakamura.com (WordPress)への書き込み系操作(メディアアップロード・投稿・ページ編集など)は、内容や規模にかかわらず必ず事前に本人の許可を取ってから実行する。標準ルール。
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f6d2b3e6-853a-449d-89e0-8e51ee85dd46
  modified: 2026-07-29T23:42:27.280Z
---

2026-07-29、Instagram自動投稿のための画像公開URLホスティング先としてWordPressのApplication Password(ユーザー名`maxakisan`)を発行してもらった際、本人から明示的な指示:

> 「必ずページ改変の際は私に許可を取ってください。私のサイトを守ることを最大限に考えてください。」

**Why**: masakinakamura.com は本人の写真家としての公開サイトであり、意図しない変更や誤操作による毀損を強く懸念している。単なる「投稿・ページ」の改変だけでなく、メディアライブラリへのアップロードのような一見軽微な書き込み操作も含めて、事前確認なしに実行すべきではないという趣旨と解釈する。

**How to apply**:
- WordPress REST API(またはその他の手段)でmasakinakamura.comに対して行う**あらゆる書き込み系操作**(メディアアップロード、投稿作成・編集、固定ページ編集、テーマ/プラグイン設定変更など)は、実行前に必ず「これから具体的に何をするか」を説明し、本人の明示的なOKをもらってから実行する。
- 読み取り専用の確認(認証テスト、既存コンテンツの閲覧など)は都度の許可なしに行って良い。
- 一度許可を得た操作でも、対象や規模が変わる場合(例: 1枚のテストアップロード→本番の複数枚アップロード)は改めて確認する。
- Application Password自体(`~/Scripts/.env.wordpress`等に保管)は本人発行のものをそのまま使うが、これを使った書き込みは上記ルールの対象。

関連: [[personal_sns_management_project]](Instagram自動投稿でWordPressを画像ホスティングに使う計画の一環として発行された経緯)。
