#!/bin/bash
# 日経電子版(個人プラン)のCAS立替精算リマインダー。launchd com.nakamura.nikkeiexpense から毎月20日9:30に起動。
# 課金は毎月1日(初回のみ2026/11/21に日割1,430円)。コーポレートカード明細のCAS読み込みに時差があるため20日に通知する。初回は2026/12/20。
source "/Users/d14461/dentsuDropbox Dropbox/中村正樹/.claude-sync/Scripts/notify/teams_notify.sh"
ym=$(date +%Y%m)
[ "$ym" -lt "202612" ] && exit 0
m=$(date +%-m)
if [ "$ym" = "202612" ]; then target="2026年11月分(日割1,430円)と12月分(4,277円)"; else target="${m}月分(4,277円)"; fi
notify_teams INFO "日経電子版 経費精算" "日経電子版 ${target}をCASで精算してください" \
 "①CAS https://cas-expense.dentsu.co.jp/cas/login?mode=top でコーポレートカード明細(日本経済新聞社)が読み込まれているか確認(未反映なら翌月まとめて可) ②一般経費>立替払い>直接精算 で起票: JU=10633725 / 勘定科目=5306250 調査費－データ購入費 / 使用理由・内容=「GLOMG41 日経電子版 個人プラン月額利用料(${target})。競合・博報堂DYグループの海外戦略・組織・人事情報の定点観測(HDY定点観測)のため。特殊IT環境タスクフォース審議承認No IS2610052」 ③領収書が必要なら日経IDラウンジ https://id.nikkei.com/lounge/ の支払い履歴からPDFを添付 ④担当GMに承認依頼"
