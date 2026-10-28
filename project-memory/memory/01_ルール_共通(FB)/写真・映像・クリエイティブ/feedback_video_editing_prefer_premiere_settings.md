---
name: feedback-video-editing-prefer-premiere-settings
description: 動画編集(響き付加など)の依頼では、ffmpeg等でClaudeが直接ファイルを加工するより、Premiere Pro側の具体的な設定値を教えてほしいという傾向
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c6df1004-d8c1-4ca8-9a93-4d0426c76632
  modified: 2026-08-08T00:19:42.876Z
---

動画(寄席オペラ岸和田公演など)に対して「響きを足してほしい」のような編集依頼を受けた際、ffmpegで実際に書き出しファイルを加工して提示したところ、ユーザーから「Premiereの設定を教えてくれればよい」と修正された。

**Why**: ユーザーはPremiere Proで手動編集しているプロジェクト(納品フォルダの書き出し済みmp4ではなく元プロジェクト)がベースであり、最終的な仕上げ・微調整は自分でPremiere上の操作として行いたい。Claudeによる裏側でのファイル自動加工(ffmpeg等)は求めていないケースが多い。

**How to apply**: 動画編集系の依頼(エフェクト・音響処理・色調整など)では、まず该当ソフト(このプロジェクトではPremiere Pro、[[premiere_cyrillic_filename_import_error]]参照)上での具体的な設定パネル名・パラメータ値を案内することを優先する。ffmpeg等での直接加工は、明示的に「ファイルを作って」「試してみて」と言われた場合や、参考用サンプルとして提示する場合に留め、既定の対応にしない。
