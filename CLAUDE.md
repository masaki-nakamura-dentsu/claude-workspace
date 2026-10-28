# Global preferences (Masaki Nakamura)

ルールの要点だけを置く。経緯・根拠・詳細は per-project memory。旧全文は `40_Claude環境・連携基盤/global_claude_md_full_history.md`（Dropboxワークスペースのmemory内）。

## 基本
- 既定は日本語で返答する。経緯や理由の説明は短くし、成果物の質は落とさない。
- Claude Codeだけで完結できる作業は最後までやる。止めて聞くのは、本人しか決められない判断・破壊的な操作・推測できない情報のときだけ。
- 恒常的な好みは、ここか per-project memory に自分から記録する。
- 有料サービスへの課金や、共有SharePointの権限変更は事前に確認する。

- 会話が長くなって `/clear` や `/compact` を勧めるときは、直前に work_status へ記録し、クリア後に最初に打つ文（例:「JCI案件インポートの続き。work_status/〇〇を読んで」）も必ず添える。全作業・会社Mac/個人Mac共通。

## 文脈・データ
- メール/Teams/ファイル/過去チャットは、全チャット共通の文脈として扱う（本人が「独立」と言ったときだけ例外）。
- Outlook/Teamsの履歴は `~/OutlookExport/parsed_emails.jsonl`、`~/TeamsExport/data/teams_messages.jsonl`（API経由のアクセスはない）。詳細は memory `local_work_data_export`。
- 「アクセスできない」と言う前に、既存の経路（共有botブラウザ/CDP、ローカルexport）を試す。何を試したかも伝える。
- 自分で設定した自動化のパラメータ（期間・頻度・閾値・出力先など）はすぐ memory に記録し、聞かれたら memory から答える。

## 記録
- 毎回の返答後に、そのプロジェクトの `memory/work_status/` に短い作業ログを追記する（削除禁止、完了時は `Status: done`）。手順は memory `work_status_protocol`。
- セッションが終わるたびに、やったこと（project）と好み・指摘・失敗（feedback）を memory に残す。
- memoryはObsidianで読める形にする（Markdown + `[[name]]`）。vault=各プロジェクトのmemoryフォルダ。
- 週次の自動memoryレビュー（月曜8:30、個人Mac）。重複の統合のみ、古さを理由に削除しない。memory `memory_weekly_review_automation`。

## ファイル
- 納品済みファイルの改訂は上書きせず別名で保存する。末尾が `YYYYMMDD` でなければ `_YYYYMMDD` を付け、既にあれば今日の日付に置き換える。同じ日の2回目以降は `_01`, `_02`…。
- PPTXを作成・改訂したら、すぐ `open <path>` で開く。
- 電通フォーマットのPPTXを作るときは、PowerPointの「セクション」(sectionLst)と未使用レイアウトを保存前に必ず削除する(依頼がなくても全タスク共通)。memory `feedback_pptx_prune_unused_sections`。
- Dropboxのオンライン専用ファイル（0バイト、`com.dropbox.placeholder`）は、まず `open -g` などで自分でDLを促し、だめなときだけ本人に頼む。

## 通知（Teams webhook）
- 質問で止まるとき（`[WAIT] …`）と作業完了時（`[DONE] …`）に送る。対話セッションからは `[ERROR]` を送らない。
- スクリプトは共通の送信口 `.claude-sync/Scripts/notify/teams_notify.{py,sh,js}` を使い、URLを直書きしない。規則は `.claude-sync/Scripts/notify/NOTIFY_RULES.md`、細かい注意点は memory `teams_webhook`。

## バックグラウンド・自動操作
- バックグラウンド処理の停止に自分で気づいたら、Teamsに通知し、再開するか確認する。ユーザーが気づくのを待たない。
- 長時間のバックグラウンド作業は、開始時に進捗の確認方法（ログ/状態ファイル）を決め、聞かれる前に節目で進捗（完了数/残り/止まっていないか）を伝える。memory `feedback_long_job_progress_reporting`。
- スクリーンショット頼み・座標クリック頼みのGUI操作（Dify/Figmaのキャンバスなど）は、着手前に許可を取る。headless/テキスト経由を優先する。
- ブラウザ自動操作でOSのフォーカスを奪わない（既定はheadless/background）。
- 作業が終わったら、自分が開いたタブは `page.close()` で閉じる。常駐タブ（Teams/Outlook等）とウィンドウの最後のタブは残す。`browser.close()` は使わない。
- ユーザーに手作業を渡すときは、確認方法（貼り付けてすぐ使えるテスト文と、正しい結果/壊れている結果の見分け方）も添える。

## マシン・環境
- 3台：会社Mac(d14461)、個人Mac(ICPTokyo2022/maxakisan)、個人Windows(maxak)。
- Dropboxワークスペースで作業を始めるときは `.claude-sync/claude_relay/<machine>_inbox.md` の `Status: pending` を確認する。見つけたら内容を示し、許可を得てから実行する（なければ何も言わない）。memory `mac_handoff_relay`。
- 大量の要約・分類など軽い作業はリモートOllama（192.168.0.11:11434, `qwen3.8:27b`）に回せるので、該当しそうなら事前に提案する。memory `ollama_qwen_remote_backend`。
- 応答終了の通知音は `~/.claude/settings.json` の Stop hook（afplay）。macOS通知は使えないので再提案しない。
- claude.ai コネクタ（Gmail等）は既定でオフ（`ENABLE_CLAUDEAI_MCP_SERVERS=false`）。必要なときだけ一時的にオンにする。memory `mcp_on_demand`。
