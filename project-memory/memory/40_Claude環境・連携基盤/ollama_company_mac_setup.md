---
name: ollama-company-mac-setup
description: 会社Mac(d14461)にOllama(qwen3:8b)をセットアップ済み(2026-08-26)。管理者権限不要、~/Applications配置。GBC Intelligence Engineのローカルナレッジ生成パイプライン等で再利用可能
metadata: 
  node_type: memory
  type: project
  originSessionId: 1749c365-0287-43f7-83ff-d010d1abf3b0
  modified: 2026-08-26T08:06:47.524Z
---

会社Mac(d14461)には元々Ollamaが入っておらず(個人Macや自宅Windows RTX3090限定だった、
[[ollama_qwen_remote_backend]]参照)、GBC Intelligence Engine
([[gbc_intelligence_engine_project]])のRegression Test作業で2026-08-26に
新規セットアップした。**管理者権限が無くても導入できた**([[company_mac_no_admin_no_homebrew]]
と同様の制約下)。

## セットアップ方法(admin不要)
```bash
export https_proxy=http://proxy1.dentsu.co.jp:8080
export http_proxy=http://proxy1.dentsu.co.jp:8080
curl -L -o Ollama-darwin.zip https://ollama.com/download/Ollama-darwin.zip
unzip Ollama-darwin.zip
mkdir -p ~/Applications
mv Ollama.app ~/Applications/
```
CLIバイナリは `~/Applications/Ollama.app/Contents/Resources/ollama`。
`/Applications`(管理者権限が要る場合がある)ではなく`~/Applications`に置くのがポイント。

## 起動時の罠(重要)
**`ollama serve`デーモン自体がプロキシ環境変数を継承していないと、`ollama pull`が
`dial tcp ...: i/o timeout`で失敗する**。`ollama pull`コマンド実行時にプロキシを
exportするだけでは効かない(実際の通信はバックグラウンドのdaemonプロセスが行うため)。
必ずdaemon起動前に環境変数をexportしてから`serve`すること:
```bash
export https_proxy=http://proxy1.dentsu.co.jp:8080
export http_proxy=http://proxy1.dentsu.co.jp:8080
export HTTPS_PROXY=http://proxy1.dentsu.co.jp:8080
export HTTP_PROXY=http://proxy1.dentsu.co.jp:8080
export NO_PROXY=localhost,127.0.0.1
nohup ~/Applications/Ollama.app/Contents/Resources/ollama serve > ~/ollama_setup/server.log 2>&1 &
disown
```
起動後、`~/Applications/Ollama.app/Contents/Resources/ollama pull qwen3:8b`
(5.2GB、Q4_K_M量子化)。API疎通は`curl http://127.0.0.1:11434/api/tags`。

## スペック
Apple M4、Metal GPU、VRAM 10.7GB利用可能。短いプロンプトの応答は3〜4秒程度、
数千字のコンテキスト+JSON出力を伴う実務プロンプトでは1件あたり30〜40秒程度
(Stage A+B 2回呼び出しの実測、[[gbc_intelligence_engine_project]]の
Regression Test作業より)。

## 用途
GBC Intelligence Engineの知見カード生成パイプライン(Stage A/B、
`regression_pipeline_v2.py`)で使用。他のローカルLLM処理タスクでも
このセットアップを再利用できる。既存の`src/ollama.py`
(`chat()`/`chat_json()`)がそのまま使える設計になっている。

**2026-10-19 アンインストール済み**(中村さん指示): ~/Applications/Ollama.app と ~/.ollama(21GB)を削除。会社MacではOllamaを使わない。LLM処理は自宅Windows(個人Mac経由 win_power.sh)。
