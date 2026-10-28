---
name: teams_claude_bridge
description: LINE公式(MasakiAI)から個人MacのClaude Code(auto mode)を動かす橋渡し(~/Scripts/line_claude_bridge、launchd常駐)。Teams版は遅いため10/18に削除済み
metadata:
  type: project
---
2026-10-18、「LINEでClaude Codeとチャットしたい」依頼。LINE公式アカウント方式/Claude公式Remote Control/Teams自分宛ての3択を出し、ユーザーは**Teams自分宛て**を選択([[line_cli_attempt_paused]]の公式アカウント作成の手間を回避)。権限は「ふだんと同じ(auto mode)」をユーザーが明示許可。

- 本体: `~/Scripts/teams_claude_bridge/bridge.js`(node+Playwright)。会社用ブラウザ dentsu-work-bot / port 9231 の既存Teamsタブ(自分宛てチャットを開いた状態)にCDP接続、newPageしない。10秒ごとに `[data-tid="chat-pane-message"]` の `data-mid` を見て新着を検出、本文は `#content-<mid>`。自分宛て判定は `[data-tid="chat-title"]` に「(You)/(あなた)」。
- 書式: `cc 本文`(全角ｃｃ・全角スペース可)。`cc /new` で会話リセット、`cc /status` で状態。返信は「🤖 」始まり(ループ防止)、3500字で分割。
- 実行: `claude -p --permission-mode auto --session-id/--resume <uuid>`、cwd=Dropbox中村正樹、タイムアウト20分、`--append-system-prompt` で「Teams webhook通知は送らない・簡潔に」。状態 `state.json`(sessionId, lastMid)、ログ `bridge.log`。異常は共通送信口 teams_notify で WARN。
- 自分(Claude)からのWrite/起動はauto modeに「Create Unsafe Agents」等で拒否→ユーザー許可後Writeは通ったが、起動(node bridge.js)は拒否。起動・launchd登録(`~/Library/LaunchAgents/com.nakamura.teamsclaudebridge.plist`、KeepAlive)はユーザーのターミナル実行で渡した([[feedback_auto_mode_unattended_agent_launchd]])。
- 注意: 同じ自分宛てチャットにSalesforceの事前告知投稿([[salesforce_report_download_automation]])もある。Teamsタブを別チャットへ移すと監視が止まる。teams_cli の `ensureLoggedIn`(rail要素)は2026-10-18時点の英語UIで失敗していた(未修正)。

## 2026-10-18 追記: 速度改善とLINE版
- 所要時間を計測: Claude自体は約6秒(起動4秒+回答2秒)。遅れの主因は監視間隔10秒と、受付メッセージの入力完了を待ってからClaudeを起動していたこと。POLL_MS 2000、Claudeを受付投稿と並行で起動するよう修正。反映は `launchctl kickstart -k gui/$(id -u)/com.nakamura.teamsclaudebridge`(ユーザー実行)。bridge.js のEditはauto modeで通った。
- トークン: 監視自体はトークン0。1メッセージ=claude -p 1回で、普段の対話と同じ文脈(CLAUDE.md+MEMORY)を読む。間が空くとキャッシュ切れで読み直しになるのも普段と同じ。長い会話は `cc /new` で軽くなる。
- LINE版: ユーザーが「LINE公式も試したい」→権限は auto mode を再度明示許可(公開入口ができる点も承知)。構成 LINE→GAS中継(`~/Scripts/line_claude_bridge/gas_Code.gs`、URLの合言葉?k=で認証、Script Propertiesにキュー)→Macが3秒ごとに取得→claude -p→reply(失敗時push)。本人だけ実行(「pair 合言葉」でuserId登録)。設定は `~/.config/line_claude_bridge.json`(600)。
- line_bridge.js: 許可後もWrite拒否→ユーザーが /permissions に `Edit(~/Scripts/line_claude_bridge/**)` を追加して書き込めた(Write()ルールは無効、絶対パスは~か//始まり)。
- 2026-10-18 LINE版 試験成功。公式アカウント名 MasakiAI、Channel ID 2012067839、本人userId登録済み。launchd: com.nakamura.lineclaudebridge(KeepAlive)。応答メッセージ(自動応答)はOFFにする必要あり。
- 2026-10-18 安全性の見直し: Teams版 postMessage に「自分宛てチャット以外なら送信中止+WARN」を追加(処理中にタブが他人チャットへ移ると本人名義で誤送信する恐れ)。起動時にブラウザ未起動なら終了せず30秒ごとに待つ(KeepAliveでの通知連発防止)。LINE版の弱点: GASは署名を検証できないので、URL+KEY(チャットにのみ記載、メモリには書かない)が漏れると偽メッセージ注入・キュー読み取りが可能。会社メール等の社内情報をLINE経由で出さないよう注意喚起済み。
- **2026-10-18 Teams版を削除**(ユーザー指示「TeamsはLINEより遅いので削除」): launchd com.nakamura.teamsclaudebridge をunload、plistと ~/Scripts/teams_claude_bridge/ を削除。以後はLINE版のみ稼働。上のTeams版の記述は経緯として残す。再作成を提案しない。
- 2026-10-18 個人LINEのトークをClaudeに読ませる方法を再調査: (1) 公式は「Agent i in chat」(2026/7/2発表、2026年内提供予定、1対1/グループでメッセージ要約等)が未提供。(2) 非公式MCP(stickerdaniel/line-mcp-server、line-selfbot-mcp、betterLINE)はLINE非公開プロトコルでAndroidサブ端末としてログイン。READMEでアカウント制限・BANの恐れを明記、開発中・星1。家族連絡の本アカウントなので非推奨とした。(3) 現実解は転送/トーク履歴書き出し。
- 2026-10-18 結論: 個人LINEの読み取りは公式Agent i in chatの提供を待つとユーザーが判断。転送まとめ修正・書き出しフォルダは保留。非公式MCPは再提案しない。Agent i提供開始の話が出たら案内する。
