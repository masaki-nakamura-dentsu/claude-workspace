# GBC Intelligence Engine / LaunchPad — 会社Mac(d14461)でのローカルサーバー起動

## 2026-08-25T16:00:00+09:00 (会社Mac d14461)
Status: done
What: 「前回作ったローカルサーバー立ち上げて」との依頼を受け、[[gbc_intelligence_engine_project]]のwebapp(2026-08-23に個人Macで作成)を会社Macで起動した。
- webappフォルダはDropbox経由で同期済みを確認: `中村正樹/Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/GBC-Knowledge/webapp/`(app.py, static/, requirements.txt一式あり)
- DB(`output/knowledge_index.db`, 32MB)も同フォルダ内に存在確認済み
- 会社Mac側にはvenvが無かったため`~/gbc_knowledge_venv_d14461`を新規作成(Dropbox外、[[feedback_venv_outside_dropbox_sync]]の罠回避、個人Mac側`~/gbc_knowledge_venv`とは別物)
- 初回`pip install`はpypi.orgへの直接到達がタイムアウトして失敗(会社MacはPyPIに直接出られない)。`~/.npmrc`にあった社内プロキシ`http://proxy1.dentsu.co.jp:8080`をhttp_proxy/https_proxy環境変数に設定して再実行し、`fastapi 0.141.1`/`uvicorn 0.52.4`のインストールに成功
- `cd webapp && nohup ~/gbc_knowledge_venv_d14461/bin/uvicorn app:app --port 8800 &`でサーバー起動、`/api/search?q=ANA`・`/api/toolkit`とも正常応答を確認(ログ: `~/gbc_knowledge_logs_d14461_server.log`)。ブラウザでの`http://localhost:8800`目視確認は未実施(ユーザーはチャットを閉じた状態)
Next: ユーザーがブラウザで`http://localhost:8800`にアクセスして表示確認。IT部門へのホスティング先確認・本番デプロイは[[gbc_intelligence_engine_project]]記載の通り未着手のまま継続課題。
