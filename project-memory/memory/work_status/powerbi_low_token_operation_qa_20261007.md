# PowerBI(ブラウザ版)を低トークンで操作できるかのQ&A

## 2026-10-07
Status: done
- 質問「PowerBIをトークン消費を抑えて操作できるか(ブラウザ版)」に回答。
- 回答要旨: 画面操作(スクショ駆動)は高コストなので避け、Botブラウザからトークン取得→REST API(Fabric getDefinition/updateDefinition、executeQueries、refresh)でテキストベース操作する方式なら低コスト。ビジュアル配置などUI作業は本人+テキスト手順。根拠メモリ: feedback_token_conscious_powerbi / gbc_kpikgi_sharepoint_export / pbix_pbir_layout_parsing_technique。
