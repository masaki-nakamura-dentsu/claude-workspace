---
name: dentsu-google-workspace-gcp-restriction
description: 会社Googleアカウント(masaki.nakamura@dentsu.co.jp)ではGoogle Cloud ConsoleでのAPI有効化・プロジェクト管理ができない(組織ポリシーで権限なし)、個人Gmailアカウントを使う必要がある
metadata: 
  node_type: memory
  type: reference
  originSessionId: d0b9fb08-071a-421a-ba91-df0a166e3de9
  modified: 2026-09-30T08:17:22.563Z
---

2026-09-30、YouTube Data API v3のAPIキー発行作業で、会社Googleアカウント(dentsu.co.jp)でGoogle
Cloud Consoleにログインし、YouTube Data API v3を有効化しようとしたところ
「このプロダクトの有効化ステータスを確認するために必要な権限がありません。」というエラーで失敗。
dentsuのGoogle Workspace組織ポリシーにより、社員アカウントでのCloud Consoleプロジェクト作成・
API管理操作が制限されていると判断(会社Mac自体の管理者権限制限[[company_mac_no_admin_no_homebrew]]
とは別種の、Googleアカウント側の組織ポリシー制約)。ユーザーは個人Gmailアカウントに切り替えて
作業を継続する方針に。

**How to apply**: 今後Google Cloud Console(console.cloud.google.com)でAPIキー発行・プロジェクト
作成・API有効化が必要なタスクでは、最初から個人Gmailアカウントでの作業を前提に案内する
(会社アカウントでまず試して失敗させる、という手順を毎回繰り返さない)。Google AI Studio
([[gemini_nanobanana_setup]]参照)がどちらのアカウントで動いていたかは未確認だが、Cloud Console
本体(プロジェクト管理・API有効化)は会社アカウントでは不可と判明済み。
