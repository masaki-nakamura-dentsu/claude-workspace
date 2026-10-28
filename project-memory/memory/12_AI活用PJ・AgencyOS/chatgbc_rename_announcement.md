---
name: chatgbc-rename-announcement
description: Agency OSの正式名称がChatGBCに決定(2026-10-27)。ChatGPT版/Dify版の名称変更は未実施(指示待ち)、告知はTeams+メール(海外駐在員のdentsu.co.jp宛含む)
metadata:
  type: project
---
2026-10-27 中村さん: Agency OSの正式名は **ChatGBC**。
- ChatGPT版(Skill表示名「Agency OS」/内部名gbc-ai-agency)とDify版の名称変更は**後で本人が指示**。それまで変更しない。
- 告知はまずTeamsとメール。海外駐在員のdentsu.co.jp宛にも送る(日英併記の案内文を作成、改称日・URLは未定のプレースホルダ)。
**Why:** 名称変更の前に告知を済ませ、混乱を避けるため。
**How to apply:** 「改称して」の指示が来るまでSkill表示名・Difyアプリ名・資料内の名称に手を付けない。改称時は[[agency_os_deploy_tools]]のツールで両方に反映。
Related: [[agency_os_poc_feedback_20261013]]

## 2026-10-28 追記
- 告知メール方針(中村さん指示): 対象は開発を知らない人。英語版は不要(日本語のみ)。位置づけは「GBCの知能を誰でも使える機能」(企画・提案専用ではない)。ChatGPTを使えない人が多いので、冒頭でDify版もあると伝える(読み飛ばし防止)。順序は インストール→使い方。事例は代表3つ(提案以外も)。ChatGPTの思考レベルはInstantでなくその1つ上(High)に誘導。Dify版URLも載せる。
- Dify版URL: https://app.dj-dify.dentsu.jp/chat/UhIAspvW1bROU3Ar 。コンソールはdentsu Japan Okta(djn-client)ログイン。WebAppのアクセスは9/14のPoC資料で「アクセス申請」が必要と書いた(dentsu.co.jpアカウントなら誰でも、とは未確認。海外駐在員が入れるかも未確認)。
- 出力の優先順位修正: SKILL_20261028 / SKILL_Dify_for_paste_20261028 を GPT作業/ に作成(事例+URL→駐在員等→CHECKLIST→CCS/BP/クレデンは最後に短く。CCSは補助化)。**ChatGPT Skill・Difyへ未反映**(会社MacのCDPボット9224/9226が停止中で反映・テスト不可。反映手順は[[agency_os_deploy_tools]])。
- アイコン: GPT作業/ChatGBC_icon/ に「ライン束のG」(SVG+PNG, 白地黒/黒地白)をコードで作成。ChatGPT画像生成は未実施。正式ローンチ時にChatGPT Skillのアイコン登録を中村さんから頼まれている。
