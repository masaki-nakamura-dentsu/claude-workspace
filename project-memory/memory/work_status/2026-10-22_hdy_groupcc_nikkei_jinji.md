# 2026-10-22 HDY定点観測: 社内クリッピング取り込み + 日経人事から海外組織図
Status: in_progress
関連: [[hakuhodo_overseas_intel_monitoring]]

## ① group-cc@dentsu.com(Meltwater「dentsu デイリーニュース」/英語版「dentsu Daily News」)
- collectors.py に groupcc_articles()(日本語版: 共有mailtoリンク `Subject=<見出し>&Body=<元URL>` から記事単位、「博報堂DY」欄は全件+他欄はis_hdy)と _groupcc_articles_en()(英語版: 「媒体 - Month D, YYYY - h:mm AM」行で区切り、HDY言及のみ。URLはsendgridで使えないので groupcc:<日付>:<見出し>)を追加。
- 海外/国内は既存の detect_scope(国名/海外グループ社名/GLOBAL_WORDS)。PowerBIは海外のみ表示。
- 旧データ(メール1通=1件、url=mail:…)は items.csv から削除し、2026-01-01から再取り込み完了: 旧109件削除→記事2,270件(海外262・国内2,008)。バックアップ items.csv.bak_202610221130、collectors.py.bak_202610221100。
- 英語版の解析は遅い(全293通で約2分)。定常運用は新着分のみなので許容。

## ② 日経の過去人事 → 海外系の組織図(未着手部分あり)
- 人事欄の記事は見出し「人事、<社名>」、ID が DGXZTSJ…。本文は「（4月1日）新役職（旧役職）氏名▽同（…）氏名」。「同」=直前の役職。例: Hakuhodo DY ONE 2026-02-12 に「グローバル管掌（海外グループ管掌）同大丸充雄」。
- 検索 https://www.nikkei.com/search?keyword=人事、博報堂 は1ページ約20件。ページ送りの方法が未解明(「もっと見る」はヘッダーのもの。&page=2 等は未検証。networkidle待ちはタイムアウトするので domcontentloaded を使う)。
- 次にやること: ページ送り(またはAPI)を特定 → 社名ごと(博報堂/博報堂DYホールディングス/博報堂DYメディアパートナーズ/大広/読売広告社/Hakuhodo DY ONE/博報堂プロダクツ/博報堂テクノロジーズ 等)に記事一覧を収集 → 本文を取得して(発令日, 社名, 新役職, 旧役職, 氏名)に分解 → 海外系(グローバル/海外/International/国名/アジア/Kyu等)で絞って people/役職の履歴表(data/nikkei_jinji.csv)と海外組織図(誰がどの管掌・局か、時系列)を作る → PowerBI用CSV。
- 共有ブラウザ9226は日経ログイン済み。Python=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3。スクリプト下書きは scratchpad(nks.py/nka.py)。タブは必ず閉じる。
- 2026-10-22 ①完了。英語版は見出しに抜粋がつながる場合あり(区切りが改行のみ)・海外判定に業界一般記事が混じる→要調整候補。次は②。
- 2026-10-22 14時台 ②進捗: ページ送り解明=`/.resources/search/partials?keyword=人事、博報堂&offset=N&volume=50`(JSON, hasNext/next.offset)。ページ内fetch必須(Playwrightのrequestはproxyで不可)。本文=/article/<ID>/ の <p class="paragraph_…">。
  - 収集器 `hdy_monitor/nikkei_jinji.py`(collectors.ALL に nikkei_jinji、CADENCE 168h=週1、会社Macのみ。heartbeatに14:00実行済みを記入)。state/nikkei_jinji_{list,bodies}.json に644本(2010-02〜2026-04)保存済み。新着のみ取得。
  - 出力 data/nikkei_jinji.csv(全発令)/nikkei_jinji_overseas.csv/nikkei_overseas_org.csv(2022以降・その後の異動なし)/nikkei_kikou.csv(機構改革)。再集計は `python3 nikkei_jinji.py`。
  - Excel: `hdy_monitor/nikkei_jinji_report.py` → reports/HDY海外組織_日経人事_YYYYMMDD.xlsx(海外組織図/幹部人事年表/全件/年別件数/機構改革)。
  - 海外判定の除外: TBWA\HAKUHODO(国内合弁)、中国四国博報堂、アドバタイジングの「タイ」、ソウルドアウト。
- 2026-10-22 ②完了: 「同」の解釈修正(同X=直前の役員ランク+X、同室等=その単位まで)。全644本→発令10,096件/海外系497件/最新海外体制72人(+Sansan補完)。Excel reports/HDY海外組織_日経人事_20261022.xlsx 作成・open済み。残: PowerBIにCSV4本追加(手順書未作成)、スライド版組織図(要望あれば)。
Status: done
- 2026-10-22 残2件着手: PowerBI構築手順_20261022.md(G-14 日経人事CSV4本・メジャー・ページ)作成済み。次=PPTX版組織図。
- 2026-10-22 残2件完了: ①PowerBI構築手順_20261022.md(G-14: CSV4本のMコード・メジャー2本・ページ「日経人事・海外組織図」・確認表)。PowerBI側の操作はユーザー作業(未実施)。②reports/HDY海外組織図_日経人事_20261022.pptx(3枚: 2026/4海外組織体制/海外組織の変遷+年別件数グラフ/海外現地法人トップ人事)。競合研究_HDY_20260127_中村追加.pptx をテンプレに(Content_body copy_1、游ゴシック、紺+薄紫の箱)。生成スクリプト hdy_monitor/nikkei_jinji_pptx_20261022.py(内容は手書き、データ更新時は要見直し)。qlmanageで3枚確認済み。
- 2026-10-22 追加依頼: ダウンロードしたpbix(~/Downloads/競合社定点観測(HDY).pbix と (1).pbix)を元に、既存セマンティックモデルを使う前提で手順書を修正。着手。
- 2026-10-22 pbix確認→PowerBI構築手順_20261022_01.md作成(0章=現状、H章=既存モデルに日経4本追加、A〜Gは参考)。ユーザー作業待ち。Status: done
- 2026-10-22 ユーザー質問「マトリックス(組織図)がない」→ビジュアル名は「マトリックス」、既存ページのマトリックスをコピーする方法を回答。手順書_01のH-6を修正。

## 2026-10-22 16:58 Excel版をSharePointへ・PowerBIからリンク
- SharePoint「GBC戦略企画-HDY研究」/HDY研究/【HDY海外組織_日経人事】を作成し、HDY海外組織_日経人事_20261022.xlsx を配置(ブラウザで表示確認済み)
- 自動化: config.SP_JINJI_DIR、core.mirror_to_onedrive(dest_dir=)、nikkei_jinji_report.publish、collectors.nikkei_jinji(新着>0で再作成+SP追加)。バックアップ *.bak_202610221654
- 手順書 PowerBI構築手順_20261022_01.md に H-9(ボタン→Web URL)と H-8 確認行を追加
- 残: ユーザーがPowerBIでボタン設置。閲覧者のサイト権限は未確認
Status: in_progress

## 2026-10-26 日経メール点検WARN対応
- 原因: items.csv のDropbox競合(会社Mac/個人Mac同時書き込み)で取り込んだ行が競合コピーへ退避。パーサーは正常
- 対処: core.merge_conflict_copies 追加(add_items先頭で自動マージ→state/conflict_archive)。12件復元(日経1・クリッピング4・SF6・他1)。バックアップ core.py.bak_/state/items.csv.bak_
Status: done

## 2026-10-27 日経メール点検WARN(2回目)
- 原因: Outlookエクスポート遅れ(収集が未読のメールを点検が判定)。nikkei_check.py に mail.json last_date 判定を追加(bak_あり)。11:25収集で該当記事取り込み済み、競合コピーなし
Status: done
