---
name: feedback-extract-from-project-files-before-asking
description: "編集ソフトのプロジェクトファイル(prproj/aepなど)に既に答えがある情報は、ユーザーに手打ちで聞く前にファイルを直接パースして抽出を試みる"
metadata:
  type: feedback
  originSessionId: current
  modified: 2026-08-22T22:07:42.123Z
---

[[serbia_embassy_concert_video_revision]]の作業で、曲名テロップを置くための「各曲の開始タイムコード」をユーザーに尋ねようとAskUserQuestionを出したところ拒否された(ツール使用そのものが却下)。その後の会話では結局、ユーザーがPremiere上で曲名テロップクリップをV2に実際に配置してくれた後、その`.prproj`ファイル(gzip圧縮XML)を直接パースして`TrackItem→SubClip→Clip→Source`の参照チェーンを辿ることで、各クリップの正確な開始タイムコードをプログラム的に取得できた。

**Why**: `.prproj`はただのgzip+XMLなので、`gunzip -c file.prproj`で中身を読める。Premiereの内部オブジェクトグラフ(ObjectID/ObjectRef/ObjectUIDによる相互参照)はやや複雑だが、Python(xml.etree)でパースし、`parent_map`(子→親の逆引き)を作ってsibling探索・祖先探索をすれば、クリップ名→シーケンス上の配置時刻(Startティック値、254016000000ティック/秒)まで機械的に解決できる。ユーザーに「何分何秒か教えて」と聞くよりも、既にプロジェクトファイルに答えがあるならそちらを読みに行く方が速く正確(ユーザー側の手打ちミスも防げる)。

**How to apply**: 動画編集(Premiere/AE)や似た構造化バイナリ/XMLプロジェクトファイルを扱うタスクで、「特定のクリップがいつ配置されているか」「特定の値が何か」を知りたくなったら、まずユーザーに尋ねる前に元のプロジェクトファイル自体を(gunzip+XMLパース等で)機械的に読み取れないか試す。読み取れそうなら黙って抽出して使う。読み取れない/曖昧な場合(例: 音声のどこで曲が切り替わるかは無音検出だけでは判別不可能だった別の局面もあった)は素直にユーザーに確認する — 「ファイルに答えがあるはずの情報」と「ファイルだけでは判断できない情報」を区別すること。

より広い括りは[[feedback_token_conscious_practices]]参照(2026-08-31統合)。
