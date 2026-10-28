# Agency OS — Dify実機テストで判明した捏造・検索漏れ問題(2件目のブリーフテスト)

## 2026-09-12T16:00:00+09:00 (approx)
Status: done(SKILL側の対応) / pending(Top K設定変更はユーザー対応待ち)
What: [[work_status/agency_os_dify_flow_rewiring_20260912]]でDocx添付読み込み配線を修正した後、
中村さんが2件目のテスト(仮ブリーフ_AcecookVietnamプロジェクト個別依頼_BD部新保様)を実施し、
新たに4件の問題を発見。

## 発見した問題(すべてローカル実データで検証済み)
1. **サンプルURLの丸ごと再利用**: 出力に`https://dgx.lightning.force.com/lightning/r/GBC__c/a009F00000xxxxxxx/view`
   という「サンプル形式」と自称するURLが出た。調査の結果、これはSKILL.mdのルールA自体に書いていた
   説明用の例(`.../xxxxx/view`、かどや製油の例)をモデルがほぼそのまま流用したものと判明。
   ドキュメント自身の説明例が事故の原因という自己言及的なバグ。
2. **ツール名の完全捏造**: 「GBCarekoko」「Nielsen」「Intage」「電通メディアプランニングツール（社内）」
   「Brandwatch/Synthesio」がTOOLS欄に出たが、`GBC-Knowledge/output/agency_os_pack/tools/tools.md`を
   直接確認したところ全て存在しない(実際は28ツール: Advertising Age/RECMA/SPEEDA/Similar Web/
   Statista/eMarketer等、すべて実URL付き)。ルールC「tools.md以外を提案するな」が破られていた。
3. **overseas_staff_index.mdの実データ不使用**: ローカルの元ファイル(485行)を直接grepしたところ、
   「## ベトナム」セクションに伊藤広貴さん(ホーチミン、現在)・野口紗知子さん(ホーチミン、現在)・
   新保泰史さん(ホーチミン、2021-2025過去)が実在(ブリーフ宛先の「新保様」と同姓という興味深い一致)。
   にもかかわらずDify側は「特定できず」と回答していた。
4. **「検索実施バケット」の生ファイル名リスト表示**、および1回目の指摘と同種の「tools.mdに記載の
   URLを参照」「実URLは新保様がSalesforceで直接ご確認ください」という丸投げ表現も再発。

## 根本原因(2と3の共通原因)
Difyの知識検索ノードがTop K=6のまま、cases/knowledge/faq/pm/tools/case_expert/overseas_staff/
task_briefingの計8ファイルを1回の検索で横断しているため、ブリーフ全文のような長いクエリでは
特定カテゴリ(tools.md、overseas_staff_index.md等)の該当チャンクが上位6件に入らず、検索結果に
一切現れないことがある。ルールC/Fで「必ずTOOLSセクション/駐在員セクションを含める」と要求している
ため、検索結果が空でもセクションを埋めようとして捏造が発生したと考えられる。

中村さんへの提案(未実施、ユーザー対応待ち): 知識検索ノードの「検索設定」でTop Kを6→15〜20程度に
増やす。改善しない場合は将来的にファイル別の個別検索(複数知識検索ノード+メタデータフィルタ)への
再設計が必要になる可能性がある。

## SKILL.md/SKILL_Dify.md修正内容(両ファイルに同一適用)
1. ルールAの説明例URLを明らかにフェイクと分かる形式(`REDACTED-EXAMPLE`)に変更し、
   「この例を実際の回答に流用するな」と明記
2. ルールCに「今回の検索で実際に返ってきたtools.mdの内容にのみ基づくこと。GBCarekoko等、
   一般知識として知っている本物の社内システム名であっても、今回の検索結果に無ければ名前を
   出すな。0件なら正直に0件と言え」を追加
3. 「Mandatory internal search pattern」節に「検索実施バケットの生ファイル名リストをユーザー
   向け出力に出すな(COMMON KNOWLEDGE TEST MODEのTest provenance欄のみ例外)」を追加

## Next(次にこのプロジェクトに触るとき)
1. 中村さんが知識検索ノードのTop Kを増やしたか確認
2. SKILL_Dify.md最新版(上記3点の追加分)がDifyに貼り直されたか確認
3. 同じAcecook Vietnamブリーフで再テストし、(a)実URLまたは正直な「出典URL未掲載」、
   (b)tools.mdの実ツールのみ使用or正直な0件、(c)overseas_staff_index.mdのベトナム3名
   (伊藤広貴・野口紗知子・新保泰史)が正しくヒットするか、を確認
4. Top K増加で改善しない場合、ファイル別個別検索への再設計を検討
