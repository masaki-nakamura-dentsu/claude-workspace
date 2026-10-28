# GBCバンド新曲 楽譜化（Beautiful Mess / First Wind）

## 2026-10-08T14:20+09:00
Status: done
What: 2曲のmp3を自動採譜し、リードシート（ボーカルメロディ＋コードネーム＋ベース）をPDF/MusicXML/MIDI/.lyで `Photographer/2026/20261008GBCバンド新曲/楽譜/` に保存。パイプラインは ~/MusicTranscribe（詳細は memory music_transcription_pipeline）。
Next: ユーザー確認後、必要ならギター/キー/ドラム譜追加やコード・メロディの手直し。

## 2026-10-08T15:45+09:00
Status: done
What: v2作成。ギター/キーボード/ドラム追加、バンドスコア＋パート譜5種＋全パート確認用MIDI＋MusicXML(_20261008付きで 楽譜/ に保存)。精度改善: beat_thisでビート同期グリッド(旧版はテンポ推定ずれで後半ズレ)、CREPEでボーカル/ベースのf0、6ステム分離、打点特徴でドラム判別、HMMコード推定。
Next: 外部Webサービス(Klangio等)へのアップロード可否をユーザーに確認中。

## 2026-10-08T17:30+09:00
Status: done
What: 外部3サービス(Klangio/Songscription/Moises)をmaxakisan専用ブラウザ(port 9230)でサビ30秒比較→Klangioが最良だが全曲・DLは有料(1曲¥299)、ユーザーは課金しない判断。比較結果を取り込みv3作成(_20261008_01): ギターをコード×ギターオンセットのパワーコード8分刻み+TAB、ハイハット8分を小節単位判定、原曲と実時間同期の確認用MIDI(pretty_midi、拍位置そのまま)、テンポ表記を平均IBIで128.6/144.5に修正、ベースの空白をbasic-pitchで補完。
Next: ユーザーの試聴フィードバック待ち。

## 2026-10-08T17:45+09:00
Status: done
What: 確認用MIDIのミックス調整(ドラムが大きすぎるとの指摘)。CC7音量 Vo110/Ba100/Gt72/Dr70/Key62/Pad45、ドラムのベロシティ キック85/スネア78/ハイハット42、パン Gt左/Key右。_20261008_02.mid として保存。
Next: 試聴フィードバック待ち。

## 2026-10-08T17:50+09:00
Status: done (paused)
What: ユーザーがプロジェクトメンバーに確認するため、このチャットはいったん終了。最新の納品物: 楽譜/ の `_20261008_01`(スコア・パート譜・MusicXML・ly) と `_20261008_02.mid`(バランス調整版の確認用MIDI)。
Next: メンバーのフィードバック(曲名・小節・パート単位)を受けて修正。作業環境は ~/MusicTranscribe(v4_*.py)、手順は memory music_transcription_pipeline。

## 2026-10-08T18:00+09:00
Status: done (paused)
What: 「Klangioの結果をどう全体に反映したか・精度は上がったか」の質問に回答。Klangioのファイルは取り込んでいない(DL不可)。参考にしたのは書き方の方針(ギター)とコード・テンポの答え合わせのみで、精度の定量評価はしていない、と説明。
Next: 希望があればKlangio無料20秒との小節単位比較で部分的な精度検証。

## 2026-10-27T10:20+09:00
Status: done (返信は未投稿・本人確認待ち)
What: Teams「バンドやろうぜ」で木村さんから依頼(10/26)の「Keep it Rolling2.mp3」をTeams添付(SharePoint, CDP 9226のctx.requestで?download=1)から取得し、既存パイプラインをコピー(~/MusicTranscribe/k_*.py)して採譜。Eb major/約167BPM(beat_thisが83↔167で揺れるが make_grid が補間)/157小節。出力は `Photographer/2026/20261027GBCバンド候補曲_KeepItRolling2/楽譜/`(バンドスコア・パート譜5種・MusicXML・ly・確認用MIDI(ミックス適用済み)、末尾_20261027)。lilypond出力名が `-Score.pdf` のように曲名が抜けるので手でリネームした。
Next: 田辺さん依頼の「PDF/MIDI→音を鳴らして原曲と比較する」検証フローは未着手(確認用MIDIは作成済み)。Teams返信は本人確認後に投稿。

## 2026-10-27T10:50+09:00
Status: done (paused)
What: Keep it Rolling2の精度確認(コード一致0.415でBM0.422/FW0.412と同程度、ドラム再現率0.68/正確さ0.94、スケール外音は声5.2%/ベース5.4%)。田辺さんへ渡すMIDI3本(KIR2 _20261027、FW/BM _20261008_02)を案内。Teams返信・MIDI投稿は本人が実施予定(未投稿)。ユーザーはメンバーの反応待ちでチャット終了。
Next: 反応が来たら ~/MusicTranscribe の k_*.py(KIR2用コピー)と *_v4.pkl を編集して再生成。田辺さんの「PDF/MIDIを鳴らして原曲比較」検証とBeautiful Mess修正は未着手。
