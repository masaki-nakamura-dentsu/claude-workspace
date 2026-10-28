# Agency OS Global Department Index 追加

## 2026-09-15T16:50Z
Status: done
What: 中村さんの依頼で、Agency OSに「グローバル対応部署」情報を追加。SharePoint「GlobalTeam」
ページ(https://esq365.sharepoint.com/sites/globalonedentsu/SitePages/GlobalTeam.aspx、
Global Q編集部運営、8カテゴリー・31部署のリンク一覧)と、その元データであるMicrosoft Forms
登録内容Excel(「グローバル関連組織紹介ページ 内容登録」、47件の登録・更新、~37組織)を共有
ブラウザ(port 9226)経由で取得。SharePoint共有リンクを`/_layouts/15/download.aspx?UniqueId=<GUID>`
形式に変換することでOffice Onlineを経由せず直接バイナリダウンロードできる技法を発見・使用。

新規`generate_global_dept_pack.py`(GBC-Knowledge直下)を実装: 組織名で登録行をマージし、
「変更なし」という値は前回登録値を保持(推測でなくメールアドレスで直前の自組織名を機械的に
解決)。出力`output/agency_os_pack/experts/global_department_index.md`(Part1=SharePoint
現行掲載、Part2=Excel登録のみで現行一覧に無い組織、100KB)。

SKILL.md(ChatGPT)/SKILL_Dify.md(Dify)両方に並行反映(bucket一覧・Withholding・使い方説明・
新規Requirement I・月次更新セクション、計6箇所ずつ)、SKILL_Dify_for_paste.mdはSKILL_Dify.mdから
プログラム的に再生成(手編集によるドリフト防止)。README.mdにも新bucketの説明・再取得手順を追加。
changelog.mdに詳細記録済み。

Next: 中村さんが実際のAgency OS拠点(ChatGPT Skill editor / Difyの「GBC Agency OS」アプリ)へ
`global_department_index.md`と更新済みSKILL.md/SKILL_Dify_for_paste.mdをアップロード・反映する
必要がある(ローカルファイル更新のみ完了、実プラットフォームへの反映は未実施)。

## 2026-09-15T17:05Z
Status: done
What: 中村さんから「もうなくなってしまった組織もあるので、それは案内しないで下さい」との
指摘を受け訂正。当初Part 2(現行SharePoint一覧に無い組織)は「留保付きで案内」する設計
だったが、廃止済みか単なる表記ズレかを機械的に見分けられないため、ヘッジでは不十分と判断し
「Part 2は案内・推奨に一切使わない(履歴保存のみ)」へ全面変更。SKILL.md/SKILL_Dify.md/
SKILL_Dify_for_paste.md(Requirement I見出し・Withholdingルール・使い方説明・bucket説明の
計6箇所ずつ)、generate_global_dept_pack.py(Part2見出し・使い方説明)、
global_department_index.md本体(再生成済み)、README.mdを全て修正。教訓は
[[feedback_dont_recommend_defunct_orgs]]として新規保存(ヘッジ文言では防げない失敗モードの
場合は除外一択、という一般則)。changelog.mdにも訂正記録追加済み。
Next: なし。中村さんが実プラットフォームへ反映する際は、修正版ファイルを使うこと。

## 2026-09-15T17:20Z
Status: done
What: 中村さんがDify版を実運用反映後、「ユニ・チャームの海外展開について相談したい」で
テストしたが組織名が一切出てこないとの報告。調査の結果、`global_department_index.md`を
COMMON KNOWLEDGE TEST MODEのバケット一覧とRequirement Iには追加していたが、**通常運用時に
実際に使われるSection 2「Mandatory internal search pattern」の検索チェックリスト**への
追加が漏れていたと判明(Requirement Iは「案件がグローバル関連と認識された後」にしか
発火しないため、広い/初期段階のブリーフだとそもそも検索されない設計になっていた)。
SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.mdを修正し、「広い/初期段階のブリーフでも
チェックする」旨を明記。教訓は[[feedback_agency_os_skillmd_multi_deployment_sync]]に
追記(新バケット追加時は複数箇所の列挙リストを全てgrepで確認する)。
Next: 中村さんにSKILL_Dify_for_paste.mdの再貼り付け(Dify)とSKILL.mdの再反映(ChatGPT)を
依頼し、より特定的なテスト質問(法務/PR/市場調査等、具体的な機能を指定するもの)での
再検証を提案。

## 2026-09-15T17:35Z
Status: done
What: 中村さんが両プラットフォームで再テスト。Dify版は正しくGlobal Department等を
返したが、ChatGPT Skill版は同じ質問(ユニ・チャームの海外向け契約交渉)で検索を一切せず
ヒアリング質問のみ返す不具合を報告。調査の結果、2026-09-11・2026-09-15午前に既出の
「ChatGPT Instantモデルは内部検索ツールを確実に呼ばない」既知バグの再発と判定
(SKILL.md自体は正しい)。中村さんがChatGPT 5.5のreasoning effortを「高」(5段階中3)に
切り替えたところ正しく動作することを確認。教訓を
[[feedback_agency_os_chatgpt_requires_thinking_model]]に保存・精緻化
(Instant/Thinkingの二択ではなく5段階effortセレクタと判明、「高」で動作確認済み)。
Next: なし。本タスク一式(Global Department Index追加・Part2除外修正・検索チェックリスト
漏れ修正・ChatGPT effort設定バグ診断)完了。PoC参加者へのeffort設定案内の恒久化は
まだ未実施(ユーザーに提案済み、返答待ち)。

## 2026-09-15T17:45Z
Status: done
What: 中村さんが下から2番目のeffortでも正しく検索できることを確認し、「一番下でも
拾ってくることがあると思われる」とコメント。特定のeffort段階を閾値として断定するのは
不正確と判断し、[[feedback_agency_os_chatgpt_requires_thinking_model]]と
[[gbc_intelligence_engine_project]]の記述を「◯段階で動作確認」から「低いほどリスク高・
高いほどリスク低(保証ではない)」という確率的な表現に修正。中村さんがセッションを
終了。
Next: なし。本タスク一式は完了。次回このプロジェクトに触るときは、(1)PoC参加者への
effort設定案内(恒久文書化)の要否確認、(2)実プラットフォーム側でのglobal_department_index.md
反映状況の確認、から。
