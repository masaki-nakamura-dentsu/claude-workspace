---
name: claude-pulse-dashboard-setup
description: 知り合いが使っていた使用状況ダッシュボード(セッション/トークン/連続日数/ヒートマップ)の正体と個人Macでの起動方法
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9859f8de-a914-4501-a31f-f1e101da27ea
  modified: 2026-08-31T22:33:29.562Z
---

2026-09-01、知り合いが表示していたClaude Codeの使用状況ダッシュボード(セッション数・メッセージ数・合計トークン数・アクティブ日数・連続日数・ピーク時間・よく使うモデル・GitHub風ヒートマップ・「The Lord of the Ringsの約X倍のトークン」という比較文)の正体を特定: OSSツール **Claude Pulse** (`pulse-for-claude-code`, GitHub: nikitadoudikov/claude-pulse)。

**起動方法**: `npx pulse-for-claude-code` でグローバルインストール不要で起動。`http://127.0.0.1:4317` でローカルWebダッシュボードが立つ。`~/.claude/projects`配下のJSONLセッションログを読み取り専用で解析するのみで外部送信なし。要件はNode 18+(個人Macはv24.14.1で確認済み)。

個人Mac(ICPTokyo2022)で2026-09-01に動作確認済み。会社Mac(d14461)でも2026-09-11に動作確認済み(Node v24.13.1、`npx pulse-for-claude-code`をバックグラウンド実行→`http://127.0.0.1:4317`が200応答→`open`でブラウザ起動、まで問題なし)。停止は`ctrl+c`または`pkill -f pulse-for-claude-code`。

**Why**: 外部npmパッケージの実行は自動モードのclassifierでブロックされ、ユーザーへの実行許可確認が必要だった(未検証サードパーティコードの実行のため)。
**How to apply**: 再度このダッシュボードを見たいと言われたら、上記コマンドで再起動するだけでよい。両Mac(個人・会社)とも動作確認済みなので、どちらで頼まれても同じ手順でよい。
