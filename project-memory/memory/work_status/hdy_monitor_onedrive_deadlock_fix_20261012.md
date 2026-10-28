# HDY定点観測 news_rss連続失敗の修正 (2026-10-12, personal_mac)
Status: done
- Teams通知「news_rssが2回連続失敗」を調査。原因は OneDrive複製のResource deadlock(収集自体は成功)
- core.py: mirror_to_onedrive()でcp+timeoutを使い、失敗しても例外にしない／run.py: resync_onedrive_mirror()で古い複製を再試行
- 手動実行で検証済み(news_rssが成功、12件を再複製)。詳細はメモリ hakuhodo_overseas_intel_monitoring

## 追記 2026-10-14
- sf収集はDropboxプレースホルダ(0バイト)xlsxを掴むと `Excel file format cannot be determined` で落ちる。0バイト除外+engine明示で対処済(collectors.py)。
- 同ログで `OneDrive複製: 9/9件失敗(次回再試行)` が継続中(別件・未解決)。
