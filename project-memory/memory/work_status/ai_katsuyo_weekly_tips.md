# GBC週刊AI Tips (AI活用PJ)

## 2026-08-18T10:00:00+09:00
Status: in progress
What: ユーザーからGBC AI活用PJの一環で「毎週ChatGPT/Copilotの使い方Tipsを発信したい」という依頼。まず契約状況の確認方法を聞くよう指示されたため、Outlookエクスポートを検索し、ChatGPT Enterprise(電通AI管理事務局が窓口、クレジット制運用: 通常600/月→6月から上限2,000/月、AIマスターは10,000/月)とGitHub Copilot Enterprise(ISnaviの生成AI利用可否リストに記載、月39USD/人、法人契約調整中)の情報を発見。Microsoft 365 Copilot(Outlook/Teams統合版)自体の座席数は見つからず。AskUserQuestionで確認方法を聞いたところ「今回はざっくりの前提で進めてOK」との回答。
Next: Tips本編の作成に着手。

## 2026-08-18T10:30:00+09:00
Status: in progress
What: [[gbc_department_move_2026]]を参照し、ユーザー自身の実務(議事録整理・Salesforceピッチリスト・アニメレポート・QBR・Smart-KINMU等)に沿った8週分のTips「GBC週刊AI Tips」をHTML Artifactとして作成・公開(URL: https://claude.ai/code/artifact/cc6b432c-928e-4bd8-8dad-3fa29c728b2e)。ChatGPT/Copilotをタグ色分けし、コピペ用プロンプト例を添付。8/18開始のAIアンバサダー制度([[ai_katsuyo_pj_ambassador]])の週次ヒアリング記録(5W1H)とWeek1の内容が噛み合う旨を補足。
Next: ユーザーからのフィードバック待ち。

## 2026-08-18T11:00:00+09:00
Status: done
What: ユーザーから「Vol.1は保存しておいてほしい、内容が自分の業務に寄りすぎているので他部署(アカウント・プロデュース部/ソリューション・プランニング部/業務管理部/局付け/拠点事業プロデュース部)中心に、かつレベルの高い使い方(例: 翻訳と同時に返信案も出力、のような複合プロンプト)を紹介してほしい」とのフィードバックを受け、Vol.1は別ファイルのまま保持し、新規に「GBC週刊AI Tips Vol.2」(Week09-16、8週分)を作成・公開(URL: https://claude.ai/code/artifact/e7133ce8-9a58-4b27-9ddf-9e2c83962d4f)。①②③形式の番号付き複合プロンプト、ChatGPTの画像/ファイル添付分析、カスタムGPT/プロジェクト機能によるテンプレート化まで含めた。
Next: —(配信形式は未指定。ユーザーが会社Mac(d14461)で作業continueする旨のみ受領)

## 2026-08-18T11:05:00+09:00
Status: done
What: ユーザーが「会社のMacで続きをやります」と発言。このセッションでの作業はここまで。プロジェクトの経緯・成果物URL・未決事項を[[ai_katsuyo_pj_weekly_tips]]に恒久メモとして保存し、d14461側セッションが引き継げるようにした。
Next: 会社Mac(d14461)側のセッションで、配信形式(Teams投稿/メール/PPTX等)の決定、AIアンバサダー制度との連携要否の確認、Vol.3以降の検討へ続く見込み。

## 2026-09-29T11:45:00+09:00
Status: done
What: ユーザーから「今月の週次AIダイジェストからおすすめTipsを抜き出し、局内配布用資料を作って」との依頼。既存の月次配信フォーマット`Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/Project_AI業務活用PJ/GBC局内へのTips配信フォーマット/AI_Tips2026年9月分.pptx`(1Tip=1スライド、目的/概要/具体的なプロンプト/ポイント+右カラムに実際のChatGPT出力スクリーンショット、既存4スライド)を雛形として、9月の週次ダイジェスト4本(08-31/09-07/09-14/09-27)から評価済みスコア(既存メモリ[[feedback_ai_tips_content_curation_criteria]])を基に上位4件を選定: 「念のため」を削って精度UP(90点)、AIに辛口批評させる壁打ち術(90点)、公開前AI情報漏洩セルフチェック(85点、セブンイレブン事例)、AI活用の説明を先に準備(80点、九州国立博物館事例)。09-14週は全件Gemini依存で低評価のため不採用、Office add-in系トピックは自動化困難(ChatGPT web chatのみ確立済み)のため見送り。ChatGPTボットブラウザ(port 9224)で各Tipsの試してみるプロンプトを実際に実行しスクリーンショット取得、python-pptx+テキスト幅実測(Meiryo/Consolasフォント直接測定)によるカスケードレイアウト自動計算でテキストオーバーフローを解消、qlmanageで4スライド全て視覚QA確認、validate.py全項目PASS。`AI_Tips2026年9月分_20260929.pptx`として同フォルダに新規保存(既存ファイルは上書きせず温存)、open済み。
Next: —(ユーザーの最終確認待ち)
