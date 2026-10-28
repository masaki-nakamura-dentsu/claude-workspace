---
name: reference-ai-people-research
description: 電通 AI People Research(AIペルソナ仮想定量調査)の場所と自動操作のコツ
metadata:
  type: reference
---
- URL: https://esq365.sharepoint.com/sites/peopleresearch/Style%20Library/home/index.aspx 。d14461の共有ブラウザ(9226)でログイン済み。データはブラウザのキャッシュ(localStorage)にのみ保存→結果はテキスト等で保存しておく。NDA・クライアント名は入力禁止。
- 属性: 性別(FormBtn--checkedクラスで判定、aria-checkedは常にfalse)/年代ドット(開始→終了の2クリック、ラベル表示は遅れる)/居住地域モーダル(プリセット「全国」→保存)。
- 「その他特性」はペルソナ属性へのキーワード一致で絞り込む。長文や「エンジニア」「製造業」は0人になる。「会社員（技術系）」=1,071人(全体10,000人)。press_sequentially+Enterでチップ化。下書きを開き直すと特性が消えるので入れ直す。
- 回答タイプ SA/MA/5SA/FA。FAはAIが分類カテゴリと割合を出す。11問は約8分で完了。
- 「調査開始」はauto modeで止められる→ユーザーの明示OKを得てから実行。
- 使用例: [[nidec_components_naming_pitch]]
- マニュアル(社内限、ユーザーのDownloadsに【クライアント提示不可】People Researchマニュアル.pdf): Tunes 15万人で学習したPeople Model、未知質問で相関0.8。回答は各選択肢の確率の平均(人数は換算)、質問は独立、5段階の単一案絶対評価は苦手、複数案の相対比較は得意。集計結果はクライアント提示可、ローデータは不可。SAには「この中にはない」「一つだけ選んでください」を入れると精度が上がる。
