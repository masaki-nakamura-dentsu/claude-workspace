---
name: freee-accounting-internal-api-registration
description: freee会計(合同会社AWIT)に取引・証憑を共有ブラウザのセッション経由の内部API(/api/p)で登録する手順（画面操作・スクショ不要）
metadata:
  type: reference
---
2026-10-05 ベトナム出張経費24件を登録した際に確立。[[shared_bot_browser]] (port 9227) で secure.freee.co.jp にログイン済みのタブから `page.evaluate(fetch)` で叩く。CSRFは `meta[name=csrf-token]` を `X-CSRF-Token` に。company_id=2733491。
- 読取: GET `/api/p/deals?company_id=…&deal_type=expense&limit=100`, `/api/p/deals/standard/{id}`, `/api/p/account_items`, `/api/p/walletables`, `/api/p/wallet_txns?walletable_id=…&start_date=…&end_date=…`
- 証憑アップ: POST `https://filebox.secure.freee.co.jp/api/p/files/upload`(FormData `file`, credentials:include) → file_uuid → POST 同ホスト `/api/p/files/register` JSON `{file_uuid,description,document_type:"receipt"}` → `{id}`（`/api/p/receipts_v2.json` は404）
- 取引作成: POST `/api/p/deals/standard` JSON `{type:"expense",issue_date,ref:"",receipts:[{id}],details:[{account_item_id,amount,description,tax_code,tax_entry_method:0,partner_id:0,default_tag_ids:[]}],payments:[{amount,date,from_walletable_id,from_walletable_type}]}`。個人立替(役員借入金)は `from_walletable_type:"private_settlement_item"`, `from_walletable_id:437478288`(役員借入金の勘定科目ID)。
- 口座明細から登録(消込): **PUT** `/api/p/wallet_txns/{id}/reconcile` JSON `{from:"new_version",from_nde:true,reconcile:{editing_deals:[],existing_deals:[],wallet_txn_id,new_deal:{deal:{issue_date,line_items:[{account_item_name,default_tags:[],description,tax_entry_method:0,tax_name,type:"positive",unit_price,vat:0,vat_system_calc:0,partner_name:""}],receipt_ids:[id],ref:""},payment_walletable:"<口座名>"}}}`
- ID: 旅費交通費437478231 / 会議費437478230 / 交際費437478229 / 役員貸付金437478287。税区分コード: 対象外2, 課対仕入10%136, 課対仕入（控80）10%189, 課対仕入（控50）8%（軽）188。口座: PayPay(AWIT)3904016, PayPay役員口座2785644, 楽天カード1504291, 現金3087924。
- 過去の記帳パターン: 中村さん個人払い→役員借入金決済、食事は会議費、海外支出は対象外。2026/10以降の非インボイス仕入はfreee上「控70」（下の2026-10-12追記参照。当初「控50」と書いたのは誤り）。
- 注意: auto modeの分類器はfreeeへのPOSTを初回拒否する。ユーザーの明示許可（2026-10-05「Freeeへの書き込みを許可します」）を得てから実行。まず1件登録→GETで読み戻し確認→残りを一括、の順。セッションは数日で切れるのでログイン画面を前面表示してユーザーにログインしてもらう。

## 追記 2026-10-12（修正待ちリスト対応で確認）
- 取引削除: `DELETE /api/p/deals/{id}`（`/deals/standard/{id}` は404）。読取は `GET /api/p/deals/standard/{id}`（口座振替は `/api/p/deals/transfers/{id}`）。
- 口座振替 `POST /api/p/deals/transfers` は口座同士だけ。役員借入金との振替は不可なので、収入取引（details=役員借入金437478288、payments=現金 wallet 3087924）で「借方 現金／貸方 役員借入金」を作る。
- 総勘定元帳: `GET /api/p/reports/general_ledgers/show?fiscal_year_id=…&fiscal_year=…&name=<科目名>&start_date&end_date&from_report=true`（年度IDが期間と合わないとエラー）。年度ID: 2026年度(2026/6〜)11931602 / 2025年度9935933 / 2024年度8484867 / 2023年度6029959。
- 修正待ちリスト: 一覧 `GET /api/p/incorrects?params[status]=not_corrected…`、再チェック `POST /api/p/incorrects/refresh`。項目ごとの無視はできない。チェック項目のオンオフは会社設定画面(company/detail)の「修正待ちリストの設定」→ `PUT /api/p/companies/details/incorrect_list` `{company:{disabled_types:"[…]"}}`。2026-10-12時点で無効化: MinusBankAccount / UnpaidOfficerLoan / SmallAmountInvoiceExemptible。
- **AWITは消費税「免税」・税込経理**。仕入の税区分（控80/控70/控50、少額特例）は税額に影響しない。
- **訂正**: 2026/10以降の非インボイス仕入の経過措置はfreee上「控70」（上の「控50」の記述は誤り）。10/5に登録した手土産4,644円(10/1)は控50のまま残っている。免税なので実害はなく、未修正。
- 証憑を既存取引に添付: `POST /api/p/deals/{deal_id}/receipts/{receipt_id}/attach` `{from_receipt_id}`。未登録証憑の一覧: `GET /api/p/receipts_v2?category=without_deal…`。
- 口座の明細: `GET /api/p/wallet_txns/search?ignore_condition=with&start_date&end_date&limit=500&offset=…`（walletableの指定は効かないので、全件取得してwalletable_idで絞る）。口座の帳簿残高・同期残高: `GET /api/p/walletables/summary?from=home` の balance / last_balance。
- 口座の構成(2026-10-12確認): 「PayPay銀行 役員口座」(2785644)は中村さん個人の口座(電通の給与が入る)。会社の経費をここから払った分は、本来は役員借入金。2026-06-01付けで補正済み。無視状態の明細は、取引を別に作っても無視のまま残る(登録残高は取引ベースなので影響はない)。
- 同じ誤りが2年続いた: 法人税申告が未払法人税等の支払を自動で計上しているのに、納付時に手入力でも登録してしまい、二重になる(2025年7月・2026年6〜7月)。今後、税金の納付は手入力しない。
