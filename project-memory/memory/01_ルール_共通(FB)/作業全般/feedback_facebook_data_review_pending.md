---
name: feedback_facebook_data_review_pending
description: 中村さんが「Facebookに自分の情報がどこまで取られているか」を後日確認したいと明言(2026-07-29)。まだ着手していない保留タスク。次にSNS関連の会話になったら思い出して提案すること。
metadata: 
  node_type: memory
  type: project
  originSessionId: f6d2b3e6-853a-449d-89e0-8e51ee85dd46
  modified: 2026-07-29T07:06:18.633Z
---

2026-07-29、SNS投稿下書き作成の作業中に、本人から「私がFacebookにどこまで情報が撮られているかも後で確認したい」と依頼あり。この時点ではまだ調査に着手していない(投稿文の下書き作成が優先タスクだったため)。

## 調査に使える材料
本人が同日取得したFacebook公式データエクスポート一式が `~/ICPTokyo2022 Dropbox/中村正樹/Photographer/SNS下書き/facebook-masakinakamura1125-2026_07_29-TpgGwHAk/` に展開済み。特に以下のフォルダが「どこまで情報が取られているか」の調査に直結する:
- `ads_information/`: `advertisers_using_your_activity_or_information.html`(自分の情報を広告に使っている広告主一覧)、`your_sampled_locations.html`(位置情報サンプル)、`ad_preferences.html`、`other_categories_used_to_reach_you.html`、`apps_detected_on_your_account.html`/`apps_detected_from_your_activity.html`(連携検知されたアプリ)等。
- `apps_and_websites_off_of_facebook/`: `your_activity_off_meta_technologies.html`(Facebook外でのトラッキング=いわゆる「オフFacebook活動」)、`connected_apps_and_websites.html`。
- `security_and_login_information/`: ログイン履歴・デバイス・IPアドレス活動等。
- `personal_information/`: プロフィール情報、facebook_accounts_center等。
- `logged_information/`: (中身は本タスク開始時点では未確認)。

## 次回やること
上記フォルダの該当htmlを読んで、「広告主にどう使われているか」「オフFacebookでの行動追跡がどこまで及んでいるか」「位置情報がどこまで記録されているか」を分かりやすく要約して報告する。まだ本人には何も報告していない状態 — この作業自体は未着手なので、次回SNS関連の会話が来たら思い出して提案すること。

関連: [[personal_sns_management_project]]、[[nakamura_facebook_post_style]](同じエクスポートから投稿文体の分析は完了済み)。
