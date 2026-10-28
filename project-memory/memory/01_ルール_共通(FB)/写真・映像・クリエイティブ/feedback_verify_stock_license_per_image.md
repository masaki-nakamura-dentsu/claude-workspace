---
name: feedback-verify-stock-license-per-image
description: "ストック写真のEditorial use only判定は画像ごとに個別確認し、バッチ確認時に結果を取り違えない"
metadata:
  type: feedback
  originSessionId: unknown
  modified: 2026-08-22T11:27:08.340Z
---

[[subway_photo_booklet_project]]で、iStockプレビュー4枚を並列Read呼び出しでまとめて確認した際、実際には商用利用可（Editorial use only表記なし）だった1枚(istockphoto-153002224、Arts et Métiers駅)を誤って「エディトリアル限定」と判定し、資料から除外してしまった。ユーザーの指摘で発覚。

**Why**: 同一構図・同じ駅の写真が複数枚並ぶ場合、視覚的な差異が小さく、並列確認時にどの画像がどの結果だったか取り違えやすい。「4枚中3枚がエディトリアルだったから残りも同様」と一般化してしまうバイアスもあった。

**How to apply**: ストック写真のライセンス確認（Editorial use only等の透かし判定）を複数枚まとめて行う際は、各画像のファイル名/IDと判定結果を明示的に1対1で記録してから次に進む。特に同じ駅・似た構図が並ぶ場合、思い込みで結果を外挿しない。ユーザーから「これは違うようです」と指摘されたら、まず自分の判定を疑い、該当画像を再確認してから訂正する（正しいと言い張らない）。

同じ現場感覚は[[feedback_verify_against_official_totals]]（数字の解釈は必ず公式合計と突合）や[[feedback_check_surrounding_rows_before_manual_entry]]と同種 — 「まとめて処理するときほど個別検証を省略しない」という一般則として、写真ライセンス確認以外の一括判定作業にも適用できる。

この一般則は[[feedback_verify_against_ground_truth]]に統合済み(2026-08-24)。
