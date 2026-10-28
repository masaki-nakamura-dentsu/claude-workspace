# Agency OS にBP局×クライアント索引を組み込み + 月次更新へ
Status: done
Date: 2026-10-21
- 元データ: gem_bp_clients_有効のみ_企業単位_20261021.csv([[gem-bp-client-list-extraction]])。GBC-Knowledge配下に作成:
  - gem_source/fetch_gem_bp_clients.js(GEM取引先担当(取)を28局分取得、局ごと再試行付き)、gem_bureaus.json、check_gem_raw.py(完全性チェック)
  - generate_bp_client_pack.py → bp_client_index_by_client.md / bp_client_index_by_bureau.md(有効のみ、局×企業で1社)
  - tools/skill_add_bp_clients.py(SKILL.mdに要件J等7か所を追記、別名出力)
  - tools/monthly_update_company.sh と monthly_freshness_check.py にGEM取得・生成を追加(会社Mac 14:00ジョブ)
- 取得: 17/28局済(raw_20261021)、残り11局を再取得中(第20ほか)。第20で検索ボタン競合で落ちたため再試行を追加。
- 次: 28局揃い→生成→Skill push(新規ファイル追加+SKILL.md)→Dify(dataset cff84aa6…へ dify_kb_create.js --dataset で追加、既存と同名は月次でreplace)→照合→README/memory更新。
- Dify側は既存ナレッジに混ぜる形(専用検索ノードは未配線)。
追記: 28局取得完了(有効10,743行=既存CSVと一致)。ChatGPT Skill v170・Dify(専用ナレッジ+検索ノード、公開)反映・照合済み。月次はmonthly_update_company.shに組込済(11/2以降の初回自動実行は未試走)。詳細は [[agency-os-bp-client-index]]。
追記 2026-10-22: Dify下書きで5問テスト(結果 scratchpad/dify_bp.json)。花王・ほげほげ(該当なし)は正解。NG: ①キリンHD提案の構成案で担当局を「第2BP局」と誤記(正解=第3BP局。キリン(株)/キリンビール(株)は索引に無いのに掲載)し、提案主体として資料に局名を入れた(要件J違反) ②サントリー「主担当」質問で第9局が中心と推察+第9局へ問い合わせ推奨(要件J違反) ③第3局の担当一覧は3社しか返らず全206社に遠い(局→クライアント検索の取りこぼし)。ChatGPT Skillは9224未起動、共有ブラウザ9226からの呼び出し口が不明で未テスト。Status: pending(修正方針の判断待ち)
追記2 2026-10-22: 禁止事項(a)〜(e)をJ節に追加した新指示文 GBC-Knowledge/output/SKILL_20261022.md(ChatGPT)・SKILL_Dify_for_paste_20261022.md を作成。Dify下書きには反映済み・再テストで キリン=第3局正解/局名は「社内メモ」に分離/サントリー主担当を推察せず=OK(公開は未)。ChatGPT Skillへのpush・Difyのtop_k 8→20変更はauto modeに『共有資源の変更』として拒否され未実施。ChatGPT現行Skillのテスト(@agencyos、5問): 花王・第3局206社・ほげほげ=OK、サントリー=「第9局が中心」NG、キリン提案=局名をスライド1/10/12に記載NG。ChatGPT呼び出しは共有ブラウザ9226で『@agencyos』入力→メニューの「スキル Agency OS」をクリック(Enterだと先頭のファイルが選ばれる)。テスト用スクリプト scratchpad/gpt.js。Status: pending(push許可待ち)
追記3 2026-10-22: 中村さん許可で3点反映済み。①ChatGPT Skill: SKILL_20261022.md(J節に禁止事項a〜f)をpush→v172・照合一致、退避 output/skill_backup_20261022(v171)。②Dify: 同趣旨のSKILL_Dify_for_paste_20261022.mdを公開(公開名20261022BP禁止事項)。③DifyのBP検索ノード1792200000003 top_k 8→20(取りこぼし解消、キリンHD・サントリーHDが取れるように)。再テスト: ChatGPT/Dify とも サントリー主担当=特定不可と回答、キリン提案=局名は「社内メモ(クライアント提示不可)」に分離・第3局正解、ソニー・花王・ほげほげOK。残: Difyの局→クライアント一覧は上位20件程度のみ(全件はChatGPT側)、キリン提案で「第3BP局へ事前連絡」と一言(軽微)。Status: done
