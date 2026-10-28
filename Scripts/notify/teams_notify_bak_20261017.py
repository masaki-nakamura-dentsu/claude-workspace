#!/usr/bin/env python3
"""Teams Webhook通知の共通送信口(2026-10-12)。文言ルールは同じフォルダの NOTIFY_RULES.md。

送信時点で次の3つを行う:
  1. 件名を「[LEVEL] ジョブ名: 要約」の形に揃え、本文は1行に潰して送る(改行があるとPower Automateが無言で失敗する)
  2. LEVEL=ERROR のときは、修復に必要な情報(スクリプト・ログ・ホスト・全文)を
     WebhookAutoFix/queue/pending/ に JSON で積む(Teams取込デーモンが止まっていても修復側に届く)
  3. このマシンの自動修復ジョブ(launchd com.nakamura.webhookautofix)を即時起動する(未登録なら何もしない)

Pythonから:  from teams_notify import notify; notify("ERROR", "Salesforce QBR DL", "成功0/失敗18", detail=..., log=...)
CLIから:     python3 teams_notify.py ERROR "ジョブ名" "要約" [--detail ...] [--log ...] [--script ...]
bashから:    source teams_notify.sh; notify_teams ERROR "ジョブ名" "要約" "詳細" "ログパス"
"""
import argparse
import inspect
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

LEVELS = ("ERROR", "WARN", "WAIT", "OK", "DONE", "INFO", "FIX")
JST = timezone(timedelta(hours=9))
HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_DIR = os.path.join(os.path.dirname(HERE), "WebhookAutoFix", "queue", "pending")
AUTOFIX_LABEL = "com.nakamura.webhookautofix"

def _webhook_url():
    """環境変数 TEAMS_WEBHOOK_URL を優先。launchdから直接起動されて未設定のときは各マシンの ~/.zshenv から読む。
    URL(署名付き)はDropbox同期されるこのファイルには書かない。"""
    url = os.environ.get("TEAMS_WEBHOOK_URL")
    if url:
        return url
    try:
        with open(os.path.expanduser("~/.zshenv"), encoding="utf-8") as f:
            for line in f:
                m = re.match(r'\s*export\s+TEAMS_WEBHOOK_URL=["\']?([^"\'\s]+)', line)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return ""


def host():
    return socket.gethostname().split(".")[0]


def _flat(s):
    return re.sub(r"\s*\n\s*", " / ", str(s or "")).strip(" /")


def _caller_script():
    for fr in inspect.stack()[2:]:
        f = os.path.abspath(fr.filename)
        if f != os.path.abspath(__file__) and not f.startswith("<"):
            return f
    return ""


def _post(title, message):
    url = _webhook_url()
    if not url:
        print("teams_notify: TEAMS_WEBHOOK_URL が見つからないため送信できません", file=sys.stderr)
        return False
    body = json.dumps({"title": title, "message": message}, ensure_ascii=False)
    err = None
    # curlを先に使う: 会社Mac(d14461)はZscaler/BIG-IPのTLS傍受でurllibの証明書検証が失敗する(2026-09-11確認)。
    for i in range(2):
        try:
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST", url,
                                "-H", "Content-Type: application/json; charset=utf-8", "--data-binary", body],
                               capture_output=True, text=True, timeout=40)
            if r.stdout.strip().startswith("2"):
                return True
            err = f"curl http={r.stdout.strip()} {r.stderr.strip()[:200]}"
        except Exception as e:
            err = e
        try:
            req = urllib.request.Request(url, data=body.encode("utf-8"),
                                         headers={"Content-Type": "application/json; charset=utf-8"})
            urllib.request.urlopen(req, timeout=30)
            return True
        except Exception as e:
            err = f"{err} / urllib {e}"
        time.sleep(3)
    print(f"teams_notify: Webhook送信失敗: {err}", file=sys.stderr)
    return False


def _enqueue(rec):
    try:
        os.makedirs(QUEUE_DIR, exist_ok=True)
        slug = re.sub(r"[^\w\-]+", "_", rec["job"])[:40]
        name = f"{datetime.now(JST):%Y%m%d_%H%M%S}_{rec['host']}_{slug}.json"
        tmp = os.path.join(QUEUE_DIR, "." + name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        os.replace(tmp, os.path.join(QUEUE_DIR, name))
    except Exception as e:
        print(f"teams_notify: キュー書込失敗: {e}", file=sys.stderr)
    try:  # 自動修復ジョブを即時起動(未登録マシンでは失敗するだけ)
        subprocess.run(["launchctl", "kickstart", f"gui/{os.getuid()}/{AUTOFIX_LABEL}"],
                       capture_output=True, timeout=10)
    except Exception:
        pass


def notify(level, job, summary, detail="", log="", script=None, fixable=True):
    """level: ERROR/WARN/WAIT/OK/DONE/INFO/FIX (NOTIFY_RULES.md参照)。通知失敗で呼び出し元を止めない。"""
    try:
        level = level.upper()
        if level not in LEVELS:
            level = "INFO"
        script = _caller_script() if script is None else script
        h = host()
        now = datetime.now(JST)
        title = f"[{level}] {_flat(job)}: {_flat(summary)}"[:150]
        parts = [_flat(detail)[:2500]]
        if log:
            parts.append(f"ログ: {log}")
        if script and level in ("ERROR", "WARN"):
            parts.append(f"スクリプト: {script}")
        parts.append(f"ホスト: {h} / {now:%m-%d %H:%M}")
        message = " / ".join(p for p in parts if p)
        ok = _post(title, message)
        if level == "ERROR" and fixable:
            _enqueue({"level": level, "job": job, "summary": summary, "detail": str(detail or ""),
                      "log": log, "script": script, "host": h, "time": now.isoformat(),
                      "webhook_sent": ok, "title": title})
        return ok
    except Exception as e:
        print(f"teams_notify: 例外 {e!r}", file=sys.stderr)
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("level")
    ap.add_argument("job")
    ap.add_argument("summary")
    ap.add_argument("--detail", default="")
    ap.add_argument("--log", default="")
    ap.add_argument("--script", default="")
    ap.add_argument("--no-fix", action="store_true", help="ERRORでも修復キューに積まない")
    a = ap.parse_args()
    sys.exit(0 if notify(a.level, a.job, a.summary, a.detail, a.log, a.script, not a.no_fix) else 1)
