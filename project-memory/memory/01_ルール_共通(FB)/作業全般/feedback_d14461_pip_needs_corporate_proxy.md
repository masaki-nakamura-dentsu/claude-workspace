---
name: feedback-d14461-pip-needs-corporate-proxy
description: 会社Mac(d14461)ではpip installがpypi.orgに直接到達できずタイムアウトする — 社内プロキシ経由が必要
metadata:
  type: feedback
---

会社Mac(d14461)からの`pip install`はデフォルトでpypi.orgに直接到達できず、
`connect timeout`で失敗する(会社ネットワークが直接の外部HTTPS接続を許可していない)。

**Why:** 2026-08-25、[[gbc_intelligence_engine_project]]のwebapp用venv構築時に発生。
`~/.npmrc`に既に社内プロキシ設定(`http://proxy1.dentsu.co.jp:8080`)があり、これを
`http_proxy`/`https_proxy`環境変数に設定して`pip install`をやり直したら解決した。

**How to apply:** d14461上で新規に`pip install`(venv作成後の依存関係インストール等)が
原因不明にタイムアウトする時は、まず`export https_proxy=http://proxy1.dentsu.co.jp:8080
http_proxy=http://proxy1.dentsu.co.jp:8080`を設定してから再実行する。npm/他のパッケージ
マネージャでも同様の問題が起きる可能性がある(`~/.npmrc`が既にこのプロキシで動いている
実績あり)。個人Mac(ICPTokyo2022)ではこの制約は無い(通常のホームネットワーク接続のため)。

**追記 2026-10-05**: プロキシ環境変数を付けてローカル連携のあるスクリプト(共有ボットブラウザCDP localhost:9226 等)を動かす時は、必ず `no_proxy=localhost,127.0.0.1` も併せて設定する。付け忘れるとlocalhost通信までプロキシに流れ「ブラウザ起動失敗」と誤判定される(週次AIダイジェスト手動実行で実際に発生)。
