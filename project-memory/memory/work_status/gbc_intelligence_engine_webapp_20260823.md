# GBC Intelligence Engine / LaunchPad — Web化

## 2026-08-23T00:00:00+09:00 (個人Mac ICPTokyo2022)
Status: in progress
What: 既存のknowledge_index.db(doc_cards/case_records/staff_profiles/faq_records/contract_tools/pm_checklists/tool_phase_mapping)を土台に、FastAPIバックエンド(webapp/app.py)+単一HTML(webapp/static/index.html)のローカルWebアプリを新規作成した。統合検索・PM CHECKLIST・PROCESS & TOOLKITの3タブ。case_briefsは既存の設計判断通り全APIから除外。venvは~/gbc_knowledge_venvに作成(Dropbox外)。localhost:8800で動作確認済み(検索API/toolkit API/checklist types APIとも正常応答、ブラウザでも表示確認)。ホスティング先(社内サーバー/Azure/会社Mac簡易サーバー等)はユーザーがIT部門にまだ未確認のため未定。ユーザーの意向で今日はここまで、続きは会社Mac(d14461)で作業予定。
Next: 会社Mac側で webapp/ フォルダ(Dropbox経由で同一パス`中村正樹/Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/GBC-Knowledge/webapp/`に同期済みのはず)を使い、(1) IT部門へのホスティング先確認、(2) 決まればそこへのデプロイ、を進める。d14461側にも別途venvを作る必要あり(Dropbox越しのvenv共有はNG、[[feedback_venv_outside_dropbox_sync]])。
