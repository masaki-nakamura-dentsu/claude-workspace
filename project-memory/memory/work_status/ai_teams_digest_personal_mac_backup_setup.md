# 週次AIダイジェスト 個人Mac(ICPTokyo2022)バックアップ環境セットアップ

## 2026-08-25T09:20:00+09:00
Status: done
What: `.claude-sync/data-export/TeamsExport/scripts/setup_personal_mac_backup.md`の手順に沿って個人Mac側にセットアップ実施。シンボリックリンク作成、brew版python3(/opt/homebrew/bin/python3)にplaywright/truststore/certifiを導入、launchdジョブ2件(`com.nakamura.aiteamsdigest.backup`=火曜8時、`com.nakamura.webtipscollector.backup`=6時間おき)を作成・ロード。webtipscollectorはRunAtLoadで即成功。aiteamsdigestは初回RunAtLoad実行時にTeamsセッションがログアウト状態で失敗(誤送信なし、state未更新で安全)、その後`--test --days 1`を2回実行し2回目で自分チャットへの投稿まで成功、パイプライン全体の動作を確認済み。詳細は project memory `ai_teams_weekly_digest.md` の2026-08-25セクション参照。
Next: 次回火曜8:00の本番自動実行、または会社Mac側の実行を待って、state file経由の二重投稿防止が実地でも機能するか確認する。
