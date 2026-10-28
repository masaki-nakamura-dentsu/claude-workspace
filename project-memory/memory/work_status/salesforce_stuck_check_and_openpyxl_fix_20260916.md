# Salesforceダウンロード停止確認 + COMBINED.xlsx同期のopenpyxl欠落修正 (2026-09-16)

## 2026-09-16T17:56
Status: done
What: ユーザーから「Salesforceダウンロードが止まっている感じがする」と確認依頼。ログ・プロセス・ロックファイルを調査した結果、16:45枠パイプラインは17:02:39に完了済み(18本中17成功/1失敗=「月別見込（設定売総 X 部署）」が3回リトライ共にdownloadイベントタイムアウト)で止まっていないことを確認。副次的に、ダウンロード後の`sync_sf_record_list.py`(COMBINED.xlsx自動更新)が`ModuleNotFoundError: No module named 'openpyxl'`で毎回失敗していることも発見・報告。
Next: ユーザーが両方の対応を指示。

## 2026-09-16T18:00
Status: done
What: (1)失敗していた「月別見込（設定売総 X 部署）」(id 00O7F00000Ay7SrUAJ)をBrowserState/download_one_report_with_retryを直接importするワンオフスクリプトで単体再ダウンロードし成功(26KB、zip検証OK)。(2)openpyxl欠落の原因は`download_all_reports.py`内`run_combined_rebuild_sync()`がsubprocess.run(["python3", ...])とバイナリ名のみ指定していたため、launchdの最小PATH下でopenpyxl未インストールのApple標準Python(/usr/bin/python3, 3.9.6)に解決されていたこと。`sys.executable`を使うよう修正し(sysは既存import済み)、修正後のインタプリタで`sync_sf_record_list.py`を手動実行し正常動作(COMBINED.xlsx同期成功)を確認済み。
Next: — (次回定時実行11:15/16:45で自動的に修正版が動く。[[sf_reports_qbr_download_automation]]への反映は次回同メモリ更新時に追記予定)
