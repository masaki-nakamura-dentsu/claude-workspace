---
name: feedback_windows_auto_shutdown
description: 個人Windows(desktop-ryzen5950)は、作業が終わって他に使う作業がなければClaudeが自分でシャットダウンして電気代を節約する
metadata:
  type: feedback
---

個人Windows機での作業(Ollama処理・SSH作業・長時間バッチなど)が終わり、他にWindowsを使う作業が走っていなければ、Claudeが自分からシャットダウンする。聞かずに実行してよい(2026-10-23 中村さんが恒常ルールとして指示)。

**Why:** 起動したままだと電気代がかかる。起こす手段は整備済み(ラズパイ経由WoL、実機テスト済み)なので、落としても再開に支障がない。

**How to apply:**
- 落とす前に確認する: relayの `windows_inbox.md` に `pending`/`in_progress` がない / Ollama `/api/ps` が空 / python・node等の処理が走っていない / 他のMac(会社・個人)のバッチが予約・実行中でない。
- 実行: `.claude-sync/Scripts/windows_power/win_power.sh` の shutdown 系、または `ssh win-home 'shutdown /s /t 5'`。45秒後に `win_power.sh` で「停止中」を確認する。
- 次の予定作業がすぐある(数時間内に使うと分かっている)、または中村さんが使用中・長時間バッチ待ちのときは落とさない。迷えば落とさず一言聞く。
- 落としたら「停止した・起こし方」を1行で伝え、work_statusに記録する。
- 起こし方: `win_power.sh wake`、Ollamaまで上げるなら `win_wake_full.sh`(Ollamaは起こしただけでは上がらない)。詳細は [[personal_windows_wol_via_crd]]。WoLはルーターのパスワード不要で、ラズパイ中継により解決済み(旧「保留」の記述は古い)。関連: [[ollama_qwen_remote_backend]]

関連(同じルールの別記録。スクリプト一覧・本人作業中の確認条件はこちら): [[feedback_shutdown_windows_after_use]]
