# Mac→Windows IME単語登録(ユーザー辞書)移行

## 2026-08-07T00:00:00+09:00
Status: done
What: d14461MacがGoogle日本語入力使用中と判明。辞書ツールでエクスポートしたUTF-8(BOM無し)テキストがWindows MS-IMEの取り込みで全行エラー(品詞の指定を確認してください)。原因はMS-IME側がBOM無しUTF-8をShift-JISとして誤読すること。UTF-16LE+BOMへ再エンコードし、品詞ラベル「姓」「名」を「人名(姓)」「人名(名)」に変換したファイル(`~/Downloads/ユーザー辞書_Windows用_20260807.txt`)を作成、ユーザーがWindowsで再インポートし成功を確認。詳細は project memory [[mac_windows_ime_dictionary_migration]]。
Next: —
