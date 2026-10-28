---
name: github_history_management
description: GitHubでの履歴管理の方針（対象範囲・ファイル別名保存との併用・秘匿情報の扱い）と現在の設定状況
metadata:
  type: project
---

2026-10-28、中村さん決定: **Claude環境+業務スクリプトは会社Macからcommit/push**（会社がGitHub利用を推奨・Claude契約も会社契約・GitHubアカウントは会社アカウント）。会社Macはgitのみ運用（gh/Homebrewなし）。**private固定**。納品物の `_YYYYMMDD` 別名保存は維持し、Gitはテキスト/コードの差分履歴を担当。個人Mac側は個人用の別リポジトリ（個人作業のみ・未作成、個人GitHubアカウントが必要）。

- 会社Mac用タスク: `claude_relay/company_mac_inbox.md` の task-GH-001。雛形は `claude_relay/github_setup/`（gitignore.company / pre-commit.company）。
- 許可リスト方式の `.gitignore`。認証情報（Webhook URL・トークン・パスワード）と個人情報（個人番号・パスポート等）は絶対にアップロードしない。pre-commitで検知して止める。社内情報そのものは会社GitHubなので可。
- `.git` はDropbox同期破損防止のため `com.dropbox.ignored` を付与（各Macが自分の.gitを持つ）。
- 個人Macで作った仮リポジトリは破棄済み（退避: `~/claude-env-personal-draft.git`）。個人側の対象候補は20_写真映像創作・Program等。30_個人・家族の個人情報は対象外。

**Why:** 認証情報・個人情報の流出防止、Dropbox同期との衝突回避、会社契約の範囲での運用。
**How to apply:** 新ディレクトリをGit対象にするときは.gitignoreに許可を追記しpre-commitを通す。push前に必ず再スキャン。関連 [[teams_webhook]] [[mac_handoff_relay]]

## 個人リポジトリ（2026-10-28 作成）
- GitHub個人アカウント `maxakisan`、private `personal-workspace`、ルート=Dropbox `中村正樹/`（.gitは同期除外、個人Macのみ）。74ファイル。
- 許可リスト: Program/、memory `20_写真・映像・創作`（GlobalQ系5件は会社業務のため除外）、`Scripts/photo_club_pdf`・`adobe_cli`。コミット用メールはGitHub noreply。
- hookは「実データ形式」（Webhook/トークン/12桁番号/@社内ドメイン/社内SharePoint）で検知。キーワード（個人番号等）は説明文で誤検知するため外した。
- 7ファイルは社名表記を一般化して個人側に追加（rakumaro: 電通→所属会社）。`dentsu_pptx_template`等のリンク名・フォルダ名はそのまま。
- GlobalQ系5件(20_内)は会社側に移すか未決。会社の`.gitignore.company`は20_を除外中。
- 会社側でも `Scripts/photo_club_pdf` と `adobe_cli` は個人側の管理に寄せるため、会社の.gitignoreから除外する想定（task-GH-001に追記）。

## 会社リポジトリ（2026-10-28 会社Mac N650893 で開始・push済み）
- URL: https://github.com/masaki-nakamura-dentsu/claude-workspace （private、会社アカウント、ルート=`.claude-sync`）。初回commit 5a5af94、787ファイル。認証はPAT(Fine-grained, Contents RW)をosxkeychainに保存（期限約90日、切れたら再作成）。
- **pushは社内プロキシ必須**: 直接だと `SSL_ERROR_SYSCALL` で切れる（読み取りは通る）。repo-localに `http.proxy=http://proxy1.dentsu.co.jp:8080` を設定済み。
- 自動モードの分類器が `git push` を「データ外部送信」として拒否する（許可ルール追加後も）。push/commitは本人がターミナルで実行するのが確実。
- 追加した許可: 20_内の `globalq_*` 5件。除外: `Scripts/photo_club_pdf` `adobe_cli`、work_statusの photo_club/adobe_cli ログ、`claude_relay/README.md`(Webhook URL直書き)、`claude_relay/github_setup/`。
- 運用: 「コミットして」→ `git add -A && git commit && git push`（pre-commitが認証情報を検知して止める）。
- 運用方針（2026-10-28 本人指示）: 自動化はせず、commit/pushが必要な場面でその都度本人に確認する。pushは分類器に止められるので、確認のうえ本人用のターミナルコマンドを案内する。権限設定の変更は本人が「よく分からない」ため勧めない。
