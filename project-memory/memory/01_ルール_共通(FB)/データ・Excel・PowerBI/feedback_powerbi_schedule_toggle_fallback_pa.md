---
name: feedback-powerbi-schedule-toggle-fallback-pa
description: PowerBI Serviceで手動更新は成功するのにスケジュール更新のトグルがオンにできない時は、深追いせずPower Automateの「データセットを更新する」で定期更新に切り替える
metadata:
  type: feedback
---
2026-10-06、競合社定点観測(HDY)で発生。所有者=aicon、ゲートウェイとクラウドの接続は全て青チェック、今すぐ更新も成功。しかし「データソースの資格情報」欄の初回「接続をテストできませんでした」が消えず、「更新スケジュールを構成する」がオンにできない(理由表示なし、マップ先再適用・再読み込みでも解消せず)。Power Automate(aicon)のスケジュール済みフロー+Power Bi「データセットを更新する」で代替し、ユーザーが設定・稼働確認した。

**Why**: クラウド接続形式(「aiconで管理」と表示され「資格情報を編集」が出ない)で作ったモデルは、旧UIの資格情報欄の警告が残り、トグルが無効化されることがある。原因の深追いはブラウザ操作の往復が多くトークン・時間がかかる。

**How to apply**: 同じ症状(手動更新OK・トグル不可)になったら、マップ先の再適用と再読み込みを1回だけ試し、だめならすぐPower Automate代替を案内する。資格情報は「設定→ゲートウェイとクラウドの接続→マップ先→新しい接続を作成」ルートで設定する。関連: [[feedback_powerbi_browser_only]] [[hakuhodo_overseas_intel_monitoring]]
