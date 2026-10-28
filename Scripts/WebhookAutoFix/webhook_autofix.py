#!/usr/bin/env python3
"""Webhookエラー通知の自動修復ランナー(2026-10-12、ユーザー依頼・無人修復はユーザー許可済み)。

入力は2系統:
  A. 修復キュー queue/pending/*.json(主系統)
     共通送信口 ../notify/teams_notify.py が [ERROR] 通知の送信時に積む。スクリプト・ログ・ホスト・全文が入っている。
     送信と同時に launchctl kickstart でこのランナーが即起動する。
  B. teams_messages.jsonl の「ワークフロー」チャット(後方互換)
     共通送信口に移行していないスクリプト(会社Mac専用のものやPower Automateのクラウドフロー)向け。
     タグ([ERROR]等)付きの件名はAで扱うので無視する。タグのない旧形式だけを件名のキーワードで判定する。
  ほかに、jsonl自体の更新停止(会社MacのTeamsデーモンが止まると、Bは何も見えなくなる)も検知する。

担当: キューの項目は、エラーが出たホストのランナーが処理する(ローカルのファイルを直せるため)。
      他ホストの項目は、30分たっても誰も処理していなければ引き取る(修正できない場合はrelayで依頼を積む)。
安全装置: 多重起動ロック / 1日あたりの起動上限 / 同じ件名は一定時間再修復しない / タイムアウト。
修復結果は [FIX] / [WAIT] で通知する([ERROR]は送らない=ループ防止)。文言ルール: ../notify/NOTIFY_RULES.md
"""
import fcntl
import glob
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(SCRIPT_DIR), "notify"))
from teams_notify import notify  # noqa: E402

STATE_DIR = os.path.join(SCRIPT_DIR, "state")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
QUEUE = os.path.join(SCRIPT_DIR, "queue")
PENDING, PROCESSING, DONE = (os.path.join(QUEUE, d) for d in ("pending", "processing", "done"))
PROMPT_TEMPLATE = os.path.join(SCRIPT_DIR, "fix_prompt_template.md")
HOST = socket.gethostname().split(".")[0]
STATE_FILE = os.path.join(STATE_DIR, f"state_{HOST}.json")
LOCK_FILE = "/tmp/webhook_autofix.lock"  # ローカルのみ(Dropbox上ではロックが効かない)

JSONL = os.path.expanduser("~/TeamsExport/data/teams_messages.jsonl")
WORKFLOW_CHAT = "ワークフロー"
JOB = "Webhook自動修復"

MAX_RUNS_PER_DAY = 6          # 1日にClaudeを起動する上限(トークン暴走防止)
SAME_TITLE_COOLDOWN_H = 6     # 同じ件名は6時間以内なら再修復しない
FOREIGN_GRACE_MIN = 30        # 他ホストのキュー項目を引き取るまでの猶予
CLAUDE_TIMEOUT_S = 40 * 60
STALE_HOURS = 26              # 1日分の休みでは通知しない

JST = timezone(timedelta(hours=9))
TAG_PAT = re.compile(r"^\[(ERROR|WARN|WAIT|OK|DONE|INFO|FIX)\]")
LEGACY_SELF_PREFIX = "【自動修復】"

# --- 旧形式(タグなし)用の判定 ---
ERROR_PAT = re.compile(
    r"失敗|エラー|error|exception|traceback|停止|異常|見つかりません|タイムアウト|timeout|"
    r"未実行|できませんでした|failed|failure|abort", re.IGNORECASE)
BENIGN_PAT = re.compile(r"失敗\s*[:：]?\s*0(?!\d)|失敗分[をの]?再実行|失敗\s*0\s*件|エラーなし|0\s*errors?", re.IGNORECASE)
SESSION_REPORT_PAT = re.compile(r"対応|調整|調査完了|一時停止|一時中断|停止しました|再実行予定|再実行完了")
PARTIAL_PAT = re.compile(r"(\d+)\s*/\s*(\d+)\s*件?成功")


def now_jst():
    return datetime.now(JST)


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, f"run_{now_jst():%Y%m}_{HOST}.log"), "a", encoding="utf-8") as f:
        f.write(f"[{now_jst():%Y-%m-%d %H:%M:%S}] {msg}\n")


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(st):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE_FILE)


def title_of(text):
    return text.strip().splitlines()[0][:100] if text.strip() else ""


def legacy_is_error(text):
    """タグなし旧形式の判定。件名(1行目)だけを見る(本文まで見ると対話セッションの報告を大量に誤検知する)。"""
    if text.startswith(LEGACY_SELF_PREFIX) or TAG_PAT.match(text):
        return False
    title = title_of(text)
    for a, b in PARTIAL_PAT.findall(text):
        if int(a) < int(b):
            return True
    if SESSION_REPORT_PAT.search(title):
        return False
    return bool(ERROR_PAT.search(BENIGN_PAT.sub("", title)))


def read_new_workflow_msgs(since_iso):
    out = []
    if not os.path.exists(JSONL):
        return out
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            if f'"{WORKFLOW_CHAT}"' not in line:
                continue
            try:
                m = json.loads(line)
            except Exception:
                continue
            if m.get("chat") == WORKFLOW_CHAT and m.get("date", "") > since_iso:
                out.append(m)
    return sorted(out, key=lambda m: m["date"])


def claim_queue_items():
    """自ホストの項目はすぐ、他ホストの項目は猶予後に processing/ へ移して引き取る(rename=取り合い防止)。"""
    os.makedirs(PROCESSING, exist_ok=True)
    claimed = []
    for p in sorted(glob.glob(os.path.join(PENDING, "*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                rec = json.load(f)
        except Exception:
            continue
        age_min = (now_jst().timestamp() - os.path.getmtime(p)) / 60
        if rec.get("host") != HOST and age_min < FOREIGN_GRACE_MIN:
            continue
        dst = os.path.join(PROCESSING, os.path.basename(p))
        try:
            os.rename(p, dst)
        except OSError:
            continue
        rec["_path"] = dst
        claimed.append(rec)
    return claimed


def finish_queue_items(recs, result):
    os.makedirs(DONE, exist_ok=True)
    for r in recs:
        p = r.pop("_path", None)
        if not p or not os.path.exists(p):
            continue
        r["fixed_by"], r["fixed_at"], r["result"] = HOST, now_jst().isoformat(), result
        with open(os.path.join(DONE, os.path.basename(p)), "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        os.remove(p)


def find_claude():
    cands = sorted(glob.glob(os.path.expanduser(
        "~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude")))
    for p in [os.path.expanduser("~/.npm-global/bin/claude")] + cands[::-1]:
        if os.path.exists(p):
            return p
    return None


def run_claude(errors_text):
    claude = find_claude()
    if not claude:
        notify("WAIT", JOB, "claudeが見つからず修復できません", detail=errors_text[:500], script="")
        return None
    with open(PROMPT_TEMPLATE, encoding="utf-8") as f:
        prompt = f.read()
    prompt = (prompt.replace("{{HOST}}", HOST)
                    .replace("{{NOW}}", now_jst().strftime("%Y-%m-%d %H:%M JST"))
                    .replace("{{ERRORS}}", errors_text))
    workdir = next((d for d in glob.glob(os.path.expanduser("~/*Dropbox*/中村正樹")) if os.path.isdir(d)),
                   os.path.expanduser("~"))
    try:
        r = subprocess.run([claude, "-p", prompt, "--allowedTools", "Read Edit Write Bash Glob Grep"],
                           cwd=workdir, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        log("claude timeout")
        notify("WAIT", JOB, f"{CLAUDE_TIMEOUT_S // 60}分で終わらず中断", detail=errors_text[:500], script="")
        return None
    out = (r.stdout or "").strip()
    log(f"claude rc={r.returncode} stderr={r.stderr[-500:]!r}\n{out}")
    if re.search(r"weekly limit|usage limit|hit your limit", out + (r.stderr or ""), re.I):
        notify("WAIT", JOB, "Claudeの利用上限で修復できず", detail=errors_text[:500], script="")
        return None
    return out


def main():
    lock = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("別の実行中のためスキップ")
        return

    st = load_state()
    now = now_jst()
    today = now.strftime("%Y-%m-%d")
    if st.get("runs_date") != today:
        st["runs_date"], st["runs_today"] = today, 0
    if "last_seen" not in st:  # 初回はjsonlの過去分を対象にしない
        st["last_seen"] = datetime.now(timezone.utc).isoformat()
        save_state(st)
        log("初回起動: 監視開始時刻を記録")

    recent = {k: v for k, v in st.get("recent_titles", {}).items()
              if now.timestamp() - v < SAME_TITLE_COOLDOWN_H * 3600}
    tasks, queue_recs, cooled = [], [], []

    # A. 修復キュー
    for rec in claim_queue_items():
        key = f"{rec.get('job')}: {rec.get('summary')}"
        if key in recent:
            cooled.append(key)
            finish_queue_items([rec], f"クールダウン中のため未処理({SAME_TITLE_COOLDOWN_H}時間以内に同じ件を修復済み)")
            continue
        recent[key] = now.timestamp()
        queue_recs.append(rec)
        tasks.append("\n".join([
            f"[修復キュー {rec.get('time')}] {rec.get('title')}",
            f"発生ホスト: {rec.get('host')}" + ("(このマシン)" if rec.get("host") == HOST else "(別マシン)"),
            f"スクリプト: {rec.get('script') or '不明'}",
            f"ログ: {rec.get('log') or '不明'}",
            f"詳細:\n{rec.get('detail', '')[:4000]}",
        ]))

    # B. 旧形式のWebhook通知
    for m in read_new_workflow_msgs(st["last_seen"]):
        st["last_seen"] = m["date"]
        if not legacy_is_error(m.get("text", "")):
            continue
        key = title_of(m["text"])
        if key in recent:
            cooled.append(key)
            continue
        recent[key] = now.timestamp()
        tasks.append(f"[旧形式のWebhook通知 {m['date']} mid={m.get('mid')}](発生ホスト・スクリプトは本文から推定)\n{m['text'][:3000]}")

    # jsonlの更新停止は修復対象にしない(会社Macを起動していない休暇日にも起きるため。2026-10-12ユーザー指摘)。
    # 停止1回につき1度だけ、平日日中に[INFO]で知らせる。デーモン自体の失敗は会社Macから[ERROR]で届く。
    if os.path.exists(JSONL):
        mtime = os.path.getmtime(JSONL)
        age_h = (now.timestamp() - mtime) / 3600
        if (now.weekday() < 5 and 9 <= now.hour < 20 and age_h > STALE_HOURS
                and st.get("stale_alerted_mtime") != mtime):
            st["stale_alerted_mtime"] = mtime
            notify("INFO", JOB, f"Teams取込が{age_h:.0f}時間止まっています", script="",
                   detail=f"teams_messages.jsonlの最終更新は{datetime.fromtimestamp(mtime, JST):%m/%d %H:%M}。"
                          "会社Macを起動していないだけなら対応は不要です。起動中なのに止まっている場合はTeamsデーモンを確認してください。"
                          "この間、旧形式の通知は自動修復で拾えません。")

    st["recent_titles"] = recent
    if cooled:
        log(f"クールダウン中のためスキップ: {cooled}")
    if not tasks:
        save_state(st)
        return

    if st["runs_today"] >= MAX_RUNS_PER_DAY:
        log(f"1日の上限に達したため修復しない: {len(tasks)}件")
        finish_queue_items(queue_recs, "1日の上限に達したため未処理")
        if st.get("cap_alerted") != today:
            st["cap_alerted"] = today
            notify("WAIT", JOB, f"本日の上限{MAX_RUNS_PER_DAY}回に到達", script="",
                   detail=f"新しいエラー{len(tasks)}件は手動で確認してください。" + " | ".join(t.splitlines()[0] for t in tasks)[:800])
        save_state(st)
        return

    st["runs_today"] += 1
    save_state(st)  # Claude実行前に保存(長時間の実行中に同じ件を再検知しないため)

    log(f"修復開始: {len(tasks)}件")
    out = run_claude("\n\n---\n\n".join(tasks))
    if out is None:
        finish_queue_items(queue_recs, "修復未実行(上限・タイムアウト等)")
        return
    msum = re.search(r"SUMMARY:\s*(.+)", out, re.S)
    summary = (msum.group(1) if msum else out).strip()[-1500:]
    finish_queue_items(queue_recs, summary)
    mj = re.search(r"判定=([^/]+)", summary)
    verdict = mj.group(1).strip() if mj else "結果"
    mt = re.search(r"対象=([^/]+)", summary)
    target = mt.group(1).strip() if mt else title_of(tasks[0])[:40]
    level = "WAIT" if re.search(r"要ユーザー対応|修正失敗", verdict) else "FIX"
    notify(level, JOB, f"{target[:30]} → {verdict}", detail=summary, script="")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ランナー自体が例外: {e!r}")
        notify("WAIT", JOB, "ランナーが例外で停止", detail=repr(e), script="")
        sys.exit(1)
