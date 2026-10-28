# Facebook Messenger 読み込み確認 (2026-08-07)

## 2026-08-07T08:50:00+09:00
Status: done
What: Facebook Messenger自動取込の稼働確認依頼。8/3 23:18で停止(18,841件)しているのを発見。原因は、facebooksync単独launchdジョブが統合デーモン`~/SyncDaemon/sync_daemon.py`(com.nakamura.syncdaemon)に置き換わっており、`sync_facebook_export.py`の処理済みフォルダ削除(`shutil.rmtree`)がバックグラウンド実行時に`Errno 11: Resource deadlock avoided`で毎回失敗し、同じフォルダを再試行し続けるループに陥っていた。手動(インタラクティブ)実行で解消: 20件追記、18,861件、最新2026-08-06 17:06まで反映。[[facebook_messenger_export_setup]]に詳細追記済み。
Next: 統合デーモン側のコード修正(rmtreeにretry/timeout追加)は未着手 — 次回また停滞したら同じ手動再実行で対処可能。

## 2026-08-07T09:05:00+09:00
Status: done
What: 「エラーになっても自動的に修復して再実行するように」との依頼を受け、`sync_facebook_export.py`にcalendar/email同期スクリプトと同じ実績あるパターン(subprocess+timeout+retry, 5回×5秒/20秒タイムアウト)を適用。メッセージファイル読み込みとフォルダ削除の両方をこの仕組み経由に変更し、削除が全リトライ失敗しても例外を投げず「次回自動再試行」としてログして処理を継続するよう修正(以前は1フォルダの削除失敗が同一実行内の他フォルダの削除もブロックしていた)。py_compileと合成テストフォルダで読み込み・削除とも動作確認済み。`sync_daemon.py`はスクリプトを毎サイクル再読み込みするため、稼働中のデーモン(PID確認済み)は再起動不要で次サイクルから新コードが有効になる。`~/FacebookExport`はDropbox共有シンボリックリンクのため会社Mac側にも自動反映。[[facebook_messenger_export_setup]]に詳細追記済み。
Next: 実運用下で数サイクル様子を見て、`削除失敗（次回自動再試行）`ログが解消されずに残らないか確認する。
