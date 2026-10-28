
## TimeTree日次チェック 失敗の自動修復 (2026-10-18 07:30受信 / 07:50対応)
Status: done
- 症状: `tt_scrape_weeks.js` の `button:has-text("今日")` クリックが element is not visible で失敗(本日が初発、10/17までは正常)。
- 原因: botプロファイルChromeのウィンドウが 500x481 まで縮んでおり、TimeTreeがナロー(レスポンシブ)レイアウトに切替わって 今日/マンスリー/ウィークリー ツールバーが hidden(DOMには存在)。ログイン切れではない。
- 対応: `~/.local/share/claude-playwright/tt_scrape_weeks.js` を修正(バックアップ `*.bak_202610180745`)。goto直後に innerWidth<1100 or innerHeight<700 なら CDP `Browser.setWindowBounds` で 1440x900 に戻してからクリック。フォーカスは奪わない。
- 検証: scrape単体で week0-13 取得成功 → `timetree_check.py` 再実行で report_2026-10-18.md 正常生成(夜の予定候補24件/登録漏れ候補2日: 11-25 大塚会、12-30 体育会忘年会)。
