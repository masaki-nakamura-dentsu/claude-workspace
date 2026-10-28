#!/usr/bin/env python3
"""
GBC週報(部長会進行用) x GBC知見 マッチング → 木村DMD向けまとめExcel生成

入力: downloads/ 配下の最新エクスポート済みxlsx
      (列: 部署名/Dept., GBC案件/Items: 案件名/Item title, フェーズ/Phase, 商流/Business flow,
            クライアント/Client, 概要/アップデート(5W1H)/Report (5W1H),
            ネクストステップ(5W1H)/Next step(5W1H), 責任者(GBC), 地域/Region, 関係会社/Partner companies, ...)
出力: output/GBC週報まとめ_<YYYYMMDD>.xlsx
      (元の列 + GBC知見アドバイス列 + 類似事例(過去週報アーカイブ)列)

また、実行するたびに当該週の案件行を archive/weekly_snapshots.jsonl に追記する
(類似事例検索は将来の実行時にこのアーカイブを遡って行う)。
"""
import json
import re
import sys
import glob
import os
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
DOWNLOAD_DIR = BASE / "downloads"
OUTPUT_DIR = BASE / "output"
ARCHIVE_FILE = BASE / "archive" / "weekly_snapshots.jsonl"

GBC_INDEX_DIR = Path.home() / "Library/CloudStorage/OneDrive-電通/GBC戦略企画部_知見インデックス化・週次まとめ"
KNOWLEDGES_FILE = GBC_INDEX_DIR / "gbc_chishiki_knowledges_index.json"
OSHIETE_FILE = GBC_INDEX_DIR / "gbc_chishiki_oshietegbc_index.json"

REGION_ALIASES = {
    "台湾": ["台湾"], "タイ": ["タイ"], "ベトナム": ["ベトナム"], "中国": ["中国"],
    "香港": ["香港"], "マレーシア": ["マレーシア"], "インドネシア": ["インドネシア"],
    "シンガポール": ["シンガポール"], "フィリピン": ["フィリピン"], "韓国": ["韓国"],
    "インド": ["南西アジア"], "米国": ["北米"], "アメリカ": ["北米"], "日本": ["日本"],
    "欧州": ["欧州"], "オセアニア": ["オセアニア"], "オーストラリア": ["オセアニア"],
    "中東": ["中東アフリカ"], "アフリカ": ["中東アフリカ"], "中南米": ["中南米"],
}


def load_json(path):
    if not path.exists():
        print(f"WARNING: {path} が見つかりません", file=sys.stderr)
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def region_tags_for(region_text):
    if not region_text:
        return []
    hits = []
    for key, tags in REGION_ALIASES.items():
        if key in region_text:
            hits.extend(tags)
    return list(set(hits)) or [region_text]


_ASCII_BIGRAM = re.compile(r"^[A-Za-z0-9]{2}$")
# common Japanese business-boilerplate/particle bigrams (sentence endings, filler
# words, dentsu's own name) that show up in almost every summary/Q&A regardless of
# topic - counting these as "shared keywords" is what caused unrelated rows (e.g.
# a terse KDDI status update, an MSG one-liner) to spuriously match unrelated Q&A
_STOPWORD_BIGRAMS = {
    "です", "ます", "した", "して", "こと", "ため", "いる", "ので", "する", "され",
    "れて", "また", "など", "につ", "いて", "対応", "実施", "予定", "検討", "案件",
    "電通", "会社", "株式", "資料", "クラ", "アン", "ント", "イベ", "ベン",
}


def keyword_overlap_score(text_a, text_b):
    if not text_a or not text_b:
        return 0
    # crude Japanese-friendly overlap: count shared 2-gram substrings of length>=2
    def ngrams(s, n=2):
        s = re.sub(r"\s+", "", s)
        return set(s[i:i + n] for i in range(len(s) - n + 1))
    a, b = ngrams(text_a), ngrams(text_b)
    shared = a & b
    # pure-ASCII-letter/digit bigrams ("an", "in", "re", "20", ...) are far too
    # common across unrelated English/alphanumeric spans (names, event titles,
    # dates) to count as real topical signal - only Japanese-containing bigrams
    # (or mixed) count toward the match
    shared = {g for g in shared if not _ASCII_BIGRAM.match(g) and g not in _STOPWORD_BIGRAMS}
    # require a minimum absolute overlap (not just ratio) so two very short
    # strings that happen to share one bigram don't score as a strong match
    if not a or not b or len(shared) < 4:
        return 0
    return len(shared) / max(1, min(len(a), len(b)))


PLACEHOLDER_NAMES = {"", "ー", "-", "−", "N/A", "n/a", "なし", "未定", "不明", "TBD"}
# dentsu's own name is not a "client" - nearly every summary/knowledge mentions it,
# so substring-matching on it produces meaningless false-positive "same client" hits
# (e.g. a knowledge entry with clientName="電通" matching every "電通シンガポール" row)
GENERIC_OWN_NAMES = {"電通", "dentsu", "Dentsu", "DENTSU", "電通グループ", "dentsu group", "Dentsu Group"}


def is_meaningful_name(name):
    if not name:
        return False
    name = str(name).strip()
    if name in GENERIC_OWN_NAMES:
        return False
    return len(name) >= 2 and name not in PLACEHOLDER_NAMES


def find_related_knowledges(client, region, summary, knowledges, top_n=3):
    scored = []
    region_tags = set(region_tags_for(region))
    client_ok = is_meaningful_name(client)
    for k in knowledges:
        score = 0.0
        reasons = []
        k_client = k.get("clientName")
        if client_ok and is_meaningful_name(k_client):
            if client.strip() == k_client.strip():
                score += 5
                reasons.append("同一クライアント")
            elif client.strip() in k_client or k_client in client.strip():
                score += 2
                reasons.append("クライアント名部分一致")
        k_region_tags = {t["name"] for t in k.get("tags", []) if t["category"] == "エリア"}
        if region_tags & k_region_tags:
            score += 1.5
            reasons.append("エリア一致")
        ov = keyword_overlap_score(summary, (k.get("summary") or "") + " " + (k.get("title") or ""))
        score += ov * 2
        if ov > 0.15:
            reasons.append("内容キーワード類似")
        if score > 1.4:
            scored.append((score, k, reasons))
    scored.sort(key=lambda x: -x[0])
    return scored[:top_n]


def find_related_oshiete(summary, oshiete, top_n=2):
    scored = []
    for o in oshiete:
        if not (o.get("answer") or "").strip():
            continue  # 未回答のQ&Aはアドバイスとして出しても無意味なので除外
        text = (o.get("questionBody") or "") + " " + (o.get("title") or "")
        ov = keyword_overlap_score(summary, text)
        if ov > 0.20:
            scored.append((ov, o))
    scored.sort(key=lambda x: -x[0])
    return scored[:top_n]


def find_similar_past_cases(client, archive_rows, current_week_key, top_n=3):
    hits = []
    for row in archive_rows:
        if row.get("_week") == current_week_key:
            continue
        if client and row.get("client") and client.strip() == row["client"].strip():
            hits.append(row)
    hits.sort(key=lambda r: r.get("_week", ""), reverse=True)
    return hits[:top_n]


def build_advice_text(related_k, related_o, similar_past):
    parts = []
    if related_k:
        parts.append("【関連するGBC知見】")
        for score, k, reasons in related_k:
            notice = f"（注意: {k['notice']}）" if k.get("notice") else ""
            parts.append(f"・{k['title']}｜{k.get('clientName') or ''}｜{','.join(reasons)}{notice}")
    if related_o:
        parts.append("【関連する教えてGBC】")
        for score, o in related_o:
            ans = (o.get("answer") or "")[:150]
            qtitle = (o.get("title") or "")[:60]
            parts.append(f"・Q: {qtitle} → A: {ans}")
    if similar_past:
        parts.append("【過去の同クライアント案件（週報アーカイブより）】")
        for r in similar_past:
            parts.append(f"・{r.get('_week')}: {r.get('phase')}｜{(r.get('summary') or '')[:80]}")
    if not parts:
        parts.append("（関連する既存GBC知見・過去事例は見つかりませんでした。知見ギャップの可能性があります）")
    return "\n".join(parts)


def find_latest_download():
    files = sorted(glob.glob(str(DOWNLOAD_DIR / "*.xlsx")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def main():
    import openpyxl

    src_path = sys.argv[1] if len(sys.argv) > 1 else find_latest_download()
    if not src_path or not os.path.exists(src_path):
        print("ERROR: 入力xlsxが見つかりません。download_step1/2 で先にエクスポートしてください。", file=sys.stderr)
        sys.exit(1)

    knowledges = load_json(KNOWLEDGES_FILE)
    oshiete = load_json(OSHIETE_FILE)

    wb = openpyxl.load_workbook(src_path, data_only=True)
    ws = wb.active

    # 「フォーマット済みレポート」エクスポートは先頭に見出し・検索条件ブロックがあるため、
    # 実際の列見出し行(クライアント列を含む行)を探す
    header_row_idx = None
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=30, values_only=True), start=1):
        if any(v and "クライアント" in str(v) for v in row):
            header_row_idx = i
            break
    if header_row_idx is None:
        print("ERROR: 列見出し行が見つかりません（レポート形式が変わった可能性）", file=sys.stderr)
        sys.exit(1)

    headers = [c.value for c in ws[header_row_idx]]
    print("検出した列見出し行:", header_row_idx, headers)

    def col(name_substr):
        for i, h in enumerate(headers):
            if h and name_substr in str(h):
                return i
        return None

    idx_dept = col("部署名") or col("Dept")
    idx_item = col("案件名") or col("Item title")
    idx_client = col("クライアント") or col("Client")
    idx_region = col("地域") or col("Region")
    idx_summary = col("概要") or col("5W1H")
    idx_phase = col("フェーズ") or col("Phase")
    idx_nextstep = col("ネクストステップ")

    # グループ化エクスポートでは部署名/案件名/フェーズはグループ先頭行にしか値がない → 前方補完(ffill)する
    rows = []
    last_dept, last_item, last_phase = None, None, None
    for r in ws.iter_rows(min_row=header_row_idx + 1, values_only=True):
        if all(v is None for v in r):
            continue
        r = list(r)
        if idx_dept is not None:
            last_dept = r[idx_dept] if r[idx_dept] not in (None, "") else last_dept
            r[idx_dept] = last_dept
        if idx_item is not None:
            last_item = r[idx_item] if r[idx_item] not in (None, "") else last_item
            r[idx_item] = last_item
        if idx_phase is not None:
            last_phase = r[idx_phase] if r[idx_phase] not in (None, "") else last_phase
            r[idx_phase] = last_phase
        rows.append({
            "raw": r,
            "client": r[idx_client] if idx_client is not None else None,
            "region": r[idx_region] if idx_region is not None else None,
            "summary": r[idx_summary] if idx_summary is not None else None,
            "phase": r[idx_phase] if idx_phase is not None else None,
        })

    week_key = datetime.now().strftime("%Y-W%W")
    ARCHIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    archive_rows = []
    if ARCHIVE_FILE.exists():
        with open(ARCHIVE_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    archive_rows.append(json.loads(line))

    out_wb = openpyxl.Workbook()
    out_ws = out_wb.active
    out_ws.title = "週報まとめ"
    out_ws.append(list(headers) + ["GBC知見アドバイス"])

    new_archive_entries = []
    for row in rows:
        related_k = find_related_knowledges(row["client"], row["region"], row["summary"], knowledges)
        related_o = find_related_oshiete(row["summary"], oshiete)
        similar_past = find_similar_past_cases(row["client"], archive_rows, week_key)
        advice = build_advice_text(related_k, related_o, similar_past)
        out_ws.append(list(row["raw"]) + [advice])

        new_archive_entries.append({
            "_week": week_key, "_saved_at": datetime.now().isoformat(),
            "client": row["client"], "region": row["region"],
            "phase": row["phase"], "summary": row["summary"],
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"GBC週報まとめ_{datetime.now().strftime('%Y%m%d')}.xlsx"
    out_wb.save(out_path)
    print("保存しました:", out_path)

    with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
        for e in new_archive_entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"アーカイブに{len(new_archive_entries)}件追記:", ARCHIVE_FILE)

    return str(out_path)


if __name__ == "__main__":
    main()
