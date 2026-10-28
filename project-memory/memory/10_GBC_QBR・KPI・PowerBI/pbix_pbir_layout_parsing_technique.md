---
name: pbix-pbir-layout-parsing-technique
description: PowerBIの新形式(PBIR)pbixファイルはzip展開+標準jsonだけでページ/スライサー/同期グループ構成を直読みできる技法
metadata:
  type: reference
  originSessionId: (2026-09-08セッション)
  modified: 2026-09-09T00:38:18.546Z
---

# 何のための技法か

[[qbr_powerbi_tableau_verification_20260906]]記載の`pbixray`はDataModel側(テーブル/DAXメジュー/Power Query M式)しか見えず、レポートのページ構成・視覚化のフィールド束縛・スライサーの同期設定は分からない。ページ・視覚化構成を調べたい時はこちらを併用する。[[powerbi_cover_dashboard_project]]の確度スライサー連動問題(★OVERVIEW vs ★予算達成トラッキング)の原因特定に使用、有効性を確認済み。

# 前提: 新形式(PBIR)かどうかの判別

`.pbix`は常にzipアーカイブ(`unzip -l`で中身が見える)。旧形式は`Report/Layout`という単一のバイナリ(UTF-16)ファイルにレポート全体の定義が入っているが、新しい「拡張レポート形式(PBIR)」では`Report/definition/pages/`配下にページ・視覚化ごとの素のJSONファイルとして分割されている。zip展開後に`Report/definition/pages/`ディレクトリが存在するかどうかで判別できる。

# 使い方(PBIR形式の場合)

```bash
unzip -o -q "/path/to/file.pbix" -d 展開先
```

- `Report/definition/pages/pages.json` — ページの並び順・アクティブページ
- `Report/definition/pages/<GUID>/page.json` — 各ページの`displayName`(GUID→表示名の対応表はこれで作る)
- `Report/definition/pages/<GUID>/visuals/<GUID>/visual.json` — 個々の視覚化。主に見るキー:
  - `visual.visualType`(例: `"slicer"`, `"lineStackedColumnComboChart"`)
  - `visual.query.queryState` — どのテーブル/列/メジューを使っているか(`Column`/`Measure`の`Expression.SourceRef.Entity`+`Property`を再帰的に拾えば視覚化が参照する全フィールドが取れる)
  - `visual.objects.general.filter` — その視覚化自体にかかっている値フィルター(例: スライサーの選択肢からnull/特定値を除外する設定)
  - `filterConfig.filters` — 視覚化レベルのフィルターペイン設定(上記とは別枠で存在することがある)
  - `visual.syncGroup` (`{"groupName": ..., "fieldChanges": true, "filterChanges": true}`) — **同期スライサーのグループ名そのもの**。これが無ければそのスライサーはどの同期グループにも属していない

Pythonで一括処理する場合、`json.load()`で素直にパースできる(UTF-8のプレーンJSON、旧形式のようなUTF-16デコードや独自バイナリ形式の考慮は不要)。

# 分かったこと・注意点

- 同期グループは「グループ名」がキーであり、同じ`groupName`を持つスライサーが自動的に同期対象になる(GUIDやページ名では紐付かない)。同じ非接続テーブル・同じ列を参照していても`syncGroup`が無ければ同期されない。
- 1ファイル内で複数の同期グループが独立して運用されているのが普通(このプロジェクトでは指標/地域/市場/事業区分/JCI関連の複数グループが既に稼働中)。
- この技法は読み取り専用の調査に使う想定。JSONを直接書き換えて再zipする運用は未検証(Power BI Desktopが期待する内部整合性を壊すリスクがあるため)、実際の変更はPower BI Desktopのスライサー編集/同期スライサーペインのGUI操作で行うこと。
- **列/メジューのリネーム計画を作る時の注意([[kgikpi_cas_uriage_soritsuki_rename]]で実害発生、2026-09-09)**: 対象語(例:「売上総利益」)を含む生列を`model.schema`で検索する際、最初に見つかったテーブルだけで満足せず、**必ずフィルタ無しで全テーブル横断検索する**こと。同じ列名が複数の独立したテーブルに別々の物理列として存在するケース(例: `Raw YTD`と`CAS予算`の両方に独立した`売上総利益`列があった)を見落とすと、片方だけリネームした状態で新しい列名を参照する数式を貼り付けてしまい「列が見つからない」エラーで手戻りになる。`sch[sch['ColumnName'].str.contains(target, na=False)]`のように`TableName`条件を付けずに実行するのが正しい手順。
- **メジュー/列のリネームは視覚化のフィールドウェル参照を自動更新しない([[kgikpi_cas_uriage_soritsuki_rename]]で実害発生、2026-09-09)**: Power BI Serviceでメジュー名や列名をリネームすると、DAX数式内の`[旧名]`参照は(状況によっては)追随することがあるが、**カード・テーブル・チャート等の視覚化がフィールドウェルに直接置いている参照は追随せず、旧名称のまま⚠️マーク付きで壊れる**(「1つ以上のフィールドに問題があります」というエラー表示になる)。したがってリネーム計画を立てる際は、DAX数式内の参照箇所の洗い出し(`dax_measures`の`Expression`を検索)だけでなく、**視覚化のフィールドウェル参照も別カテゴリとして必ず洗い出す**こと。後者は本技法(PBIRのvisual.json直読み)で`"Property":"対象語.*"`を正規表現検索すれば、どのページのどの視覚化(GUID・visualType)が対象フィールドを使っているか完全に一覧化できる——実際に効果を確認済み。両方のリストを事前に用意してから作業を始めるのが正しい順序で、後から壊れて発覚するのは手戻りが大きい。
