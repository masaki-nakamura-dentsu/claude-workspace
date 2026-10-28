# 会社Mac(d14461)への導入手順

個人Mac(ICPTokyo2022)のセッションからは会社Macを直接操作できない(SSH等の到達性なし)ため、この一式をDropbox経由で用意した。会社Mac上のターミナル、または会社Mac上で動くClaude Codeセッションで以下を一度だけ実行すれば導入完了。

## 前提確認

- `~/Library/LaunchAgents/com.nakamura.calendarsync.plist` が存在し、動いているPython3のパスが確認できること(このジョブの中で動的に再確認もするが、念のため先に `/usr/libexec/PlistBuddy -c "Print :ProgramArguments:0" ~/Library/LaunchAgents/com.nakamura.calendarsync.plist` で見ておくと良い)。
- `claude` コマンドがこのMacのPATHで使えること(個人Mac側の `~/TimeTreeCheck/run_daily_check.sh` が動いている実績があるので、同じ仕組みが使えるはず)。

## 導入コマンド

```bash
SRC="$HOME/dentsuDropbox Dropbox/中村正樹/.claude-sync/Scripts/company_sync_check"

mkdir -p ~/CompanySyncCheck/reports
cp "$SRC/run_daily_check.sh" ~/CompanySyncCheck/
cp "$SRC/daily_check_prompt.md" ~/CompanySyncCheck/
chmod +x ~/CompanySyncCheck/run_daily_check.sh

cp "$SRC/com.nakamura.companysynccheck.plist" ~/Library/LaunchAgents/
# plist内のパスが /Users/d14461/... 決め打ちなので、ユーザー名が違う場合は
# ProgramArguments・StandardOutPath・StandardErrorPath の3箇所を実際のホームディレクトリに書き換えてから load すること
launchctl load ~/Library/LaunchAgents/com.nakamura.companysynccheck.plist
launchctl list | grep companysynccheck
```

## 動作確認(任意、即時実行してテストしたい場合)

```bash
launchctl kickstart -k gui/$(id -u)/com.nakamura.companysynccheck
sleep 30
cat ~/CompanySyncCheck/launchd_stdout.log
```

## 個人Mac側との役割分担

- 個人Mac(7:30、`~/TimeTreeCheck/`): TimeTree登録漏れチェック + Facebook同期チェック + メール・カレンダー同期チェック
- 会社Mac(14:00、`~/CompanySyncCheck/`、本セットアップ): メール・カレンダー同期チェック + Teams同期チェック(report-only、自動再ログインはしない)

両Mac起動タイミングが違うという中村さんの申告(個人Mac=朝7:30起動率高、会社Mac=14:00起動率高)に基づき、1日のうちどちらかのMacが起動していれば最低1回はメール・カレンダーの stale チェック/回復が走るようにするのが狙い。
