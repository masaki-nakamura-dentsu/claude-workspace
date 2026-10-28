---
name: dentsu-ccs-explorer-api
description: dentsu CCS Explorer(m1-panel-explorer.azurewebsites.net)の海外生活者調査データを、画面キャプチャなしでAPI経由で集計する方法
metadata:
  type: reference
---

> **【2026-10-23 方針】旧CCS Explorerは更新停止(dentsu.Connectへ移行)。この記録は旧データの参照用としてそのまま残す。CCSの情報を新しく更新・取得するときは Audience Builder(dentsu.Connect)を使う。→ [[dentsuconnect_ccs_migration]]**
URL: https://m1-panel-explorer.azurewebsites.net/selectSurvey/selectSurvey (Azure Easy Auth、curlは401)。masaki.nakamura@dentsu.co.jp でログインすればどのマシンでも入れる: 会社Mac=9226、個人Mac=9231(dentsu-work-bot、2026-10-17確認)。Playwright APIRequestは社内証明書で失敗するため、**ページ内 fetch(page.evaluate)** で叩く。

主なAPI(GET):
- `api/surveys/mvp?includings=market&includings=dashboards` 全調査一覧(556件、約80市場。名称 "CCS <国> <年>")
- `api/surveys/{id}/info` サンプル数・推計母集団
- `api/questions?surveyId={id}` 設問一覧
- `api/surveys/{id}/attributes` 全選択肢(questionId, dimensionArrayId, value1/value2) ※6MB
- `api/charts?surveyId={id}` 既存チャート定義(chartDimensions に questionId/dimensionId)
- `api/targets/inSurvey/{id}` 既存ターゲット(先頭要素の .base = 全体 "Base Population")
集計(POST `api/charts/data`): body `{chart: 既存チャート, target: T, baseTarget: base, multiTargets: null}`。自作ターゲットは `{surveyId, name, id:0, baseId, base, description, isPublic:false, isImported:false, childTargets:[], childSurveyIds:[], targetElements:[group...]}`、group=`{itemType:2, relation:1(AND), description, children:[{itemType:1, questionId, relation:2(OR), description, children:[], targetDimensions:[], targetElementValues:[{dimensionArrayId, isSelected:true, description}]}]}`。description が無いと500系(Object reference)エラー。結果は percent(Top2等)、totalWeight/推計母集団×sampleSize ≒ n。
- CCS Japan 2025(id 950)には所属部門 E9(questionId 243162: Engineering=20105784, Study/Development=20105785)があり技術職で切れる。
- 既知不具合: Taiwan 2025(954)はチャートの次元が空で値が出ない、China 2024(767)はTechnology/Like youチャート無し、Singapore 2026(1147)はbase無し。
- 初回利用: 2026-10-06 Nidec案件([[nidec_components_naming_pitch]])。スクリプトはscratchpad(消える)。

- 2026-10-17: 全559調査・67市場(標準調査「CCS <市場> <年>」の最新)。設問は調査ごとに約250-300、市場間で言い回しが違うものが多く、20市場以上で共通は276問。選択肢(attributes)は value1=回答、value2以降=区分・項目(例 H1趣味: value3=趣味名, value2=頻度)。
- 取得・カタログ化: GBC-Knowledge/ccs_source/fetch_ccs_raw.js(生JSON) → generate_ccs_catalog.py → output/ccs_catalog_YYYYMMDD/(ccs_survey_index / ccs_question_catalog / ccs_questions_by_market)。[[ccs_peopleresearch_bureau_rollout]]
