---
name: feedback-powerbi-browser-only
description: ユーザーのPowerBI作業はブラウザ版(Service)前提。手順書・案内にDesktop手順を書かない
metadata:
  type: feedback
---
2026-10-06、HDY定点観測のPowerBI手順書をDesktop前提の詳細版で作ったところ「MacにはDesktop版がないのでブラウザ版での作業を前提にして」と指示された(過去2026-09-05にも「私はブラウザ版なのでリボンに書式は無い」と訂正済みの同種ミス)。

**Why**: 会社Mac(d14461)ではPower BI Desktopが動かない。過去にWindows 365でDesktopを使った記録があっても、現在の作業環境はブラウザ版。

**How to apply**: PowerBIの手順・クリックパスは常にService(app.powerbi.com)の編集画面・Power Query Onlineで書く。Power Query Onlineの既知の罠(空のクエリへの複数行貼付は壊れる→既存クエリを複製して詳細エディターで編集、OneDriveのファイルはWeb.Contentsを数式で直接、日本語パスはURLエンコード)を手順に織り込む。細かいクリック単位の手順を求められている(2026-10-06「こういった細かいところまで手順書に入れて欲しい」)。関連: [[feedback_powerbi_ui_label_accuracy]] [[feedback_token_conscious_powerbi]]
