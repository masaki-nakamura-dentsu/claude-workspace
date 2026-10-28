---
name: geo-mini-audit-v2-review-20261022
description: GBCメンバー作成の ChatGPT用 geo-mini-audit-v2 Skill を、実際に dentsu Enterprise ChatGPT(CDP 9226)で カルビー/日本/ポテチ で通しテストしたレビュー記録
metadata:
  type: project
---
Status: done (2026-10-22)

- 対象: ~/Downloads/geo-mini-audit-v2.zip。ChatGPTで Phase1→2→3→PPT を通しで実行(チャット: chatgpt.com/c/6ad98fe7-e83c-8338-9e91-1c411bf7079b)。
- 結果: 承認ゲート・30問(7/8/7/8)・集計の算術は正しく動作。PPT 12枚も生成された。
- 問題: (1)30問を1ターンで一括実行→独立クエリとして検証不能 (2)新規一時チャットで3問を再実行したら ID8 は#2→#1、ID15 は 不出現→出現 と不一致(試行ブレ) (3)ブランド名入り4問(ID21,22,29,30)が Mention/#1 を押し上げ (4)Phase2の表で Prompt/First Brand/Evidence/Sources列が欠落 (5)競合評価が定性のみ (6)Phase3で「Largest change in #1」欠落。
- 後片付け: 一時チャット3本+テストチャット1本が履歴に残る。使ったタブは close 済み。
- 関連: [[chatgpt_web_automation]]
