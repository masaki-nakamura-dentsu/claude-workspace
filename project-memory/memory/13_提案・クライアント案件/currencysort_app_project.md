---
name: currencysort-app-project
description: 外貨判定iPhoneアプリCurrencySort（SwiftUI+SwiftData、オンデバイスOCR）の開発状況・場所・既知の制約
metadata: 
  node_type: memory
  type: project
  originSessionId: f93e50d1-bd7c-49e4-82a3-5ac3d32fbcbf
  modified: 2026-09-17T13:18:18.044Z
---

空港などで余った外貨（紙幣・硬貨）をカメラで撮影し、Vision framework（オンデバイスOCR、通信不要）で印字文字を読み取って国・通貨を判定、国別に仕分けて寄付する作業を助けるiPhoneアプリ。

場所: `中村正樹/Software/CurrencySort/`（Dropbox配下、git管理下、`main`ブランチ）。
構成: SwiftUI + SwiftData、`project.yml`が正（`.xcodeproj`はgit管理外、`xcodegen generate`で生成）。deploymentTarget iOS 17.0、SWIFT_VERSION 5.0（Swift 6厳格並行性チェック非該当）。詳細アーキテクチャは`README.md`に記載。

**Why**: 会社Mac(d14461)はXcode本体が未インストール（Command Line Toolsのみ）で開発基盤の構築・構文チェックまでしかできなかったため、[[mac_handoff_relay]]の仕組みで個人Mac(ICPTokyo2022)側に実ビルド・実機テストを依頼した（2026-09-16、task-007）。

## 現状（2026-09-17時点、実機テスト完了・task-007 done）

- 個人Mac側にもXcodeが未導入だったためApp Store経由で手動インストール（Xcode 27.0）。`mas install`はApple側の大容量アプリ再ダウンロードAPI制限で失敗、GUI経由が必要だった（[[feedback_sudo_and_mas_install_limitations]]参照）。
- `xcodegen generate`→シミュレータSDKビルド→実機（iPhone 16 Pro「iPhonemn」）ビルド・インストール・起動まで到達。Xcodeで無料Apple ID(maxakisan@gmail.com)サインイン、Signing Team設定、iPhone側Developer Mode有効化・開発者証明書信頼が必要だった（いずれもGUI操作、CLI化不可）。
- 実機での対話的デバッグで**4件の実バグを発見・修正**（すべてコミット済み、mainブランチ）:
  1. `CameraPreviewView.swift`: `AVCapturePhotoOutputPhotoDelegate`という存在しない型指定（正: `AVCapturePhotoCaptureDelegate`）— シミュレータビルド時に発見
  2. `CameraPreviewView.swift`: 撮影画像が`.cgImage`でEXIF回転情報を失い、OCRが横倒し画像を処理していた → orientation焼き込み済みCGImageに正規化
  3. `CameraPreviewView.swift`: カメラが`.builtInWideAngleCamera`固定でマクロ撮影に切り替わらずピントが合わなかった → `.builtInTripleCamera`優先の仮想デバイス選択に変更
  4. `OCRCurrencyIdentifier.swift`: 短い(1-2文字)OCR断片が複数通貨キーワードに偶然部分一致し無意味な候補が並ぶ → 3文字未満を除外
  5. `OCRCurrencyIdentifier.swift`: ベトナムドン等、`currencies.json`のキーワードがASCII表記なのに実機OCRはダイアクリティカルマーク付きで返り不一致 → `.folding(.diacriticInsensitive)`で正規化
- 診断用に結果画面へ撮影画像サムネイルと（候補ゼロ時のみ）OCR認識生テキスト表示を追加（恒久機能として維持、キーワード追記の判断材料になる）。
- 実機最終確認: インド紙幣(500ルピー)・ベトナム紙幣(20,000ドン)ともに一致度100%、保存→履歴→国別集計の一連の流れも正常動作確認済み。
- **既知の残課題（バグではない）**: 硬貨（2ユーロで確認）はOCRが文字を1件も検出できず判定不可。刻印文字は低コントラスト・湾曲していてVisionのテキスト認識が苦手なため。README記載のTODO「硬貨対応の強化（Core ML画像分類検討）」が対応の方向性、今回はスコープ外。

## 硬貨対応: Core ML画像分類器を追加（2026-09-17）

ユーザーから「通貨を画像の特徴データから判別できるようにしたい」と依頼があり着手。

- **データセット**: [World Coins (Kaggle, wanderdust/coin-images)](https://www.kaggle.com/datasets/wanderdust/coin-images) — 32カ国・約8000枚・211額面クラス。国→ISO通貨コードにマッピングし直し、30通貨（アプリの34通貨辞書のうち30個と一致、驚くほど好相性）に集約して学習データを再構成。
- **学習環境**: `~/CurrencySortML/`（Dropbox外、venv含む。理由は[[feedback_venv_outside_dropbox_sync]]と同じくGB単位のデータをDropbox同期対象に含めないため）。Python 3.11のvenv（Homebrew既定は3.14でtensorflowが非対応だったため個別インストール）。
- **硬貨分類器**: Create MLフレームワーク（`xcrun swift train_coin_classifier.swift`、GUIなしでコマンドライン学習可能）でMLImageClassifierを学習。テスト精度93.7%、モデルサイズ176KB（Vision内蔵特徴抽出器を使う転移学習のため軽量）。
- **紙幣分類器（バックアップ用）**: [Microsoft BankNote-Net](https://github.com/microsoft/banknote-net)の学習済みMobileNetV2エンコーダ(.h5)をcoremltools(TensorFlow 2.21+tf-keras互換レイヤ経由)でCore ML変換、17通貨の埋め込みデータでKeras分類ヘッドを学習(97%)、encoder+classifierを1つのpipelineモデルに結合。紙幣はOCRで既に100%的中しているため主目的はOCRのバックアップ。
- **Kaggle認証**: 新方式のaccess token(`KGAT_...`形式)を`~/.kaggle/access_token`に保存して使用（旧来のkaggle.json username+key方式ではない）。
- **統合設計**: `CompositeCurrencyIdentifier`がOCR+2つの画像分類器を並走させ、通貨ISOコードごとに最大確信度の候補を採用。
- **重要な学び（実機検証で判明）**:
  1. 硬貨は撮影距離が精度に最も強く影響する（画面に大きく収まれば90%超、小さいと30-50%）。カメラ画面に点線円ガイドを追加して対策。
  2. 硬貨には「正立」の基準がないため複数回転させて判定するTTAを試したが、**単純平均は逆効果**（1方向の高確信度が他の学習してない回転角度の低い値で薄まる）。**最大値採用に変更して解決**。
  3. コインの中には「加盟国共通デザイン面」（ユーロ硬貨の裏面など）があり、その面だけでは国を特定する情報が本質的に乏しい場合がある（学習データ自体がこの面を多く含んでいたため発覚）。

## 重大バグ修正: 連続撮影OOM Kill（2026-09-17続き）

実機で3回前後連続スキャンするとiOSにメモリ不足で強制終了(signal 9)される事故が発生。
原因は**OCR(`.accurate`高解像度)と硬貨画像分類(4方向TTA)を`async let`で並列実行**し
ピーク時にVisionの一時メモリが重なっていたこと。`CompositeCurrencyIdentifier`で
順番実行に変更して解決(7回連続スキャンで再現しないことを確認)。他に撮影解像度キャップ・
判定前縮小・autoreleasepool明示・VNCoreMLRequest使い回しも対策として実施済み。
**教訓: Vision/CoreMLの重い処理(OCR .accurate、CoreML分類TTA)は絶対に並列実行しない。**
紙幣用のBankNote-Net予備分類器はコストに見合わず削除、OCR+硬貨Core ML分類のみの
構成に整理。EuroCoinDataset(23カ国)追加でユーロがスペインのみ学習だった問題も解消
(テスト精度93.7%→95.7%)。

## 続き: UI改善・アイコン・PoC配布準備（2026-09-17後半）

- **カメラ画面**: 点線円ガイド、Liveモード（シャッター不要のリアルタイムプレビュー、
  `bolt.fill`アイコンでは分かりにくいとフィードバックを受け「Liveモード ON/OFF」の
  テキストボタンに変更）。Liveモードは軽量版判定(`quickIdentify`、1方向のみ・
  顕著性クロップなし)を約1秒間隔で実行、シャッターは引き続き高精度パスを使用。
- **アプリアイコン**: 活動のカバー画像（「外貨コイン仕分けワークショップ」バナー、
  手+硬貨イラスト）を参考にChatGPTで生成。個人アカウント(maxakisan@gmail.com)の
  共有ブラウザで作業中、Googleアカウント選択で個人/会社アカウントが混線してハング
  →新規専用Chromeプロファイル(`chatgpt-work-bot`、port 9229)を作りmasaki.nakamura@
  dentsu.co.jpでログインし直して解決。
- **履歴/国別集計**: 履歴クリアボタン追加（国別集計も同じ`ScanRecord`参照のため自動連動）、
  国別集計に円グラフ(Swift Charts `SectorMark`)追加。`isDonated`→`isProcessed`に
  リネーム（「寄付済み」固定表記はユーザー指摘により撤回、用途は必ずしも寄付とは
  限らないため）。**注意**: このモデル変更後、旧シェーマのSwiftDataストアが残っている
  実機で保存したデータが履歴/集計に反映されない不具合が発生→アプリ削除→再インストール
  (開発者証明書の再信頼が必要)で解決。今後モデルのプロパティ名を変える際は同じ問題に
  注意。
- **PoC配布**: TestFlightにはApple Developer Program登録($99/年)が必要と案内。
  ユーザーが登録試行→本人確認却下→登録ページ自体も「現在Apple Developer Programへの
  登録は完了できません」で完全ブロック（フォーラムでも既知の頻発パターン、オンライン
  問い合わせページも読み込めず八方塞がりになりやすい）。電話(0120-277-535、Apple Japan
  一般窓口)での問い合わせに誘導し、無事問い合わせ完了。**Developer Program登録は
  この時点で未完了、ユーザーからの返答待ち**。登録完了後にXcodeでチーム切替→
  TestFlightアップロード設定が次のステップ。

## How to apply

さらなる通貨キーワード拡充や硬貨判定精度向上（自前撮影データ追加、円ガイド充足度の自動検知等）を頼まれたら、まず`personal_mac_inbox.md`のtask-007のResultとこのファイルを確認してから着手する。硬貨分類器の再学習手順はリポジトリの`README.md`「硬貨用画像分類モデルの再学習方法」参照。新たな作業は新規タスクとして`personal_mac_inbox.md`か`company_mac_inbox.md`に立てること。

関連: [[mac_handoff_relay]]（会社Mac→個人Macへの作業依頼の仕組み）、[[feedback_sudo_and_mas_install_limitations]]

## 再インストール手順（2026-09-28、無料Apple ID署名の7日期限切れで起動不可になった際）

無料Apple IDの開発署名は**7日で失効**し、アプリが起動しなくなる。Developer Program登録までは定期的に再インストールが必要。
CLIで完結する手順（iPhonemnをUSB接続した状態で）:
1. `xcodegen generate`（※project.ymlにチームIDがないため生成後はTeam未設定になる）
2. `xcodebuild -project CurrencySort.xcodeproj -scheme CurrencySort -destination 'id=00008140-000E48E91EE3001C' -derivedDataPath ~/CurrencySortBuild -allowProvisioningUpdates DEVELOPMENT_TEAM=ADVX2Z9V96 CODE_SIGN_STYLE=Automatic build`
3. `xcrun devicectl device install app --device 00008140-000E48E91EE3001C ~/CurrencySortBuild/Build/Products/Debug-iphoneos/CurrencySort.app`
4. 初回起動時に「信頼されていない」エラーになる場合はiPhoneの 設定→一般→VPNとデバイス管理→maxakisan@gmail.com を信頼（CLI不可）。
Team ID: ADVX2Z9V96（maxakisan@gmail.com 個人チーム）。bundle id: com.nakamura.currencysort。
