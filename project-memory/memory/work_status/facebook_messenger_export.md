# Facebook Messenger エクスポート取り込み

## 2026-07-30T18:10:00+09:00
Status: done
What: ユーザーがFacebook公式「情報をダウンロード」を毎日自動実行するよう設定し、GoogleDriveに保存されるようにした。パーサースクリプト(`~/FacebookExport/sync_facebook_export.py`)を新規作成し、Facebook独自の文字化けバグ（UTF-8バイト列をLatin-1として誤エンコード）を修正する処理を実装。初回実行で34件のメッセージを`facebook_messages.jsonl`に取り込み成功、GoogleDrive側の処理済みフォルダも自動削除された。3時間おきに自動実行するlaunchdジョブ(`com.nakamura.facebooksync`)も設定・登録済み（GoogleDriveがこのMac限定のため、このMac専用のジョブ）。[[facebook_messenger_export_setup]]に詳細記録。
Next: 次回のGoogleDrive自動ダウンロード後、launchdジョブが正しく拾ってマージ・削除しているか確認する。LINE/WhatsAppは手動エクスポート方式でまだ未着手（ユーザーからの続報待ち）。

## 2026-07-30T19:00:00+09:00
Status: in progress
What: ユーザーから「以前ダウンロードした過去のFacebookデータも全部含めてほしい」との依頼。2つの過去アーカイブを発見: (1) Dropbox「Photographer/SNS下書き」内の2026-07-29付フルエクスポート（HTML形式、507スレッド）→ HTML用パーサー`backfill_facebook_html_export.py`を新規作成し実行、18,776件を新規マージ成功（読み込みエラー0件）。データ範囲は2020-02-12〜2026-07-30、計18,805件に拡大。(2) Dropbox「MyDocument家の事/facebook履歴」内のより古いアーカイブ(779、1,545スレッド)→ ZIPも展開済みフォルダも実体0バイトで、Dropboxのオンライン専用プレースホルダーと判明（`com.dropbox.placeholder`属性で確認）。dd/brctl等コマンドラインからの強制ダウンロードを試みたが失敗（brctlはApple iCloud専用でDropboxには無関係と判明）。ユーザーにFinderからの手動ダウンロードを依頼済み。[[facebook_messenger_export_setup]]に詳細記録。
Next: ユーザーが779アーカイブをDropboxでダウンロード完了したら、同じbackfill_facebook_html_export.pyで取り込む。

## 2026-08-07T09:10:00+09:00
Status: blocked
What: ユーザーから「ちゃんと読み込めているか確認して」との依頼で、会社Mac(d14461)から`.claude-sync/data-export/FacebookExport/`(Dropbox経由の個人Macからのコピー)を点検。データ自体は正常(18,841件、文字化けなし、2020-02-12〜2026-08-03)だが、**2026-08-03 10:41を最後に4日間新規メッセージが取り込まれていない**ことが判明。個人Mac(ICPTokyo2022, ユーザー名maxakisan)側のlaunchdログに`OSError: [Errno 11] Resource deadlock avoided`(GoogleDrive処理済みフォルダのrmtree失敗)が記録されており、それ以降は新しいfacebook-*サブフォルダがGoogleDriveに現れていない模様。DropboxのCalendarExportは8/6まで新しいので同期経路自体は健全、Facebook取り込み処理固有の問題と切り分け済み。[[facebook_messenger_export_setup]]に詳細記録・MEMORY.md索引も更新済み。
Next: 個人Mac(ICPTokyo2022)で直接、GoogleDriveに新しいmeta-*/facebook-*フォルダが届いているか、Meta側の自動エクスポートスケジュールがまだ有効かを確認する必要あり(会社Macからは確認不可)。
