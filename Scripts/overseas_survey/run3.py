#!/usr/bin/env python3
"""F群 海外事業調査 v3: 公式サイト直接取得方式。
検索は公式URL特定のみ → トップ/会社概要/沿革を取得 → 正規表現で海外シグナル抽出 → 候補のみqwenで確認。
判定: あり(根拠URL付き) / シグナルなし(サイト確認済) / 不明(公式サイト特定不可・取得不可)。逐次保存・再開可。
使い方: python run3.py 入力.csv 出力.csv [--limit N] [--workers 4] [--sample N]
実行は ~/venvs/overseas/bin/python (ddgs, lxml)。Ollamaは OLLAMA_HOST(既定 192.168.0.11:11434)。"""
import csv, json, os, re, sys, time, argparse, random, ssl, urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor
from ddgs import DDGS
from lxml import html as LH

OLLAMA = "http://%s/api/chat" % os.environ.get("OLLAMA_HOST", "192.168.0.11:11434")
MODEL = "qwen3.8:27b"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Accept-Language": "ja,en;q=0.8"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
# 公式サイトではない集約・ニュース・求人系ドメイン
BAD = re.compile(r"(wikipedia|baseconnect|tdb|teikoku|nikkei|indeed|prtimes|mynavi|rikunabi|en-japan|townwork|green-japan|wantedly|"
                 r"facebook|twitter|x\.com|instagram|youtube|linkedin|note\.com|ameblo|yahoo|google|bing|navitime|itp\.ne|ekiten|"
                 r"mapion|jp-corp|nta\.go|houjin|ullet|minkabu|kabutan|buffett|job|career|recruit|rekaizen|alarmbox|"
                 r"fuma-net|salesnow|musubu|cnavi|catr|mikata|iタウン|hatena|goo\.ne|biz-journal|kaisha|shachihata|shigoto)", re.I)
PAGE_LINK = re.compile(r"会社概要|企業情報|会社情報|会社案内|沿革|企業概要|About|Company|Profile|グローバル|海外|事業所|拠点|ネットワーク")
LANG_LINK = re.compile(r"(^|/)(en|english|zh|cn|zh-cn|zh-tw|ko|th|vn|id)(/|$|\.)|English|中文|简体|繁體|한국어|ภาษาไทย", re.I)
STRONG = re.compile(r"(海外(拠点|子会社|法人|支店|支社|営業所|工場|店舗|事業|展開|進出|取引|売上|市場|輸出)|現地法人|駐在員事務所|輸出|グローバル(展開|拠点|ネットワーク)|"
                    r"(アメリカ|米国|中国|上海|北京|深圳|香港|台湾|韓国|ソウル|タイ|バンコク|ベトナム|ハノイ|ホーチミン|インドネシア|ジャカルタ|シンガポール|マレーシア|インド|フィリピン|ドイツ|フランス|英国|イギリス|ロンドン|ブラジル|メキシコ)\s*(支店|支社|現地|拠点|工場|営業所|法人|オフィス|事務所)|"
                    r"[A-Z][A-Za-z.& ]{2,40}\s(Co\.,? ?Ltd|Inc\.|Pte\.? ?Ltd|GmbH|Limited|LLC|Corp)|Overseas|Global (Network|Offices?)|Subsidiar(y|ies))")
PROMPT = """企業「{name}」(業種:{ind})の公式サイトから抜き出した文です。この会社自身が現在「海外拠点・海外子会社・海外売上/輸出・海外店舗」を持つ/行っているかを判定してください。
ルール: 文に根拠がなければ「不明」。過去の閉鎖や計画のみ、取引先・親会社・仕入先の情報、サイトの閲覧言語切替だけは根拠にしない。
抜粋(URL付き):
{ev}
JSONのみ: {{"海外事業":"あり|不明","根拠":"40字以内","url":"根拠のURL"}}"""

def clean(n): return re.sub(r"[（(]株[）)]|[（(]有[）)]|[（(]合[）)]|株式会社|有限会社|合同会社|\s", "", n)

def get(url, timeout=12):
    try: return _get(url, UA, timeout)
    except urllib.error.HTTPError as e:
        if e.code in (403, 406, 429): return _get(url, {"User-Agent": "curl/8.4.0", "Accept": "text/html"}, timeout)
        raise

def _get(url, hdr, timeout):
    req = urllib.request.Request(url, headers=hdr)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        ct = r.headers.get("Content-Type", "")
        if "html" not in ct and ct: return None, url
        raw = r.read(1_500_000)
        m = re.search(rb"charset=([\w-]+)", raw[:3000]) or re.search(r"charset=([\w-]+)", ct)
        enc = (m.group(1).decode() if isinstance(m.group(1), bytes) else m.group(1)) if m else "utf-8"
        try: txt = raw.decode(enc, "replace")
        except LookupError: txt = raw.decode("utf-8", "replace")
        return txt, r.geturl()

def find_site(name):
    cn = clean(name)
    cands = []
    for q in (f"{cn} 公式サイト 会社概要", f"{cn}"):
        for attempt in range(3):
            try:
                cands += DDGS().text(q, region="jp-jp", max_results=8, backend="bing"); break
            except Exception as e:
                if "No results" in str(e): break
                time.sleep(3 * (attempt + 1))
        if cands: break
        time.sleep(0.8)
    core = re.sub(r"[ー・\-]", "", cn)
    seen = set()
    for x in cands:
        u = x["href"]; host = urllib.parse.urlparse(u).netloc
        if host in seen or BAD.search(host): continue
        seen.add(host)
        # 社名が検索結果のタイトル/本文に出ていること(別会社の取り違え防止)
        if core[:4] in re.sub(r"[ー・\-\s]", "", x["title"] + x["body"]):
            return u
    return None

def page_text(doc):
    for bad in doc.xpath("//script|//style|//noscript"): bad.drop_tree()
    return re.sub(r"[ \t　]+", " ", doc.text_content())

def collect(site, name):
    """返り値: (取得できたか, ページ一覧[(url,text)], 言語切替あり, 社名が本文に出たか)"""
    pages, lang = [], False
    txt, final = get(site)
    if not txt: return False, [], False, False
    base = urllib.parse.urlparse(final)
    root = f"{base.scheme}://{base.netloc}/"
    try:
        doc = LH.fromstring(txt); doc.make_links_absolute(final)
    except Exception:
        return False, [], False, False
    links, seen = [], {final}
    for a in doc.xpath("//a[@href]"):
        h, t = a.get("href", ""), (a.text_content() or "").strip()[:30]
        if LANG_LINK.search(t) or LANG_LINK.search(urllib.parse.urlparse(h).path): lang = True
        if urllib.parse.urlparse(h).netloc == base.netloc and PAGE_LINK.search(t) and h not in seen:
            seen.add(h); links.append(h)
    pages.append((final, page_text(doc)))
    for h in links[:4]:
        try:
            t2, f2 = get(h)
            if t2: pages.append((f2, page_text(LH.fromstring(t2))))
        except Exception: pass
    core = re.sub(r"[ー・\-\s]", "", clean(name))
    named = any(core[:4] in re.sub(r"[ー・\-\s]", "", p[1]) for p in pages)
    return True, pages, lang, named

def evidence(pages):
    ev = []
    for u, t in pages:
        for m in STRONG.finditer(t):
            s = t[max(0, m.start() - 40): m.end() + 50].replace("\n", " ")
            ev.append((u, s))
            if len(ev) >= 12: return ev
    return ev

def ask(prompt):
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False,
                       "think": False, "format": "json", "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    return json.loads(json.loads(urllib.request.urlopen(req, timeout=300).read())["message"]["content"])

def judge(r):
    name = r["企業名"]
    try:
        site = find_site(name)
        if not site: return ["不明", "公式サイト特定できず", "", "低"]
        ok, pages, lang, named = collect(site, name)
        if not ok: return ["不明", "公式サイト取得不可", site, "低"]
        if not named: return ["不明", "取得ページに社名なし(別サイトの可能性)", site, "低"]
        ev = evidence(pages)
        if not ev:
            return ["シグナルなし", "公式サイト確認済・海外の記載なし" + ("(外国語版リンクあり)" if lang else ""), pages[0][0], "中"]
        j = ask(PROMPT.format(name=name, ind=r.get("業種", ""), ev="\n".join(f"- {u}: {s}" for u, s in ev)))
        v = j.get("海外事業", "不明")
        if v == "あり":
            return ["あり", str(j.get("根拠", ""))[:80], j.get("url") or ev[0][0], "高" if lang else "中"]
        return ["シグナルなし", "記載はあるが海外事業の根拠弱い:" + str(j.get("根拠", ""))[:40], pages[0][0], "低"]
    except Exception as e:
        return ["不明", f"エラー:{type(e).__name__}:{str(e)[:40]}", "", "低"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--limit", type=int); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sample", type=int); a = ap.parse_args()
    rows = list(csv.DictReader(open(a.src, encoding="utf-8-sig")))
    if a.sample: random.seed(1); rows = random.sample(rows, a.sample)
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
