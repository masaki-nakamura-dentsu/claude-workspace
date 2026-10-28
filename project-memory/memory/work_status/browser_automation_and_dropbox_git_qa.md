# ブラウザ自動化準備 & Dropbox/Git同期に関するQ&A

## 2026-08-04T00:00:00+09:00 (概算)
Status: done
What: ユーザーから「今後ブラウザ操作もお願いしたい、準備は何が必要か」と質問。過去のSalesforceレポート自動化・Google Mapsリスト保存の実績([[salesforce_report_download_automation]]、[[google_maps_list_save_automation]])を踏まえ、Chrome debug-port+専用プロファイルでSelenium/Playwrightをアタッチする方式(自動化ツール自身にブラウザを起動させるとログインブロックされるため)を説明。具体的な対象サイト未定、次回具体的な依頼があれば着手する状態。
Next: ユーザーから具体的なサイト/操作の依頼待ち。

## 2026-08-04T00:10:00+09:00 (概算)
Status: done
What: ユーザーから「Claudeの他Mac同期、DropboxでなくGitの方が良いか」と質問。[[dropbox_config_sync]]の実績(2Mac間で正常動作)と、Gitに変える場合の得失(履歴管理は強いが自動即時同期でなくなる、リモート要、追記ログ系ファイルに不向き)を比較して回答。折衷案(Dropbox内でgit initしてローカル履歴だけ持つ)も提示。
Next: ユーザーが「今のままDropboxで」と決定、対応完了。

## 2026-08-04T00:15:00+09:00 (概算)
Status: done
What: ユーザーから「この会話はちゃんと履歴で保存・共有されているか」と質問。生の会話ログ(~/.claude/projects/.../*.jsonl)はこのMacにローカル自動保存されるが他Macには同期されないこと、Dropbox経由で同期されるのはmemory/配下の要約メモとwork_status/ログのみであることを説明。同時に、本来毎応答後に書くべきwork_status/ログを今回の会話で書けていなかった抜け漏れに気づき、この会話用のファイルとして遡って作成(このファイル自体)。
Next: 以後の応答から、通常運用としてwork_status/への記録を再開する。

## 2026-08-04T00:20:00+09:00 (概算)
Status: done
What: ユーザーから「この会話は他Macでも把握するように(決定事項と要約のみでよい)」と明示的に依頼。既にこのファイル自体がDropbox同期対象であり、直前の対応で既に条件を満たしていることを確認・回答。新規の仕組みは不要、[[work_status_protocol]]の標準運用を継続するのみ。
Next: —
