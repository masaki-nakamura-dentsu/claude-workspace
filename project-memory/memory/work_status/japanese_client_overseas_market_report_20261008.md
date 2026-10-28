# 日系クライアント別 海外拠点数字 (2026-10-08)
Status: done
- RF&P元データ(25ACTUAL/26BUDGET/RF1/RF2 + P8)から日系52社分を生成、各クライアント別数字フォルダへ保存
- Toyota画像と照合: 25実績/RF1/RF2一致、予算±0.3%、Canada RF1/RF2のみ画像側レート違い(-10%)
- launchd com.nakamura.clientmarketreport(月木9:15)で更新検知→再生成→Teams通知
- 2026-10-08 ユーザーがフィードバック待ちでセッション終了。未回答の確認事項: (1) Canadaの換算レートを画像に合わせ約237円/£にするか (2) 関連会社(Lexus/Uniqlo等)・リスト外日系(Daikin/TDK等)を対象に加えるか。回答が来たら config.json を修正して --force で再生成(同日なら _01 連番)。
