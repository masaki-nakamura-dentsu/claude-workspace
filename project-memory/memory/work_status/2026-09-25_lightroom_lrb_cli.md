## [2026-09-25] Lightroom 自作CLI `lrb` を開発し旧 lightroom-cli を置き換え
Status: done
- 依頼: Lightroom終了時に毎回 CLI Bridge が強制終了のようになる → 旧ツールを使わず自作CLIで問題解消。
- 旧プラグインの問題: LrSocket 2本を常時保持、10秒ごとにtimeout→再接続を無限に繰り返しログ58MB、AppShutdown.luaがLrShutdownFunctionを返さず終了時にソケット閉鎖待ち→再起動要求が走る。
- 新: ~/Scripts/adobe_cli/lrbridge/（lrbridge.lrplugin + lrb.py、README.md有）。ファイルスプール方式でソケット無し。`lrb quit` で終了2.1秒・bridge stop正常を複数回確認。
- 旧プラグインは ~/Scripts/lightroom_cli_autostart_backup/lightroom-cli-bridge.lrplugin_disabled_20260925 に退避（Modulesから除去）。pipxのlightroom-cli本体は未アンインストール。
- 実機テスト済: status/selected/view/folder/find/info/rate/label/title/keyword/import/develop-set(読み戻し検証ok)/thumb/export(長辺800px正常)/collections/collection-add。
- テスト残骸: ~/Pictures/LrBridgeTest/lrbridge_test.jpg をカタログに読み込み(id 91482336、★3・レッド・キーワード「テスト」「LrBridge」・コレクション「LrBridgeTest」)。ユーザーに削除可と案内。
- 途中でLightroom前面化を1回ユーザー許可のうえ実施(背景起動がスプラッシュで停止するため)。

## [2026-09-25] 追記: 旧ツール本体とログを削除
Status: done
- `pipx uninstall lightroom-cli`（`lr`/`lr-mcp`消滅）、LrClassicLogs の LightroomPythonBridge.log(58MB)・MenuActions.log・StopMenuAction.log を削除。
- 退避した旧プラグイン(~/Scripts/lightroom_cli_autostart_backup/)は指示外のため残置。`lrb`は動作に影響なし。

## [2026-09-25] セッション終了
Status: done
- ユーザーが「task end」。残作業なし（旧プラグイン退避フォルダとテスト写真1枚は残置、ユーザー判断待ち）。
