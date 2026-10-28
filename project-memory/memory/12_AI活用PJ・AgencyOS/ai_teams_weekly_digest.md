---
name: ai_teams_weekly_digest
description: "社内AI関連Teamsチャンネルを週1回自動監視し、AI活用PJのTips元ネタをヘッドレスclaude呼び出しで自動要約する仕組み。設定ファイル・スクリプト・運用方法"
metadata:
  type: project
  originSessionId: 86655793-9c0c-4cdd-867b-e20342b361f7
  modified: 2026-09-14T03:05:31.227Z
---

2026-08-18、[[ai_katsuyo_pj_ambassador]]のキックオフ議事録で出た「社内各所のAIチームTeamsをウォッチしてネタを引っ張ってくる」というアイデアを受けて構築。既存の[[continuous_data_capture_setup]](teams_daemon.pyが全チャット/チャンネルを30分おきにポーリングして`~/TeamsExport/data/teams_messages.jsonl`に蓄積)をそのまま土台に使い、新規に「週次で対象チャンネルだけを抜き出して自動要約するレイヤー」を追加した。

## 構成(すべて会社Mac d14461上)
- **`~/TeamsExport/ai_watch_channels.txt`**: 監視対象チャンネル/チーム名のリスト(1行1件、`#`でコメント)。`teams_messages.jsonl`の`chat`フィールドと完全一致で照合する。初期値はGBC AI活用PJ自身の運営チャンネル群(共有会/運営用/AIマスターGr/拡大版第一回・第三回/AIコンシェルジュ)。**他部署のAIチームチャンネルを追加する場合、ユーザーが先にTeamsで参加(join)し、その表示名をこのファイルに追記するだけでよい**(収集自体は既存daemonが全チャット共通で行っているため追加のスクレイピング設定は不要)。
- **`~/TeamsExport/weekly_ai_digest.py`**: 本体スクリプト。
  - 状態ファイル`~/TeamsExport/data/weekly_ai_digest_state.json`に前回実行時刻(`last_digest_run`)を保持
  - 前回実行から6日未満なら即skip(頻繁なlaunchdポーリングでも安全)
  - 監視対象チャンネルの、前回実行時刻以降のメッセージだけを`teams_messages.jsonl`から抽出(最大400件に切り詰め)
  - **新着メッセージが0件ならclaude呼び出し自体をスキップ**(トークン節約、ユーザーの明示的要望)
  - 新着があれば、ヘッドレスclaude(`claude -p "<prompt>"`)を1回呼び出し、Tips候補として使えそうな内容だけをMarkdownダイジェストに要約させる
  - 出力先: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/Project_AI業務活用PJ/weekly_ai_digest/AI関連Teams_週次ダイジェスト_YYYYMMDD.md`
  - claude呼び出し失敗時は状態を更新せず、次回同じウィンドウで再試行される(データロストしない設計)
  - `claude`バイナリはPATHに無い(VSCode拡張機能に同梱)。`~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude`をglobで動的に解決している(拡張機能バージョンが上がってもパス変更で壊れないように)。ここは本チャット自体を動かしている実行環境と同じ実体。
- **`~/Library/LaunchAgents/com.nakamura.aiteamsdigest.plist`**: 6時間おき(`StartInterval=21600`)+`RunAtLoad=true`でスクリプトを起動。実際に「週1回」動くのはスクリプト内部の6日ガードによる(既存のcalendar/email syncと同じ「短い間隔でポーリング、内部で冪等にスキップ」設計思想)。Python実行パスは`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`(既知のTCC platform-binary問題を踏まえ、既存ジョブと同じ非プラットフォームバイナリを使用)。ログは`~/TeamsExport/digest_launchd_stdout.log`/`digest_launchd_stderr.log`。

## 設計判断の経緯(ユーザーとのやり取り)
- 「なるべくトークンを使わないように」という要望を受け、AskUserQuestionで2点確認:
  1. 対象チャンネルの特定方法 → 「既存の登録済みチャンネル」+「まだ参加していないチームもある」の両方
  2. 実行頻度 → 週1回
  3. 要約タイミング → 収集と同時に自動要約
- 要約方式についてさらに確認: 「AI一切介さずキーワードで整形(トークン不使用)」vs「ヘッドレスclaude呼び出しで要約」→ **後者を選択**。ただし新着ゼロの週はclaude呼び出し自体をスキップする設計にして、無駄なコストは避けている。
- 動作確認: `claude -p "Reply with exactly: OK"`が実際に応答すること、launchd経由での初回実行が`skip: ...新着メッセージなし`で正常終了(exit 0)することを確認済み(2026-08-18時点、対象チャンネルは直近実運用が薄いため0件が正しい結果)。

## 2026-08-18(同日夜): ユーザーが実際のAI関連チームのリンクを共有、チャンネル追加
ユーザーから社内の実際のAI関連Teamsチーム/チャンネルのURL(計4チーム分のリンク→後に1チーム分は7チャンネルの詳細リンクに整理し直して再送)が共有された。共有ブラウザ(port 9226)経由でPlaywrightで各リンクを開いて名前と参加状況を確認:

- **AIベースキャンプ**(チャンネル「一般」)、**AIマスターコミュニティ**(チャンネル「お知らせ・告知」): 閲覧権限はあったが、当初は左レール(お気に入り)に出ていなかったため既存daemonの収集対象外だった → ユーザーがTeamsで「お気に入り」登録 → 左レールに出現し収集対象化を確認
- **AIベースキャンプ配下の6チャンネル**(groupId `afa4506f-6db1-4227-9ab6-3eb7058bae84`。ユーザーが個別チャンネルリンクとして再共有): 生成AI活用・業務効率化Tips/情報交換・事例共有・交流/テクノロジーニュース＆トレンド＆雑談/Weekly AI Trend Report/AI革命対策本部（木曜1600-）/dentsu生成AIなんでも相談室 — いずれも`ai_watch_channels.txt`に追加済み
- **groupId `c91206a0-c52e-49c8-98c9-7873298723f7`のチーム**: 最初にユーザーが共有した4リンクのうち1つ。当初Playwright操作では中身が表示されず未参加と誤判定したが、ユーザーが確認したところ実際には**「0_全参加者（全ユニット＋CoE_PM）」というチャンネルで、既に参加済み**だった(Playwright側の描画/クリック処理がたまたま失敗していただけ、というオチ)。左レールで存在確認の上`ai_watch_channels.txt`に追加済み。
- 左レール探索中に偶然もう1つ発見: **「【AIのニュースを発信！】AI MIRAI」**(既に左レールにあり、追加のお気に入り登録不要で即収集対象化)

**重要な既知の制約(要注意)**: `weekly_ai_digest.py`のチャンネル照合はteams_daemon.pyが記録する「チャット名の完全一致文字列」ベースであり、**チーム名を含まないチャンネル単体の表示名**(例:「一般」「お知らせ・告知」)しか取得できない。「一般」は社内の無数のチームに同名チャンネルが存在するため一意に識別できず、**意図的にウォッチ対象から除外**した(AIベースキャンプの「一般」チャンネルはこの制約により現状カバーされていない)。「お知らせ・告知」も同様のリスクがあるが、2026-08-18時点で左レール上に他の同名チャンネルは無く一意だったため追加した — 将来同名チャンネルが増えたら誤収集のリスクがある。根本対応(teams_daemon.py側でチーム名+チャンネル名を組み合わせた一意なキーを記録するよう改修)は未着手、必要になったら検討する。

## 2026-08-18(同日夜、続き): 実データでのテスト投稿を実施
ユーザーから「テストでアウトプットを見たい、自分のTeamsチャットに投稿してみて」との依頼。実際の過去ログ(GBC AI業務活用PJ関連チャンネル、263件、2026-02〜08月分)を使い、`weekly_ai_digest.py`の`build_prompt()`+ヘッドレスclaude呼び出しをそのまま流用してサンプルダイジェストを生成(架空データではなく実データ)。`post_self_chat.py`経由で自分チャットに「【テスト投稿】」ラベル付きで投稿・送信成功。

**生成された内容の質は良好**: 海外市場0次分析(ワードクラウド)、プロンプトのJSON形式化、SNS投稿検索のツール使い分け、大量ソース参照時の誤回答対策、ChatGPTメモリ管理のコツ、Global People Model実案件活用、画像生成アイコン変換Tips — いずれも発言者・日付付きで具体的、Tips配信の元ネタとして十分実用的な粒度だった。この結果から、要約プロンプト自体の設計(build_prompt内の指示文)は現状のままで機能として問題ないと判断できる。

新規追加した6+2チャンネルはこの時点でまだdaemonが新規メッセージを収集していない(favorites登録直後のため)ため、今回のテストは意図的に旧チャンネルの蓄積データを使った。**新規チャンネルに実際の投稿が付いた後の本番エンドツーエンド動作(state管理・claude呼び出し・ファイル出力)はまだ未検証** — 次回そちらを確認すること。

## 2026-08-18(同日夜、さらに続き): リッチテキスト化・パーマリンク・実際のTeams自動投稿に対応(大幅リライト)
テスト投稿を見たユーザーから改善要望: (1) GBC AI業務活用PJ以外のチャンネルからもちゃんと抽出できるか確認したい (2) Markdownの`##`等が生表示されて読みにくい→太字やフォントサイズ・色で見やすく (3) 元投稿に飛べるURLリンクを張る (4) データソース(チャンネル名)を明記する (5) 要約中の重要キーフレーズを色で目立たせる。これを受けて`weekly_ai_digest.py`を全面リライトした:

- **`channel_ids.json`(新規)**: chat名→Teamsパーマリンク構築用ID(channelId/groupId or chatId、tenantId)のマッピング。共有ブラウザで各チャンネルを右クリック→「リンクのコピー」(要注意: メニュー文言は「リンクを**コピー**」ではなく「リンクの**コピー**」)を自動操作して収集。GBC AI業務活用PJ系は「チーム/チャンネル」ではなく実は**「チャット」種別**(グループチャット)であることが判明し、パーマリンク形式もchannel用/chat用で異なる(chat用はgroupIdなし)。全ウォッチ対象15件中13件のID取得済み、未取得は「GBC AI活用PJ 拡大版 第一回」と「AI MIRAI」(左レールから見つからず、要再調査)。
- **claudeへのプロンプトを構造化JSON出力に変更**: 各トピックに`title`/`summary`/`highlight`(要約中の重要キーフレーズをそのまま抜き出し)/`source_chat`/`source_mid`を持たせる。mid(メッセージの一意ID)も生ログに含めて渡すようにした。
- **HTML化してTeamsへリッチテキストとしてクリップボード経由でペースト投稿**: `post_html_to_self_chat()`が`navigator.clipboard.write()`でHTML(text/html + text/plain)を書き込み、compose boxに`Cmd+V`でペースト→Enter送信。**plain textのinsert_text()ではリッチ書式が効かないため、この方式に変更**(要: `context.grant_permissions(["clipboard-read","clipboard-write"])`)。太字見出し(紫`#5B2D90`)、重要キーフレーズ強調(赤`#C0261E`太字)、出典チャンネル名(グレー小文字)、「元の投稿を開く」リンク、を実装。
- **`--test [--days N]`フラグを追加**: state管理を無視して即座に実行・投稿できる(本番の週次実行とは別に、いつでも動作確認できるように)。
- **実データでの検証結果(2026-08-18)**: `--test --days 200`で263件のログから**12トピックを複数チャンネル(GBC AI業務活用PJ 共有会/運営用/拡大版第一回)にまたがって正しく抽出**、自分チャットへの投稿に成功。投稿後のDOMを直接検査し、`<strong>`太字・`<span style="color:...">`色付け・実際に機能する`<a href="https://teams.microsoft.com/l/message/...">`リンクが正しく生成されていることを確認済み(パーマリンクの実クリック動作そのものは未検証、フォーマットの妥当性は確認済み)。

**重要な仕様変更(ユーザーに要説明)**: 本番の週次自動実行(launchd経由)も、これまでの「ファイル保存のみ」から**「自分チャットへの自動投稿+ファイル保存」に変更された**。次回の対象チャンネル新着発生時、ユーザーの自分チャットに毎週自動でメッセージが投稿されるようになる。

## 2026-08-18(同日夜、さらに続き2): 重大な同時実行バグを発見・修正、パーマリンクは未解決
ユーザーから2回目のフィードバック: (1) GBC AI業務活用PJ以外からの抽出が見えない (2) トピック間の空白行 (3) リンクがどれも正しく機能していない (4) タイトルのフォントを大きく (5) テストは200日でなく40日で十分。

**重大インシデント調査**: `--test --days 40`を実行→daemon(teams_daemon.py)がちょうど同時にポーリング中(左レールDOMを激しく操作中)で、自チャット投稿後の検証で全く無関係の他人とのチャット(齋藤賢太郎さん、中村佳菜さん/土門達郎さんのグループ)にいることが判明し、**投稿が他人のチャットに誤送信された可能性を懸念**。teams_messages.jsonl(daemonが同ポーリングで収集した最新データ)を全文検索した結果、ダイジェスト文言はどこにも見つからず、**誤送信ではなく単純にサイレント送信失敗だったと判明**(実害なし、ただし紙一重だった)。

**根本原因**: `post_html_to_self_chat()`が左レールのtreeitem indexを読み取った直後にdaemonが同じDOMを操作すると、クリック時点でindexの対応がずれ、意図しないチャットをクリックしてしまう。従来のコードはクリック成否を検証せず「送れたはず」で処理を続けていたため、失敗が完全にサイレントだった。

**修正**: クリック後に必ず`page.title()`に「あなた」が含まれるか検証(最大3回リトライ)、ペースト直前・送信直前にも再検証、送信後もメッセージ数増加を確認——**どこかで自チャットにいないと判明したら例外を投げて中断し、絶対に他のチャットに書き込まない**設計に変更。daemonがアイドル(直近のポーリング完了ログ確認)であることを確認した上で`--test --days 40`を再実行し、正常に自チャットへ投稿されたことを確認。

**残った未解決の問題: パーマリンクが機能しない**。投稿されたリンクを実際にクリックして検証したところ、意図したメッセージ/チャットではなく**全く無関係な「GlobalQ編集部 | 一般」チャンネルに着地**した。`/l/message/{chatId}/{mid}?tenantId=..&parentMessageId=..&createdTime=..&context=%7B%22contextType%22%3A%22chat%22%7D`という構築式(Microsoftの一般的なdeep link仕様から類推したもの)は**chat種別のリンクでは正しく機能していない**ことを確認。channel種別(groupId付き)の方は未検証。正しい形式は実際のメッセージを右クリック→「リンクのコピー」で得られる生の文字列を解析しないと確定できない見込み(2026-08-18時点、メッセージ単位のコピーリンクUI操作は要素特定に失敗し未達成)。**ユーザーには、投稿された「元の投稿を開く」リンクは現状信頼できない旨を明示的に伝えた**。

**新チャンネル(生成AI活用・業務効率化Tips等9件)は、daemonの完全なポーリング後も引き続きメッセージ0件**。teams_daemon.pyは新規チャンネルでも直近3日分のみバックフィルする設計のため、これはバグではなく単に該当期間に投稿が無かったための正しい結果と判断(要再確認: 今後実際に投稿があった際に正常に収集されるか)。

## 2026-08-18(同日夜、さらに続き3): 監視対象からGBC AI業務活用PJ自身のチャンネルを除外
ユーザーから: 最終的なダイジェストは「GBC AI業務活用PJ 共有会」に投稿する運用にするので、そのチャンネル自身を監視対象に含めると自己参照になってしまう。あわせて「GBC AI業務活用PJ 運営用」「GBC AIマスターGr」「05-2. この業務、AIでできる？」も除外してほしいとの指示。`ai_watch_channels.txt`からこの3チャンネル(元々未追加だった05-2も含め明記)を除外し、コメントで理由を記録。現在の監視対象は12チャンネル(拡大版第一回・第三回、AIコンシェルジュ、AI MIRAI、AIベースキャンプ配下6件、お知らせ・告知、0_全参加者)。

**重要な運用フロー確定**: このダイジェストシステムの最終形は「監視対象チャンネル群から集めた情報を要約し、GBC AI業務活用PJ 共有会に投稿する」という設計。テスト投稿は引き続き自分チャットで行い、本番切り替え(投稿先を共有会に変更)はまだ未実施。

同じ会話の中で追加で「GBC AI活用PJ 拡大版 第一回」「拡大版 第三回」「ＡＩ コンシェルジュ Concierge Ai」も対象外にとの指示があり、最終的に**監視対象は9チャンネル**まで絞り込まれた: 0_全参加者(全ユニット＋CoE_PM)、AI革命対策本部(木曜1600-)、Weekly AI Trend Report、dentsu生成AIなんでも相談室、【AIのニュースを発信！】AI MIRAI、お知らせ・告知、テクノロジーニュース＆トレンド＆雑談、情報交換・事例共有・交流、生成AI活用・業務効率化Tips。**GBC AI業務活用PJ自体の運営系チャンネル(共有会・運営用・AIマスターGr・拡大版シリーズ・AIコンシェルジュ)は全て除外され、他部署発の外部AIチームチャンネルのみを監視する設計に確定した。**

## 2026-08-18(同日夜、さらに続き4): スケジュール確定・Web(YouTube/ニュースサイト)クローリング機能を追加
ユーザーから「実装する。週1回月曜朝に実行、他の月曜朝タスクがあれば合わせる。送信先は当面自分宛のみ、将来的にチームチャットへ」との指示。既存launchd(`com.nakamura.aiteamsdigest.plist`)を`StartInterval`ポーリングから**`StartCalendarInterval`(毎週月曜8:00)**に変更(personal_sns_management_projectの`com.nakamura.snsdraft.plist`が同じMon/Thu 8:00パターンを使っていたのを参考に採用)。

続けて「ネット上(YouTube/Webサイト)のTipsもクローリングして取り込みたい、トークンを節約する仕組みで」との依頼。**設計方針**: RSS/Atomフィードのポーリングは完全にLLMを使わない(標準ライブラリのHTTP+XML解析のみ)、要約時(週1回のヘッドレスclaude呼び出し)にのみTeamsメッセージと合流させて渡す、という構成に(既存の[[feedback_prefer_deterministic_over_llm]]方針と合致)。

**実装**:
- `~/TeamsExport/web_watch_sources.txt`: 監視対象RSS/AtomフィードURLのリスト(1行1件)。YouTubeチャンネルもRSS URL形式(`https://www.youtube.com/feeds/videos.xml?channel_id=...`)で追加可能と明記
- `~/TeamsExport/web_tips_collector.py`: フィード取得→新着アイテム(タイトル・リンク・日付・概要・フィード自身のtitleをsource_nameとして)を`data/web_tips_items.jsonl`に追記。dedupは`data/web_tips_seen.json`(source+linkのSHA1ハッシュ)。LLM呼び出し無し
- `com.nakamura.webtipscollector.plist`: 6時間おきに`web_tips_collector.py`を実行(こちらはStartInterval、頻度を上げてもコストゼロなため)
- `weekly_ai_digest.py`を拡張: `collect_new_web_items()`追加、`build_structured_prompt()`がTeamsログと合わせてWEB由来アイテムも同じプロンプトに含める(JSON出力スキーマに`source_url`を追加、WEB由来トピックはこちらを直接使い、Teams由来は従来通り`source_chat`+`source_mid`からパーマリンクを構築)
- **SSL証明書エラーに遭遇・修正**: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`(python.org版)は`Install Certificates.command`未実行だと`urllib.request`がCERTIFICATE_VERIFY_FAILEDで失敗する既知の問題。`certifi`パッケージ(インストール済みだった)のCAバンドルを明示的に`ssl.create_default_context(cafile=certifi.where())`で使うよう修正し解決。**今後この同じpython3バイナリで新規にHTTPS通信するスクリプトを書く際は、同じSSL証明書問題に最初から気をつけること**(calendar/emailの既存syncスクリプトはローカルファイル読み書きのみでHTTPS通信していなかったため、これまで顕在化していなかった問題)

**初期ソース**: ユーザーが具体的な候補を思いつかなかったため、一般的な日本語AIニュースソースを提案・動作確認の上で採用: **ITmedia AI＋**(`https://rss.itmedia.co.jp/rss/2.0/aiplus.xml`)、**AINOW**(`https://ainow.ai/feed/`)。候補として検討したがリンク切れ/404で不採用: ledge.ai。ASCII.jpの全社汎用フィードはAI特化でないため見送り。

**動作確認**: 実データで30件収集(ITmedia 20件+AINOW 10件)、`weekly_ai_digest.py --test --days 3`(Teamsメッセージ0件、Web30件)で正しく5トピック抽出・自分チャットへの投稿を確認。「原始人プロンプトで節約」「AIペルソナで壁突破」など実務Tipsとして使える粒度で抽出できており、リンクも実記事URL(itmedia/atmarkit)で確実に機能する(Teamsパーマリンクと違い、こちらは単純な外部URLなので信頼性が高い)。

## 2026-08-19: コンテンツ採用基準の学習、対象チャンネル追加、再検証
ユーザーが実際のテスト投稿(13トピック)に対しGood/Bad評価を実施。「技術ニュースそのものではなく、局員の業務(効率化/マーケ/クライアント業務)に直結するTipsになっているか」という基準を明示。[[feedback_ai_tips_content_curation_criteria]]に評価基準・実例を保存し、`weekly_ai_digest.py`の`build_structured_prompt()`のルール部分に同じ基準を追記(製品ニュース・他業種・選定基準記事・安全対策記事は除外、実務で試せるプロンプト/ユースケース/失敗事例は採用)。

続けてユーザーから追加例: 味の素「ほんだし」のAI画像加工でラベルが崩れ炎上した事例([itmedia記事](https://www.itmedia.co.jp/aiplus/article/2608/17/2000000564/))も「興味深い」との評価。理由は(1)実クライアント(味の素)が絡む、(2)SNS投稿は広告代理店の本業。これを受け「実在ブランドが絡むSNS/クリエイティブでのAI活用事例は、成功だけでなく失敗事例も積極採用」というルールを追加(プロンプト・メモリ両方)。

また新規チャンネル追加: 「dj_ChatGPT Enterpriseユーザ_情報共有」チームの「情報交換」チャンネル(groupId `fde1ae13-6a8b-4f7c-a35e-8a6b9faa9de5`)。既に参加済み・左レールにあり、`ai_watch_channels.txt`に追加(監視対象10チャンネルに)。

**再検証**: daemon(teams_daemon.py)との同時実行による安全ロジックの誤中断(意図通りの正しい動作)を2回経験しつつ、daemonアイドル時に`--test --days 3`を実行。改良後のプロンプトで、Web30件から**Good評価だった3トピックのみ**(原始人語トークン削減、AIペルソナでマーケ課題解消、AIエージェントのマーケ活用10選)が正しく抽出され、以前Bad評価だった話題は全て除外されていることを確認。味の素の記事自体は収集時点でRSSフィードの掲載期間外だったため今回のデータセットには含まれていなかった(基準としては反映済みなので、次回以降その種の記事が収集されれば採用される見込み)。

## 2026-08-19(続き): 重大バグ発見 — 新規9チャンネルは「収集できていた」のではなく「収集できていなかった」
ユーザーから「情報交換チャンネルに昨日動きがあったはずだが拾えてる？」と聞かれ調査した結果、**[[continuous_data_capture_setup]]に詳細記載の重大バグを発見**: teams_daemon.pyは「コミュニティ」タイプのチャンネル(`channel-pane-message`というDOM構造)を全く検知できておらず、常にメッセージ0件という結果を返していた(エラーにならないため気づかれなかった)。**このAI関連ダイジェストプロジェクトで2026-08-18に新規追加した9チャンネルは全てこの「コミュニティ」タイプであり、追加時点からずっと収集できていなかった**——これまで「新規チャンネルはまだ活動がないから0件」と説明していたのは誤りで、実際には活動があっても拾えない状態だった。

teams_daemon.pyを修正・再起動済み(詳細は[[continuous_data_capture_setup]])。またチャンネル追加時、「情報交換」という名前がGBC AI業務活用PJ内の空チャンネルと衝突していることも判明(実害は今のところ無い)。

## 2026-08-19(続き2): チャット終了・Mac起動状態に対する堅牢性を確認・強化
ユーザーから「このチャットを閉じても月曜に実行されるか」「会社Macを閉じていても実行されるか」との質問。回答:
- **チャットを閉じても問題ない**: launchd(`com.nakamura.aiteamsdigest.plist`)によるOSレベルのスケジュール実行であり、このClaude Codeセッションとは完全に独立
- **Mac起動状態は要注意点があり、その場で修正した**: この会社Mac(d14461)は毎晩シャットダウンされる運用([[continuous_data_capture_setup]]の既知の制約)。`StartCalendarInterval`は正確に月曜8:00にMacが起動していないと発火しないが、`RunAtLoad=true`があるためMacを次に起動したタイミングで確実に1回実行される(スクリプト内部の6日ガードのおかげで、実行が多少ずれても正しく前回からの差分を拾える)。**ただし発見した実際のリスク**: `weekly_ai_digest.py`の投稿処理は、共有ボットブラウザ(port 9226)が既に起動している前提で`connect_over_cdp`していたが、teams_daemon.py自身がブラウザを自動起動するまでに5分の起動遅延(`STARTUP_DELAY_SECONDS`)がある。Mac再起動直後に両ジョブがほぼ同時にRunAtLoadで走った場合、`weekly_ai_digest.py`の方が先に動いてブラウザが見つからずエラーになる可能性があった。
- **修正**: `weekly_ai_digest.py`に`ensure_bot_browser_running()`を追加(teams_daemon.pyの`connect_shared_browser()`と同じロジック——起動確認→無ければ`open -na "Google Chrome" --args --remote-debugging-port=9226 ...`で自前起動→最大30秒待機)。Teamsタブが無い場合も自動で新規タブを開いて`https://teams.microsoft.com/v2/`に遷移するフォールバックを追加。修正後、`--test --days 1`で正常動作(既存ブラウザ稼働中のケース)を再確認済み。ブラウザが本当に落ちている状態からの自動起動フローそのものは(Chromeを意図的に落とすのが他の作業に影響するため)未実地検証——次にMacが完全再起動した際の初回実行で実質的に検証されることになる。

## 2026-08-24(続き): 情報ソース拡充(Webニュース2件+YouTube2件)
ユーザーから「個人MacでYouTubeチャンネルを4つ追加してもらったはず」との申告があったが、`web_watch_sources.txt`はこのセッションで今日新規作成した会社Mac(d14461)ローカルのファイルであり、個人Macとは同期されておらず、該当する作業記録もメモリ上に見当たらなかった——**別セッション/別プロジェクトとの記憶混同である可能性が高いと判断し、正直にその旨を伝えた**。ユーザーが2チャンネル分(AI仙人、mikimiki webスクール)を再度指定してくれたため、`curl`でチャンネルページから`externalId`(=チャンネルID)を抽出し、RSS URL(`https://www.youtube.com/feeds/videos.xml?channel_id=...`)を構築・動作確認の上で追加。残り2チャンネル(ユーザーが「あなたが提案した」と述べているもの)は特定できておらず、要望があれば別途対応。

あわせてWebニュースも「ITmedia マーケティング」(広告・マーケ業界ニュース)と「AIsmiley」(AI導入事例メディア)を動作確認の上で追加。現在の全情報ソース:
- Teamsチャンネル10件(前述)
- Web RSS: ITmedia AI＋、AINOW、ITmedia マーケティング、AIsmiley
- YouTube: AI仙人、mikimiki webスクール

`web_tips_collector.py`のAtom解析部分で`Element`オブジェクトの真偽値評価に関するDeprecationWarningも発見・修正(`or`演算子ではなく`is not None`判定に変更)。

## 2026-08-24(続き2): Claudeが自主調査してYouTube2件+Webサイト1件を追加
ユーザーから「(自分が探すのではなく)ChatGPT/Copilotで業務改善・マーケ支援・広告作業をする方法を紹介するYouTube/Webサイトを広く探して」との依頼。WebSearchで調査し、チャンネルページの`externalId`を`curl`で抽出→RSS動作確認、という手順で以下を追加:
- **Akiyama Yuta(AI活用術)**(YouTube、UCx3CHuiy-14g2y4hqkpnebQ): SNS運用・AI動画生成・コンテンツ制作の実践テクニック中心。マーケ/広告クリエイティブ業務との親和性が高いと判断
- **KEITO【AI&WEB ch】**(YouTube、UCfapRkagDtoQEkGeyD3uERQ): 最新AIツールの実践的活用法・レビュー
- **Web担当者Forum**(Webサイト、`https://webtan.impress.co.jp/rss.xml`): Web/マーケティング実務者向け老舗メディア

検討したが不採用: 「AI×ビジネスラボ Yama」(副業/クリックベイト色が強く、既存の採用基準([[feedback_ai_tips_content_curation_criteria]])に照らすと「不要」判定になりやすいと予測し見送り)。「ledge.ai」「webtan.impress.co.jpの個別カテゴリRSS」はURLが無効/404で不採用。

現在の全Web/YouTubeソース(8件): ITmedia AI＋、AINOW、ITmedia マーケティング、AIsmiley、Web担当者Forum、AI仙人、mikimiki webスクール、Akiyama Yuta、KEITO。全て`web_tips_collector.py`で動作確認済み(60件新規収集)。

## 2026-08-24(続き3): 個人Mac(ICPTokyo2022)でのバックアップ実行に対応
ユーザーから「会社Macが動いていない時に個人Macでも実行されるようにして」との依頼。実行環境をDropbox共有型に再構築:

**変更内容**:
- `weekly_ai_digest.py`/`web_tips_collector.py`/`ai_watch_channels.txt`/`web_watch_sources.txt`/`channel_ids.json`を
  `~/TeamsExport/`直下から`.claude-sync/data-export/TeamsExport/scripts/`(Dropbox共有フォルダ)へ移動
- d14461側は`~/TeamsExport/scripts`をこのDropboxフォルダへのシンボリックリンクとして再作成(既存の`~/TeamsExport/data`と同じパターン)
- スクリプト内の全パスを`Path(__file__).resolve()`起点の相対解決に変更(ハードコードされた`/Users/d14461/...`を排除)、
  `OUTPUT_DIR`もDropboxルートから動的に導出するよう変更——**マシン依存箇所をゼロにした**
- 共有ボットブラウザのport(9226 vs 9227)/profileディレクトリを環境変数`AI_DIGEST_BOT_PORT`/`AI_DIGEST_BOT_PROFILE`で
  上書き可能にし、同じスクリプトファイルが両Macでそのまま動くようにした
- 状態ファイル(`weekly_ai_digest_state.json`)はもともと`data/`内にあり既にDropbox共有済みだったため無変更で流用——
  **これにより「どちらか先に実行した方が状態を更新し、もう片方は6日ガードで自動的に二重投稿を回避する」という
  仕組みが自然に成立する**([[memory_weekly_review_automation]]の週次メモリレビューで既に実証済みの同じパターンを踏襲)
- d14461のlaunchd plist 2件を新パス(`~/TeamsExport/scripts/...`)に更新、再ロード・動作確認済み
- 旧`~/TeamsExport/`直下の重複ファイルは削除済み(drift防止)

**個人Mac側でやるべきセットアップ手順を`.claude-sync/data-export/TeamsExport/scripts/setup_personal_mac_backup.md`に
詳細記載**(Dropbox経由で個人Macにも同期される)。d14461側からは個人Mac上でのシンボリックリンク作成・launchdジョブ
インストール・実行確認を代行できないため、**次に個人Mac(ICPTokyo2022)でセッションが開かれた際に、このファイルを
見つけて実施する必要がある**——ユーザーにもその旨を伝えた。

**既知の制約**: teams_daemon.py(Teamsメッセージ収集)は個人Macでは動かさない設計のまま(会社Mac限定)。会社Macが
長期間起動しない場合、Teamsチャンネル由来のTipsは更新されないが、Web/YouTube由来のTipsは個人Mac単独でも収集・
生成できるため完全には空にならない。

**副次的に発見した未解決事項**: `weekly_ai_digest_state.json`の`last_digest_run`が今日(2026-08-24、本来の本番初回実行日)時点でも
依然として`2026-08-18T06:12:25`のまま更新されていないことに気づいた——つまり**本番(非--testモード)の自動実行は
これまで一度も成功していない**(今日の朝8:33の実行はSSL証明書エラー等で失敗していた可能性が高い、既に証明書問題は
修正済みなので来週は改善が期待できる)。次回月曜(2026-08-31、または個人Mac側なら火曜)の実行後、state fileが
正しく更新されるか要確認。

## 2026-08-27: AIアンバサダー向けデモ検証で発見した2つの実バグ(未修正)
ユーザーが実際に配信されたTips 11本(週次ダイジェストの実出力)をAIアンバサダーのデモに使えるか検証した際、内容とは別にダイジェスト生成の仕組み自体に2つのバグを発見した:

1. **重複トピックの排除漏れ**: 11本のうち実質8トピックで、3組が同一ニュースの重複だった(「AIペルソナで顧客像を仮想化」×「AIペルソナで企画課題解消」=味の素冷凍食品×NEC BestMoveの同じ話、「ChatGPTの推薦は固定気味」×「AIの『おすすめ』の裏側」=ITmedia 893rd Lapの同じ記事、「自分史をAIに学ばせ執筆」×「自分の全データをAIに学習」=松浦勝人氏の同じ投稿)。Teams発ソースとWeb RSS発ソース(あるいは複数RSSフィード間)で同じ元ネタを別々に拾ってしまっている。`build_structured_prompt()`に統合前のdedup(タイトル類似度またはURL/発言者ベースでの重複検知)が無いのが原因と推測される。
2. **出典名が空欄になるケースがある**: 11本中5本で「出典:」の後にソース名が入らず空欄のままリンクだけ残っていた(簡潔指示でトークン節約/AIペルソナで顧客像を仮想化/ChatGPTの推薦は固定気味/自分史をAIに学ばせ執筆/AIにAIの出力を採点させる、のいずれもTeams発トピック)。`source_chat`が正しく埋まっていない、またはHTML/Markdown整形時にソース名フィールドが欠落している可能性がある。

**How to apply**: 次にこのスクリプトを触る際、(1) `build_structured_prompt()`の出力JSONに重複除去ロジック(同一URL/類似タイトルのトピックは1つに統合するようclaudeへの指示文に明記、または後処理でのdedup)を追加すること、(2) Teams発トピックで`source_chat`が実際に出力に反映されているかHTML生成部分を確認すること。ユーザーはこの2点の修正をまだ依頼していない(検証結果の報告のみ)ため、次回明示的な指示があってから着手する。

## 動作未確認の部分(次回このメモを見た時にチェック)
- **実際に新着メッセージがある状態でのエンドツーエンド動作は未検証**(初回テスト時点で対象チャンネルに直近メッセージが無かったため)。次に対象チャンネルへ投稿があった後、`weekly_ai_digest_state.json`の`last_digest_run`が更新され、`weekly_ai_digest`フォルダに実際にMarkdownダイジェストが生成されるかを確認すること。
- ユーザーがまだ参加していない他部署のAIチームチャンネルは未特定・未追加。9/1定例会以降、具体的なチャンネル名が分かり次第`ai_watch_channels.txt`に追記する。
- 6時間間隔ポーリング+6日ガードの組み合わせが実運用でズレなく週1回に収まるか、数週間分のログで様子見が必要。

## How to apply
今後「週次ダイジェストが動いているか」「AIチームの情報収集どうなってる」と聞かれたら、まず`~/TeamsExport/digest_launchd_stdout.log`と`weekly_ai_digest`フォルダの中身を確認する。ゼロから作り直す必要はない。チャンネル追加の依頼は`ai_watch_channels.txt`への1行追記だけで済む。

## 2026-08-22: YouTube情報源4件を追加候補として確定(個人Mac側セッション、実書き込みは未実施)
ユーザーから2つのYouTubeチャンネル(AI仙人ch、mikimiki web スクール)を`web_watch_sources.txt`に追加したいとの依頼。加えて類似の良質ソースの探索も依頼された。**このセッションは個人Mac(ICPTokyo2022)上で動いており、`~/TeamsExport/`配下は`data`サブフォルダ(JSONLエクスポート)のみDropboxシンボリックリンクで共有されている**——`web_watch_sources.txt`・`weekly_ai_digest.py`本体・`channel_ids.json`等のスクリプト/設定ファイルは会社Mac(d14461)のローカルにしか存在せず、このセッションからは直接編集できないことを確認済み(2026-08-22)。そのため今回は**channel_id特定とRSS動作確認、内容の採用可否判断まで**を行い、実際のファイル追記はd14461側セッションに持ち越し。

**ユーザーが最終確定した追加候補4件(`web_watch_sources.txt`にこの4行を追記すればよい):**
```
https://www.youtube.com/feeds/videos.xml?channel_id=UCRxPq02pjQS_ax60gcTSDHQ
# AI仙人ch — AI歴10年の個人が音声入力等の具体的効率化Tipsを発信
https://www.youtube.com/feeds/videos.xml?channel_id=UChxtIA33ty53Hh4MmkXNASg
# mikimiki web スクール — 登録35万人、Canva/ChatGPT/Gemini/Claude複合プロンプト・仕事術。Vol.2の「複合プロンプト」路線と相性良い
https://www.youtube.com/feeds/videos.xml?channel_id=UCf1da7iwcLGe8Z5YYocRcWQ
# 神川陽太｜Copilot情報局 — Microsoft 365 Copilot専門。GBCが実際契約している製品そのものを扱う点で高適合
https://www.youtube.com/feeds/videos.xml?channel_id=UCCIPlDofGZVef3HArQBRrEw
# 【さき】のAIでええやん。— ClaudeCode活用・Gemini Notebooks連携など再現性の高い具体テクニック中心
```
いずれも`curl`でRSSフィードの実データ取得・直近動画タイトルを確認済み(2026-08-22時点で正常動作)。

**調査時に検討し除外した候補(再提案不要、[[feedback_ai_tips_content_curation_criteria]]の基準で不適合と判断済み)**:
- けんすう(`UCdhJxokoEAfVaXK3xRZ9aHQ`) — キャリア論/抽象的な思想発信中心(切り抜きshorts)、既存Bad判定の「Meta/抽象的教育コンテンツ」と同系統
- ここなのAI大学(`UCopTsucSPUP_N5n4fcLQtXQ`) — 「AIで稼ぐ」副業マネタイズ系インフルエンサー色が強く業務Tipsではない
- SHIFT AI(`UC4ljNH-TkMrevjISKcD6V0Q`) — RSSフィードに動画エントリが存在せず情報源として機能しない
- ウェブ職TV(`UClNZUVnSFRKKUfJYarEUqdA`) — RSS取得が繰り返し失敗、未検証のまま保留

**中間判定でユーザーが今回見送った候補(将来の追加を検討する際に再利用可)**:
- あやや のITスキルアップ塾(`UC4nPvEed6-yII4LNxml8r_w`) — Gmail Gemini自動化など有用だがGoogle Workspace中心(GBCはM365中心のため優先度低)
- 池田朋弘のリモートワーク仕事術(`UCRNTuir40AFoXYn58mriIng`) — 個人vlog色が強く、業務Tipsというより日々の所感・著書執筆記録が多い

**How to apply(次にd14461側でこのメモを見た時)**: 上記4行を`~/TeamsExport/web_watch_sources.txt`に追記するだけでよい。追記後は`weekly_ai_digest.py --test --days 3`等で新規ソースからの収集動作を確認するとよい(既存のITmedia/AINOW追加時と同じ検証パターン)。

## 2026-08-31: 6日ガードを暦週ベースに置換、実行、既知バグ2件を修正
ユーザーから「6日ガードは不要、毎週月曜に実行されるようにして」「本日分を実行して」「重複トピック/出典名空欄の2バグも直して」との明示的指示。`weekly_ai_digest.py`(`~/TeamsExport/scripts/`、Dropbox共有)を修正:

- **ガード方式変更**: `MIN_INTERVAL=timedelta(days=6)`の経過日数ガードを廃止し、`same_jst_week()`(JST・月曜始まりの暦週が同じかどうか)による判定に置換。**背景**: 会社Mac(d14461)は毎晩シャットダウンされ`RunAtLoad=true`で毎朝launchdが本スクリプトを起動するため、日次実行を防ぐガード自体は必要(完全撤廃は不可)——ただし旧方式は「前回の実際の実行」が遅延(今回は火曜深夜)すると、次の月曜が来てもまだ6日経っていないとしてスキップしてしまう不具合があった。暦週ベースなら「今週すでに実行したか」だけを見るので、本番実行が多少ずれても次の月曜には必ず動く。plist(`com.nakamura.aiteamsdigest.plist`)自体はStartCalendarInterval Weekday=1 Hour=8のまま変更不要。
- **出典名空欄バグ修正**: `resolve_missing_sources()`を追加。claudeの出力任せにせず、`source_mid`→Teamsメッセージのchat名、`source_url`→WEB記事のsource_nameを実データから機械的に逆引きして`source_chat`が空の場合に埋め戻す決定的な仕組み([[feedback_prefer_deterministic_over_llm]]方針)。
- **重複トピックバグ修正**: (1) プロンプトのルールに「同じ出来事を指す複数ソースは1トピックに統合すること」を明記する指示を強化、(2) 保険として`dedupe_topics()`を追加——source_mid/source_urlの完全一致、およびtitle+highlightの文字列類似度(difflib、閾値0.6)で明らかな重複を除去。
- **副次的に発見・修正した実バグ**: `post_html_to_self_chat()`の投稿検証がメッセージ件数の前後比較(before/after count)に依存しており、Teams側の仮想化リストの都合で件数が実際の送信と無関係に増減し**false negativeで例外を投げるのに実際は正常投稿されていた**ことが今回の本番実行で発覚(before=22→after=20なのに実際は投稿済み)。件数比較を廃止し、見出し文字列(`heading`、実行ごとに一意)が直近メッセージ本文に実際に現れるかを確認する内容ベースの検証に変更(`verify_text`引数を追加)。

**本日(8/31)の実行結果**: 上記修正後に本番モードで実行→Web由来4トピック(AIモデルでSNS動画量産/ChatGPT Workで代理操作/GA4でAI経由流入を計測/生成AIで動画を記事化、出典: Akiyama Yuta・ITmedia AI＋・Web担当者Forum×2)を正しく抽出・重複無し・出典名すべて記入済みで自分チャットへの投稿に成功(前述の検証false negativeにより一度例外で終了したが、実際は投稿成功していたことをブラウザの実メッセージを直接読み取って確認)。ただし例外発生によりスクリプト自身の`save_state()`は実行されなかったため、`weekly_ai_digest_state.json`の`last_digest_run`と`weekly_ai_digest`フォルダのアーカイブMarkdownファイル(`AI関連Teams_週次ダイジェスト_20260831.md`)はこちらで手動で本番相当の内容に補完・整合させた(以後は今回の検証ロジック修正により、この手動補完は不要になる見込み)。

**How to apply**: 次に「動いているか」聞かれたら、まず`weekly_ai_digest_state.json`の`last_digest_run`が直近の月曜以降になっているか確認。上記の検証ロジック修正後は例外=本当に失敗、と信頼してよいはず(要: 数週間の実運用で再確認)。

## 2026-08-25: 個人Mac(ICPTokyo2022)側バックアップ実行環境セットアップ完了
`setup_personal_mac_backup.md`の手順を実施、以下すべて完了・動作確認済み:
- `~/TeamsExport/scripts` シンボリックリンク作成(Dropbox `.claude-sync/data-export/TeamsExport/scripts`へ)
- python3パス: `/opt/homebrew/bin/python3`(brew版、3.14.7)。この個人Macのbrew版python3にはplaywright/truststore/certifiが未導入だったため`pip install --break-system-packages playwright truststore certifi`で導入
- launchdジョブ2件を`~/Library/LaunchAgents/`に作成・ロード:
  - `com.nakamura.aiteamsdigest.backup`: 火曜8:00(手順書のデフォルト案をそのまま採用、ユーザーからの変更要望はまだ無し)
  - `com.nakamura.webtipscollector.backup`: 6時間おき(StartInterval=21600)。RunAtLoadで即実行・Web記事2件収集に成功
- 共有ボットブラウザ(port 9227, `~/.chrome-profiles/timetree-bot`)は稼働中だったが、Teamsタブがログアウト状態(Microsoftログイン画面)になっていた。ウィンドウを画面上(left:100,top:100)に再配置・前面化でユーザーに知らせた後、2回目の`--test --days 1`実行で正常にセッションが有効化され自分チャットへの投稿に成功(1回目はログイン画面のままpage.evaluateがナビゲーションで中断されるエラー、実際の投稿・誤送信は発生せず)

**重要な既知の挙動**: `RunAtLoad=true`のためplistをロードした瞬間に本番モードが即実行される。ロード時点でstate fileの`last_digest_run`(2026-08-18)から既に6日超過していたため、初回ロードでいきなり本番投稿を試みて上記ログアウトエラーで失敗した(実害なし、state未更新で次回に安全に持ち越し)。**今後同種のバックアップジョブを個人Mac/会社Macいずれかに新規ロードする際は、ロード前に対象の共有ボットブラウザのログイン状態を確認しておくと同じ失敗を避けられる。**

**現状**: 個人Mac側もパイプライン全体(ブラウザ自動化・ヘッドレスclaude呼び出し・Teams投稿)が動作確認済み。次回の実運用は火曜8:00の`aiteamsdigest.backup`または6時間おきの`webtipscollector.backup`。会社Mac(d14461)が先に実行していればstate file経由で自動スキップされる設計は個人Mac側でも同様に機能する想定(実地未検証、次回月曜/火曜の自然発火で確認できる)。

## 2026-09-02: 「手動発掘Tips」の1回限り差し込み機構を追加(Open AI Office Add-in対応)
ユーザーから「ChatGPT Office Add-in(PowerPoint版)の作業効率Tipsも入れたい。新しい情報だけを検索せず、役に立つTipsを探して」との依頼。既存のRSS/Teams自動収集は本質的に「直近の新着」しか拾えない設計([[feedback_prefer_deterministic_over_llm]]によりLLMは要約のみ・収集は決定的処理)のため、特定プロダクトの評価済みTipsをその場でWebSearchし、[[feedback_ai_tips_content_curation_criteria]]の基準(具体性・非自明性・GBC業務関連性・ツールの実利用可能性)でフィルタして3件採用(選択範囲への直接書き込み/配色だけ統一/デッキ構成のAIレビュー)。AskUserQuestionで追加先を確認したところ「次回の週次AI Teamsダイジェストに手動挿入」を選択。

**実装**: `weekly_ai_digest.py`(`~/TeamsExport/scripts/`)に手動Tips差し込み機構を追加:
- `~/TeamsExport/data/manual_staged_topics.json`: 待機列。中身は`build_structured_prompt()`が生成するのと同じJSON schema(title/summary/highlight/how_to_try/source_chat/source_mid/source_url)の配列
- `load_manual_staged_topics()`/`clear_manual_staged_topics()`を追加
- `generate()`に`extra_topics`引数を追加、claude抽出結果の**先頭に**マージしてからdedupe_topics()を通す(手動Tipsは常に優先表示、かつ将来同じ話題がRSS経由で来た場合も重複除去の対象になる)
- `main()`: `staged_topics`が存在する場合、新着メッセージ/WEB記事が0件でもスキップせず生成を強行するよう分岐変更。投稿成功後に`clear_manual_staged_topics()`で待機列をクリア(次回以降は再送しない)
- `generate()`内部もリファクタ: `messages`/`web_items`が両方空ならclaude呼び出し自体をスキップ(手動Tipsのみの週でも無駄なLLM呼び出しをしない)
- 動作確認: `py_compile`通過、`generate([], heading, [], extra_topics=staged)`をドライラン実行し3件が正しくレンダリングされることを確認済み(実際の投稿・ファイル書き込みは行っていない、次回月曜の本番実行で自動的に含まれる想定)

**How to apply**: 今後も「〇〇というツール/機能のTipsを検索して入れて」と言われたら、同じ手順を踏む——WebSearchで調査→[[feedback_ai_tips_content_curation_criteria]]の基準で絞り込み→`manual_staged_topics.json`に同じschemaで追記(既存内容と統合、上書きしない)。ファイルは1回使われると自動でクリアされる設計なので、複数件を貯めたい場合は次回実行前にまとめて追記すること。このファイルの中身が残ったまま何週も放置されている場合、本番実行が滞っている(state file / launchdログ参照)可能性がある。

**重要な追記(2026-09-07)**: この機構でstagingした3件(ChatGPT Office Add-in Tips)がそのまま2026-09-07号の6トピック中3件を占め、ユーザーから「Office製品だけの情報はNGです。通常のChatGPTやCopilotの使い方も同じぐらいTipsが欲しい」との構成バランスに関するフィードバックを受けた([[feedback_ai_tips_content_curation_criteria]]の新dimension 7参照)。**この機構はLLM抽出プロンプトを経由せずコード側で直接マージされるため、`build_structured_prompt()`に追加した構成バランスのルールが効かない**——今後手動でTipsをstagingする際は、特定の1製品/1機能に偏った候補を3件以上まとめて仕込まない、汎用的な(特定Office製品に依存しない)ChatGPT/Copilot技法も混ぜる、といったバランス判断をClaude自身が事前に行うこと。

## 2026-09-07: Teamsログインセッション切れで3日間サイレント停止、Webhook通知を組み込み
ユーザーから「ダイジェストが動いていないようだが確認して」との依頼で調査。**原因**: 共有ボットブラウザ(port 9226)のdentsu SSOセッションが失効し、パスワード再入力画面で止まっていた。これにより:
- `teams_daemon.py`(全チャット収集): `teams_messages.jsonl`の更新が2026-09-04 10:17で3日間停止。ログを見ると当該デーモンはアカウント選択ボタンを9秒おきに無限クリックし続けるだけで、パスワード入力(自動化不可)が必要な状態からは自力で抜け出せていなかった。
- `weekly_ai_digest.py`: 2026-09-07月曜8:00の本番実行が同じセッション切れで「自分チャットが見つからない」エラー(exit code 1)。`last_digest_run`は2026-08-31のまま更新されず、次回起動時に再試行される状態だった。

ユーザーがブラウザで手動ログイン(パスワード+MFA)して復旧。`teams_daemon.py`は「ログイン確認。ポーリング開始。」に復帰、153チャットのポーリングを再開したことを確認済み。

**恒久対応**: ユーザーから明示的指示「そういうエラーが起きている時は必ずWebhookやTeamsでの自分への投稿で知らせて」を受け、両スクリプトの失敗検知箇所に[[teams_webhook_powerautomate]]のWebhook通知を直接埋め込んだ(詳細・一般化した方針は[[feedback_bake_error_notifications_into_automation]]):
- `teams_daemon.py`: `wait_for_login()`が10分でタイムアウトしabortする分岐(`main()`内、「ログイン確認できずアボート」ログの直後)に`notify_teams_webhook()`呼び出しを追加
- `weekly_ai_digest.py`: `if __name__ == "__main__":`ブロックで`main()`を`try/except`し、例外発生時に通知してから`raise`(launchdのログ/exit code記録は従来通り維持)
- Webhook自体の送信失敗は`try/except: pass`で握りつぶし、本来の異常終了処理を妨げない設計
- 実装後、webhook呼び出し自体(HTTP到達性)は動作確認済み。**次にこのパターンの障害(セッション切れ等)が実際に起きた際、通知が届くか自体は未検証**——次回発生時に確認すること。

**How to apply**: 今後「動いているか確認して」と聞かれた際、まずこのWebhook通知が実際に飛んでいなかったか(=ユーザー自身のTeams自分チャット/Power Automate実行履歴)も合わせて確認するとよい。飛んでいなければ通知の実装自体に不具合がある可能性がある。

## 2026-09-07(続き): 手動で本番実行、評価を受けて2つの新ルールを追加
ログイン復旧直後、ユーザーから「今日の分のダイジェスト作って」と依頼。`weekly_ai_digest.py`を手動実行(非`--test`)し正常完了: Teams新着10件+Web176件+手動staged3件から6トピック抽出、自分チャット投稿+アーカイブ保存([AI関連Teams_週次ダイジェスト_20260907.md](../Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/Project_AI業務活用PJ/weekly_ai_digest/AI関連Teams_週次ダイジェスト_20260907.md))、`state`更新済み。

その後ユーザーが6トピックを100点満点で評価([[feedback_ai_tips_content_curation_criteria]]に詳細記録)。2つの新ルールをその場で`build_structured_prompt()`に反映済み:
1. **週またぎ重複排除**: `load_recent_topic_titles()`を追加、直近4回分のアーカイブ`.md`の`## `見出しをプロンプトに「既出トピック」として渡し、同じ切り口の再登場を減点/除外させる。実装中にDropbox同期特有のUnicode正規化(NFC/NFD)不一致で日本語ファイル名パターンの`glob()`が0件になる罠を踏み、日本語文字列でのパターンマッチをやめてこの出力フォルダ内の`*.md`全件を対象にする方式に変更して解決。
2. **AIインフルエンサー制作は明示的に対象外**: GBCが実施しない業務のため、技法として具体的でも除外するルールを追加。

**How to apply**: 次回以降のダイジェストで週またぎ重複が実際に減っているか、他の判断基準と同様に評価結果を見て確認すること。

## 2026-09-14: Webhook失敗通知が会社Macで無言で機能していなかったバグを発見・修正
ユーザーから「動いていない気がする、確認して。会社Macが実行できていない時は個人Macがバックアップで実行するように」との依頼で調査。

**発見1: 今週(9/14月曜)の本番実行が実際に失敗していた**。08:41、会社Mac再起動直後のlaunchd RunAtLoadで起動 → 共有Teamsブラウザがまだ起動しきっていない状態で`post_html_to_self_chat()`が「自分チャットが見つからない」エラーで失敗(過去にも既出の起動レース、[[continuous_data_capture_setup]]参照)。state fileは更新されず(`last_digest_run`は9/7のまま)。

**発見2(重大): 2026-09-07に追加した失敗時Webhook通知(`notify_teams_webhook()`)が、会社Mac固有の`urllib.request`証明書検証エラー(python.org版python3、[[feedback_d14461_python_https_cert_verify_use_curl]]と同根)により、実装以来ずっとサイレントに機能していなかった**。`except: pass`で握りつぶされるため気づけなかった。今回`weekly_ai_digest.py`の`notify_teams_webhook()`を`urllib.request`→`curl`サブプロセス呼び出しに書き換えて修正・動作確認済み(HTTP 202到達確認)。Dropbox共有スクリプトなので修正は両Mac(d14461/ICPTokyo2022)に即時反映される。

**対応**: 修正後、今週分を手動で本番実行(`python3 weekly_ai_digest.py`、非--test)→自分チャット投稿・アーカイブ・state更新まで成功(3トピック、[AI関連Teams_週次ダイジェスト_20260914.md](../Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/Project_AI業務活用PJ/weekly_ai_digest/AI関連Teams_週次ダイジェスト_20260914.md))。

**個人Macバックアップについて確認した結論**: ユーザーの「バックアップさせて」という依頼は、2026-08-24/25で既に構築済みの仕組み(`com.nakamura.aiteamsdigest.backup`、火曜8:00、shared state fileでの二重投稿防止)がそのまま満たしている。**新規構築の必要はなかった** — 今回の実体は「バックアップ自体は動く設計だが、失敗に気づく手段(Webhook)が壊れていたので次の障害検知が遅れる状態だった」というバグ。今後「動いているか確認して」と聞かれたら、(1) state fileの`last_digest_run`が直近の月曜以降か、(2) Webhook通知が実際に「ワークフロー」チャットに届いているか、の2点を確認する。

**How to apply**: 今後このスクリプトや類似の自動化スクリプトに会社Mac上でHTTPS通信(Webhook, API呼び出し等)を追加する際は、`urllib.request`ではなく最初から`curl`サブプロセス経由にすること(この既知の証明書問題を毎回踏まないため)。[[feedback_bake_error_notifications_into_automation]]も参照——通知機構自体が壊れていないかは実際に一度発火させて届くことを確認するまで信頼しない。

## 2026-10-05: TeamsのURLドメイン変更で投稿失敗 → 修正
TeamsのURLが`teams.cloud.microsoft`に移行し、`post_html_to_self_chat()`の`"teams.microsoft.com" in pg.url`判定が既存タブにマッチしなくなっていた(新規タブを開いて左レール未描画のまま「自分チャットが見つからない」で失敗)。両ドメイン許容+左レールの`wait_for_selector`を追加して修正済み。**手動実行時の注意**: Web収集がタイムアウトする時は`http_proxy/https_proxy=http://proxy1.dentsu.co.jp:8080`を付けるが、その際は必ず`no_proxy=localhost,127.0.0.1`も付ける(付けないとCDP接続 localhost:9226 がプロキシに流れて「共有ボットブラウザ起動失敗」になる)。アーカイブのファイル名日付はUTC基準(月曜朝JST実行→前日の日付)。

## 2026-10-19: 10/18号が下書きのまま未送信 → JSクリック方式に修正
- 症状: 自分チャット入力欄に本文が貼られたままEnterが効かず未送信。検証中に別チャット(榎本さん)へ遷移し失敗。榎本さんチャットへの誤送信は無し(DOMで確認)。
- 原因: 共有ブラウザのウィンドウを最小化/画面外に置くため、Playwrightの座標クリック・Enterが別要素に当たる。
- 修正: 左レールのクリックと送信を `element.click()`(JS、送信ボタン `data-tid="newMessageCommands-send"`)に変更。入力欄はfocus()。手動で送信し、state=2026-10-18T23:29Z、アーカイブはTeams本文から `..._20261019.md` に保存。
- 送信先は引き続き「自分のみ」(10/19ユーザー回答)。榎本さんへの自動配信は入れない。
- teams_messages.jsonl の10/16夕〜10/19朝の空白は会社Macを夜間・土日に起動しないため(正常)。月曜朝の起動後に更新再開を確認(10/19 09:15)。更新が止まって見えても、まず週末・夜間かどうかを確認する。

## 2026-10-26: 「ナレッジ・ノウハウ共有」チャンネル2件を監視対象に追加
ユーザー依頼。AIマスターコミュニティ(groupId 384afd75…)と dj_ChatGPT Enterpriseユーザ_情報共有(groupId fde1ae13…)に同名チャンネル「ナレッジ・ノウハウ共有」があり、`scripts/ai_watch_channels.txt`に1行で追加(同名なので両方まとめて拾う)。`channel_ids.json`は同名衝突で誤リンクになるため未登録(リンク省略)。**teams_daemonは左レールのみ巡回するため、両チャンネルのお気に入り登録が必要**(登録前は`teams_messages.jsonl`に0件)。
**訂正(同日)**: 上記「お気に入り登録が必要」は誤り。ユーザーは両チャンネルを左レールの独自セクション「GBC AI活性PJ」に入れていた。CDPでレールを確認し、同名2件が存在(daemonの対象になる)。レールのセクションはお気に入りに限らず、どのセクションでも収集対象。
