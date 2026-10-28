---
name: powerpoint-freeze-proxy-auth-issue
description: "会社Mac(d14461)でネイティブPowerPointがファイルメニュー操作等でフリーズする問題。根本原因はプロキシ/Zscaler経由のMicrosoft 365認証通信の失敗、IT未解決(2026-08-18時点)"
metadata:
  type: project
  originSessionId: 86655793-9c0c-4cdd-867b-e20342b361f7
  modified: 2026-08-24T05:20:54.403Z
---

2026-08-18、会社Mac(d14461)でMicrosoft PowerPoint(ネイティブアプリ)が、ファイルを何も開いていない状態でもFileメニューを押しただけでフリーズする問題が発生。長時間の切り分けの末、原因を特定。

**確定した原因**: 社内プロキシ(`10.2.3.31:8080`)経由でのMicrosoft 365認証通信(`login.microsoftonline.com`, `graph.microsoft.com`, `*.sharepoint.com`)が正常に完了せず、Office内部の`NSURLSession`が`didReceiveChallenge`(認証チャレンジ)を繰り返し再試行し、メインスレッドをブロックしている。端末にはZscaler(`com.zscaler.tray`、TLSインスペクション型セキュリティ製品)とMicrosoft Defender for Endpoint(ネットワークフィルター拡張有効)の両方が稼働しており、どちらか(おそらくZscaler)がOffice 365向けTLS通信を検査対象にしていることが疑われる。

**切り分けで否定した原因**(同様の症状が今後出た場合、再確認不要):
- ファイル破損(複数ファイル・真っさら起動でも再現)
- Dropbox同期(ローカル圏外コピーでも再現)
- Ollama等ローカルアプリのリソース消費([[gbc_intelligence_engine_project]]で使っていたOllama+qwen3:8bは無関係と確認しアンインストール済み)
- 認証トークンの単純な破損(Keychainの`OneAuthAccount`4件を削除し再サインインさせても同一症状)
- 再起動では直らない

**再現確実な切り分け方法**: Wi-Fiをオフにすると即座に解消し正常操作可能(複数回確認済み)。Wi-Fiオンだと即座に再発する。

**2026-08-18追記(ユーザー確認)**: Wordでも同様に再現する。**Excelでは再現しない**。また正確には無限フリーズではなく、数分待つと自然に復帰する(=特定のネットワーク呼び出しのタイムアウト待ちと推測される、無限ループではない)。

**2026-08-18追記2(IT一次回答テスト+新手がかり)**: IT案内のOfficeサインアウト→サインインを試したが改善せず。新たな手がかりとして、**Command+Z(元に戻す)やCommand+Cはキーボードで実行するとフリーズするが、同じ「元に戻す」を編集メニューからマウスクリックすると即座に完了し詰まらない**ことが判明。この端末では`wdavdaemon_enterprise`(Microsoft Defender for EndpointのEDR/Endpoint DLPコンポーネント)が稼働中で、Endpoint DLP機能は特定のキー操作(コピー等)を監視しMicrosoft Purviewへポリシー確認の通信を行う仕組みがある。キーボードショートカット実行時のみこの監視パスの通信が発生し同じプロキシ問題で詰まる一方、メニュークリックはこの監視パスを経由しないため影響を受けないと推測される。→ Zscalerに加えてMicrosoft Defender for EndpointのEndpoint DLP機能も疑わしい対象として追加。マシン情報: MacBook Pro (Mac16,1)、シリアル`DXVD4P6FMX`、会社機器番号`650893`。

**現在の回避策**: (1) Wi-Fiオフで作業、(2) Teams内蔵のOffice Web版編集機能を使う(問題なく動作)、(3) Undo等はメニュークリックで代替すればキーボードショートカットより速い場合がある。

**IT報告用の診断サマリーをデスクトップに保存済み**: `~/Desktop/PowerPoint_フリーズ_IT報告用メモ.md`(ユーザーがそのままIT/ヘルプデスクに提出できる内容、技術的根拠・確認依頼事項込み)。

**How to apply**: 今後このMacで同様の「Office系アプリがフリーズする」報告があれば、まずこのメモを参照し、(1) Wi-Fiオフで直るか確認、(2) 直るならIT側のプロキシ/Zscaler/Defender設定がまだ直っていないと分かる、(3) IT側の対応(Microsoft 365エンドポイントのSSLインスペクション除外設定)が完了したかを本人に確認してから再調査する。同じ調査(sample/lsofでの切り分け)を最初からやり直す必要はない。

**2026-08-19追記(重要・上記の原因特定を覆す可能性)**: IT一次対応の指示で `~/Library/Group Containers/UBF8T346G9.Office` フォルダをデスクトップに退避したところ、PowerPointのフリーズが実際に解消したとユーザーが報告(Wi-Fiオフ等の切り分けとは別に、この手順単体で改善)。これは前述の「根本原因はプロキシ/Zscaler経由のO365認証タイムアウト」という結論と矛盾する。考えられる解釈: (a) 実際には両方の要因が絡んでいた、(b) Office側のローカルキャッシュ/設定破損がそもそもの原因で、プロキシ切り分け(Wi-Fiオフ)は別の副作用や偶然の一致だった可能性。退避した`UBF8T346G9.Office`(旧データ)はユーザーが削除済みのため、今後this個体で再現実験はできない。**How to applyへの追加**: 今後同様のフリーズが再発した場合、Wi-Fiオフを試す前に、まず「Officeアプリ全終了→`UBF8T346G9.Office`を退避→起動確認」を先に試す方が手数が少ない可能性がある。ただし退避により該当Mac上のOutlookローカルキャッシュ(予定表等)が消え再同期が必要になる副作用があるため、実施前に本人へ影響を説明すること([[outlook_calendar_missing_after_office_container_reset]]参照)。

**2026-08-24追記(ユーザーが明確に訂正)**: 「PowerPointは以前伝えた通りZscalerの問題ではなかった」とユーザー本人が明言。上記08-19追記のOfficeコンテナ退避での解決が事実上の答えで、Zscaler/プロキシ説は誤りだったと確定して良い。**重要: 以後、このMac上で起きる別の不具合(例: 別スクリプトのDNS解決失敗など)を「これもZscalerだろう」と安易に類推しないこと**——本件はZscaler原因説自体がユーザーによって否定されている、根拠のない拡大解釈をしないよう注意。
