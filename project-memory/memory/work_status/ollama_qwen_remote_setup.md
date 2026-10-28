# Ollama/Qwenリモートバックエンド セットアップ

## 2026-08-23T05:49:08Z
Status: done
What: ユーザー依頼「192.168.0.11:11434のOllamaサーバー(モデルqwen3.8:27b)をリモートバックエンドとして使うよう設定」に対応。~/.zshenvにOLLAMA_HOST=192.168.0.11:11434を追加(このMac=個人Mac/ICPTokyo2022限定、.zshenvはDropbox非同期)。ollama CLI未導入だったためbrew installで導入。リモートサーバーへの疎通確認、当初モデル未pullだったためユーザー確認の上qwen3.8:27b(17GB)をpull・成功確認済み。続けてユーザーから「トークン消費を抑えられそうな時は処理前にアドバイスして」という標準ルールの依頼があり、グローバルCLAUDE.md(実体: .claude-sync/CLAUDE.md)に2026-08-23付の標準ルールとして追記、詳細をmemory/40_Claude環境・連携基盤/ollama_qwen_remote_backend.mdに記録、MEMORY.mdにも索引追加。まだ具体的なオフロード先スクリプトは未作成(ユーザーから対象タスクの指定なし)。
Next: ユーザーが具体的なオフロード対象タスク(例:Teams週次要約など)を指定してきたら、そのタスク用のOllama連携スクリプトを作成し、memory/40_Claude環境・連携基盤/ollama_qwen_remote_backend.mdに追記する。
