---
name: feedback-check-dropbox-sync-before-claiming-isolated
description: "別Macとメモリ/設定が共有されているかどうかを述べる前に、必ず[[dropbox_config_sync]]と実際のシンボリックリンクの状態を確認する。未確認のまま「共有されない」と言い切らない。"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cb9cc477-4604-45e6-83cf-8866a41b6ad8
  modified: 2026-08-22T22:00:21.991Z
---

ユーザーが複数のMac(maxakisan / d14461)を使っており、CLAUDE.md・settings.json・プロジェクトごとの`memory/`は[[dropbox_config_sync]]の仕組みで`.claude-sync`フォルダ経由・シンボリックリンクで既にMac間共有されるよう設定済み(2026-07-08セットアップ、2026-07-13に両Mac確認済み)。

**Why:** [[powerautomate_attendance_summary_project]]の作業終了時、「続きは別のMacで行う」と言われて、確認せずに「`~/.claude/projects/`はMacごとに独立しているので自動的には引き継がれない」と断言してしまった。実際には`ls -la`で確認したところ、CLAUDE.md・settings.json・memory/・MEMORY.mdの全てが既に`.claude-sync`へのシンボリックリンクとして正しく設定されており、直前に保存したメモリファイルも即座にDropbox同期フォルダ内に存在していた。ユーザーから「もともと共有するようお願いしていたはず」と指摘されて発覚した、完全に避けられたはずの誤り。

**How to apply:** 「別のMacでは見えない」「共有されない」のような、Mac間の設定・メモリ共有状態について何か主張する前に、必ず以下を先に行う。
1. [[dropbox_config_sync]]を読んで、そもそも共有設定が存在するかを確認する
2. `ls -la ~/.claude/CLAUDE.md ~/.claude/settings.json ~/.claude/projects/<this-project-key>/memory` 等で、実際にシンボリックリンクになっているか・どこを指しているかを確認する
未確認のまま「ローカルにしか無い」「同期されない」と断定しない。

**再発(2026-08-23)**: [[memory_weekly_review_automation]]の設計中、確認せずに「メモリファイルはMac個別でDropbox同期外」とCLAUDE.md・project memoryの両方に書いてしまい、会社Macへの不要な二重展開手順まで書いた。ユーザーに「会社Macで何と指示すればよいか」と聞かれて初めて`ls -la`で実際のシンボリックリンクを確認し、誤りが判明(実際は`memory/`ごとDropbox共有済みで、会社Macは何もしなくても同じファイルを見ている)。**この記憶ファイル自体を読んでいながら手順1・2を怠った**のが根本原因 — 「Mac間共有について何か書く前に確認する」というルールを"知っている"だけでは実行時に自動適用されない。次回以降、複数Mac・Windowsが絡む話題(同期・展開・インストール手順)を書く/話す直前に、このメモリの存在を思い出すトリガーとして「複数マシン」というキーワード自体を意識する。

より広いパターンは[[feedback_verify_against_ground_truth]]に統合済み(2026-08-24) — 「断定する前に一次情報を確認する」という一般則の一事例。
