# Agency OS SkillのPPTX出力が電通フォーマットにならない問題の修正

## 2026-09-08T16:10:00+09:00
Status: done
What: 中村さんから「Agency OS SkillのPPTX出力が電通フォーマットで出ない、PoC前に直したい」と相談。
原因調査の結果、Skillの`references/deck-production.md`のテンプレート追従ルールが「ユーザーが
テンプレートを供給したら従う」という条件付きで、電通GTMテンプレート自体がSkillに同梱されていな
かったと判明。対応として(1)`dentsu_gtm_template_clean.pptx`(サンプルスライド75枚削除、レイアウト
70種のみ、28MB→9.4MB)を新規作成、(2)`deck-production.md`を「常に同梱テンプレートを使う」必須
ルールに書き換え(レイアウト名一覧・配色・Verdanaフォント・python-pptx既知の罠を追記)、(3)`SKILL.md`
10章を同様に修正、の3ファイルを`GPT作業/`フォルダにローカル保存した。中村さんがChatGPT Skill
エディタで手動アップロード・保存し、動作確認したところ「上手くいきました」と報告あり、電通フォーマット
での出力に成功したことを確認。
Next: — (完了)
