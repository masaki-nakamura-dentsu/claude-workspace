---
name: media-planner-ccs-planner
description: Media Planner(旧CCS Planner)の使い方・操作自動化の勝ち筋と詰まり所。ターゲットはAudience BuilderのPanel IDs CSV必須
metadata:
  type: reference
---
- 名称は2026年から「Media Planner」(旧CCS Planner)。URL https://ccs-planner.dentsuconnect.com/home?clientCode=A_DJPN&tenantId=pbpnlqrzm 。**使える**(2026-10-23、会社Mac 9226 botブラウザで操作成功。[[dentsuconnect_ccs_migration]]の「使えない」は誤り/解消)。
- マニュアル: Downloads/「1014 Media Planner 戦略企画・拠点P支援部.pptm」。局員向け手順メモ=Media_Planner_使い方メモ_局員向け_20261023.md、要約は Dropbox `Work/GBC_戦略企画部/情報データ／ツールバンク/Media Planner/Media_Planner_まとめ_20261023.md`。
- ターゲットはAudience BuilderでAudience作成→Export Panel Ids(CSV)→ブリーフでアップロード。無いとAll adultsのみ。
- 自動操作のコツ(Playwright connectOverCDP localhost:9226、新規タブで操作→page.close): react-selectは `.dentsu-chip-input-light-mode__placeholder` クリック→type→Enter。Surveyが1つ目、Clientが2つ目(`#react-select-3-input`)。チャネル選択チェックボックスは `evaluate(e=>e.click())`(同ページに11個、index0は全選択)。Manualプランの予算セルは `[role=gridcell]` 2列目をdblclick→Meta+a→数値→Enter。**保存はfloppy-diskアイコンのボタン**(PUT /project)。保存しないと閉じたとき消える。
- Automaticは選択状態が永続化して挙動がぶれる/Nextが押せず未完。Manualが確実。
- 未解決: Audience Builder「Build an audience」(audience-explorer.dentsuconnect.com/planning)でMarket=Japan+Define manuallyを選んでもContinueがdisabledのまま(react-aria)。次は実マウス操作かUIの別経路(Import CCS data / AI Audience)を試す。
- 2026-10-23作成プロジェクト: 「ゲームヘビーユーザー若年層_TV+オンライン_2億円_20261023」(Internal Pitch, Japan 2025, Plan 1 Manual、All adults基準の暫定)。
