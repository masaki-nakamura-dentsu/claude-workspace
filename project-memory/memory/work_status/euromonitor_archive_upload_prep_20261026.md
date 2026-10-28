---
name: work_status/euromonitor_archive_upload_prep_20261026
description: Euromonitor DL済みデータをGBCクレデン共有チャネルのナレッジ領域へ格納する準備(B案)と個人Mac引き継ぎ
metadata:
  type: project
---
Status: in_progress (2026-10-26 会社Mac→個人Mac引き継ぎ)
- アレココチームの指示で格納先は アレココ DocApp の Tool/21 内に新規フォルダ(2026-10-26ユーザー指定)。
- 決定: B案(PDF1,891+LCP txt/html各905、約2.5GB)。PPT約7.5GBは外す。HTMLは人が読みやすいので残す。
- 準備済み: Euromonitor_レポート保存_20261023/アップロード準備_20261026/Euromonitorアーカイブ_20261023/ (00_はじめに/01_索引.xlsx/02〜06)。
- 引き継ぎ: 同フォルダの 引き継ぎ_個人Macへ_20261026.md、relay personal_mac_inbox task-026(pending)。
- 未了: SharePoint容量確認、契約終了後の共有可否(ライセンス)確認、実アップロード(要許可)、チャネル投稿。
- Opinion 187件はPDF完備(取得不可分はブラウザ印刷PDF)。

追記 2026-10-26 個人Mac: 引き継ぎmd読了(初回0バイトplaceholder→open -gでDL済)。格納用フォルダの件数は 02=1516/03=182/04=187/05=6/06=1810 で一致。ただし全ファイルが Dropbox オンライン専用(0バイト)のため、アップロード前に一括DLが必要(約2.5GB、未実施)。容量・ライセンス確認済みかをユーザーに質問中。アップロードは未実施。relay task-026 は pending のまま。

追記 2026-10-26 個人Mac: ユーザーが容量・ライセンスOKと回答、一括DL許可。Dropbox全件DL完了(0バイト0件)。~/Library/CloudStorage/OneDrive-電通/GBC_アレココ - 添付ファイル/Tool/21/Euromonitorアーカイブ_20261023/ へrsyncコピー完了(3,703件=3,700+索引+はじめに、フォルダ別件数一致、既存Tool/21ファイルは無変更)。OneDriveのクラウド同期完了は未確認。教訓: 一括DLに `open -g` は全ファイルを関連アプリで開くので使わない(Acrobat/Excel/Preview起動、~$ロックファイル混入→削除済)。Web側の件数・html表示検証とチャネル案内依頼は未了。

追記 2026-10-26 個人Mac: ユーザーが同期完了と報告。同期フォルダ側を再確認: 3,703件・0バイト0件・フォルダ別件数一致・ロック/.DS_Store無し・索引3,702行(ヘッダ込)・Wound Care in Japan PDF有。SharePoint Web上の目視検証(Teams検索・html表示)は未了(ユーザー確認待ち)。
