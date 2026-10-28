# Teams⇔Claude Code橋渡し (2026-10-18)
Status: done(LINE版のみ稼働。Teams版は10/18削除)
- LINE希望→3択でTeams自分宛てに決定。bridge.js 作成、読み取りセレクタ確認済み。詳細 memory teams_claude_bridge.md
- 10/18: entry.line.bizがログイン後404→manager.line.bizの「作成」ボタン経由を案内
- 10/18: Messaging APIチャネル作成済み(Channel ID 2012067839)。チャネルシークレットは本構成では未使用(チャットに貼られたので再発行を推奨済み)。次はアクセストークン発行・本体の書き込み許可待ち
- 10/18: LINE Developersは英語表示。Providers一覧→プロバイダー→チャネル→Basic settings/Messaging APIタブの順に案内
- 10/18: トークン発行済み。Write()ルールは不可→Edit(~/Scripts/line_claude_bridge/**)を案内
- 10/18: Edit(~/Scripts/line_claude_bridge/**)許可後に line_bridge.js 書き込み成功。~/.config/line_claude_bridge.json にKEY/pairCode作成済み、gasUrlとトークンはユーザー入力待ち。次はGAS公開→設定→試験起動→launchd(com.nakamura.lineclaudebridge)
- 10/18: 手順3の保存コマンドがheredoc+input()でEOFError(標準入力が台本に使われるため)→zsh readで受けてenv経由で保存する版を再提示
- 10/18: GASのURLの場所を質問された→デプロイを管理で確認する手順を案内
- 10/18 09:33: LINE版 試験成功(本人登録・テスト応答。Claude処理約10秒)。残: 応答メッセージOFF、launchd com.nakamura.lineclaudebridge登録(ユーザー実行)
- 10/18: 再起動時の挙動と危険性を説明。Teams版に誤送信防止・起動待ちを追加(再起動はユーザー実行)
- 10/18: Teams版を削除(launchd解除・plist・フォルダ削除、プロセス無しを確認)
- 10/18: 個人LINEのメッセージを読めるか質問→公式APIでは不可。転送/トーク履歴txt書き出し/(非推奨)LINE Mac版の画面読み取りを提示、回答待ち
- 10/18: 個人LINE読み取り方法を再検索(非公式MCPあり=BANリスク、公式Agent i in chatは年内予定)→回答、方式選択待ち
- 10/18: 個人LINE読み取りは公式Agent i待ちで保留と決定。本タスク完了
