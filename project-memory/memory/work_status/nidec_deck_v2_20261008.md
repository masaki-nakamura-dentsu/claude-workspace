# Nidec 共同編集デッキ 第2版(HINO風に全面作り直し)
- Date: 2026-10-08 / d14461 / Status: done(16:31 クラウド反映確認。中身は第2版と完全一致)
- Target: OneDrive Teamsチャットファイル/Nidec_社内打ち合わせ_戦略たたき台_20261006.pptx (表示82枚+旧版非表示)
- Backups/scripts: Work/Client/Nidec/作業履歴フォルダ/
- 2026-10-08 16:2x: クラウド版は12,410,878B(14:23の第1版)のまま。ローカルは第2版12,623,155B。SyncEngineログで ConflictResolver の GetConflictPathForLocalFile/RecordFail が数秒ごとに反復(.png)。候補: OneDrive「Global Q_サイトのリソース ファイル/SitePages/Global_info_tools/」の 1244239160-/4012902649-サムネ_世界の広告費成長率予測.png(10/7作成の同名サムネ2件)。SharePoint REST直接アップロードは auto mode classifier(Modify Shared Resources)で拒否 → ユーザー判断待ち。
- 確認方法: SharePoint REST GetFolderByServerRelativeUrl('/personal/masaki_nakamura_dentsu_co_jp/Documents/Microsoft Teams チャット ファイル')/Files で Length/TimeLastModified を見る(esq365-my.sharepoint.com、共有Botブラウザ9226でページ内fetch)。
- 16:31 OneDrive再起動後に同期でクラウド反映(12,623,155B)。途中、須田さんが開いていてSharePointロック(SPFileLockException 423)→直接アップロードは失敗、同期経由で反映。教訓: 共同編集ファイルが同期されないときは、まず LockedByUser をREST(GET .../LockedByUser)で確認する。
