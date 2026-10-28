# bash/zsh用: source して notify_teams LEVEL "ジョブ名" "要約" ["詳細"] ["ログパス"]
# 文言ルールは NOTIFY_RULES.md。中身は teams_notify.py を呼ぶだけ。
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    _TEAMS_NOTIFY_PY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/teams_notify.py"
else
    _TEAMS_NOTIFY_PY="$(cd "$(dirname "${(%):-%x}")" && pwd)/teams_notify.py"
fi
notify_teams() {
    local level="$1" job="$2" summary="$3" detail="${4:-}" log="${5:-}"
    local caller="${BASH_SOURCE[1]:-$0}"
    python3 "$_TEAMS_NOTIFY_PY" "$level" "$job" "$summary" --detail "$detail" --log "$log" --script "$caller" >/dev/null 2>&1 || true
}
