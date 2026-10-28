# Agency OS PoC報告資料をTeamsの声で更新 — 2026-10-15
Status: done
Machine: d14461
- 入力: Teams(10/14 15:00以降の返信。daemon取り込みを待って取得)、フォーム7件目(解さん、Excelをブラウザで開いて同期させてからREST取得)
- 出力: Agency_OS_PoCフィードバック報告_20261015_01.pptx(18枚)。_20261015.pptxは相談スライドの番号ずれがある失敗版(使わない)
- 編集スクリプト: 20260909PoC説明/edit_PoC報告_20261015.py(_20261013_01=中村さん修正版を開いて該当シェイプだけ変更)
- 変更: 表紙日付/要点/概要(7件・3.7・11名/28)/使われ方に解さん行/新規「Teamsで寄せられた声」/課題6件/対応6件/出来ることに2用途追加/指標/相談3を名称へ/全結論行を言い切り型へ

## 追記(同日) 名称3案・Difyログ・KPI・Appendix・改修
Status: done(差し替え・反映は中村さん作業待ち)
- 資料: Agency_OS_PoCフィードバック報告_20261015_02.pptx(27枚)。Dify使われ方/不足、名称案(ChatGBC・askGBC・GBCNavi)、KPI(ログと閲覧数で自動)、Appendix(使い方の例4枚+ChatGPT/Dify使い分け)。スクリプト edit_PoC報告_20261015_02.py
- Difyログ取得: console.dj-dify.dentsu.jp/console/api を同一オリジンで(先に /console/api/system-features を開く)。chat-conversations / chat-messages / statistics/*
- 改修: GPT作業/SKILL_20261015.md・SKILL_Dify_20261015.md・SKILL_Dify_for_paste_20261015.md、GBC-Knowledge/add_case_refs.py → output/agency_os_pack_20261015、差し替え用_20261015(18ファイル)
- 追記: Difyワークフローに「検索語の言い換え」を追加し指示文10/15版と合わせて公開(API経由)。テスト2件OK。Difyナレッジ差し替えとChatGPT Skillは未(中村さんと分担相談中)
- 追記: ChatGPT Skillへ18ファイル+指示文10/15版をAPIで反映(version 139、全件一致、他21ファイル・PPTX無傷)。Difyナレッジは dify_kb_replace.js で差し替え中(大物待ち)。ツールは GBC-Knowledge/tools/
- 追記: Difyナレッジ21件の差し替え完了(全件サイズ一致)。途中でDifyのログイン期限切れ(401)→dify_kb_replace.jsにrefresh-token再試行を追加。報告書を1本の流れに再構成 → Agency_OS_PoCフィードバック報告_20261015_03.pptx(28枚、スクリプト edit_PoC報告_20261015_03.py)。9224は使用後に閉じた
- 追記: 文字数制限撤廃版(SKILL_*_20261015_01)をChatGPT/Difyに反映・テストOK。tools/dify_prompt.js 追加。9224は閉じた
- 追記: 文字数制限撤廃を報告書に反映 → _20261015_04.pptx(課題1/対応1/テスト行/改修内容1行を書き換え、スライド追加なし)
