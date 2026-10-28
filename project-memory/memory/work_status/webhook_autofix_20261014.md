## 2026-10-14 04:21 HDY定点観測 sf 収集失敗 (自動修復)
Status: done / machine: 個人Mac(MacBookMN)

- 症状: `sf` 収集で `ValueError: Excel file format cannot be determined`。10/13 22:19・10/14 01:20・04:20 の予備系実行で連続失敗。
- 原因: `SF_PITCH_DIR`(Salesforce書き出し/APAC Pitch - List All_v1.31)の**最新xlsxがDropboxオンラインのみのプレースホルダ(0バイト、`com.dropbox.placeholder`)**。57本中49本が0バイト。`max(mtime)`でその0バイトを掴んで pandas が形式判定不能。
- 修正: `collectors.py` の `sf()` で 0バイトを除外して実体のある最新ファイルを選ぶようにし、`engine="openpyxl"` を明示。バックアップ `collectors.py.bak_202610140421`。
- 検証: `python3 -c "import collectors; print(collectors.sf())"` → `(0, 'HDY絡み184件 (…2026-10-12-09-39-20.xlsx)')` 正常。
- 残課題(軽微): 10/13以降のSF書き出しは実体がないため、sfは10/12版を参照。必要なら当該xlsxをFinderで「オフラインで利用可能」にする。

## 21:40 Salesforce QBR DL(個人Mac) 18本未取得 ERROR
Status: done(要ユーザー対応)
- 症状: 2026-10-14 07:45スロットのフェイルオーバーが9回×18本すべて「レポートビルダーのiframeが見つかりません」で0/18。
- 原因: 共有ブラウザ dentsu-work-bot(port 9231)のOkta/MyApps SSOセッション切れ。レポートURLへ行くと
  https://myapps.dentsu.com/app/salesforce/.../sso/saml の「MyApps - サインイン」画面へ飛ぶ(CDP経由で確認)。
  タブにはToopher(Salesforce Authenticator)検証の残骸URLもあり、MFA再承認が必要な状態。
- 対応: MFAは自力突破しない方針のため復旧はユーザー操作待ち。
  再発時の無駄打ち(9回×18本×3試行)を止めるため download_all_reports.js に
  isSsoSessionAlive() 事前判定を追加(ログイン画面URLなら即中断・[WAIT]通知・exit 2)。
  バックアップ: download_all_reports.js.bak_202610142145 / node --check 通過。
- ユーザー作業: Chromeの dentsu-work-bot プロファイルでMyApps→Salesforceに再ログイン(Authenticator承認)。
  確認方法: `cd ~/SalesforceExport/reports_pipeline_personal && NODE_PATH="$HOME/.local/share/claude-playwright/node_modules" /usr/local/bin/node download_all_reports.js`
  → 「SSOセッション切れを検知」が出なければ回復。18/18成功のOK通知が届く。
