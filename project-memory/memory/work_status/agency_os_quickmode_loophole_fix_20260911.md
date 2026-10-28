# Agency OS(ChatGPT Skill)QUICKモードの社内ナレッジ/電通フォーマット抜け穴修正

## 2026-09-11T00:00:00+09:00
Status: done
What: ユーザーから「Agency OSが社内ナレッジを見ないことがある(理由:アイディア出しだから)、アウトプットが電通フォーマットでない場合がある」とのフィードバック(ChatGPT共有リンク4件、いずれも本セッションから403/アクセス不可)。`GPT作業/SKILL.md`を精読し原因特定: (1)「Mandatory internal search pattern」節がSTANDARD/FULL AGENCYのみを対象にしQUICKモードを除外していた、(2)「Client deliverable requirements(A-F)」も同様にQUICKモード除外、(3)チャット回答の構成を電通フォーマット(拡散収束/1-3-1/fact+解釈)にする規定がSKILL.mdに存在しなかった。編集前を`SKILL_V4.md`として保存後、SKILL.md本体を修正: 全モードで内部検索を必須化(QUICKは軽量版)、deliverable要件をQUICKにも拡大適用、新規ルールG(電通フォーマット強制)を追加。418行→472行。
Next: ユーザーが`GPT作業/SKILL.md`最新版をChatGPT Skillエディタに貼り付けて保存し、QUICKモードでの再テストを実施する必要あり。

## 2026-09-11T01:00:00+09:00
Status: done
What: ユーザーから追加依頼「DIFYの方も修正して」「ChatGPTでアクセス権がないと言われたチャットがあった、他の人は使えるのか確認して」「Difyでも駐在員の名前が出なかったケースがあった」。ChatGPT bot browser(port 9224、社内ワークスペース済みログイン)を起動し、共有リンク4件を実際に開いて本文を読了(社外からは403だが社内ログイン済みセッションからは閲覧可能と判明)。分析結果: 4件中1件のみ内部ナレッジ引用に成功しており、成功例は「Thinkingモデル」、失敗3例は全て「5.5 Instant」モデルで生成されていた。失敗パターンは2種類: (a)「アイディア出し段階なので内部検索していません」と明言(ユーザー報告と一致)、(b)「このチャット環境ではKnowledge Pack本体にアクセスできていません」と明言(ただし直前の成功例とほぼ同一の依頼文だったため、本物の権限差ではなくInstantモデルがツール呼び出しを試みず先回りで「使えない」と判断した可能性が高いと判定)。SKILL.mdにさらに2点追記(内部検索必須化をユーザー依頼文の文言に依存させない、「アクセスできない」と言う前に必ず実際に検索を試みることを明記)。472行→484行。

続けてDify版「GBC Agency OS」(console.dj-dify.dentsu.jp)を共有ブラウザ(port 9226、ログイン済み)経由でライブ調査。LLMノードのSYSTEM promptは旧版のまま(ChatGPT側同様の更新が必要、今回は貼り付け作業自体はリスク回避のため未実施)。作業中、SYSTEM promptエディタでja-JP環境由来と見られる誤字混入事故が1回発生(Cmd+A操作時)したが即座にCmd+Zで復旧・文字数一致を確認、バージョン履歴で直近の公開版(17:11)が事故より前であることも確認し、本番への影響なしと確認済み。「駐在員の名前が出なかった」の根本原因を特定: ナレッジベース内`overseas_staff_index.md`がインデックス作成エラー(Bedrock埋め込みAPIの1テキスト最大2048文字制限を、このデータセットのチャンク長設定4000文字が生む一部チャンク(過去の駐在経験者セクション、3986文字)が超過、ドキュメント全体が0/64チャンクとも一度も検索されていない状態)。再試行2回実施も同一エラーで失敗(既存ドキュメントのチャンク長再設定機能がないため、削除→チャンク長1024文字での再アップロードが必要と判明、他18ファイルには影響なし)。削除は確認を要するため未実施。調査全体の詳細記録を`GBC-Knowledge/agency_os_and_dify_investigation_20260911.md`に新規作成。
Next: ユーザーに(1)SKILL.md最新版のChatGPT/Dify両方への反映、(2)Difyのoverseas_staff_index.md削除+チャンク長1024での再アップロード、(3)PoC参加者へのThinkingモデル利用案内、の3点を確認・依頼する。

## 2026-09-11T02:00:00+09:00
Status: in progress
What: AskUserQuestionでDify側2作業の実施方針を確認。ユーザー回答: 「今日はもう仕事終了、来週行う。両方とも(SYSTEM prompt差し替え・overseas_staff_index.md削除+チャンク長1024再アップロード)Claude(私)が来週実施する予定」。ChatGPT側のSKILL.md反映についてはユーザー回答に含まれず(Dify側2問のみ質問した)ため、要否未確認のまま持ち越し。今日のセッションはここで終了。
Next: 【来週の再開時にまず実施すること】(1) Difyの「GBC Agency OS」チャットフロー(console.dj-dify.dentsu.jp/app/047d1529-f9fb-4211-a5a9-dc45aaee90a1)のLLMノードSYSTEM promptを、`GPT作業/SKILL.md`最新版(484行)に差し替える。前回はクリップボード経由の慎重な方法を試す前に時間切れとなった——直接クリックでの選択操作はja-JP環境でIME誤挿入を起こすリスクが実証済みなので、`context.evaluate(() => navigator.clipboard.writeText(...))`でクリップボードに全文をセットしてから、テキスト外の余白をクリックしてフォーカスし、Cmd+Aで選択→Cmd+Vで貼り付け、という手順を使うこと(生のキー入力でのCmd+A単体使用は避ける)。貼り付け後は文字数と冒頭/末尾を目視確認し、`{{#context#}}`相当の変数チップ表記が保持されているか確認してから「公開する」を押す(ユーザー確認は不要、来週は私の判断で実施してよいと明言されている)。(2) `datasets/cff84aa6-5a33-4678-a794-0259ee2c002a`内の`overseas_staff_index.md`(ドキュメントID `6b75ff0c-0f2e-4341-a74b-30465afbf7ad`)を削除し、`GBC-Knowledge/output/agency_os_pack/experts/overseas_staff_index.md`をチャンク長1024文字(セグメンテーション設定で明示指定)で再アップロード、インデックスが「利用可能」になることを確認する。(3) ChatGPT側SKILL.mdの反映要否はユーザーに確認できていないので、来週最初に一言確認する。詳細な原因分析は`GBC-Knowledge/agency_os_and_dify_investigation_20260911.md`参照。
