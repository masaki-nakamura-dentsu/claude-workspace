# Outlookカレンダー登録用メモ(メモリ週次レビュー・手動実施リマインダー)

headlessの`claude -p`はmemory/ディレクトリへの書き込みが「sensitive file」として一律ブロックされ、
自動化(launchd)では実処理(重複統合)が毎回失敗する。対話セッションでは書き込めるため、
このリマインダーで毎週手動実施に切り替える。

## 登録する予定の内容

- **タイトル**: メモリ週次レビュー(手動実施)
- **繰り返し**: 毎週、月曜日
- **時刻**: 8:30〜8:45(既存のlaunchd起動時刻に合わせる。時間帯は自由に調整可)
- **本文にコピペする依頼文**:

```
Claude Codeに以下を依頼する:

「今週のメモリ週次レビューを手動で実施して」

対象: ~/.claude/projects/*/memory 配下(このMacに存在する全プロジェクト)
ルール:
- 重複統合の結果、完全に別ファイルへ吸収された元ファイルのみ削除可
- 老朽化・完了済みを理由にした削除は禁止
- 統合後はMEMORY.mdのインデックスも更新、work_status/に実施記録を残す
- MEMORY.md(20KB超)とCLAUDE.md(8KB超)はサイズを点検し、超えていれば圧縮する(review_*_template.md参照)
詳細手順は per-project memory `memory_weekly_review_automation.md` および
このフォルダの `review_prompt_template.md` を参照。
```

## 背景

2026-08-24、会社Mac(d14461)にもlaunchd登録を行ったが、個人Mac側で先に自動発火した
今週分のログを確認したところ、バックアップのみ成功し実際の重複統合・書き込みは
全て「sensitive file」としてブロックされていたことが判明。settings.json側で
permissions.allow(Edit(...)ルール)を追加しても解消せず、`--dangerously-skip-permissions`
を使わない限り回避不可と判断。ユーザーはそのトレードオフを避け、手動運用に切り替えることを選択。
