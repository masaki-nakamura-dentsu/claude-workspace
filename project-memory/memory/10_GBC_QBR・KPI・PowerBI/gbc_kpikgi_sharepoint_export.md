---
name: gbc_kpikgi_sharepoint_export
description: GBC KGI/KPIレポート(Power BI)を毎日PDF化しArekoko SharePointへ自動保存する仕組み(稼働中)の設定値と、Fabric API経由の定義取得/DAX検証技法
metadata:
  node_type: memory
  type: project
  originSessionId: b48b93fb-729f-416d-8759-5f95bd809e32
  modified: 2026-10-07T04:56:07.988Z
---

2026-10-07構築・稼働開始(会社Mac d14461)、ユーザーが構成を承認済み。
- 対象: ワークスペース「GBC数字管理レポート」/レポート「KGI/KPI レポート」 https://app.powerbi.com/groups/4656808f-2e02-44ce-9333-83518ae6624a/reports/fdf185d9-4877-4452-be0c-4fee36ece32c (isOnDedicatedCapacity=False=Pro)。セマンティックモデルID bae9c380-3cb2-4860-b2a8-96d1f1486aec
- 保存先: https://esq365.sharepoint.com/sites/GBCarekoko の `/sites/GBCarekoko/DocLib1/KPI／KGIレポート_定期保存`(「／」は全角U+FF0F)。ローカル同期なし。
- ファイル名: `KGIKPIレポート_yyyyMMdd.pdf`(同日2本目以降は_01…、上書きしない)。約2.5MB/15ページ。
- 方式: `~/PowerBIExport/export_kgikpi_to_sharepoint.py` が [[shared_bot_browser]](port 9226)でUI「エクスポート→PDF→エクスポート」→ SharePoint REST(AddUsingPath、Cookie認証)でアップロード。成功/失敗ともTeams Webhook通知。ログ `~/PowerBIExport/export_log.txt`、状態 `state.json`。`--force`で即時実行。
- スケジュール(2026-10-16変更、ユーザー依頼「毎日保存」): launchd `com.nakamura.kgikpiexport` 毎日9:40/11:40/13:40/15:40/17:40/19:40起動、**当日すでに成功していればスキップ**→毎日1本。失敗・スリープ時は同日の次枠で再試行。旧仕様(9:40/15:40・40時間間隔=1日おき)のバックアップ `.bak_202610161`・`plist.bak_20261016`。Mac電源オフの日(週末等)は保存されない。
**Why:** Proのため、Power Automateの「Export To File」アクションとサブスクのPDF添付(UIで「なし」しか選べない、2026-10-07ユーザー確認)は使えない。
**How to apply:** 頻度の変更はスクリプトの当日判定かplist(MIN_INTERVAL_HOURSは廃止)。失敗通知が来たらまずBotブラウザのEntraセッション切れを疑う。

## 副産物: ユーザーにPBIXを頼まずに最新定義を取る技法(2026-10-07確認)
- PBIXダウンロードAPIは大規模モデル形式のため `OperationIsNotSupportedForPremiumFilesModel` で不可。
- 代わりにBotブラウザで app.powerbi.com を開き `window.powerBIAccessToken` を取得 → Fabric `POST /v1/workspaces/{ws}/reports/{id}/getDefinition`(PBIR JSON)と `/semanticModels/{id}/getDefinition?format=TMDL`(全DAX/リレーション)がPro環境でも成功。スクリプト `~/PowerBIExport/pbix/def.py`。
- DAX検証は `POST /v1.0/myorg/datasets/{id}/executeQueries`(`~/PowerBIExport/pbix/q.py <file.dax>`)。DEFINE TABLE/MEASUREで仮の表・メジャーを本番データで試せる。注意: 1回のクエリで返るのはEVALUATE1つ分だけ。VAR名に日本語は使えない。

## アレココ「設定運用関連」ページの公開範囲(2026-10-08 REST/Power BI APIで確認)
- ページ(SitePages Id63)に既にPower BI Webパーツ(KGI/KPIレポート、workspace埋込URL)+見出し「GBC KPI/KGIダッシュボード」+アプリリンク(Dentsu Global Report appId 48fc0d7f)がある。**対象ユーザー(audiences)は空**、サイトのページライブラリに対象ユーザー設定フィールドなし=**未有効化**。ページ枠・見出しは全員に見える。
- 実データの保護はPower BI側の権限のみ: ワークスペース(中村Admin/aicon Admin/山田桂太Contributor)、モデルRead=山本高之・高橋・木村・石坂+Entraグループ2つ(35419f65…/754b1613…、名前未解決=アプリ対象者の可能性)。権限なしの人にはWebパーツ内でアクセス不可表示。
- サイトにSPグループ「GBCマネージャー」(Id834、16名、所有者aicon)あり=管理職限定の権限付与に流用できる候補。
- ⚠ PDF保存先 DocLib1(戦略企画部ライブラリ)とフォルダ `KPI／KGIレポート_定期保存` は**権限継承=サイト全員(GBC M365グループ)が閲覧可**。管理職限定にするならフォルダの継承を切る必要あり(中村はサイト所有者でないためRoleAssignments参照不可=操作は所有者権限が必要)。
- 2026-10-08 続き: ユーザーが方式B(対象ユーザー)を選択。管理職の定義=Entraグループ「GBC(ラインマネジメント職)」sec_..._120 (oid 35419f65-2045-4382-9881-12043cb11868、PBIモデルRead済み)＋「GBC(マネジメント職)」sec_..._20 (oid 1629b91f-2d42-4d75-bfd6-0667e7e5911e、**PBI権限なし**)＋個人 石坂直樹・木村剛(個人は対象ユーザーに指定不可=グループのみ)。
- aicon用の別Chromeプロファイル `~/.chrome-profiles/aicon-bot` ポート9228 を作成(aiconはアレココのサイト管理者)。サイトのページライブラリ(b44edd1d…)の対象ユーザー機能を**有効化済み**(ListEnableTargeting.aspx)。
- テストページ作成→ページ編集→PDFフォルダ権限変更は auto mode の分類器に「共有リソース変更」としてブロックされ、未実施。
- **2026-10-08 最終**: ユーザー判断でSharePointへのPBI埋込はやめ、アプリへのリンクのみ残す(ページ編集はユーザー本人が担当)。サイトのページの対象ユーザー機能は有効化したまま。
- **PDFフォルダ `KPI／KGIレポート_定期保存` の権限を変更済み**(aiconでREST、ユーザーの明示許可あり): 継承を中止(copy=false, clearSubscopes=true)→ GBC所有者=フルコントロール、aicon=フルコントロール(自動付与)、中村=投稿(自動アップロード用)、閲覧=GBC(ラインマネジメント職)・GBC(マネジメント職)・石坂直樹・木村剛・山本高之。中のファイルはフォルダの権限を継承。中村アカウントで追加権限ありを確認済み。閲覧者を増減するときはこのフォルダのアクセス許可の管理で行う。

## 2026-10-13 UI変更対応(自動修復)
- Power BIの新リボン(「新しいリボンを試す(プレビュー)」オン)では「エクスポート」ボタンが無く、リボンに「PDF」ボタンが直接ある(押すと従来と同じ「エクスポート」ダイアログ)。スクリプトは `エクスポート` or `PDF`(exact) のどちらかを待ち、見える方を押すよう修正済み。再度タイムアウトしたらまずリボンUI変更を疑う。

- 2026-10-15 追記(自動修復): 朝の起動がスリープ復帰直後でネット未接続→ERR_INTERNET_DISCONNECTEDで失敗する事象が10/13・10/15に発生。スクリプトに wait_for_network()(curlでapp.powerbi.com疎通確認、15秒間隔・最大300秒)を追加。バックアップ export_kgikpi_to_sharepoint.py.bak_202610150955。

## 2026-10-27 信頼性強化(ユーザー依頼「バックアップがエラーになりがち」)
- 失敗ログ12件の内訳: PDF 0 bytes×5、ネット未接続×4(うちgoto 2)、アップロード403×1、DLタイムアウト(15分)×1、要素待ち×1。
- **0 bytesの根本原因**: PBIのPDFダウンロードは `blob:` URL で、Playwright(CDP接続)が受け取る前にURLが破棄され空になる。10/22〜27に多発し、リトライだけでは直らなかった。
- 対策(バックアップ `.bak_202610270`): ①`URL.createObjectURL`をフックしてBlobをページ内から直接base64で読み出す(従来のexpect_downloadは予備) ②PDFヘッダ(%PDF-)検証 ③DLタイムアウト15→4分 ④書き出し再試行3→4回 ⑤書き出し成功PDFを `~/PowerBIExport/archive/`(直近14本)に控え、アップロードは4回リトライ(403対策)、失敗分は `state.json` の `pending` に積み次回成功時に再送。
- 10/27 08:47 実機で成功確認(2.5MB)。再び失敗が出たらまず blob フックの効き(PBI側のDL実装変更)を疑う。
