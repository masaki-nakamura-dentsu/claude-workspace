# Agency OS 月次内容更新チェック自動化
Status: done
Date: 2026-10-19
monthly_freshness_check.py + launchd com.nakamura.agencyosmonthlycheck を登録。初回 2026-11-02 9:30。
追記: アレココ・CCSの月次作り直し+Skill/Dify自動反映 tools/monthly_update.sh 作成。個人Macでの試走・launchd登録は relay task-019(pending)。
追記2: 会社MacのOneDrive「GBC_アレココ - 添付ファイル」にDocApp添付426件すべてあり(サイズ一致、24件は未DL)。会社MacからWindows Ollamaには届かない(Tailscaleなし)。実行マシンをユーザーに確認中。
追記3: 更新量見込み(月約11件)、会社MacのOllama削除、mac_direct(send/worker/install)作成、確認ジョブに個人Macへの自動依頼を追加。個人Macでinstall.sh実行待ち。
追記4: mac_direct 動作確認OK。task-019試走を個人Macへ送信、結果待ち。
追記5: 試走はclaude -p終了で停止。--detach追加、install_monthly_update.sh作成。個人Macでユーザー実行待ち。
追記6: 個人Macでlaunchd登録完了・試走起動。結果待ち。
追記7: 試走成功・変更なし。task-019 done。Status: done
追記8: 代行依頼をkickstart方式に修正・送信テストOK。
追記9: IM CMOレポート(Dentsu Creative 2026 CMO Report Making It Real、山田さん10/14投稿)はdentsu.dot取得(9/16)後の公開でAgency OS未収録→差分取得中。駐在員週次ジョブ停止を修正し10月分取込。
追記10: dentsu.dot差分取得(TL+13・事例+4、CMO 2026含む)→output/dentsudot_pack_20261019→差し替え用_20261019_dentsudot。Skill push は auto mode(Unrequested Commit)で拒否→ユーザー許可待ち。Skill v158をskill_backup_20261019に保存済み。
追記11: dentsu.dot反映済み。会社Mac月次スクリプト作成・試走中。漏れ点検結果をメモリに記録。
追記12: 会社Mac月次登録・10月分反映完了。Love the Work再ログイン待ち。Status: done
追記13: SF/FAQ/担当者/LoveTheWork を会社Mac月次に追加、試走中
追記14: 10ファイル反映完了。Status: done
- 2026-10-19 エキスパート認定方法の相談開始(現状整理と論点提示)
- 10/19 認定者=部長に決定。候補はSalesforce案件内容から出したい(中村さん)
