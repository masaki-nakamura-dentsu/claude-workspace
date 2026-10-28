# Lightroom CLI 自動起動パッチ

## 2026-08-09T10:45:00+09:00
Status: done
What: 「Lightroom CLIプラグインを使わなくてもCLI操作できるように」との依頼を受け意図を確認したところ、実際の不満は「毎回手動でStart CLI Bridgeを押すのが面倒」だった。プラグイン自体を排除する方向(AppleScript/カタログDB直接操作)は機能が大幅に制限されるため不採用とし、既存プラグイン`lightroom-cli-bridge.lrplugin`の`PluginInit.lua`を直接パッチして解決。原因は`Config.lua`の`autoStart=true`が実装されておらずログを出すだけのダミーだったこと。`MenuActions.lua`と同じ起動処理を`PluginInit.lua`の末尾に移植し、Lightroom完全終了→再起動で検証(メニュー操作なしで`lr system status`がconnected:true、`lr catalog get-selected`も正常応答)。オリジナルは~/Scripts/lightroom_cli_autostart_backup/にバックアップ。詳細は[[lightroom_cli_setup]]。
Next: — (完了。ただし`lightroom-cli`パッケージ更新時にプラグインが再インストールされるとこのパッチは上書きされるため、更新時は再適用が必要)
