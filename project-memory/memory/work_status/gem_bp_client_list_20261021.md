# GEM 28局クライアントリスト取得 (2026-10-21)
Status: done
- GEMから28局分(26,427行/15,194社)をCSV化。詳細は [[gem-bp-client-list-extraction]]
- 次: 海外CI・CAS売総との突合、有効のみ絞り込み
- 追記: 有効のみ絞り込み後、海外CI×GBC実績で4分類(A/B/C/D+E/F)に判定。Excel出力済。次: 目視確認、Agency OS組み込み(別チャット)
- 訂正: 海外CIはJCIでなく RF & P の 2025 ACTUAL Category Management を使用(詳細 [[gem-bp-client-list-extraction]])。修正版 `GBC_クライアント有用性判定_20261021_01.xlsx` 出力済(親グループ128: A13/B48/C3/D64)。旧版(JCI)は破棄扱い。
- 検討中: 各社の海外事業調査を会社Mac/個人Windowsどちらでやるか(回答済み、推奨は下記)。
Status: in-progress
- 2026-10-21 会社Macで日系B群20社の海外事業をWebSearchで調査 → `work_analysis/B群日系_海外事業メモ_20261021.xlsx`。残: 海外企業の日本法人(B群の海外勢)、海外CIなし約6,700社(量が多いため個人Windowsに回す案、取引先名の持ち出し可否を要確認)。
- 2026-10-21 取引先名の個人Windows持ち出し許可を記録、F群6,700社の海外事業調査をWindows inboxに起票(pending)。Status: done
- 2026-10-21 B群の海外勢(日本法人)の動きをWebSearchで調査→work_analysis/B群海外勢_日本法人メモ_20261021.xlsx。Status: done
- 2026-10-22 F群の海外事業調査結果を局別に整理→work_analysis/GBC_海外展開済み未開拓候補_局別_20261022.xlsx。Status: done
- 2026-10-22 F群海外事業調査完了(6,700社)→局別候補Excel `GBC_海外展開済み未開拓候補_局別_20261022_01.xlsx`(シート『局別優先順位』、スコア=BP扱い40+海外マーケ35+新事業25、売上高は未使用の代用推定)。次: 各BP局3社ずつ抜粋してPPTXに入れる(Excelは別途提出)。対象PPTXは未確定(局の戦略資料/BPLISTスライドか要確認)。Status: in-progress
- 2026-10-22 局別3社(28局×3=84社)を `GBC_CAS売総・貢献売総を伸ばす戦略について_20261022.pptx` のp.22-26(BPLIST直後、5枚)に挿入。生成は同フォルダ build7_bp3.py。除外: 使用不可表記(ユーザベース)・製作委員会・国際機関(ERIA)。マスタExcelを GBC-Knowledge/gem_source/bp_priority/BP局別_海外展開候補_マスタ.xlsx に置き、更新はこれを直してbuild7を再実行。Status: done
