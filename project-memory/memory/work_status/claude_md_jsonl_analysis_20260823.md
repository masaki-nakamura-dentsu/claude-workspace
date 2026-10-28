---
name: claude-md-jsonl-analysis-20260823
description: 2026-08-23、セッションJSONL履歴分析→CLAUDE.md改良、および毎週月曜自動実行の仕組み構築
metadata: 
  node_type: memory
  type: project
  originSessionId: 3a502140-90c5-40df-90dc-68e1b6335ff0
  modified: 2026-08-22T22:07:05.352Z
---

Status: done

## やったこと
1. ユーザー依頼で、このMacの過去74セッション(2026-07-23〜08-23、約700MB)のJSONLトランスクリプトを
   general-purpose agentに分析させ、「躓いている箇所」「セッションをまたいだ重複質問」を抽出。
2. 見つかった2パターンをCLAUDE.md(実体: `.../.claude-sync/CLAUDE.md`)に追記:
   - バックグラウンド作業(Bash background/Agent/ブラウザ自動操作)が無言停止した際、ユーザーの気づきに
     頼らず自分で検知してTeams通知→再開する標準ルール
   - Claude自身が設定した自動化パラメータ(同期範囲・頻度等)は即座にメモリへ記録し、聞き返されたら
     即答する標準ルール([[feedback_powerbi_track_own_instructions]]をPowerBI限定から全プロジェクト共通へ一般化)
3. ユーザーから「毎週月曜の他のタスクとともに自動実行して」と依頼され、当日朝に別セッションが構築した
   既存の週次メモリレビュー基盤(`com.nakamura.memoryweeklyreview`、月曜8:30起動)に相乗りする形で
   CLAUDE.md改良ステップを追加。AskUserQuestionで「完全自動(追記まで自動適用)」の承認を得た。
   詳細は[[memory_weekly_review_automation]]の「追加(2026-08-23、同日中)」セクション参照。

## 学び・注意点
- **auto mode classifierがCLAUDE.mdを無人で自動編集するスクリプトの追加をブロックした**。無理に回避せず
  ユーザーに確認したところ、この件については完全自動でよいとの回答だった。同種の「無人実行でグローバル
  設定ファイルを変更する仕組みを組む」タスクでは、今後も同様にAskUserQuestionで一度確認するのが安全。
- 週次自動レビュー基盤(`~/MemoryWeeklyReview/`)は当日朝に別セッションが独立に構築していた
  (`com.nakamura.memoryweeklyreview`)。プロジェクトを跨いだ並行セッションが同日に関連する自動化基盤を
  作ることがあるので、新しい定期実行タスクを頼まれたら、まず`launchctl list`/`~/Library/LaunchAgents/`
  や関連メモリ(`grep -rl "月曜\|毎週\|weekly" memory/`)で既存の仕組みがないか確認してから重複構築しない
  ほうがよい(今回はこの確認により、車輪の再発明を避けて既存ジョブに相乗りできた)。
- JSONL履歴のマイニングは生ファイルを読まずjqでユーザー発話テキストだけ抽出するのが必須
  (700MBを直接読むとコンテキストが壊れる)。週次自動実行版は前回実行以降の差分だけを見るようマーカー
  ファイルで範囲を絞り、毎回全履歴を再スキャンしない設計にした。

## 次回このメモリに触れるとき確認すること
2026-08-24(月)の自動実行後、Teams通知(「週次CLAUDE.mdレビュー完了」)とCLAUDE.mdの実際の差分を確認する。
