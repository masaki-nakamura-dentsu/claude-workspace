---
name: agency-os-deploy-tools
description: Agency OSのChatGPT Skill/Difyナレッジを画面キャプチャなしで反映・照合するツール(GBC-Knowledge/tools)。Skillの内部API(hazelnuts)の仕組み
metadata:
  type: reference
---
2026-10-15 作成。場所: 20260814GBC知見集約プロジェクト/GBC-Knowledge/tools/(README.mdに手順)。
- chatgpt_skill.js(CDP 9224): pull / compare / push。ChatGPT Skillは内部API `/backend-api/hazelnuts/<id>`。中身は全ファイル連結のtar(sediment_id)、メタの `files` に各ファイルの start/length(辞書オブジェクトで返る場合と文字列の場合あり)。ダウンロードは `POST .../files/get_download_link {file_id: sediment_id}`。保存は `POST /backend-api/hazelnuts/draft`(id,name,display_name,description,instructions,apply_resolution:false,files=[{file_id:sediment_id,path,range}](変えないファイル、SKILL.md以外),file_contents=[{path,content}](変えるファイル))。認証は /api/auth/session の accessToken と ChatGPT-Account-Id(_accountクッキー)。2.5MB程度ずつ分けて保存し、1回ごとにメタを取り直す。
- 中村さん指示(10/15): Skillのファイルは削除・再アップロードしない(アップロード不可の仕様)。既存ファイルの中身を置き換える。確認はスクショでなく中身をプログラムで照合する。
- dify_kb_replace.js(CDP 9226): 同名文書を元のprocess_ruleのまま original_document_id で上書き→indexing-status待ち→upload_fileサイズ照合。files/upload?source=datasets(バッチ上限5件)。
- Agency OS Skill ID 6a8e694f429c81b8a9544812b9b8f080、内部名 gbc-ai-agency、表示名 Agency OS。10/15時点 version 139、safety_check_status=blocked(10/15以前から。意味は未確認)。
Related: [[agency_os_poc_feedback_20261013]] [[gbc_intelligence_engine_project]]
- 2026-10-17 個人Macから反映: ツールは環境変数 CDP_PORT でポート指定可(chatgpt_skill.js / dify_prompt.js / dify_kb_replace.js / 新規 dify_kb_create.js)。個人Macは ChatGPT=9229(chatgpt-work-bot)、Dify=9231(dentsu-work-bot)。会社Macは従来どおり9224/9226。
- 新規 tools/dify_kb_create.js: 新しいナレッジを作り、既存ナレッジ(--like)の区切り・埋め込み設定を引き継いでフォルダの.mdを入れる。
- Difyに追加(10/17): ナレッジ arekoko_catalog(b8da3a3c-e78d-400d-82ec-647817713b24)・ccs_catalog(1574510c-7a14-4253-904a-d4e16e341ee4)。検索ノード「知識検索 アレココ目録」(1792200000001、top_k 8)・「知識検索 CCS設問」(1792200000002、top_k 4)をテンプレート→ノード→コード実行(変数g,h)に配線。公開名「20261017目録CCS追加」。変更前のワークフローJSON: GBC-Knowledge/output/dify_workflow_backup_20261017.json。
- ChatGPT Skill: version 147(10/17)、目録3+CCS3ファイル追加、指示文 SKILL_20261017_02。反映前のバックアップ GBC-Knowledge/output/skill_backup_20261017/(version 142)。
- 教訓: 目録とCCSを同じDifyナレッジに入れるとtop_kを奪い合いCCSが取れず、LLMが設問文を捏造した。英語のCCSカタログは日本語の質問で検索に掛からない→日本語の国名・カテゴリ名を添えて解消。目録の目次は細切れに取り出されるので各行に資料ID、15行ごとに資料名を入れた。
- 2026-10-19: 指示文 SKILL_20261019 を反映(version 149、照合一致)。Output economy rule 9=HTML版出力(同一Markdown本文をPythonで変換・目次ページ内リンク・要点カード・URL件数照合)。Dify版(SKILL_Dify)には未反映(チャット欄はHTML非描画のため別方式検討)。
- 2026-10-19(2): 初回テストでHTML未生成→Always-on #6に最終手順として追加、SKILL_20261019_01をversion 151で反映・一致(150は不明な別保存)。
- 2026-10-19(3): 2回目テストでHTMLが手書き要約→変換コード(GPT作業/agencyos_md2html.py)をSKILL末尾Appendixに同梱、SKILL_20261019_02をv153で反映。**push 1回でversionが2進む**(149→151→153)。過去の『不明な別保存』はこれが原因で他者の上書きではない。
- 2026-10-19 月次 内容更新チェックを自動化: GBC-Knowledge/tools/monthly_freshness_check.py、launchd com.nakamura.agencyosmonthlycheck(会社Mac d14461、平日9:30起動、jpholidayで土日祝・年末年始を除いた第1営業日以降・当月未実施なら実行。state=output/monthly_check/last_run.txt)。各*_source・knowledge_index.db・OneDrive駐在員xlsxの最終更新を見て、35日超=古い/パックより新しい=再生成候補をoutput/monthly_check/agency_os_check_YYYYMM.mdに出し、teams_notify(WARN/INFO、job名AgencyOS月次)。読むだけで再生成・反映はしない。手動は --force。10月分は試走のみ(本番stateは未記録、11/2が初回)。
- 2026-10-19(4): 3回目もHTML手書き(変換コード不使用)+本文からCHECKLIST/URL欠落→常時HTML撤回、依頼時のみ(SKILL_20261019_03、v155)。教訓: 長大SKILL.md末尾のコードはChatGPTに使われない。出力形式の追加指示は本体品質を落とし得る。
- 2026-10-19(続き) 中村さん依頼: アレココ・CCSも月次で作り直し、Skill・Difyへ自動反映。tools/monthly_update.sh(個人Mac専用: ~/arekoko_files・9231・9229・Windows Ollama)。流れ: CCS取得→カタログ / アレココ一覧・添付DL・ページ抽出→win_power wake→要約・照合(新規分のみ)→shutdown→目録 → 前回反映分(output/monthly_update/deployed.txt、初期値 arekoko_catalog_20261017_04 / ccs_catalog_20261017_01)と比較、件数90%未満・空ファイルなら反映せずERROR → 変更分だけ 差し替え用_YYYYMMDD_auto へ → Skillをpullでバックアップ→push→compare → dify_kb_replace(ワークフロー公開はしない)。launchd com.nakamura.agencyosmonthlyupdate(平日9:00、第1営業日以降・当月未実施)の登録は personal_mac_inbox task-019 で依頼中(10/19時点 pending)。既知の限界: 内容が変わった既存資料は summary.json があると要約し直さない。
- 2026-10-19(5): 依頼時HTMLも手書き(変換コード不使用)→ChatGPT側でのHTML変換は限界と判断。代案=貼り付け変換ツール(決定的変換)を提案中。別件: v155の通常回答でCHECKLIST・URL欠落、思考11秒(Thinking不足の疑い)。
- 2026-10-19(6): 貼り付け変換ページ GBC-Knowledge/tools/AgencyOS_HTML変換.html 作成(オフライン単体HTML、Markdown/リッチテキスト貼付→目次・要点カード・URL照合→保存)。ChatGPT側HTMLは依頼時のみのまま。前回テストはInstantモードだった(CHECKLIST欠落の原因)。
- 2026-10-19(7): HTML方式撤回、SKILL_20261019_04(=20261017_02内容)をpush。ユーザー評価『変換ページは少し改善程度、ひと手間かけて使うか疑問』。
- 2026-10-19(3) 更新量の見込み: アレココ新規登録は月7〜25件(直近12か月平均≒11、1件あたり添付1〜2ファイル)。要約は新規分だけなので自宅Windows 27Bで数分〜20分程度。会社MacにもOneDrive「GBC_アレココ - 添付ファイル」で全426ファイルあり(サイズ一致)だが、Ollamaがない(10/19削除)ため実行は個人Macのまま。会社Macの確認ジョブは、今月の monthly_update.sh が未着手なら [[mac_direct_instruction]] で個人Macへ実行依頼する。
- 2026-10-19 注意: 個人Macでは GBC-Knowledge が『知見機能/20260814GBC知見集約プロジェクト/』直下(01_AI活用 の階層なし)。会社Macと階層が違うので、パスは相対の固定段数で書かず .claude-sync を上へ探す。
- 2026-10-19 11:05頃 個人Macで install_monthly_update.sh 実行済み(launchd com.nakamura.agencyosmonthlyupdate 登録、runs=0)。試走(--detach --force --no-deploy)をユーザーが起動、結果待ち。
- 2026-10-19 11:10頃 試走成功(個人Mac、--no-deploy): CCS 559調査、アレココ新規0、Windows起動50秒→Ollama起動→60秒後シャットダウン予約、目録・CCSとも前回反映分と完全一致(変更ファイルなし)。本番初回は2026-11-02 9:00。
- 2026-10-19 会社Mac確認ジョブの代行依頼を『launchctl kickstart com.nakamura.agencyosmonthlyupdate』に変更(monthly_update.shを直接頼むとclaude -p終了で止まるため)。send.sh経由のkickstartはauto modeを通った(runs=1)。今回は試走が変更なしでlast_run=2026-10を記録済みのため即終了=正常。10月分は完了扱い、次は11/2。
- 2026-10-19(4) 中村さん許可でdentsu.dot 2ファイルをSkill・Difyへ反映(照合一致、Skill v158→、反映前 output/skill_backup_20261019)。※このときfix_pack_links.pyを通し忘れた版を出した(URL前後の空白処理なし)→ 会社Mac月次で修正版に置き換わる。
- 会社Mac月次 tools/monthly_update_company.sh 作成(dentsu.dot・Love the Work・グローバル部署・ファクト(ニュース/統合レポート)・駐在員一覧 → fix_pack_links → Skillと比較し変わったものだけ反映)。平日14:00、個人Macの月次(last_run.txt)が当月完了してから動く(同時保存回避)。state: last_run_company.txt。
- 自動更新しないもの(10/19点検): topic_expert_index(手で選別済み、再生成するとPart3が復活)、Salesforce由来の cases_*/knowledge_*/case_expert_index/faq/tools/pm_checklists(knowledge_index.db 8/18時点、SF全件エクスポートとDB再構築が要る)、局員プロフィール(8/18、取得スクリプトなし)、Teams推定エキスパート(Ollama+手選別)、スライドバンク・LaunchPad(手作業資料)、SKILL.md・references(指示文)。
- 確認: Skill上の credentials_facts / global_department_index / lovethework は「現ソース→生成→fix_pack_links」で反映版と完全一致(手順が再現できる)。
- 2026-10-19(5) 会社Mac月次 com.nakamura.agencyosmonthlyupdate.company(平日14:00)を登録。初回分(10月)を手動反映: credentials_facts(ニュース+6件)・dentsudot 2(fix_pack_links済み)・global_department_index・overseas_staff_index(10月駐在員)をSkill・Difyへ、照合一致。last_run_company=2026-10。
- Love the Work: 共有ブラウザ9226のログインが切れていた(全ブランド0件、画面にSign in)→ユーザーの再ログイン待ち。networkidle待ちで時間切れしていたので domcontentloaded+最大15秒に変更(元 scrape_lovethework_bak_20261019.js)。全0件ならWARN。
- 一覧は tools/README.md「毎月の自動更新」。
- 2026-10-19(6) 中村さん指示で会社Mac月次に追加: Salesforce全件(レポート「GBC全履歴_知見集約用」00OfP00000K25mTUAR、salesforce_source/download_full_history.py。1.5万行で書き出し15秒超→共通処理が受け取れず~/Downloadsに落ちるので拾う)、FAQ(SharePoint 2025-GBCTeam共有リンク、launchpad_source/download_faq.js→FAQ List_Update_YYYYMMDD.xlsx、build_launchpad_tablesは日付付き最新を優先)、担当者一覧(アレココHome、scrape_gbc_dept_contacts.js、networkidleで時々失敗→2回試行)。refresh_db_sources.py で knowledge_index.db の case_records・faq_records だけ入れ替え(バックアップ残す、90%未満なら中止)→ generate_agency_os_pack.py --mode poc → fix_pack_links → add_case_refs(10/19時点で反映版と完全一致を確認)。topic_expert_index は update_topic_expert_part1.py で Part1 だけ差し替え。
- 中村さん方針(10/19): topic_expert(エキスパート認定方法は後日相談・保留)、スライドライブラリ・LaunchPad資料は更新しない、Skill指示文は必要時のみ(月次に入れない)。
- 10/19実績: SF 14,939→14,860件(DB入替済み、旧DB knowledge_index_backup_20261019_144159.db)、FAQ 88件(変化なし)、Love the Work 134→147件(再ログイン後)、担当者一覧は9/15から変化なし。
- 10/19 15時台: SF・FAQ・Love the Work・担当者Part1由来の10ファイル(cases_*7、case_expert_index、faq、lovethework、topic_expert)をSkill・Difyへ反映、照合一致。Difyは10ファイルで10分超かかる。
- 2026-10-22 上司アドバイス: DifyでWeb検索を足せる。上司はTavily(https://www.tavily.com/)と組み合わせている。Agency OS(Dify版)に「社内データ外の質問」用のWeb検索ノード追加を検討(未着手・APIキー取得と課金有無の確認待ち)。ChatGPT版はWeb検索が標準で使えるのでDify側だけの課題。
- 2026-10-23 GBCクレデン共有チャネル週次カタログ: GBC-Knowledge/credential_channel_source/(fetch_channel_listing.py=SharePoint REST一覧、build_credential_pack.py、diff_manifest.py)+tools/weekly_credential_update.sh(会社Mac、平日8:30起動・週1、launchd登録は install_weekly_credential.sh を本人実行)。Dify ナレッジ credential_channel_catalog(71e8e7cd-3c1f-4e1f-a69a-685b943ff5ce)・検索ノード1792200000004、Skill要件K(v174)。URLは pptx=UniqueId方式 Doc.aspx?sourcedoc=%7BGUID%7D、pdf=パス+?web=1。コード実行ノードは出力30要素上限があり、BP局とクレデンは1要素に統合。auto modeはLaunchAgents書き込みを拒否する。詳細 [[work_status/gbc_credentials_slide_bank_master_deck_project_20260930]]
