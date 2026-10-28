---
name: freee-invoice-awit-business
description: ユーザーの個人事業(合同会社AWIT、撮影・映像制作等)のfreee請求書クラウド、見積↔請求の照合方法
metadata: 
  node_type: memory
  type: project
  originSessionId: 8398ab2c-8887-404f-8ba3-180175bec9af
  modified: 2026-08-12T02:39:58.747Z
---

ユーザーは「合同会社AWIT」名義で撮影・動画編集・デザイン等の個人事業を持ち、freee請求書
(`invoice.secure.freee.co.jp`)で見積書・請求書を管理している。主な取引先: メディカル＆アートLab表参道合同会社(寄席オペラ関連)、落語を介して日本文化を広める会、セルビア日本音楽交流推進の会、齋藤友紀氏など。これはGBC/電通の仕事とは別の個人事業。

## アクセス方法
[[shared_bot_browser]] のICPTokyo2022用共有ブラウザ(port 9227)に既にログイン済みタブが存在することがある
(`https://invoice.secure.freee.co.jp/reports/quotations/...`)。無ければそのタブ経由で新規に開く。

## 見積→請求の未請求チェック手順(2026-08-12に確立)
1. 一覧ページのUIテキスト(見積書名・取引先・金額)だけでの突合は不正確 — 件名変更や複数見積のマージなどで
   金額が一致しないケースがあり、誤判定した(例: 寄席オペラ「追加編集作業」5,500円が別の請求書合計と
   偶然一致したが実際は未請求だった)。
2. 正確な方法: ブラウザNetworkで見積一覧ページ読み込み時のXHRをキャプチャすると
   `https://invoice.secure.freee.co.jp/api/p/reports/quotations?cancel_status=uncanceled&per_page=100&page=1`
   というJSON APIが呼ばれている。各見積オブジェクトに `invoices_count` フィールドがあり、
   `0` なら請求書に未変換(=未請求)と確実に判定できる。
3. ただし2023年以前の「旧」ラベルが付いた見積(freee会計から移行されたレガシーレコード、
   `service_name: "accounting"` かつ `invoices_count` フィールド自体が存在しない)はこの方法で判定不能。
   これらは古いfreee会計側の記帳データがそのまま同期されたもので、freee請求書上の紐付け情報を持たない。
   古い案件なので別ルートで既に請求・入金済みの可能性が高い。
4. 個別の見積詳細ページでも確認可能: 詳細画面のタブ切り替え(`select.vb-select__body` から
   `関連帳票` を選択)で「関連帳票はありません」なら未変換、請求書情報が出れば変換済み。
   ただし一覧ページに比べて1件ずつ確認するのは非効率なので、API方式を優先する。

## 2026-08-12時点の調査結果
freee請求書ネイティブの見積(2023年9月以降、30件)のうち7件が未請求(合計588,371円)。
最大2件は2026年の新しい案件(ウズベキスタン公演見積 400,000円、寄席オペラ4/11・4/26分 161,612円)。
残り5件は2023〜2025年の小額案件。詳細はユーザーとの会話ログ参照。

## How to apply
今後「Freeeで見積もりして未請求の案件」等の確認依頼が来たら、まずこのAPI方式(`invoices_count`フィールド)
で一覧を突合する。UIのテキスト突合だけに頼らないこと。

## 見積書の作成をAPIで行う(2026-10-05に確立)
共有ブラウザ(9227)で `invoice.secure.freee.co.jp` のタブを開き、`page.evaluate(fetch)` で呼ぶ。headerは `x-csrf-token`(meta csrf-token) / `x-company-id: 2733491` / `x-freee-client-name: invoice`。ページ外から `ctx.request.post` で呼ぶと401になる。
- 一覧: GET `/api/p/reports/quotations?...`、詳細: GET `/api/p/reports/quotations/{id}`
- 検証用: POST `/api/p/reports/quotations/preview`(保存しない)→ 作成: POST `/api/p/reports/quotations` → 修正: PUT `/api/p/reports/quotations/{id}`
- body: `{quotation_date, subject, quotation_no, customer:{partner_id, name, default_title:"様", ...}, lines:[{line_no,line_type:"item"|"text",line_description,line_tax_rate_id:1,line_unit_price,line_quantity,line_uom_name}], tax_entry_method:"out", tax_fraction:"omit", line_amount_fraction:"omit", withholding_tax_entry_method:"out", template_id:902452, company_name:"合同会社AWIT", company_description:"247-0061\n神奈川県鎌倉市台1980-23"}`。partner_idはトップレベルではなく `customer` の中に入れる(トップレベルだと「取引先を入力してください」で400)。敬称は `customer.default_title` で指定する。省略すると空欄になる。
- 見積番号は YYYYMMDDNN 形式(その日の1件目は01)。
- 齋藤友紀さん(partner_id 99459117、ユーザーは「斎藤由紀」と書くこともある)の単価: 写真撮影5,000円/時間、動画撮影2,000円/時間、交通費は「式」で計上(税10%)。おかし会では「写真データ共有・動画配信設定・記録他」20,000円を加えることがある。自宅の最寄りは北鎌倉駅。北鎌倉⇔浜松町のIC運賃は片道902円(2026-10時点)。

## 見積作成API(2026-10-05確立)
共有ブラウザで `invoice.secure.freee.co.jp/reports/quotations/new` を開いたタブから page.evaluate fetch:
POST `/api/p/reports/quotations`、ヘッダ `X-CSRF-Token`(meta csrf-token) + `X-Company-Id: 2733491` + `X-Freee-Client-Name: invoice`(無いと401)。
Body: `{quotation_date,subject,quotation_no,customer:{partner_id,name,default_title:"御中"},tax_entry_method:"out",tax_fraction:"omit",line_amount_fraction:"omit",withholding_tax_entry_method:"out",template_id:902452,lines:[{line_no,line_type:"item"|"text",line_description,line_uom_name,line_unit_price,line_quantity,line_tax_rate_id:1,line_withholding:false}]}`(トップレベルpartner_idは不可→customer.partner_id)。
見積番号は YYYYMMDD+2桁連番。**複数セッションで同時に見積作成することがあるので、POST直前に一覧を再取得し空き番号を採番・同件名の重複チェックをする。**
単価実績: TokyoLeaves(Crimson Forest, partner_id 121955483) 撮影費8,000円/h・写真修正加工4,000円/h・交通費は実費+管理費20%で計算(※比率・内訳は注記に書かない、[[feedback_quote_hide_markup_ratio]])(北鎌倉⇔湘南江の島 片道415円、北鎌倉⇔和田塚 片道355円=JR155+江ノ電200)。更新は PUT `/api/p/reports/quotations/{id}` に作成時と同じBody。更新前に issue_status/deliver_status を確認し、送付済みなら一言断る。おかし会/イベント系は写真5,000円/h・動画2,000円/h。会場が主催者手配なら「スタジオ費 0円」+注記行。
- 2026-10-05 みなと区民まつり(見積69210219): 待ち時間は請求しない方針(実撮影の時間帯だけ計上)。配信なしの場合は「写真データ共有・記録他」5,000円+「動画編集費」10,000円にした。ユーザーは時間単価の請求対象から待機時間を外すことを好む。
