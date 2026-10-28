#!/bin/bash
# 週次メモリレビュー: ~/.claude/projects/*/memory/ を棚卸しし、
# 重複メモリの統合(および統合済み重複ファイルの削除)とパターンの一般化を
# claude -p に行わせる。ユーザー承認済みの制約(2026-08-23):
#   削除してよいのは「重複統合の結果、内容が別ファイルに完全吸収された元ファイル」だけ。
#   老朽化・完了済みを理由にした削除は行わない(review_prompt_template.md側で指示)。
# 個人Mac(ICPTokyo2022)・会社Mac(d14461)それぞれで同じスクリプトを
# launchdから週次(月曜朝8:30、既存のsnsdraft Monday起動に合わせた)起動する想定。マシン固有のパスはハードコードしない。
#
# 既知のリスク(2026-08-15 continuous_data_capture_setup記録済み):
# claude -p はアカウントの週次利用上限に達すると数日単位で無言のまま失敗しうる。
# このスクリプトは失敗を検知してTeams通知するので、同じ「無言の失敗」は起きない設計。

set -u
[ -f "$HOME/.zshenv" ] && source "$HOME/.zshenv"   # TEAMS_WEBHOOK_URLとPATHを取り込む
# Teams通知は共通送信口(../notify/teams_notify.sh、NOTIFY_RULES.md)経由。件名は「[LEVEL] ジョブ名: 要約」
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../notify" && pwd)/teams_notify.sh"
export PATH="$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_TEMPLATE="$SCRIPT_DIR/review_prompt_template.md"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
TODAY="$(date +%Y%m%d)"
RUN_LOG="$LOG_DIR/run_${TODAY}.log"

CLAUDE_BIN="$(ls -d "$HOME"/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | sort -V | tail -1)"
if [ -z "$CLAUDE_BIN" ]; then
    echo "[$TODAY] claude binary not found" >> "$RUN_LOG"
    if command -v notify_teams >/dev/null 2>&1; then
        notify_teams ERROR "週次メモリレビュー" "claudeバイナリが見つからない" "VS Code拡張のclaudeバイナリが見つかりませんでした" "$RUN_LOG"
    fi
    exit 1
fi

SUMMARY_ALL=""
FOUND_ANY=0

for memdir in "$HOME"/.claude/projects/*/memory; do
    [ -f "$memdir/MEMORY.md" ] || continue
    FOUND_ANY=1

    # 複数マシンで同じジョブを入れても二重処理しないためのガード。
    # memory/はDropbox経由で複数Macから共有されうるので、_backups/の最新日付を
    # 「どのマシンが最後にレビューしたか」の共有マーカーとして使う。
    LATEST_BACKUP="$(ls "$memdir/_backups" 2>/dev/null | sort | tail -1)"
    if [ -n "$LATEST_BACKUP" ]; then
        LATEST_EPOCH="$(date -j -f "%Y%m%d" "$LATEST_BACKUP" "+%s" 2>/dev/null || echo 0)"
        NOW_EPOCH="$(date "+%s")"
        DAYS_SINCE=$(( (NOW_EPOCH - LATEST_EPOCH) / 86400 ))
        if [ "$LATEST_EPOCH" -gt 0 ] && [ "$DAYS_SINCE" -lt 5 ]; then
            echo "[$TODAY] skip $memdir: already reviewed ${DAYS_SINCE}d ago (marker $LATEST_BACKUP, possibly by another machine)" >> "$RUN_LOG"
            continue
        fi
    fi

    echo "[$TODAY] reviewing $memdir" >> "$RUN_LOG"

    PROMPT="$(sed "s#{{MEMORY_DIR}}#$memdir#g" "$PROMPT_TEMPLATE")"

    OUTPUT="$("$CLAUDE_BIN" -p "$PROMPT" \
        --allowedTools "Read Edit Write Bash Glob Grep" \
        2>>"$RUN_LOG")"
    RC=$?

    echo "$OUTPUT" >> "$RUN_LOG"

    if echo "$OUTPUT" | grep -qi "weekly limit\|usage limit\|hit your limit"; then
        echo "[$TODAY] quota limit hit for $memdir" >> "$RUN_LOG"
        if command -v notify_teams >/dev/null 2>&1; then
            notify_teams WARN "週次メモリレビュー" "利用上限のため未実行" "利用上限のため $memdir のレビューがスキップされました。来週再試行されます。" "$RUN_LOG"
        fi
        continue
    fi

    if [ $RC -ne 0 ]; then
        echo "[$TODAY] non-zero exit ($RC) for $memdir" >> "$RUN_LOG"
        if command -v notify_teams >/dev/null 2>&1; then
            notify_teams ERROR "週次メモリレビュー" "レビュー中にエラー(exit $RC)" "$memdir のレビュー中にエラー(exit $RC)" "$RUN_LOG"
        fi
        continue
    fi

    SUMMARY_ALL="$SUMMARY_ALL

[$memdir]
$OUTPUT"
done

if [ "$FOUND_ANY" -eq 0 ]; then
    echo "[$TODAY] no memory directories found" >> "$RUN_LOG"
else
    if command -v notify_teams >/dev/null 2>&1; then
        notify_teams OK "週次メモリレビュー" "完了" "${SUMMARY_ALL:0:900}"
    fi
fi

# --- CLAUDE.md週次改善(2026-08-23追加、ユーザー承認済み: 完全自動でCLAUDE.mdへの追記まで実行) ---
# セッションJSONL履歴(~/.claude/projects/*/*.jsonl)から「躓いている箇所」「セッションをまたいだ
# 重複質問」を検出し、まだ反映されていないパターンをCLAUDE.mdへ追記する。マーカーファイルで前回実行
# 以降の新規セッションだけを対象にする(毎回全履歴を再スキャンしない)。CLAUDE.mdはDropbox経由で
# 複数Mac共有のため、上のmemory/レビューと同じ「直近数日以内に他マシンが実行済みならスキップ」の
# ガードをマーカーファイルの日時で行う。
CLAUDE_MD_TEMPLATE="$SCRIPT_DIR/review_claude_md_template.md"
STATE_DIR="$SCRIPT_DIR/state"
BACKUP_DIR="$SCRIPT_DIR/claude_md_backups"
mkdir -p "$STATE_DIR" "$BACKUP_DIR"
MARKER_FILE="$STATE_DIR/claude_md_review_marker.txt"

SKIP_CLAUDE_MD=0
if [ -f "$MARKER_FILE" ]; then
    MARKER_EPOCH="$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$(cat "$MARKER_FILE")" "+%s" 2>/dev/null || echo 0)"
    NOW_EPOCH="$(date "+%s")"
    if [ "$MARKER_EPOCH" -gt 0 ] && [ $(( (NOW_EPOCH - MARKER_EPOCH) / 86400 )) -lt 5 ]; then
        SKIP_CLAUDE_MD=1
        echo "[$TODAY] skip CLAUDE.md review: marker is recent (possibly another machine already ran it this week)" >> "$RUN_LOG"
    fi
fi

if [ "$SKIP_CLAUDE_MD" -eq 0 ] && [ -f "$CLAUDE_MD_TEMPLATE" ]; then
    echo "[$TODAY] running CLAUDE.md weekly review" >> "$RUN_LOG"
    CMD_PROMPT="$(sed -e "s#{{MARKER_FILE}}#$MARKER_FILE#g" -e "s#{{BACKUP_DIR}}#$BACKUP_DIR#g" "$CLAUDE_MD_TEMPLATE")"

    CMD_OUTPUT="$("$CLAUDE_BIN" -p "$CMD_PROMPT" \
        --allowedTools "Read Edit Write Bash Glob Grep" \
        2>>"$RUN_LOG")"
    CMD_RC=$?

    echo "$CMD_OUTPUT" >> "$RUN_LOG"

    if echo "$CMD_OUTPUT" | grep -qi "weekly limit\|usage limit\|hit your limit"; then
        echo "[$TODAY] quota limit hit for CLAUDE.md review" >> "$RUN_LOG"
        if command -v notify_teams >/dev/null 2>&1; then
            notify_teams WARN "週次CLAUDE.mdレビュー" "利用上限のため未実行" "来週再試行されます。" "$RUN_LOG"
        fi
    elif [ $CMD_RC -ne 0 ]; then
        echo "[$TODAY] non-zero exit ($CMD_RC) for CLAUDE.md review" >> "$RUN_LOG"
        if command -v notify_teams >/dev/null 2>&1; then
            notify_teams ERROR "週次CLAUDE.mdレビュー" "エラー(exit $CMD_RC)" "CLAUDE.mdレビューのclaude -pがエラー終了" "$RUN_LOG"
        fi
    else
        if command -v notify_teams >/dev/null 2>&1; then
            notify_teams OK "週次CLAUDE.mdレビュー" "完了" "${CMD_OUTPUT:0:900}"
        fi
    fi
elif [ "$SKIP_CLAUDE_MD" -eq 0 ]; then
    echo "[$TODAY] review_claude_md_template.md not found, skipping CLAUDE.md review" >> "$RUN_LOG"
fi
