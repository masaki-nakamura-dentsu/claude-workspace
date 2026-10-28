# redespresso.co.jp お問い合わせフォーム未達調査

## 2026-09-10T06:55:00+09:00
Status: done
What: contact / 事業者向け登録ページのHTMLを取得しEverest Formsのフォーム構造(nonce・honeypot・name属性)を確認→フロント側に不備なし。次にDNSを確認し、MX/SPFがGoDaddy(secureserver.net)、Web側はGMOお名前.comレンタルサーバー(www59.onamae.ne.jp)と判明。SPFが`-all`(hard fail)でお名前.com側を許可しておらず、DMARCが`p=reject`のため、WordPress(Everest Forms)がPHP mail()で@redespresso.co.jpアドレスをFromにして送るとSPF不整合で受信側に拒否される可能性が高いと結論。ユーザーに解決策(SMTP経由送信への切替等)を提示。
Next: ユーザーがEverest Forms管理画面でEntries(エントリー保存有無)と通知設定を確認、WP Mail SMTP等でGoDaddy SMTP認証送信に切替するかを判断。

## 2026-09-11T09:00:00+09:00
Status: done
What: Entries確認(1236件正常保存、フォーム側は無関係と確定)→通知のFrom/To確認(From=info@redespresso.co.jp、自ドメイン宛にも届いていない事実がSPF/DMARC拒否説を裏付け)→お名前.com側だけでは直せない理由(DNSはGoDaddyネームサーバー管理)を説明→WP Mail SMTPプラグイン導入、GoDaddy Workspace Email(MXパターンから確認、クライアントに聞かず判定)のSMTP(smtpout.secureserver.net等)にinfo@redespresso.co.jpで認証送信する設定を1ステップずつ案内→ユーザーが実施し解決確認。project memoryに手法と結論を保存済み。
Next: ―(完了)

## 2026-10-26 Redespresso スマホ表示(スライダー重なり)調査 + PHP脆弱性(php2shell)確認
Status: pending（本番への修正は未適用・本人の許可待ち）
What: スマホでトップのスライダーが3枚縦積み・キャプション重なり。原因=Flash Toolkit 1.2.7が`flash-swiper`ハンドルを読むが、テーマFlash 1.4.4は`swiper`でしか登録しておらずSwiper JS未読込(PC幅も同じ)。テーマ編集案は管理リスクでNG→テーマ非変更案(追加CSSで2枚目以降を非表示 / Code Snippets等でflash-swiper登録)。CSS案はローカル注入で表示OK確認済み。PHP: Site Health=8.1.34(LiteSpeed)。8.1はEOL(2025-12-31)だが、お名前.com RSは2026-10-22 20:45に全PHP版へパッチ適用済み(版数表示は変わらない)と公式告知。CVE-2026-115560(session.upload_progress、修正版未公開)は要設定確認。
Next: 本人がCSS案/Snippets案を選択→適用(WP管理画面)。お名前.comでプラン(RS)とsession.upload_progress設定を確認。

## 2026-10-26 (続き) 追加CSSでスライダー復旧を試行
Status: pending（Customizer保存がWAFにブロック）
What: Swiper無しで3枚が自動フェードするCSS(`scratchpad/slider.css`、`.swiper-container:not(.swiper-container-initialized)`限定でJS復旧後は自動無効)をPC/スマホでローカル検証OK。Customizerの追加CSSへ追記保存を試みたが、保存POSTが「閲覧できません (Forbidden access)」(サーバー側WAF)で拒否され未反映。既存追加CSSは変更なし(バックアップ scratchpad/custom_css_BEFORE_20261026.css)。
Next: 本人がお名前.comのWAF設定を確認(一時OFFにして保存→ONに戻す等)するか手動貼り付けを試す。許可があれば再度保存を実行。

## 2026-10-26 (続き2) 簡素化CSSで再試行→同じくWAFで拒否
Status: pending（下西さんにWAF一時OFF依頼の返信待ち）
What: コメント・@media除去の簡素版(scratchpad/slider_v1.css)でも保存POSTが「Forbidden access」。ユーザー手動貼り付けも失敗(別文言)。方針どおり、クライアント(下西さん)にお名前.comでWAF一時OFFを依頼する返信文を作成。
Next: WAF OFF連絡後、`python3 scratchpad/save_css.py slider_v1.css`(または slider.css)で保存→スマホ幅で確認→WAFをONに戻してもらう。

## 2026-10-27 (続き3) WAF一時OFF→CSS保存→WAF ON復帰、スライダー復旧完了
Status: done
What: 本人許可(今回限り)でお名前.com RS(rs1275786)のWAFをredespresso.co.jpのみ一時OFF→save_css.py(slider_v1.css)でCustomizer追加CSS保存成功→WAFをONに戻した(スクリプトのfinallyで復帰、画面でON確認)。スマホ幅(390px)でスライダーが1枚表示・キャプション重なりなしを確認。認証情報はmemory非保存(一時PW)。
Next: クライアント(下西さん)にスライダー修正完了を連絡、一時PWを元に戻してもらう。
