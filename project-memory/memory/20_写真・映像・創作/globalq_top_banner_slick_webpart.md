---
name: globalq-top-banner-slick-webpart
description: Global Q TOP(GlobalQ-TOP.aspx)のカルーセルは独自Webパーツ「slick」で、バナー画像をbase64でページ内に埋め込む。重くなると保存が戻る・画像が白紙になる
metadata:
  type: project
---
Global QサイトTOP(`/sites/globalonedentsu/SitePages/GlobalQ-TOP.aspx`、サイトのページ item 390)の上部カルーセルは独自SPFx Webパーツ「slick」(webPartId 136119c4-7afc-4fa8-80f9-b601ccfb759f)。プロパティ img1〜img5 に画像を **data:URIのbase64で直接格納**し、url1〜url5 がリンク先、さらに src にスライドHTMLを丸ごと複製して持つ(=画像が2重に入る)。

2026-10-14 佐藤文さんから「バナー差し替えが元に戻る/画像3が白紙」の相談(Teams GlobalQ編集部)。調査結果: CanvasContent1が約12.4MB(このWebパーツだけで12.26MB)。img1(ICE-BREAKING NEWS)がPNG 1.6MB、img3は先頭の`data:image/png;base64,`ヘッダーと冒頭が欠けた壊れたbase64(2.1MB)でurl3も空→白紙表示の直接原因。img2は#011の画像のままリンクだけ4koma_013。GeminiのPNGをそのまま入れるとページがさらに肥大化し保存失敗→元に戻ると推定。PNG→JPEG(q80)で1.6MB→276KBに落ちることを確認。

**How to apply:** バナー差し替え相談が来たら、まずREST(`_api/web/lists/GetByTitle('サイトのページ')/items(390)?$select=CanvasContent1`)で各imgのサイズ・ヘッダー有無を確認。対策は画像をJPEG・数百KBに圧縮してから入れる。ページ変更は共有サイトなのでユーザーの明示許可が必要([[feedback_sharepoint_permission_change_needs_explicit_ok]])。バナー画像の書き出し手順は[[globalq_top_banner_monthly_export]]。読み取り用スクリプト=既存のesq365.sharepoint.comタブでfetchを実行する方式(新規タブを開かない)。
