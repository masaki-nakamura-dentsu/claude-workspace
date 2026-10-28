## [2026-10-25] マニュライフ生命 モニター広告/山手線ADトレインSim撮影 LR取込・★1セレクト
Status: done
- /Volumes/Extreme SSD/20261025マニュライフ生命広告 の ARW158枚(A5_03098-03255)を lrb import、★1を19枚。
- モニター(場所クラスタ別7枚): 03121/03133/03144/03154/03170/03185/03195
- 山手線Sim(カット別12枚): 03208中吊り/03117車内/03212ドア上/03219ホームドア/03102ドアなし/03227車体/03230ホーム/03233乗降/03237・03251・03246・03104 五反田高架
- 丸山さんTeams(10/16,23): 11/2(月)4:45大崎集合、内回り大崎5:09始発、ホームドア有無で見え方が違う。

## [2026-10-25] 最終セレクト33枚 → PureRAW → DNG → LR反映（途中）
Status: in_progress
- ユーザー最終セレクト=★1の33枚。LR「プリセットで書き出し→DxO PureRAW 4 ですぐに処理」(System Events経由メニュークリック、画面キャプチャ不使用)でSSDフォルダに *-001..033.dng 出力済み。LRに取込済み。
- 元ARWの現像設定(露出/トーン/WB/クロップ等、LensProfile・Upright除く)をDNGへdevelop-setで反映済み(map: scratchpad外 /private/tmp/claude-501/map.json)。
- Upright: PerspectiveUpright=1 をdevelop-setしても変換行列が計算されない→lrbに `lrb upright` (Commands.lua C.uprightAuto) を追加、LR再起動待ち。LR quitが「ユーザによってキャンセル」で止まり再起動できていない。
- 残: LR再起動→`lrb upright`でDNG33枚Auto Upright(元でガイド済みの5枚は要検討)→モニター7種DNGの緑をManulife Green(#00A758想定)に合わせWB調整→DNGに★1。

## [2026-10-26] LR再起動済み、Upright/WB再開
Status: in_progress
- コンテキスト約129k。/clear後は「マニュライフOOH写真の続き。work_status/2026-10-25_manulife_ooh_select を読んで」で再開。

## [2026-10-26] 完了
Status: done
- DNG33枚: Upright Auto(ガイド済み5枚=03102/03121/03123/03126/03139は元のガイド設定をコピー)、03212のみ補正が過大で Upright オフに戻した。
- モニター16枚(03121〜03199)はTemperatureのみ調整し、広告緑の色相を #00A758(151.6°)に合わせた(誤差±0.4°)。Tintはユーザー設定を維持。
- DNG33枚に★1。lrbに `lrb upright` 追加(Upright変換行列キーはUprightTransform_<mode>。Lua側の判定キーは_5固定でok=falseと出るが計算自体は成功)。
