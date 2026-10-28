# 個人Mac(ICPTokyo2022)ディスク空き容量確保

## 2026-08-19T00:00:00+09:00 (JST, おおよそ)
Status: done
What: 空き容量79GB→119GB(約40GB回収)。調査→ユーザー確認を挟みながら実行。削除内容: After Effectsディスクキャッシュのうち8/12より前の分(20.18GB、7/5更新の大量ファイルが主)、Chromeキャッシュ(7.5GB)、ollama(brew uninstall + ~/.ollama削除、4.9GB)、Homebrewダウンロードキャッシュ(brew cleanup、230MB)、LibreOffice(brew cask経由でアンインストール)、Steam/Amazon Cloud Driveの残骸(アプリ本体は既に無く設定ファイルのみ残存、計2.7GB)。保持したもの: Camera Raw キャッシュ、DxO PureRAW(使用中と確認)、AEキャッシュの直近7日分(25.9GB、作業中のプロジェクトの可能性)。
Next: — (完了。ユーザーが今後さらに増やしたい場合はOneDrive-電通(25GB)/Dropbox(47GB)のオンデマンド化が次の候補として残っている)

## 2026-08-23T10:10:00+09:00 (JST)
Status: done
What: 前回(8/19)119GBまで回収した空きが4日で10GBまで急減(-109GB)していた件に対応。調査の結果、Chrome code_sign_clone一時ファイルが12GB新規蓄積(自動操作でChromeプロセスを頻発起動するのが一因と推定)、AEキャッシュ26GB・ACRキャッシュ8GBが再蓄積、Chrome File Systemサイトデータが8.8GB(正体不明)を確認。ユーザー許可を得てChrome code_sign_clone(12GB)とChrome On-Device AIモデル(8GB)を削除、空き10GB→21GBに回復。OneDriveの「GBC_アレココ-サイトドキュメント」フォルダ(21GB)をユーザーがFinderで「ダウンロードを削除」実行済みだが、stat確認で49ファイル中1件しか実際には回収されておらず、macOSの遅延式Purgeable Space方式のため即時反映されないことが判明(詳細は[[mac_disk_space_cleanup_technique]])。ユーザーは急がず自動回収に任せる方針で終了。未着手のまま残したもの: Adobe系キャッシュ約34GB、Homebrew/pip約1GB、Chrome File Systemサイトデータ8.8GB。
Next: 次回ディスク逼迫時はまずChrome code_sign_clone(/private/var/folders/*/*/X/)を確認すると即座に回収できる。この「短期間で急減する」パターン自体が気になるので、次回は原因(自動操作の頻度、Premiere/AE利用パターン等)をもう少し深掘りする余地あり。

## 2026-09-27 再調査（個人Mac）
Status: done (Camera Rawキャッシュのみ保留)
空き17GB/460GB(96%)。候補: AEキャッシュ26G(26.3旧版分)、Chrome code_sign_clone 6.3G、Camera Rawキャッシュ8G、Downloads大物(IMG_0136.MOV 9.1G, wav 1.9G)、Lightroom旧残骸(v15-4.lrcat-data 11G[6/20以降未更新・lrcat本体なし]、v13-3 Helper 5.9G、競合コピーlrcat 5.1G)、Chrome Default/File System 8.8G、CurrencySortML 10G、Homebrew/pip/playwright ~3G。削除はユーザー承認待ち。
実施(ユーザー承認済): AE 26.3キャッシュ, code_sign_clone, Homebrew/pip, Lightroom旧残骸3点(v15-4.lrcat-data, v13-3 Helper, 競合コピーlrcat+shm/wal)を削除。空き17→62GB。保留: Camera Rawキャッシュ8G(Photoshop起動中)、ms-playwright 1.1G(実体はブラウザ本体で自動化が依存しうるため)。ユーザー指示: Downloadsは本人が整理、CurrencySortMLは削除禁止。
追加調査(同日): システムデータ151G/macOS49G/iOSファイル34Gの内訳質問に回答。スワップ使用22G(稼働17日)→再起動推奨。iOSファイル=iPhoneバックアップ(MobileSync、VSCodeにフルディスクアクセスなく中身確認不可)→設定画面ⓘから本人削除推奨。macOS49Gは削減不可。
