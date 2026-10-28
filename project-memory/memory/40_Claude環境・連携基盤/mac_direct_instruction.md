---
name: mac-direct-instruction
description: 会社Mac→個人MacのClaude Codeへ直接指示する仕組み(.claude-sync/Scripts/mac_direct、Dropboxキュー+claude -p常駐)。2026-10-19作成
metadata:
  type: project
---
2026-10-19 中村さん依頼「会社Macから個人MacのClaude Codeに直接指示できるように」。個人Macは出張時以外は常時起動。
- send.sh(送る側): `send.sh "指示"` / `--wait` / `--wait-min N` / `--to company_mac` / `--result <ID>`。キューは `.claude-sync/claude_relay/direct/<宛先>/{pending,running,done}`(Dropbox)。ID=日時-送信元。
- worker.sh(受ける側): 15秒ごとにpendingを1件ずつ `claude -p --permission-mode auto`(cwd=中村正樹、1件60分で打ち切り MACDIRECT_TIMEOUT)、結果は done/<ID>.result.md。受付INFO/完了DONE/失敗WARNをteams_notify(ジョブ名「Mac間指示」)。落ちたら running を pending に戻して再開。ログ ~/MacDirect/worker.log。
- install.sh: launchd com.nakamura.macdirect(KeepAlive)。auto modeでは登録拒否されるのでユーザーがターミナルで実行。10/19時点で個人Macは未登録(personal_mac_inbox task-019 の手順5)。
- 既存の inbox.md(人が許可して実行)とは別系統。こちらは送った時点で実行される。LINE版([[teams_claude_bridge]])と同じauto mode権限。
- 利用例: Agency OS月次チェック(会社Mac)が今月の monthly_update.sh 未実行を検知すると send.sh で個人Macへ実行依頼([[agency_os_deploy_tools]])。
- 2026-10-19 個人Macで install.sh 実行済み(state=active)、会社Macからの往復テスト成功(約25秒、MacBookMN.local/maxakisan)。続けて task-019 の試走を send.sh で依頼(ID 20261019-105237-company_mac)。
- 2026-10-19 失敗と対処: 個人Macのclaude -pが試走をバックグラウンド起動して先に終了→試走も停止(ログ1行のみ)。monthly_update.sh に --detach(perl setsid で別セッション起動)を追加、worker.sh の依頼文に「長い処理は別セッションで起動」を追記(worker再起動までは旧文面)。会社Macから『別セッションで起動して』と送る操作は auto mode に Create Unsafe Agents で拒否された→長時間ジョブの起動・launchd登録はユーザーのターミナルで。登録用 tools/install_monthly_update.sh を作成。
- kickstartでlaunchdジョブを起動させる依頼はauto modeを通る(10/19確認)。長い処理はこの形で頼む。

関連: 「まず send.sh」の運用ルールは [[feedback_use_mac_direct_first]]
