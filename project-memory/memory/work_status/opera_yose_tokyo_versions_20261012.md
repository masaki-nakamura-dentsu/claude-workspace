# オペラ寄席東京(2026-09-13) Long/3min/1min 作成
Status: done (2026-10-13 0:xx) — 本人が_20261012_01.prprojを開いて確認待ち
- 参照: 岸和田prproj(Dropbox placeholder→TextEditでbackground open して実体化)の「寄席オペラ岸和田・霞町 Long/3min/1min」構成を解析済み
  - 3min: 冒頭(楽屋2カット+ロゴ4s)→各曲約12s×(曲名テロップpsdをV3、ロゴ横をV4に通し)→魔笛.ai→落語短カット群→写真3枚+笑いSE→スタッフロール。全カット0.8sクロスディゾルブ
  - 1min: 同構成で各曲約3.5s
  - Long(約57分): 各曲フル+落語ダイジェスト約11分
- 東京の現状: 第一部_オペラ_マルチカム下地はユーザーがカメラ切替編集済み(〜3983s, song_1-8テロップ配置済、9/10未配置)。第二部_落語は未編集
- PprBridgeに place-range/place-still/export-audio/open-sequence を追加(jsx+ppb.py)、CEPフォルダにデプロイ済。__reloadHostは__dirnameずれで壊れていた→main.jsのHOST_JSXを絶対パスに修正。汎用evalコマンドはauto modeで拒否(RCE扱い)→専用コマンドに変更
- 次: ユーザーがパネル開き直し→第一部/第二部の音声書き出し→曲境界・拍手/笑い検出→3シーケンス生成
- 2026-10-13: カット269本+XMLでアングル割当、テロップ10点修正、Long/3min/1min生成。クロスディゾルブ未適用

## 2026-10-24 フィードバック対応(3min)着手
Status: waiting(ブリッジ未接続)
依頼: ①映像にブラー②演奏にリバーブ(ナレは無し)③冒頭ナレ「今回の寄席オペラはこの…」→「この」削除(正しくは"オペラ寄席")④アップを減らし引きのステージ全景へ⑤ワレンチナ独唱の曲名テロップ「優雅な月」→「カルメン」。**3minを複製してから修正(既存は上書きしない)**。
確認済: 最新prprojは_20261012_01.prproj(10/18)。1min_v2もある。PprBridge heartbeat停止中(Premiereは7:04起動済)→本人にパネルを開いてもらう必要あり。

## 2026-10-24 フィードバック対応 実施(3min/1min/1min_v2の複製に適用)
Status: waiting(本人が `_20261024_01.prproj` を開いて確認)
- 複製: `オペラ寄席東京 3min_20261024` / `1min_20261024` / `1min_v2_20261024`(元は無変更)。保存先 `..._20261024.prproj`(API適用後)→ `..._20261024_01.prproj`(アングルをXMLで引きに変更済、これが最新)
- 実施: ナレ「この」を無効化(3min 4.62-5.08s / 1min 2.20-2.75s、元ナレは「寄席オペラは」と発話)/ ブラー(ガウス)量8をV1全体 / スタジオリバーブ(既定wet25%)を演奏クリップのみ(ナレ・出囃子・SEは除外)/ 7曲目をカルメン(Long 3340s付近、Valentinaソロ)+テロップsong_10に差替(3min)、1minは3345s / 引き: V1を本編マルチカムの直接クリップに置換し、CAM3(index2)とCAM2(index1)を交互(3minは14s曲を半分で切替)
- 学び: ネスト(Long)から直接マルチカムに置換すると音量が曲ごとに変わる(Longに編集ゲインあり)→曲ごとに比率でA1レベル補正。overwriteClipはV/A連動で、音声だけ戻せない。

## 2026-10-24 第2回FB(進行中)
Status: in-progress。開いているのは `_20261024_01.prproj`。作業用スクリプトは scratchpad の build.py/angles.py(消える可能性あり)
指示: ①ブラーは「元映像+ブラー複製を不透明度30%で上のトラックに」(V1のブラーはamount0にするか除去) ②クローンのV1クリップはIsMulticam=falseで全CAM1化→XMLでIsMulticam=true+全カメラ使用(CAM1は3minのみ頻度を下げる、1min/v2は均等) ③リバーブ強化(大ホール感。Studio Reverb: room1.0/decay高/wet~0.5) ④「この」は無音でなく削除→ナレを遅らせ、ナレ終了直後に音楽(3min:切り位置4.40s→音楽5.77sの直前に着地、シフト約+1.2s。1min:Long2.4-4.40を3.22sで終わるよう+1.22s。ナレ音声はa3.wav/a1.wavを切ってwav化→A3に配置、元A1先頭クリップは無効化) ⑤カルメン差替は**そのまま触らない**(再度クライアント確認)
ppbの追加コマンド(exportFrame/addAudioEffectToTrack等)はpprbridge.jsxに実装済み。
- 2026-10-24 第2回FB適用済 → `_20261024_02.prproj`(最新、本人が開いて確認待ち)。ブラー複製(V3/コピー用トラック,量25,不透明30%)、V1ブラー0、ナレ=別wav(素材/ナレ_*.wav)をA3へ遅延配置(3min 2.0s開始〜5.59s、1min 1.27〜3.2s)、リバーブ dry1.0/wet0.75/room1.0/decay0.85、XMLでSelectedTrackIndex+IsMulticam追加(3minはCAM1少なめ、1min/v2は均等)。カルメン差替はそのまま。スクリプトは .claude-sync/Scripts/{angles,blurcopy,rv}.py
