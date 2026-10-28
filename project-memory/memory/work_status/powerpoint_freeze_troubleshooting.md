# PowerPointフリーズ問題の切り分け

## 2026-08-18T11:00:00+09:00
Status: done (根本原因特定、修正はIT対応待ち)
What: 会社MacでネイティブPowerPointが頻繁にフリーズする件を調査。ファイル破損・Dropbox同期・Ollama常駐(アンインストール実施)・認証トークン破損(Keychain OneAuthAccount削除して再サインインさせても再現)を順に切り分けて否定し、`sample`コマンドでのスタックトレース採取と`lsof`でのネットワーク接続確認により、社内プロキシ(10.2.3.31:8080)経由のMicrosoft 365認証通信(login.microsoftonline.com等)が失敗し続けていることを特定。Wi-Fiオフで即座に解消することを複数回再現確認し確定。Zscaler(TLSインスペクション型)とMicrosoft Defenderのネットワークフィルターが端末で稼働中、どちらかがO365向け通信を検査対象にしている可能性が高い。IT報告用サマリーを`~/Desktop/PowerPoint_フリーズ_IT報告用メモ.md`として作成・送付。詳細は[[powerpoint_freeze_proxy_auth_issue]]。
Next: ユーザーがIT/ヘルプデスクに報告し、プロキシ/Defenderの除外設定が入るのを待つ。次回同様の報告があれば、まずWi-Fiオフで直るか確認しIT対応状況を聞く(同じ調査をやり直さない)。

## 2026-08-18T13:00:00+09:00
Status: done (追加の切り分け情報をIT側へ提供、対応待ち継続)
What: IT/ヘルプデスクの一次回答(Officeサインアウト→サインイン)をユーザーが試したが改善せず。ユーザーが新たに気づいた「Command+Z/Command+Cはキーボードで実行するとフリーズするが、同じ操作をメニューからマウスクリックすると即座に完了する」という手がかりを分析。`wdavdaemon_enterprise`(Microsoft Defender for EndpointのEDR/Endpoint DLP)がキー操作を監視しMicrosoft Purviewへポリシー確認通信を行う仕組みがあることを確認し、これがキーボード実行時のみ発生する遅延の原因である可能性が高いと結論。Zscalerに加えてDefenderのEndpoint DLP機能も疑わしい対象として追加。機器番号(MacBook Pro Mac16,1、シリアルDXVD4P6FMX)も取得し、IT報告用メモとプロジェクトメモリ([[powerpoint_freeze_proxy_auth_issue]])を更新、ユーザーに再送付。
Next: ユーザーがこの追加情報をIT/ヘルプデスクに返信し、Defender Endpoint DLP関連の除外設定を確認してもらうのを待つ。
