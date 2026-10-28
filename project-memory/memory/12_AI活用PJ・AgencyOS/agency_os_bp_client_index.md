---
name: agency-os-bp-client-index
description: Agency OSにGEM由来の「BP局×クライアント索引」を組み込み、会社Mac月次更新に追加した(2026-10-21)
metadata:
  type: project
---
クライアント名→担当BP局、BP局→担当クライアントを引けるようにした。元は [[gem-bp-client-list-extraction]] の有効のみ8,904組(28局・7,290社)。
- ファイル: bp_client_index_by_client.md / by_bureau.md(GBC-Knowledge/output/bp_pack_20261021)。SkillはSKILL.mdに要件J(局は事実の提示のみ、主担当・推奨をしない、クライアント向け資料に出さない)を追加。ChatGPT Skill v170、Dify公開「20261021BP局追加」。
- Dify: 既存ナレッジに混ぜると検索で拾えなかったため、専用ナレッジ+専用検索ノードにした。コード実行ノードの出力は30要素上限なのでBP結果は1要素にまとめる。
- 月次: monthly_update_company.sh(会社Mac、第1営業日14:00〜)がGEM取得→生成→差分反映。初回の自動実行は2026-11-02以降で未試走(要確認)。
- 注意: 登録上の担当で主担当・取引量ではない。局の増減はgem_bureaus.jsonを直す。
**How to apply:** 月次通知にGEM関連のWARNがあれば会社MacのGEMログイン(9226)を確認。
