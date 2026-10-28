# Agency OS Dify版: 内部ファイル名/外部システムへの誘導バグを修正・公開(20260917)

## 2026-09-17T09:40:00+09:00
Status: done
What: 中村さんがDify版で「海外の自動車業界事例を教えて」をテストし、2点の不具合を報告:
(1) URLが表示されない箇所がある(dentsudotの自動車事例がゼロヒット)、
(2) `topic_expert_index.md`/`tools.md`等の**内部ファイル名を名指しで「直接照会してください」と誘導**、
`dentsudot.com`/`GBCarekoko`/SharePoint「GlobalTeam」といった**外部・内部システムへユーザー自身で
検索するよう誘導**——エンドユーザーはこれらのファイル/システムにアクセス権が無いため不適切。

原因: 既存の「Offloading」ルール(SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.md共通)が
「バンドルファイルを引用として使うな」という狭い範囲にしか触れておらず、ゼロヒット時に
モデルが「親切のつもりで」ファイル名やライブシステムへの誘導文を生成することを防げていなかった。

対応: 3ファイル(SKILL.md/SKILL_Dify.md/SKILL_Dify_for_paste.md)のOffloadingルールを強化し、
(a) いかなる内部バケット/ファイル名もユーザー向け出力に一切出さない、(b) dentsudot.com・
GBCarekoko・SharePoint等のライブシステムへユーザー自身の検索を促さない、(c) ゼロヒット時の
「次の一手」として許されるのは今回の検索で実際に見つかった人物/部署名のみ、というルールを
明記。SKILL_Dify_for_paste.mdはSKILL_Dify.mdから再生成(frontmatter+ローカル限定コメント除去)
して手編集ドリフトが無いことを確認済み([[feedback_agency_os_skillmd_multi_deployment_sync]]の
教訓通り3ファイル並行反映)。

Dify「GBC Agency OS」の実LLMノードSYSTEM promptへ反映・公開まで完了(共有ブラウザport 9227)。
**技術メモ(次回の参考に)**:
1. このDifyワークフローの主LLMノードのSYSTEM prompt欄(リッチテキストcontenteditable)への
   クリップボード貼付(クリック→Meta+A→Meta+V)は、ブラウザウィンドウが**実際にOS上で
   オンスクリーン・フォアグラウンドになっている状態でないと機能しない**(オフスクリーン/
   非フォーカス状態でのCDP合成入力では見た目上エラー無く完了するが実際には反映されない)。
   `document.execCommand('insertText')`による直接DOM操作も同様に無効(Reactが即座に元の
   内部状態へ差し戻す)。オンスクリーンに一時的に戻す→操作→即オフスクリーンに戻す、
   という手順を踏むこと。
2. 「公開する」ボタンをクリックしただけでは公開されない——実際にはドロップダウンメニューが
   開くだけで、その中の**「更新を公開」(⌘⇧P)を追加でクリックして初めて公開される**。
   ヘッダーの「公開済み ◯時間前」表示が更新されたかで成功を確認できる。

Next: (1)実機で再テストし、内部ファイル名・外部システムへの誘導が出なくなったか確認。
(2)dentsudot事例がゼロヒットだった件は、`dentsudot_case_studies_01.md`(790.9k語)/
`dentsudot_thought_leadership_01.md`(887.4k語)という突出して大きい2ファイルが
メインの「knowledge_consumer...」データセット(他17ファイルと共存)に同居しているための
Top-K競合が原因の可能性が高い([[gbc_intelligence_engine_project]]の
`cases_global_01.md`系と同じパターン)。根本修正には`知識検索2/3/4`と同様の専用データセット+
専用ノードへの分離が必要になる可能性があり、これはキャンバス上のノード追加・配線作業
(中村さんが自分で覚えたいと以前表明した領域、[[feedback_reduce_browser_automation_tokens]]の
スクリーンショット多用リスクにも該当)——着手前に中村さんに意向を確認すること。
