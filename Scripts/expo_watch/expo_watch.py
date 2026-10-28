#!/usr/bin/env python3
"""ベオグラード万博(Expo 2027)の日次ウォッチ。
claude -p (WebSearch/WebFetch)で現地メディア・公式情報を集め、
レポートをDropboxに保存し、要点をTeamsに送る。既報のURLは state.json で除外する。
パラメータ(2026-10-26設定): 毎日9:00 / 現地メディア+公式優先 / 新着のみ報告。"""
import json, re, subprocess, sys, os
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.home() / "dentsuDropbox Dropbox/中村正樹"
REPORT_DIR = ROOT / "Work/Client/Serbia_Expo/日次レポート"
STATE = HERE / "state.json"
LOG = Path.home() / "expo_watch_logs"
sys.path.insert(0, str(ROOT / ".claude-sync/Scripts/notify"))
from teams_notify import notify

JOB = "万博ウォッチ"
JST = timezone(timedelta(hours=9))
CLAUDE = str(Path.home() / ".local/bin/claude")

PROMPT = """あなたはベオグラード国際博覧会(EXPO 2027 Belgrade, 2027/5/15-8/15, 会場はスルチン地区)の情報収集担当です。
今日は {today}。WebSearchとWebFetchで、**直近{days}日以内に出た情報**を集めてください。最低でも10回以上、キーワードと媒体を変えて検索し、各媒体の記事ページも実際に開いて日付と内容を確認すること。

## 優先順位
1. 公式情報(最優先): Expo 2027公式サイト(expo2027belgrade.rs / expo2027.rs等)、セルビア政府・関係省庁(srbija.gov.rs 等)、Expo 2027運営会社、Infrastruktura železnice Srbije / Srbijavoz(鉄道)、ベオグラード市、空港(Nikola Tesla)、JETRO・外務省・在セルビア日本大使館(日本館関連)。
2. 現地メディア: RTS, Tanjug, Beta, B92, N1, Blic, Politika, Danas, Novosti, Informer, RTV, Nova.rs, Ekspres, Kurir, Mondo, Beograd.rs 等。
3. 英語・日本語の報道は補足のみ。
検索はセルビア語(ラテン文字・キリル文字の両方)で行うこと。例: "Expo 2027", "Ekspo 2027", "Експо 2027", "Expo voz", "pruga Expo", "metro Beograd Expo", "Surčin Expo događaji", "program Expo 2027", "Japanski paviljon", "nacionalni dani Expo", "Expo 2027 ulaznice", "Expo 2027 saobraćaj".

## 特に知りたいこと
会期中の交通(鉄道・電車・地下鉄/BG Voz/シャトル・空港アクセス・道路)、開催イベント・文化プログラム・ナショナルデー、チケット・開場時間、会場建設の進捗・遅延、参加国館(特に日本館)、宿泊・治安・規制、ビザ、運営体制・人事・予算の変化。

## 除外(すでに報告済みのURL。同じ記事は載せない)
{seen}

## 出力
次のJSONだけを出力(前後に説明文やコードフェンスを付けない)。見つからなければ items は空配列。
{{"items":[{{"category":"交通|イベント|チケット・運営|建設進捗|日本館・参加国|その他",
"official":true/false(発信元が公式機関なら true),
"headline_ja":"日本語の見出し(40字以内)",
"summary_ja":"何が決まった/起きたか。日付・数字・固有名詞を含め2〜3文。です・ます調",
"highlight":"summary_ja内にそのまま含まれる最重要フレーズ(日付や数字など、15字以内)",
"implication_ja":"日本館・来場者・現地運営にとって何を意味するか(1文、推測は『〜とみられる』)",
"source":"媒体名または機関名","published":"YYYY-MM-DD(不明なら空)","url":"記事URL","lang":"sr|en|ja"}}],
"headline_summary":["今日の要点を各40字以内で最大3つ"],
"note":"検索で不確かだった点を1文(任意)"}}
事実だけを書き、推測は「〜とみられる」と明示。URLは実際に確認できたものだけ。"""


def load_state():
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {"seen": []}


def run_claude(prompt):
    r = subprocess.run(
        [CLAUDE, "-p", prompt, "--allowedTools", "WebSearch", "WebFetch", "Bash(curl:*)", "--no-session-persistence"],
        capture_output=True, text=True, timeout=1500, cwd=str(HERE))
    if r.returncode != 0:
        raise RuntimeError(f"claude exit {r.returncode}: {r.stderr[-500:] or r.stdout[-500:]}")
    return r.stdout


def parse(out):
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        raise ValueError("JSONが見つからない: " + out[:300])
    return json.loads(m.group(0))


HEAD_C, HL_C, IMP_C = "#5B2D90", "#C0261E", "#1B6E3C"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_html(items, data, heading, first, rp):
    P = [f'<p style="font-size:17px;"><b>{esc(heading)}</b></p>']
    pts = data.get("headline_summary") or []
    if pts:
        P.append("<ul>" + "".join(f"<li>{esc(x)}</li>" for x in pts[:3]) + "</ul>")
    P.append(f"<p>新着 {len(items)} 件(公式 {sum(1 for i in items if i.get('official'))} / 報道 {sum(1 for i in items if not i.get('official'))})</p><p>&nbsp;</p>")
    for n, i in enumerate(items):
        tag = "公式" if i.get("official") else "報道"
        P.append(f'<h2><span style="color:{HEAD_C};">■ [{esc(i.get("category",""))}] {esc(i.get("headline_ja",""))}</span></h2>')
        body = esc(i.get("summary_ja", ""))
        hl = esc(i.get("highlight", ""))
        if hl and hl in body:
            body = body.replace(hl, f'<span style="color:{HL_C}; font-weight:bold;">{hl}</span>', 1)
        P.append(f"<p>{body}</p>")
        if i.get("implication_ja"):
            P.append(f'<p><span style="color:{IMP_C};"><b>▶ 意味合い:</b> {esc(i["implication_ja"])}</span></p>')
        pub = f" / {esc(i['published'])}" if i.get("published") else ""
        P.append(f'<p><span style="color:#666666; font-size:12px;">出典: {esc(i.get("source",""))}({tag}{pub}) &nbsp;<a href="{esc(i["url"])}">記事を開く</a></span></p>')
        if n != len(items) - 1:
            P.append("<p>&nbsp;</p>")
    if data.get("note"):
        P.append(f'<p><span style="color:#666666; font-size:12px;">※ {esc(data["note"])}</span></p>')
    return "\n".join(P)



def post_to_self_chat(html, verify_text):
    """週報の投稿関数を流用するが、タブ選択だけ差し替える。
    ボットブラウザにはTeamsタブが複数あり(2026-10-27)、週報の関数は最初のタブを使うため
    別チャンネル表示のタブに当たって失敗する。自分宛チャット表示中のタブを優先する。"""
    import inspect
    sys.path.insert(0, str(Path.home() / "TeamsExport/scripts"))
    import weekly_ai_digest as w
    src = inspect.getsource(w.post_html_to_self_chat)
    old = 'page = next((pg for pg in ctx.pages\n                     if "teams.microsoft.com" in pg.url or "teams.cloud.microsoft" in pg.url), None)'
    new = ('_c = [pg for pg in ctx.pages if "teams.microsoft.com" in pg.url or "teams.cloud.microsoft" in pg.url]\n'
           '        page = next((pg for pg in _c if "あなた" in pg.title()), _c[0] if _c else None)')
    assert old in src, "weekly_ai_digestの構造が変わった"
    ns = dict(w.__dict__)
    exec(src.replace(old, new), ns)
    ns["post_html_to_self_chat"](html, verify_text)


CHANNEL_URL = ("https://teams.microsoft.com/_#/l/channel/19%3Ad5b28c13989b440dad18b999923f84f6%40thread.tacv2/"
               "05_%E9%96%A2%E9%80%A3%E6%83%85%E5%A0%B1%E5%85%B1%E6%9C%89"
               "?groupId=951a0954-c2dc-4738-9c12-fdb1abc47fdb&tenantId=fccbe2bf-88de-49c4-af92-1e9500cb29a4")
MENTION_TYPE = "@ベオグラード"      # 候補の先頭に「🇷🇸ベオグラード万博 行催事(制作)(Team)」が出る
MENTION_PICK = "行催事"
BOT_CDP = "http://127.0.0.1:9226"


def post_to_channel(html, verify_text):
    """🇷🇸ベオグラード万博 行催事(制作) / 05_関連情報共有 に、チームへの@メンション付きで新規投稿する。
    ブラウザ(共有ボットブラウザ)のTeams Web版で行い、デスクトップアプリは起動しない。
    URLは _#/l/channel 形式(teams.microsoft.com/l/... だとアプリ起動ページで止まる)。"""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(BOT_CDP)
        ctx = b.contexts[0]
        pg = ctx.new_page()
        try:
            pg.goto(CHANNEL_URL, timeout=60000)
            box = pg.locator("[data-tid=ckeditor]").first
            box.wait_for(timeout=90000)
            if "05_関連情報共有" not in pg.title():
                raise RuntimeError(f"チャンネルに着地できていない: {pg.title()!r}")
            pg.wait_for_timeout(3000)
            box.click()
            pg.keyboard.press("Meta+A"); pg.keyboard.press("Backspace")  # 下書きはタブをまたいで残る
            pg.wait_for_timeout(500)
            pg.keyboard.type(MENTION_TYPE, delay=150)
            opt = pg.locator('[data-tid^="autocomplete-picker-item-"]').filter(has_text=MENTION_PICK).filter(has_text="Team").first
            opt.wait_for(timeout=20000)
            opt.click()
            pg.wait_for_timeout(500)
            pg.keyboard.press("Shift+Enter")
            # OSのクリップボード/Meta+Vは使わない(ユーザーが別ブラウザ操作中だとそちらに貼り付くため)。
            # 対象ページ内でpasteイベントを合成し、このタブのエディタにだけ流し込む
            pasted = pg.evaluate("""(html) => {
                const el = document.querySelector('[data-tid=ckeditor]'); el.focus();
                const dt = new DataTransfer();
                dt.setData('text/html', html); dt.setData('text/plain', html.replace(/<[^>]+>/g, ''));
                return el.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true})); }""", html)
            pg.wait_for_timeout(2000)
            draft = box.inner_html()
            if "schema.skype.com/Mention" not in draft and 'itemtype' not in draft:
                raise RuntimeError("メンションが下書きに入っていない。送信を中止")
            if verify_text not in box.inner_text():
                raise RuntimeError("本文の貼り付けに失敗。送信を中止")
            if os.environ.get("EXPO_DRY"):  # 動作確認用: 送信せず下書きを消して終了
                print("DRY: draft ok, mention ok, len", len(box.inner_text()))
                pg.keyboard.press("Meta+A"); pg.keyboard.press("Backspace")
                return
            sent = pg.evaluate("() => { const b = document.querySelector('[data-tid=\"sendMessageCommands-send\"]');"
                               " if (!b || b.disabled) return false; b.click(); return true; }")
            if not sent:
                pg.keyboard.press("Enter")
            for _ in range(15):
                pg.wait_for_timeout(1000)
                for m in pg.query_selector_all('[data-tid="chat-pane-message"]')[-3:]:
                    if verify_text in (m.inner_text() or ""):
                        # 2026-10-28: 送信直後の表示だけでは実投稿を保証できなかったため、再読込して確認する
                        pg.wait_for_timeout(5000)
                        pg.reload(timeout=60000)
                        box.wait_for(timeout=90000)
                        pg.wait_for_timeout(6000)
                        if any(verify_text in (x.inner_text() or "") for x in pg.query_selector_all('[data-tid="chat-pane-message"]')[-3:]):
                            return
                        raise RuntimeError("送信直後は見えたが再読込後に投稿が残っていない")
            raise RuntimeError(f"投稿を確認できない(looked for {verify_text!r})")
        finally:
            pg.close()


def main():
    LOG.mkdir(exist_ok=True)
    now = datetime.now(JST)
    today = f"{now:%Y-%m-%d}"
    st = load_state()
    seen = st["seen"][-150:]
    try:
        days = 7 if st["seen"] else 90  # 初回のみ遡及
        out = run_claude(PROMPT.format(today=today, days=days, seen="\n".join(seen) or "(なし)"))
        (LOG / f"{now:%Y%m%d_%H%M}.raw.txt").write_text(out)
        data = parse(out)
    except Exception as e:
        notify("ERROR", JOB, "収集に失敗", detail=str(e), log=str(LOG))
        return 1

    items = [i for i in data.get("items", []) if i.get("url") and i["url"] not in seen]
    items.sort(key=lambda i: (not i.get("official"), i.get("category", "")))

    # レポート(Dropbox)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rp = REPORT_DIR / f"expo_watch_{now:%Y%m%d}.md"
    L = [f"# ベオグラード万博 日次レポート {today}", ""]
    if data.get("note"):
        L += [f"> {data['note']}", ""]
    if not items:
        L.append("新着なし。")
    for i in items:
        tag = "【公式】" if i.get("official") else "【報道】"
        L += [f"## {tag}[{i.get('category','')}] {i.get('headline_ja','')}",
              f"{i.get('summary_ja','')}", f"▶ 意味合い: {i.get('implication_ja','')}", "",
              f"- 出典: {i.get('source','')} ({i.get('published','')}) / {i.get('lang','')}",
              f"- {i['url']}", ""]
    rp.write_text("\n".join(L))

    st["seen"] = (seen + [i["url"] for i in items])[-300:]
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1))

    # Teams: チャンネルへ直接投稿(2026-10-27〜)。新着なしのときは投稿せず、自分宛Webhookにだけ報告
    if not items:
        notify("INFO", JOB, "更新なし", detail=data.get("note", ""), log=str(rp))
        return 0
    heading = f"今日の要点 ({today})"
    html = render_html(items, data, heading, len(seen) == 0, rp)
    try:
        post_to_channel(html, heading)
    except Exception as e:
        notify("ERROR", JOB, "チャンネル投稿に失敗", detail=repr(e), log=str(rp))
        return 1
    notify("OK", JOB, f"投稿しました {len(items)}件", log=str(rp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
