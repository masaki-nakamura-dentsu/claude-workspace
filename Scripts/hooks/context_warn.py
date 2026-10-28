#!/usr/bin/env python3
import json,sys
try:
    p=json.load(sys.stdin).get("transcript_path");last=0
    for line in open(p):
        try: u=json.loads(line).get("message",{}).get("usage")
        except Exception: continue
        if u: last=u.get("input_tokens",0)+u.get("cache_read_input_tokens",0)+u.get("cache_creation_input_tokens",0)
    if last>=120000:
        print(f"[context] 現在約{last//1000}kトークン。返答冒頭でwork_status記録→/clear(または/compact)を一言勧めること。")
except Exception: pass
