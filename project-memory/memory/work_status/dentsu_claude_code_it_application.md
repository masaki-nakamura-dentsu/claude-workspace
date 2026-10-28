# dentsu社内 Claude Code申請・セットアップ調査

## 2026-08-25T00:00:00+09:00 (概算)
Status: done
What: 「社内でClaude Codeの仕様の申請方法は？」に対し、Outlook/Teamsエクスポートを検索して2026-06-10の実際の承認済み申請記録（特殊IT申請エージェント経由、申請No. d14461-20260610091702）を特定。手順・利用条件・制約をreference memory `dentsu_claude_code_it_application_process.md` に保存し、MEMORY.mdにも索引追加。続けて「特殊IT申請エージェントのURLは？」に対しM365 Copilot Chatの直リンクを発見し同メモリに追記。
Next: —

## 2026-08-25T00:10:00+09:00 (概算)
Status: done
What: PostToolUse hookからMEMORY.mdサイズ超過(19.6KB)の警告を受け、31KB→14.7KBまで圧縮(各エントリの説明を大幅短縮、詳細は個別トピックファイル側に温存、情報の削除なし)。
Next: —

## 2026-08-25T00:20:00+09:00 (概算)
Status: done
What: 「同僚がWindowsでセットアップしようとしている、初期設定は？」に対し追加調査。2026-06-10の別メール(B243案件)で、本人が一度は「アプリインストール」タスクフォース審議も申請しかけたが「VS Code内でClaude Codeを使えば目的を果たせる」と分かりキャンセルした経緯を発見(重要: 会社PCではVS Code標準支給、その中でCLIを使うなら重い方の審議は不要)。また会社Mac側の実際の`~/.npmrc`(社内プロキシ proxy1.dentsu.co.jp:8080)を確認し、Windows側でも同様のnpmプロキシ設定が必要になる可能性が高いと回答。Windows側での実際の設定記録は見つからず、Mac側の実績からの類推である旨を明記して回答した。
Next: 同僚が実際にセットアップして別の詰まりどころが出てきたら、`dentsu_claude_code_it_application_process.md`を更新する。
