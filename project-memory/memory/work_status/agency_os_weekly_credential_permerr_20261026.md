# AgencyOS週次(クレデン) PermissionError復旧 2026-10-26
Status: done
- 10/26 8:30 launchd実行が全112ファイルPermissionErrorで失敗→90%ガードで反映せず(Skill/Difyは無傷)。
- 調査: 対話・launchd submit(別ジョブ)ともOneDrive同期フォルダ(~/Library/CloudStorage/OneDrive-電通/GBC - 02．クレデン共有チャネル)の100 pptxを全部読めた。bashのheadは launchd下で Operation not permitted になるが、python3(Python.framework 3.14)は読める。→原因は断定できず、起動直後のFile Provider/権限が一時的に未準備だった可能性。
- 10:13 kickstartで再実行→108カード・変更なし・last_run=2026-W44。
- 対策: weekly_credential_update.sh に事前読取チェック(5回×60秒リトライ、駄目ならERROR)を追加。
