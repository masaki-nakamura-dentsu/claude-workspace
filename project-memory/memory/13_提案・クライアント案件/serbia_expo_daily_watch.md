---
name: serbia_expo_daily_watch
description: ベオグラード万博2027の日次ウォッチ(現地メディア+公式、Teams通知)の設定値・場所・運用
metadata:
  type: project
---

2026-10-26設定。会社Mac launchd `com.nakamura.expowatch` が毎日9:00に実行。関連 [[serbia_expo_beograd_2027_bid]] [[automation_schedule_overview]]

- スクリプト: `.claude-sync/Scripts/expo_watch/{run.sh,expo_watch.py,state.json}`。`claude -p`(WebSearch/WebFetch/curl)で収集→JSON→整形。
- 収集方針: 公式(Expo公式・政府・鉄道・JETRO/大使館)最優先、次にセルビア現地メディア(RTS/Tanjug/B92/N1/Blic/Kurir等)。セルビア語(ラテン・キリル)で検索。交通・イベント・チケット・建設・日本館が重点。
- 期間: 通常は直近7日、初回のみ45日遡及。既報URLは state.json で除外(新着のみ報告)。
- 投稿先(2026-10-27変更): Teamsチーム「🇷🇸ベオグラード万博 行催事(制作)」の `05_関連情報共有` チャンネルへ直接投稿。先頭でチームに@メンション、続けて「今日の要点 (日付)」+新着記事(AI Tips週報と同じ紫見出し/赤強調/緑の意味合い/出典リンク)。新着なしの日は投稿せず、自分宛Webhook `[INFO] 万博ウォッチ: 更新なし` のみ。成功時は自分宛に `[OK]`。
- 投稿方式: 共有ボットブラウザ(CDP 9226)のTeams Web版。URLは `teams.microsoft.com/_#/l/channel/...` 形式(`/l/channel` だとデスクトップアプリ起動ページで止まる→ユーザーから「アプリでなくブラウザで」と指示)。@メンションは `@ベオグラード` と打ち `data-tid^=autocomplete-picker-item-` の候補をクリック。下書きはタブをまたいで残るので先にクリアする。
- 動作確認は必ず `EXPO_DRY=1` で(送信直前で止まる)。
- Dropbox出力:  `Work/Client/Serbia_Expo/日次レポート/expo_watch_YYYYMMDD.md`(全文)+ Teams `[INFO] 万博ウォッチ: 新着N件`(上位6件の要約)。失敗時 `[ERROR]`。
- ログ: `~/expo_watch_logs/`。
**制約:** 会社Macが落ちている日(休日の自動シャットダウン)は実行されない。WebFetchが接続拒否になることがあり、記事の日付未確認の項目が出る。

**失敗談(2026-10-27):** 動作確認用に入れたつもりのDRYガードが実際はコードに入っておらず、テスト実行でチャンネルに本日分の重複投稿をしてしまった。教訓: 本番へ送信しうるテストは、ガードがファイルに入ったことをgrepで確認してから走らせる。
