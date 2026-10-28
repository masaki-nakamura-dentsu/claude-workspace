# Agency OS PoC説明会資料 — Dify使い方ページ追加

## 2026-09-14T09:00:00+09:00 (approx)
Status: done
What: 中村さんから「本日Agency OSのPoC説明会、ChatGPT Enterpriseを使えない方にDifyの使い方のページも追加して」と依頼。最新版`Agency_OS_PoC募集資料_20260911.pptx`(15:25版、`中村修正_20260911`より後の統合版と判断)をベースに、新規スライド「使い方(Dify版)」(STEP1アクセス申請/STEP2使い方/STEP3現時点でのご留意点)を5枚目(ChatGPT版「使い方(実行例)」の直後)に追加し、`Agency_OS_PoC募集資料_20260914.pptx`として保存(命名規則通り、既存の`_20260911`を`_20260914`に置換)。qlmanage単一スライド抽出で3回レイアウト崩れを目視確認・修正(初回はSTEP4ボックスが枠外にはみ出し、テキスト量に応じてボックス高さを再計算して解消)。保存後`open`でファイルを開いた。

実際のWebApp URLは共有ブラウザ(d14461, port 9226, 既にDify Okta認証済み)経由でconsole.dj-dify.dentsu.jpの「GBC Agency OS」アプリ(id: 047d1529-f9fb-4211-a5a9-dc45aaee90a1)の「公開する」パネルを開き、「アプリを実行」リンクのhrefから直接取得(推測・過去ケース事例ファイル内の無関係なDify URLと混同しないよう注意した): **https://app.dj-dify.dentsu.jp/chat/UhIAspvW1bROU3Ar**

スライド記載内容は[[gbc_intelligence_engine_project]]の2026-09-11〜12の記録(QUICKモード廃止、Web検索非対応の割り切り、PPTX電通テンプレ非対応、SKILL_Dify.mdでの正直性ルール追加等)と整合させ、事実確認済みの制約のみを記載(内部のバグ調査詳細・ケースID・個人名などは[[feedback_gbc_ai_material_authoring_rules]]に従い非掲載)。フィードバック送信方法はDifyのWebApp側にChatGPTのような会話共有リンク機能があるか確認できなかった(Okta再ログインが必要でこのセッションでは完了せず)ため、断定を避けて「スクリーンショットやコピーしたテキストを同じフォームに貼付」という確実な代替案を記載。

Teams通知(`send_teams`, [[teams_webhook_powerautomate]])で完了報告済み。

Next: (1)中村さんご自身によるスライド最終確認(特にURL・アクセス権付与フローの整合性)、(2)Difyの会話共有機能の有無を今後確認できれば、フィードバック手順の記載をより具体的に更新可能。

## 2026-09-14T09:05:00+09:00 (approx) — セッション終了
Status: done
What: 中村さんが`Agency_OS_PoC募集資料_20260914.pptx`をPowerPoint上でご自身でも追加編集・保存済み(ファイルmtime 08:59、ロックファイル`~$...`存在を確認=現在PowerPointで開いたまま)。「私もアップデートしました。これでこのチャット閉じます」とのことでセッション終了。このファイルはユーザーが今まさに開いている状態のため、以降このセッションからは一切触れない([[feedback_dont_overwrite_open_pptx]]の通り)。
Next: なし。次回このプロジェクトに触るときは、このwork_statusと[[gbc_intelligence_engine_project]]の2026-09-14の記録から再開すること。
