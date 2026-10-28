---
name: arekoko_catalog_project
description: アレココ資料を「1資料=1エントリ」の目録にしてAgency OSに入れる検討(2026-10-17試作)
metadata:
  type: project
---
2026-10-17 中村さん: 知見カードがあまり機能していない。資料の中身を目録化すれば使いやすくならないか検討してほしい。

分かったこと:
- Agency OSのPOC Packの知見カードは14,894件中1,500件、資料は404件中192件しか入っていない(半分以上の資料はAgency OSから見えない)。少数の大型資料に偏る(1資料117件など)。
- カードの Why it matters / When to use / Recommended action / Warning はほぼ定型文で、検索・回答の雑音になっている。
- 試作: GBC-Knowledge/generate_arekoko_catalog.py(DBから決定的に生成、LLMなし)→ output/arekoko_catalog_20261017/。目録一覧(62KB)+詳細(892KB)、404資料全部。各資料に国・業種・タグの出現数と収録項目(カード見出し)。
- 試作の弱点: 項目の並びはページ順でない、資料のアレココ上の正式タイトル・登録日・概要が無い、国表記がゆれる(韓国/South Korea/大韓民国)、アレココIDが無い資料が1件。
- 改良案(未実施): 会社Mac(9226)でアレココのKnowledges/Toolsリストから正式タイトル・日付・概要を付ける。元ファイルのスライドタイトル・見出しをページ番号付きで機械抽出して目次にする。
- Agency OSへの反映(chatgpt_skill.js push、Dify)は中村さんの判断待ち。
Related: [[gbc-intelligence-engine-project]] [[agency-os-deploy-tools]] [[agency-os-poc-feedback-20261013]]

2026-10-17 午後(中村さんOKで本格化):
- アレココのリストは Knowledges 279 / Tools 27(8/15以降の新規も含む、DBに無い添付46件)。項目: Title, publicStart, clientName, implementation, associatedCompany, market, summary(概要), relatedTags, staff, notice, keyword(+Toolは serviceSupplier/targetURL/contractPeriod/responsibleDepartment/description)。
- 流れ(GBC-Knowledge/arekoko_source/): fetch_arekoko_meta.js(リスト+DocApp添付一覧、9231)→ download_arekoko_files.js(pdf/pptx/docx/xlsx 426件6.3GB → ~/arekoko_files、Dropbox外)→ extract_pages.py(ページ見出し・本文を機械抽出 → ~/arekoko_pages、19,687ページ)→ summarize_docs.py(自宅Windows Ollama qwen3.8:27b で資料要約+見出しが弱いページの一行説明。Claudeトークン不使用、1件5〜60秒)→ generate_arekoko_catalog.py(目録生成、LLMなし)。旧版の試作スクリプトは generate_arekoko_catalog_draft_20261017.py。
- 要約のトピックは本文に無いものをコードで捨てる。
- SKILL改訂: GPT作業/SKILL_20261017.md・SKILL_Dify_20261017.md・SKILL_Dify_for_paste_20261017.md(目録とCCS設問一覧の案内、CCS ExplorerのURL)。本番反映は中村さんのOK待ち。
- 個人Macでは GPT作業 の SKILL_*.md が0バイトに見えた(Dropboxの未取得、xattrなし)。TextEditで open -g すると実体化した。
- 2026-10-17: summarize_docs.py に Teams 途中経過通知を追加(共通送信口、30分ごとINFO=件数・%・完了見込み、開始INFO、完了DONE、要約空が3/10/30件でWARN)。間隔は環境変数 AREKOKO_NOTIFY_EVERY_SEC(既定1800)。プロセスが落ちた・固まった場合は本体から通知できないので、Claude側の見張り(PID+ログ20分無更新)で検知する。
- 2026-10-17 13:10: 331件目でOllamaの応答待ちのまま33分停止(Ollama側はモデル未ロード状態)。urlopenのtimeoutを900→300秒にして再開。
- 2026-10-17 13:27 完成: output/arekoko_catalog_20261017_01/(index 63KB + 詳細2ファイル計2.2MB)。306登録・438ファイル・要約419・目次19,320行。画像のみPDF6件は要約なし。知見カード0件の登録も目録には入った。既知の粗: PDF見出しの先頭1字欠け(例 p1「026年版」)。Agency OS反映は中村さんOK待ち(SKILL_*_20261017_01と一緒に)。
- 2026-10-17 要約の誤り確認(中村さん依頼): arekoko_source/verify_summaries.py。機械照合(数字2桁以上・英単語3字以上が本文にあるか。カタカナは英語資料の訳語が引っかかるので対象外)+Ollama 27Bで1文ずつ裏付け判定→裏付けなしは本文どおりに直す/直せなければ捨てる。直した文も機械照合に通ったときだけ採用。結果は <file>.verified.json、目録生成はこれを優先して使う。機械照合で引っかかったのは1,643文中41文(本文に無い数字、ドイツ語の要約1件)。試行で「社内資料です」等の根拠のない性格づけを直していた。
- PDF見出しの先頭欠け(「026年版」): PDF自体の文字情報・見た目ともに欠けている(スライドの端からはみ出した文字)。generate_arekoko_catalog.py の repair_heading で登録タイトル・ファイル名と突き合わせて最大3字を補う。
- 並列化: WindowsのOllamaは同時に1件しか処理しない(3件同時→3倍の時間、10/17計測)。OLLAMA_NUM_PARALLEL を上げる依頼を windows_inbox task-017 に登録。個人MacはM4 Pro/24GBでローカルOllama稼働中だがモデル未取得(27Bは17GBでMacの作業を圧迫、8Bは品質が落ちる)。
- 2026-10-17 15時 照合完了・目録 output/arekoko_catalog_20261017_02 が最新(要約は照合済み、見出し補正は1件のみ)。照合結果: 1,643文中 書き直し630・削除43(書き直しの多くは言い回しの変更、根拠のない性格づけ「社内資料」等を除去。一部は裏付けのある情報まで削る過剰修正あり、正確さ優先で許容)。
- 追加修正: 要約は必ず日本語(中国語・ドイツ語資料11件が原語で要約されていた→作り直し)。照合の数字は万/億を百万/十億に換算して比較(「5000万ドル」=「$50 million」)。本文が無く「ファイル名は〜」だけの要約4件は載せない。
- 見出し補正の失敗: 最初はスペースを消して照合したため「Thailand Credentials」→「tsuThailand…」など40件誤補正。数字始まり(直前も数字)と小文字始まり(スペースなしで英字に続く)だけに限定して解消。補正は機械的にやるほど誤爆するので、変更一覧を必ず出して目視する。
- 中村さんのOK待ち: ChatGPT Skill・Difyへ目録(_02)+CCS設問一覧+SKILL_*_20261017_01 を反映。
- 2026-10-17 15:20 本番反映完了(中村さんOK)。最新: 目録 output/arekoko_catalog_20261017_04、CCS output/ccs_catalog_20261017_01、指示文 GPT作業/SKILL*_20261017_02。詳細は [[agency-os-deploy-tools]]。Difyテスト: タイCCS提案は正しい調査・実在設問、サウジの資料ページは正しいが p27-29(広告費推移)を拾えない(検索件数の限界)、ベトナム契約の質問に「CCSは対象外」の1行が残る。
