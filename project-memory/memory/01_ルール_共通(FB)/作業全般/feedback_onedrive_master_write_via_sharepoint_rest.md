---
name: feedback-onedrive-master-write-via-sharepoint-rest
description: OneDrive上の共同編集pptx(正本)を更新するときは、ローカル同期フォルダへcpせずSharePoint RESTで直接上書きし、サーバー側の更新日時・サイズで確認する
metadata:
  type: feedback
---
OneDrive同期フォルダ内の正本をcpで書き換えると、Officeの共同編集と衝突して「アップロードがブロックされました」になり、自分の画面では新しく見えても他の人には古い版のまま(2026-10-13 Nidec)。ユーザーに「他の人から見ると反映されていないかも、やり直して」と言われた。

**Why:** Officeファイルの同期はOffice側が握っており、外部からの書き換えはアップロードされない。PowerPointでsaveしてもsaved=trueになるだけでサーバーは変わらなかった。

**How to apply:** 正本の更新は、会社Macの共有ボットブラウザ(9226)からSharePoint REST `GetFolderByServerRelativePath(...)/Files/AddUsingPath(decodedurl=...,overwrite=true)`(X-RequestDigestは/_api/contextinfo)で上書きする。スクリプト雛形=Work/Client/Nidec/作業履歴フォルダ/spupload.js(~/.local/share/claude-playwrightで実行)。事前に `$expand=LockedByUser` でロックを確認(本人のロックでも423になる。PowerPointを閉じても10分以上外れないことがある→開いている場所を閉じてもらう)。完了報告はサーバー側のTimeLastModified・Length・UIVersionLabelを確認してから。cpしたファイルはDropboxのxattr(com.dropbox.attrs/quarantine)も持ち込む。[[nidec_components_naming_pitch]]

**ロックが外れないとき(2026-10-13)**: 共同編集者がいるとRESTは423のまま。ユーザーの許可(今回限りと明示された)を得て、PowerPointで正本(OneDriveパス→クラウド文書として開く)を共同編集で開き、AppleScriptで変更を書き込んで保存→サーバーDLで反映を確認、の順で成功。AppleScriptの要点: `make new shape`の戻り値は使えず `shape (count of shapes of s) of s` で取り直す / 書式は `set ff to fill format of sh` のように変数に取ってから設定 / 文字範囲(characters 1 thru n)は不可、`character k of tr`を1文字ずつ / 東アジア文字は `east asian name` も設定しないと明朝になる / 改行はCRで返るのでタイトル照合は1行目だけ。雛形=作業履歴フォルダ/nav_applescript.py。共同編集ではPowerPointの許可が毎回必要か確認すること。

**スライド追加をロック中の正本に入れる(2026-10-13 16時)**: ユーザー許可のうえ、作成済みpptx(src)と正本(dst)を両方PowerPointで開き、`copy object slide N of src` → `go to slide (view of document window) number pos` → `paste object view` で貼り付け(貼った位置の直後に入る。ノートも残る)。雛形=作業履歴フォルダ/paste_slides.applescript(引数: src名 dst名 直後に入れるスライドのタイトル src番号)。AppleScriptでは before / v / w / x など予約語と衝突する変数名は使えない。document windowsはインデックスで回し`name of (get presentation of dw)`をtryで比較。作業用コピー同士で先に試してから本番に使う。ユーザーは自分のMacのPowerPoint操作を許可する場合がある(10/13は2回とも都度許可)。

**REST上書き直後に旧版で巻き戻る(2026-10-14)**: 版31.0をアップした約1分後、中村さん名義ロックで旧内容の版32.0が保存された(ユーザーはどこでも開いていなかったと回答)。同期クライアントの古いローカルコピーが上げ直した可能性。→ アップ後すぐ報告せず、2〜3分おいてVersions/Lengthを再確認し、サーバーからDLして中身を確かめてから完了報告する。2回目のアップ(版33.0)は巻き戻らなかった。

**2026-10-14 自分のミス**: 10/13に作ったSharePoint用スクリプト(splock/spupload/spdl.js)が最後に `b.close()` を呼んでいた([[shared_bot_browser]]で禁止)。10/14朝に9226が停止していた(因果は未確認)。修正済み=`process.exit(0)`で終える。共有ブラウザを再起動するとSharePointはパスワード再入力が必要になる(SSO切れ)→再起動は最後の手段。

**2026-10-14 追記**: ユーザー名義のロックが30分以上外れないことがあり、ユーザーから「SharePointではうまくいかないのでPowerPointで更新して」と指示。構造変更(移動・削除)も、AppleScriptで「新ページを貼付→旧ページを非表示(hidden of slide show transition)/delete slide」で反映できた(雛形 v14_ops.py)。必ず作業用コピー同士で先に試し、Python版と表示テキストを突き合わせてから本番に使う。画像圧縮など丸ごと差し替えはこの方法ではできない。

**2026-10-14 11時 ユーザーの常時許可**: 「SharePoint側は上手くいかないので、今後はあなたの方でPowerPointを使った更新作業を許可します」。Nidec正本の更新は、都度の許可なしでPowerPoint共同編集+AppleScriptで行ってよい(作業用コピーで先に試す・バックアップ・サーバー再DLで検証、は続ける)。

**AppleScriptでテキストを足すとき(10/14)**: `make new shape`のproperties(left/top等)は無視されることがある→`make new text box`で作り、作成後に位置・サイズを明示的に設定。枠線は出ない。変数名 h/x/w/before 等は予約語と衝突しうるので px/py/pw/ph 等にする。
