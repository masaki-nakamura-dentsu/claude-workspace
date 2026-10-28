---
name: powerbi-jci-pitch-status-chart
description: TableauのJapan Clientピッチ状況ダッシュボード(QBRブック内の複数ページ)をPower BIに移植するプロジェクト。スライド2(3チャート+サマリー+9スライサー+ALL ITEM+明細)は2026-08-31完成。2026-09-01にCompetitive Analysis(Q1 (5))・Service/Market/Client by Status(Q8/Q8(2)/Q8(3))の4ページを追加。Competitive Analysisの凡例並び順のみ未解決で保留。
metadata: 
  node_type: memory
  type: project
  originSessionId: cea55476-8755-4d86-971e-97d9cf86fcd8
  modified: 2026-09-05T10:25:30.914Z
---

# 背景

2026-08-27、[[powerbi_gbc_dashboard_current_state]]の保留タスク(棒グラフ→テーブル切替)を一旦保留にし、代わりに新規着手。目標はTableauの以下の出力をPower BIで再現すること:

- 元Tableauファイル: `GBC戦略企画部_GBC設定実績・見込/QBR作成/7. QBR_Japan Client ピッチ状況.twb`(OneDrive)
- 目標ビジュアル(スライド2): `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Tableau書き出しデータ/7. QBR_Japan Client ピッチ状況_20260814.pptx`
- 元データ更新マニュアル: `(Manual) GBC QBR_Tableau20260401.docx`の「8. 元データの更新(日系ターンアラウンド)」節。Salesforceレポート「APAC Pitch - List All_v1.31」(`00OfP00000Cq0rRUAR`)がソース。
- 正樹さんの指示: Salesforceと直結した`GBC__c`ベースの集計にする(旧Excel手動プロセスは踏襲しない)。

**注意**: twb内の該当ダッシュボード(story-point名`Q1`)は既に削除済みで、実体は残っていない。計算ロジックは同workbook内に残る計算フィールド定義(`JCI Win # %`等の関連ワークシート群)から復元した。

# 目標ビジュアルの構成(スライド2、画像で確認済み)

タイトル「Japan Client ピッチ状況(グループ売総、FY26に結果判明案件)」、サブタイトル「All Pitches - YTD」

1. **左: Won/Lost Status by Pitch Types** — 積み上げ棒グラフ。X軸=Won/Lost/Pipeline、積み上げ=ピッチ種別(Offensive/Defensive)、値=Group売総(GBP)合計。バー上に合計値、セグメント内に内訳値とラベル表示。
2. **中央: Net Win (Off&Won-Def&Lost)** — 積み上げ棒グラフ1本。積み上げ=部門バケット(Others/Media/Brand/Integrated、下から順)、値=Net Winメジュー。上部に`TTL=3,814`表示。
3. **右: Net Win Vs. HDY** — 積み上げ棒グラフ1本。積み上げ=HDY相手かどうか(VS NOT-HDY/VS HDY)、値=Net Win。
4. **下部: サマリーテーブル** — 列: Net Win (GBP) / # of Pitches / Won / # of Pipelines / Won Pitch # %。

# Tableau計算フィールドのロジック(twbから抽出済み、正確)

**フェーズ判定(Won/Lost/Pipeline/Cancelled)** — 元名`ﾌｪｰｽﾞ/Phase (2)`:
```
IF [フェーズ/Phase] = "完了･成立 (Complete)" OR [フェーズ/Phase] = "進行中/受注済み (Order Received)"
THEN "Won"
ELSEIF [フェーズ/Phase] = "完了･不成立 (Incomplete)" AND [獲得グループ/Winning Group] <> "なし(競合中止)/None (Pitch cancelled)"
THEN "Lost"
ELSEIF [フェーズ/Phase] = "完了･不成立 (Incomplete)" AND [獲得グループ/Winning Group] = "なし(競合中止)/None (Pitch cancelled)"
THEN "Cancelled"
ELSEIF [フェーズ/Phase] = "仕掛中/未受注 (In Progress)"
THEN "Pipeline"
END
```

**Net Win**:
```
SUM(
  IF [ピッチ種別/Pitch Type] = "Offensive" AND [Phase(2)] = "Won" THEN [Group売総/Revenue (GBP)]
  ELSEIF [ピッチ種別/Pitch Type] = "Defensive" AND [Phase(2)] = "Lost" THEN -[Group売総/Revenue (GBP)]
  ELSE 0
  END
)
```
(Offensive×勝ち=純増、Defensive×負け=純減。Offensive×負け/Defensive×勝ちは0円扱い=中央グラフには影響しない)

**HDY判定**:
```
IF CONTAINS([競合グループ/Competitor's Group], "博報堂/Hakuhodo") THEN "Y" ELSE "N" END
```

**部門バケット(Others/Media/Brand/Integrated)** — 元名`提供ｻｰﾋﾞｽ/Services to Provide(2)`:
```
IF TRIM(IFNULL([提供サービス/Services to Provide], '')) = '' THEN NULL
ELSEIF CONTAINS(...,'Creative') AND (Media Planning/Buying Traditional or Digitalのいずれか含む) THEN 'Integrated'
ELSEIF CONTAINS(...,'Creative') THEN 'Brand'
ELSEIF (Media Planning/Buying Traditional or Digitalのいずれか含む) THEN 'Media'
ELSE 'Others'
END
```
(`提供サービス/Services to Provide`は複数値を含みうる文字列列、CONTAINSで判定=マルチセレクトpicklistの可能性大)

**その他の集計メジュー(すべてPhase(2)ベースの単純SUM/IF)**: # of Pitch Completed(Won+Lost)、# of Won/Lost Pitch、GBP of Won/Lost Pitch、# of Pipelines、Won Pitch # %、Won Pitch Amount % など。パターンはすべて`SUM(IF [Phase(2)]="X" THEN [値] ELSE 0 END)`。

# Salesforceフィールド名マッピング(要確認・未確認混在)

[[powerbi_migration_gbc_dashboard]]で既に確定済み(`GBC__c`オブジェクト、マスタ行の項目):

| ラベル | API名 | 状態 |
|---|---|---|
| 部署名/Dept. | `GBCorgChoice__c` | 確定済み |
| 地域/Region | `GBCArea__c` | 確定済み |
| 市場/Market | `GBCCountry__c` | 確定済み |
| 事業(業務)区分/Business category | `GBCJU__c` | 確定済み |
| クライアント/Client | `GBCClient__c`(→Account) | 確定済み |
| 商流/Business flow | `GBCCommercial_distribution__c` | 確定済み |
| フェーズ/Phase | `GBCPhase__c` | 確定済み |
| 活動項目/Activity Items | `GBCMiddleClass__c` | 確定済み(ただし「提供サービス/Services to Provide」とは別物の可能性あり、要区別) |
| 関係会社/Partner companies | `GBCOutsideCom__c` | 確定済み |
| GBC貢献度 | `GBCContributionPercent__c` | 確定済み(0-100スケール、/100必要) |
| GM確認 | `GBCGMConfirmed__c` | 確定済み |
| Group売総(JPY) | `GBCGross__c` | 確定済み(ただしJCIは**GBP建て**の別フィールドの可能性、要確認) |

**2026-08-27追加確認済み**(正樹さんがSalesforce Object Manager「GBC案件/Items」→項目とリレーションをxlsxエクスポートして提供、全147フィールドを確認):

| ラベル | API名 | 型 | 備考 |
|---|---|---|---|
| ピッチ種別/Pitch Type | `GBCCompetitivePitch__c` | 選択リスト(単一) | |
| GBC案件/Items: 重複/Dup | `GBCConnection__c` | 参照関係(GBC__c自己参照) | 条件は空欄判定 |
| JP Turnaround Project | `GBC_JP_APAC_Turnaround_PJ__c` | チェックボックス | |
| 責任者/Owner | `GBCResponsiblePerson__c` | 参照関係(従業員) | **確定(2026-08-27)**: 参照先オブジェクトは`Employee__c`(表示ラベル「従業員」)。`GBCParentResponsiblePerson__c`は月別子レコード専用でマスタ行では全行NULL、使用不可と判明。`Employee__c`と`Id`結合し`Name`列を展開して名前を取得する。**`Name`列は「姓 和雄」のように姓名の間に半角スペースが入る形式**(元のSF Reportフィルタ画面の表示「小池和雄」はスペースなし表示だったが実データはスペースあり、要注意)。`CustomName__c`(姓名)列は全行NULLだった(未使用フィールドの模様)。 |
| 獲得グループ/Winning Group | `GBCWinningAgencyGroup__c` | 選択リスト(複数選択) | |
| 提供サービス/Services to Provide | `GBCServicestoProvide__c` | 選択リスト(複数選択) | |
| 提供サービス/Services to Provide(2) | `GBCServicestoProvide2__c` | 数式(テキスト) | **Salesforce側に既にOthers/Media/Brand/Integratedのバケット化ロジックが実装済みの可能性大**(Tableau計算フィールドと同名)。ただし式の中身は未確認のため、今回はTableauから復元した式をPower Query側で独自実装する方針(検証可能性を優先) |
| 競合グループ/Competitor's Group | `GBCCompetitorsGroup__c` | 選択リスト(複数選択) | |
| ピッチ実施日/Pitch Date | `GBCPitchDate__c` | 日付 | |
| Group売総/Revenue (GBP) | `GBCGrossGBP__c` | 数値(15,0) | JPY版`GBCGross__c`とは別フィールド、確認済み |
| ピッチ結果判明日/Pitch Close Date | `GBCPitchCloseDate__c` | 日付 | **2026-08-31発見・確定**。twbファイル(グレップで直接確認)とObject Manager書き出しxlsxの両方で照合済み。標準Opportunity.CloseDateと同様、Won/Lost確定分は実際の結果判明日、Pipeline(未決着)分は決着予定日が入っている模様(この列がnullでない行のみを対象にすると目標データと一致することで裏付け)。目標スライドのサブタイトル「FY26に結果判明案件」はこの列のYEAR=2026フィルタに対応 |

原本の全147フィールド一覧(xlsx)は正樹さんのDownloadsから以下に移動・保存済み: `Work/GBC_戦略企画部/GBC_数字管理・業務管理(QBR)/Salesforce書き出し/GBC__c_項目とリレーション_20260827.xlsx`(今後も他のGBC__c関連作業で再利用する想定、要更新時はこのファイルを直接上書き)。

# Salesforceレポートのフィルタ条件(スクリーンショットで確認済み、AND結合)

1. 部署名/Dept. 次の文字列と一致する: AP1部, AP2部, BD部, SP1部, SP2部
2. GBC案件/Items: レコードタイプ 次の文字列と一致しない: (GBC)年度月別明細 (=マスタ行のみ)
3. ピッチ種別/Pitch Type 次の文字列と一致する: Defensive, Offensive, Unknown
4. 商流/Business flow 次の値を含まない: Out-In
5. 地域/Region 次の文字列を含む: APAC, EMEA, Americas, Global
6. GBC案件/Items: 重複/Dup 次の文字列と一致する: ""(空欄)
7. JP Turnaround Project 次の文字列と一致する: True
8. 責任者/Owner 次の文字列を含む: 小池和雄, 宮川武, 新保泰史
9. フェーズ/Phase 次の文字列と一致する: 仕掛中/未受注 (In Progress), 完了・不成立 (Incomplete), 完了・成立 (Complete), 進行中/受注済み (Order Received), ""(空欄)
10. 獲得グループ/Winning Group 次の値を含まない: なし(競合中止)/None (Pitch cancelled)

条件10が「Cancelled」を全件除外するため、実質的にPhase(2)の"Cancelled"分岐はこのレポート内では出現しない(データセット自体から除外済み)。

# 次回の進め方

1. ~~正樹さんに未確認フィールドのAPI名をSalesforce Object Managerで確認してもらう~~ → 完了(2026-08-27)。
2. 下記のPower Query M式(新規クエリ`JCI_Pitch_Base`)をPower BI Desktopで実行し、フィルタ後の行数・合計値を目標値(下記「検証用の目標値」)と突合。
3. 一致すれば3チャート+サマリーテーブルを新規ページに構築。

## Power Query M(新規クエリ`JCI_Pitch_Base`、正樹さんが貼り付け・実行)

既存`SF案件リスト`と同じ接続パターン(RecordType結合で子レコード除外)を踏襲。**責任者/Owner条件は`Employee__c`結合方式で確定・検証済み**(2026-08-27、実機で最終ステップまで到達確認済み)。

```
let
    ソース = Salesforce.Data("https://login.salesforce.com/", [ApiVersion=48]),
    GBC__c = ソース{[Name="GBC__c"]}[Data],
    RecordType = ソース{[Name="RecordType"]}[Data],
    Employee__c = ソース{[Name="Employee__c"]}[Data],
    列を選択 = Table.SelectColumns(GBC__c, {
        "Id", "Name", "RecordTypeId",
        "GBCorgChoice__c", "GBCCompetitivePitch__c", "GBCCommercial_distribution__c",
        "GBCArea__c", "GBCConnection__c", "GBC_JP_APAC_Turnaround_PJ__c",
        "GBCResponsiblePerson__c",
        "GBCPhase__c", "GBCWinningAgencyGroup__c", "GBCCompetitorsGroup__c",
        "GBCServicestoProvide__c", "GBCPitchDate__c", "GBCGrossGBP__c"
    }),
    重複を削除 = Table.Distinct(列を選択, {"Id"}),
    RecordTypeと結合 = Table.NestedJoin(重複を削除, {"RecordTypeId"}, RecordType, {"Id"}, "レコードタイプ情報", JoinKind.LeftOuter),
    レコードタイプ名の展開 = Table.ExpandTableColumn(RecordTypeと結合, "レコードタイプ情報", {"Name"}, {"レコードタイプ名"}),
    条件2_子レコード除外 = Table.SelectRows(レコードタイプ名の展開, each [レコードタイプ名] <> "年度月別明細（GBC）"),
    条件1_部署名 = Table.SelectRows(条件2_子レコード除外, each List.Contains({"AP1部","AP2部","BD部","SP1部","SP2部"}, [GBCorgChoice__c])),
    条件3_ピッチ種別 = Table.SelectRows(条件1_部署名, each List.Contains({"Defensive","Offensive","Unknown"}, [GBCCompetitivePitch__c])),
    条件4_商流 = Table.SelectRows(条件3_ピッチ種別, each [GBCCommercial_distribution__c] = null or not Text.Contains([GBCCommercial_distribution__c], "Out-In")),
    条件5_地域 = Table.SelectRows(条件4_商流, each [GBCArea__c] <> null and (Text.Contains([GBCArea__c],"APAC") or Text.Contains([GBCArea__c],"EMEA") or Text.Contains([GBCArea__c],"Americas") or Text.Contains([GBCArea__c],"Global"))),
    条件6_重複Dup = Table.SelectRows(条件5_地域, each [GBCConnection__c] = null),
    条件7_Turnaround = Table.SelectRows(条件6_重複Dup, each [GBC_JP_APAC_Turnaround_PJ__c] = true),
    Employeeと結合 = Table.NestedJoin(条件7_Turnaround, {"GBCResponsiblePerson__c"}, Employee__c, {"Id"}, "責任者情報", JoinKind.LeftOuter),
    責任者名の展開 = Table.ExpandTableColumn(Employeeと結合, "責任者情報", {"Name"}, {"責任者名"}),
    条件8_責任者 = Table.SelectRows(責任者名の展開, each [責任者名] <> null and (Text.Contains([責任者名],"小池 和雄") or Text.Contains([責任者名],"宮川 武") or Text.Contains([責任者名],"新保 泰史"))),
    条件9_フェーズ = Table.SelectRows(条件8_責任者, each [GBCPhase__c] = null or Text.Contains([GBCPhase__c], "(In Progress)") or Text.Contains([GBCPhase__c], "(Incomplete)") or Text.Contains([GBCPhase__c], "(Complete)") or Text.Contains([GBCPhase__c], "(Order Received)")),
    条件10_獲得グループ = Table.SelectRows(条件9_フェーズ, each [GBCWinningAgencyGroup__c] = null or not Text.Contains([GBCWinningAgencyGroup__c], "Pitch cancelled")),
    列追加_フェーズ判定 = Table.AddColumn(条件10_獲得グループ, "Phase2", each
        let
            phase = [GBCPhase__c],
            wg = [GBCWinningAgencyGroup__c],
            isCancelled = wg <> null and Text.Contains(wg, "Pitch cancelled")
        in
            if Text.Contains(phase, "(Complete)") or Text.Contains(phase, "(Order Received)") then "Won"
            else if Text.Contains(phase, "(Incomplete)") and not isCancelled then "Lost"
            else if Text.Contains(phase, "(Incomplete)") and isCancelled then "Cancelled"
            else if Text.Contains(phase, "(In Progress)") then "Pipeline"
            else null, type text),
    列追加_NetWin = Table.AddColumn(列追加_フェーズ判定, "NetWin", each
        if [GBCCompetitivePitch__c] = "Offensive" and [Phase2] = "Won" then [GBCGrossGBP__c]
        else if [GBCCompetitivePitch__c] = "Defensive" and [Phase2] = "Lost" then -[GBCGrossGBP__c]
        else 0, type number),
    列追加_HDY = Table.AddColumn(列追加_NetWin, "HDY", each
        if [GBCCompetitorsGroup__c] <> null and Text.Contains([GBCCompetitorsGroup__c], "博報堂/Hakuhodo") then "Y" else "N", type text),
    列追加_部門バケット = Table.AddColumn(列追加_HDY, "PracticeBucket", each
        let
            s = [GBCServicestoProvide__c],
            hasCreative = s <> null and Text.Contains(s, "Creative"),
            hasMedia = s <> null and (Text.Contains(s,"Media Planning (Traditional)") or Text.Contains(s,"Media Buying (Traditional)") or Text.Contains(s,"Media Planning (Digital)") or Text.Contains(s,"Media Buying (Digital)"))
        in
            if s = null or Text.Trim(s) = "" then null
            else if hasCreative and hasMedia then "Integrated"
            else if hasCreative then "Brand"
            else if hasMedia then "Media"
            else "Others", type text),
    列追加_ofRecord = Table.AddColumn(列追加_部門バケット, "# of Record", each 1, Int64.Type)
in
    列追加_ofRecord
```

## ステータス: 完成(2026-08-31、目標値と完全一致確認済み)

3チャート+サマリーテーブルとも構築完了。サマリーテーブルの実測値が目標と完全一致: Net Win(GBP)=3,814,085 / # of Pitches=176 / # of Won=91 / # of Pipelines=36 / Won Pitch # %=65.0%。詳しい解決の経緯(フェーズ値の実データ判明・FY26日付フィルタの発見)は[[work_status/powerbi_jci_pitch_status_chart_20260827]]の2026-08-31セッション節を参照。

**2026-08-31同日中に全て完了**: 体裁調整・9スライサー・ALL ITEM+明細ページまで完成。以下は完了後の最終状態。

## 追加機能(2026-08-31、同日後半で完成)

**9スライサー**: `決着年`/`決着四半期`/`決着月`/`クライアント名`/`地域_Bridge_JCI[地域]`/`市場_Bridge_JCI[市場]`/`GBCCompetitivePitch__c`(ピッチ種別)/`提供サービス_Bridge_JCI[提供サービス]`/`ピッチスコープ_Bridge_JCI[ピッチスコープ]`/`勝因敗因_Bridge_JCI[勝因敗因]`/`Phase2`(Win/Lost/Pipeline)。

**フィールド追加**(`JCI_Pitch_Base`): `GBCCountry__c`(市場)、`GBCClient__c`→Account結合の`クライアント名`、`GBCScopeOfPitch__c`(ピッチスコープ)、`GBC_Cause__c`(勝因敗因)、`CreatedDate`、`GBCGross__c`(Group売総JPY)、`BP_Support__c`(BPサポート)。計算列: `決着四半期`/`決着月`(GBCPitchCloseDate__c基準)、`実施年`/`実施四半期`(GBCPitchDate__c基準、決着日ベースとは別物)、`案件名表示`(前月作成なら"● "付与、`DateTime.LocalNow()`基準で動的判定)。

**ブリッジテーブル5本**(複数選択リスト用、`JCI_Pitch_Base`参照): `地域_Bridge_JCI`/`市場_Bridge_JCI`/`提供サービス_Bridge_JCI`/`ピッチスコープ_Bridge_JCI`/`勝因敗因_Bridge_JCI`。いずれも`Id`+対象列→セミコロン分割→展開→トリム(null安全化必須、`勝因敗因`はnull行有りで一度エラー発生)。リレーションシップは各ブリッジ`[Id]`↔`JCI_Pitch_Base[Id]`、**一対多(ブリッジ側が多)+クロスフィルター両方向**(既存の市場_Bridge等と違い`JCI_Pitch_Base`の`Id`はユニークなので多対多不要、と正樹さんに確認の上で決定)。

**`Phase2一覧`ディメンションテーブル(新規)**: 手動テーブル(`#table`で Won/Lost/Pipeline+並び順の3行)。左チャートの軸をこちらに差し替え、`JCI_Pitch_Base`と一対多(単一方向)でリレーション、ビジュアルの「空の値を表示」をONにすることで、スライサーで絞ってWon/Lost/Pipelineのいずれかが0件になっても軸に表示され続けるようにした。**「空の値を表示」はPower BI Web版では書式ペインになく、軸/凡例フィールドの「∨」ドロップダウンメニューにある**(要注意ポイント)。

**`ALL ITEM+`明細ページ(新規)**: Tableauのworksheet XML(`<worksheet name='ALL ITEM+'>`の`<rows>`タグ)を直接grepして列順序・フィルタ・ソートを正確に復元。テーブルビジュアル1つ、列順=案件名表示/クライアント名/地域/市場/ピッチ種別/PracticeBucket/実施年/実施四半期/競合グループ/Phase2/BPサポート/Group売総GBP/Group売総JPY。フィルタ: PracticeBucketがnullでない、GBCGrossGBP__c≥1。ソート: GBP降順。`実施年`列は集計方法を「集計しない」に変更必要(数値列なので放置すると自動SUMされ無意味な合計が出る、実際に発生・修正済み)。

**残タスク(いずれも急ぎでない、正樹さんの意向で後回し)**:
1. ページ体裁: タイトル「Japan Client ピッチ状況(グループ売総、FY26に結果判明案件)」・サブタイトル「All Pitches - YTD」の追加、ページ名変更 → **正樹さんが独自に対応済み(2026-08-31)**。
2. `ALL ITEM+`テーブルの列見出しを内部フィールド名(`GBCArea__c`等)から日本語ラベルに変更(任意、後回し可)。

## 検証用の目標値(pptxスライド2、2026-08-14時点、確認済み)

- Won/Lost/Pipeline(Group売総GBP'000、ピッチ種別内訳): Won=6,945(Offensive 4,380+Defensive 2,514の端数)/Lost=10,165(Offensive 9,590+Defensive)/Pipeline=1,251(Offensive 975+Defensive)
- Net Win 合計=3,814(Others 1,244/Media 386/Brand 1,711/Integrated 472)
- Net Win Vs. HDY: VS HDY=1,992/VS NOT-HDY=1,822(合計3,814)
- サマリーテーブル: Net Win(GBP)=3,814,085 / # of Pitches=176(Won+Lost+Pipelineの全件数) / Won=91 / # of Pipelines=36 / Won Pitch # %=65.0%(=Won÷(Won+Lost)、Pipelineは分母に含まない)
- **注意**: Pipelineの金額(GBP'000)はpptx時点で1,251だったが、2026-08-31のライブデータでは1,314とやや差異あり。件数(Won91/Lost49/Pipeline36)は完全一致。ライブ接続なので自然なデータドリフトと判断(バグではない)。

## `JCI_Pitch_Base` 最終版M式(2026-08-31時点、実機で全数値一致確認済み)

```
let
    ソース = Salesforce.Data("https://login.salesforce.com/", [ApiVersion=48]),
    GBC__c = ソース{[Name="GBC__c"]}[Data],
    RecordType = ソース{[Name="RecordType"]}[Data],
    Employee__c = ソース{[Name="Employee__c"]}[Data],
    列を選択 = Table.SelectColumns(GBC__c, {
        "Id", "Name", "RecordTypeId",
        "GBCorgChoice__c", "GBCCompetitivePitch__c", "GBCCommercial_distribution__c",
        "GBCArea__c", "GBCConnection__c", "GBC_JP_APAC_Turnaround_PJ__c",
        "GBCResponsiblePerson__c",
        "GBCPhase__c", "GBCWinningAgencyGroup__c", "GBCCompetitorsGroup__c",
        "GBCServicestoProvide__c", "GBCPitchDate__c", "GBCPitchCloseDate__c", "GBCGrossGBP__c"
    }),
    重複を削除 = Table.Distinct(列を選択, {"Id"}),
    RecordTypeと結合 = Table.NestedJoin(重複を削除, {"RecordTypeId"}, RecordType, {"Id"}, "レコードタイプ情報", JoinKind.LeftOuter),
    レコードタイプ名の展開 = Table.ExpandTableColumn(RecordTypeと結合, "レコードタイプ情報", {"Name"}, {"レコードタイプ名"}),
    条件2_子レコード除外 = Table.SelectRows(レコードタイプ名の展開, each [レコードタイプ名] <> "年度月別明細（GBC）"),
    条件1_部署名 = Table.SelectRows(条件2_子レコード除外, each List.Contains({"AP1部","AP2部","BD部","SP1部","SP2部"}, [GBCorgChoice__c])),
    条件3_ピッチ種別 = Table.SelectRows(条件1_部署名, each List.Contains({"Defensive","Offensive","Unknown"}, [GBCCompetitivePitch__c])),
    条件4_商流 = Table.SelectRows(条件3_ピッチ種別, each [GBCCommercial_distribution__c] = null or not Text.Contains([GBCCommercial_distribution__c], "Out-In")),
    条件5_地域 = Table.SelectRows(条件4_商流, each [GBCArea__c] <> null and (Text.Contains([GBCArea__c],"APAC") or Text.Contains([GBCArea__c],"EMEA") or Text.Contains([GBCArea__c],"Americas") or Text.Contains([GBCArea__c],"Global"))),
    条件6_重複Dup = Table.SelectRows(条件5_地域, each [GBCConnection__c] = null),
    条件7_Turnaround = Table.SelectRows(条件6_重複Dup, each [GBC_JP_APAC_Turnaround_PJ__c] = true),
    Employeeと結合 = Table.NestedJoin(条件7_Turnaround, {"GBCResponsiblePerson__c"}, Employee__c, {"Id"}, "責任者情報", JoinKind.LeftOuter),
    責任者名の展開 = Table.ExpandTableColumn(Employeeと結合, "責任者情報", {"Name"}, {"責任者名"}),
    条件8_責任者 = Table.SelectRows(責任者名の展開, each [責任者名] <> null and (Text.Contains([責任者名],"小池 和雄") or Text.Contains([責任者名],"宮川 武") or Text.Contains([責任者名],"新保 泰史"))),
    条件9_フェーズ = Table.SelectRows(条件8_責任者, each [GBCPhase__c] = null
        or [GBCPhase__c] = "New（新規）"
        or [GBCPhase__c] = "Complete（完了・成立）"
        or [GBCPhase__c] = "Incomplete（完了・不成立）"
        or [GBCPhase__c] = "進行中/受注済み (Order Received)"),
    条件10_獲得グループ = Table.SelectRows(条件9_フェーズ, each [GBCWinningAgencyGroup__c] = null or not Text.Contains([GBCWinningAgencyGroup__c], "Pitch cancelled")),
    条件11_結果判明日あり = Table.SelectRows(条件10_獲得グループ, each [GBCPitchCloseDate__c] <> null),
    列追加_決着年 = Table.AddColumn(条件11_結果判明日あり, "決着年", each Date.Year([GBCPitchCloseDate__c]), Int64.Type),
    列追加_フェーズ判定 = Table.AddColumn(列追加_決着年, "Phase2", each
        let
            phase = [GBCPhase__c],
            wg = [GBCWinningAgencyGroup__c],
            isCancelled = wg <> null and Text.Contains(wg, "Pitch cancelled")
        in
            if phase = "Complete（完了・成立）" or phase = "進行中/受注済み (Order Received)" then "Won"
            else if phase = "Incomplete（完了・不成立）" and not isCancelled then "Lost"
            else if phase = "Incomplete（完了・不成立）" and isCancelled then "Cancelled"
            else if phase = "New（新規）" then "Pipeline"
            else null, type text),
    列追加_Phase2並び順 = Table.AddColumn(列追加_フェーズ判定, "Phase2並び順", each
        if [Phase2] = "Won" then 1
        else if [Phase2] = "Lost" then 2
        else if [Phase2] = "Pipeline" then 3
        else if [Phase2] = "Cancelled" then 4
        else 5, Int64.Type),
    列追加_NetWin = Table.AddColumn(列追加_Phase2並び順, "NetWin", each
        if [GBCCompetitivePitch__c] = "Offensive" and [Phase2] = "Won" then [GBCGrossGBP__c]
        else if [GBCCompetitivePitch__c] = "Defensive" and [Phase2] = "Lost" then -[GBCGrossGBP__c]
        else 0, type number),
    列追加_ピッチ種別並び順 = Table.AddColumn(列追加_NetWin, "ピッチ種別並び順", each
        if [GBCCompetitivePitch__c] = "Offensive" then 1
        else if [GBCCompetitivePitch__c] = "Defensive" then 2
        else if [GBCCompetitivePitch__c] = "Unknown" then 3
        else 4, Int64.Type),
    列追加_HDY = Table.AddColumn(列追加_ピッチ種別並び順, "HDY", each
        if [GBCCompetitorsGroup__c] <> null and Text.Contains([GBCCompetitorsGroup__c], "博報堂/Hakuhodo") then "VS HDY" else "VS NON-HDY", type text),
    列追加_HDY並び順 = Table.AddColumn(列追加_HDY, "HDY並び順", each
        if [HDY] = "VS NON-HDY" then 1 else 2, Int64.Type),
    列追加_部門バケット = Table.AddColumn(列追加_HDY並び順, "PracticeBucket", each
        let
            s = [GBCServicestoProvide__c],
            hasCreative = s <> null and Text.Contains(s, "Creative"),
            hasMedia = s <> null and (Text.Contains(s,"Media Planning (Traditional)") or Text.Contains(s,"Media Buying (Traditional)") or Text.Contains(s,"Media Planning (Digital)") or Text.Contains(s,"Media Buying (Digital)"))
        in
            if s = null or Text.Trim(s) = "" then null
            else if hasCreative and hasMedia then "Integrated"
            else if hasCreative then "Brand"
            else if hasMedia then "Media"
            else "Others", type text),
    列追加_部門バケット順 = Table.AddColumn(列追加_部門バケット, "PracticeBucket並び順", each
        if [PracticeBucket] = "Others" then 1
        else if [PracticeBucket] = "Media" then 2
        else if [PracticeBucket] = "Brand" then 3
        else if [PracticeBucket] = "Integrated" then 4
        else 5, Int64.Type),
    列追加_ofRecord = Table.AddColumn(列追加_部門バケット順, "# of Record", each 1, Int64.Type)
in
    列追加_ofRecord
```

## DAXメジュー(最終版、`JCI_Pitch_Base`テーブルに追加)

```
Net Win (GBP) = SUM('JCI_Pitch_Base'[NetWin])
# of Pitches = COUNTROWS('JCI_Pitch_Base')
# of Won = COUNTROWS(FILTER('JCI_Pitch_Base', 'JCI_Pitch_Base'[Phase2]="Won"))
# of Lost = COUNTROWS(FILTER('JCI_Pitch_Base', 'JCI_Pitch_Base'[Phase2]="Lost"))
# of Pipelines = COUNTROWS(FILTER('JCI_Pitch_Base', 'JCI_Pitch_Base'[Phase2]="Pipeline"))
Won Pitch # % = DIVIDE([# of Won], [# of Won] + [# of Lost])
Group売総_GBP合計 = SUM('JCI_Pitch_Base'[GBCGrossGBP__c])
```

**注意**: `# of Pitches`は全件数(Won+Lost+Pipeline)、`Won Pitch # %`の分母はWon+Lostのみ(Pipeline除外)。この2つの指標定義の違いに一度気づかず旧DAX案でズレが発生したので、再実装時は要注意。

## チャート構築(最終版、3チャート+サマリーテーブル、`GBC数字管理レポート`ワークスペース内の新規ページ)

1. **左(積み上げ棒)**: 軸=`Phase2`(ビジュアルフィルタでWon/Lost/Pipelineのみ、並べ替えの基準列=`Phase2並び順`)、凡例=`GBCCompetitivePitch__c`(並べ替えの基準列=`ピッチ種別並び順`、下から Offensive→Defensive→Unknown)、値=`Group売総_GBP合計`(表示単位=千)。データの色: Defensive=`#4e79a7`/Offensive=`#e15759`/Unknown=`#f28e2b`。
2. **中央(積み上げ棒1本)**: 軸=空(フィールドなし)、凡例=`PracticeBucket`(並べ替えの基準列=`PracticeBucket並び順`、下から Others→Media→Brand→Integrated)、値=`Net Win (GBP)`。データの色: Integrated=`#4e79a7`/Others=`#76b7b2`/Media=`#e15759`/Brand=`#f28e2b`。
3. **右(積み上げ棒1本)**: 軸=空(フィールドなし)、凡例=`HDY`(並べ替えの基準列=`HDY並び順`、値は"VS HDY"/"VS NON-HDY"に変更済み、下から VS NON-HDY→VS HDY)、値=`Net Win (GBP)`。データの色: VS NON-HDY=`#c7c7c7`/VS HDY=`#edc948`。
4. **下部テーブル**: `Net Win (GBP)`/`# of Pitches`/`# of Won`/`# of Pipelines`/`Won Pitch # %`をテーブルビジュアルの列に追加(ディメンション無しで自動的に1行になる)。`Won Pitch # %`は表示単位をパーセントに変更。

## ハマった罠まとめ(次回同種作業の教訓、2026-08-27〜31)

1. **半角中黒(･)と全角中黒(・)の不一致**: twbから抽出した文字列は半角カナの中黒(U+FF65)を含んでいたが、Salesforce実データは全角(U+30FB)。**さらに2026-08-31判明**: 中黒だけでなく、英語注記を囲む括弧自体が全角(`Complete（完了・成立）`)で、かつ日英の並び順もTableauの想定(日本語→英語)と逆(英語→日本語)だった。**加えて`仕掛中/未受注 (In Progress)`という値自体がSalesforce側で`New（新規）`に変更されていた**(ラベル変更、Tableau作成時から乖離)。**確立した対策**: 複合文字列の判定は絶対に推測でハードコードせず、`Table.Distinct`+`"【" & [列] & "】"`で実データを一字一句確認してから完全一致(`=`)で書く。
2. **`Text.Contains(null, ...)`をif条件に使うとエラーになる**: null判定は`let`で先に`isXxx = 列 <> null and Text.Contains(列, "y")`のように独立変数化してから使う。
3. **件数が想定の約2倍になる不具合**: 原因はSalesforceレポートの明示的フィルタカード(10個)以外に、レポート画面の別セクション(またはTableau側フィルタパネル)に**日付範囲フィルタ**が別途存在していたこと。今回は目標スライドのサブタイトル「FY26に結果判明案件」がヒントになった。**教訓**: 件数/合計が想定より明らかに多い場合、フィルタ条件の抽出元(スクショ等)に日付・年度条件が漏れていないか、タイトル/サブタイトルの文言も手がかりに疑うこと。
4. **Web版DAXエディタは複数メジューの一括貼り付け不可**: 「名前=式」を複数行まとめて1つの数式バーに貼ると構文エラー。メジューは1つずつ「新しいメジュー」で追加する必要がある。
5. **列の「並べ替えの基準列」設定だけでは軸の並び順が変わらないことがある**: ビジュアル自体が「値で並べ替え」になっている場合、列側の設定より優先される。ビジュアル右上の「...」または並べ替えアイコンから、並べ替え対象を軸のフィールド名(値ではなく)に明示的に変更する必要がある。
6. **ビジュアルの値のテキストを個別に変更したい場合**: Power BI Desktopには「値の名前を変更」機能があるが、**Power BI Service(Web版)の通常の右クリックメニューには出てこない**(コピー/共有/アラート/テーブルとして表示/グループ化/選択解除/集計/新しいビジュアル計算のみ)。Web版で個別ラベルを変えたい場合は、Power Query側で元データの値自体を書き換えるのが確実(この時は色設定・並べ替え列の再設定が必要になる点に注意)。
7. **「積み上げ棒グラフ1本」を作るには軸を空にする**: 軸にフィールドを入れると通常のクラスター棒グラフ(カテゴリごとに別の棒)になってしまう。1本の棒の中に凡例で積み上げたい場合は、軸フィールドを空のままにし、凡例にだけフィールドを入れる。

## Web版Power BIでのデバッグ手法(汎用、他クエリでも応用可)

Web版Power Query(Power BI Service)は「適用されたステップ」の行数表示が`99+`止まりで、実際の行数・列内の値の全体像を確認できない。有効な手法: 確認したい内容ごとに**専用の小さい診断クエリ**(`検証_◯◯確認`のような名前)を都度作り、`Table.SelectColumns`で見たい列だけに絞り、`Table.Distinct`や`Table.Group`で集計してから見る。文字列の完全一致条件を書く前に、対象列の値を`Table.Distinct`で確認し、`"【" & [列] & "】"`のように記号で囲んで全角/半角・前後の見えない文字を判別するのが有効。

Tableauの元データソースの色・フィルタ設定を確認したい場合、twbファイルはXML形式なので、Bashで直接grep/Pythonでパースして`<encoding attr='color' ...>`や`<filter ...>`ブロックを抽出するのが、Tableauアプリを開くより速く正確(2026-08-31、色パレットとPitch Close Dateフィルタの発見に実際に使用)。

# 2026-09-01追加分: 競合グループスライサー + Competitive Analysis(Q1 (5)) + Q8/Q8(2)/Q8(3)ツリーマップ3ページ

## 競合グループスライサー(既存2ページ「JCI_All_Pitches(グラフ)」「JCI_All_Pitches(内訳)」に追加)

`競合グループ_Bridge_JCI`(既存5ブリッジと同パターン、`GBCCompetitorsGroup__c`セミコロン分割)を新設。リレーションシップは他ブリッジ同様「多対一 (*:1)、テーブルから=競合グループ_Bridge_JCI」。

## Competitive Analysis(Tableau story-point「Q1 (5)」、タイトル「Competitive Analysis - YTD」)

WON/LOST別、競合グループごとの積み上げ棒グラフ2本(軸なし・凡例のみの単一積み上げ棒)。

**重大な罠**: スライサー用の`競合グループ_Bridge_JCI`(分解済み)をそのまま凡例に流用すると、複数競合が併記された案件の売上が二重カウントされ合計が水増しされる(WON 6,945K→9,456K、LOST 10,165K→18,703K)。詳細と対策は[[feedback_tableau_multiselect_no_split_for_charts]]参照。対策として`競合グループ_Dim_JCI`(分解しない、生の`GBCCompetitorsGroup__c`ごとにWON/LOST合計・順位を集計)を新設し解決:

```
let
    ソース = JCI_Pitch_Base,
    列を選択 = Table.SelectColumns(ソース, {"GBCCompetitorsGroup__c", "Phase2", "GBCGrossGBP__c"}),
    null置換 = Table.TransformColumns(列を選択, {{"GBCCompetitorsGroup__c", each if _ = null then "(未設定)" else _, type text}}),
    グループ別集計 = Table.Group(null置換, {"GBCCompetitorsGroup__c"}, {
        {"WON合計", each List.Sum(Table.SelectRows(_, each [Phase2]="Won")[GBCGrossGBP__c]), type number},
        {"LOST合計", each List.Sum(Table.SelectRows(_, each [Phase2]="Lost")[GBCGrossGBP__c]), type number}
    }),
    WON順位追加 = Table.AddIndexColumn(Table.Sort(グループ別集計, {{"WON合計", Order.Descending}}), "WON売上順位", 1, 1, Int64.Type),
    LOST順位追加 = Table.AddIndexColumn(Table.Sort(WON順位追加, {{"LOST合計", Order.Descending}}), "LOST売上順位", 1, 1, Int64.Type),
    表示列追加 = Table.AddColumn(LOST順位追加, "競合グループ", each [GBCCompetitorsGroup__c], type text),
    LOST表示用列追加 = Table.AddColumn(表示列追加, "競合グループ_LOST表示用", each [GBCCompetitorsGroup__c], type text)
in
    LOST表示用列追加
```

`JCI_Pitch_Base`側にDAX計算列`競合グループ_表示 = IF(ISBLANK('JCI_Pitch_Base'[GBCCompetitorsGroup__c]), "(未設定)", 'JCI_Pitch_Base'[GBCCompetitorsGroup__c])`を追加し、`競合グループ_Dim_JCI[GBCCompetitorsGroup__c]`(1側)↔`JCI_Pitch_Base[競合グループ_表示]`(多側)、一対多(1:*)・単一方向でリレーション(空欄がリレーションキーになれないエラーの回避、スライサー用途ではないため単一方向で十分)。

メジュー: `Won Revenue (GBP)`/`Lost Revenue (GBP)` = `CALCULATE(SUM('JCI_Pitch_Base'[GBCGrossGBP__c]), 'JCI_Pitch_Base'[Phase2]="Won"/"Lost")`。

色: twbのcustom color encodingから単独競合名ごとのHEXを抽出し両チャートで統一(博報堂/Hakuhodo=`#a0cbe8`、WPP=`#b6992d`、Publicis=`#59a14f`等、[[work_status/powerbi_jci_pitch_status_chart_20260827]]2026-09-01節に詳細)。

**未解決(保留、次回リベンジ)**: WON/LOSTそれぞれ独立して金額降順に積み上げたいが、`WON売上順位`/`LOST売上順位`(rank列、`並べ替えの基準列`に指定)+ LOST用に列を複製(`競合グループ_LOST表示用`)する方式を試みても、LOST側の凡例順序がWON側の順位につられたような不可解な並びになり未解決。ブラウザキャッシュのリロードや列の削除→再追加も試したが改善せず。原因不明。

## Q8/Q8(2)/Q8(3): Service/Market/Client by Status(3ページとも共通パターン)

Won/Lost/Pipeline別の3枚組ツリーマップ+下部にWon/Lost/Pipeline合計カード。新規メジュー`Pipeline Revenue (GBP) = CALCULATE(SUM('JCI_Pitch_Base'[GBCGrossGBP__c]), 'JCI_Pitch_Base'[Phase2]="Pipeline")`。

| ページ | Tableau名 | グループ | 詳細(ネスト) |
|---|---|---|---|
| JCI_All_Pitches(サービス構成) | Q8 | `PracticeBucket` | なし |
| JCI_All_Pitches(マーケット構成) | Q8 (2) | `JCI_Pitch_Base[GBCCountry__c]`(市場、生の値、Bridge不使用) | なし |
| JCI_All_Pitches(クライアント構成) | Q8 (3) | `クライアント名` | `GBCCountry__c`(市場、生の値) |

市場もセミコロン区切りの複数選択リストだが、Tableau側も分解せず1カテゴリとして扱っているため([[feedback_tableau_multiselect_no_split_for_charts]])、`市場_Bridge_JCI`は使わず`GBCCountry__c`を直接使用(競合グループの教訓を活かし最初から正しい実装、問題なく一致)。

**配色**: twbの`<style-rule element='mark'><encoding attr='color' ... palette='blue_10_0'/>`のような内蔵パレット名から、Won=blue系/Lost=red系/Pipeline=gray系という統一ルールを発見(3ページとも共通)。内蔵パレットはtwbに正確なHEXが保存されないため、ColorBrewer標準Blues/Reds/Greysに基づく近似HEXをPower BIの「色の彩度」(最小/中央/最大の3点)に設定:
- Won: 最小`#DEEBF7`/中央`#6BAED6`/最大`#08306B`
- Lost: 最小`#FEE0D2`/中央`#FB6A4A`/最大`#99000D`
- Pipeline: 最小`#D9D9D9`/中央`#969696`/最大`#252525`

Power BIのツリーマップは既定で値の大きい順に自動配置されるため、円グラフ/棒グラフで必要だった並べ替えの基準列トリックは不要。

Pipeline合計はTableauのpptxスナップショット値と数百K円ズレるが、ライブデータの自然なドリフト(既知、バグではない)。

## 解決済み(2026-09-05): 勝敗(Won/Lost)スライサーが反応しない問題

正樹さんから、`サービス構成`/`マーケット構成`/`クライアント構成`/`競合分析`の4ページで「勝敗」スライサーを動かしても表示が変わらない(Wonを選んでもWonだけにならない)との指摘。

**確定した原因と対応**: これらのページは元々「Won/Lost(/Pipeline)を3枚の別々のツリーマップ/棒グラフとして横並びに常時表示する」設計(各ビジュアルが個別に`Phase2="Won"`等の固定フィルターを持つ)。正樹さんに確認したところ、**この3枚固定表示のままで良い**とのことで、そもそも不要だった「勝敗」スライサーを4ページとも削除して解決(バグ修正ではなく、意図と合っていなかったUI要素の削除)。
