# GBC週報×知見まとめ→木村DMD送付プロジェクト

Status: in_progress

## 2026-08-11
- 中村さんから依頼: 毎週水曜夜にSalesforce週報を読み、GBC知見と照らして木村剛DMD(tkimura@dentsu.co.jp)にまとめを送るフローを作りたい。GBC知見自体も索引化して他プロジェクトで再利用したい。「進め方を相談」という依頼だったのでAskUserQuestionで4点確認(宛先=木村剛さんで確定、実行スタイル=半自動、出力=Excel、インデックスはClaude主導で草案作成)
- GBC知見サイト(SharePoint GBCarekoko、実体は「GBCアレココ」ハンドブック)へのアクセスを共有Botブラウザ(port 9227)で確認、追加ログイン不要
- 知見が既に構造化SharePointリスト(Knowledges 253件、教えてGBC 54件)+独自分類体系(7カテゴリ×80タグ)で運用されていることを発見。ゼロから分類を作らずそのまま抽出
- `~/Library/CloudStorage/OneDrive-電通/GBC戦略企画部_知見インデックス化・週次まとめ/`にインデックスJSON3ファイル+READMEを保存
- Salesforceレポート(00O7F00000AmEiQUAV)へのアクセスも確認、列構成を判明（レポートビルダーを保存せず閲覧のみで確認）。現時点(水曜朝)で該当0件、夜の実行が前提と判明

## 2026-08-12 続き
- ~/GBCWeeklyReport/に週報パイプライン一式を構築: download_step1/2 (Salesforceエクスポート自動化,Node/Playwright)、build_summary.py(GBC知見突合+Excel生成+週次アーカイブ)
- ダミーデータでロジック検証: 実在の「教えてGBC」Q&A(台湾PizzaHutのPerformanceベース契約)を正しく最上位マッチさせることを確認
- 詳細は per-project memory `gbc_weekly_report_kimura_dmd_project.md` に記録済み

## 2026-08-12 さらに続き: 実データでのテスト実行完了(下書きまで、送信はしていない)
- ユーザーが「過去のレポートでテストしたい」と依頼。SalesforceのUIで一時的に過去20日間にフィルタを広げて33件のデータで検証
- ユーザーが「Salesforceのエクスポートは例外で、あなたが私のメールをチェックしてその数字を入れてよい」と標準ルールとして許可 → `feedback_salesforce_verification_code_standing_permission.md`に保存
- 実データで2つの罠を発見: ①エクスポートは一時フィルタでなく保存済みフィルタで実行されることがある(条件パネルを閉じてから実行が必要) ②「詳細のみ」形式は日本語が`?`に文字化けする実データ破損バグ(「フォーマット済みレポート」形式なら正常)
- `build_summary.py`をフォーマット済みレポートの実際のExcel構造(グループ化・ffill必要)に対応させ、マッチング精度のバグ2件(「ー」誤マッチ、空欄回答のQ&A混入)を修正。33件中16件に妥当な関連知見が付くことを確認
- Outlook Web UIが`outlook.cloud.microsoft`に移行しており、outlook_cliの添付機能が壊れていたのを発見・修正(`~/.claude-sync/Scripts/outlook_cli/lib.js`)。修正後、木村剛さん宛の下書き(宛先/件名/本文/添付ファイル)を`--dry-run`で正常作成・スクリーンショットで確認。**実送信はしていない**
- 詳細は per-project memory `gbc_weekly_report_kimura_dmd_project.md` に記録済み

## 2026-08-12 さらに続き: 会社Mac(d14461)へ作業移行のため個人Macでの作業を切り上げ
ユーザーが「一旦会社Macにこの作業を移行するので、このPCでの作業を切り上げます」と明言。
- `~/GBCWeeklyReport/`をDropbox `.claude-sync/Scripts/GBCWeeklyReport/`に実体移動、個人Macにはシンボリックリンクを残した(outlook_cliと同じパターン)
- デバッグ用の一時ファイル(スクリーンショット・調査用スクリプト)は削除、本番3スクリプト+README+archive+downloads+outputのみ残存
- download系3スクリプトの共有Botブラウザport指定を`GBC_BOT_PORT`環境変数で上書き可能にした(d14461は9226、個人Macは9227がデフォルト)
- README.mdにd14461側で必要な前提条件(port/profile差異、Playwright環境、python3のopenpyxl未確認)を明記
- 詳細は per-project memory `gbc_weekly_report_kimura_dmd_project.md` に記録済み

Status: 会社Mac側での続行待ち

## 残作業(次は会社Macで)
- d14461での動作確認(GBC_BOT_PORT=9226で接続、Playwright/openpyxl環境確認から)
- 本番の週次実行はまだ実施していない(次は毎週水曜夜、保存済みフィルタのまま本番実行)
- Outlookカレンダーへのリマインダー設定はユーザー本人が必要(Claude書き込み権限なし)、トリガーフレーズも未確定
- 今回作成したテスト下書き(件名「【テスト】GBC週報×GBC知見 週次まとめ」)はOutlook下書きフォルダに残存、要検討(削除 or 本番初回で上書き)

## 2026-08-12 さらに続き: d14461(会社Mac)側の環境検証完了
中村さんが「自動化Salesforceレポート分析と知見管理フローの続きをします」と会社Mac(d14461)から再開。
- `~/GBCWeeklyReport`シンボリックリンクを作成、README記載の前提条件(Playwright/openpyxl/共有Botブラウザport 9226)をすべて確認 → 問題なし
- フルパイプライン(エクスポート→認証コード自動入力→build_summary.py)をd14461上でエンドツーエンドに実行して動作確認。水曜朝時点は0件(想定通り、活動は日中に随時登録)。0件のテスト出力は削除済み
- **d14461側の残作業は解消**。残るは本番の水曜夜実行のみ
- 詳細は per-project memory `gbc_weekly_report_kimura_dmd_project.md` に記録済み

Status: 本番の水曜夜実行待ち

## 2026-08-12 さらに続き: マッチング品質検証・2件のバグ修正・トリガーフレーズ確定
中村さんの指示「知見がちゃんと意味のあるものになっているか先に確認」に対応。
- バグ1: クライアント名部分一致が自社名「電通」への誤マッチを許していた(電通シンガポール等が無関係にヒット) → GENERIC_OWN_NAMES除外で修正
- バグ2: 文字2-gram類似度が英語頻出2文字・日本語定型句(です/ます/対応/実施/電通等)を拾って誤爆 → ASCII bigram除外+ストップワード除外+閾値0.15→0.20で修正
- 効果: 33件中「知見あり」判定16件→5件に減少、残った5件は質的に妥当(サンリオ/花王×2/富士通のクライアント名一致+MSG1件)
- トリガーフレーズ確定:「木村さんへGM会週報のレポートをまとめて」(業況見通し用とは別物)
- テスト下書き(木村さん宛)は中村さんの指示でそのまま残すことに決定
- 詳細は per-project memory `gbc_weekly_report_kimura_dmd_project.md` に記録済み

Status: 中村さんによる output/GBC週報まとめ_20260812.xlsx の内容確認待ち → OKなら本番の水曜夜実行へ
