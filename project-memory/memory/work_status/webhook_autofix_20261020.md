
## 10:57 KGI/KPIレポート定期保存 PDF保存失敗(N650893)
- Status: done
- 原因: 09:55起動時に一時的なネットワーク未接続(300秒タイムアウト)。コード不具合なし
- 対応: 接続回復を確認後に手動で1回再実行→10:56 KGIKPIレポート_20261020.pdf のアップロード完了

## 12:44 外務省危険Lv 取得失敗(N650893) SSL CERTIFICATE_VERIFY_FAILED
- Status: done
- 原因: 旧版がPython urllibで取得→会社Macの社内プロキシTLS傍受で証明書検証失敗([[feedback_d14461_python_https_cert_verify_use_curl]])
- 対応: スクリプトは12:42時点で既にcurl+proxy取得版に更新済み(別セッション作成と推定)。編集なし。出力先を/tmp/mofa_test/out.xlsxに向けて単体実行→OK 国キー219 地域246 都市28。一部海外領(プエルトリコ等)はXMLパース不可でskip(既存仕様)
