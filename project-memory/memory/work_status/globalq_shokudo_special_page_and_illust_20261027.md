---
name: globalq_shokudo_special_page_and_illust_20261027
description: Global Q食堂企画(TASTE THE CULTURE 11/16-30)の特設ページ構成案・メニュー別イラスト20枚・最新メニュー反映(2026-10-27)
metadata:
  type: project
---
Status: done (一次納品。KVコピー確定・ファクトチェック待ち)

## やったこと(2026-10-27)
- Teams「カフェコラボ企画について」の濱田さん10/21・10/26共有(最新メニュー表・4カイレイアウト資料)を取得して反映。
- 特設ページ構成案HTML: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/03_GlobalQ/GlobalQ_Private/20260915社食プロジェクト/TASTE_THE_CULTURE_案/特設ページ構成案_TASTE_THE_CULTURE_20261027.html`
- イラスト: 同フォルダ `POP_豆知識/`(白背景原本)と `POP_豆知識/透過PNG/`(白背景除去・簡易)。3キャラ(海外はじめ/陽気ポカ夫/国際麗子)が各メニューを食べる絵を20枚(+承認済みジャンバラヤ)。生成スクリプト `~/.local/share/claude-playwright/gen_eating_batch.js`(ChatGPT、9226、4タブ並列。承認済みPOPの絵を画風参照、キャラPNGを添付)。
- 構造: 飯ランガイド→「テイストカルチャー」ハブ→①食堂企画(期間限定) ②飯ランガイド(常設)。

## 最新情報の要点
- 卓上POP: 11/13設置〜11/30夕方回収、期間中ランダム設置、設置回収はGlobal Q側。関西不可、中部11/26のみ。
- 4カイWESTグローバルメニュー19品+EAST2品(棒棒鶏サラダ・バインミー)。追加: 回鍋肉丼・カリフォルニア風ちらし寿司・コームーヤーン・焼味飯。
- 要確認: フォーが「タイ」表記、11/23-24赤塗り、17→21メニュー、関西ランチ4種の残り1種。

**Why:** 食堂企画の告知・POP・特設ページ制作。**How to apply:** 続きは卓上POP全メニュー分の組版(.ai)、ページ実装、豆知識のファクトチェック。

## 2026-10-27 追加指示(企画構成OK後)
- 構成OK。電通拠点紹介は必須でなく、**Global Q内の関連記事(例:インド料理→インド駐在員インタビュー)へリンク**。先にGlobalQサイト構成をクロールして理解。
- 企画9「みんなで世界を食べよう」は**やらない**(ページから削除)。
- フォー=**ベトナム**に確定。日付・国名はOK。11/23-24は提供なし。KVコピーは濱田さん返答まだ。
- **21品で作る**(豆知識も21)。豆知識の**出典確認は自分で**行う。
- イラストは**全て違うポーズ**(ガツガツ、頬を赤らめて喜ぶ等)で再生成。
- SharePointページ制作を自分でできるか打診あり。トークン過大なら原稿のみ作り本人が作業。

## 2026-10-27 実施結果(追加指示分)
- Global Qをクロール(SharePoint REST、573ページ)。構成=左メニュー「始めようグローバル！」(メシランガイドはここ)/「日本の世界のdentsu人発見」(What's up?・駐在員インタビュー)等。国別関連記事マップを作成(MajorVersion>=1で公開確認。タイの760は未公開→761を使用)。マレーシアは専用記事なし。
- 企画9を削除。豆知識21本を出典確認(WebSearch)、諸説あるものは「〜とされる」に。ジャンバラヤPOP文面(フランス語→プロヴァンス語)は修正案のみ提示(承認済みなので未変更)。
- イラスト20枚を全て違うポーズで再生成: `POP_豆知識/v2_ポーズ違い/`(+透過PNG)。旧版は `POP_豆知識/` 直下。スクリプト `~/.local/share/claude-playwright/gen_eating_v2.js`(同時2タブ推奨。4タブだと2コマ混入が出た)。
- 構成案HTML: `..._20261027_02.html`(旧版は別名で残置)。
- SharePointページ制作は未着手(本人の判断待ち)。共有サイト変更は明示許可が必要。

## 追記（2026-10-27 turn3）SharePoint下書き作成（ユーザーがREST作成を明示許可）
- 下書きページ作成済み（未公開）: id=764 / https://esq365.sharepoint.com/sites/globalonedentsu/SitePages/TASTE-THE-CULTURE-食堂企画（下書き）.aspx
- 画像21枚(JPEG約2MB合計)は SiteAssets/TasteCulture2026/tc_{key}.jpg にアップロード。ページ内はURL参照（base64埋め込みなし）。
- 作成スクリプト: ~/.local/share/claude-playwright/tc_make_draft.js（`PAGEID=764 node tc_make_draft.js "<title>"` で内容を上書き保存）。データは scratchpad/tc_data.json。
- 重要: このテナントの savepage は CanvasContent1 を「HTML」ではなく「JSON配列(controlType 4/3)」で受ける（HTMLだと JsonReaderException）。
- 構成: ヒーロー/企画について/開催概要/カレンダー表/メニュー図鑑21(左画像4+右本文8、関連記事リンク)/食べる3人/もっと知りたい方へ/出典。ジャンバラヤは修正案の文面を使用。内部メモ(要確認等)は載せていない。
- 未実施: ハブページ(テイストカルチャー)作成、ナビ変更、公開。既存ページには一切触れていない。
Status: done（下書き作成まで）

## 追記（turn4）公開ページ(TASTE-THE-CULTURE.aspx, id=765)にカレンダー→図鑑ジャンプリンクを追加（ユーザーが明示許可）
- アンカー=H3見出し文字（空白→「-」）。表セル20か所(18品)に `<a href="#エンコード見出し" data-interception="off">` を付与。検証: 20リンク全て遷移先あり、クリックで該当カードへ移動。
- 方法: CheckOut→リストアイテム CanvasContent1 を MERGE（HTMLのまま）→CheckIn(major)。※savepage はJSON専用。バックアップ: scratchpad/tc_live_backup_20261027.json。スクリプト: ~/.local/share/claude-playwright/tc_link_calendar.js。
- 未リンク: 表外注記のティッカマサラ/棒棒鶏/バインミー（必要なら対応）。ユーザーが公開後にレイアウトを3カラム等へ編集済み。
- ジャンプURL一覧: TASTE_THE_CULTURE_案/メニュー図鑑ジャンプ先URL_20261027.md
Status: done
