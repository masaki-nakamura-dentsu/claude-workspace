---
name: feedback-pureraw-via-lightroom-menu-no-screencapture
description: DxO PureRAWはLightroomのメニュー(ファイル>プリセットで書き出し>DxO PureRAW 4 ですぐに処理)をSystem Events経由で実行する。画面キャプチャはNG
metadata:
  type: feedback
---

PureRAWで複数RAWを処理するとき、PureRAWを直接GUI操作せず、Lightroomの書き出しメニューから「DxO PureRAW 4 ですぐに処理」を選ぶ（2026-10-25 マニュライフ案件で本人が指定、画面キャプチャはNG）。

**Why:** スクリーンショット/座標クリック依存の操作を避けたい。メニュー名指定のSystem Events操作は可。
**How to apply:** `lrb select`で対象選択→osascriptで ファイル>プリセットで書き出し の項目名に「ですぐに処理」を含むものをclick。出力DNGは元フォルダに `*-001.dng` 連番で出る（33枚で約1時間）。取込後は元ARWの現像設定をdevelop-setでコピー（LensProfile/Uprightは除外）し、Uprightは `lrb upright`（現像モジュール経由）で再計算。WBの色合わせは緑の色相を測定してTemperatureのみ調整する方法が有効。[[work_status/2026-10-25_manulife_ooh_select]]
