---
name: redespresso-contact-form-mail-fix
description: "redespresso.co.jp（クライアント: 株式会社ケンコロジー/Kencology）のEverest Formsお問い合わせメールが届かなかった問題。原因はSPF/DMARC不整合、WP Mail SMTP+GoDaddy認証送信で解決（2026-09-11）"
metadata: 
  node_type: memory
  type: project
  originSessionId: 369d1a2e-6e6d-4237-a1f1-7450cb8c8c51
  modified: 2026-09-11T08:16:37.994Z
---

redespresso.co.jp（管理者: 中村さん、クライアント: 株式会社ケンコロジー/Kencology Corporation）で、Everest Forms経由のお問い合わせ・事業者向け登録フォームのメールが届かない問題が発生し、2026-09-11に解決した。

## 原因
- Webホスティング: GMOお名前.comレンタルサーバー（www59.onamae.ne.jp）
- メール(MX): GoDaddy（smtp.secureserver.net / mailstore1.secureserver.net、Workspace Email）
- SPF: `v=spf1 include:secureserver.net -all`（GoDaddy以外はハード失格）
- DMARC: `p=reject`（SPF/DKIM不整合は拒否）
- WordPress(Everest Forms)がPHP mail()でお名前.comのサーバーから`info@redespresso.co.jp`をFromに送信していたため、SPF失格→DMARC拒否でメールが一切届いていなかった（Entriesにはフォーム送信自体は1236件正常に保存されていた＝フロントは無関係と切り分け済み）。

## 解決策
WP Mail SMTPプラグイン（by WPForms）を導入し、GoDaddyのSMTP(`smtpout.secureserver.net`, Port 465/SSL, 認証あり)に`info@redespresso.co.jp`の実アカウントで認証接続して送信するよう変更。Fromアドレスも同じ`info@redespresso.co.jp`に統一。DNS変更は不要だった。

**Why**: DNSゾーン(SPF/DMARC)はGoDaddyのネームサーバー(domaincontrol.com)で管理されており、お名前.com側の管理画面からは編集不可能だったため、DNSを変えずに送信経路をGoDaddy側の正規ルートに合わせる方式を選んだ。

**How to apply**: 同種の「Webホスティングとメールホスティングが別会社」なWordPressサイトで問い合わせフォームが届かない相談を受けたら、まず`dig MX/TXT(SPF)/TXT(_dmarc)`とWebサーバーの逆引きDNSを比較し、送信元(Web側)がSPFの許可リストに入っているかを確認する。入っていなければ同じ手法（正規のメールアカウントでSMTP認証送信に切り替え）が通用する可能性が高い。

## 診断で使った技術
- `dig MX/TXT/_dmarc.TXT`でSPF/DMARC確認、`dig -x`でWebサーバーIPの逆引きから提供事業者を特定（GMO vs GoDaddyの分離を発見）
- Everest FormsのEntries一覧でフォーム送信自体が成立しているかを切り分け（メール到達だけの問題と確認）
- MXレコードのパターン(`secureserver.net`単体 vs `mail.protection.outlook.com`)からGoDaddy Workspace EmailかM365かを、クライアントに聞かずに判定できた

Status: 解決済み（2026-09-11、ユーザー確認済み）
