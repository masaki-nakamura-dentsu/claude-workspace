---
name: hakuhodo-overseas-intel-monitoring
description: HDYグループ海外戦略の定点観測(収集=会社Mac自動、PowerBI「競合社定点観測(HDY)」aicon・PA定期更新)。現状サマリー・設定値・次の作業
metadata:
  type: project
---

## ★現状サマリー(2026-10-06 夕方 情報源拡充後。新しいチャットはここから再開)
- **収集(稼働中)**: 会社Mac launchd `com.nakamura.hdymonitor`(3時間おき)/`com.nakamura.hdydigest`(月曜8:45 Teams週報)。コード `Work/GBC_戦略企画部/GBC経営企画グローバル戦略分析／競合分析など/競合分析/HDY定点観測/hdy_monitor/`。CSVは `data/` と aicon OneDrive `~/Library/CloudStorage/OneDrive-電通/AICON - 戦略企画部/HDY定点観測/` に出力。Sansan組織ツリーは月1回自動(6社)。スリープ復帰直後のネット待ち(最大5分)あり。
- **PowerBI(稼働中)**: ワークスペース/セマンティックモデル「競合社定点観測(HDY)」(Pro、所有者aicon、ブラウザ版で構築)。CSV10本+`SF_HDY_Pitches`(GBCダッシュボードのJCI_Pitch_Base複製+vs_HDY/hdy_won)+`更新日時`表。資格情報は「設定→ゲートウェイとクラウドの接続→マップ先→新しい接続を作成」(Salesforce=masaki、OneDrive=aicon)。
- **定期更新**: PowerBIのスケジュールトグルは不可→Power Automate(aicon)「競合社定点観測(HDY)_定期更新」毎日9:30/12:30/15:30/18:30。失敗通知3種(依頼失敗/20分後に更新日時>30分で更新処理失敗/確認クエリ失敗)をTeamsフローボット→masakiへ(カード投稿+アダプティブカードJSON)。テスト成功確認済み。
- **手順書の最新版**: `HDY定点観測/PowerBI構築手順_20261006_05.md`(ブラウザ版・実施結果反映)。ユーザーはVS Codeプレビューで読む。
- **2026-10-06夕 情報源拡充(稼働)**: 新収集器 `hdy_monitor/extras.py` = works(Hakuhodo Global Our Work 181事例・受賞791件、毎日/週1全件)、ir(HDYHD IRライブラリ eir-parts の決算説明会資料・質疑応答PDF→overseas_ratio/financials/ir_comments、Ad Age All Access Excel→adage_agency、region_mix=日本公式/米国=Ad Age米国シェア×連結収益の推計/その他海外=残差)、jobs_web(台湾104・インドNaukri=共有ブラウザ9226でJSON傍受、ベトナムVietnamWorks API。中国はボット対策で不可)、articles(重要/海外記事の本文+og:image、Google NewsはbatchexecuteでURL復元、自社全文/他媒体1,500字、3時間毎40本)。news_rssに業界誌RSS+site:検索・広告賞・セミナー検索、pagesにHILL ASEAN、signalに「セミナー・レポート」追加、source_type=industry。新CSV8本(articles, works, work_awards, overseas_ratio, region_mix, adage_agency, ir_comments, financials)。手順書=`PowerBI構築手順_20261006_06.md` G章(ページ: 重要記事/海外売上比率・地域構成/広告賞・海外事例)。Ad Ageはユーザーが共有ブラウザ9226でログイン済み(2026-10-06)。Ad AgeのExcel URLはログイン不要の固定パターン(config.ADAGE_XLSX_URL)。数値確認: FY2025通期 海外売総比率26.4%、FY2025上期28.26%、FY2025地域構成 日本73.8%/米国8.4%/その他海外17.9%。TDnet原本は1か月で消えるのでIRはeir-parts(announcement_1.js)を使う。
- **2026-10-06夕② LinkedIn等追加(本人承認で方針変更: 旧「LinkedIn不要」は撤回)**: extras.linkedin = ログイン不要の jobs-guest API で会社別求人(location=Worldwide&f_C=<ID>)、会社ページのJSON-LD numberOfEmployees=LinkedIn登録社員数(月1、linkedin_headcount)、HDY系会社の自動発見(週1)。会社IDは f_C= か organization:<ID>。5秒間隔(3秒×40回で429)。seed/exclude は config。注意: 「2,400人」はHakuhodo VN説明文中の日本国外全体の人数、VN単体登録は182人。extras.roster = hakuhodo.vn/careers の Meet Our Team(17名)→ roster_people・人事シグナル。iimjobs(gladiator.iimjobs.com/job/search API、現0件)、Naukri語追加。手順書最新 `PowerBI構築手順_20261006_07.md` G-10。
- **2026-10-07 さらに拡充**: entity_sites(Our Network各社ページ→公式サイト/LinkedIn→採用ページ・ニュース欄。トップURLのみ採用、報道サイト除外。EXTRA_ENTITY_SITESでIDEO/Red Peak/SYPartners/Public Digital)、entity_watch(各社ニュース新着→items、採用ページ求人→jobs source=careers:)、core.employer_names/is_hdy_employer(61社社名で求人広告主判定・JobStreet検索語拡大→掲載中202件)、LinkedIn自動発見を61社社名+entity_sitesのLinkedInリンクに拡大、yuho(有報2003-2025: 海外主要子会社996行・連結子会社/持分法/従業員。2024年度から記載方針変更で19社に見える)。中国語のsignal語追加。PR配信site:検索追加。手順書最新=`PowerBI構築手順_20261007.md` G-11。※config編集で「# 海外各社サイトのチーム紹介ページ」がCADENCE内コメントと一致し構文エラーを起こした(即修正)→config編集後は必ず py_compile。
- **2026-10-07 日付バグ修正**: itemsのPowerBI date列が掲載日なし→first_seen代用で過去記事が2026年に集中(ユーザー指摘「2026年が異常に高い」)。PowerBI側はdate=publishedのみ+date_known列(手順書_20261007_01 G-12)、収集側に backfill_dates(元ページのpublished_time等から補完、日150件)。補完後も掲載日不明172件。2026年が多い残りの理由=メール(2026/1〜)・Google News(30日)が今年分のみ。
- **2026-10-07 ユーザー要望「グローバル関連に絞る」**: items/articlesに scope列(海外/国内、core.detect_scope: 国≠日本/GLOBAL_SOURCES/海外グループ社名義/GLOBAL_WORDS)。海外1,165・国内243。articles収集は国内を除外。タイトル補正 core.better_title(「Japanese Version」等→PDFファイル名・元ページtitle)、ページ送り削除、Hakuhodo Globalの「News Oct. 2, 2026」前置き除去。PowerBIは「すべてのページでのフィルター」scope=海外(手順書_20261007_02 G-13)。
- **次の作業(未着手)**: ①レポートのページ作り(手順書D章+G章: 概況/人材需要/人事/展開国マップ/海外組織図/本社組織人数/対HDYピッチ) ②個人Mac予備系の設置(relay task-008、pending) ③日経電子版ID申請の承認待ち(差し戻し対応済み_20261006.xlsxを再送)→承認後にキーワードアラート設定案内 ④Meta広告ライブラリ等の第2段階は未着手。
2026-10-05構築。関連: [[hakuhodo_proposal_analysis]] [[sf_reports_qbr_download_automation]] [[local_work_data_export]] [[automation_schedule_overview]] [[powerbi_jci_pitch_status_chart]]

**場所**: `Work/GBC_戦略企画部/GBC経営企画グローバル戦略分析／競合分析など/競合分析/HDY定点観測/`(README.md・PowerBI構築手順.md あり)。コード`hdy_monitor/`(config.pyに情報源/辞書集約)、`data/`(items.csv, jobs.csv, jobs_daily.csv, sf_hdy_pitches.csv)、`reports/weekly/`。CSVは`~/Library/CloudStorage/OneDrive-dentsu/HDY定点観測/`にも複製(PowerBI ServiceをWebコネクタでゲートウェイ無し更新させるため)。

**ユーザー決定(2026-10-05)**: 範囲=HDYグループ全体 / 主系=会社Mac、予備=個人Mac / 出力=Teams週報+PowerBI(常時更新) / LinkedIn不要 / Salesforceの競合情報はJCIピッチレポート(APAC Pitch - List All_v1.31)を使う / 国別にどんな人材を求人しているかを見たい。

**設定値**: 会社Mac launchd `com.nakamura.hdymonitor`(StartInterval 10800=3時間、RunAtLoad)、`com.nakamura.hdydigest`(月曜8:45)。個人Mac予備系は relay task-008 で依頼(3時間おき、heartbeatが6時間以上古い時だけ代行 FAILOVER_STALE_HOURS=6、週報は月曜9:30に未作成なら作成)。収集間隔: news 3h / pages 6h / tdnet 6h / jobs 24h / mail 3h / sf 12h / watch 24h。失敗は2回連続でTeams通知。会社Macは通信にproxy1.dentsu.co.jp:8080必須(curl経由)。ログ`~/hdy_monitor_logs/`。

**情報源**: Google News RSS16クエリ、Hakuhodo Global RSS、読広経由の博報堂DYグループトピックスRSS、読広/大広RSS、博報堂ニュースリリース・DY ONE・Kyu Stories・Hakuhodo Globalニュースのリンク差分、Hakuhodo Global peopleページ増減(人事)、TDnet(yanoshin API, 2433)、求人=Greenhouse(ideo, sidlee, redpeak, keplergroup)/Lever(sypartners)/JobsDB・JobStreet(TH,HK,MY,SG,PH,ID)、Outlookエクスポート(Sansan役職変更のHDY人物行、nikkei.comアラート、dentsuデイリーニュースのHDY言及、「海外動向」件名)、SFピッチxlsx、採用ページ4つのハッシュ監視。

**既存の関連運用(発見)**: GMC株式会社に「博報堂DYグループ海外動向報告書」を月次外注(久賀谷洋さん窓口、ユーザーCC)、久賀谷さんが月次で手動クリッピングを共有。本システムはこの手動クリッピングを自動化・補完できる位置づけ。

**未対応**: HDYHD/DYMPのニュース欄はJS描画で取得不可(代替あり)、Naukri/中国/ベトナム求人、Meta広告ライブラリ・Google広告透明性センター(第2段階、共有Botブラウザ)、日経はアラートメール受信設定待ち。日経の助言: 両方の契約は不要。まず電通の法人契約(テレコン)を確認、無ければ電子版(4,277円/月)で足りる。人事の自動通知は日経人事ウオッチProという別サービス。

**2026-10-05追加(展開国マップ・組織図・人数)**: 収集器`org`(hdy_monitor/org.py、24時間)を追加。Hakuhodo Global「Our Network」の全拠点ページを巡回し事務所単位で国を判定(1ページに複数国の事務所あり、例: DY ONEページ=DAC系7拠点)→network_offices/entities/people.csv。Our NetworkにKyu系・独・英が載らないためconfig.NETWORK_SUPPLEMENTで手動補完。本社側はSansan名刺CSV(`HDY定点観測/input/sansan/`、2026-01-30書き出し2本を配置)から海外関連部署(グローバル/海外/International/kyu等、万博系除外、最終接点4年以内、退職除外)→hq_global_people/hq_dept_headcount(人数=名刺ベースの下限値)。駐在員数は`HDY海外_日本人社員数_*.xlsx`(FY20-FY26シート=国別、Jul 2024 (2)=会社別)→expat_headcount。countries.csv=国マスタ(緯度経度/ISO3、PowerBIのMap用)。初回: 94事務所/17か国、幹部60名、本社42名/32部署。手順書は`PowerBI構築手順_20261005.md`(旧版は残置)。海外拠点の総従業員数は公開情報なし。

**2026-10-05 Sansan自動書き出し(稼働)**: ユーザーが「Sansanのデータダウンロードは問題ない、許可する、月1回程度でOK」と明言(2026-10-05)。`hdy_monitor/sansan_export.py`、CADENCE `sansan: 720`(月1回)、会社Macのみ。手順: 共有ブラウザ9226でSSOログイン→企業タブ検索`#SimpleSearchWord`(ホーム検索はマイデータ限定なので不可)→社名をNFKC正規化して照合(DY ONEは全角「Ｈａｋｕｈｏｄｏ　ＤＹ　ＯＮＥ」)→組織ツリータブ→「印刷」隣の「ダウンロード」→ダイアログsubmit。初回6社成功(博報堂4850985208115/大広6289572129464/DY ONE 7652012723727ほか)→本社海外関連54名・40部署。日経電子版の契約は上司と相談中(ユーザー)。Sansan Labs「人事異動ニュース」は役員級のみ、日経人事欄は局長・GM級まで。

**2026-10-05 フォルダ移動**: ユーザー指示で `2026年_博報堂研究/` 配下から1階層上の `競合分析/HDY定点観測/` へ移動(今後も継続蓄積するため)。launchd 2本のパスも更新済み。駐在員数の元資料は config.RESEARCH_DIR(=競合分析/2026年_博報堂研究)を参照。

**2026-10-05 個人Mac予備系 設置完了(task-008)**: 個人Macでのフォルダ実体は `Work/GBC_戦略企画部/GBC経営企画グローバル戦略分析／競合分析など/競合分析/HDY定点観測/`(「2026年_博報堂研究」階層なし。ユーザーが配置)。launchd `com.nakamura.hdymonitor.backup`(StartInterval 10800, RunAtLoad)・`com.nakamura.hdydigest.backup`(月曜9:30)、plistは~/Library/LaunchAgents、出力 ~/hdy_monitor_logs/launchd_backup.{out,err} / launchd_digest_backup.{out,err}。Python は /opt/homebrew/bin/python3 3.14 + user site の pandas 3.0.6 / openpyxl 3.1.5(--break-system-packages)。予備系は主系が健全だと無出力で終了するのが正常。Dropboxのオンライン専用化を防ぐためフォルダを「オフラインで利用可能」にする必要あり。

**2026-10-05 日経電子版の社内申請書を作成**: `競合分析/日経電子版ID取得/` に記入済み `N2_外部サービス　ビジネス版_届出書_日経電子版_20261005.xlsx` と `N4_誓約書_日経電子版_20261005.docx`(元様式は未変更)。記入値: 所属=グローバル・ビジネス・センター 戦略企画部、社員番号14461、クラスPC(評価シートより)、所属長=山田桂太(評価者のため仮置き・要確認)、機器管理番号=N650893(MacのComputerName、推定・要確認)、使用理由=その他(競合HDYの海外戦略・人事の定点観測)、取扱情報=一般/マーケティング情報、管理主体=電通管理/申請部門管理、アプリ導入なし。電通管理を選ぶと別紙「システム環境レビュー ヒアリングシート」提出が必要と様式に記載(未入手)。

**2026-10-06**: 日経電子版のID取得申請をユーザーが提出済み。承認結果待ち。承認後はキーワードアラートのメール受信設定を案内する(mail収集器が nikkei.com 送信元を取り込む)。
**2026-10-06 改修**: スリープ復帰直後(8:40)に全収集がHTTP 000で失敗していたため、run.pyに wait_for_network(最大5分、30秒間隔で hakuhodo-global feed を確認)を追加。つながらなければ失敗扱いにせずスキップ。

**2026-10-06 PowerBIのアカウント方針**: ユーザーは異動の可能性を考えaiconで作成したい意向。助言: aiconで作成(ワークスペース・データセット所有者・データソース資格情報すべてaicon)。CSVの置き場もmasaki個人OneDriveからaiconのOneDrive(戦略企画部/HDY定点観測)へ移す提案→aicon側でフォルダ作成・masakiに編集共有・masakiのOneDriveにショートカット追加してもらい、config.ONEDRIVE_MIRRORを切替予定(ユーザー作業待ち)。PowerBIはSalesforceに直接つながずsf_hdy_pitches.csvを読むのでSF資格情報は不要。収集処理自体はmasakiの会社Mac/Salesforceログインに依存(異動時は引継ぎ要)。

**2026-10-06 CSV複製先をaiconへ切替(設定値)**: config.ONEDRIVE_MIRROR = ~/Library/CloudStorage/OneDrive-電通/AICON - 戦略企画部/HDY定点観測 (aiconのOneDriveのフォルダをmasakiのOneDriveにショートカット追加したもの)。フォルダが無ければ複製しない(自動作成しない)。旧複製先 OneDrive-dentsu/HDY定点観測 は残置・以後更新されない。PowerBIはaiconで作成、URLはaicon側ファイルで。
**SF依存の議論(2026-10-06)【訂正あり】**: ユーザーは「SalesforceダウンロードがMac依存なので依存しない方が安定」と提起。最善はPowerBIのSalesforceオブジェクトコネクタ(GBC__c)で直接取得し、HDY抽出・Won/Lost判定をPower Queryで行う案。ただしService側のスケジュール更新はSalesforce接続アプリ未承認(invalid_client/OAUTH_APPROVAL_ERROR_GENERIC、2026-07-15から管理者チーム対応待ち)で不可→承認されればGBCダッシュボードと同時に解決。レポート登録(購読)方式は1人7件上限で既に別用途が逼迫。それまでは現行のMac経由を継続。

**2026-10-06 訂正(ユーザー指摘)**: 上記「Service側スケジュール更新はSalesforce接続アプリ未承認で不可」は古い情報で誤り。GBCダッシュボードは2026-08-19〜25に`GBC__c`オブジェクトコネクタ直結へ切替済みで、ユーザー確認によりPowerBI Serviceが1日2回Salesforceから自動更新できている。→HDY用PowerBIの対HDYピッチも、GBCダッシュボードのJCI_All_Pitchesクエリ(GBC__c直結、HDY判定=GBCCompetitorsGroup__cに"博報堂/Hakuhodo")を複製して作る方針(Mac非依存)。sf_hdy_pitches.csvは週報(Mac側)用に継続。差異: CSV版は自由記入欄(競合その他/競合エージェンシー名/獲得エージェンシー名)や大広等も拾うため件数が多い(184件)。

**2026-10-06 手順書更新**: `HDY定点観測/PowerBI構築手順_20261006.md`(旧20261005版は残置)。aiconで作成・公開、CSV10本はaicon OneDrive(https://esq365-my.sharepoint.com/personal/aicon_dentsu_co_jp/Documents/戦略企画部/HDY定点観測/ 想定・要実パス確認)、対HDYピッチはGBCダッシュボードの`JCI_Pitch_Base`クエリ(列: Phase2, HDY, NetWin, # of Record, GBCCountry__c等)を複製し`SF_HDY_Pitches`としてvs_HDY/hdy_won列を追加。前回回答で`JCI_All_Pitches`と書いたのはページ名で誤り(クエリ名はJCI_Pitch_Base)。

**2026-10-06 Q&A**: aicon所有のワークスペース/セマンティックモデルでも、Salesforceのデータソース資格情報はmasaki.nakamuraのSalesforceアカウントでOAuth登録可能と回答(資格情報の入力操作は所有者aiconで行い、サインインする相手をmasakiにする)。注意: dentsu SalesforceはSSOのため、OAuth画面でaiconのMicrosoftセッションが自動で使われないよう、アカウント選択で masaki を選ぶ/InPrivateで行う。異動時はSF資格情報だけ後任で再登録すればよい(作り直し不要)。

**2026-10-06 手順書(ブラウザ版)**: ユーザーは会社MacにDesktopが無く**ブラウザ版(Service)前提**(明言)。最新手順書=`PowerBI構築手順_20261006_02.md`(_01=Desktop詳細版は使わない)。ワークスペースはPro(PPUは閲覧者全員PPU必要なので不採用、回答済み)。手順の要点: 「データを貼り付けるか手動で入力」で仮表_仮→セマンティックモデル作成→データモデルを開く→編集→クエリ→データの変換。1本目は空のクエリの数式バーに1行式、2本目以降は「複製」→詳細エディター(空クエリへの複数行貼付は壊れる既知の罠)。URLは日本語部分をURLエンコード。SF_HDY_PitchesはGBCダッシュボードのJCI_Pitch_Baseを詳細エディターからコピー。手順中の「新しい項目」「データを貼り付けるか手動で入力」「レポートの作成」等のラベルは未検証(ユーザーの画面で要確認)。

**2026-10-06 日経申請 差し戻し対応**: 13行目「導入が必要となる理由」(B13:G13結合)が空欄で差し戻し。サービス概要・業務用途/標準ICT環境で難しい理由(有料会員限定・局長級人事は日経のみ)/登録アカウント(@dentsu.co.jp、社貸与端末N650893のブラウザのみ)を記入し `N2_..._日経電子版_20261006.xlsx` で保存(日付欄も10/6に更新)。

**2026-10-06 PowerBI実名(設定値)**: ワークスペース名=「競合社定点観測(HDY)」、セマンティックモデル名=「競合社定点観測(HDY)」(手順書の`HDY定点観測`表記はこれに読み替え)。
**エラー対応**: CSVクエリ接続後の保存で `MaxConcurrentEvaluationsReached error code for SKU 'General'`(Power Query Online共有環境の同時評価数上限)。データ不備ではなく一時的な混雑。対処=数分待って再保存、他のPower Queryタブ(GBCダッシュボード等)を閉じる、それでもダメなら一部クエリの「読み込みを有効にする」を外して数本ずつ保存。

**2026-10-06 進捗**: CSV10本は数本ずつ保存で取込成功。SF_HDY_Pitchesの追加ステップで「Token ',' expected.」→直前ステップ末尾のカンマ不足 or `??`演算子非対応の可能性。`??`を使わない版(if [x]=null then "" else Text.From([x]))を提示。手順書に反映予定(未反映)。

**2026-10-06 進捗**: SF_HDY_Pitches(`??`なし版)成功。E-1でデータソースの資格情報画面に「接続をテストできませんでした」、Salesforce(https://login.salesforce.com/ aiconで管理)とWeb(esq365-my aiconで管理)が表示→各行の「資格情報を編集」でSF=OAuth2+masaki、Web=OAuth2+aicon(プライバシー組織)を案内。リンクが無い場合は歯車→接続とゲートウェイの管理から。

**2026-10-06 E-1進捗**: 資格情報は「設定→ゲートウェイとクラウドの接続→マップ先→新しい接続を作成」ルートで成功(Salesforce=masaki、接続名 競合社定点観測_Salesforce)。Webは1つ目成功、2つ目で「重複する接続名」→既存接続をマップ先で選ぶ、出なければ別名(_OneDrive_2)で作成と案内。

**2026-10-06 E-1**: 接続とゲートウェイの管理で、ユーザー=Concierge(Power Query Online編集時に自動作成される接続)の2件がオフライン: yamada_keitaの:x:/r/パス(2026/07/10、GBCダッシュボード作業時のもの)とaicon(本日10:49、CSVクエリ編集時)。スケジュール更新には使われないので放置でよいと回答(yamada分は削除しない)。判定は今すぐ更新→更新履歴の完了で行う。

**2026-10-06 E-2詰まり**: 今すぐ更新は成功するが、設定のデータソースの資格情報に「接続をテストできませんでした」が残りスケジュールのトグルがオンにできない(所有者aicon、ゲートウェイとクラウドの接続は全て青チェック)。案内: マップ先を選び直して適用→再読込。ダメならPower Automate(aicon、スケジュール済みクラウドフロー、9/12/15/18時30分、Power BI「データセットを更新する」)で代替。

**2026-10-06 PowerBI構築 完了(設定値)**: セマンティックモデル「競合社定点観測(HDY)」(ワークスペース同名、Pro、所有者aicon)。資格情報=「設定→ゲートウェイとクラウドの接続→マップ先→新しい接続を作成」で 競合社定点観測_Salesforce(masaki OAuth)・競合社定点観測_OneDrive(aicon OAuth)。PowerBIのスケジュール更新トグルは「データソースの資格情報」の古い警告が消えずオン不可→**Power Automateフロー「競合社定点観測(HDY)_定期更新」(aicon、スケジュール済み、毎日9:30/12:30/15:30/18:30 JST、Power BI「データセットを更新する」)で定期更新、稼働確認済み**。失敗時はPowerBIから通知が来ないのでフロー実行履歴で確認(Teams通知は未設定)。手順書最新=`PowerBI構築手順_20261006_03.md`(実施結果反映)。

**2026-10-06 失敗通知**: ユーザー依頼で、PAフロー「競合社定点観測(HDY)_定期更新」に Teams「チャットまたはチャネルでメッセージを投稿する」(フローボット→masaki)を実行条件=失敗/タイムアウトで追加する手順を案内(ユーザー作業、未完了確認)。注意: 「データセットを更新する」は依頼受付で成功扱い→PowerBI側の更新処理失敗は拾えない。拾うには鮮度メジャー+ダッシュボードのデータアラート+PAトリガーの追加案を提示(未依頼)。

**2026-10-06 失敗通知②の設計(手順書_20261006_04 E-3)**: PowerBIに`更新日時`表(DateTimeZone.UtcNow→SwitchZone(9)→#table)を追加。PAフローで 更新→Teams通知①(実行条件 失敗/タイムアウト)→遅延20分(実行条件 成功+スキップ)→「データセットに対してクエリを実行する」EVALUATE ROW("経過分", DATEDIFF(MAX('更新日時'[更新日時]), UTCNOW()+TIME(9,0,0), MINUTE))→条件 first(body(...)?['firstTableRows'])?['[経過分]'] > 30 → Teams通知②。テストは閾値-1で。ダッシュボードのデータアラート案は更新失敗時に判定されない恐れがあり不採用。ユーザー作業(未完了確認)。

**2026-10-06 フローレビュー(エクスポートzip)**: Recurrence(Tokyo 9/12/15/18時30分)・更新・通知①(Failed/TimedOut)・遅延20分(Succeeded+Skipped)・クエリ・条件>30は正しい。不具合2点を指摘: (1)「条件」のrunAfterが『チャットやチャネルにカードを投稿する_2』Succeeded→通常時はスキップされるため条件が動かず②が来ない→実行条件を『スキップされました』のみに。(2)Teamsアクションが『カードを投稿』(PostCardToConversation)で本文がプレーンテキスト→アダプティブカードJSONが必要で投稿失敗の恐れ→『メッセージを投稿』に差し替えかカードJSONに。

**2026-10-06 フロー再レビュー**: 条件のrunAfterが『カード_2: Skipped』に修正済みでOK。テナントのTeamsコネクタに『チャットまたはチャネルでメッセージを投稿する』が無い→カード投稿(PostCardToConversation)のまま、本文をアダプティブカードJSONに置換する方法(B)を3アクション分のJSONで案内。

**2026-10-12 OneDrive複製のdeadlock対策(個人Mac予備系で発覚)**: Teams「news_rss が2回連続失敗」の原因は収集ではなく、core.write_csv末尾の `shutil.copy2` → aicon OneDriveへの複製が `OSError [Errno 11] Resource deadlock avoided` で失敗し、例外が収集全体を失敗扱いにしていたこと(data/本体は書けていた。2026-10-07から断続的に発生し、468回記録。個人Mac側のOneDriveフォルダは10/8から更新が止まっていた)。修正: core.py に `mirror_to_onedrive()`(別プロセスの `cp -p`、communicateのtimeoutは60秒、kill後の回収待ちは5秒まで。失敗してもFalseを返すだけで例外を出さない)を追加し、run.py の収集ループ後に `resync_onedrive_mirror()`(data/*.csv のうちOneDrive側が古いものだけ再複製し、結果は run.log に「OneDrive複製: …」と出す)を追加。バックアップは ~/hdy_monitor_logs/{core,run}.py.bak_20261012。検証: 手動で `--role backup --only news_rss` を実行 → 成功し、遅れていた12件も再複製できた。コードはDropbox共有なので会社Mac主系にも同じ修正が反映される。
**2026-10-21**: 日経ID申請が承認された(ユーザー)。契約先として日経電子版の個人向け月額プラン(https://www.nikkei.com/promotion/、@dentsu.co.jpで登録)を案内。契約後にキーワードアラートの設定を案内する。
**2026-10-21 日経電子版 設定完了**: 契約済み(@dentsu.co.jp)。共有ブラウザ9226で日経にログイン済み(ユーザーが実施)。Myニュースのキーワードフォロー=博報堂/大広/読売広告社/Hakuhodo(キーワードフォローは /search?keyword=X の `.rn-follow-button`、管理は /mynews/recent/manage)。メール設定(regist.nikkei.com/ds/setup/mail.do)でMyニュースメール(#NEWS03_PC)のみオン、配信=平日朝夕・土日祝朝。collectors.mail に日経まとめメールを見出し+記事URLで1件ずつ取り込む分岐を追加(バックアップ collectors.py.bak_202610211400)。実メールの形式は未確認→初回受信後に取り込み結果を確認する。
**2026-10-21 日経の費用精算(設定値)**: 個人プランで契約(10/21申込、無料体験〜11/20、初回課金11/21に1,430円=日割、以降毎月1日に4,277円)。審議承認No=IS2610052。宮川さん指示: GBC契約ではなく個人契約、CASで「一般経費>立替払い>直接精算」、JUはWi-Fiと同じ。リマインダー=launchd `com.nakamura.nikkeiexpense`(毎月5日・25日9:30起動、スクリプト側で初回2026/11/25のみ・以降は毎月5日だけTeams INFO通知)、スクリプト `.claude-sync/Scripts/nikkei_expense/nikkei_expense_remind.sh`、会社Macのみ。マニュアル=OneDrive GBC_アレココ/☆局員向け資料/CAS経費/★★GBC_CAS経費操作マニュアル_20260422.pptx(P12-15)。
**2026-10-21 精算の設定値 更新(ユーザー指定)**: JU=10633725、勘定科目=5306250 調査費－データ購入費、7桁カテゴリーコード=GLOMG41(使用理由・内容欄の先頭に記入)。支払はコーポレートカード読み込み(引落→CAS反映に時差)のため、リマインダーを毎月20日9:30に変更、初回2026/12/20(11月日割分+12月分をまとめて案内)。使用理由の定型文はスクリプト内。
**2026-10-21 日経メール自動点検(ユーザー要望「言われなくても自動で確認」)**: `hdy_monitor/nikkei_check.py`、launchd `com.nakamura.nikkeicheck`(3時間ごと、会社Macのみ、ログ ~/hdy_monitor_logs/nikkeicheck.{out,err})、状態 state/nikkei_check.json。受信から4時間以上たった日経メールを判定: 初回の記事単位取り込み成功でOKを1回だけ通知/HDY言及があるのに取り込めていなければWARN+本文を state/nikkei_sample_<日付>.txt に保存(→その形式に合わせて collectors.mail を直す)/日経メール4日以上途絶でWARN(1回)。
**2026-10-22 日経メール取り込み修正(実メールで判明)**: 送信元 mynikkei@mx.nikkei.com、件名「【Myニュース】<見出し>」、本文は「MYニュースメール」〜「思った通りのニュースが届かない」の間に 見出し行→`[https://www.nikkei.com/article/…?n_cid=kobetsu]`。その後ろの「話題のトピック」は日経のおすすめで対象外。該当なしの回は「最新の記事はありません」。キーワード一致は記事本文でも起きるため見出しに社名が無い(例: 10/21 省エネ住宅事業の情報漏洩=事務局が博報堂)→ collectors.nikkei_articles() でキーワード欄の記事を is_hdy で絞らず全部記録するよう変更(バックアップ *.bak_202610221000)。10/21分を再取り込み、nikkei_check の初回OK通知済み。日経の記事は国内案件が多く scope=国内 になり、PowerBIの海外フィルタでは表示されない。
**2026-10-22 社内クリッピング(group-cc@dentsu.com)を記事単位で集計**: collectors.groupcc_articles(日本語版=博報堂DY欄全件+他欄HDY言及、英語版=HDY言及のみ)。1月〜再取り込みで2,270件(海外262)。詳細 [[work_status/2026-10-22_hdy_groupcc_nikkei_jinji]]。
**2026-10-22 日経人事→海外組織図(稼働)**: 収集器 `nikkei_jinji`(hdy_monitor/nikkei_jinji.py、週1=168h、会社Macのみ、共有ブラウザ9226のページ内fetch)。検索API `/.resources/search/partials?keyword=人事、<社名>&offset=&volume=50`、本文 `/article/<ID>/` の p.paragraph_*。2010-02〜2026-04の人事記事644本→発令10,096件、海外系497件、最新海外体制72人。CSV: nikkei_jinji / nikkei_jinji_overseas / nikkei_overseas_org / nikkei_kikou(機構改革)。Excel `reports/HDY海外組織_日経人事_YYYYMMDD.xlsx`(nikkei_jinji_report.py、Sansan名刺で日経に無い人を補完)。限界: 博報堂の海外ユニット長級は2014年以降日経人事欄に出ていない。PowerBIへのCSV追加は未実施。詳細 [[work_status/2026-10-22_hdy_groupcc_nikkei_jinji]]。
**2026-10-22 追記**: PowerBI手順書の最新版=`PowerBI構築手順_20261022.md`(G-14 日経人事)。スライド版 `reports/HDY海外組織図_日経人事_20261022.pptx`(競合研究デッキの体裁)。日経に出ない博報堂の海外ユニット長は不明のまま(名刺で補完)。
**2026-10-22 pbixで現状確認→手順書_20261022_01**: 最新pbix(ユーザーDL)で確認。モデルはクエリ26本・メジャー24本・リレーション14本・ページ11枚(概況/重要記事/国別の人材需要/人事ニュース/展開国マップ/海外組織図・主要人物/本社 海外関連組織と人数/対HDYピッチ/海外売上比率・地域構成/広告賞・海外事例/海外子会社の推移)、C〜G-12反映済み。G-13のレポート全体フィルターは未設定。自動日付テーブル有効。手順書最新版=`PowerBI構築手順_20261022_01.md`(H章=既存モデルへ日経人事4本を追加、year列は文字列)。ユーザー作業待ち。

- 2026-10-22 日経人事の海外組織xlsxをSharePointへ自動追加: 置き場=GBC戦略企画-HDY研究サイト(sites/GBC584-)「ドキュメント/HDY研究/【HDY海外組織_日経人事】」(同期パス ~/Library/CloudStorage/OneDrive-電通/GBC戦略企画-HDY研究 - ドキュメント/HDY研究/…、config.SP_JINJI_DIR)。collectors.nikkei_jinji が新着人事記事>0の回だけ nikkei_jinji_report.build_xlsx→publish(別名で追加、上書きなし)。PowerBIはフォルダURLへのボタン(手順書 _01 のH-9)。閲覧者はサイトメンバーである必要(追加は権限変更=要確認)。

- 2026-10-26 日経メール点検WARN(10-25分)の原因はパーサーではなく Dropbox 競合: 会社Mac(08:22)と個人Macが同時に data/items.csv を書き、会社Mac側の追記11件が「items (中村正樹 の競合コピー …).csv」へ退避→消失(10-23も同様に7件)。対処: core.merge_conflict_copies を add_items の先頭で呼び、競合コピーにしか無い行を戻してコピーは state/conflict_archive へ移す。10-07/08/21の古い競合コピーは意図的に整理した mail: 行なので戻さず archive へ。今回12件を復元。同種WARNが来たらまず data/ の競合コピーを確認。
- 2026-10-27 日経メール点検WARN(10-26分)は別原因: Outlook書き出しの遅れで08:20の収集時点ではメール未着、11:18の点検が先に判定。nikkei_check.py は state/mail.json の last_date より新しいメールを判定しないよう修正。11:25の収集で取り込み確認(mail 新規46)。
