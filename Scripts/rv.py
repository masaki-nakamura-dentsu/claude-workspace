import json,subprocess,sys
P="/Users/maxakisan/.local/bin/ppb"
V=json.loads(sys.argv[1])
def call(c,p): return subprocess.run([P,"call",c,json.dumps(p,ensure_ascii=False)],capture_output=True,text=True).stdout.strip()
for S in sys.argv[2:]:
    d=json.loads(subprocess.run([P,"sequence-details",S],capture_output=True,text=True).stdout)
    for a in d['audio'][0]:
        if a['name'].startswith('マルチカメラ') and (a['start']>6.5 or S.endswith('0261024') and 'v2' not in S):
            if 'スタジオリバーブ' in call("clipComponents",{"sequenceName":S,"kind":"a","track":0,"atSec":a['start']}):
                for p,v in V.items(): call("setParam",{"sequenceName":S,"kind":"a","track":0,"atSec":a['start'],"comp":2,"prop":int(p),"value":v})
