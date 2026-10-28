---
name: mac-freeze-20260830-ai-print-prep-incident
description: 2026-08-29夜、個人Mac(ICPTokyo2022)がメモリ枯渇でフリーズ→翌朝05:17強制再起動。ai_print_prep.py(Illustrator入稿自動化)が原因の可能性が高い
metadata: 
  node_type: memory
  type: project
  modified: 2026-08-29T21:50:11.922Z
  originSessionId: 3d22b780-a3cd-43f0-a5b2-e54b58731236
---

**事象**: 2026-08-29深夜〜08-30早朝、個人Mac(ICPTokyo2022)がメモリ枯渇で完全に応答不能になり、ユーザーが電源長押しで強制再起動(05:17)。

**調査で判明した事実**:
- JetsamEvent診断レポート(`/Library/Logs/DiagnosticReports/`)によると23:07〜翌02:40の間に少なくとも15回のメモリ逼迫イベントが発生し、**毎回例外なく"largestProcess"がAdobe Illustrator**だった。
- 02:40を最後にログが途絶え(空きメモリ約329MBまで低下)、次の記録は05:17の`shutdown_stall`レポート(OSがシャットダウン処理自体のハングを検知)。
- 21:18: [[subway_photo_booklet_project]]の目録ページを手動/インライン相当の旧手順で圧縮完了(1.84GB→156MBの`_OL.ai`)——これは正常完了しており問題なし。
- 22:11: Claude(このセッションの前日版)が`~/Scripts/adobe_cli/ai_print_prep.py`を新規作成。CMYK変換・画像埋め込み・**画像を350ppiで一括rasterize**・テキストアウトライン化・別名保存を1つのIllustratorセッションで行う入稿一括処理スクリプト。スクリプト自身のdocstringに「rasterize(normalize)ステップは使い捨てコピーでの構造検証のみで、実ファイルでの視覚確認は未実施」と明記されていた。
- 22:11以降、新たに生成された`_OL.ai`や出力ファイルは一切見つからない → もし22:11以降にこのスクリプトが実ファイルに対して実行されたなら、**完了せず処理が止まったまま(=Illustratorがrasterizeループ等で固まった)可能性が高い**。
- ai_print_prep.pyはBashツール経由の実行のため`~/.zsh_history`に記録が残らず、実際に何度・どのファイルに対して実行されたかは直接確認できなかった(この点は未確定)。

**結論(確度: 高いが断定はできず)**: 前夜Claudeが作成した`ai_print_prep.py`——特に「実ファイルでは未検証」と自ら記していたrasterize一括処理ステップ——を無人実行したことが、Illustratorのメモリ暴走・Mac全体のフリーズの引き金になった可能性が高い。

**Why**: 画像を多数含む「目録」ページ(元々1.84GBあった=多数の高解像度クリップ画像を含む)のような重いファイルに対し、検証不十分な新規スクリプトでrasterize()を繰り返し呼ぶ処理を、ユーザーに確認せず・無人(夜間)で実行したこと自体がリスクだった。

**How to apply**: 今後、(1)新規に書いた・実ファイルで未検証のExtendScript/AppleScript自動化(特にrasterize/フィルタ処理/エクスポート等メモリを大量に使う操作)を、大きな入稿ファイルに対して無人・夜間で実行しない。実行前に「これは初めて実ファイルに使うので少し様子を見ながら進める」等、リスクを明示してユーザーに確認を取る。(2)複数ファイルをループ処理するIllustrator自動化は、1ファイルごとにIllustrator自体を再起動する(osascriptでquitしてから再度openする)など、プロセスメモリをリセットする仕組みを入れることを検討する。(3)長時間かかりうる自動化を無人実行する場合は、実行中に`vm_stat`や`ps`でメモリ使用量を定期チェックし、閾値を超えたら中断する簡易ガードを入れることも検討。[[photoshop_illustrator_cli_setup]]・[[feedback_confirm_before_image_heavy_work]]と関連。

ユーザーへの報告後、本人から「止めてください、別チャットで続けます」との指示があり、この時点で調査を打ち切った。ai_print_prep.pyの実行有無・実行タイミングの完全な特定は未完了。

**2026-08-30追記: 再発を確認・対策済み。安全な代替手順を確立。**
別チャット(このメモの続き)で、`ai_print_prep.py`の「rasterize一括処理」ステップをデフォルトで無効化(`--dangerous-rasterize-normalize`フラグでのみ有効、大きな警告をdocstringに追記)。その上で目録以外の8ファイル(表紙+7カ国、各1〜2枚の全画面写真)に対して[[subway_photo_booklet_project]]で使った安全な代替経路(`ai_thumbnail_tool.py`の`measure`→`compress`(外部caesiumclt、Illustrator外)→`replace`(`PlacedItem.embed()`のみ、`document.rasterize()`は不使用))を実行したところ、**4ファイル目(US、10P-P11)の2回目のreplace呼び出し中に再びIllustratorが無応答になった**。この時点で`vm_stat`を確認したところ空きメモリが約73MB(前回フリーズ時の329MBよりさらに低い)まで低下しており、危険と判断してユーザーの都度確認を待たず`kill -9`でIllustratorを強制終了(空きメモリは即座に約3GBまで回復、システムフリーズを未然に防止)。

**根本原因の確定**: `document.rasterize()`を使わない軽量な`replace`操作自体は安全だが、**同一のIllustratorプロセスをまたいで`ai open`→処理→`ai close`を何度も繰り返すと、Illustrator側でメモリが解放されずに蓄積していく**(このメモ冒頭の「How to apply (2)」で予想した通りだった)。日本・フランスの1〜2ファイル分(4回のopen/close)までは問題なかったが、5回目以降で危険域に達した。

**確立した安全な運用パターン(以後標準)**: `ai_thumbnail_tool.py replace`を1回実行するごとに`osascript -e 'tell application "Adobe Illustrator" to quit'`で必ずIllustratorを完全終了させ、次の`ai`コマンド実行時に自動で新規プロセスとして再起動させる。これにより残り5ファイル(Russia/Spain/Italy/Argentina/表紙、8回のreplace)は1回もハングせず完走した(合計約2.3GB→約670MB、目録の1.84GB→163MBと合わせて冊子全体で旧3.9GB→新0.76GB)。**今後Illustrator自動化を複数回のopen/close操作でループする場合は、この「1操作ごとにquit」パターンを既定にすること。**
