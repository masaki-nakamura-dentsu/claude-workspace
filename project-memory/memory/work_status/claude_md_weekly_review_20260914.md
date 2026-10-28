---
name: claude-md-weekly-review-20260914
description: 2026-09-14、CLAUDE.md週次自動レビューの実施記録。ブラウザ自動操作関連で2件追記。
metadata:
  node_type: memory
  type: project
  modified: 2026-09-14T00:00:00Z
---

Status: done

## やったこと
1. マーカーファイル(`.../MemoryWeeklyReview/state/claude_md_review_marker.txt`)を読み、前回マーカー
   2026-09-06T23:40:25Z(UTC)以降に更新された`.jsonl`を対象に抽出(BSD `find -newermt`は
   `2026-09-06T23:40:25Z`形式のISO8601"T"/"Z"を解釈しないため、`"2026-09-06 23:40:25"`形式に変換して対応)。
2. 対象22セッション(サブエージェントjsonlは除外)から`jq`でユーザー発話のみ抽出し、躓き系キーワード
   (エラー・失敗・止まって・教えて等)でスクリーニングした上で、ヒットしたファイルと主要な長文ファイル
   (Dify Agency OS作業の2セッションが特に長大)を目視確認。
3. 各セッションの属するプロジェクトメモリ(`MEMORY.md`)を確認し、すでにカバー済みの話題を除外。
   - `4bbd5008`(2026-09-09頃、Mac間タスクキューの実行前許可要求)、`5b42416d`(会社Mac指示のWindows展開依頼)は
     いずれもCLAUDE.mdの2026-09-08/09-11の既存Standing rule(Mac間タスクキュー許可制)で既にカバー済みと確認、除外。
   - `2e00fac4`(QBR/PowerBIのDAX貼り付けエラー3回連続)は、既存のper-projectメモリ
     `feedback_dax_one_measure_per_code_block.md`/`feedback_dax_syntax_self_check.md`で既にカバー済みと判断、
     プロジェクト固有の話題でもあるためCLAUDE.md化は見送り。

## CLAUDE.mdへ追記した2件
1. **GUI自動操作は着手前に許可確認(スクリーンショット多用が見込まれる場合)**: 2026-09-12のDify「Agency OS」
   ワークフロー編集セッション(`34768629...`)で、ユーザーが「トークンたくさん使っていますか？」→
   「今回のあなたの動きはトークンの消費が激しすぎます」→明示的な事前許可要求、と3段階にわたり同種の指摘を
   繰り返した。同日のper-projectメモリ`feedback_reduce_browser_automation_tokens.md`で「ルール格上げ(重要)」
   として既に一般化されていたが、CLAUDE.md本体には未反映だったため追記。
2. **ブラウザ自動操作のフォーカス奪取禁止(再発)**: 2026-08-07にper-projectメモリ
   `feedback_browser_automation_no_focus_steal.md`として既に確立していたルールだが、2026-09-08の
   セッション(`45a120a6...`)で「いまだ私の作業を邪魔するのです。特にキーボードで文字を打っているときに
   あなたが使っているブラウザがアクティブになり、文字が打てません」と同種の苦情が再発。CLAUDE.md本体には
   一度も反映されていなかったため、他プロジェクトでの再発防止も兼ねて追記。

編集前にCLAUDE.mdを`.claude-sync/Scripts/MemoryWeeklyReview/claude_md_backups/20260914/CLAUDE.md`にバックアップ済み。
既存のルールの削除・書き換えは行っていない(末尾に新規2件を追加のみ)。

## 見送った候補
- Agency OS(ChatGPT版/Dify版)のQUICKモード出力品質問題(`fb529540`, `34768629`): URL非表示・内部用語の
  そのまま出力など。プロダクト(Agency OS Skill)自体の実装課題であり、Claude Codeの作業スタイルの話ではないため
  CLAUDE.mdの対象外と判断。プロジェクト側メモリ(`ai_agency_team_feedback_*`等)で追跡されている前提。
- TimeTree/Outlookカレンダー同期デバッグ(`1b5aa1b8`)は単発の技術デバッグであり、パターン化の材料としては薄いため見送り。

## 結論
新規2件をCLAUDE.mdへ追記。マーカーファイルは`2026-09-13T23:38:56Z`(UTC)に更新済み。

## 次回このメモリに触れるとき確認すること
- 今回追記した2件(GUI自動操作の事前許可確認/フォーカス奪取禁止)が、今後のセッションで本当に順守されているか
  (特にフォーカス奪取は2026-08-07に一度ルール化されたのに再発した実績があるため、再々発していないか要注意)。
