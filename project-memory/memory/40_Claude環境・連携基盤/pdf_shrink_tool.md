---
name: pdf-shrink-tool
description: 汎用PDF軽量化スクリプト(画像解像度を落として確認用PDFを作る)、両Mac共通、場所とインストール要件
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-23T23:45:51.630Z
  originSessionId: d1d78d1e-9d04-439f-a4b6-a3e1ca509738
---

写真を多く含むPDF(冊子・写真集など)を、画像解像度を落として軽量化する汎用スクリプト `pdf_shrink.py` を作成済み(2026-08-23、[[subway_photo_booklet_project]]の小冊子PDF軽量化がきっかけ)。

**本体**: `~/ICPTokyo2022 Dropbox/中村正樹/.claude-sync/Scripts/pdf_shrink.py`(Dropbox同期、個人Mac/会社Mac共通)
**呼び出し用シンボリックリンク**: `~/Scripts/pdf_shrink.py`([[adobe_cli]]/outlook_cliと同じ配置方式)

**使い方**:
```
python3 ~/Scripts/pdf_shrink.py 入力.pdf              # 100dpiで圧縮(デフォルト)
python3 ~/Scripts/pdf_shrink.py 入力.pdf --dpi 150
python3 ~/Scripts/pdf_shrink.py 入力.pdf -o 出力.pdf
python3 ~/Scripts/pdf_shrink.py 入力.pdf --preset ebook
```

**中身**: Ghostscript(`gs`)の`-sDEVICE=pdfwrite -dPDFSETTINGS=/screen`+画像解像度指定のみ。ページレイアウト/トリムサイズ/ページ数は変更しない完全汎用ツール(小冊子専用の[[subway_photo_booklet_project]]内`subway_booklet_trim.py`とは別物で、トンボ切りなどの座標処理は一切しない)。ページ数の簡易整合性チェック(正規表現で`/Type/Page`をカウント)付き。

**依存関係**: Ghostscriptのみ。標準ライブラリのみで書かれているためpikepdf等の追加pipインストールは不要。

**会社Mac(d14461)でのセットアップ手順**(ユーザーから「pdf_shrink.pyを会社Macでもセットアップして」と言われたら — 2026-08-24に実施済み、以後はこの手順の再実行は不要、`which gs`で確認するだけでよい):
1. Dropboxが同期済みか確認(会社Macのマウントパスは個人Macと異なる可能性、[[dropbox_config_sync]]参照)
2. `ln -sf` で `~/Scripts/pdf_shrink.py` を上記Dropboxパスにシンボリックリンク
3. **注意: 会社Mac(d14461)はHomebrew未導入かつユーザーに管理者権限なし**(`groups`にadminなし)。`brew install`はsudoを要求し失敗する。この環境ではさらにインタラクティブなsudoパスワード入力もできない(TTYなし)ため、Homebrew導入自体が不可。
   - **実際に使った回避策**: root権限不要のmicromamba(自己完結バイナリ、`https://micro.mamba.pm/api/micromamba/osx-arm64/latest` からDL)を`~/.local/micromamba-bin/bin/micromamba`に展開 → `MAMBA_ROOT_PREFIX=~/.local/micromamba micromamba create -y -n tools -c conda-forge ghostscript` でconda-forge版gs(10.07.1)を`~/.local/micromamba/envs/tools/bin/gs`に導入 → `~/.local/bin/gs`にシンボリックリンク(`~/.local/bin`は`.zshrc`で既にPATH済み)。
   - 個人Mac(ICPTokyo2022)ではHomebrewが使える前提なので、そちらは従来通り`brew install ghostscript`でよい。会社Macだけこの回避策が必要。

**実績**: 237MB→1.1MB(99.5%削減)、10ページの小冊子PDFで動作確認済み(個人Mac)。会社Mac(d14461)でも2026-08-24にテストPDFで3.2MB→1.2MB(61.7%削減)を確認済み。
