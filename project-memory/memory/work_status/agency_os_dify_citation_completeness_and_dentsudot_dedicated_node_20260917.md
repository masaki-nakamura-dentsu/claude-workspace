# Agency OS Dify版: 引用完全性ルール構造化+dentsudot専用データセット/ノード追加(20260917)

## 2026-09-17T10:20:00+09:00
Status: done
What: 前段の内部ファイル名/外部システム誘導バグ修正([[work_status/agency_os_dify_offloading_filename_leak_fix_20260917]])を中村さんが実機再テストしたところ、新バグを発見:
CASE_ID 13014(GM Korea、`cases_apac_01.md`に実在・SALESFORCE_URL付き)が回答内で
「(ナレッジ記録より)」「出典URL未掲載」に格下げされていた(6件リストの4番目、
1〜2番目は正しく引用)。中村さんから「指示文/出力が長くなって省略されているなら
構造改善も検討して」と要望があり、単純なルール追記ではなく構造的対応を実施:

1. **プロンプト圧縮・統合**: 「Equally binding failure modes」の7項目
   (Fabrication/Withholding/Bare-hit reporting/Citation degradation/
   Meaningless citation/Deferral/Offloading)を4項目
   (Fabrication/Citation completeness/Withholding/Offloading)に統合し重複除去。
   「confirmed DATE:」形式の事例注釈は全てchangelog.mdへ退避(モデルが毎ターン
   読む必要がない情報)。SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.md全てで
   実施、grep差分で機能欠落なしを確認。
2. **構造的対策(exhortationでなく強制フォーマット)**: ルールA(引用表示)に
   「CASE系レコード3件以上は表形式(案件名/CASE_ID/担当者/出典URL列)必須」を
   追加。表形式なら空のURLセルが目視で一目瞭然になり、段落形式のように後半項目
   だけ引用が雑になる現象を構造的に防止する狙い。
3. 結果: SKILL_Dify.mdは278行/41.8KB→277行/40.3KB(新規追加分を差し引いても
   実質圧縮)。SKILL.mdも同様に整理。

並行して中村さんがDify本体側の実装(下記②)を実施し、途中2回のバグを発見・
やり取りで修正:
- ①SYSTEM prompt貼替+公開: 中村さんが実施、公開確認済み(「公開済み ◯分前」)。
- ②dentsudot専用データセット+ノード追加: 新規データセット
  (自動命名「dentsudot_thought_...」、2ファイル・埋め込み完了)は前セッションで
  作成済み。中村さんが知識検索3/4を複製する形で「知識検索 DENTSUDOT」ノードを
  追加しコード実行ノードに接続。**1回目の修正でreturn文にのみ`(e or [])`を
  追加し、関数シグネチャ`def main(a,b,c,d)`にe引数を追加し忘れ**(NameErrorで
  ワークフロー全体が落ちるバグ)を実機確認で発見・指摘、中村さんが
  `def main(a: list, b: list, c: list, d: list, e: list) -> dict:
  return {"result": (a or []) + (b or []) + (c or []) + (d or []) + (e or [])}`
  に修正。最終確認済み(入力変数5件が知識検索/2/3/4/dentsudotのresultに正しく
  対応、reload後の実際のコード内容で確認)。

**教訓**: Difyのワークフローエディタでブラウザタブを長時間掴んだままリロード
無しで繰り返しinnerText抽出すると、実際の編集(ユーザーによる別操作含む)後も
古いレンダリング内容がスタックした状態で返ってくることがある(自動保存/公開の
タイムスタンプが同じ値のまま何度readしても変わらない、が明確なサイン)。
`page.reload()`を挟むと最新状態を正しく取得できた——長時間セッションでの
状態確認は疑わしければまずreloadする。

Next: 中村さんに実機で「海外の自動車業界事例を教えて」等を再テストしてもらい、
(1)表形式で複数CASEが出るか、(2)dentsudot事例が今度は拾われるか、(3)後半項目の
引用が省略されないか、を確認する。Salesforce新規案件→Agency OS自動起動
(未着手の別TODO)は今回も対象外。
