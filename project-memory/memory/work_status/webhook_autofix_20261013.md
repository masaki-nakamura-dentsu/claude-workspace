# Webhook自動修復 2026-10-13

## 2026-10-13T08:45:00+09:00
Status: done
What: 旧形式Webhook通知2件(mid=1791846745768 / 1791846894541)を受領、両方とも**既に解消済み**と判定。
1) 「カレンダー同期: フロー停止の疑い」(08:12発報) → 同日08:32に新スナップショット `calendar_snapshot_20261012040314_5000.csv` を受信し `work_status/calendar_sync_health.md` に Status: done が記録済み。Power Automateフローは生存。9/27・10/5と同じ「週末に溜まって月曜朝に届く」パターンで、閾値ベースの誤検知。
2) 「週次AIダイジェスト: 実行失敗(self-chat not found)」(08:14発報) → この個人Macの08:00実行は**成功**(`digest_backup_stdout.log`: posted to self-chat, archived AI関連Teams_週次ダイジェスト_20261012.md、7 topics / state `last_digest_run=2026-10-12T23:00:05Z`)。失敗したのは別マシン(会社Mac)側の二重実行で、Teams左レール未描画によるもの。原因・対策は同日08:20〜08:30の別セッションが既に `weekly_ai_digest.py` に実装済み(バックアップ `weekly_ai_digest.py.bak_202610130830` あり): STARTUP_WAIT_S=180の起動待ち / 左レール再読込を30秒×10回リトライ / 投稿直前の状態ファイル再読込による二重実行ガード。
→ 追加の修正・再実行は不要。relay投入も不要(同件が既に対応済みのため)。
Next: 次週月曜(2026-10-19)の自動実行で、会社Mac側が二重実行ガードにより正しくskipするか、またはリトライで成功するかを確認。カレンダー同期の「週末滞留→月曜朝に回復」パターンは誤検知が続くため、閾値(現在115h前後で発報)の見直しを検討。

## 2026-10-13 15:4x KGI/KPIレポート定期保存 PDF保存失敗(会社Mac N650893)
- Status: done
- 原因: Power BI Serviceの新リボン(プレビュー、オン)でUIが変わり「エクスポート」ボタンが無くなり「PDF」ボタン直押しに。09:40の失敗は別件(ネット切断 ERR_INTERNET_DISCONNECTED)。
- 対応: ~/PowerBIExport/export_kgikpi_to_sharepoint.py を新旧両UI対応に修正(バックアップ .bak_202610131600)。`--force`で再実行し成功: KGIKPIレポート_20261013.pdf (2,527,011 bytes) をArekokoへ保存、state.json更新。
