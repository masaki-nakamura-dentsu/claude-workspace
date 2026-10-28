# Pylance exclude設定(ワークスペースパフォーマンス)

## 2026-09-15T00:00:00
Status: done
What: VSCodeのPylance「大量ソースファイル」警告への対応。ワークスペース(中村正樹Dropboxルート)は総ファイル数約108万、うちPhotographer(74.5万)やWork/Client(17.9万)等ほぼ非コードのため、`.vscode/settings.json`に`python.analysis.exclude`/`files.watcherExclude`/`search.exclude`を追加(.venv、Photographer、Work配下の非コードサブフォルダ等を除外、実Pythonファイルのあるフォルダは温存)。ユーザーがVSCode再読み込み済み。
Next: —
