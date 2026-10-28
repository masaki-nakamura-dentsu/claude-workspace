---
name: gbc-intelligence-engine-mac-session-20260816
description: GBC Intelligence Engine構築セッション(個人Mac側)、環境構築からWindows並行処理・完了まで
metadata: 
  node_type: memory
  type: work_status
  originSessionId: a2b1d5fa-32d1-43c1-a288-bd925645a6b0
  modified: 2026-08-17T00:15:17.663Z
---

Status: done(個人Mac側の作業は終了。ユーザーは会社Macで継続予定)

## やったこと
- 個人MacにOllama+qwen3:8bを新規インストール、GBC Intelligence Engineプロジェクト(会社Mac発、ChatGPT引き継ぎ)の
  続きをClaude Codeで実装(Evidence→Fact→Knowledge→Cardパイプライン、readers/extractor/knowledge_builder/
  card_builder/markdown_writer/deduplicate)
- SharePoint(GBCarekoko/DocApp)からダウンロード済みの実コーパス(外付けSSD、402ファイル)に対して本番実行
- 自宅Windows(RTX3090)とのマシン間並行処理を構築(CRC32静的分割、環境変数ベースの設定分離、全workerマニフェスト
  参照によるcatch-up対応)
- 複数の重大バグを発見・修正(Qwen3思考モード起因のタイムアウト、venvのDropbox同期衝突、CRC32絶対パスバグ、
  外付けSSD瞬断による誤マニフェスト記録、dedupe.pyのO(n²)スケーラビリティ)
- 最終的に14,897件の知見カードを生成、672グループの重複統合完了

詳細は[[gbc_intelligence_engine_project]]、技術的な教訓は[[feedback_venv_outside_dropbox_sync]]を参照。

## 残作業(会社Macで継続予定)
- Phase2以降(Knowledge Graph化、Assistant Partner、GPT連携、Web化)は未着手
- カード0件だった12ファイルの内容を人の目で最終確認(妥当と推定したが未検証)
- 個人Mac側のlaunchd設定・venv(`~/gbc_knowledge_venv`)は残置(再利用可能、ただしplistは削除済みなので
  再度使う場合は`launchctl bootstrap`からセットアップし直しが必要)
