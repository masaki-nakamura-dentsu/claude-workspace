---
name: feedback_gemini_gem_followup_needs_explicit_image
description: Global Q Gemへの修正依頼は「この場でNano Bananaで1枚生成して」と明示しないとJSONテキストが返る。ダウンロードボタン誤検知に注意(10/19)
metadata:
  type: feedback
---
Global Q 4コマGemで同じチャットに修正を頼むと、画像ではなく「再生成用JSONプロンプト」がテキストで返ることがある。このときコードブロックのダウンロードボタンを画像と誤認して、JSONを .png として保存してしまった。

**Why:** 2026-10-19 BX漫画第2話の修正で発生。
**How to apply:** 修正依頼の文面には「この場でNano Bananaで画像を1枚生成して」を最初から入れる。完了判定は、応答内に img があり、かつダウンロードボタンがあること。保存したら `file` コマンドで画像か確認する。スクリプトは Project_BX拡散/作業履歴フォルダ/manual/manga/gem_fix.py。[[gemini_web_automation]] [[globalq_4koma_manga_project]]
