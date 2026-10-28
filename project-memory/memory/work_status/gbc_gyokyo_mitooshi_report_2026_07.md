# GBC業況見通しレポート(2026年7月分)作成

## 2026-08-03T01:35:00Z
Status: done
What: 「今後の業況見通し」重要情報アンケート7月分を作成。6月・7月のSalesforce業務リストを突合し、過去の記入済みファイル(3〜6月分)と重複しない当月確定の主要ピッチ案件(勝利6件/敗退2件/仕掛5件)を抽出して下書きに記入。ユーザーが書式面(改行→「、」区切り、未選択の業況見通し選択肢テキスト削除、行高さ/フォント調整)を最終手直しし、内容は正しいと確認済み。次回以降は同じ手順・書式で細かい指示なしに自動作成してよいと明言されたため、手順をプロジェクトメモリ([[gbc_gyokyo_mitooshi_report_workflow]])に保存済み。
Next: 来月(8月)に「8月分を作って」と言われたら、保存済み手順書どおりに自動実行する。

## 2026-08-03T06:40:00Z
Status: done
What: ユーザーから、毎月最初の平日朝のリマインドと、Salesforceダウンロードの自動化について相談を受けた。(1) リマインドは、クラウドroutine/CronCreateではローカル通知が不可能と判明したため、Power Automate(定期実行+平日/日付条件+自分宛メール)方式で設計し、手順書`今後の業況見通し/POWER_AUTOMATE_SETUP_REMINDER.md`を作成(ユーザーが未構築、要ビルド)。(2) Salesforceダウンロードは、Teams自動化と同じPlaywright+Chrome永続プロファイル方式で試作し、ユーザーと一緒にライブテストして実際に成功(ダウンロードしたxlsxが過去ファイルと同一形式であることを確認)。エクスポート操作はiframe内、確認ダイアログは外側ページにポータル描画される点、エクスポート実行後にメール確認コードが必須な点(dentsuの2026年6月新セキュリティ要件)を特定し、2段階スクリプト`~/SalesforceExport/download_step1_export.py`+`download_step2_enter_code.py`として実装・動作確認済み。詳細は[[salesforce_report_download_automation]]に保存。
Next: (a) ユーザーがPower Automateリマインドフローを構築したら動作確認。(b) 来月の本番ダウンロード時に、確認コードが本当に毎回必要かどうか(デバイス信頼期間の有無)を確認する。(c) 可能ならパスキー登録でコード入力自体を不要にできないか検討。

## 2026-08-03T07:05:00Z
Status: done
What: リマインドについて、Power AutomateではなくOutlookカレンダーの組み込み「毎月の最初の平日」継続予定で十分と判断(ユーザー指摘)。POWER_AUTOMATE_SETUP_REMINDER.mdは削除し、[[salesforce_report_download_automation]]を更新。また「Power Automateから直接Claudeに指示できないか」との質問に、外部→Claude Codeの起動経路が存在しないこと、確認コード入力はどのみち人手が必要なことを説明。さらにユーザーから、起動フレーズは汎用の「Salesforceダウンロードして」だと将来の他のSalesforceダウンロード依頼と混同するため、「業況見通し用のSalesforceをダウンロードして」に限定する指示があり、メモリに反映済み。
Next: 来月、カレンダーリマインド経由でユーザーから「業況見通し用のSalesforceをダウンロードして」と言われたら、[[salesforce_report_download_automation]]の手順で実行する。
