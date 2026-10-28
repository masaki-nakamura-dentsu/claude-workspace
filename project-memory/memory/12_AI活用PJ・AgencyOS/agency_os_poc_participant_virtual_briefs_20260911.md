---
name: agency-os-poc-participant-virtual-briefs-20260911
description: Agency OS PoC参加者28名(部長級6-7名だけでなく一般メンバーも含む)全員分の「テスト用仮想ブリーフ」をWordで生成した記録。保存場所・命名規則・架空クライアント一覧
metadata:
  type: project
  originSessionId: 84978898-dfb7-4599-a7c7-1acda18aba04
  modified: 2026-09-11T07:50:13.031Z
---

2026-09-11、「Agency OSのPoCのそれぞれの参加者に対して、それぞれのテスト用仮想ブリーフを生成して」との依頼で、当日作成済みだった`Agency_OS_PoC_参加者名簿_20260911.xlsx`(28名、部署/氏名/役職/メールアドレス、AP1部10名・AP2部2名・AP3部2名・BD部9名・SP2部4名・SP1部1名)を元に、28名全員分のテスト用仮想ブリーフ(python-docx、Word)を生成した。[[gbc_intelligence_engine_project]]の「Agency OS」Skill([[feedback_brief_means_client_brief]]参照)のPoC関連作業。

## 保存場所・成果物
`Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/20260814GBC知見集約プロジェクト/20260909PoC説明/テスト用仮想ブリーフ_20260911/`(新規サブフォルダ)に、`テスト用仮想ブリーフ_{架空会社名}_{部署}部{氏名}様_20260911.docx`の命名規則で28ファイル。

生成スクリプトは`/private/tmp/claude-503/.../scratchpad/generate_virtual_briefs.py`(セッション終了後は消える一時ファイル、再利用する場合は要再作成)。

## 既存の「仮ブリーフ」との使い分け(重要な判断ポイント)
同フォルダには2026-09-09作成の6-7GM分「仮ブリーフ」(7&i/Manulife/Acecook Vietnam/ゼスプリ/デンソー/JETROセルビア(後にフランス政府案件に差替)/SEIKO)が既に存在し、これらは**実案件ベース**(Salesforceで各GM本人の実際の案件を特定し、それをクライアント一人称視点で書いたもの、PoC説明会での訴求力を狙ったもの)。

今回の「テスト用仮想ブリーフ」は言葉が違う(「仮想」)ことと、対象が一般メンバーも含む28名に広がったことから、**実案件ではなく架空クライアントで作るべき**と判断した。根拠: (1) 2026-09-08のPoC募集資料で既に「架空案件Nusantara Roast」という前例が使われていた、(2) 一般メンバー28名の多くはSalesforce上「責任者(GBC)」として実案件が紐づいていない可能性が高く、実案件ベースだと大半が代替事例頼みになり個別性が失われる、(3) 実際にAgency OSを試す「テスト」用途では機密実案件を使わない方が安全、という3点。ユーザーからの明示的な訂正・確認は無く、この場では自律判断で進めた。

## 生成した28社の架空クライアント一覧(業界重複なし)
AP1部: Solvane Watch(高級時計)/TerraNova Outdoor Gear(アウトドア)/BluePeak Financial Group(銀行)/Aurelia Cosmetics(化粧品)/Kestrel Mobility(マイクロモビリティ)/Loom & Thread(アパレル)/Meridian Airlines(航空)/Verdant Foods(プラントベース食品)/PlayForge Studios(モバイルゲーム)/Halcyon Hotels & Resorts(ホテル)。
AP2部: Kinfolk Home Goods(ホーム用品小売)/Nordbridge Telecom(通信)。
AP3部: Meadowlark Insurance(生命保険)/CedarPoint Pharma(製薬)。
BD部: Riviera Spirits(スピリッツ)/OrbitalPay(決済)/Sable & Stone Jewelry(ジュエリー)/GreenGrid Energy(再エネ)/Wanderlust Travel(旅行代理店)/PixelCraft Toys(玩具)/Ferrovia Logistics(物流)/Blossom Baby Co.(ベビー用品)/Ember Coffee Roasters(コーヒーチェーン)。
SP2部: Vantage Motors(EV)/Lumen Beauty Devices(美容機器)/Northstar University(大学)/PawCare Pet Co.(ペットケア)。
SP1部: Terra Verde Agritech(アグリテック)。

## フォーマット
既存の仮ブリーフDocxを`python-docx`で解析し、フォント(游明朝)・色(ネイビー1B2A40=タイトル/見出し、グレー666666=日付/差出人組織、ダークグレー222222=本文)・サイズ(日付10pt/タイトル16pt/見出し11.5pt/本文10.5pt)・段落間隔まで完全に踏襲。構成は7セクション固定: 1.ご相談の背景 2.今回のご依頼内容 3.ターゲット・対象 4.現状の課題・懸念 5.ご期待する成果物 6.ご予算感・スケジュール(既存踏襲で空欄のまま) 7.その他留意事項。

ユーザーから「ok task end」で完了確認を受けたのみで、内容への追加フィードバックは無し。次にこのタスクに触るときは、実際にAgency OS Skillへこれらのブリーフを投入してテストした結果(誰のブリーフでどんな出力が出たか)を確認してから再開すること。
