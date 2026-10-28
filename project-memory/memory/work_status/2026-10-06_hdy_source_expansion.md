# 2026-10-06 HDY定点観測 情報源拡充
Status: done
- extras.py 追加(works/ir/jobs_web/articles)、config/collectors/README更新、手順書 PowerBI構築手順_20261006_06.md(G章)
- Ad Age: ユーザーが共有ブラウザでログイン→プロフィール/Excel取得(米国売上 2025 $497M)
- 残: ユーザーがPowerBIでG章のクエリ8本追加+ページ作成。digestへの重要記事掲載は未対応
- 追記: インド/ベトナム求人の追加調査。LinkedIn guest API(jobs-guest/.../search?location=Worldwide&f_C=<会社ID>)はログイン不要で会社別全件取得可(AGL 696020=7件、Hakuhodo Group Vietnam 31144780=10件、Kingdom Digital 3488089)。会社ページから従業員数も取れる(Hakuhodo VN 2,400)。TopCV/CareerVietは実求人なし、Indeed 403。実装はユーザー判断待ち(元方針はLinkedIn不要)
- 追記2: ユーザー承認で1〜4全実装(LinkedIn会社別求人+登録社員数、iimjobs/Naukri拡張、博報堂VNチーム紹介の増減)。手順書_07 G-10
- 2026-10-07: 追加拡充(entity_sites/entity_watch/yuho/社名ベース求人検索/LinkedIn自動発見拡大)。手順書 PowerBI構築手順_20261007.md G-11
- 2026-10-07 09:09 LinkedIn自動発見完了: 23社(新規7: Auburn, Audience IQ Asia, BCM, Hakuhodo Digital Indonesia, Hakuhodo First, Hakuhodo Malaysia, Southpaw)。掲載中求人215件。Status: done
