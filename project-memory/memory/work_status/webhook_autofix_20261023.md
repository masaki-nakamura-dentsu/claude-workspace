
## 09:58 Salesforce QBR DL(個人Mac) connectOverCDP失敗
- Status: pending-user
- 事象: 09:38にSSOセッション切れ(WAIT通知済み)で中止→09:58の再実行でconnectOverCDP「Browser context management is not supported」。9231のChromeは起動中だが、タブが chrome://profile-picker/ のみ(プロファイル未読込状態)
- 原因: 前段のSSO切れと同根。bot用Chromeがプロファイル選択画面で止まり、Playwrightがcontext取得不可。スクリプト無編集・再実行なし
- ユーザー対応: dentsu-work-botのChromeでプロファイルを選び、MyApps経由でSalesforceへ再ログイン(MFA)→その後パイプライン再実行
