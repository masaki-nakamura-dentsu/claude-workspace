---
name: browser-account-routing
description: 作業用ブラウザはログインするアカウントの種類(dentsu.co.jp会社/個人Gmail/ChatGPT Enterprise/aicon共有)で使い分ける。マシン別のポート・プロファイル・作業の対応表
metadata:
  node_type: memory
  type: feedback
  originSessionId: a464ea17-1665-41fd-bcae-d201d0b777a4
  modified: 2026-10-12T00:43:37.134Z
---

**ルール(2026-10-12 ユーザー指示)**: ブラウザ自動操作では、どの作業用ブラウザを使うかを**その作業で使うアカウントの種類**で決める。新しい作業を作るときも、既存の作業を直すときも、まず「この作業はどのアカウントの作業か」を決め、下の表のそのアカウント用ブラウザにつなぐ。違うアカウントのブラウザに相乗りしない。

**Why:** 個人Macの共有ブラウザ(9227)は個人Gmail系のログインなのに、Salesforceバックアップがそこで動いていて全件失敗した(2026-10-12、[[sf_reports_qbr_download_automation]])。会社用(dentsu-work-bot/9231)に分けたら解決した。1つのプロファイルに複数のアカウントを混ぜると、Googleのアカウント選択で止まる・SSOが切れる・違うアカウントで操作するといった事故が起きる([[chatgpt_web_automation]] 2026-09-17の例)。

**How to apply:**
- 新しいWebサービスを自動化するときは、そのサービスに入るアカウントを確認し、表のブラウザを使う。そのアカウント用のブラウザが無いときだけ、新しいプロファイルを空いているポートで作って、この表に追記する。
- 作業を新しいブラウザへ移したら、表の「作業」欄を更新する。
- [[shared_bot_browser]]の「1台に共有ブラウザ1つ」ルールは、**同じアカウントの中で**共有する、という意味に読み替える。
- ログインが切れていたら、ウィンドウを画面に出してユーザーにログインしてもらい、終わったらすぐ画面外(-2500,-2500)へ戻す。

## 個人Mac(ICPTokyo2022, maxakisan) — 2026-10-12時点

| ポート | プロファイル(`~/.chrome-profiles/`) | アカウント | 作業 |
|---|---|---|---|
| 9231 | dentsu-work-bot | **会社** masaki.nakamura@dentsu.co.jp (dentsu MyApps SSO / Microsoft Entra / dentsu Japan Okta) | Salesforce QBRバックアップ(代行)とSalesforce関連全般、Teams CLI・自分宛て投稿・SF事前確認、Outlook CLI、GBC週報DL、AI Teamsダイジェスト(バックアップ側launchd)、Dify |
| 9229 | chatgpt-work-bot | **会社** ChatGPT Enterprise (dentsu.co.jp) | 仕事用ChatGPTの自動操作([[chatgpt_web_automation]]、`~/Scripts/chatgpt_project_test/`) |
| 9227 | timetree-bot (「共有ブラウザ」) | **個人** Gmail系 | TimeTree、МФК PHOTOSのSNS投稿([[mfk_photos_posting_access_gap]])、freee会計(合同会社AWIT、[[freee_accounting_internal_api_registration]]) |
| 9230 | maxakisan-bot | **個人** maxakisan@gmail.com | 個人用ChatGPT、個人アカウントで入るWebサービス |
| 9228 | powerautomate-bot / aicon-bot | **部門共有** aicon@dentsu.co.jp | 出退勤報告のPower Automate([[powerautomate_attendance_summary_project]])、アレココSharePointの管理([[gbc_kpikgi_sharepoint_export]])。aiconの操作はユーザー手動が原則([[feedback_powerautomate_aicon_browser_manual_only]]) |
| 9223 | nobrock-maps-bot | 個人Google | Googleマップのリスト保存([[google_maps_list_save_automation]]) |

**2026-10-12 移行完了**: それまで9227で動いていた会社アカウントの作業をすべて9231へ移した(ユーザーがTeams/Outlook/Difyに9231で1回ずつログイン)。
- `~/Scripts/teams_cli/lib.js` → 9231(Teamsの新URL teams.cloud.microsoft も認識するよう修正)。`teams list`で動作確認済み(ユーザー自身のターミナル実行でも確認)。
- `.claude-sync/Scripts/outlook_cli/lib.js` → 個人Macは9231(会社Macは9226のまま)。`list.js --limit 3`で確認済み。
- `.claude-sync/Scripts/GBCWeeklyReport/*.js` → 既定ポート9231(会社Macは`GBC_BOT_PORT=9226`)。SalesforceログインはSFバックアップで確認済み、本番DLは次回の週報時に初確認。
- `com.nakamura.aiteamsdigest.backup.plist` → `AI_DIGEST_BOT_PORT=9231`/`dentsu-work-bot`。RunAtLoadで即投稿されないよう、RunAtLoadを一時的に外して読み込み直してから元のファイルに戻した(launchd上は9231で読み込み済み)。初の実行は次回火曜8:00(主ジョブが動かなかった週のみ)。
- `download_all_reports.js` の Teams事前確認 → `TEAMS_PORT=9231`。
- Dify → 9231でログイン済み(スクリプトなし、手動・アドホックな操作のみ)。
- 変更前ファイルはそれぞれ `*_bak_20261012.*`(plistは `~/SalesforceExport/aiteamsdigest.backup.plist_bak_20261012`)。
- 9227(timetree-bot)には今、個人Gmail系の作業だけが残っている。

## 会社Mac(d14461)

| ポート | プロファイル | アカウント | 作業 |
|---|---|---|---|
| 9226 | `~/SalesforceExport/browser_profile` (共有) | **会社** dentsu.co.jp (Google含め会社アカウント) | Salesforce QBRレポート本体、Teams daemon、CAS、Outlook CLI、Power Automate確認、CCS Explorer、AI People Research、Gemini(仕事) |
| 9230 | maxakisan-bot | **個人** maxakisan@gmail.com | Klangio / Songscription / Moises ([[music_transcription_pipeline]]) |

**注意(2026-10-12)**: TeamsのURLは `teams.microsoft.com` → `teams.cloud.microsoft` に移行している。Teamsタブを探すコードは両方を認識すること(teams_cli・SFパイプライン・weekly_ai_digest.pyは対応済み)。


**2026-10-18 ユーザー指示(厳守)**: 同じアカウントの作業は同じブラウザで行う。TimeTreeもエアコン業者とのやり取り(ミツモア・くらしのマーケット・Gmail)も、すべて個人アカウント **maxakisan@gmail.com** の作業なので、個人Macでは **9227(timetree-bot、常駐の共有ブラウザ)** に新しいタブを開いて作業し、終わったらそのタブだけ閉じる。**別のブラウザ(9230 maxakisan-bot)を新しく立ち上げない**。アカウントが違う場合だけ別ブラウザでよい。
- 10/14〜10/18に9230を立ち上げてミツモア・くらしのマーケットにログインしたのは誤り(9230は10/18に閉じた)。この2サイトは9227にはまだログインしていないので、次回はユーザーに9227でログインしてもらう。
- 9230に残っている個人ChatGPTのログインも、次に必要になったときに9227へ移す(新規に9230は起動しない)。

関連: [[feedback_company_account_services_any_machine]](dentsu社内サービスは個人Macの9231でも入れる)
