# アニメIP海外検索トレンドダッシュボード

## 2026-08-27T17:40:00+09:00
Status: in progress
What: 新規プロジェクト開始。要件ヒアリング(Artifact形式のWebダッシュボード/SNS除外/少数タイトル×少数国のプロトタイプ、をユーザーが選択)後、Google Trends(pytrends経由)でSpy x Family/Jujutsu Kaisen/One Piece/Demon Slayer/Attack on Titan × 米・仏・伯・インドネシア・比 の実データを収集し、WebSearchでタイトル毎の最新ニュース(コラボ・イベント)も収集。ランキング+タイトル詳細の2タブ構成のArtifactダッシュボードとして公開完了(実データのみ、モック無し)。YouTube/Googleマップ/ニュース国別フィルタは未接続と明記。
Next: ユーザーの都合で本日は終了。次回はYouTube Data APIキー発行の要否確認、タイトル/国の拡張、または定期更新の自動化について相談してから着手する。詳細は project memory `anime_ip_search_dashboard_project.md` 参照。

## 2026-09-17T14:20:00+09:00
Status: done
What: ユーザーから「GeminiのアニメIP分析プロンプト(市場レポート/ランキング/トレンドの3機能)をAgency OSに組み込みたい」と相談。Agency OS(ChatGPT Skill、GBC戦略企画部のクライアント提案書生成ツール)にはGeminiのようなGoogle Trends/YouTube/Googleマップのネイティブ連携が無いという技術的制約を説明した上でAskUserQuestionで方針確認し、「既存のこのダッシュボードを本格拡張する。Agency OS連携は次回」という結論に着地。Geminiプロンプトの①②③全機能をカバーする方針で、5カ国(US/FR/BR/ID/PH)×7項目の市場データ、5タイトル×4項目(コラボ事例/検索インテント/視聴者熱量4軸/エンゲージメント密度)の深掘りデータを4体のgeneral-purposeエージェントに並列でWebSearchさせ収集(すべて実在の参照URL付き)。ダッシュボードを「市場レポート」「タイトルランキング(SMS)」「タイトル×国 詳細トレンド」の3タブ構成に拡張し同一URLで再公開(https://claude.ai/code/artifact/99375019-caf8-4805-a43a-9f23a947cf75)。SMSスコア(Search Volume 40%+Momentum 30%+Engagement Density 30%)のうちEngagement Densityは実測APIが無いため定性データに基づく5段階の参考スコアとして実装し、UIとfooterに「実測値ではない」旨を明記(捏造防止)。
Next: Agency OS(SKILL.md/SKILL_Dify.md)との連携方法(参照導線を追加するか等)をユーザーと相談してから着手。YouTube Data APIキー発行の要否、タイトル/国の拡張も未着手のまま。

## 2026-09-30T13:55:00+09:00
Status: done(TODO.mdの5項目中4項目。⑤個人Mac環境構築のみ未着手)
What: 前回セッションが残したTODO.md(タイトル増量/2レンズ分離/属性別ランキング/日英併記/GB欠落再取得/個人Mac化)についてAskUserQuestionでユーザーに優先度確認 → ①②④⑥に加え③(推計値と明示した上で実装)も承認され、5項目中4項目を実施。Artifactを99375019(旧URL)からVersion7として再公開(新URL: https://claude.ai/artifact/KvM7kk6va5bokmQouvj6Za)。22タイトル×11ヶ国に拡張、ランキングタブに「合成指標(SMS)/グローバルファン人気(AniList)/現地検索関心(Google Trends)」のレンズ切替と、性別・年代ターゲット層による並び替え(推定値、注記付き)を追加。タイトル名の日英併記(AniList native表記)も反映。GB(イギリス)の欠落5タイトルも再取得成功。
発見したバグ2件(共に修正済み): (1)新規タイトル"Re:ZERO -Starting Life in Another World-"の記号(コロン+ハイフン)がpytrendsリクエストを壊し11ヶ国全滅していた→クエリ語のみ"Re:Zero"に差し替えて解決。(2)GB再取得データのキーがAniList生表記のままで正規化済み表示名と不一致、Demon Slayer/Jujutsu Kaisenが実際にはマージされていなかった→逆引き辞書で正規化して解決。既存の`dom_stub_check.js`に加え、`document.querySelector`(単数形)がスタブ未対応と気づき事前に`getElementById`へ書き換え、さらに11ヶ国×3レンズ×3性別×3年代の総当たりテストスクリプト(`test_lens_logic.js`)を新設して公開前に検証。
Next: ⑤個人Mac環境構築は未着手(会社Macでは検証不可)。既存ギャップとしてSpy x Familyが拡張6ヶ国(GB/DE/MX/IN/VN/KR)で未取得のまま残存(今回作業とは無関係、表示上は自動除外されクラッシュしない)。詳細は`TODO.md`(2026-09-30更新版)とproject memory `anime_ip_search_dashboard_project.md`参照。

## 2026-09-30T14:30:00+09:00
Status: done
What: v7公開後、ユーザーから「タイトル数がまだ少ない・提案ブリーフも1件だけ」と指摘。ArtifactからPowerBI+永続データストアへの方向転換案を提示し議論。並行して、Agency OSへのGemini版アニメIP分析プロンプト移行の是非について技術検証(GeminiのGoogle Trends/YouTubeデータは認証API連携ではなくWeb検索合成であり、これが「ランキングのブレ」の原因であることをGeminiへの直接質問+Dify版SKILL.mdの制約記述の突合で特定)。ユーザーはこの内容をプロンプト提供者の榎本さんへ共有し、「Agency OSへの移行は一旦保留、Gemini運用は継続、検索によらない安定データ取得法を自分の方で検討する」という結論で着地。
Next: タイトル増量(PowerBI移行含む)・提案ブリーフ拡充は次回以降。詳細はproject memory `anime_ip_search_dashboard_project.md`(続き9・続き10)参照。

## 2026-09-30T17:50:00+09:00
Status: done
What: ユーザーから「pytrendsはファンデータでは」との質問→実は逆(pytrends=一般大衆検索、AniList=コアファン)と整理し、マスコミュニケーション視点の補強データソースを設計・実装。Netflix Top10(公式週次一括TSV)/Wikipedia pageviews(Wikidata経由の言語版PV)/YouTube Data API(公式トレーラー再生数)の3つを新規実装し、既存のAniList+Google Trendsと合わせて5レンズ体制に。YouTube APIキーは会社Googleアカウントでは発行不可と判明(組織ポリシー、個人Gmailで解決)。データ収集中にWikidata自動解決の誤爆(One Piece→衣服、Attack on Titan→ビデオゲーム等)を発見・修正。最終的に5ソース分をPowerBI取り込み用のdim/fact CSV(6ファイル)としてpowerbi_exportフォルダに出力完了。
Next: このCSVセットをPowerBIに実際に取り込み、レポート構築へ進む。詳細はproject memory `anime_ip_search_dashboard_project.md`(続き11)参照。
