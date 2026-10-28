---
name: ccs_peopleresearch_bureau_rollout
description: CCS/AI People Researchを Claude Code を使えない局員に使わせる仕組みの検討(2026-10-17 相談段階)
metadata:
  type: project
---
2026-10-17 ユーザー相談: 局員は Claude Code 不可。ユーザー案は「基本ファイル+知りたいことをChatGPTに渡し、ChatGPTが書いたPythonを局員が実行」。

Claudeの回答(方針案、未決定):
- ユーザー案の弱点: CCSはAzure Easy Auth(curlは401)でPython単体では認証が通らない、社内証明書問題、局員PCのPython導入は申請要の可能性、毎回違うコードが出てデバッグできない。
- 推奨: 「取得」と「分析」を分ける。取得=固定ツール(第一候補: CCS画面上で動くブックマークレット。ページ内fetchで既に動作実績あり [[dentsu-ccs-explorer-api]])でCSV出力。分析=CSVをChatGPT(Agency OS Skill等)に渡しChatGPT側のPython実行で分析→局員PCにPython不要。
- ChatGPTには設問カタログ(questionId一覧)をKnowledgeで持たせ、取得ツールに渡す「取得指示(JSON/表)」を作らせる案も提示。
- People Research はGUIツールで自動化は脆いので、設問設計テンプレ(マニュアルの精度ルール、[[reference-ai-people-research]])+結果分析プロンプトを配る方式を推奨。
- 要確認: CCS/People Researchの社内データ利用ルール(ChatGPTへのアップロード可否)。
- 未検証: ブックマークレットが社内Edgeで動くか。試作は会社Mac(9226のCCSセッション)で。
- 2026-10-17 中村さん確認: CCS/People ResearchのデータはChatGPTにアップロード可(Enterprise契約で機密情報も可)。
- 2026-10-17 CCS設問カタログをAgency OSに入れる作業を会社Mac向けtask-016として依頼キューに登録(市場別最新調査の一覧+設問マスター、本番pushは中村さんOK後)。
- 2026-10-17: 中村さんの希望で、海外市場が関わる相談では毎回CCSを確認して「CCSで確認できること」を出すよう必須化(SKILL_*_20261017_01、Rule D+Mandatory search)。消費者と関係ない相談(法務・契約・人事)では出さない。
