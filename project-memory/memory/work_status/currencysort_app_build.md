# CurrencySort（外貨判定アプリ）ビルド対応

## 2026-09-16T16:05
Status: in progress
What: 会社Mac側が個人Mac inbox(task-007)にCurrencySort(SwiftUI外貨OCR判定アプリ)の開発基盤を残し、個人Mac側で着手。Dropbox同期待ち（プレースホルダ化含め約15分）→Xcode本体が個人Macにも未導入と判明しApp Store経由でユーザーに手動インストールしてもらう→xcodegen generate→シミュレータSDKビルドで`AVCapturePhotoOutputPhotoDelegate`(存在しない型、正しくは`AVCapturePhotoCaptureDelegate`)のビルドエラーを発見・修正しBUILD SUCCEEDED、修正をコミット済み。
Next: ユーザー帰宅後、iPhoneをUSB接続してもらいSigning Team設定→実機ビルド・実行→カメラ撮影〜判定〜保存〜履歴〜国別集計の動作確認、可能なら実紙幣でOCR精度確認。完了したらpersonal_mac_inbox.mdのtask-007をStatus: doneに更新。

## 2026-09-17T06:50
Status: done
What: iPhone実機接続・Apple IDサインイン・Signing Team設定・Developer Mode有効化・開発者証明書信頼を経て実機ビルド・インストール・起動に到達。ユーザーと対話的に撮影→結果確認を繰り返し、4件の実バグを発見・修正（EXIF回転情報喪失でOCRが横倒し画像処理/カメラがマクロに切り替わらずピント合わず/短いOCR断片の偶然一致で無意味な候補乱立/ベトナムドン等ASCIIキーワードと実際のダイアクリティカル付きOCR結果の不一致）。診断用に結果画面へ撮影画像と認識生テキストの表示も追加。インド・ベトナム紙幣で一致度100%、保存/履歴/国別集計の一連動作を実機確認済み。硬貨(2ユーロ)はOCRの原理的限界で判定不可と判明（バグではなくREADME記載の既知TODO）。全修正をgitコミット済み、personal_mac_inbox.mdのtask-007をStatus: doneに更新済み。
Next: なし（完了）。さらなる通貨キーワード拡充や硬貨対応(Core ML検討)が必要になれば新規タスクとして立てる。

## 2026-09-17T08:25
Status: done
What: ユーザー依頼「画像特徴データから通貨判別」に対応。Kaggle World Coins dataset(32カ国8000枚)を30通貨に再構成しCreate MLで硬貨用画像分類器を学習(テスト精度93.7%)、Microsoft BankNote-Netの学習済みエンコーダをCore ML変換し紙幣用分類パイプラインも構築(97%)。CompositeCurrencyIdentifierでOCR+両分類器を統合。実機で対話的に検証し、(1)硬貨は撮影距離が精度に最も影響→点線円ガイド追加、(2)回転TTAの単純平均が逆効果と判明→最大値採用に変更、で改善。最終的に大きく写した硬貨で一致度92-96%を確認。全変更をgitコミット済み、README更新済み、プロジェクトメモリに詳細記録済み。
Next: なし（完了）。学習パイプライン一式は`~/CurrencySortML/`(Dropbox外)に保存、再学習手順はREADME参照。

## 2026-09-17T13:15
Status: in progress（Apple Developer Program登録待ち）
What: 硬貨判定精度をさらに改善（EuroCoinDataset 23カ国追加、95.7%）。実機で連続スキャン時にOOM Kill(強制終了)する重大バグを発見、複数の仮説的修正(解像度キャップ・縮小・autoreleasepool・リクエスト再利用・アダプティブTTA)を試すも解決せず、ユーザーからトークン使用量への懸念指摘を受けて一旦立ち止まり原因を再整理→真因判明（OCRと硬貨分類を`async let`で並列実行しVisionのピークメモリが重なっていた）→順番実行に変更し7回連続スキャンで再現しないことを確認。あわせてUI改善一式: Liveモード(シャッター不要のリアルタイムプレビュー、軽量判定パス)追加、カバー画像を元にChatGPTでアプリアイコン生成・設定、履歴クリアボタン追加、国別集計に円グラフ追加、「寄付済み」表記を「処理済み」に一般化(isDonated→isProcessed、モデル変更に伴い実機で一度データ不整合が起き削除→再インストールで解消)。PoC配布についてユーザーから相談を受けTestFlight配布とApple Developer Program登録($99/年)を案内、登録試行→本人確認却下→登録ページ自体が完全ブロック(フォーラムで既知の頻発パターン)→電話でのApple Developer Support問い合わせに誘導し無事問い合わせ完了。
Next: **ユーザーがApple Developer Programの登録可否についてAppleからの返答待ち**。登録完了後、Xcodeでチームを切り替えてTestFlightへのアップロード設定を行う。それまでは個人Macでの実機ビルド・インストールでの配布/テストを継続。
