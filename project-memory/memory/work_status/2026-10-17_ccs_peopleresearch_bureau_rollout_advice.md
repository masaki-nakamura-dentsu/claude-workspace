# CCS/People Research を局員(Claude Code非利用者)に展開する方法の相談

## 2026-10-17
Status: done
What: 「基本ファイル+ChatGPTにPythonを書かせて局員がローカル実行」案を評価し、代替案を回答。要点: 取得(認証が必要)と分析を分離。CCSは固定の取得ツール(候補: ブラウザ内で動くブックマークレット/固定Pythonスクリプト)でCSV化→分析はChatGPTのコード実行(局員PCにPython不要)。People ResearchはGUIツールなので自動化せず、ChatGPTで設問設計・結果分析を補助するテンプレ化を推奨。詳細は [[ccs_peopleresearch_bureau_rollout]]。
Next: ユーザーの方針決定待ち。試作する場合はCCSセッションのある会社Mac(d14461, 9226)で検証が必要。

## 2026-10-17 11:20
Status: done
What: (1) task-015完了(failover_check.jsに停止フラグ、テスト済み、inboxにResult記入)。(2) CCS設問カタログを会社Mac向けtask-016として登録。(3) アレココ目録の試作を作成 → [[arekoko_catalog_project]]。
Next: 目録のAgency OS反映可否と、正式タイトル・ページ目次の追加を中村さんが判断。task-016は会社Macで実行待ち。

## 2026-10-17 12:00
Status: in_progress
What: CCSを個人Mac(9231)で取得しカタログ化完了(output/ccs_catalog_20261017)、task-016をdone。アレココ: リスト・添付426件をDL、ページ抽出済み、Windows Ollamaで要約を実行中(バックグラウンド、見張りあり)。SKILL_20261017系3ファイル作成、changelog追記。
Next: 要約完了→generate_arekoko_catalog.pyで output/arekoko_catalog_20261017_01 を生成・確認→中村さんOK後にChatGPT Skill/Difyへ反映。

## 2026-10-17 12:10
Status: in_progress
What: CCSの提案を必須化したSKILL_*_20261017_01(3種)を作成、changelog追記。アレココ要約はWindowsで継続中。
Next: 要約完了→目録生成→中村さんOK後に反映(反映するのは_01版)。

## 2026-10-17 12:20
Status: in_progress
What: ユーザー依頼で要約スクリプトにTeams途中経過通知(30分ごと)を追加し再起動(169/426件済みから再開)。見張りはPID方式で再設定(前の見張りはpkillの巻き添えで停止)。
Next: 完了DONE通知→目録生成。

## 2026-10-17 12:15
Status: in_progress
What: Webhook件名が長いと切れる指摘→共通送信口teams_notify.pyに28字制限・ジョブ名短縮・本文への全文退避を追加、NOTIFY_RULES.md更新。要約スクリプトの文言を短くして再起動(206/426件済み、PID23547、見張り再設定)。テスト通知送信。
Next: 要約完了→目録生成。

## 2026-10-17 12:20
Status: in_progress
What: Webhook件名28字制限のテスト通知を中村さんが確認(成功)。
Next: アレココ要約完了→目録生成。

## 2026-10-17 13:12
Status: in_progress
What: 要約が331/426件で33分停止→見張りが検知。timeout 300秒に短縮して再開(PID26303)、Teams WARN送信、見張り再設定。
Next: 完了→目録生成。

## 2026-10-17 13:30
Status: in_progress
What: 要約426件完了、目録 output/arekoko_catalog_20261017_01 生成(306登録)。
Next: 中村さんOK後、ChatGPT Skill(個人Macは9229)とDifyに目録+CCS+SKILL_*_20261017_01を反映。

## 2026-10-17 14:00
Status: in_progress
What: 見出し先頭欠けを登録タイトル照合で補正。要約の照合 verify_summaries.py を作成し全件実行中(Windows 27B)。WindowsのOllamaは直列と判明→windows_inbox task-017(OLLAMA_NUM_PARALLEL)登録。
Next: 照合完了→目録再生成(arekoko_catalog_20261017_02)→サンプル目視→報告。

## 2026-10-17 14:05
Status: in_progress
What: 中村さんがWindowsにtask-017(OLLAMA_NUM_PARALLEL)を指示済み。照合スクリプトにOllama無応答時の待機・再試行(結果を書かない)を追加して再起動(PID29178、163件済)。見張り: 照合の停止15分/完了/task-017のdone検知。個人MacのローカルLLMは使わない(FB記録)。
Next: task-017完了→並列ベンチ→並列化して照合を加速。

## 2026-10-17 14:30
Status: in_progress
What: task-017完了(Windowsは既に並列可・設定変更なし)。verify_summaries.pyに--workersを追加し3並列で再開(PID29870、237件済)。長い依頼では1.1倍しか速くならないと計測、メモリ記録。
Next: 照合完了→目録再生成→サンプル目視→報告。

## 2026-10-17 15:00
Status: in_progress
What: 要約の照合完了、日本語化11件・数字換算・見出し補正を直し、目録 arekoko_catalog_20261017_02 を生成。抜き取り確認OK。
Next: 中村さんOK後に反映。

## 2026-10-17 15:20
Status: done
What: ChatGPT Skill(v147)とDify(公開20261017目録CCS追加)にアレココ目録・CCS設問一覧・新指示文を反映、照合一致。Difyは目録/CCSを別ナレッジ・別検索ノードに。テストで見つかった捏造・ページ混同を修正してから公開。
Next: 中村さんがChatGPT版でテスト。

## 2026-10-17 15:30
Status: done
What: 個人Windowsのシャットダウン依頼→遠隔の経路なし(22/5985閉、3389/445のみ)。手動かWindows側Claudeでの実行を案内。
Next: 必要ならWindowsにOpenSSH等を入れて遠隔停止できるようにする(要許可)。

## 2026-10-17 15:45
Status: in_progress
What: 個人Macから個人Windowsを止める構成: Mac側の鍵・ssh config・win_power.sh作成、Windows側OpenSSH設定を windows_inbox task-018 に登録。
Next: task-018完了後に ssh win-home で接続確認→win_power.sh shutdown のテスト。

## 2026-10-17 15:55
Status: in_progress
What: 中村さん依頼で個人Windowsを win_power.sh wake で起動(約105秒でping応答)。
Next: Windows側でtask-018実行→ssh確認。
