#!/usr/bin/env python3
"""F群 海外事業調査: 名前ルールで「なし」→ 残りはBing検索+Ollama(qwen)で判定。逐次保存・再開可。
使い方: python run.py 入力.csv 出力.csv [--limit N] [--workers 3]
実行は ~/venvs/overseas/bin/python (ddgs入り)。Ollamaは OLLAMA_HOST(既定 desktop-ryzen5950:11434)。"""
import csv, json, os, re, sys, time, argparse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from ddgs import DDGS

OLLAMA = "http://%s/api/chat" % os.environ.get("OLLAMA_HOST", "192.168.0.11:11434")
MODEL = "qwen3.8:27b"
NONE_PAT = re.compile(r"^(.{0,6})?(.*(県|市|町|村|区役所)$|公益(財団|社団|信託)|一般(財団|社団)|財団法人|社団法人|宗教法人|学校法人|医療法人|社会福祉法人|協同組合|組合|協会$|連合会|.*(ファミリーマート|セブン.?イレブン|ローソン)$|.*(自動車|ダイハツ|スバル|トヨタ|日産|ホンダ|マツダ|三菱自動車)(販売|販社)?（株）$|.*(銀行|信用金庫|信用組合)$|電通.*)")
NONE_PAT2 = re.compile(r"(公益(財団|社団|信託)|一般(財団|社団)|財団法人|社団法人|宗教法人|学校法人|医療法人|社会福祉法人|組合|協会|連合会|(県|市|町|村)$|信用金庫|信用組合|(ダイハツ|スバル|トヨタ|日産|ホンダ|マツダ).*販売|^(株)?(沖縄|南九州|北海道|東北|関西|九州|中部|東海)?(ファミリーマート|ローソン|セブン.?イレブン)|ファミリーマート$)")
PROMPT = """あなたは企業調査の担当です。次の日本企業について、検索結果の抜粋だけを根拠に「海外拠点・海外売上・海外進出(輸出・海外店舗・海外子会社含む)」の有無を判定してください。
企業名: {name}(業種: {ind})
検索結果:
{snips}

ルール: 抜粋に根拠がなければ推測せず「不明」。外資系の日本法人で日本法人自体に海外拠点の記載がなければ「不明」。同名の別会社の情報は使わない。
JSONのみで答える: {{"海外事業":"あり|なし|不明","根拠":"40字以内","url":"根拠にした検索結果のURL(なければ空)","確度":"高|中|低"}}"""

def clean(n): return re.sub(r"[（(]株[）)]|[（(]有[）)]|株式会社|\s", "", n)

def search(name):
    out = []
    for q in (f"{clean(name)} 海外 事業 子会社 拠点", f"{clean(name)} 海外展開 輸出 海外売上"):
        for attempt in range(3):
            try:
                out += DDGS().text(q, region="jp-jp", max_results=5, backend="bing"); break
            except Exception as e:
                if "No results" in str(e): break
                time.sleep(3 * (attempt + 1))
        time.sleep(1.0)
    seen, res = set(), []
    for x in out:
        if x["href"] in seen: continue
        seen.add(x["href"]); res.append(x)
    return res[:8]

def ask(prompt):
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False,
                       "think": False, "format": "json", "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    return json.loads(json.loads(urllib.request.urlopen(req, timeout=300).read())["message"]["content"])

def judge(r):
    name = r["企業名"]
    if NONE_PAT2.search(clean(name)) or clean(name).endswith(("県", "市")) or "電通" in name:
        return ["なし", "名前から海外事業は考えにくい(自治体・法人格・地域販社等。Web未検索)", "", "中"]
    res = search(name)
    if not res: return ["不明", "検索結果なし", "", "低"]
    snips = "\n".join(f"[{i+1}] {x['title']} {x['href']}\n{x['body'][:200]}" for i, x in enumerate(res))
    try:
        j = ask(PROMPT.format(name=name, ind=r["業種"], snips=snips))
        v = j.get("海外事業", "不明"); v = v if v in ("あり", "なし", "不明") else "不明"
        c = j.get("確度", "低"); c = "低" if v == "不明" else (c if c in ("高", "中", "低") else "低")
        return [v, str(j.get("根拠", ""))[:80], j.get("url", ""), c]
    except Exception as e:
        return ["不明", f"判定エラー:{str(e)[:40]}", "", "低"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--limit", type=int); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    rows = list(csv.DictReader(open(a.src, encoding="utf-8-sig")))
    done = {}
    if os.path.exists(a.dst):
        for x in csv.reader(open(a.dst, encoding="utf-8-sig")): done[x[0]] = x
    todo = [r for r in rows if r["取引先企業コード"] not in done][: a.limit]
    new = not os.path.exists(a.dst)
    f = open(a.dst, "a", encoding="utf-8-sig", newline=""); w = csv.writer(f)
    if new: w.writerow(["取引先企業コード", "企業名", "海外事業", "根拠の一言", "根拠URL", "確度"])
    t0 = time.time(); n = 0
    with ThreadPoolExecutor(a.workers) as ex:
        for r, v in zip(todo, ex.map(judge, todo)):
            w.writerow([r["取引先企業コード"], r["企業名"], *v]); f.flush(); n += 1
            if n % 20 == 0: print(f"{n}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
    print("done", n)
