---
name: company-mac-no-admin-no-homebrew
description: 会社Mac(d14461)はユーザーに管理者権限がなくHomebrew等sudoを要するインストール手段が使えない、root不要の回避策(micromamba)を確立済み
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6de2ed38-d5c2-4b6a-9592-c6797ea7bcd1
  modified: 2026-10-01T00:56:55.779Z
---

会社Mac(d14461)は2026-08-24時点でHomebrew未導入、かつユーザー(d14461)は管理者(admin)グループに属していない(`groups`コマンドで確認済み)。この環境ではsudoパスワードの対話入力もできない(TTYなし)ため、`brew install`のようなsudoを要するインストール手順は原理的に使えない。IT部門経由のヘルプデスク依頼か、以下のroot不要の回避策のどちらかになる。

**確立済みの回避策(2026-08-24、[[pdf_shrink_tool]]のGhostscript導入で実施)**: micromamba(自己完結型の単一バイナリ、`https://micro.mamba.pm/api/micromamba/osx-arm64/latest`からDL、インストーラ不要)を使い、conda-forgeからCLIツール/ライブラリをroot権限なしでユーザーディレクトリ配下(`~/.local/micromamba/envs/...`)に導入する。バイナリは`~/.local/bin/`(既に`.zshrc`でPATH済み)にシンボリックリンクして通常コマンドとして使えるようにする。conda-forgeにパッケージがあれば大抵のCLIツール(画像/PDF処理系、圧縮系など)がこの方法で導入可能。

**How to apply**: 会社Mac(d14461)で新しいCLIツール/ライブラリの導入が必要になったら、まず`which brew`と`groups`で毎回状況を再確認するのではなく、この制約を前提にいきなりmicromamba経由の導入を試みてよい(2026-08-24にユーザーが「非rootで用意する方法を試す」を選択し、IT部門への依頼より先に技術的回避策を試すことを支持した)。個人Mac(ICPTokyo2022)はHomebrewが使える前提なので、この回避策は会社Mac限定。

**2026-10-01追加 — GUIアプリ(.app)はmicromambaすら不要な別ルートがある**: LibreOfficeを導入する際に判明。`/Applications`はroot:adminグループ所有で書き込みには管理者権限が要るが、`~/Applications`(ユーザー自身のホーム配下)は最初から書き込み可能で、macOSは`.app`バンドルをどこから実行しても問題なく動く。つまり.pkgインストーラではなく**.dmgをマウントして中の.appを`~/Applications`へコピーするだけ**で、sudo・Homebrew・mas・micromambaのいずれも使わずにGUIアプリを導入できる。CLIから叩きたい場合は、中のバイナリ(例: `LibreOffice.app/Contents/MacOS/soffice`)を`~/.local/bin/`へシンボリックリンクすればPATHに乗る(既存のmicromambaパターンと同じ置き場所)。**How to apply**: 会社Macで「.appとして配布されるGUIアプリ」の導入依頼が来たら、まず公式配布が.dmg(.pkgではなく)かを確認し、.dmgであればこのルートを最初に試す — micromamba/conda-forgeにそのアプリが無いか探す前に、これが一番早い。詳細事例は[[work_status/company_mac_libreoffice_install_20261001]]参照。

関連: [[feedback_sudo_and_mas_install_limitations]]は「管理者権限があってもClaude CodeのBashツールは対話的sudo/大容量mas installを実行できない」という、どのMacでも当てはまるツール側の制約(本ファイルの「会社Macにはそもそも管理者権限が無い」という機種固有の制約とは別種)。
