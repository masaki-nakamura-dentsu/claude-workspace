# PowerBI GBCダッシュボード「Salesforce更新日」JST化修正

## 2026-09-01T18:15:00+09:00
Status: done
What: 「Salesforce更新日」カードが深夜2時台などUTC時刻で表示される問題を調査、`Salesforceデータ取得日時`クエリが`DateTime.LocalNow()`(サーバー側ローカル=UTC)を使っていたことが原因と特定。`DateTimeZone.UtcNow()`→`SwitchZone(9)`でJST変換するM式に修正するも、最初「中身を丸ごと置き換え」を指示した際に元のテーブル化/列名構造を把握せずに提示したため`Missing_References`エラー発生。姉妹クエリ`CAS実績データ最終更新日時`の実コード(`#table`でテキスト列化するパターン)を教えてもらい、同じ構造で再構成したM式で解決。「Salesforce更新日: 2026/9/18 10:35」のように正しくJST表示されることを確認済み。
Next: —
