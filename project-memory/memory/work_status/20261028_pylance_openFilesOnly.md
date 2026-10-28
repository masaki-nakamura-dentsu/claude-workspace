---
name: 20261028_pylance_openFilesOnly
description: Pylance「多数のソースファイル」通知を diagnosticMode=openFilesOnly で解消
metadata:
  type: project
---
Status: done
- Dropbox直下の .vscode/settings.json に `python.analysis.diagnosticMode: "openFilesOnly"` を追加（既存のexclude21件は維持）。通知は解消済み。
- 副作用: 未オープンファイルのProblems表示が出なくなるのみ。補完・定義ジャンプは影響なし。
