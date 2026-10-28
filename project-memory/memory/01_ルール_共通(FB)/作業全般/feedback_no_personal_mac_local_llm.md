---
name: feedback_no_personal_mac_local_llm
description: ローカルLLMの処理は自宅Windows(192.168.0.11)のOllamaで行い、個人Macのローカルモデルは使わない(10/17指示)
metadata:
  type: feedback
---
2026-10-17、アレココ要約の並列化を検討した際、中村さんから「個人MacのローカルLLMは使わない」と指示。

**Why:** 個人Mac(M4 Pro/24GB)で27Bを動かすと17GBを使い、Mac上の作業が重くなる。8Bでは品質が落ちる。
**How to apply:** Ollamaに投げる処理は自宅Windowsのサーバー([[ollama_qwen_remote_backend]])に限定する。速くしたいときはWindows側の同時処理数(OLLAMA_NUM_PARALLEL)を上げる方向で考え、個人Macにモデルを入れたり処理を分けたりしない。
