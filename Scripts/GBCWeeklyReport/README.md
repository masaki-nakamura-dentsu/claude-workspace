# GBC週報 x GBC知見 まとめ送付パイプライン

実体は Dropbox `中村正樹/.claude-sync/Scripts/GBCWeeklyReport/` にあり、各Macの `~/GBCWeeklyReport` はそこへのシンボリックリンク（[[outlook_cli]]と同じパターン）。2026-08-12、ICPTokyo2022(個人Mac)で実データ33件を使ってエクスポート〜Excel生成〜メール下書き作成までテスト済み（送信はしていない）。作業を会社Mac(d14461)に引き継ぐ想定でこの場所に配置した。

## 全体フロー
1. `GBC_BOT_PORT=<port> node download_step1_export.js` — Salesforceレポート(`00O7F00000AmEiQUAV`, GBCすべての週報：部長会進行用(過去１週間・優先度高))を共有Botブラウザ経由でエクスポート。メール認証コードが必要な場合はここで停止する。
2. コードが必要な場合: `outlook read` 等でmasaki.nakamura@dentsu.co.jp宛のメール(差出人noreply@salesforce.com、件名「Salesforce で ID を確認」)を自分で確認してよい([[feedback_salesforce_verification_code_standing_permission]]によりユーザーの都度許可は不要)。`GBC_BOT_PORT=<port> node download_step2_enter_code.js <6桁コード>` を実行。`downloads/`にxlsxが保存される。
3. `python3 build_summary.py`(openpyxlが入っているpython3で。引数省略で`downloads/`内の最新ファイルを自動選択) — 各案件行をGBC知見インデックス(`~/Library/CloudStorage/OneDrive-電通/GBC戦略企画部_知見インデックス化・週次まとめ/`、OneDrive経由でどのMacでも同じ内容)と`archive/weekly_snapshots.jsonl`(過去週の同案件アーカイブ、Dropbox同期でどのMacで実行しても共有される)に照合し、「GBC知見アドバイス」列を追加した`output/GBC週報まとめ_<日付>.xlsx`を生成。
4. 内容を中村さんに提示・確認してもらう
5. 確認後、`outlook send --to tkimura@dentsu.co.jp --subject "..." --attach output/GBC週報まとめ_<日付>.xlsx "本文"` で送付（まずは`--dry-run`で下書きを作り、最終確認してから本送信を推奨）

## Macごとの前提条件（会社Mac d14461 で動かす前に確認）
- **共有Botブラウザのport/profileが違う**（[[shared_bot_browser]]）: ICPTokyo2022=port 9227・`~/.chrome-profiles/timetree-bot`、**d14461=port 9226・`/Users/d14461/SalesforceExport/browser_profile`**。上記スクリプトは`GBC_BOT_PORT`環境変数で切り替え可能にしてあるので、d14461では`GBC_BOT_PORT=9226`を付けて実行する（PROFILE_DIRは自動起動時のみ使う値でd14461では既にブラウザが起動している前提のため通常は関係ない）。
- **Node/Playwright実行環境**: [[claude_playwright_setup]]の`~/.local/share/claude-playwright`がd14461にまだ無ければ先に導入。`GBC_BOT_PORT=9226 NODE_PATH=$HOME/.local/share/claude-playwright/node_modules node download_step1_export.js`のように両方の環境変数を付けて実行する。
- **python3のopenpyxl**: ICPTokyo2022では`/usr/bin/python3`(3.9系)にopenpyxlが入っていた。d14461でどのpython3にopenpyxlが入っているか未確認、事前に`python3 -c "import openpyxl"`で確認すること。
- **GBC知見インデックス・週次アーカイブはMac間で自動共有される**: 知見インデックスはOneDrive-電通経由、`archive/weekly_snapshots.jsonl`はDropbox(.claude-sync)経由でどちらのMacで実行しても同じデータを参照・追記する。

## 既知の注意点（2026-08-12の実データテストで判明）
- レポートは仮想スクロールグリッドのためDOM直接スクレイピングはできない → 必ずエクスポート機能(Excel)を使う
- **エクスポートは保存済みレポート定義の「現在の実行状態」を使う。画面上で一時的にフィルタを緩めても、`条件`パネルを開いたまま追加アクション→エクスポートすると元の保存済みフィルタで実行されてしまうことがある。** 一時フィルタを使う場合は、フィルタ適用後に条件パネルを必ず閉じてからエクスポートする。
- **エクスポート形式は必ず「フォーマット済みレポート」(デフォルト)を使う。「詳細のみ」はHTMLベースかつcharset宣言が誤っており日本語が`?`に文字化けする実データ破損バグがある。**
- 「フォーマット済みレポート」のExcelは1〜13行目がタイトル・検索条件ブロック、14行目が本当の列見出し、15行目以降がデータ。**部署名/Dept.・案件名/Item title・フェーズ/Phaseの3列はグループ先頭行にしか値が入らない**（`build_summary.py`が前方補完(ffill)で対応済み）。
- レポートは水曜の日中に活動が随時登録されていくため、朝一の実行だと0件のことがある。夜に実行するのが確実（本番は保存済みの「過去1週間・優先度高」フィルタのまま実行する想定）
- `build_summary.py`のマッチングは簡易な文字n-gram類似度＋クライアント名/エリアタグ一致。プレースホルダー値("ー"等)除外・未回答Q&A除外の対策済みだが、まだ発展途上。送付前に人の目でざっと確認すること

## 木村DMD
tkimura@dentsu.co.jp（木村剛さん）

## 現在の状態(2026-08-12時点)
- Outlook下書きに「【テスト】GBC週報×GBC知見 週次まとめ」が保存済み(木村さん宛、添付ファイルつき、未送信)。本番運用開始時にこの下書きを削除するか使い回すか要検討。
- 本番の週次実行(水曜夜、保存済みフィルタでの正式実行)はまだ未実施。
- Outlookカレンダーへの水曜夜リマインダー設定はClaudeには書き込み権限がないため、中村さん本人が設定する必要がある。トリガーフレーズも未確定。
