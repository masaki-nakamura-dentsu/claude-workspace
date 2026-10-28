# Windows作業依頼キュー

使い方は同フォルダの `README.md` 参照。プロジェクトを問わずここに依頼を追記していきます。

---

## [2026-08-17T10:15] task-001 — GBC知見集約: メタデータ再抽出プロンプト強化後の再テスト
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:
プロンプト(prompts/backfill_metadata.txt)とスクリプト(backfill_metadata.py)を会社Mac側で
修正済みです(言語タグをLLM判断から除外し文字種による機械判定に変更、industry/tagsの判定
基準を厳格化)。以下を実行してください。

1. `output/backfill_manifest_worker0.txt` を一旦空にする(前回テスト分をやり直すため)
2. `C:\gbc_knowledge_venv\Scripts\python.exe backfill_metadata.py --limit 20` を実行
3. 更新された `output/json/` 内のカードを数件確認し、country/client/industry/tagsが
   evidenceの引用文の範囲内で妥当に埋まっているか(根拠不明な補完が無いか)を確認
4. このタスクのResult欄に、確認した件数・妥当だった件数・気になった点を書く

Result:
【実行前に発見した注意事項】
manifest初期化前に、このタスクとは無関係と思われるbackfill_metadata.pyの
プロセスが2つ(PID 38060: gbc_knowledge_venv版、PID 42080: 別のPython3.11環境版)
既に`--limit`指定なしで実行中だった(開始9:53、このタスク依頼10:15より前)。
Windows側ユーザーに確認したところ「心当たりなし・前回テストの残プロセスの可能性」
とのことで、安全に停止(Stop-Process)してからmanifestを初期化・再テストを実施した。
なお停止までの間に旧プロンプトでGBC-3A〜3E系のカードが多数更新されていた
(このtask-001の対象外だが、旧(修正前)プロンプトでの更新である点に留意)。

【テスト実行結果】
`backfill_manifest_worker0.txt`を空にし、`--limit 20`を実行。
結果: 対象20件 / 更新3件・変更なし17件・エラー0件。

【更新された3件の確認】
1. GBC-00211B861B76(日本アニメ市場の海外シェア): country="日本"は妥当
   (title/knowledgeに明記)。industry="アニメ業界"は要注意 — evidence引用文には
   「日本アニメ市場」とあるのみで「アニメ業界」という語そのものは無く、
   プロンプトが明示的に禁止している「アニメの話題だからエンタメ業界、のような
   連想」に近い可能性がある(市場→業界への読み替え)。ボーダーラインだが
   厳格に見ると連想寄り。
2. GBC-00224434EB7B(Digi-Keyのブランドキーワード競争): client="Digi-Key"は
   evidence引用文に明記されており妥当。★country="米国"は根拠不明 —
   evidence引用文にもknowledge本文にも国名の記載が無く、"Digi-Key"が
   米企業であるという一般知識からの補完と思われる。プロンプトが求める
   「evidence/knowledgeに明記されている場合のみ」の基準に反している疑いが強い。
3. GBC-00409985E46F(フィリピンの人口構成): country="フィリピン"はtitle/
   knowledge/evidenceすべてに明記されており妥当。industry/tagsは空欄のまま
   (安全側の判断、問題なし)。

【総評】
3件中2件(GBC-00409985E46Fと部分的にGBC-00224434EB7Bのclient)は妥当。
1件(GBC-00224434EB7Bのcountry="米国")は根拠不明な補完の疑いが強く、
プロンプト強化後もこのパターンの誤補完は完全には無くなっていない可能性がある。
もう1件(GBC-00211B861B76のindustry)もグレーゾーン。
本番の大規模実行(--limitなし)を再開する前に、「市場/企業名から国・業種を
一般知識で補完してしまう」ケースへの追加対策(例: 企業名だけを根拠にした
country補完を禁止する一文をプロンプトに追加する等)を検討することを推奨する。

対応者: Windows側Claude Code(2026-08-17 10:15-10:33実施)

---

## [2026-08-17T10:45] task-002 — プロンプト再強化(一般知識からの補完禁止)+ 再々テスト
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done(ただしフル実行は保留 — 下記参照)
Instruction:
task-001の丁寧な検証で見つかった2件、ありがとうございました。原因は判明済みです
(中村さんがWindows機のチャット窓を2つ同時に開いていて、それぞれが独立にフル実行を
開始していた。1つは停止済み。データ破損は無し、二重処理の無駄のみ)。

その上で、GBC-00224434EB7B(country="米国"を企業名からの一般知識で補完)は
プロンプト強化後も残っていた本物の問題なので、prompts/backfill_metadata.txtに
以下を追加しました(Dropbox同期済み、要pull):
- 企業名・ブランド名についての一般知識(あなたが元々知っている情報)からの
  country/industry補完を明示的に禁止する一文
- 「〜市場」→「〜業界」のような言い換えでの補完も明示的に禁止

お願いしたいこと:
1. 現在動いている(はず)のプロセスが1つだけであることを確認(タスクマネージャーで
   python.exeが1つだけか)。複数あれば中村さんに確認の上、1つに絞る
2. manifestはtask-001実行後の状態(20件処理済み)のままでよいので、追加で空にする
   必要はない。そのまま `--limit 20` を実行し、次の20件で再検証
3. 更新されたカードを確認し、GBC-00224434EB7Bのような「企業名からの一般知識による
   補完」や「市場→業界の言い換え」が無くなっているか確認
4. 問題が無ければ、その時点でようやく本番のフル実行(上限なし)に進んでOK。
   ただし**フル実行は同時に1プロセスだけ**にすること(今回の混乱の再発防止)
5. Result欄に確認結果を記入し、フル実行を開始したらTeams Webhookで一報してください

Result:
【手順1: プロセス確認】
実行前にpython.exeプロセスは0個(誰も動いていない状態)を確認。安全な状態だった。

【手順2: --limit 20 再実行】
manifestはtask-001実行後の状態のまま(20件処理済み)、追加で空にせず続きの20件を処理。
結果: 対象20件 / 更新10件・変更なし10件・エラー0件。

【手順3: 更新10件の確認 — 前回の指摘パターン(企業名からの一般知識補完)は再発なし】
GBC-008FF9363596(country="中国")、GBC-009669DEFAF7(client="Dentsu")、
GBC-009F5FA51050(country="中国")は、いずれも該当する国名・企業名の文字列が
evidence引用文に直接含まれており妥当。GBC-008DF4D1DFA8(industry="通信")も
evidenceに「Telkomは...通信サービスを提供」と明記されており妥当。
→ 前回指摘した「Digi-Keyは米国企業だから」のような企業名からの一般知識のみでの
country/industry補完は、この10件では再発していない。プロンプト追記は効いている。

★【新たに見つかった問題 — 前回より深刻な可能性】
GBC-007046471122(役員候補の推薦, dentsu integrated-report2023_all.pdf):
client="Dentsu", industry="Advertising" が付与されたが、このカードに渡された
情報(title/knowledge/why_it_matters/when_to_use/action/evidence.quote)の
どこにも"Dentsu"や"Advertising"に類する文字列は一切登場しない。evidence引用文は
"The Nominating Committee is responsible for nominating candidates for director
and executive positions..."という一般的なガバナンス文言のみ。
→ 企業名がevidence中に無いにもかかわらずclient/industryが埋まっており、
前回の「企業名は書かれているが国だけ一般知識で補完した」ケースより悪い、
「企業名すら書かれていないのに社名・業種そのものを生成してしまった」ケース。
LLM(qwen3:8b)が学習データ上でdentsuの統合報告書の文言を記憶していて
再現した可能性がある。今回追加したプロンプト文言(企業名からの補完禁止)は
「evidence中に企業名がある場合」を想定した文言のため、この
「企業名すら無いのに生成する」パターンは想定外でカバーできていない。

△【副次的に見つかった別種の問題 — industry欄の用途のズレ】
以下2件は評価が分かれるグレーゾーン:
- GBC-0073C0C18483(dentsuのサステナビリティ): industry="sustainability,
  digital citizenship" — evidence中の単語ではあるが、これは「dentsuという
  会社の業種」ではなく「このカードのテーマ」を書いてしまっている
  (dentsu自体の業種を書くなら「広告」等のはず)。
- GBC-007EA6DA7437(UN-Habitatとの提携): industry="Event Management" —
  evidence中の"event management platform"から取っているが、これも
  UN-Habitat(国連機関)の業種ではなく、プロジェクトの内容を書いてしまっている。
industry欄が「evidenceに書かれた語」という条件は満たしつつ、本来の定義
(取引先/対象の実際の業種)とズレた使われ方をしているケースが複数あり、
今回追加したプロンプト文言では防げていない。

【判断】
前回指摘した「企業名からの一般知識補完」パターンは解消されたが、代わりに
(1)evidence中に企業名すら無いのに社名/業種を生成する、より深刻な新パターンと
(2)industry欄の意味を取り違えて「テーマ」を書いてしまうパターン、の2つを
新たに発見した。指示の「問題が無ければ本番フル実行に進んでOK」の条件を
満たさないと判断し、**フル実行は開始せず保留**した。manifestは40件処理済みの
まま(task-001/002のテスト分)。Teams Webhookでの「フル実行開始」通知も、
開始していないため送っていない(この結果のサマリーのみ別途送信済み)。

対応者: Windows側Claude Code(2026-08-17 10:45-11:05実施)

---

## [2026-08-17T11:15] task-003 — プロンプトではなくコード側で機械的にブロックする方式に変更
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done(重要な問題2件を発見のため、フル実行は保留 — 下記参照)
Instruction:
非常に丁寧な検証、ありがとうございました。ご指摘の通り、8Bクラスのローカル
LLMにプロンプトの指示だけで完全に守らせるのは限界があると判断し、
プロンプトではなく**コード側で機械的に弾く方式**に変更しました
(backfill_metadata.py / prompts/backfill_metadata.txt をDropbox同期済み、要pull)。

変更点:
1. **根拠グラウンディング検証を追加**: country/clientはLLMの回答をそのまま
   信用せず、evidence引用文(NFKC正規化・大文字小文字無視)の中に実際に
   その文字列が含まれているかをPython側で照合し、含まれていなければ
   機械的に破棄するようにした(`_grounded_in_evidence()`)。
   GBC-007046471122のような「evidence中に企業名すら無いのに生成する」
   ケースは、LLMが何を返してこようと自動的に空欄に戻ります。
2. **industryを自由記述からGBCアレココの正式業種タグ21種類の選択式に変更**
   (`load_industry_pool()`)。「Event Management」「sustainability」のような
   カードのテーマ・活動内容を書いてしまう誤用は、そもそも候補一覧に
   存在しないため機械的に発生しなくなります。
3. Mac側でこの3パターン(Dentsu捏造/Event Management/正当なDigi-Keyケース)を
   モック応答で再現テストし、すべて意図通り(捏造は破棄、正当なものは許可)に
   動作することを確認済みです。

お願いしたいこと:
1. プロセスが1つだけであることを確認(前回と同様)
2. manifestは現状(40件処理済み)のままでよいので、続きの20件で
   `--limit 20` を再実行
3. 更新されたカードを確認。今回は「evidenceに根拠が無い値」自体がコード側で
   弾かれる設計なので、確認観点は主に(a) 正当な値まで誤って弾かれすぎていないか
   (安全側に倒しすぎて有用な情報も捨てていないか)、(b) industryの選択式化で
   不自然な選択(候補一覧にはあるが実態と合わない業種)が起きていないか、の2点
4. 問題なければ本番フル実行(上限なし、1プロセスのみ)へ進んでOK
5. Result欄に記入し、フル実行開始時はTeams Webhookで一報してください

Result:
コードの新方式(_grounded_in_evidence()によるcountry/client照合、industryの
選択式化)の実装内容も確認しました。設計意図は正しいですが、実際に動かしてみたところ
**2つの独立した重要な問題**を発見したため、フル実行は開始せず保留しています。

【手順1: プロセス確認】実行前にpython.exeプロセスは0個。安全な状態だった。

【手順2: --limit 20 実行】manifestは現状(40件処理済み)のまま続きの20件を処理。
結果: 対象20件 / 更新12件・変更なし8件・エラー0件。実行中、`_grounded_in_evidence()`
による[警告](根拠不明で破棄)ログは1件も出力されなかった。

★★【問題1: 新方式は"今日以降に新しく埋める値"にしか効かず、既存の汚染データは
一切修正されない — 実際に汚染例を複数発見】
今回「更新」された12件の中に、明らかにevidenceと矛盾する値が残っているものが
複数あった:
- GBC-00C4BB23918D: client="dentsu", industry="Advertising"
  → evidenceは配当payout ratioに関する英文のみ。"dentsu"の文字列は一切登場しない。
- GBC-00EDC950E45F: country="日本"
  → evidenceは"Ministry aims to achieve 100% electrification by 2030"という
  ミャンマーに関する英文(ファイル名: ...Myanmar-Final Report.pdf)。「日本」を
  裏付ける記述は皆無。
- GBC-00F52C857019: industry="食品・飲食"
  → evidenceは中国・台湾在住KOL/KOCのフォロワー数に関する内容。食品・飲食との
  関連は一切ない。

これらのIDを、task-001実行前に空にする直前の**元のmanifest(3000件)**と
照合したところ、いずれも元のmanifest内(43行目・51行目・54行目付近)に
既に存在していたことを確認した。つまりこれらは今日の新しいコードで
生成された値ではなく、**今朝発見・停止した暴走プロセス(旧prompt・チェック
機構なし)によって既に書き込まれていた値**である。
`backfill_one()`はcountry/client/industryが「既に値が入っている場合は
無条件でスキップ」する設計(空欄のみ埋める)なので、_grounded_in_evidence()の
チェックは一切通らず、今後どれだけ実行してもこれらの値は永久に検証・修正
されない。今回tags欄の差分か何かで再保存(save_card)がかかり、mtimeだけ
今日の日付に更新されたため、一見「今日生成されたデータ」に見えてしまっていた。
→ 元のmanifestが3000件あったことから、暴走プロセスは少なくとも数千件規模で
何らかの値を書き込んでいた可能性があり、その中に同様の汚染がどれだけ
含まれているか不明。

★★【問題2: industry欄には根拠照合チェックが無い(country/clientのみ)】
GBC-00F297353B29(UNIQLOの中国メディア対応に関するカード)で
industry="ファッション"が今回付与されたが、コードを確認したところ
`_grounded_in_evidence()`はcountry/clientのみに適用されており、industryは
`if value in valid_industries:`という候補一覧内チェックのみで、evidence文字列
との照合は行われていない(backfill_metadata.py L153-160)。このカードの
evidenceには「ファッション」という語は一切登場せず、"UNIQLOは有名なファッション
企業だから"という一般知識からの補完が今も可能な状態(前回task-002で指摘した
問題と同じ種類のもの)。industry選択式化は「候補外の値を防ぐ」効果はあるが、
「候補内であっても根拠のない選択を防ぐ」効果は無い。

【判断】
問題1は「今日の対策では直せない過去の汚染」、問題2は「今日の対策そのものの
穴」という、性質の異なる2つの課題。どちらも本番フル実行前に方針を決めて
おきたいため、フル実行は開始していません。Teams Webhookでの通知もこの
判断内容のみ送信済み(フル実行開始の通知はまだ)。manifestは60件処理済みの
まま(task-001/002/003のテスト分)。

対応者: Windows側Claude Code(2026-08-17 11:15-11:40実施)

---

## [2026-08-17T11:50] task-004 — 両問題を解消、本番フル実行をお願いします
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:
2件とも非常に的確な指摘で助かりました。両方Mac側で対応しました(Dropbox同期済み、要pull)。

【問題2の対応】industryにもcountry/clientと同じ根拠グラウンディングを追加しました。
LLMには"industry_evidence_phrase"(業種と判断した根拠となるevidence中の一言一句)も
一緒に返させ、その引用文自体がevidence.quoteに実在するかを機械的に照合します。
候補一覧内であっても根拠引用が無い/evidenceに見つからなければindustryごと破棄します
(UNIQLOのような一般知識のみでの補完はこれで防げます)。

【問題1の対応】`clean_ungrounded_fields.py`という新しいクリーンアップスクリプトを
作り、Mac側で**既に実行・適用済み**です(LLM不要、evidence.quoteとの文字列照合のみの
Pythonスクリプト)。
- 対象は「tagsが非空のカード」に限定(tagsはmain.pyの元々の抽出処理では絶対に
  生成されないため、非空=今回のbackfillが触った確実な証拠として使えます。
  最初evidence.quote全件と単純照合したところ7,407件という広すぎる範囲が
  ヒットしてしまい、今回のbackfill以前からmain.pyが正しく入れていた既存データ
  まで巻き込むところだったため、この絞り込みを入れました)
- 対象2,982件に対し実施。内訳: country破棄602件・client破棄302件・
  industry破棄1,155件(全件)・tags破棄2,982件(全件)
- backfill用manifestも削除済みなので、次回実行時はこれらのカードも含めて
  正しく再処理対象になります

現在の状態: country空欄12,693件・client空欄13,017件・industry空欄11,110件・
tags空欄14,897件(全件)。

お願いしたいこと:
1. プロセスが1つだけであることを確認
2. 最新コード(backfill_metadata.py / prompts/backfill_metadata.txt /
   clean_ungrounded_fields.py)をpull
3. 今回は事前の小規模テストは不要です。ここまで3段階のテストと2段階の実地検証を
   経ているので、そのまま本番フル実行(`--limit`なし)を開始してください。
   ただし**同時に1プロセスだけ**であることを重ねてお願いします
4. 開始したらTeams Webhookで一報してください。長時間かかる見込みなので、
   完了時も同様にWebhookでお願いします

Result:
【手順1: プロセス確認】実行前にpython.exeプロセスは0個。安全な状態だった。

【手順2: pull確認】clean_ungrounded_fields.py・backfill_metadata.py(industry_evidence_phrase
によるindustryの根拠照合を追加)ともに反映済みを確認。manifestは削除済み(バックアップのみ残存)、
対象14,897件を確認。

【フル実行開始時のトラブル】
起動直後にpython.exeプロセスが2つ動いているのを発見(1つは自分が起動したgbc_knowledge_venv版、
もう1つは別のPython3.11環境版で心当たりなし・今朝の残りの可能性)。中村さんに確認の上、
心当たりの無い方(PID 41744)を停止したところ、巻き添えで自分が起動した方のプロセスも
消えてしまい(原因不明、バックグラウンド実行の扱いに起因する可能性)、最初の起動試行は
実質何も処理せず終了していた(manifestへの書き込み無し)。`nohup ... &`で明示的にデタッチする
形で再起動し、今度はプロセスが継続して稼働し、manifestが実際に増加していくことを確認できた。

【現在の状態】
`nohup`で起動したプロセス(gbc_knowledge_venv版、1つのみ)が稼働中。数十秒で数十件のペースで
manifestが増加しており、実際に処理が進んでいることを確認済み。14,897件全体では数時間規模の
見込み。1プロセスのみであることを維持しています。完了時にResult欄を更新し、Teams Webhookで
一報します。

【追記・訂正 13:20頃】
再起動後にまた「python.exeが2つ動いている」状態を見つけたが、今回はParentProcessIdを
きちんと辿ったところ、2つ目(素のPython311)の親が1つ目(venvのpython.exe、自分が起動した
本体)そのものだった。つまりvenvのpython.exeは常に子プロセスとして素のPythonを起動する
構成らしく、**「python.exeが2つ見える」こと自体はこのプロジェクトでは正常であり、
重複実行の証拠にはならない**ことが判明した。この事実を踏まえると、task-001で報告した
「今朝2つの独立したプロセスが暴走していた」という見立て自体、実は1プロセスだった
可能性がある(その後Mac側からいただいた「2つのチャット窓が同時に依頼していた」という
説明が正しかったかどうかも再検証が必要かもしれません)。manifestが3000件まで育っていた
ことや、古いプロンプトによる汚染データが実在したこと自体は事実として変わりません。
Windows側メモリ(gbc_worker_setup.md)にこの訂正を記録済みです。

現在はこの「2プロセス(親子)」構成のまま正常にフル実行が進行中です(1論理プロセスとして
扱っています)。

【完了報告 16:31】
13:15頃開始、16:31頃終了。所要時間約3時間15分。
結果: 対象14,772件(事前テスト分と合わせ全14,897件中) / 更新8,815件・変更なし5,954件・エラー3件。

内訳詳細:
- 根拠グラウンディングによる[警告](根拠不明で破棄)ログ: 323件。country/client/industryの
  いずれかで、LLMが提案した値がevidenceに実在しないと機械的に判定され、自動的に空欄へ
  戻された。新しい安全機構が本番規模でも継続して機能していたことを示す実測値。
- 処理エラー3件はすべて`'cp932' codec can't encode character...`という、Windows上で
  ログ出力時に特定のUnicode文字(アクセント付きラテン文字等)がcp932(Windowsのデフォルト
  文字コード)にエンコードできず[警告]メッセージの出力自体がクラッシュしたもの
  (GBC-01710F8071B4 / GBC-20464B529565 / GBC-34E3CD)。データ破損では無く、単に
  この3件がmanifestに未記録のまま残っているだけなので、次回backfill_metadata.py実行時に
  自動的に再処理対象になる。
- LLM出力がJSONとして解析できず3回リトライ後も失敗した件数: 38件。これらは
  例外にはならず「変更なし」に計上され、manifestには処理済みとして記録されるため、
  今後自動で再処理されることはない(該当カードのcountry/client/industry/tagsの一部が
  空欄のまま残っている可能性がある)。

【完了後のサンプル確認】
GBC-2*.json帯からランダムに3件確認。2件は空欄のまま(安全側の判断、問題なし)、
1件(GBC-2C2915A309FB、EUのおむつ市場)はcountry="EU"(evidenceに明記)、
industry="家庭用品"(evidence中の「おむつ市場」から業種候補一覧内の適切な項目へ
根拠を持って分類)と、いずれも妥当な結果だった。

manifestは14,894/14,897件(エラー3件分を除く)。フル実行はこれで完了です。
Status: done

対応者: Windows側Claude Code(2026-08-17 11:50-16:31実施)

---

## [2026-08-17T16:45] task-005 — 完了報告への対応(情報共有のみ、対応不要)
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:
本番フル実行お疲れさまでした。全体として非常に良い結果でした(tags 0%→58.8%、
根拠グラウンディングが323件を実際にブロックするなど安全機構も本番規模で機能確認済み)。

ご報告いただいた2件の残課題について、将来また実行する際のためにコードを直して
おきました(今すぐの対応は不要です):
1. cp932クラッシュ対策: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
   を追加。今後同種の文字でクラッシュしなくなります(該当3件は元々manifest未記録
   なので次回実行時に自動再処理されます)。
2. JSON解析失敗時にmanifestへ書き込んでしまう問題を修正: `backfill_one()`が
   LLM応答取得失敗時はNoneを返すようにし、main()側でその場合はmanifestに
   書かず次回再試行させるようにしました。今回発生した38件は残念ながら
   遡って特定できないため未修正のまま残りますが(小規模な既知の残課題として
   許容)、今後同じ失敗が起きても自動的に再試行されるようになります。

Result:
(対応不要のため記入不要)

---

## [2026-08-26T17:40] task-006 — Knowledge Card新Pipeline Regression Test(300件)の続き
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:

### 背景(短く)
中村さんの指摘で、既存のKnowledge Card(`output/knowledge_index.db`)に
「元資料に無い解釈・一般化・推奨行動の混入」「数値/単位の抽出誤り」の問題が
あると判明(`knowledge_quality_audit.md`参照)。対策として、生成をStage A
(SOURCE FACTのみ抽出)とStage B(INTERPRETATIONのみ生成、ACTIONは生成しない)に
分離した新Pipelineを作り、監査と同じ300件サンプル(`audit_sample.json`)で
旧Pipelineと比較するRegression Testを実施中だった。**FULL DB(14,897件)の
再生成はまだ行っていない/行ってはいけない**(中村さんがこのRegression Testの
結果を見てから判断する)。既存DB・既存Agency OS Pack(`output/agency_os_pack*/`)は
一切変更しないこと。

会社Mac(d14461)で300件中35件処理したところで、中村さんが会社Macを
シャットダウンする必要が生じ、この続きをWindows側に引き継ぐことになった。
バックグラウンドプロセスは会社Mac側で安全に停止済み(35件のjsonlは正常、
データ破損なし)。

### 1. 前提条件の確認(まずこれをやってから本体作業へ)
1. **Ollama+qwen3:8bが使えるか確認**: `ollama list` でqwen3:8bが出るか確認。
   出なければ `ollama pull qwen3:8b`(以前の2台並行処理[main.py本番実行]で
   既にWindows側にOllamaが入っている可能性が高い、[[gbc_intelligence_engine_project]]
   の2026-08-16〜17の記録参照)。API疎通は `curl http://127.0.0.1:11434/api/tags`
   (別ホスト/ポートで動かしている場合は後述の環境変数で調整可能)。
2. **元資料(GBC_アレココ - 添付ファイル、Knowledge/Toolフォルダ、計804ファイル)への
   アクセス**: 以前の2台並行処理(main.py本番実行時)でWindows側が担当した際に
   使っていたローカルのコピー/マウント先(当時の`GBC_INPUT_DIR`環境変数の実体)が
   まだ残っているはずなので、そのパスを確認してください。無ければ、この作業は
   元資料が無いと実行できないため、中村さんに「外付けSSD(Extreme SSD)が
   Windows側に無いと続きができない」と伝えてください(Result欄に明記)。
3. **Pythonパッケージ**: `C:\gbc_knowledge_venv\Scripts\python.exe` (既存venv、
   以前のbackfill作業で使用)に `pymupdf` `python-docx` `python-pptx` `openpyxl`
   `requests` が入っているか確認(`pip list`)。不足があれば同venvへ追加インストール。

### 2. 本体作業: 残り265件の処理を再開
このプロジェクトフォルダ直下の `regression_pipeline_v2.py` は中断・再開に対応済み
(`--out`ファイル内の既存IDをスキップするので、同じコマンドを再実行すれば
36件目から自動的に再開される)。マシン固有パスは環境変数で渡す設計にしてある
(Windows用にコード変更は不要):

```powershell
$env:GBC_SSD_ROOT = "<手順1-2で確認した元資料フォルダの実際のパス>"
# Ollamaが既定(http://127.0.0.1:11434)以外なら以下も設定
# $env:GBC_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
# $env:GBC_OLLAMA_MODEL = "qwen3:8b"

cd "<このプロジェクトフォルダ>"
C:\gbc_knowledge_venv\Scripts\python.exe regression_pipeline_v2.py --out output_v2\regression_v2_results.jsonl
```

進捗はコンソールに `[N/300] ...` の形式で1件ずつ出力される(1件あたり30〜40秒
程度、残り265件で概算2.5〜3時間)。完了すると `output_v2/regression_v2_results.jsonl`
が300行になる。

### 3. 300件完了後: 比較・レポート作成
同フォルダの以下2つのスクリプトを順に実行(いずれも既に実装済み、変更不要):

```powershell
C:\gbc_knowledge_venv\Scripts\python.exe regression_compare.py
C:\gbc_knowledge_venv\Scripts\python.exe regression_review_build.py
```

- `regression_compare.py` → `output_v2/regression_comparison.json`
  (SOURCE FACT fidelity/Hallucination率/Interpretation混入率/Numeric error率/
  Evidence completeness/Hedge preservation率/Unsupported generalization率/
  Duplicate率/QUARANTINE率/VERIFIED・USABLE比率などの定量比較)
- `regression_review_build.py` → `regression_review.md`
  (severe事例8件+RECMA由来5件+リスクカテゴリ横断サンプルの横並び比較、
  合計40件程度)

### 4. 最終レポート作成
上記2つの出力(`regression_comparison.json`・`regression_review.md`)を踏まえて、
`regression_report.md`というファイルをプロジェクト直下に新規作成し、以下を
まとめてください:
1. 旧Pipeline vs 新Pipelineの定量比較(上記summary部分の表)
2. severe事例(GBC-02F583/021520D99995/03576F5DA4AF/0EF7F6/11FF96397231/
   0007FB4A926B/55B3529BE939/54BB3959A6F7/RECMA由来カード)がそれぞれ
   どう改善されたか、`regression_review.md`から個別に言及
3. 新Pipelineでも残ったエラー・問題(あれば具体例付きで)
4. False Positive(新Pipelineが過剰に厳しく判定した例)/
   False Negative(新Pipelineでも見逃した問題)があれば具体例
5. Knowledgeとしての有用性が低下していないか(情報量が薄くなりすぎていないか等)
6. 新Schemaの実例10件(regression_review.mdから代表的なものを抜粋)
7. QUALITY SCORE分布(VERIFIED/USABLE/USE_WITH_CAUTION/QUARANTINEの件数・割合)
8. FULL DB(14,897件)への適用可否の判断(推奨)
9. 適用する場合の推定時間(300件の実測時間から比例計算)
10. 既存Agency OS Knowledge Pack(`output/agency_os_pack*/`)を差し替えるべきか

**重要**: FULL DB(14,897件)の再生成は、中村さんがこの`regression_report.md`を
確認して指示するまで絶対に開始しないでください。既存の`output/knowledge_index.db`・
`output/agency_os_pack*/`は一切変更しないでください(新しい出力は`output_v2/`配下と
プロジェクト直下の新規ファイルのみ)。

### 5. 完了後
- このタスクのStatusを`done`にし、Result欄に定量比較のサマリと
  `regression_report.md`のパスを書いてください
- プロジェクトの`memory/work_status/`(会社Mac側で使っていたファイル
  `gbc_intelligence_engine_regression_v2_20260826.md`があれば同じファイルに
  追記、無ければ新規作成)に作業ログを残してください([[work_status_protocol]]参照)
- Teams Webhookで完了報告してください(README.md記載の`Send-TeamsMessage`使用)

Result:
【手順1: 前提条件確認 — 2件ともブロッカーを発見、本体作業(残り265件)は未着手】

(1) 元資料(外付けSSD)へのアクセス: このWindows機のドライブを全て確認しましたが
(C:M.2_1, D:M.2_2, E:SSD_inside, F:HDD_inside, L/M/O/P:Photo_*, T:IO-Data_1TB)、
「GBC_アレココ」や「Extreme SSD」に該当するものは見つかりませんでした。
中村さんの想定通り「外付けSSD(Extreme SSD)がWindows側に無いと続きができない」
状態です。GBC_SSD_ROOT環境変数を設定する対象パス自体が存在しません。

(2) Ollama qwen3:8bモデル: `ollama list`で確認したところ、このWindows機に
入っているのは`qwen3.8:27b`(27.3B、3日前pull)のみで、スクリプトの既定モデル
`qwen3:8b`は入っていませんでした。会社Mac側で会社Macで既に処理済みの35件は
おそらくqwen3:8bで生成されているはずなので、Windows側で`GBC_OLLAMA_MODEL`を
`qwen3.8:27b`に変更して残り265件を処理すると、同じRegression Testの中で
モデルが混在してしまい、比較結果の一貫性が崩れる可能性があります(27Bは8Bより
高性能な別モデルで、単純な代替とはみなせません)。SSDが接続され次第、
qwen3:8bをこの機にpullしてから再開すべきか、qwen3.8:27bで統一して265件を
処理してよいか(その場合35件との比較可否)、ご判断をお願いします。

【現状】output_v2/regression_v2_results.jsonlは会社Mac側の35件のまま変更なし。
既存DB・Agency OS Packには一切触れていません。SSD接続とモデル方針が決まり次第、
再度「windows_inbox.mdを確認して」と声をかけていただければ本体作業(手順2以降)を
実行します。

対応者: Windows側Claude Code(2026-08-27実施、前提条件確認のみ)

【追記 2026-08-27】中村さんよりSSDパス(D:\GBC_アレココ - 添付ファイル)とモデル方針
(qwen3.8:27bで統一)の指示をいただき、残り265件の処理をバックグラウンドで開始しました。
GBC_SSD_ROOT="D:/GBC_アレココ - 添付ファイル", GBC_OLLAMA_MODEL="qwen3.8:27b"。
進捗はoutput_v2/run_windows.logに出力。qwen3:8bとqwen3.8:27bが混在する点は
中村さんの明示判断のもの。

【完了報告】残265件を約86分(19.5秒/件)で処理、エラー0件。300件全件完了。
regression_compare.py・regression_review_build.pyを実行し、
プロジェクト直下に`regression_report.md`を新規作成した(全10項目網羅)。

定量サマリ: generalization_suspect_rate(過剰一般化)が56.0%→0.7%へ劇的改善。
一方でavg_scoreは82.8→68.2、QUARANTINEは15件→75件へ悪化。ただしこの悪化は
主に「事実を再特定できなかったカード(has_fact=False、54件/18%)を機械的に
0点・隔離とする」設計変更が主因で、事実抽出に成功した246件だけで見ると
平均点は旧とほぼ同水準(約83点相当)に戻る。severe事例8件+RECMA由来5件は
13件中12件で明確な改善を確認(regression_review.md参照)。

新たに見つかった残課題: (1)SOURCE FACT中に元資料に無い数値計算(小数点15桁の
比率等)が混入する疑いのあるケースを発見(GBC-0102B8C9F333等、プロンプトの
「計算禁止」規則への違反)。backfill_metadata.pyで実装済みの根拠グラウンディング
と同様の機械チェックをStage Aにも追加すべき。(2)quote_not_located(元資料内で
該当箇所を再特定できない)が16.3%、(3)SOURCE FACTへのInterpretation混入疑いが
20.0%。

**判断: FULL DB(14,897件)への一括適用は現時点では推奨しません。**
上記(1)の数値グラウンディング対策を先に実装・再検証すべきと判断しました
(詳細はregression_report.md 8章)。参考: 同ペースでFULL DB全件を処理すると
約80.7時間(約3.4日、1プロセス)かかる試算です。

既存DB(output/knowledge_index.db)・既存Agency OS Pack(output/agency_os_pack*/)は
一切変更していません。詳細な数値・severe事例ごとの比較・推奨アクションは
`regression_report.md`をご確認ください。

対応者: Windows側Claude Code(2026-08-27実施)

---

## [2026-08-27T07:07] task-007 — regression_report.md 3-1「数値計算混入」対策の実装+再検証
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:
`regression_report.md` 3-1・8章で指摘された「Stage AのSOURCE_FACTに元資料に無い
数値計算(GBC-0102B8C9F333の小数点15桁の比率等)が混入する」問題への対策を実装し、
効果を再検証してください。個人Mac側で`regression_pipeline_v2.py`のstage_a()と
`backfill_metadata.py`の`_grounded_in_evidence()`を確認した上での提案です。

1. `regression_pipeline_v2.py`に数値グラウンディングチェックを追加する
   (`backfill_metadata.py`の`_grounded_in_evidence()`と同じ思想: LLM出力の中で
   コード側が機械的に検証できる部分は必ず検証する)。設計案:
   - `SOURCE_FACT`中の数値トークン(`[+-]?\d[\d,]*\.?\d*\s*%?`程度の正規表現)を
     全て抽出する
   - 各数値がStage Aに渡した`context["context_text"]`(元資料の抜粋全文、
     `source_evidence_quote`ではなくこちら — quote自体もLLM生成なので検証対象と
     しては不適切)の中に、カンマ・空白を正規化した上で実在するかを確認する
   - 実在しない数値が1つでもあれば`_numeric_suspect=True`とし、該当数値と
     理由(`not_in_context`)を記録する
   - 加えて、小数点以下4桁を超える数値は実在チェックの有無に関わらず
     `_numeric_suspect=True`(理由`long_decimal`)とする(GBC-0102B8C9F333のような
     LLM自前計算はほぼ確実にこのパターンのため、割り算・平均等の計算結果を
     機械的に検出する簡便なヒューリスティックとして)
   - この設計案はあくまで叩き台なので、実装時に文字化け・全角数字(NFKC正規化要)
     等の実データ特有の問題が出れば適宜調整して構いません
2. 実装後、`output_v2/regression_v2_results.jsonl`のうちNUMERIC_SUSPECTだった63件
   (`regression_compare.py`のNUMERIC_SUSPECT判定ロジック参照)を対象に、
   Stage Aだけ再実行して`_numeric_suspect`が正しく検出されるか確認する
   (300件全体の再実行は今回は不要、まず63件で効果を確認してください)
3. 効果が確認できたら、`regression_compare.py`の`score_new()`に
   `_numeric_suspect=True`のカードを強制QUARANTINE(または大幅減点)に
   組み込む変更を追加する(既存の`has_fact=False`強制QUARANTINEと同じ扱い)
4. 使用モデルは`qwen3.8:27b`で統一してください(中村さんが8/27に既に指示済みの
   方針を踏襲、個人Mac側にも同モデルが導入済みで一致しています)
5. このタスクのResult欄に、(a)63件中何件が新たにNUMERIC_SUSPECTとして検出されたか
   (b)long_decimal起因/not_in_context起因の内訳(c)誤検知(正当な数値なのに
   フラグが立った)と思われる例があれば具体的に、を記録してください

**重要**: 今回もFULL DB(14,897件)の再生成・既存`output/knowledge_index.db`・
既存`output/agency_os_pack*/`への変更は、中村さんが明示的に指示するまで
一切行わないでください(task-006と同じ制約を継続)。

Result:
「windows_inbox.mdを確認して」の声かけを受けて着手しました。

【実装】`regression_pipeline_v2.py`に`numeric_grounding_check()`を実装(提案設計案通り、
SOURCE_FACT中の数値をStage Aに渡した元資料の抜粋(context_text)と照合。小数点以下5桁以上は
`long_decimal`、それ以外で元資料中に実在しない2桁以上の数値(年号除く)は`not_in_context`)。
`stage_a()`の戻り値に`_numeric_suspect`/`_numeric_suspect_reasons`を追加し、
`regression_compare.py`の`score_new()`にも強制QUARANTINE条件として組み込み済み
(既存300件データには未適用、今後の再実行分から反映)。モデルはqwen3.8:27bで統一(指示通り)。

【検証(63件、LLM再呼出し無し)】既存のsource_factとlocate_context()で決定的に
再取得したcontext_textを照合(quote自体もLLM生成のため検証対象から除外、提案設計通り)。
(a) 63件中17件(27%)を検出。内訳: long_decimal起因1件(GBC-0102B8C9F333、3-1で
指摘した小数点15桁の計算混入の典型例を正しく検出)、not_in_context起因16件。
(b) 参考として旧heuristicで未検出だった他237件にも適用したところ検出0件(誤検知なし)。
(c) 誤検知の疑い: 検出17件中4件を手動精査したところ3件が誤検知パターンでした
— ①日本語「〜月」表記と元資料の英語月名表記のズレ(GBC-00CAA957627A)、②ファイル名・
ページ番号がSOURCE_FACT本文に混入しその数字がフラグされたケース(GBC-0129FAFA0EDD、
これは計算混入ではなく別種の「事実のみ抽出」逸脱)、③元資料のヨーロッパ式コンマ小数点
("9,8%")を桁区切りコンマと誤認識(GBC-01647E)。残り1件(GBC-040C75E406BD)は
1カード内に誤検知(万単位への正しい換算)と正検知(元資料に無いドル換算をLLMが
独自追加)が混在する興味深い例でした。

【判断】long_decimalシグナルは精査した範囲で誤検知なく高精度、not_in_contextは
27%検出中の一部に上記の誤検知パターンがあり精度に改善余地あり。ただし本チェックは
自動破棄ではなくQUARANTINE(隔離)止まりのため、誤検知があってもデータは失われず
安全側の設計です。詳細・改善案は`regression_report.md`11章に追記済み。

FULL DB(14,897件)の再生成・既存DB・既存Agency OS Packへの変更は今回も一切
行っていません。

対応者: Windows側Claude Code(2026-08-27実施)

---

## [2026-08-27T07:29] task-008 — 数値グラウンディングの精度改善(コンマ処理・ファイル名/ページ番号除外)+ 実データでの再検証
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:
task-007のResultで報告いただいた誤検知2パターン(コンマ小数点・ファイル名/ページ番号混入)
について、個人Mac側で`regression_pipeline_v2.py`を直接修正しました(Dropbox同期済み、
pull不要のはずですが念のため最新か確認してください)。変更点:

1. `numeric_grounding_check()`: context側の正規化形を2通り用意("1,234"のような桁区切り
   コンマ用と、"9,8%"のような欧州式小数点コンマ用)、いずれかに一致すればgroundedとする
2. `_strip_filename_and_page_refs()`を新設: 数値抽出前にファイル名(`*.pdf`等)・ページ参照
   ("99ページ目"等)をSOURCE_FACTから除去。正規表現だけでは拾いきれない場合
   (例:"FY25"のように拡張子と離れた場所にある数字)に備え、`context["source_file"]`の
   文字列そのものがSOURCE_FACT中に含まれていれば丸ごと除去する処理も追加
3. `stage_a()`から`numeric_grounding_check()`への呼び出しに`context.get("source_file")`を
   追加で渡すよう変更

**個人Mac側での検証(SSDが無いため、`output_v2/regression_v2_results.jsonl`の
既存source_evidence_quoteをcontext_textの近似として使った簡易テストのみ実施)**:
GBC-01647E(コンマ小数点)・GBC-0129FAFA0EDD(ファイル名/ページ番号)とも誤検知が
解消することを確認。GBC-0102B8C9F333・GBC-040C75E406BD(本物の問題を含むカード)は
引き続き正しく検出されることも確認(退行なし)。GBC-00CAA957627A(英語月名"Nov."と
日本語"11月"の表記ズレ)は今回の依頼範囲外のため未対応のまま残しています。

お願いしたいこと:
1. 最新の`regression_pipeline_v2.py`を確認(Dropbox同期済みのはず)
2. 実際の`context_text`(元資料から`locate_context()`で再取得したもの、簡易テストで
   使った近似値ではなく本番と同じもの)を使って、既存63件のNUMERIC_SUSPECT全件に
   新しい`numeric_grounding_check()`を再適用(LLM再呼出しは不要、決定的な後処理のみ)
3. 特にGBC-01647EとGBC-0129FAFA0EDDが実データでも誤検知として正しく解消しているか、
   個別に確認してください(近似データでの確認結果と実データでの結果が食い違う
   可能性があるため)
4. 63件以外(旧heuristicで未検出だった237件)にも適用し、新たな誤検知が
   発生していないか確認
5. 結果を`regression_report.md`11章に追記し、このタスクのResult欄にも
   (a)63件中の検出件数・内訳の変化(task-007時点の17件からどう変わったか)
   (b)GBC-01647E/GBC-0129FAFA0EDDの解消確認結果
   (c)新たな誤検知や見落としがあれば具体例、を記録してください

**重要**: FULL DB(14,897件)の再生成・既存DB・既存Agency OS Packへの変更は
今回も中村さんが明示的に指示するまで一切行わないでください。

Result:
「windows_inbox.mdを確認して」の声かけで着手しました。個人Mac側の修正
(コンマ2通り正規化・`_strip_filename_and_page_refs()`)は最新化済みを確認。

【実データ(SSD経由のlocate_context()、LLM再呼出しなし)での再検証】
(a) 63件中の検出数: 17件→**13件**に減少。
(b) GBC-01647E(コンマ小数点)・GBC-0129FAFA0EDD(ファイル名/ページ番号)は
実データでも誤検知が解消したことを確認(個人Macの近似データ検証と一致)。
GBC-0102B8C9F333(long_decimal)・GBC-040C75E406BD(not_in_context、ドル換算の
独自追加)は引き続き正しく検出、退行なし。
(c) 新たな誤検知: 旧heuristic未検出だった237件への適用で新規誤検知0件
(改善前と同じ)。GBC-00CAA957627A(日英月表記ズレ)は依頼範囲外のため
誤検知のまま残存(仕様通り)。残る13件中、今回個別精査していない8件については
task-007時点から検出結果に変化なし(コンマ/ファイル名パターンに該当しないため)。

詳細はregression_report.md 12章に追記済み。FULL DB・既存DB・既存Agency OS Packへの
変更は今回も一切行っていません。8章のFULL DB適用可否判断は変更なし(中村さんの
指示待ち)。

対応者: Windows側Claude Code(2026-08-27実施)

---

## [2026-08-27T08:14] task-009 — 未検証の残り数値グラウンディング疑い事例を人間レビュー(FULL DB適用前の品質確認)
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:
中村さんが「クオリティを優先したい」と明言し、FULL DB適用(約80時間)の前に、
残っている品質確認事項を先に潰す方針になりました。regression_report.md 12章を
読み返したところ、**レポート自体の集計に矛盾**を見つけました:
「それ以外の8件」と書きつつ実際に列挙されているIDは10個で、レポート内でも
「実際は10件」と注記されています。また「今回改めて個別精査したのは上記4件」と
ありますが列挙されているIDは0102B8C9F333/040C75E406BD/00CAA957627A/01647E/
0129FAFA0EDDの5件です。5+10=15 ≠ 13(63件中の検出数)なので、集計が合っていません。

まず数を正しく確定した上で、未検証分を実際の元資料と照合してレビューしてください。
個人Mac側にはSSDが無く元資料を参照できないため、この作業はWindows側にお願いします。

1. `output_v2/regression_v2_results.jsonl`の該当300件に対し、現行の
   `numeric_grounding_check()`(コンマ処理・ファイル名/ページ番号除外の改善込み)を
   再適用し、**現時点で`_numeric_suspect=True`となる正確なID一覧(13件のはず)**を
   出力する(重複無く、過不足なく)
2. その13件のうち、task-007/008で既にレビュー済みの5件
   (GBC-0102B8C9F333/GBC-040C75E406BD/GBC-00CAA957627A/GBC-01647E/GBC-0129FAFA0EDD)
   を除いた**残り(正しい件数を確定した上でその全件、8件でも10件でも省略せず全件)**
   について、task-007/008と同じ方法(該当箇所を元資料から実際に開いて確認)で
   1件ずつレビューしてください。各件について:
   a. 実際に元資料に無い数値計算・捏造なのか(真陽性)
   b. task-007/008で見つけた3パターン(日英月表記ズレ/ファイル名混入/コンマ小数点)
      とは別の、**新しい種類の誤検知パターン**なのか
   を判定し、bの場合は具体的にどう誤検知しているかを記述してください
3. 新しい誤検知パターンが見つかった場合、それを直すべきかどうかの推奨も記載してください
   (即座に修正する必要はありません、中村さんへの報告のための判断材料が目的です)
4. Result欄に、(a)正しいID一覧と件数の確定結果(レポートの集計ミスの訂正)、
   (b)残り全件のレビュー結果(真陽性/誤検知の内訳と、誤検知なら具体的な原因)、
   (c)新しい誤検知パターンが見つかったかどうかと対応の推奨、を記録してください

**重要**: FULL DB(14,897件)の再生成・既存DB・既存Agency OS Packへの変更は
今回も中村さんが明示的に指示するまで一切行わないでください。

参考: 個人Mac側では`migrate_v2_schema.py`(doc_cardsへのv2_*列追加+分類UPDATE)と
`search.py`/`webapp/app.py`/`gpt_integration/query_report.py`/
`generate_agency_os_pack.py`の改修を実装し、本番DBのコピー上で300件分の動作検証を
済ませています(本番ファイルは無変更)。このtask-009はFULL DB本実行の前段階の
品質確認という位置づけです。

Result:
「windows_inbox.mdを確認して」の声かけで着手しました。ご指摘の集計ミス、
申し訳ありませんでした — 正しく確定・訂正しました。

【(a) 正しいID一覧・件数】現行チェックで`_numeric_suspect=True`となるのは重複無く
**13件**(GBC-0102B8C9F333, 00CAA957627A, 040C75E406BD, 01701F, 02EFE5F7C8EE,
0817DA29782F, 0EB579DCE325, 2239C1090563, 233CCFFD9598, 31D311B8D096,
41467DB68567, 428BA658A2F0, 612DE5B5635A)。既レビュー3件(0102B8C9F333/
040C75E406BD/00CAA957627A)を除く**10件**が未レビューでした(旧レポートの
「4件」「8件/10件」という記載は誤りで、正しくは3件・10件でした)。

【(b) 残り10件のレビュー結果】**10件中10件すべてが誤検知(真陽性0件)でした。**
- 5件(半数): 英語"million/billion"→日本語「万/億」への**正しい**単位変換
  (例: "$184 billion"→"1840億ドル"、"3.5 million"→"350万回"、全て検算済みで
  数値的に正確)。task-007/008の3パターンとは別の**新しい誤検知パターンで、
  かつ発生頻度が最多**でした。
- 2件: 既知の「〜月」vs英語月名(GBC-00CAA957627Aと同一パターン、対応範囲外)。
  なおこの2件のうち1件(428BA658A2F0)は00CAA957627Aと同じ元資料の同じ文を
  参照しており、重複カードの疑いあり(3-4節のduplicate_rateと関連)。
- 1件: 範囲を表すハイフン("0-100点")が負の数値"-100"と誤認識される新パターン。
- 1件: 順位ラベルの位置的推論+短い数値トークンが無関係な数値中に部分文字列
  として偶然一致し検出結果が不安定になる新パターン(判定方式自体の弱点)。

【(c) 新しい誤検知パターン・対応推奨】(b)の通り3種類の新パターンを発見。
最重要は「million/billion↔万/億変換」で、13件中5件(38%)を占め、
既存の対応済み2パターンより高頻度です。**13件中、真の問題(真陽性)は
GBC-0102B8C9F333とGBC-040C75E406BDの2件のみで、的中率は約15%**という
ことが今回のレビューで判明しました。FULL DB適用前に、magnitude語変換への
対応を優先することを推奨します(具体案・詳細はregression_report.md 13章)。
即座の実装はしていません(判断材料としての報告に留めています、指示通り)。

FULL DB・既存DB・既存Agency OS Packへの変更は今回も一切行っていません。

対応者: Windows側Claude Code(2026-08-27実施)

---

## [2026-08-27T09:10] task-010 — 「自己PR/CSR定型文/テンプレート由来の空疏な文言」検出監査(300件)
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:

### 背景
task-009までは「数値グラウンディング(捏造数値の検出)」の話でしたが、これは別の
新しい品質軸です。中村さんから「わりと当たり前のことが知見として書いてあるものが
多い、除外する方法はないか」との指摘があり、会社Mac側で調査しました。

最初にLLM不要のヒューリスティック(country/client/industryが空欄+evidence_quoteに
数字なし)を試しましたが、精度が五分五分で不採用。次にLLM分類スクリプト
`audit_genericness.py`(GENERIC=誰でも知っている一般常識 vs SPECIFIC=固有名詞・数値あり)
を作り既存の300件層化サンプル(`audit_sample.json`)に適用しましたが、**中村さんに
実際に20件×2ラウンドで100点満点採点してもらったところ、GENERIC群平均80点・
SPECIFIC群平均85点とほぼ差が無く、この軸は実際の価値判断とは相関しないと判明**しました
(低スコア例ですら「実績を積んできた」30点、「都市部の消費者は新しい支払い方法を
好む」は逆に90点、等)。

採点結果を分析した結果、実際の判断軸は「一般常識かどうか」ではなく
**「誰について語っているか(自社の実績/体制についての自己PR・定型開示文 vs
外部の市場/消費者/事例についてのリサーチ知見)」**だと分かりました。低評価だったのは
「実績を積んできた」(自己PR)、「取締役会の実効性評価を外部機関を活用して実施」
(CSR定型開示文)、テンプレートファイル由来の中身の無い比喩、など。逆に「都市部の
消費者は新しい支払い方法を好む」や実際のペルソナ・生活者リサーチ例は、一見抽象的でも
高評価でした。

この教訓を反映した新スクリプト `audit_boilerplate.py`(BOILERPLATE=自己PR/CSR定型文/
テンプレート由来の空疏な文言 vs SUBSTANTIVE=外部の市場/事例についてのリサーチ知見)を
実装済みです(Dropbox同期済み、要pull)。会社Mac側でqwen3:8bを使い、人間採点済みの
28件(下記)で簡易検証したところ、BOILERPLATE判定の人間平均68.0点・SUBSTANTIVE判定
80.8点で、旧v1(80 vs 85)より分離が改善しました。ただし誤判定も残っています
(例: GBC-002E70037DEBの「NTT-dentsu×TGS VRで大阪万博スポンサー獲得」という
明確な具体事例をBOILERPLATEと誤判定、GBC-00224434EB7Bの「Digi-Keyブランドキーワード
競合入札」は固有名詞があるためSUBSTANTIVEと判定されたが人間は「通常の広告会社の
作業」として60点と評価、等)。

### お願いしたいこと
1. **前提確認**: `ollama list`でqwen3.8:27bが使えるか確認(task-007/008で既に
   導入済みのはず)。`audit_boilerplate.py`をpullし、最新か確認(冒頭のdocstringに
   このタスクの背景と判定基準の詳細を書いてあります)
2. **300件本実行**: 以下を実行してください。
   ```powershell
   $env:GBC_OLLAMA_MODEL = "qwen3.8:27b"
   C:\gbc_knowledge_venv\Scripts\python.exe audit_boilerplate.py
   ```
   `output_v2/boilerplate_audit_results.jsonl`に300行出力されます(resumable設計、
   途中で止めても再実行で続きから)。
3. **モデル比較検証(重要)**: 下記の人間採点済み28件のIDと得点(100点満点)を使い、
   qwen3.8:27bでの判定がqwen3:8bより人間評価との分離が改善するか確認してください。
   ```
   GBC-0001CCE23388:80, GBC-0007FB4A926B:90, GBC-0013DC2FF815:90, GBC-002C6F:90,
   GBC-007E6CEF374E:90, GBC-0086D00BF8BA:90, GBC-008F13CB1283:60, GBC-00DD6521897E:70,
   GBC-00EA44:70, GBC-00EBEB3F403F:70, GBC-000AA12338DE:90, GBC-00211B861B76:90,
   GBC-00224434EB7B:60, GBC-002E70037DEB:90, GBC-00409985E46F:90, GBC-004C1D7D8030:90,
   GBC-005BE6:90, GBC-0073C0C18483:80, GBC-F2D166EB2F3D:10, GBC-F2A4856B19F2:80,
   GBC-B1BD1E750FC9:70, GBC-A3227F60EA30:70, GBC-4FDB5AC93ACD:40, GBC-251AB1B0DE30:60,
   GBC-548C8962B7D3:50, GBC-3A8594ED61CA:90, GBC-42350C6BDB8E:30, GBC-D00CA0:90
   ```
   これらのIDはoutput/knowledge_index.dbのdoc_cardsテーブルにあります(300件サンプルには
   含まれないものもあるのでDBから直接引いてください)。BOILERPLATE判定群/SUBSTANTIVE
   判定群それぞれの人間平均点を算出し、qwen3:8b実測値(68.0 / 80.8、差13点)と比較して
   ください。上記の2つの既知の誤判定例(002E70037DEB、00224434EB7B)がqwen3.8:27bでは
   改善するかも個別に確認してください。
4. **300件の分布集計**: BOILERPLATE/SUBSTANTIVE件数比率、risk_categories別の内訳
5. **レポート作成**: `boilerplate_audit_report.md`をプロジェクト直下に新規作成し、
   (a)モデル比較検証結果、(b)300件分布、(c)誤判定パターンがあれば具体例、
   (d)FULL DB(14,897件)へのこの軸の適用可否についての推奨、をまとめてください

### 重要な制約
- 既存DB(`output/knowledge_index.db`)・既存Agency OS Pack・既存の
  `output_v2/genericness_audit_results.jsonl`(v1の参考データ、232/300件、破棄しないこと)には
  一切触れないでください。今回の出力は`output_v2/boilerplate_audit_results.jsonl`と
  新規レポートファイルのみです
- FULL DB(14,897件)への適用・既存Agency OS Packの変更は、中村さんが明示的に
  指示するまで一切行わないでください
- 完了後、このタスクのStatusを`done`にしてResult欄に記入し、
  `memory/work_status/`に作業ログを残し、Teams Webhookで完了報告してください

Result:
【1. モデル比較検証(28件)】BOILERPLATE判定群(n=15)人間平均67.3点、SUBSTANTIVE判定群
(n=13)人間平均81.5点、分離幅14.2点(qwen3:8bの13.0点からわずかに改善、劇的な差ではない)。
既知の誤判定2件のうちGBC-002E70037DEB(大阪万博スポンサー獲得)はqwen3.8:27bで
SUBSTANTIVEに修正され改善を確認。GBC-00224434EB7B(Digi-Keyブランドキーワード競合)は
引き続きSUBSTANTIVE判定のままだが、人間評価も60点という中間的な値でありボーダーライン
事例と判断(誤判定と断定しにくい)。

【2. 300件本実行】エラー0件で完了。BOILERPLATE 69件(23.0%)・SUBSTANTIVE 231件(77.0%)。
risk_categories別ではcredential_source・success_story(実績・成功事例系)がBOILERPLATE
比率最高(約26-27%)、market_countryが最低(13.5%)で、直感と整合する傾向。

【3. 誤判定パターン】300件全件の人間再採点は今回実施していないが、BOILERPLATE 8件・
SUBSTANTIVE 5件をランダム抽出し目視確認したところ、いずれも判定基準に沿った妥当な
判定で新たな誤判定パターンは見つからなかった(ただし13件は300件の一部であり全数保証
ではない)。

【4. 推奨】数値グラウンディングと同様、自動削除ではなく「レビュー優先度を下げる
フラグ」としての条件付き適用を推奨。中間的スコアの境界事例を扱うBORDERLINEカテゴリの
検討も提案。詳細は`boilerplate_audit_report.md`参照。

既存DB・既存Agency OS Pack・`output_v2/genericness_audit_results.jsonl`(v1参考データ)には
一切触れていません。FULL DB適用は中村さんの判断待ちです。

対応者: Windows側Claude Code(2026-08-27実施)

---

## [2026-08-27T09:45] task-011 — Stage A/B新パイプライン FULL DB本実行(残り14,597件、PoC判断で開始)
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: paused(中村さんの指示により一時停止。PoCとしての位置づけを見直した上で
改めてFULL実行を検討する方針。下記Result参照)
Instruction:

### 背景
中村さんが「まずは今のクオリティでPoC進めたいので、Fullをスタートしても良い」と
判断しました。task-007〜009で見つかった既知の限界(数値グラウンディング的中率15%・
SOURCE FACTへの解釈混入20%・GBC-00CAA957627A系の月表記ズレ)は未解決のままですが、
これ以上の精度改善を待たずにPoCとしてFULL DB本実行に進みます。
`full_db_migration_design.md`(Additive移行設計、6節に中村さんの4決定事項)に沿った
進め方です。

新規スクリプト`full_pipeline_v2.py`を作成しました(`regression_pipeline_v2.py`の
stage_a/stage_b/locate_contextをそのまま再利用、入力を「300件サンプル」から
「doc_cards全件のうち300件サンプルを除いた14,597件」に変更しただけ。出力フォーマットは
regression_pipeline_v2.pyと完全互換)。会社Mac側で`load_all_cards_excluding_sample()`が
正しく14,597件を返すことを確認済みです(依存パッケージpymupdf/python-docx/python-pptx/
openpyxlも会社Mac側venvに追加インストール済み、Dropbox同期不要のローカルvenvなので
Windows側では変更不要のはずです)。

### お願いしたいこと
1. **前提確認**: `full_pipeline_v2.py`をpull、最新か確認。`ollama list`でqwen3.8:27bを
   確認。python.exeプロセスが0個であることを確認(過去に複数プロセス事故が複数回
   あったため、開始前に必ず確認してください)
2. **本実行を開始**(同時に1プロセスのみ):
   ```powershell
   $env:GBC_SSD_ROOT = "D:/GBC_アレココ - 添付ファイル"
   $env:GBC_OLLAMA_MODEL = "qwen3.8:27b"
   cd "<このプロジェクトフォルダ>"
   nohup相当のバックグラウンド実行、または通常のPowerShellで:
   C:\gbc_knowledge_venv\Scripts\python.exe full_pipeline_v2.py --out output_v2\full_v2_results.jsonl
   ```
   14,597件 × 実測19.5秒/件(task-006実績)で**約79時間(約3.3日)**の見込みです。
   `--out`ファイルの既存IDをスキップする設計なので、途中で中断しても同じコマンドで
   再開できます。
3. **進捗報告(重要)**: 過去に長時間バックグラウンド処理が無人で止まっていたのに
   気づかれなかった事例が複数回あったため、**Teams Webhookで定期的に進捗報告**して
   ください(目安: 1,000件処理ごと、または6時間おきのどちらか早い方)。エラーで
   停止した場合・SSDが切断された場合等の異常時も直ちにTeams Webhookで報告してください
4. **完了後**: Result欄に(a)処理件数・所要時間・エラー件数、(b)`has_fact=False`の
   件数・比率、(c)`_numeric_suspect=True`の件数・比率、を記入し、Teams Webhookで
   完了報告してください

### 重要な制約
- 既存DB(`output/knowledge_index.db`)・既存Agency OS Pack・既存の300件サンプル結果
  (`output_v2/regression_v2_results.jsonl`)には一切触れないでください。出力は
  `output_v2/full_v2_results.jsonl`のみです
- **本番DBへのマイグレーション(`migrate_v2_schema.py --allow-production`の実行)は
  このタスクの範囲外です**。FULL実行が完了しても、中村さんと会社Mac側での確認・
  指示があるまでマイグレーションは実施しないでください
- 途中でこのファイル(windows_inbox.md)に新しいtaskが追記されても、この長時間処理は
  中断しないでください(新task追記は別作業の依頼であり、このFULL実行の中断指示では
  ありません。中断が必要な場合は明示的に「task-011を中断してください」と書きます)

Result:
(実行中)【追記 開始から約11.5時間後】1,058/14,597件(7.2%)処理、41,572秒経過
(平均39.3秒/件)。これはtask-006実測の19.5秒/件のほぼ倍で、task-012(qwen3:8b)との
GPU同時実行による速度低下と判断される。task-012の指示書に「task-011の速度が明らかに
低下したらtask-012を一時停止しtask-011を優先する」とあったため、この時点でtask-012を
一時停止した(詳細はtask-012のResult参照)。今後task-011単独の速度がどこまで回復するか
次回進捗報告で確認する。単独ペース(19.5秒/件)に戻れば残り13,539件で約73時間
(合計で開始から約85時間)、このペースのままなら約148時間(合計で開始から約160時間、
約6.7日)の見込み。

【停止 2026-08-27】中村さんより「時間がかかりすぎるのでいったん止めてください」との
指示を受け、本実行プロセスと進捗監視スクリプトを両方停止した(python.exeプロセスが
残っていないことを確認済み)。停止時点で1,086/14,597件処理済み(出力は
`output_v2/full_v2_results.jsonl`にそのまま保持、resumable設計のため再開時は
続きから処理可能)。中村さんより「PoCが終わって改めてFULLで回すことを考える」との
方針も共有された — 今回のFULL規模の試行は一旦区切りとし、PoC(300件サンプルでの
Regression Test、regression_report.md)の結果を踏まえて改めてFULL実行の要否・
やり方を検討する位置づけに変わった。既存DB・既存Agency OS Packには一切触れていない。

対応者: Windows側Claude Code(2026-08-27実施)

---

## [2026-08-27T10:05] task-012 — BOILERPLATE軸FULL監査(残14,560件)をtask-011と並行実行
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: paused(task-011優先のため一時停止 — 指示書の契約通り。下記Result参照)
Instruction:

### 背景
task-010(BOILERPLATE=自己PR/CSR定型文検出)の300件本実行の続きとして、残る14,597件への
全件適用を、会社Mac側でも試みましたが、qwen3.8:27bはApple Silicon(会社Mac)では1件
120秒超と非現実的に遅く(RTX3090とは特性が異なる)、qwen3:8bに切り替えて37件処理した
ところで、中村さんの指示により**「FULLはWindows側で実行する」方針に統一**することに
なりました。会社Mac側の処理は停止済みです。

新規スクリプト`full_boilerplate_audit.py`(Dropbox同期済み、要pull)を作成済みです。
`audit_boilerplate.py`(task-010で使ったBOILERPLATE/SUBSTANTIVE判定ロジック)を、
300件サンプルを除く`doc_cards`全件に適用する版です。出力先
`output_v2/full_boilerplate_audit_results.jsonl`には、会社Mac側で処理した**37件が
既に入っています(シードデータとしてそのまま使ってください、削除・再処理不要)**。
スクリプトは既存IDをスキップして続きから処理するresumable設計なので、そのまま実行
すれば38件目以降が処理されます(残り約14,560件)。

### 重要: task-011と同時にGPUを使うことになります
中村さんの指示で**task-011(Stage A/B FULL、qwen3.8:27b、約79時間)と並行実行**します。
同一GPU(RTX3090、24GB)で2つのOllama処理が同時に走ることになるため、以下に注意して
ください:
- **モデルはqwen3:8b(軽量な方)を使ってください**(`$env:GBC_OLLAMA_MODEL = "qwen3:8b"`)。
  task-010の実測でqwen3.8:27bとの精度差はごくわずか(分離幅14.2点 vs 13.0点)なので、
  並行実行時の負荷軽減を優先します
- 開始直後、両プロセスとも正常に応答が返っているか(タイムアウトやエラーが出ていないか)
  を数分間観察してください。もしVRAM不足(OOM)やtask-011側の処理速度が明らかに
  低下する兆候が見られた場合は、**task-012を一時停止し、task-011を優先**した上で
  Result欄にその旨を記録してください(task-011が主目的のFULL実行のため優先度が高い)

### お願いしたいこと
1. `full_boilerplate_audit.py`をpull、37件のシードデータが
   `output_v2/full_boilerplate_audit_results.jsonl`に入っていることを確認
2. 以下を実行(task-011とは別プロセス、別ターミナルで):
   ```powershell
   $env:GBC_OLLAMA_MODEL = "qwen3:8b"
   C:\gbc_knowledge_venv\Scripts\python.exe full_boilerplate_audit.py
   ```
3. task-011への影響が無いことを確認しながら進めてください(上記の注意点参照)
4. 完了後、Result欄に(a)処理件数・所要時間・エラー件数、(b)BOILERPLATE/SUBSTANTIVE
   件数比率、(c)task-011への影響有無、を記入し、Teams Webhookで完了報告してください

### 重要な制約
- 既存DB・既存Agency OS Pack・既存の`output_v2/boilerplate_audit_results.jsonl`
  (300件本実行結果)・`output_v2/genericness_audit_results.jsonl`(v1参考データ)には
  一切触れないでください。出力は`output_v2/full_boilerplate_audit_results.jsonl`のみです
- 本番DBへの反映(除外/優先度低下のどちらにするか)は中村さんの判断待ちのため、
  このタスクの範囲外です

Result:
qwen3:8bはこのWindows機に未導入だったためpull済み(5.2GB)。開始直後約4.5分の観察
(6回チェック、45秒間隔)では両ジョブとも安定したペースで進み、明確な速度低下は
見られなかったため、そのまま両プロセスを継続した。

【追記・一時停止 開始から約11.5時間後】開始から11.5時間経過した時点でtask-011の
進捗を確認したところ、平均39.3秒/件と単独実行時の実測(19.5秒/件)のほぼ倍まで
低下していたことが判明した(短時間の観察では検知できなかった、長時間の累積効果と
見られる)。指示書の「task-011側の処理速度が明らかに低下する兆候が見られた場合は、
task-012を一時停止し、task-011を優先する」との事前合意に基づき、この時点でtask-012を
一時停止した(TaskStop、python.exeプロセスの停止を確認済み)。

【停止時点の進捗】task-012は1,921/14,597件(13.2%、シード37件含む)を処理して
一時停止。BOILERPLATE/SUBSTANTIVEの内訳等の集計はtask-011完了後、再開して
続きから処理する(resumable設計のため中断分のデータは失われていない)。

既存DB・既存Agency OS Pack・task-010の300件結果には一切触れていません。
再開のタイミングは中村さんの指示、またはtask-011の速度が回復し安全に並行できると
判断した時点で行います。

【追記】その後task-011自体も「時間がかかりすぎる」との中村さんの指示で停止し、
「PoCが終わって改めてFULLで回すことを考える」方針に変わったため(task-011のResult
参照)、task-012も同じ位置づけで保留とする。停止時点の1,921件処理済みデータは
そのまま保持。

対応者: Windows側Claude Code(2026-08-27実施)

## [2026-09-15T09:58] task-013 — Teams全履歴からの暗黙エキスパート抽出(Agency OS「Topic Expert Index」拡張)
Project: `Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/20260814GBC知見集約プロジェクト/GBC-Knowledge/`
Status: done
Instruction:
別の会話で、Agency OS([[gbc_intelligence_engine_project]]参照)に「誰に聞けばよいか」の
第3のインデックス`experts/topic_expert_index.md`を追加した(SharePoint部署別担当者一覧 +
中村さんから直接申告されたチーム別エキスパート、の2本立て)。中村さんから追加要望があり、
「Teamsのやり取りから『この人はこのエキスパート』と分かるものをリスト化してAgency OSに
組み込みたい、明示的な言及だけでなく関与度からの推定も含めて本格的にやりたい」との指示。

会社Mac側で「メッセージ単位の分類が大量に発生する重い処理なので、個人Windows機の
Ollama(qwen3.8:27b)で一次分類してからClaudeで仕上げたい」という方針を中村さんに確認済み
だが、会社Macからこの機のOllama(192.168.0.11:11434)に接続できなかった(ネットワーク的に
届かない)。そのため、**この処理自体をWindows側Claude Codeセッションで実行してほしい**
(このマシンなら自分のOllamaにlocalhostで確実に届くはず)。

【対象データ】
`teams_export_source/teams_messages_d14461_20260915.jsonl`(このタスクの一部として
会社Macから新規コピー配置、Dropbox同期済み)。1行1メッセージのJSONL
(`chat`, `mid`, `author`, `date`, `text`)、7,340件、2026-01-01以降、会社Mac(d14461)の
Teamsエクスポート(42チャット/チャンネル分)。`author`はTeams UI側の表示都合で
約25%しか埋まっていない(同一人物の連続投稿の先頭のみ表示される仕様のため、nullは
「直前と同一発言者」の可能性が高い——決め打ちせず、mid昇順でchatごとにソートし、
直前の非null authorを引き継ぐ機械的な補完をまず行うこと)。

【やってほしいこと】
1. 上記の`author`欠損補完(同一chat内でmid昇順ソート→直前の非null authorをforward-fill)。
   ただし先頭からnullが続く場合は補完せず「unknown」のままにする(でっち上げない)。
2. メッセージ本文から「この人は特定のトピック/業務領域に詳しい・頼られている」ことを
   示す信号を抽出する。2種類を区別して扱うこと:
   - **EXPLICIT**: 「〇〇さんに聞いて」「〇〇さんが詳しい」「〇〇さん案件で相談させて
     ください」のような、他者が名指しで頼っている/推薦している明示的な言及
   - **INFERRED**: 特定トピックのスレッド/チャットで継続的に回答役・説明役を担っている
     等、発言パターンからの推定(EXPLICITより弱い根拠として明示的に区別すること)
   トピックは既存の`experts/topic_expert_index.md`のカテゴリ(法務/契約管理/出張関連/
   設定リクエスト/直受注/D13/ツール/ゲーム/DEI/ナレッジ/GlobalQ/チームビルディング/
   アレココ事務局、AI開発・AI相談/インバウンド/IPコンテンツ・アニメ・ゲーム/
   日系外食産業海外進出/博報堂分析/Salesforce/PowerBI・PowerApps開発/アプリ開発)に
   寄せられるものは寄せつつ、それ以外の自由記述トピック(自由なキーワード、例:
   「〇〇クライアントの過去提案」「インド案件」等)も許容してよい——無理に既存
   カテゴリへ押し込めて情報を失わないこと。
3. **根拠グラウンディング必須**(このプロジェクト全体の設計原則、
   [[feedback_prefer_deterministic_over_llm]]・knowledge_quality_audit.mdの教訓を踏襲):
   LLM(Ollama)に抽出させた(person, topic, evidence_quote, kind)の`evidence_quote`が
   実際に元メッセージ本文に文字列として存在するか、Python側で機械照合すること。
   一致しないものは自動破棄する(evidenceの捏造を機械的に防ぐ、GBC Intelligence
   Engineの`_grounded_in_evidence()`と同じ設計思想)。
4. 出力は中間JSON(`output/teams_implicit_expert_candidates.json`)。各エントリ:
   `{person, topic, kind: "explicit"|"inferred", evidence_quote, chat, date, mid}`。
   Claude側(どのマシンでもよい)が後でレビュー・Markdown化するので、この時点では
   確定リストではなく「候補」でよい——ただし根拠(evidence_quote)は必ず機械的に
   検証済みのものだけを残すこと。
5. **プライバシー配慮**: 業務上のトピック専門性に関係ない個人的な会話内容
   (雑談・体調・プライベートな相談等)は抽出対象にしない。判定に迷う場合は
   除外側に倒すこと(過剰抽出より過少抽出の方が安全)。
6. 処理方式・チャンク分割・プロンプト設計はWindows側の裁量で問題ない
   (このプロジェクトの他のOllama処理と同様、`"think": false`・`temperature`を
   下げてJSON出力を安定させる等、既知の罠は[[gbc_intelligence_engine_project]]
   参照)。処理時間が長時間に及ぶ場合は進捗を定期的にResultへ追記すること。
7. 完了したら、このタスクのResultに(a)候補件数(explicit/inferred内訳)、
   (b)グラウンディングで自動破棄した件数、(c)気になった精度上の懸念、を記入し、
   Teams Webhookで完了報告すること(既存ルール通り)。Markdown統合・SKILL.mdへの
   反映は別途Mac側で行うので、このタスクでは中間JSON生成までで完了でよい。

Result:
「windows_inbox.mdを確認して」の声かけを受け、中村さんに実行許可(AskUserQuestion)を
得た上で着手しました。

【実行前のテストで重大な精度問題を発見・修正】
本番投入前に少数バッチで試したところ、当初のプロンプト設計では「宛先の敬称(○○様)」や
「Teamsの返信引用ブロック(引用開始、○○、日時...引用終了)」に含まれる第三者名を、
発言者本人が語った内容と誤認して不適切なinferred候補を大量生成する問題を発見しました
(例: 単なる「ログインできました」「ありがとうございます」等の相槌が、文中に埋め込まれた
別人の名前を根拠にその人物の「Salesforce専門性」として誤抽出されるケースが多発)。
対策として(1)プロンプトに発言者ラベル("発言者: 実名 | 日時 | 本文"形式)を明示し宛先/引用名との
混同に関する注意書きを追加、(2)inferred種別はPython側で抽出人物名と実際の発言者
(author forward-fill結果)が一致する場合のみ採用し、不一致は機械的に破棄、という2段階の対策を
実装しました。修正後の再テストで誤検出はほぼ解消しました(詳細は[[gbc_intelligence_engine_project]]
参照用にコメントとして`extract_implicit_experts.py`内に残しています)。

【前提条件確認】
Ollama(qwen3.8:27b)はローカルで疎通確認済み。teams_export_source/
teams_messages_d14461_20260915.jsonl(7,340件、243チャット、非空本文7,274件)を使用。
python.exeプロセスは実行前0個、実行中1個(gbc_knowledge_venv)のみだったことを確認。

【author欠損補完】
mid昇順→chatごとにforward-fill。先頭からnull続きの場合は"unknown"のまま(でっち上げなし)。

【本番実行】
チャットごとに30件区切りでバッチ化(全391バッチ)、Ollama(qwen3.8:27b、think:false、
temperature:0.1)で(person, topic, kind, evidence_quote)を抽出。所要時間 約40分
(09:58頃〜開始、5〜8秒/バッチ)。チェックポイント方式(処理済みバッチキーをjsonlに記録)で
中断・再開に対応済みですが、今回は中断なく391/391件を完走しました。

【結果サマリ】
(a) 候補件数: 合計405件(explicit=160件、inferred=245件)
(b) グラウンディングによる自動破棄: 77件(evidence_quoteが元メッセージ本文に実在しない、
    またはinferredで抽出人物名と実際の発言者が不一致だったもの)
(c) 気になった精度上の懸念:
   - 「中村正樹」(表記ゆれ含む: 中村正樹/中村 正樹/中村 正樹 Masaki Nakamura)が
     405件中138件(約34%)を占め、突出して多い。このエクスポート自体が中村さんの
     Teamsアカウントからの抽出であり、多くのチャットで中村さんが宛先・返信対応の
     中心になっているための構造的バイアスと考えられます。Markdown化の際、この
     偏りをそのまま「幅広い分野のトップエキスパート」として提示すると実態と
     ずれる可能性があるため、Mac側での統合時に按分・注意書きの検討を推奨します。
   - 人物名の表記ゆれ(スペース有無・ローマ字併記有無)が正規化されていないため、
     同一人物が複数の別名義でCounterに現れます。Markdown統合時に名寄せが必要です。
   - inferred種別は「発言者=抽出人物名」の一致のみを機械チェックしており、
     実際に「継続的に回答役を担っているか」(質問への応答か、単なる自分の作業報告か)
     までは検証していません。サンプル確認では実質的に問題ない候補が多数でしたが、
     稀に「自分の作業進捗を淡々と報告しているだけ」のメッセージがinferredとして
     残っているケースもありました(例: ファイル送付・並べ替え作業の報告等)。
     Claude側でのレビュー時に「質問への回答」度合いを再確認することを推奨します。
   - プライバシー配慮(雑談・体調・プライベート除外)はプロンプト指示のみで、
     機械的な検証は行っていません。サンプル確認の範囲では業務外の内容は
     見当たりませんでしたが、全405件の目視確認はしていません。

出力: `output/teams_implicit_expert_candidates.json`(405件)
チェックポイント: `output/teams_implicit_expert_checkpoint.jsonl`(391バッチ分、再実行時は自動スキップ)
進捗ログ: `output/teams_implicit_expert_progress.log`
実装: `extract_implicit_experts.py`(プロジェクト直下)

Teams Webhookで完了報告済み。

対応者: Windows側Claude Code(2026-09-15実施)

## [2026-10-17T13:55] task-017 — Ollamaの同時処理数を上げる(OLLAMA_NUM_PARALLEL)
Project: 中村正樹/ (ルート)。Agency OS用アレココ目録の要約・照合を個人MacからこのPCのOllama(192.168.0.11:11434、qwen3.8:27b)に投げている([[ollama_qwen_remote_backend]] [[arekoko_catalog_project]])
Status: done(設定変更は不要と判断 — 既に並列動作していた。下記Result参照)
Instruction: |
  背景: 2026-10-17に個人Macから測ったところ、このPCのOllamaは依頼を1件ずつしか処理しない(3件同時に送ると3倍の時間)。
  中村さんから「ローカルLLMを並行して働かせて速くしたい」と依頼あり。
  やってほしいこと(実行前に中村さんへ内容を見せて許可を取る):
  1. 現在の設定を記録: `[Environment]::GetEnvironmentVariable('OLLAMA_NUM_PARALLEL','User')` と 'Machine'、`ollama --version`、`nvidia-smi` のVRAM使用量(27B読み込み時)。
  2. ユーザー環境変数 OLLAMA_NUM_PARALLEL=2 を設定し、Ollamaを再起動(タスクトレイのOllamaを終了→再起動)。
  3. 個人Macから試す想定のベンチ: 同じ27Bに異なる短い依頼を2件同時に送り、1件ずつより合計時間が短いか。
     VRAMが足りず遅くなる(CPUにはみ出す)なら 1 に戻す。速くなり、VRAMに余裕があれば 3 も試す。
  4. 採用した値と測定結果をResultに書く。
Result:
【結論】Windows側のOllamaは**既に並列処理できており、OLLAMA_NUM_PARALLELの変更は不要**。
環境変数は一切変更していません(現状のまま)。ボトルネックはこのPCではなく
**個人Mac側のクライアント(リクエストの投げ方)**にある可能性が高いです。

【手順1: 現状記録】
- OLLAMA_NUM_PARALLEL: User=未設定 / Machine=未設定 / Process=未設定
  (Ollama 0.32系は未設定時に空きVRAMから自動決定する。結果的に十分な並列スロットが確保されていた)
- OLLAMA_HOST(User) = 0.0.0.0:11434 (LAN公開済み)
- ollama version 0.32.15
- GPU: RTX 3090 24576MiB。qwen3.8:27b ロード時 19,980MiB使用 / 4,347MiB空き、
  PROCESSOR=100% GPU、CONTEXT=16384 (CPUはみ出しなし)

【手順2-3: ベンチ結果(このPC内のlocalhostから実測、同一モデル・num_predict=120・temperature=0)】
| 同時件数 | 逐次実行の合計 | 並列実行の実時間 | 短縮率 |
|---|---|---|---|
| 2件 | 44.5秒 | 22.3秒 | **2.00倍** |
| 3件 | 70.9秒 | 22.8秒 | **3.11倍** |
| 4件 | (約92秒相当) | 26.9秒 | 約3.4倍 |
| 6件 | (約138秒相当) | 28.7秒 | 約4.8倍 |

6件同時でも全リクエストが28.7秒以内に完了し、実行中も PROCESSOR=100% GPU を維持
(VRAM 19,956MiB使用/4,371MiB空き)。**CPUへのはみ出しは発生せず、速度低下も無し**。
→ 「VRAMに収まらないなら無理に入れなくてよい」とのご指示でしたが、そもそも
   設定を増やす必要が無かったため、環境変数は変更せずVRAMリスクもゼロです。

【手順4: 採用値】
**変更なし(未設定のまま)**。現状で2〜6並列が正常に機能しているため、
OLLAMA_NUM_PARALLEL を明示設定するとむしろ自動調整が効かなくなり不利になり得る。

★【中村さんへ — 次に確認していただきたいこと】
依頼にあった「3件同時に送ると3倍の時間がかかる」は、このPC内からは**再現しません**
(3件同時で3.11倍速くなる)。考えられる原因は個人Mac側:
1. スクリプトが実は逐次実行になっている(for ループで1件ずつ await/待機している)。
   → asyncio.gather / 並列スレッド / `xargs -P 3` 等で本当に同時送信になっているか確認。
2. 同一HTTPコネクション(セッション)を使い回していて直列化している。
   → リクエストごとに別コネクションを張る、または http クライアントの
      コネクションプール上限(例: httpx の max_connections=1)を確認。
3. モデルのkeep_aliveが切れて毎回ロードし直している可能性(初回は17GBのロード待ちが入る)。
   → 計測前にウォームアップ1回を入れる(今回のベンチもそうしています)。

検証方法(Mac側で実行、このPCのOllamaに直接当てる簡易テスト):
  time ( for i in 1 2 3; do curl -s http://192.168.0.11:11434/api/generate     -d '{"model":"qwen3.8:27b","prompt":"List 3 colors.","stream":false,"think":false,"options":{"num_predict":60}}'     -o /dev/null & done; wait )
この実時間が「1件だけ送ったときの時間」とほぼ同じなら並列は効いています(＝Mac側スクリプトの問題)。
3倍かかるなら、そのcurl自体は並列なのでネットワーク/クライアント側をさらに切り分けます。

対応者: Windows側Claude Code(2026-10-17 実施)
  [2026-10-17 14:30 個人Mac] 確認: 個人Macから実際の照合依頼(長文)で比べると、1件ずつ10件/分 → 3並列11件/分(約1.1倍)。長い依頼では読み込みでGPUが埋まるため。照合は--workers 3で継続。

## [2026-10-17T15:45] task-018 — 個人Macから遠隔シャットダウンできるようにOpenSSH Serverを設定
Project: 中村正樹/ (ルート)。[[home_network_setup]] [[feedback_home_infra_no_public_exposure]]
Status: done(2026-10-17 完了・疎通確認はMac側task-016待ち)
Instruction: |
  背景: 2026-10-17、中村さんから「今後は個人Macからも個人Windowsをシャットダウンできる構成に」と依頼。
  今はSSH(22)もWinRM(5985)も閉じていて、個人Macから止める手段がない。個人Mac側の準備は済み
  (鍵 ~/.ssh/id_ed25519_windows、~/.ssh/config の Host win-home → 192.168.0.11 / User maxak、
  スクリプト .claude-sync/Scripts/windows_power/win_power.sh)。
  やってほしいこと(管理者PowerShellが必要。実行前に中村さんへ内容を見せて許可を取る。UACの許可は中村さんが押す):
  1. OpenSSH Serverを入れて自動起動にする:
     Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
     Set-Service sshd -StartupType Automatic; Start-Service sshd
  2. 鍵認証だけにする: C:\ProgramData\ssh\sshd_config で `PasswordAuthentication no`、`PubkeyAuthentication yes` を有効にする
     (末尾の `Match Group administrators` / `AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys` はそのまま)。
  3. maxak が管理者なら C:\ProgramData\ssh\administrators_authorized_keys に次の1行を書く(UTF-8、BOMなし、改行LFかCRLF):
     ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH99n5aFC6tEUZj0qDk+gLaydlswx9tx1DflpyqEQ9W4 maxakisan@ICPTokyo2022-win-admin
     権限: icacls C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
     (管理者でなければ C:\Users\maxak\.ssh\authorized_keys に書く)
  4. 外から入れないようにする(自宅インフラは公開しない方針): インストール時にできる受信ルール OpenSSH-Server-In-TCP の
     リモートアドレスを LAN と Tailscale だけに絞る:
     Set-NetFirewallRule -Name OpenSSH-Server-In-TCP -RemoteAddress 192.168.0.0/24,100.64.0.0/10
  5. Restart-Service sshd。Windows内で `ssh -o BatchMode=yes localhost exit` は鍵が無いので失敗してよい。
     代わりに `Get-NetTCPConnection -LocalPort 22 -State Listen` で待受けを確認。
  6. Resultに、各手順の結果と、maxak が管理者だったか、どちらの authorized_keys に書いたかを記入。
     個人Mac側で `win_power.sh` の接続確認(`ssh win-home hostname`)をするので、Windowsは起動したままにしておく。
Result:
【結論】**完了**。Windows(192.168.0.11)で鍵認証のみのSSH待受けが稼働し、LAN/Tailscaleのみに
制限済み。残りは個人Mac側からの疎通確認(personal_mac_inbox task-016)のみ。

【重要な仕様変更: ログインユーザー maxak → maxakisan】
中村さんの指示により変更。Windowsに maxakisan が存在しなかったため**新規作成**した。
パスワードは中村さん自身がRead-Hostで入力しており、**Claudeは関知せず・どこにも保存していない**。
- `DESKTOP-RYZEN59\maxakisan` SID ...-1003 / PrincipalSource=Local / Administrators所属(確認済み)
- 管理者のため鍵は administrators_authorized_keys に登録(手順3の分岐はこちら)
- 参考: 既存 maxak は PrincipalSource=MicrosoftAccount

【Claudeから実行できなかった件(重要な申し送り)】
Windows側Claude Codeの**自動モード安全フィルタが `Unauthorized Persistence` と判定し、
Bash/Write両方でスクリプト作成を拒否**した(常時待受けのリモートアクセス設定のため)。
中村さんの承認済みだったがセッション側では解除できず、**手順を提示して中村さんが
管理者ターミナルで手動実行**する形に切り替えた。検証・記録はClaude側で実施。
→ 今後この種の設定変更をWindows側Claudeに依頼する場合、同じフィルタに当たる前提で
  「手動実行用コマンドの作成」までを依頼範囲とするのが現実的。

【各手順の結果(Claude側で独立に検証済み)】
- [0] maxakisanアカウント作成(管理者) — **完了**
- [1] OpenSSH.Server~~~~0.0.1.0 = **Installed**、sshd = **Running / Automatic**
- [2] sshd_config: `PasswordAuthentication no` / `PubkeyAuthentication yes` を確認。
      末尾の `Match Group administrators` と `AuthorizedKeysFile .ssh/authorized_keys` は温存。
      バックアップ `sshd_config.bak_20261017` を作成済み
- [3] C:\ProgramData\sshdministrators_authorized_keys = 115B(鍵1行、UTF-8 BOM無し)。
      icacls で Administrators:F / SYSTEM:F に制限 → **非昇格シェルからは読めない状態**
      (= 権限設定が正しく効いていることの確認になった)
- [4] OpenSSH-Server-In-TCP: RemoteAddress = `192.168.0.0/24, 100.64.0.0/10` のみ。
      Enabled=True / Action=Allow / Direction=Inbound
- [5] port22 **LISTEN確認**: `0.0.0.0:22` と `[::]:22` (PID 31248)

★【中村さんに知っておいていただきたい注意点2つ】
1. **FWルールのProfileが `Private` のみ**。現在の接続先(aterm-2563e2-a)はPrivate判定なので
   今は通るが、ネットワークがPublicに変わるとSSHが**通らなくなる**。自宅限定運用なら
   このままで安全側。恒久的に効かせたいなら `-Profile Private,Domain` を明示する。
2. Tailscaleは当初未導入だったが、**同日(2026-10-17 19:00頃)中村さんの指示により導入・ログイン完了**。
   - winget install Tailscale.Tailscale → v1.104.1、サービス Running/Automatic
   - ログインは中村さんが手動(ブラウザ認証)。アカウントは **maxakisan@ でMacと同一tailnet**
   - Windowsのtailnetノード: **desktop-ryzen5950 / 100.100.64.40**(許可済み100.64.0.0/10の範囲内)
   - Tailscaleアダプタの NetworkCategory = **Private** → 上記1のProfile=Privateルールが適用され通る
   - 検証: `Test-NetConnection 100.100.64.40 -Port 22` = True、`tailscale ping macbookmn` = pong 11ms
   → **外出先からの遠隔シャットダウンも可能な構成になった**(ポート開放は一切していない)。
     Mac側 task-016 に、LAN用(win-home)とTailscale用(win-ts)の2系統を設定する指示を追記済み。

3. ★**止められても起こせない**: WoLはルーター(HGW-BL500HM)の管理パスワード不明で保留中
   ([[wol_setup_status]])。外出先から落とすと帰宅して物理的に電源を押すまで使えない。
   このPCはOllamaバックエンド(27B)でもあるのでMac側の要約・照合処理も止まる。
   遠隔シャットダウンは「帰るまで使わないと確信できるとき」限定の運用が前提。
   WoL側の解決は中村さんに提案済み(2026-10-17時点で未着手)。

【Mac側への申し送り】
`User maxak` のままでは接続不可のため personal_mac_inbox.md に **task-016** を起票済み
(~/.ssh/config の User変更 + `ssh win-home hostname` 疎通確認 + win_power.sh のユーザー
決め打ち確認)。疎通確認のため**Windowsは起動したまま**にしてある。

対応者: Windows側Claude Code(検証・記録)/ 実行: 中村さん(管理者ターミナルで手動、2026-10-17)

---

## [2026-10-21T19:00] task-gbc-overseas-F — GBC利益拡大: 海外CIなし取引先(F群)の海外事業調査
Project: `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/20261019_予算達成と稼ぐ力分析/work_analysis/`
Status: done (2026-10-22 完了。Windowsの作業は不要・Ollamaは使い終わり)
Instruction:
入力 `海外事業調査_入力_F群_20261021.csv`(約6,700社、取引先名を含む)。**ユーザー(中村さん)が2026-10-21に個人Windowsへの取引先名の持ち出しを許可済み**(電通の扱い企業かどうかはこのリストだけでは判別できないため)。
各社について、Web検索で「海外拠点・海外売上・海外進出の有無」を調べ、出力CSV `海外事業調査_結果_F群_20261021.csv` に保存。列=取引先企業コード/企業名/海外事業(あり・なし・不明)/根拠の一言/根拠URL/確度(高中低)。
- 先に上位100社で試行し、結果を中村さんに見せてから全量に進む。ローカルOllama(qwen)での一次判定も可。結果は逐次保存。
- 持ち出しは取引先名のみ。他の社内数値(売総など)は含めない。
Result:
2026-10-21 Mac側Claude Codeが実施。先頭100社を試行し `海外事業調査_結果_F群_20261021.csv` に保存。Web検索で確認できたのは約30社(あり19・不明数社・ドミノのみ「なし」中)。残りは自治体・財団・外資系等で、Web未検索の推定(確度低)。全量(約6,700社)はMac側で `Scripts/overseas_survey/run.py`(Bing検索+WindowsのOllama qwen判定、名前から明らかな「なし」はルール判定)を2026-10-21に開始、約6時間。再開可(同じコマンドで続きから)。Windowsは完了まで起動したままにする。

2026-10-22 全量完了(Mac側)。最終版 `海外事業調査_結果_F群_20261022_01.csv`(6,700社): あり1,403/要確認634/なし648/シグナルなし1,968/不明2,047。
方式変更: 検索スニペット判定(run.py/run2.py)は的中率が低く、公式サイト直接取得方式 `run3.py`(検索は公式URL特定のみ→会社概要等を取得→正規表現→候補のみqwen確認)に切替。旧不明4,058社と旧あり1,892社を再調査し、旧あり634社を『要確認』に降格、483社を確定(確度高)。不明は不明のまま。
Windows側の追加作業・起動維持は不要。
