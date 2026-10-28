---
name: japanese_client_overseas_market_report
description: 日系クライアント別「海外市場(国)・エンティティ・領域別」数字(25実績/26予算/RF1/RF2,千円)の自動生成。元データ・換算レート・launchd設定・照合結果
metadata:
  type: project
---
2026-10-08 依頼(海外拠点の扱い検討用)。書式=市場|25年実績|26年予算|26年RF1|26年RF2 の表(Toyota CI画像 ~/Downloads/画像.jpeg)。

- 元データ: `Work/共用_ビジネス開発室/02. IM数字関連/RF & P` の `<年>RF|PF/<年> <版> Category Management.xlsx` 明細シート(Ret Details SAC等, Industry/Brand/Client/Market/CI/TT, £'000通期) + 最新 `<年>P/Pn <年> Japan client report.xlsx` の Ret CI/TT(YTD, 市場×Brand×Segment)。RF=見込, P=実績。
- 画像の数字 = **Client Income(£千)×版別円レート**。逆算レート: 25実績/26予算 197.271、RF1 211.4195、RF2 212.6939 (`config.json` fx_jpy_per_gbp)。予算は市場ごとに±0.3%ズレ(現地通貨建て予算レートと思われる)、Canadaだけ画像のRF1/RF2が約237円で換算されており当方より+11%。新版(RF3/ACTUAL)のレートは未登録→直近レートで仮換算しTeams通知で要更新と出る。
- 対象: Japan client reportのClient List(67社, Dentsu Inc除外)。表記ゆれalias(Shiseido/Suzuki/Suntory/Dai-ichi/Rakuten)。Lexus・Honda India・Uniqlo・Maruti・Beam Suntory等の関連会社は**含めていない**(社内リスト準拠)。Daikin/TDK/SMFG等リスト外日系も未対象。
- 領域区分(参考): Media=Carat/Dentsu X/iProspect/Amnet/Posterscope/Story Lab/Vizeum/Other Media、CXM=Merkle等、Creative=DBA/dentsuMB/360i/Isobar/MKTG/Tag等。
- スクリプト: `~/ClientMarketReport/build_client_market_report.py` (+config.json, state.json)。`--force`/`--no-notify`。0byteプレースホルダは `open -g -a Preview` で実体化(成功確認済)。
- 出力: `GBC_数字管理・業務管理(QBR)/各クライアント別数字/<Client>/<Client>_海外拠点別数字_YYYYMMDD.xlsx`(シート: 市場別CI千円/£千, 市場×領域, 市場×エンティティ, 当年YTD実績£千, 注記) + `_日系クライアント一覧_YYYYMMDD.xlsx`。初回52社。
- launchd `com.nakamura.clientmarketreport` 毎週月・木 9:15、元ファイル(パス+mtime)変化時のみ再生成→Teams Webhook通知。エラー時もWebhook通知。月次Pレポート更新でも再生成される。

**保留中(2026-10-08時点)**: 依頼者のフィードバック待ち。確認事項=Canada換算レート(画像は約237円/£)／関連会社・リスト外日系を対象に含めるか。再開時はこの2点の回答を確認し、config.json(fx_jpy_per_gbp / client_alias / japanese_clients)を更新して `python3 -W ignore ~/ClientMarketReport/build_client_market_report.py --force` を実行。
