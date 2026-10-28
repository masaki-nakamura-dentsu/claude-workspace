---
name: dentsu-claude-code-it-application-process
description: dentsu社内でClaude Code等のAI製品を利用する際の特殊IT申請フロー(Teamsボット経由)、実際の承認済み記録
metadata: 
  node_type: memory
  type: reference
  originSessionId: aa7bfb31-79b2-4fd6-935f-acfb149ae31a
  modified: 2026-08-25T08:21:23.003Z
---

社内でClaude Code(や他のAI製品)を利用するための申請は、Teams上の「特殊IT申請エージェント（β版）」（= 特殊IT申請ボット、Requestbot Nonstandardit）経由で行う。

**エージェントURL**: https://m365.cloud.microsoft/chat/?titleId=T_8f59e958-fe7b-0e68-7904-b583ed23bf73&source=agentCenterDialog （M365 Copilot Chat上で動作。Teamsアプリとしても利用可）

**手順**:
1. 上記URL(またはTeamsアプリ)で「特殊IT申請エージェント」を開く
2. 申請 ＞ AI製品 ＞ AI製品利用申請フォーム
3. 社員番号入力 → Office365/Excel等への接続許可を求められたら「許可」を押す（ここでConnectorAuthorizationErrorが出ることがあった。対処法: リセット/`/debug clearstate`ボタン→再実行、それでもダメならブラウザキャッシュクリア＋エージェント再インストール。問い合わせ先: non_standard_it_bot_hypercare@group.dentsu.co.jp）
4. 審議希望のツール名（例: Claude Code (Pro)）を記載して申請
5. 承認は「特殊ＩＴ 申請ボット Requestbot Nonstandardit <non_standard_it_request_bot@dc1.dentsu.co.jp>」からメールで通知される

**承認済み実績**: 中村正樹氏はClaude Code (Pro)を2026-06-10に申請・承認済み（申請No. d14461-20260610091702、拠点:東京、利用者:d14461）。

**承認内容の制約（Claude Codeの例、他AI製品も同様の枠組み）**:
- 入力可: 公開情報／社外秘情報／極秘情報(a〜c以外)
- 入力禁止: 極秘・取扱厳重注意情報／極秘情報(a〜c含む)
- dJ AIガバナンスコミッティコメント: 商用利用可、学習オフ設定が必要、SOC2未取得のため情報区分に制約あり、Claude提供以外のMCPを使う場合は別途セキュリティ確認が必要
- 利用規約: https://www.anthropic.com/legal/commercial-terms
- 生成物は権利侵害に要注意

**端末へのアプリインストールは別申請が必要（ただしVS Code経由なら基本不要）**: スタンドアロンのインストーラー版を使う場合は 申請 ＞ 非AI製品 ＞ 特殊IT導入・審議依頼フォーム（拠点／申し込み種別=特殊IT環境（ソフト）／承認済みサービス名・申請番号を記載）が必要。関連スレッド「ClaudeCodeアプリの利用について【タスクフォース審議申し込み・問い合わせ_B243】」によると、この届出書の「導入が必要となる理由」欄には (1)サービス概要・業務用途・取り扱いデータ例 (2)特殊IT申請エージェントで発行された承認番号 (3)ブラウザ利用では業務遂行が難しい理由（詳細に） の3点を明記する必要がある。
**重要**: 中村氏自身は2026-06-10にこのアプリインストール審議を一度申請しかけたが、「アプリを使用しなくてもVS Codeなどの使用で目的は果たせる」と判明したため申請をキャンセルした（電通総研テクノロジー佐藤氏とのRE:B243スレッド）。会社PCにはVS Codeが標準支給されており、その統合ターミナル上でClaude Code CLIを使う形なら、この重い方のタスクフォース審議は不要というのが実際の結論。同僚に案内する際もまずこの軽い方（VS Code内利用）を勧めてよい。

**Windows機での技術的セットアップ（未検証・Mac実績からの類推）**: 会社ネットワークは外部への直接HTTPS接続を許可しないため、`npm install -g @anthropic-ai/claude-code`のようなnpm経由のインストールは社内プロキシ設定が無いとタイムアウトする（会社Mac(d14461)の`~/.npmrc`に実際に`proxy=http://proxy1.dentsu.co.jp:8080`/`https-proxy=http://proxy1.dentsu.co.jp:8080`の設定が入っており、[[feedback_d14461_pip_needs_corporate_proxy]]の通りpipでも同じ現象が起きた実績あり)。Windows側でも`npm config set proxy http://proxy1.dentsu.co.jp:8080`と`npm config set https-proxy http://proxy1.dentsu.co.jp:8080`（または`%USERPROFILE%\.npmrc`に直接記載）が必要になる可能性が高い。ただしWindows側での実際の設定記録は未確認、同僚が実際に試して結果が分かればここを更新すること。

**参考リンク**:
- AI製品申請管理リスト: https://esq365.sharepoint.com/sites/IT165/Lists/AI/AllItems.aspx?viewid=d1cb2932-eb47-4b0e-ac3d-c182997eaf9f
- 特殊IT申請エージェント利用ガイド(PDF): ISnaviサイト（/sites/ISnavi/Shared Documents/特殊IT/特殊IT申請エージェント_利用ガイド.pdf）
- 利用条件の問い合わせ: AIサポートセンター（dJ AIガバナンスコミッティ事務局窓口、Formsリンクあり）

Why: 社内で新規AI製品を使う全メンバーが通る共通フロー。[[ai_katsuyo_pj_overseas_funding]]や[[ai_katsuyo_pj_ambassador]]などAI活用PJ関連の話が出た際にも、個別ツール導入の実務フローとして参照できる。
