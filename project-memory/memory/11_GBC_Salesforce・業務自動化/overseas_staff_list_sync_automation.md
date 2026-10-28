---
name: overseas-staff-list-sync-automation
description: SharePoint「海外駐在員リスト」を会社Mac(d14461)にOneDrive同期経由で自動取得・アーカイブするlaunchdパイプライン(2026-09-03構築、動作確認済み)
metadata:
  type: project
  originSessionId: e391f24b-6df4-4944-89a9-fa657b9f3d5c
  modified: 2026-09-04T05:45:51.347Z
---

2026-09-03、globalonedentsuサイト(https://esq365.sharepoint.com/sites/globalonedentsu/)の
SiteAssets/SitePages/海外駐在員リストを常にMac上に最新版として自動取得する仕組みを構築。

## 採用方式(重要な発見)
新規のMicrosoft Graph API / Azure ADアプリ登録によるOAuth実装は**行わなかった**。調査の結果、
対象フォルダは既に会社Mac(d14461)の純正OneDriveクライアントで同期済みだったため
(`~/Library/CloudStorage/OneDrive-電通/Global Q_サイトのリソース ファイル/SitePages/海外駐在員リスト/`)、
これをそのままローカルの一次情報源として使う方式にした。理由:
- 新規Azure ADアプリ登録は[[dentsu_claude_code_it_application_process]]のような特殊IT申請/管理者同意が必要になる可能性が高く、[[company_mac_no_admin_no_homebrew]]の管理者権限なし制約とも相性が悪い
- OneDriveアプリの既存ログイン(dentsu SSO)をそのまま使うため、パスワード/トークンをコード側で一切扱わない
- 過去データ(Shared Documents相当)も既に別フォルダとして同期済みだった: `Global Q - 駐在員リスト`(2020-2021)、`Global Q - ドキュメント`(2019, 2022年分の重複コピー含む)

**今後同種の「SharePoint/Teams上のファイルを自動取得したい」という依頼が来たら、まず
`~/Library/CloudStorage/OneDrive-*/` 配下に対象フォルダが既に同期されていないか
`find`で先に確認すること。同期済みなら新規OAuth実装は不要で、この方式が最速。**

## 構成(2026-09-03、ユーザー指示により保存先を変更)
- スクリプト: `~/OverseasStaffList/sync_overseas_staff_list.py`(Python3標準ライブラリ+requests、外部依存最小)
- **保存先はユーザー指定により `~/Library/CloudStorage/OneDrive-電通/Global Q - 駐在員リスト`(共有チームのOneDrive同期フォルダ、2020-2021の過去データが元々置かれていた場所)に変更済み。** 当初はローカル専用の`~/OverseasStaffList/archive`+`/latest`を作ったが、ユーザーから直接この共有フォルダへの保存を指示され、設計変更した。
  - **重要な注意点**: この保存先は他メンバーも見える共有SharePointライブラリ(OneDriveで双方向同期)。書き込んだファイルはSharePoint側にもアップロードされ、サイトへのアクセス権を持つ他の人にも見える。「latest/を毎回削除して作り直す」という当初案は、共有フォルダ内で他人から見て頻繁にファイルが消えたり現れたりするため不適切と判断し廃止。代わりに全月次ファイルを蓄積していく方式(既存の2020-2021分と同じ並び)にした。
  - 2026-09-03時点で2023年2月〜2026年9月分(35件)を新規コピー済み。「Global Q - ドキュメント」フォルダ(2019年・2022年分、重複サフィックス付きファイル混在)からの追加取込は、共有フォルダを不要に散らかさないためユーザー確認なしには行わない判断とし、今回は未実施(必要なら次回指示を待つ)。
- ログ(`sync_log.txt`)は共有フォルダには置かず、ローカルの`~/OverseasStaffList/`に残す。
- 重複判定はSHA-256ハッシュ(ファイル名ではなく内容で比較)
- ファイル名からの年月抽出は3パターンに対応: `YYYY年M月`、`YYYYMMDD`、`YYYYMM`(いずれも正規表現で先頭一致、実際のファイル名の揺れ複数パターンで検証済み)
- ログ: `~/OverseasStaffList/sync_log.txt`(全実行を記録、フォルダ消失等の異常も原因が分かる形で記録される設計、意図的に壊して動作確認済み)
- Teams通知: 新規ファイル検知時と失敗時に送信([[teams_webhook_powerautomate]]のURLを launchd plist の`EnvironmentVariables`経由で`TEAMS_WEBHOOK_URL`として渡す設計。**Python `urllib.request`はこのMacの証明書ストアの問題でSSL検証に失敗する(`unable to get local issuer certificate`) — `requests`ライブラリを使えば同じエンドポイントに問題なく届く(202確認済み)。今後このMacでPythonからHTTPS POSTする処理を書く際は、urllib.requestではなくrequestsを使うこと。**

## launchd(2026-09-03、頻度をユーザー指示により変更)
`~/Library/LaunchAgents/com.nakamura.overseasstafflistsync.plist`。当初`StartInterval=3600`(1時間おき)だったが、
元データが月1回しか更新されないため「頻度が高すぎる」とユーザーから指摘があり、**`StartCalendarInterval`で
毎週月曜7:30に変更**(`RunAtLoad`は外した — ログインの度に走ると週次の趣旨に反するため)。
呼び出し先も`sync_overseas_staff_list.py`単体ではなく、下記の`weekly_update.py`(sync→駐在履歴再生成を順に実行)に変更。

## weekly_update.py([[overseas_staff_assignment_history]]と統合)
ユーザーから「[[overseas_staff_assignment_history]]のbuild_assignment_history.pyも同じタイミングで自動実行できるか」
と依頼され、`~/OverseasStaffList/weekly_update.py`を新設。sync→駐在履歴再生成の順に実行(履歴再生成は最新のアーカイブ
内容に依存するため順序を保証する必要があり、2つの独立したlaunchdジョブを同時刻に並べる案ではなく、1つのジョブ内で
順次呼び出す設計にした)。各ステップは独立してtry/exceptしており、片方が失敗してももう片方は試行する。
ログ・Teams通知処理は`~/OverseasStaffList/common.py`に共通化し、`sync_overseas_staff_list.py`と
`build_assignment_history.py`の両方がそこから`log()`/`send_teams()`/`content_hash_of()`を import する構成に整理した。

## 重要なバグ修正(2026-09-03): 単純なファイル全体のSHA-256は重複判定に使えない
週次化の動作確認中に、変更されていないはずのファイルが「内容が変わった」と誤検知され、共有フォルダに
`_20260903`サフィックス付きの紛らわしい重複ファイルが12件出来てしまうバグを発見(実機で遭遇、修正後に削除済み)。
**原因**: SharePoint/OneDriveは初回同期後に`docProps/custom.xml`や`customXml/item*.xml`(機密ラベル等のメタデータ)を
非同期で書き換えることがあり、これによりファイル全体のバイト列は変わるが、実際のセルデータ(`xl/worksheets/*`,
`xl/sharedStrings.xml`)は一切変わっていない、ということが起きる。**対策**: `common.content_hash_of()`で
zip内の`xl/worksheets/*`と`xl/sharedStrings.xml`のみを対象にハッシュを取るよう変更(メタデータ部分は無視)。
これにより誤検知が解消し、副次効果として`build_assignment_history.py`側の重複除去(SOURCE_DIRS内の同一内容ファイル、
SharePointが自動生成する`_58685`のような衝突コピー名)もより正確になった(71件→68件のユニークファイル)。
**今後同種の「Excel/Office文書ファイルの内容変更検知」を実装する際は、ファイル全体のハッシュではなく、
xlsx内部の実データ部分(ワークシート+共有文字列)だけを対象にすること。これはOneDrive/SharePoint同期ファイル
全般に当てはまる注意点。**

## 検証済み結果(2026-09-03)
保存先変更後、共有フォルダへ35件を新規コピー(19件→54件)。最新月判定は2026年9月_海外駐在員リスト-.xlsxを正しく検出。
xlsxファイルの整合性(zip構造)も確認済み。2回目実行は新規0件で正しくスキップ(SHA-256一致)を確認。
launchd経由の実行(RunAtLoad)も正常動作(exit code 0)を確認済み(保存先変更前の設定で検証、変更後もスクリプト内部のARCHIVE_DIR定数を変えただけなのでlaunchd設定自体の再ロードは不要)。

## 2026-09-04追記: 3ステップ目を追加(海外駐在員_異動履歴まとめ.xlsx)
ユーザーから[[overseas_staff_timeline_workbook]]の自動更新も依頼され、`weekly_update.py`に
`build_timeline_workbook.main()`を追加(sync→駐在履歴再生成→このタイムラインワークブック再生成、の3段構成)。
詳細は[[overseas_staff_timeline_workbook]]参照。

## 2026-09-04追記(同日続き): 4ステップ目を追加(Agent OS / Agency OS連携)
このデータをAgent OS(ローカル`/Users/d14461/AIAgency`)とAgency OS(ChatGPT Skill)双方から
参照できるようにする依頼があり、対応方針が二分岐した:
- Agent OS(ローカル)側は新規処理不要。[[overseas_staff_assignment_history]]参照。
- Agency OS(ChatGPT Skill)側は[[gbc_intelligence_engine_project]]が持つ
  `generate_overseas_staff_pack.py`の再実行が必要なため、`weekly_update.py`に4番目のステップ
  `update_agency_os_pack.main()`を追加(sync→駐在履歴再生成→タイムラインワークブック再生成→
  **Agency OS Pack(overseas_staff_index.md)再生成**、の4段構成)。詳細は[[gbc_intelligence_engine_project]]
  の2026-09-04セクション参照。ChatGPT Skillへの実アップロードは自動化不可のため、内容変化時のみ
  Teams通知する設計。

## 未検証・今後の注意点
- launchdの1時間定期実行が実際に次回時刻(1時間後)に発火するかは未確認(構築直後のため)。次回セッションで`sync_log.txt`のタイムスタンプ間隔を確認するとよい。
- 会社Macがオフ/スリープの時間帯にSharePointへ新月ファイルが追加された場合、次にMacを開いた時のRunAtLoadで取得される(即時性はない)。
- 個人Mac(ICPTokyo2022)側にはこの自動化は展開していない(会社Mac限定のOneDrive同期フォルダに依存するため、個人Macで同じ仕組みを作るには個人Mac側でも同じSharePointサイトがOneDrive同期されている必要がある — 未確認)。

## 2026-10-19 週次ジョブが9/3以降一度も動いていなかった件(修正済み)
- 原因: 会社Macは毎晩21:45に自動シャットダウン(jp.co.dentsu.shutdown)、朝8時台に起動。月曜7:30は電源オフで毎回実行されなかった(電源オフ中の予定はlaunchdが後から実行しない)。→ 月曜9:45に変更(元plistは ~/OverseasStaffList/com.nakamura.overseasstafflistsync_bak_20261019.plist)。
- 2つ目の原因: 10月リストがOneDriveの未ダウンロード(dataless)で「File is not a zip file」→スキップ。sync_overseas_staff_list.py の archive_file で全体を読み切ってダウンロードさせ、最大3回読み直すよう修正。
- 10/19に手動実行(kickstart)で10月分を取込、駐在履歴343セグメント・最新月2026-10、overseas_staff_assignment_history_20261019.xlsx と 異動履歴まとめ を更新。
- 中村さん判断(10/19): 駐在員履歴は毎週の更新で足りるので、月次更新には組み込まない。
