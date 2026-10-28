---
name: claude_routines_local_automation_gap
description: Claudeのルーティン(スケジュール済みクラウドエージェント)機能は、今運用中のローカル定期実行タスクのほぼ代替にならない理由
metadata: 
  node_type: memory
  type: reference
  originSessionId: a7447f04-ba4c-46e6-8692-fcd453a667c8
  modified: 2026-08-31T23:41:19.333Z
---

2026-09-01、「今のlaunchd等の定期実行タスクをClaudeルーティン機能で置き換えられるか」と聞かれ調査。関連: [[automation_schedule_overview]]

## 結論
ルーティンはAnthropicのクラウド上で動く完全に独立したセッション(CCR)で、以下に一切アクセスできない:
- ローカルファイル(Dropbox上のExcel/pptx等)
- 共有ボットブラウザ(Playwright、port 9226経由)
- PowerBI Desktop
- launchd常駐プロセス・デーモン
- Outlook/Teamsのローカルエクスポート(JSONL)

かつ最短実行間隔が1時間のため、20分おきポーリング系(syncdaemon等)はそもそも仕様上合わない。

## 移行候補になりうるもの
GitHubリポジトリ上のコード作業、またはclaude.aiのMCPコネクタ経由で完結する外部API限定タスク(ローカルファイル・ローカルアプリ操作が不要なもの)。[[automation_schedule_overview]]記載の現行タスクにはこれに該当するものが今のところない。

## How to apply
「ルーティンで自動化できないか」と聞かれたら、まずそのタスクがローカルファイル/アプリ/常駐プロセスに依存するか確認する。依存するなら基本的に対象外と即答してよい(再調査不要)。依存しない完全クラウド完結タスクが新たに出てきた場合のみ、ルーティン化を具体的に検討する。
