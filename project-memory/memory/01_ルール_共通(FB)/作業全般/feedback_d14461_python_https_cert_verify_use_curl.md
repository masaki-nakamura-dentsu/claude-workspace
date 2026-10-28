---
name: feedback-d14461-python-https-cert-verify-use-curl
description: 会社Mac(d14461)ではPythonのurllib/requestsによるHTTPS通信がSSL証明書検証で失敗する — curlをsubprocess経由で使うと成功する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bab247fc-90c6-4c4d-81a8-c1d0f636e2c7
  modified: 2026-09-11T00:24:24.130Z
---

会社Mac(d14461)から外部HTTPSエンドポイント(例: Power Automateのwebhook URL)へPythonの
`urllib.request`(certifi同梱のCAバンドルを使っても同様)でPOSTすると、
`SSL: CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`で失敗することがある。
同じURLに対し`curl`(macOSのシステム信頼ストア=Keychainを使う)は問題なくHTTP 202等で成功する。

**Why**: 2026-09-11、[[continuous_data_capture_setup]]のtask-002(カレンダー/メール同期への
Teams通知組み込み)で発見。会社Macのネットワークは[[bigip_zscaler_reconnect_loop_conflict]]
の通りBIG-IP/Zscaler経由でTLS傍受されており、傍受用の証明書はmacOSのSystem Rootsには
信頼されていてもPython(python.orgビルド)がバンドルする独自CAストア/certifiには含まれて
いない。macOSのcurlはSecureTransport(システムKeychain)を使うため成功するが、Pythonの
`ssl`モジュールはOS非依存の証明書ストアを使うため失敗する——[[feedback_d14461_pip_needs_corporate_proxy]]
(pipが直接到達できずタイムアウトする問題)とは別の原因(こちらは接続自体は成立しTLSハンドシェイクの
証明書検証だけが失敗する)。

**How to apply**: 会社Mac(d14461)で新規にPythonからHTTPS POST/GETするコードを書くときは、
`urllib.request`/`requests`をいきなり信用せず、まず`curl`で疎通確認してから、本実装も
`subprocess.run(["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json",
"-d", json.dumps(payload, ensure_ascii=False)], capture_output=True, timeout=20)`のように
curl経由で実装するのが最も確実(`~/SalesforceExport/reports_pipeline/download_all_reports.py`の
`send_teams()`が最初の実装例、[[teams_webhook_powerautomate]]も参照)。`requests`ライブラリも
内部でcertifiを使うため同じ理由で失敗する(2026-09-11、`OverseasStaffList/common.py`の
`requests.post()`で実際に確認)——urllib固有の問題ではなくPython全般のCA証明書ストアの
問題。個人Mac(ICPTokyo2022、自宅ネットワーク)ではこの問題は未確認——会社Mac固有の可能性が高い。

**2026-09-11時点でこのパターンで修正/確認済みのファイル**(会社Mac、d14461):
- `~/SalesforceExport/reports_pipeline/download_all_reports.py`の`send_teams()`(既に対応済みだった、最初の発見)
- `~/CASExport/cas_monthly_pipeline.py`の該当関数(既に対応済みだった)
- `~/CalendarExport/sync_calendar_export.py`の`notify_teams()`(今回新規実装+curl化)
- `~/OutlookExport/sync_power_automate_export.py`の`notify_teams()`(urllib→curlに修正)
- `~/TeamsExport/teams_daemon.py`の`notify_teams_webhook()`(urllib→curlに修正、元々`except: pass`で
  失敗が完全に無音だったため一層気付きにくかった)
- `~/OverseasStaffList/common.py`の`send_teams()`(requests→curlに修正)

会社Mac上でTEAMS_WEBHOOK_URLを使う新規スクリプトを書く前に、まずこのリストと
[[continuous_data_capture_setup]]の2026-09-11エントリを確認すること。
