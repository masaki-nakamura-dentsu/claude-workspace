
## 2026-10-15 09:50 KGI/KPIレポート定期保存 PDF保存失敗(会社Mac N650893)
- Status: done
- 原因: 09:42起動時にネット未接続(ERR_INTERNET_DISCONNECTED)。10/13 09:40も同じ。スリープ復帰直後にlaunchdが走り、Wi-Fi/VPN接続前にアクセスしていた。09:50時点では接続回復済み。
- 対応: ~/PowerBIExport/export_kgikpi_to_sharepoint.py に wait_for_network()(curlでapp.powerbi.comに届くまで15秒間隔・最大5分待機)を追加し「開始」直後に呼ぶよう修正(バックアップ .bak_202610150955)。`--force`で1回再実行し成功: KGIKPIレポート_20261015.pdf (2,528,888 bytes) をArekokoへ保存、state.json更新。
