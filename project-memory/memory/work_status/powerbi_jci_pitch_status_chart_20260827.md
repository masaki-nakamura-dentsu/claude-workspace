## 2026-08-27 セッション: JCIピッチ状況チャート、Tableau計算ロジック解析完了 → SFフィールド名確認待ちで中断

**Status: in progress (中断、次回はフェーズ値の実データ確認から再開)**

前段: [[powerbi_gbc_dashboard_current_state]]の持ち越しタスク(横棒グラフ上位N)は正樹さんが既に100件に設定済み、検証用クエリもクリーンアップ済みと確認。「設定_月別_前年比」棒グラフ→テーブル切替の新規依頼はブックマーク+ボタン方式の手順を案内したが、作業量が大きいため保留に(§9に追記)。

代わりにTableauの「7. QBR_Japan Client ピッチ状況.twb」スライド2(Won/Lost by Pitch Types、Net Win、Net Win vs HDY、サマリーテーブル)をPower BIに移植する新規タスクに着手。

**やったこと**:
- pptx書き出し(20260814版)のスライド2を画像抽出し、目標ビジュアルの構成を確認。
- twbファイル(XML、5.4MB)から該当ダッシュボード用の計算フィールド定義を正規表現で抽出。目的のダッシュボード自体(story-point名`Q1`)は削除済みだったが、計算フィールド定義(`ﾌｪｰｽﾞ/Phase (2)`のWon/Lost/Pipeline/Cancelled判定、`Net Win`、`HDY`判定、`提供ｻｰﾋﾞｽ/Services to Provide(2)`の部門バケット化)は他の関連ワークシートに残っており復元できた。
- マニュアル`(Manual) GBC QBR_Tableau20260401.docx`の「8. 元データの更新(日系ターンアラウンド)」を確認、元データはSalesforceレポート「APAC Pitch - List All_v1.31」(`00OfP00000Cq0rRUAR`)経由と判明。
- 正樹さんから当該レポートのフィルタ条件10個をスクリーンショットで受領、記録済み。
- 既存ログから確定済みSalesforceフィールドマッピング(部署名/地域/市場/事業区分/クライアント/商流/フェーズ/活動項目/関係会社/GBC貢献度/GM確認)を再利用可能と確認。

**ブロッカー**: ピッチ種別/Pitch Type、GBC案件/Items:重複/Dup(マスタ行レベル)、JP Turnaround Project、責任者/Owner、獲得グループ/Winning Group、提供サービス/Services to Provide、競合グループ/Competitor's Group、ピッチ実施日/Pitch Date、Group売総/Revenue(GBP、JPY版`GBCGross__c`とは別物の可能性)の9項目のSalesforce API名が未確認。Salesforce直結アクセス手段がこちらに無いため、正樹さんにObject Manager(GBC案件/Items→項目とリレーション)での確認を依頼中。

詳細は[[powerbi_jci_pitch_status_chart]]参照(Tableau計算式の完全な復元ロジック・フィルタ条件・次回手順を記載済み)。

**続き**: 正樹さんがSalesforce Object Manager「GBC案件/Items」の項目とリレーション一覧(全147フィールド)をxlsxでエクスポートして提供。未確認だった9フィールドすべて解決(ピッチ種別=`GBCCompetitivePitch__c`、重複/Dup=`GBCConnection__c`、JP Turnaround Project=`GBC_JP_APAC_Turnaround_PJ__c`、責任者=`GBCResponsiblePerson__c`(ID)/`GBCParentResponsiblePerson__c`(テキスト候補)、獲得グループ=`GBCWinningAgencyGroup__c`、提供サービス=`GBCServicestoProvide__c`、競合グループ=`GBCCompetitorsGroup__c`、ピッチ実施日=`GBCPitchDate__c`、Group売総GBP=`GBCGrossGBP__c`)。xlsx原本はDownloadsから`Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し/GBC__c_項目とリレーション_20260827.xlsx`に移動保存(今後のGBC__c関連作業で再利用可能)。

これを元に新規クエリ`JCI_Pitch_Base`のPower Query M式(10条件のフィルタ+Phase2/Net Win/HDY/部門バケットの列追加)、DAXメジュー5本、3チャート+テーブルの構築手順一式を作成し[[powerbi_jci_pitch_status_chart]]に記載、正樹さんに提示済み。

**続き(検証作業、Power BI Web版で正樹さんが実施)**:
1. 条件8(責任者)で行が0件になる不具合発生 → 診断クエリで`GBCResponsiblePerson__c`の生値がID(`a0W7F...`)であり名前ではないと判明 → Object Managerで参照先オブジェクトを追って`Employee__c`(表示ラベル「従業員」)と特定 → `Employee__c`と結合し`Name`列を展開する方式に修正、**これは解決・動作確認済み**。ただし実データの氏名は「小池 和雄」のように姓名間に半角スペースが入る形式(SF Reportフィルタ画面の表示はスペース無しだった)と判明、条件式もスペース入りに修正。
2. 責任者条件を直したら**今度はフェーズがWonしか出ない不具合**が発生。原因調査で、twbから抽出した「完了･成立 (Complete)」の中黒が半角カナ(･)で、Salesforce実データは全角(・)だったため完全一致比較が静かに全滅していたことが判明 → 英語カッコ部分一致(`Text.Contains(phase,"(Complete)")`等)に変更、あわせて`Text.Contains(null,...)`をif条件に使うと評価エラーになる別バグも発見・修正(`let`で先にnull安全な変数化)。
3. **しかし修正後も症状変わらず(Wonのみ)**。半角/全角中黒だけが原因ではなく、英語部分を囲む括弧自体が全角(既に`レコードタイプ名`の判定で全角括弧`（GBC）`が使われている実例があり、同じパターンの可能性)、または日英の並び順が想定と逆の可能性を疑っている。フェーズ値を一切加工せず記号で囲んで確認する診断クエリを流している途中で終業時間になり中断。

**次回再開ポイント**: [[powerbi_jci_pitch_status_chart]]の「現在地」節に貼ってある診断クエリ(`GBCPhase__c`の値を`【`と`】`で囲んで正確な表記を確認するもの)を実行してもらい、出力を一字一句確認するところから。責任者(条件8)側は解決済みなので再度疑う必要なし。

正樹さんから今後必要なスライサーとして「計上年/四半期/クライアント名/地域/市場/ピッチ種別/提供サービス/競合グループ/フェーズ」の指定あり(まだ`JCI_Pitch_Base`に未追加、クライアント名・計上年/四半期は追加実装が必要)。

## 2026-08-31 セッション: フェーズ値の実データ確定→FY26日付フィルタ発見→数値完全一致→3チャート構築中

**Status: in progress(サマリーテーブル追加待ち、ほぼ完成)**

前回の中断点(診断クエリ)から再開。

**やったこと**:
1. 診断クエリの結果、`GBCPhase__c`の実データは想定と全く違う形式と判明: 英語が先頭+全角括弧(`Complete（完了・成立）`/`Incomplete（完了・不成立）`)、かつ`仕掛中/未受注 (In Progress)`は存在せず代わりに`New（新規）`という値だった(SF側でラベルが変更された模様)。`進行中/受注済み (Order Received)`のみ半角括弧で従来想定通り。実データの4値そのまま完全一致(`=`)に切り替え、`New（新規）`→Pipelineとして`JCI_Pitch_Base`の「条件9_フェーズ」「列追加_フェーズ判定」を修正。
2. 修正後も件数が目標(Won91/Lost85/Pipeline36の想定)と合わず428件(目標の約2倍)。目標スライドのサブタイトル「FY26に結果判明案件」に着目し、正樹さんにTableau側フィルタ(twbファイル)を確認してもらったところ、`ピッチ結果判明日/Pitch Close Date`(YEAR=2026)という未実装の日付フィルタを発見。twbファイルをBashで直接grep・Object Manager書き出しxlsx(`GBC__c_項目とリレーション_20260827.xlsx`)を検索し、API名`GBCPitchCloseDate__c`(標準Opportunity.CloseDateと同様、Won/Lost実績日＋Pipelineの決着予定日を兼ねるフィールドと推測)を特定。
3. この日付フィルタを追加(当初2026固定→後に正樹さんの要望で計上年フィルタをスライサー化する必要があり、Power Query側は「値がある行のみ」に緩めて`決着年`(Date.Year)をネイティブ列として追加する方式に変更)。
4. 検証: Won=91/Lost=49/Pipeline=36(合計176)、Group売総=18,424,119円で再現。目標の「# of Pitches=176」は全件合計、「Won Pitch # %=65.0%」はWon/(Won+Lost)=91/140という指標定義の食い違いも解消(誤った旧DAX案を修正)。
5. DAXメジュー7本(`Net Win (GBP)`, `# of Pitches`, `# of Won`, `# of Lost`, `# of Pipelines`, `Won Pitch # %`, `Group売総_GBP合計`)を提示 → 正樹さんが1つの数式バーに全部貼って構文エラー(Web版DAXエディタは1メジュー=1回の新規作成が必須、複数行貼り付け不可という新知見) → 1つずつ作成し直して解決。
6. 3チャート構築、Net Win(GBP)カード=3.81M(目標3,814,085)で一致確認。左チャートで最初Wonバーが表示されない不具合発生→ビジュアル単位のフィルタでWonのチェックが外れていたのが原因と判明・解決。中央チャート(PracticeBucket)の並び順を「Others→Media→Brand→Integrated」に固定するため、Power Query側に`PracticeBucket並び順`列(Others=1/Media=2/Brand=3/Integrated=4)を追加し、Power BI Web版のモデルビュー→列のプロパティパネル→「詳細」内の「並べ替えの基準列」で設定、解決。

**新知見(次回以降の教訓)**:
- Power BI Web版のDAXエディタ(新しいメジュー)は複数行の「名前=式」をまとめて貼ると構文エラーになる。メジューは1つずつ追加が必要。
- Web版モデルビューでの列プロパティ設定(並べ替えの基準列など)は、右ペインの列を選択→プロパティパネルの「詳細」を展開すると出てくる(Desktopの「列ツール」リボンに相当)。
- Salesforceの選択リスト値は元Tableauのラベルと完全に一致しない場合がある(ラベル変更・順序・全角半角の違い)ため、推測でハードコードせず必ず実データを診断クエリで先に確認する方針を今回も踏襲・再確認。

**残作業**: 下部サマリーテーブル/カード群(`Net Win (GBP)`/`# of Pitches`/`# of Won`/`# of Pipelines`/`Won Pitch # %`)の配置のみ。配置後、目標pptxとの最終突合を予定。`JCI_Pitch_Base`の最新M式・DAXメジュー・既知の罠は[[powerbi_jci_pitch_status_chart]]に追って反映予定。

**Next**: サマリーテーブル配置→スクショ確認→完成なら[[powerbi_gbc_dashboard_current_state]]のページ一覧に正式追加。

## 2026-08-31 セッション(続き): 体裁調整・9スライサー・ALL ITEM+明細ページを追加、本日終了

**Status: done(本日分の依頼はすべて完成、次回は正樹さんからの追加依頼待ち)**

前段のサマリーテーブル一致確認の後、以下を実施。

1. **3チャートの見た目調整**: 中央/右チャートが「積み上げ棒グラフ1本」になっていなかった(軸にフィールドを入れていたため)のを、軸を空にして凡例に移動する形に修正。Phase2/ピッチ種別/PracticeBucket/HDYそれぞれに並び順用の列(`Phase2並び順`等)を追加してモデルビューの「並べ替えの基準列」で固定。twbファイルを直接grep・パースして正確な配色コード(Tableauの実際の16進カラー)を取得し、3チャートすべてに適用。HDYの値を"Y"/"N"から"VS HDY"/"VS NON-HDY"にPower Query側で書き換え(Web版のビジュアル右クリックに「名前の変更」が無いことが判明したための代替策)。
2. **9スライサー追加**: 決着四半期/決着月/クライアント名(Account結合)/地域/市場/ピッチ種別/提供サービス/ピッチスコープ(`GBCScopeOfPitch__c`)/勝因敗因(`GBC_Cause__c`)。地域・市場・提供サービス・ピッチスコープ・勝因敗因はSalesforce複数選択リストのため、正樹さんの判断で最初からブリッジテーブル化(`地域_Bridge_JCI`等5本、`JCI_Pitch_Base`参照→Id+対象列→セミコロン分割→展開→トリム)。リレーションシップは`Id`同士(既存の市場_Bridge等とは異なり`JCI_Pitch_Base`の`Id`がユニークなので、多対多ではなく**一対多+双方向**で組んだ、この判断の理由は[[powerbi_jci_pitch_status_chart]]参照)。`勝因敗因`列はnull行があり`Text.Split(null,...)`でエラー→null安全化して解決。
3. **左チャート「空データも軸に表示」対応**: `Phase2`が元のファクトテーブル列のままだと0件カテゴリが軸から消える仕様のため、`Phase2一覧`という独立ディメンションテーブル(手動テーブル、Won/Lost/Pipeline+並び順)を新設し、軸をこちらに差し替え+リレーションシップ(一対多、単一方向)+ビジュアルの「空の値を表示」をON。**この設定はPower BI Web版では書式ペインではなく、軸フィールド自体の「∨」ドロップダウンメニューにある**(ここも一つハマりポイントだった)。
4. **ALL ITEM+ページ新規構築**: TableauのworksheetXML(`<rows>`タグ)を直接grepして正確な列順序・フィルタ条件・ソート条件を復元(推測より確実)。新規フィールド3つ追加: `GBCGross__c`(Group売総JPY)、`BP_Support__c`(BPサポート)、`案件名表示`(作成日が前月なら"● "を先頭付与、Power Query側で`DateTime.LocalNow()`基準に動的判定)。加えて`実施年`/`実施四半期`(ピッチ実施日ベース、決着日ベースの`決着年`/`決着四半期`とは別物)を追加。テーブルビジュアル1つで構築、Group売総GBP降順ソート・提供サービスnull除外・GBP≥1フィルタを適用、実データがTableau側の並び順・件数と一致することを正樹さんが確認済み。仕上げに`Phase2`のWin/Lostスライサーも追加。

**新知見(次回以降の教訓)**:
- 複数選択リストのブリッジテーブルは、ファクト側のIDがユニークなら`多対多`ではなく`一対多+双方向`で十分(既存の市場_Bridge等は逆にRaw YTD側のIDが重複するので多対多が必要だった、というだけ)。
- Power BI Web版で「空の値を表示」(Show items with no data)は書式ペインになく、軸/凡例フィールドの「∨」ドロップダウンにある。
- Tableauのtwbファイルは、色・フィルタだけでなく`<rows>`/`<cols>`タグから正確な列順序・ソート条件・フィルタ条件も復元できる(ワークシート単位で`<worksheet name='...'>...</worksheet>`をgrepすればよい)。今回`ALL ITEM+`ワークシートの列順・フィルタを画像の目視や推測なしに正確に再現できた。
- Power Query M式で日付ベースの「動的な今月/先月」判定をする時は`DateTime.LocalNow()`から`Date.StartOfMonth`/`Date.AddMonths`で計算する(このプロジェクトのSelectedYear/SelectedMonthパターンと同系統の考え方)。

これでJCIピッチ状況チャートプロジェクトは、3チャート+サマリーテーブル+9スライサー+ALL ITEM+明細ページまで完成。次回持ち越しは無し(正樹さんから新規依頼が来るまで待機)。詳細は[[powerbi_jci_pitch_status_chart]]に反映予定。

## 2026-09-01 セッション: 競合グループスライサー追加→Competitive Analysisページ→Q8/Q8(2)/Q8(3)の3ツリーマップページまで完成

**Status: ほぼ完了(Competitive Analysisページの凡例並び順のみ未解決で保留)**

正樹さんが2ページを「JCI_All_Pitches(グラフ)」「JCI_All_Pitches(内訳)」とリネーム済みと判明。以下を実施。

**1. 競合グループスライサー追加**: 両ページに`競合グループ_Bridge_JCI`(既存5ブリッジと同パターン、`GBCCompetitorsGroup__c`をセミコロン分割)を新規作成しスライサー追加。リレーションシップ作成時に再度「多対一 (*:1)」の向き(テーブルからJCI_Pitch_Base、テーブル表示が競合グループ_Bridge_JCIの場合)を間違えて重複値エラーが発生→カーディナリティのドロップダウンを逆にして解決(既知の教訓の再発、[[powerbi_gbc_dashboard_current_state]]§4に既に記載済みの内容)。

**2. Tableau「Q1 (5)」= Competitive Analysis - YTDページの移植**: twbファイルを直接grep/parseして、`ALL NW_Comp W`/`ALL NW_Comp L`ワークシートの構造(軸なし・凡例=競合グループの単一積み上げ棒、WON/LOST別)を復元。

- **重大な罠(教訓化必須)**: 最初、スライサー用に作った`競合グループ_Bridge_JCI`(セミコロン分割・複数値展開)をこのチャートの凡例にも流用したところ、WON合計が6,945K→9,456K、LOST合計が10,165K→18,703Kに水増しされた。原因は、複数の競合グループが記載された案件(例:「博報堂/Hakuhodo; WPP」)が分解されて両方に売上が二重カウントされたため。**Tableau側は複数選択リストの組み合わせ文字列を分解せず、1つの結合文字列をそのまま1カテゴリとして扱っている**(twbのcolor encodingが確認できた:個別の会社名だけでなく「WPP; Omnicom」のような組み合わせも独立したbucketとして定義されていた)。対策として、分解しない専用の`競合グループ_Dim_JCI`(生の`GBCCompetitorsGroup__c`ごとにWON/LOST合計・順位を集計するディメンションテーブル、JCI_Pitch_Base側に非空文字列版の計算列`競合グループ_表示`をDAXで追加してリレーション)を新設し解決。**同じ罠が「Market by Status」「Client by Status」ツリーマップでも起きかけたが、事前にこの教訓を踏まえて`市場_Bridge_JCI`を使わず生の`GBCCountry__c`列を直接使う方式を最初から選択、問題なく完成。**
- 空欄値をリレーションのキーにできない(「列 ''には空白の値が含まれていますが...」エラー)問題は、DAX計算列で`IF(ISBLANK(...), "(未設定)", ...)`のnull安全化+Power Query側も同じロジックで空欄を「(未設定)」に統一して解決。
- **未解決(保留)**: WON/LOSTそれぞれ独立して「金額の大きい順」に積み上げるため、`競合グループ_Dim_JCI`に`WON売上順位`/`LOST売上順位`という順位列を追加し、`並べ替えの基準列`をWON用・LOST用で別々の列(`競合グループ`/`競合グループ_LOST表示用`、同じ内容を複製)に設定する方式を試みたが、最終的にLOST側の凡例順序がWON側の順位(`WON売上順位`)につられたような不可解な並びになり解決に至らず。正樹さんの判断でこの課題は保留、次回リベンジ予定。色の統一(競合グループごとに固定HEX、twbのcustom color encodingから抽出)は別途完了済み。

**3. Tableau「Q8」「Q8 (2)」「Q8 (3)」= Service/Market/Client by Statusの3ツリーマップページ移植**: いずれもWon/Lost/Pipeline別の3枚組ツリーマップ+下部Won/Lost/Pipeline合計カード、という共通パターン。`Pipeline Revenue (GBP)`メジューを新規追加(Won/Lost Revenueは既存流用)。

- Service by Status: `PracticeBucket`(サービス区分、単一選択想定)で構成比、Market by Status: `GBCCountry__c`(市場、生の値)で構成比、Client by Status: `クライアント名`(グループ)×`GBCCountry__c`(詳細、ネスト)の2階層ツリーマップ。
- **配色はTableauの`<style-rule element='mark'><encoding attr='color' ... palette='blue_10_0'/>`のような内蔵パレット名からグラデーションを復元**: Won=blue系、Lost=red系、Pipeline=gray系という統一ルールをtwbから発見(3ページとも共通)。内蔵パレットはtwbに正確なHEXが保存されないため、ColorBrewerの標準Blues/Reds/Greysに基づく3点(最小/中央/最大)の近似HEXをPower BIの「色の彩度」書式に設定する方式で対応、正樹さんの目視確認でOKをもらえた。
- Pipeline合計は既知の理由(ライブデータの自然なドリフト、[[powerbi_jci_pitch_status_chart]]に既記載)によりTableauのpptxスナップショット値と一致しないことを再確認、バグではないと回答済み。

**次回**: Competitive Analysisページの凡例並び順(WON/LOST独立ソート)のリベンジが最優先の持ち越しタスク。それ以外は正樹さんからの新規依頼待ち。
