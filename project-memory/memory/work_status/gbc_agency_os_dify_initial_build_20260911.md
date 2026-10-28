# GBC Agency OS — Dify版の初回構築(このチャットの本題)

## 2026-09-11T15:15:00+09:00 (approx)
Status: done
What: PoC参加者のメールアドレス名簿作成(Excel)から始まり、6名(石井美香・須田・五十嵐・徳田・石井憲吾・吉田寿哉)がChatGPT版Agency OSを開けない問題を調査。原因は3種類に分解: (1)須田さん・石井憲吾さんは会社Enterpriseだが未ログインでディレクトリ未反映(初回ログインで解決)、(2)石井美香さん・徳田さんはGBC単独契約のChatGPT Business(別テナント)、(3)五十嵐さん・吉田寿哉さんはシニアのためChatGPTライセンス自体が無くCopilotのみ。(2)(3)への対応として社内Dify(console.dj-dify.dentsu.jp、全社員アクセス可・Vertex AI経由でClaude利用可)を発見し、「GBC Agency OS」アプリをゼロから構築(チャットフロー: スタート→知識検索[GBC Knowledge Pack 19ファイル、ハイブリッド検索+Rerank]→LLM[SYSTEM=SKILL.md全文]→回答)。Claude Sonnet 5はこのDifyインスタンスのVertex AIプラグインでtemperatureエラー→ThinkingDeltaストリーミングクラッシュという既知バグで動作せず、Claude Sonnet 4.6に切り替えて動作確認(実案件の正確な引用・CHECKLIST生成を確認)。未公開のまま中村さんに引き継ぎ。詳細は[[gbc_intelligence_engine_project]]の「2026-09-11: 4拠点目「Dify」版を構築」節に記録済み。
Next: なし(このチャットは終了。後続の複数セッションが同日〜9/14にかけてこのDifyアプリを大幅に改良済み — アクセス権/ファイル添付/検索精度/捏造対策等、[[gbc_intelligence_engine_project]]の後続セクション参照)。
