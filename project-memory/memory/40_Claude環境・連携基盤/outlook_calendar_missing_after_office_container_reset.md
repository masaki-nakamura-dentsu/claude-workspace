---
name: outlook-calendar-missing-after-office-container-reset
description: 会社Mac(d14461)でUBF8T346G9.Office退避後にOutlookの予定表が表示されなくなった件。原因と復旧手順、PowerPointフリーズ対応とのトレードオフ
metadata: 
  node_type: memory
  type: project
  modified: 2026-08-19T03:04:21.644Z
  originSessionId: be88ba32-bfaf-4693-820f-20ea6496aa6a
---

2026-08-19、IT一次対応の指示（[[powerpoint_freeze_proxy_auth_issue]]参照）でPowerPointフリーズ対策として `~/Library/Group Containers/UBF8T346G9.Office` をデスクトップへ退避 → PowerPointは正常化。しかし副作用としてOutlookの予定表(カレンダー)が表示されなくなった。ユーザーは退避した旧フォルダを既に削除済みのため、単純に元へ戻す復旧はできない。

**原因**: `UBF8T346G9.Office` にはOutlookのローカルキャッシュ(予定表データベース含む)も格納されている。退避により空の新規プロファイルが自動生成され、Exchangeサーバーとの再同期が必要な状態になった。表示上も「見出しの週範囲」と「実際に表示されている列の日付」がズレるなど、UI再描画の不整合も観測された。

**提案した復旧手順(未検証、本人による実施待ち)**:
1. Outlookを完全終了→再起動し、バックグラウンド再同期の完了を待つ
2. 週/日/月表示の切り替えや「今日」ボタンで再描画を強制
3. フィルターや左サイドバーの予定表チェック漏れを確認
4. それでも直らなければ、Outlook環境設定からアカウントを一度削除して再追加し、フルリシンクを強制

**How to apply**: 同様の「Officeコンテナ退避でPowerPoint/Wordは直ったがOutlookの予定表が消えた」という報告が来たら、まずこのメモの復旧手順を提示する。また今後PowerPointフリーズ対応でこのフォルダ退避を提案する際は、事前に「Outlookのローカルキャッシュがリセットされ、予定表が一時的に見えなくなり再同期が必要になる」副作用を本人に伝えること。
