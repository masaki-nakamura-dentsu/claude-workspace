---
name: openclaw_setup
description: OpenClaw(セルフホストAIエージェント)を個人Macに試験導入した際の構成・手順・現状
metadata: 
  node_type: memory
  type: project
  originSessionId: 11969c26-513a-4d99-85fc-3a5bc0a1b632
  modified: 2026-09-15T04:51:17.303Z
---

2026-09-15、個人Mac(ICPTokyo2022)にOpenClaw(チャット経由でPCを自律操作するOSSエージェント、開発者Peter Steinberger)を試験導入した。

**インストール**
- ワンライナー: `curl -fsSL https://openclaw.ai/install.sh | bash`(npm経由、Homebrewでnode更新)
- バイナリ: `/Users/maxakisan/.npm-global/bin/openclaw`
- バージョン: 2026.9.4

**LLMバックエンド**
- Anthropic、認証方式は「Claude CLI再利用」(`claude -p`、APIキー別発行ではない)
- モデル: `anthropic/claude-opus-5`
- 重要: この方式は普段のClaude Code/Claude Pro・Maxの利用上限を消費する共有プール。本格運用する場合はAnthropic APIキーへの切替を推奨(公式ドキュメントも共有・本番用途にはAPIキー推奨と明記)

**チャットチャネル: Telegram**
- ボット: `@masakinakamura_bot`(BotFatherで作成、審査なし・即時発行)
- `openclaw channels add --channel telegram --token <token>` で登録済み
- ペアリング承認済み: telegramUserId `7396445172`(username: maxakisan)
- LINEは公式プラグインあり(`@openclaw/line`)だが、[[line_cli_attempt_paused]]と同じくLINE Developers公式アカウントの手動作成が必須+今回は外部公開Webhook URL(ngrok等)も追加で必要なため、初回は見送りTelegramを選択

**現状(2026-09-15時点)**
- ゲートウェイはbackground service化していない(`openclaw gateway install`未実行)。`openclaw onboard`実行時にフォアグラウンドでゲートウェイが起動する仕様
- ユーザーが手動でCtrl+Cして停止済み。再開するには同じターミナルで`openclaw gateway run`を実行する必要がある
- Control UIダッシュボード: `http://127.0.0.1:18789/`

**Why**: 「軽く試したい」という要望だったため、APIキー新規発行やLINE公式アカウント作成など手間のかかる経路は避け、最短でチャット操作を体験できる構成(Claude CLI再利用+Telegram)を選んだ。

**How to apply**: 次回このMacでOpenClawの話が出たら、まずこのファイルで現在の構成(バックエンド・チャネル・稼働状態)を確認してから対応する。本格運用に移行する話が出たらAPIキー移行とゲートウェイのbackground service化(`openclaw gateway install`)を提案する。
