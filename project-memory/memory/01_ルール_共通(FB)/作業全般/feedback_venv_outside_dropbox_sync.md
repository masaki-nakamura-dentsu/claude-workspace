---
name: feedback-venv-outside-dropbox-sync
description: 開発環境(Python venv、頻繁に書き換わるログファイル等)はDropbox同期フォルダの中に絶対に置かない、全プロジェクト共通ルール
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2b1d5fa-32d1-43c1-a288-bd925645a6b0
  modified: 2026-08-17T00:14:43.882Z
---

Pythonの`.venv`(仮想環境)や、頻繁に追記されるログファイルは、Dropbox同期対象のプロジェクトフォルダの
**外側**(ローカル専用パス)に置く。プロジェクトのコード本体(`.py`/設定/出力データ)はDropbox同期でよいが、
OS依存のバイナリや高頻度書き込みファイルは同期させない。

**Why**: [[gbc_intelligence_engine_project]]で、MacとWindowsの両方が同じDropbox同期フォルダ内に`.venv`を
作成したところ、Unix形式とWindows形式の仮想環境がDropbox同期で衝突し、両方とも破損した
(`main (中村正樹 の競合コピー).py`のようなconflicted copyも多発)。頻繁に書き換わるログファイルも同様に、
同期の負荷や競合の原因になる。

**How to apply**: 複数マシン(会社Mac/個人Mac/個人Windows、[[reference_mac_naming]])で同じDropbox同期
プロジェクトを触る開発タスク全般に適用。venv作成時は`~/gbc_knowledge_venv`のようにホームディレクトリ直下や
`/Users/<user>/venvs/`のような非同期パスに作る。ログも`~/gbc_knowledge_logs/`のようにローカルパスへ出力する。
`main.py`側は`Path(__file__).parent`基準でプロジェクトパスを解決しているため、venv/ログの物理的な場所が
どこであってもプロジェクト本体の実行には支障がない。
