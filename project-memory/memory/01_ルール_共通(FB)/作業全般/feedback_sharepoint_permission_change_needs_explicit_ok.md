---
name: feedback_sharepoint_permission_change_needs_explicit_ok
description: アレココ等の共有SharePointの変更(ページ作成・編集・権限変更)は、ユーザーが具体的な作業を明示的に許可するまで実行しない。auto modeでもブロックされる
metadata:
  type: feedback
---
2026-10-08、「Bで進めて」という方針の了承だけでテスト用ページの作成に進んだところ、auto modeの分類器に「共有リソースの変更」としてブロックされた。その後、ユーザーが「PDFフォルダの権限を修正して」と具体的に指示してからは問題なく実行できた。
**Why:** 共有サイトはGBC全員が使うので、方針への同意は個々の変更操作の許可とは別に扱われる。
**How to apply:** 共有SharePointへの書き込みは、「何をどう変えるか」を示し、ユーザーがその操作を明示的に許可してから行う。事前のテストページ作成も変更操作に含まれる。変更前に現状の権限を読み取り、変更後に再読み取りで検証する。関連: [[gbc_kpikgi_sharepoint_export]]
