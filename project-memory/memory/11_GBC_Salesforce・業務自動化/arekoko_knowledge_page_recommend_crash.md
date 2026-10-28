---
name: arekoko_knowledge_page_recommend_crash
description: アレココKnowledge.aspxが読み込み中のまま止まる不具合の原因(おすすめ登録記事の非公開化)と直し方。2026-10-16修復
metadata:
  type: project
---
2026-10-16、中牧さん(ITチケットINC1813827)から「10/8以降Knowledge.aspxが読み込めない、中村の10/8サイトのページ列追加が原因か」と問い合わせ。
- 原因: ページはカスタムSPFx「アレココ検索パーツ」1つだけ。「ナレッジリーダーのおすすめ」枠はリスト KnowledgeLeaderRecommend(96256048…)の itemIdId で Knowledges(359aef33…)を1件ずつ `publishStatus eq 1` 付きで取得し、結果[0].thumbnailImage を読む。増永さんが10/8 9:32にナレッジID117(2025年版ベトナム広告事情)を非公開化→空配列→`Cannot read properties of undefined (reading 'thumbnailImage')` で描画全体が止まった。
- 10/8に中村が行った「サイトのページ」の対象ユーザー機能有効化(列 _ModernAudienceTargetUserField 等の追加)は無関係。ページは別リストしか参照していない。
- 修復: KnowledgeLeaderRecommend の項目ID2(→117)を中村アカウントでREST recycle(ごみ箱、復元可)。表示回復を確認済み(おすすめ113・118、よく見られています等が表示)。ユーザーの明示許可あり。
**How to apply:** 再発したら、おすすめ・よく見られています系のリストに非公開/公開期間外/削除済みのナレッジIDが残っていないか見る。Webパーツ側は空結果を想定していない作りなので、記事を非公開にする際はおすすめから先に外すよう運用で注意。調べ方はBotブラウザ(9226)でページを開きpageerrorを拾うのが速い。関連: [[gbc_kpikgi_sharepoint_export]] [[feedback_sharepoint_permission_change_needs_explicit_ok]]
