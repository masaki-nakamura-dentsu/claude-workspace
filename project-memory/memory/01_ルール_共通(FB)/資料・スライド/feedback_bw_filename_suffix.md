---
name: feedback-bw-filename-suffix
description: 白黒(モノクロ)版の画像・デザインファイルを書き出す際は必ずファイル名に_BWを付けて区別する、標準ルール
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e376cff7-6c3d-466c-a5b4-0cca31836179
  modified: 2026-08-09T02:01:01.034Z
---

画像やデザインファイルの白黒(グレースケール)版を作る際は、必ずファイル名に`_BW`サフィックスを付けて元のカラー版と区別する。

**Why:** 2026-08-09、[[tokyo_leaves_project]]のキービジュアル書き出し作業で本人が明示的に指示。「クライアントが白黒での使用も検討したいとのこと」という文脈で、「_BWは今後の作業でも同じルールです」と述べており、このプロジェクト限定ではなく標準ルールとして扱ってほしいという明言。

**How to apply:** 今後どのプロジェクトでも、カラー版に加えて白黒版を作る依頼が来たら、ファイル名の末尾(拡張子の直前)に`_BW`を付ける。既に日付サフィックス([[feedback_pptx_filename_versioning]])が付く場合は`<ベース名>_<日付>_BW.<拡張子>`の順(例: `TokyoLeavesKV_01_20260809_BW.jpg`)。
