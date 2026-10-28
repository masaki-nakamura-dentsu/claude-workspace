# 同期状況チェック (2026-08-06, d14461 Mac)

## 2026-08-06T10:35:00+09:00
Status: in progress
What: ユーザー依頼でメール/カレンダー/Teams/Facebookの4チャネル同期を確認([[feedback_sync_check_scope]]の通り一括で)。メール: OneDriveに196件/59時間分の未処理ファイル滞留を発見、手動同期で解消(147件マージ、最新まで追いつき済み)。Teams: デーモン正常稼働、最新メッセージ09:24 JST。カレンダー: OneDriveに353件のスナップショット滞留、手動同期を実行したが通常(6-10分)より大幅に時間がかかり、実行継続中(既存launchd起動分と合わせて2プロセスが並行処理中)。Facebook: 共有DropboxのFacebookExportがAug 3 23:18で59時間停滞 — 同期はICPTokyo2022 Mac専用設計のためd14461からは直接復旧不可。
Next: カレンダー同期の完了確認(次回このMacに触れた時)。Facebook同期はICPTokyo2022 Mac側で同様の手動同期チェックが必要 — 未着手。

## 2026-08-06T11:56:00+09:00
Status: done
What: カレンダー同期の手動実行が完了。OneDrive滞留スナップショットは353件→14件(直近分のみ)に減少、calendar_events.jsonは11:54に更新済み。メール・カレンダー・Teamsの3チャネルはd14461 Mac上で正常化を確認・完了。
Next: Facebook Messengerのみ未解決 — ICPTokyo2022 Mac(私用Mac)で `~/FacebookExport` の同様の手動同期チェックが必要(このMacからは同期先データが見えるだけで実行できない)。
