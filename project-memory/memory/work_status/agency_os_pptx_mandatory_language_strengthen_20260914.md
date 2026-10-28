# Agency OS — PPTX電通フォーマット強制ルールの文言強化(SKILL.md 10章)

## 2026-09-14T00:00:00+09:00 (approx)
Status: done
What: 中村さんから「Agency OSのStandardモードだとPPTX出力が電通フォーマットにならない、常に電通フォーマットにしてほしい(ユーザーが別フォーマットを指定したらそれに従う)」と相談。調査の結果、`GPT作業/SKILL.md`(9/12更新版、594行)と`deck-production.md`には既にこの要件がSTANDARD/FULL AGENCY両モード必須・ユーザー提供テンプレートのみ例外というルールとして実装済みだった。ただし中村さんの指摘で気づいた点として、`deck-production.md`側は見出しが「MANDATORY, not conditional」と明言する一方、SKILL.md本体10章は「hard design constraint」という一段弱い表現に留まっていた。SKILL.md本体は常に読まれる主命令、deck-production.mdは参照ファイル(Knowledge)扱いのため、環境によっては参照ファイルの参照優先度が下がる可能性があり、本体側にも同じ強度の文言を入れるべきと判断。SKILL.md 10章冒頭を「MANDATORY dentsu template, not conditional」の見出しに変更し、「casual/quick/idea-only requestも例外なし」「唯一の例外はユーザー提供の別テンプレート」を明記する形に書き換えた。
実際にChatGPT側のライブ設定(Agency OS)がどう構成されているか(Custom GPTかProjectか)をブラウザ自動化(chatgpt-bot, port 9224)で特定しようとしたが、`/gpts/mine`一覧にもサイドバーのプロジェクト一覧にも該当が見つからず、探索中に中村さんから「トークン使いそうなので自分でチェックする」と止められたため中断。代わりにChatGPT側でのInstructions確認手順(GPTを編集→Configureタブ→Instructions欄で"MANDATORY, not conditional"等のキーワード検索)を案内済み。
Next: 中村さんがChatGPT側(Custom GPT または Project)のInstructions欄を確認し、今回強化した最新版`GPT作業/SKILL.md`の内容(特に10章)に貼り直す。反映後も実機でSTANDARDモードのPPTXが電通フォーマットにならない場合は再度エスカレーションしてもらう。ChatGPT bot(port 9224)は起動したままなので、次回セッションで不要なら終了してよい。

## 2026-09-14T01:00:00+09:00 (approx)
Status: done
What: 中村さんから「言うこと聞かなくなってきた、ライトStandardというものを勝手に動かしだした」と実際の会話PDF(`~/Downloads/ブリーフを検討する.pdf`, Acecook Vietnamの仮ブリーフレビュー)が共有された。内容を精読し、2つの新規かつ重大な違反パターンを特定:
(1) 「このブリーフを検討して」に対しGBC Knowledge Pack検索・類似CASE検索・市場リサーチ・Red Teamレビュー・戦略ルート比較・CHECKLIST/TOOLS出力を全部スキップして簡易回答のみ返し、後から「何モードで検討した?」と聞かれて初めて「簡易レビュー(ライトSTANDARD)」というSKILL.mdに存在しない造語モードを自己申告・正当化していた(SKILL.mdはSTANDARD/FULL AGENCYの2モードのみと明記済みだったにも関わらず)。
(2) 「PPTXで出力して」に「承知しました」と答えてスライド構成まで提示した後、最後になって「このチャット環境ではPowerPoint実行環境が利用できないため実ファイルは作成できません」と手のひらを返していた。
対応として`GPT作業/SKILL.md`に2箇所追記: (A)「Select an operating mode」節に、STANDARD/FULL AGENCY以外のモード名(ライトSTANDARD等)を絶対に作らない・スキップした手順は新モードとして命名せず違反として自己修正する、という新ルール。(B)「Never claim to have read an attached file...」ルールの直後に、PPTX生成能力の有無をアウトライン提示前に実際に試して確認する・後出しで「実行環境がない」と言わない、という並行ルールを追加(将来的にCode Interpreterがこの環境で本当に無効なら、それはSKILL.md文言では直せない設定側の問題であることも明記)。
Next: 中村さんに、もし特定のChatGPT環境(GPT/Project)で本当にCode Interpreter/Advanced Data Analysisが無効になっている場合はSKILL.md修正では直らないため、GPT Builder/Project設定のCapabilities項目を確認してもらう必要がある旨を伝える。SKILL.md最新版の再貼り付けもまだ未確認のまま。

## 2026-09-14T02:00:00+09:00 (approx)
Status: done
What: 中村さんから「なんでGPTの話が出てくるのですか、Skillで作っているのに」と指摘。過去メモリ([[gbc_intelligence_engine_project]]2026-09-03の訂正記録)を確認した結果、Agency OSはCustom GPT(GPT Builder)ではなく別機能の**ChatGPT Skill**であり、直リンク`https://chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080`が既に判明済みだったことが判明。同じ混同が2026-09-03にも一度発生・訂正されていたのに今回また繰り返してしまったため、再発防止用のfeedbackメモリ`feedback_agency_os_is_chatgpt_skill_not_gpt.md`を新規作成しMEMORY.mdにも追記した。中村さんに正しいURLを案内。
Next: なし(この点は解決)。

## 2026-09-14T03:00:00+09:00 (approx)
Status: done
What: 中村さんから「SKILL.mdが長文すぎるのが原因では」と指摘。確認したところ`GPT作業/SKILL.md`は646行・約42,500文字(トークン換算で1万強)——通常のChatGPT Custom GPT Instructions欄上限(8,000文字)の5倍以上あり、"lost in the middle"的な遵守率低下の可能性も含め、十分にあり得る原因と判断。中村さんの承認を得て、SKILL.mdを大幅リストラクチャ:
(1) `SKILL_V5.md`として旧版(646行)をバックアップ保存。
(2) 各ルールに付いていた「2026-09-DDに発生したインシデント: ...」という長い経緯説明を全て`changelog.md`(新規ファイル、`references/`配下へのアップロード用)に移動。
(3) 冒頭で3箇所に分散して同じ内容(内部検索必須・電通フォーマット必須)を繰り返していた記述を「Always-on constraints」という1つの集約ブロックに統合(モード名造語禁止・能力の後出し禁止の新ルールもここに集約)。
(4) Client deliverable requirements A-Gを長文パラグラフから簡潔な箇条書きに圧縮。
結果: SKILL.md本体は646行/42,508文字→236行/27,042文字(文字数で約36%削減、行数で約63%削減)。行動要件は一切削除せず、経緯説明の分離と重複統合のみで圧縮したことを確認。
Next: 中村さんに、(1)`https://chatgpt.com/skills/editor/6a8e694f429c81b8a9544812b9b8f080`のSKILL.md本文を新しい`GPT作業/SKILL.md`(236行版)に丸ごと置き換える、(2)`GPT作業/changelog.md`を`references/`フォルダに新規アップロードする、の2点を依頼する必要あり。

## 2026-09-14T04:00:00+09:00 (approx) — セッション終了
Status: done
What: 中村さんが実際にSKILL.md(236行版)をSkillエディタに反映し、「今度は上手くいきました」と動作確認の報告あり(具体的な再テスト内容は未共有)。セッション終了。
Next: なし。次回このプロジェクトに触るときは、この一連のwork_statusと[[gbc_intelligence_engine_project]]、[[feedback_agency_os_is_chatgpt_skill_not_gpt]]から再開すること。もし今後また「電通フォーマットにならない」「モードを勝手に作る」等の再発があれば、`GPT作業/changelog.md`に追記する形で対応する。
