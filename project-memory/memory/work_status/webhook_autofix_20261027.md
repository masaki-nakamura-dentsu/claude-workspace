---
name: webhook_autofix_20261027
description: 2026-10-27 自動修復ログ
metadata:
  type: project
---

## 08:46 KGI/KPIレポート定期保存 PDF 0 bytes(会社Mac N650893)
- Status: monitoring
- 事象: 08:25定期実行(4回リトライ全て0 bytes)、私の `--force` 再実行1回(08:35〜08:45、4回とも0 bytes)も失敗。Botブラウザ(9226)は稼働中。
- 判断: 10/22・10/26と同症状。いずれも午前の0 bytesが10:10〜15:40の枠で自然回復(Power BI側エクスポート生成が空になる一過性)。スクリプト無編集(別セッションが今朝リトライ4回化・archive再送を追加済み)。再実行はこれ以上しない。
- 次: launchdの11:40/13:40/15:40枠で自動再試行。15:40も失敗ならBotブラウザで手動PDFエクスポートが空にならないか確認、Botブラウザ再起動を検討。

## 13:05 外務省危険Lv 取得失敗(会社Mac N650893)
- Status: done
- 事象: 13:00定期実行で 00A.xml が取得できず(curl空応答)。13:02時点では直接・プロキシとも不通(Googleも不通)=一時的なネットワーク断。
- 対応: プロキシ経由(proxy1.dentsu.co.jp:8080)で到達確認後、plist指定のPython3.14で1回再実行→OK(国キー483/地域282/都市255、SPアップロード200)。スクリプト無編集。
- 注意: 手動実行は /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 を使う(既定python3はopenpyxl無し)。
