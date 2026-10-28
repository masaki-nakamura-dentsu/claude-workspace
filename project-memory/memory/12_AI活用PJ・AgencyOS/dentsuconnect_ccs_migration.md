---
name: dentsuconnect-ccs-migration
description: 【運用ルール】CCS情報の更新はAudience Builder(dentsu.Connect)を使う。旧CCS Explorerは更新停止、記録は残す。構成と旧Explorerとの突合結果
metadata:
  type: project
---
- 2026-10-23: 「CCS Explorerは今後更新が止まり、dentsu.Connectに移行。今後はdentsu.Connectが主なデータソース」と本人から。
- ポータル: https://www.dentsuconnect.com/dashboard (Okta=login.mediaecosystem.io、会社Mac 9226のbotブラウザでログイン済み。パスワードは本人が入力)。CCS本体のメニューは無く、Audience Builder(別データ・Merkury系)、Business Planner、Media Planner(Global)等のアプリ群。
- CCS Planner = Media Planner (Global): https://ccs-planner.dentsuconnect.com/home?clientCode=A_DJPN&tenantId=pbpnlqrzm 。API=ccs-planner-svc.dentsuconnect.com(/survey, /client, /brief, /plan/*, /channel, /export)。メディア配分(リーチ最適化)ツールで、設問別クロス集計APIは見当たらない。調査はSPSS(.sav)+チャネルテンプレート由来。
- /survey は98件(公開93、テスト5、57か国、2018-2026)。旧Explorer559調査・67市場のうち、名前一致86件。Plannerのみ12件(Australia 2023, GB 2026, Turkey 2026, Czechia 2024等)。Japan 2024/2025/2026は両方にある(Japan 2026はPlannerではTest扱い)。
- 未確認: 同一調査の中身(n・設問・回答値)の一致、Explorer相当の設問別集計がdentsu.Connect側のどこでできるか。
- 旧Explorer取得の手順は [[dentsu_ccs_explorer_api]]。更新が止まる前に最新状態を保存しておくのが安全。

## 2026-10-23 追記: Audience Builderが主データ源(CCS Plannerは使えない)
- 本人から「CCS Plannerは使えず、Audience Builderでデータを見る」。入口 https://audience-explorer.dentsuconnect.com/crosstab (実体はiframe aue-crosstab.dentsuconnect.com。ボタンはframe内なので page.frames() から操作)。
- GraphQL: gql.dentsuconnect.com/graphql。`GetSurveyList`(ccsSurveys: surveys(surveyFilterInput:{dataSource:CCS}))で調査一覧。Create new crosstab→市場→データセット選択の画面で呼ばれる。
- 結果: 140調査・21市場(Japan 11件)。**調査IDと名前は旧Explorerと一致(139/140)**=同一バックエンド。新規は CCS Taiwan 2026(id1173)のみ。旧Explorerは559調査・67市場なので、A_DJPNクライアント権限で見える範囲が約1/4(特注調査・多くの市場は出ない)。
- getClientMapping.allowedDatasets は A_DJPN で空[]。Crosstab保存件数0。
- 未確認: 実際の集計値(n・Top2)が旧Explorerと一致するか、crosstab結果のAPI。

## 結論・運用ルール(2026-10-23、本人確認済み)
- Audience Builderの調査は旧Explorerと同一データ(調査ID・名前139/140一致)と本人が確認。
- **旧CCS Explorerの情報(メモリ・取得済みJSON・カタログ)はそのまま置いておく。**
- **CCSの情報を更新するときはAudience Builderを使う**(Explorerのapi/charts/dataを新規に叩かない)。CCS Plannerは使えない。
- 注意: A_DJPN権限だと140調査・21市場のみ。旧559調査・67市場のうち特注調査や他市場が必要なときは、Explorer保存分を使うか権限拡大を依頼。
- 今後の更新手順の起点: audience-explorer.dentsuconnect.com/crosstab → iframe(aue-crosstab)のCreate new crosstab → GetSurveyList(gql.dentsuconnect.com)。集計APIの詳細は未調査。

## 2026-10-23 集計取得ツール構築(Audience Builder)
- 場所: GBC-Knowledge/ccs_source/audience_builder/ (ab_client.js, README_ab.md, out/)。Dropbox内パス: Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/GBC-Knowledge/ccs_source/audience_builder
- 画面のドラッグ操作は不要。認証ヘッダーを拾ってGraphQL直叩き: GetSurveyList / Codebook(isMetrics:true) / submitCrossTabMetricsJob→getCrossTabMetricsJobResult。使い方は README_ab.md。
- 検証: Japan 2025 n=10,140・母集団72,922,764が旧Explorerと一致、Male×Maleがコードブック値と一致。
- 落とし穴: introspection無効 / UIのreact-dndは通常のdragToでは動かず合成DragEventが必要(今後不要) / crosstab保存は未実施(ブラウザ内の探索用で保存データなし)。

## 2026-10-23 訂正
- CCS Planner=Media Planner(Global)は**実際には使えた**。ターゲットはAudience BuilderのPanel IDs CSVで取り込む方式。詳細は [[media_planner_ccs_planner]]。

## 運用(2026-10-23 本人OK)
- CCSの定期更新(調査一覧・コードブック)は、Audience Builder経由の ab_client.js で行う。旧Explorerは更新しない(記録は保持)。
- 更新時は botブラウザのOktaログイン確認 → surveys / codebook を再取得し、前回(out/surveys_20261023.json)と差分(新規調査・Taiwan 2026のような追加)を見る。
