---
name: feedback_check_slicer_syncgroup_before_field_swap
description: スライサーのフィールド差し替えを案内する前に、そのスライサーのsyncGroup(fieldChanges)を必ず確認する
metadata:
  type: feedback
---
2026-10-07 KGIKPIで「年スライサーを年選択[年ラベル]に差し替え」と案内したら、そのスライサーが同期グループ「計上年」(fieldChanges=true)に属していて、表紙★OVERVIEWを含む10ページの年スライサーまで差し替わり、各ページの値が「--」になった。月スライサーのsyncGroupは確認したが、年スライサーは確認していなかった。
**Why:** fieldChanges=trueの同期グループでは、1つのスライサーのフィールド変更がグループ全体に伝わる。他のページのメジャーは元の列(Raw YTD[計上年])で絞られる前提なので壊れる。
**How to apply:** PBIR(getDefinition)で、対象スライサーの visual.syncGroup を見てから手順を書く。同期グループに属していたら「先にスライサーの同期ペインでグループ名を変えて切り離す」手順を、差し替えより前に入れる。関連: [[feedback_verify_visual_binding_before_dax_swap]]
