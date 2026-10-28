---
name: line_cli_attempt_paused
description: LINE用CLI開発の検討経緯。公式アカウント作成の手間がネックで中止、雛形コードのみ残存
metadata: 
  node_type: memory
  type: project
  originSessionId: 3f03cb6f-1bc5-43fa-b02a-fc5146b6795e
  modified: 2026-08-09T01:12:40.363Z
---

2026-08-09、LINEのCLI開発を依頼されたが中止した。

検討の流れ:
- 個人LINEアカウントの自動操作は非公式手段になり規約リスクがあるため除外
- LINE公式アカウント(Messaging API)方式に絞り、送信/ブロードキャスト/クォータ確認のCLIを実装
  - `~/Scripts/line_cli/line_cli.py`(stdlib urllibのみ、依存なし)
  - `~/bin/line` ラッパー、`~/.zshenv` に `PATH="$HOME/bin:$PATH"` を追加済み(これは汎用設定なので他のCLI用にも有効、消す必要なし)
- しかし公式アカウント(LINE Developersでのチャネル作成)自体が「作るのが面倒」という理由で中止に

**Why**: 公式アカウント作成はブラウザでの手動登録が必要で自動化できず、ユーザーがその手間を避けたいと判断した。機能不足や規約懸念が理由ではない。

**How to apply**: 今後LINE連携の話が出たら、まず「公式アカウント作成の手間」がネックだったことを踏まえ、(a) 既に用意済みの雛形コードがあることを伝える、(b) 再度公式アカウント方式を無条件に提案しない — 代替手段([[teams_self_chat_autopost]]の拡張など)も選択肢として出す。
