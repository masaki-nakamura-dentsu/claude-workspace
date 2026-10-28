# PHP2Shell (CVE-2026-109618/109619) 対応

## 2026-10-22
Status: waiting
What: 管理5サイト(masakinakamura.com / mfk-photos.com / stellamarie.jp / awit.world / kataribe.art)はConoHa WING(共有ブラウザでログイン済み、CDP :9227)。WP Site Healthで読み取り確認: masakinakamura.com=PHP 8.3.31、他4つ=8.2.31(修正版は8.3.36/8.2.35)。ConoHaは修正番号をサーバー側で更新する方式。reikootsuka.com・saisoho.conohawing.comは未使用。本人判断: ConoHaの対応を待ち、現時点では変更なし。
Next: ConoHaメンテ後にsite-health.php?tab=debugでphp_versionを読み取り再確認(要請があれば)。未更新なら問い合わせ文面を作成。

## 2026-10-23
Status: waiting
What: 共有ブラウザ(CDP :9227)のwp-admin既存タブ内fetchでsite-health debugを再読取。masakinakamura.com=8.3.35(前回8.3.31)、stellamarie.jp/mfk-photos.com/awit.world/kataribe.art=8.2.34(前回8.2.31)。更新は進んだが、修正版の番号(8.3.36/8.2.35)には1つ足りない。ConoHaは番号を上げず/バックポートの可能性もあり、番号だけでは判定不可。
Next: ConoHaに「修正済みか」の問い合わせ文面を作成(要請があれば)。

## 2026-10-23 続き
Status: done
What: ConoHa終報(10/22 20:45、manage.conoha.jp/Information/Index?code=29f5...)を確認。番号を上げずに修正だけ取り込む方式で、適用後バージョンは8.2.34/8.3.35(他略)。当方5サイトの表示と一致=対応済み。ユーザー側の作業不要。問い合わせ文面は不要。
