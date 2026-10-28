import json,subprocess,sys
P="/Users/maxakisan/.local/bin/ppb"
S=sys.argv[1]; add=sys.argv[2]=="add"
def call(c,p):
    o=subprocess.run([P,"call",c,json.dumps(p,ensure_ascii=False)],capture_output=True,text=True).stdout.strip()
    if '"ok": false' in o: print("ERR",c,o[:150])
    return o
def sd(): return json.loads(subprocess.run([P,"sequence-details",S],capture_output=True,text=True).stdout)
if add: call("addVideoTrack",{"sequenceName":S})
d=sd()
e=[i for i,t in enumerate(d['video']) if len(t)==0][0]
v1=[c for c in d['video'][0] if c['name']=="マルチカメラ_全体 本編"]
# V1のブラーを0に
for c in v1: call("setParam",{"sequenceName":S,"kind":"v","track":0,"atSec":c['start'],"comp":2,"prop":5,"value":0})
for c in v1:
    call("placeRange",{"targetSequence":S,"sourceName":"マルチカメラ_全体 本編","inSec":c['inPoint'],"outSec":c['inPoint']+c['end']-c['start'],"atSec":c['start'],"videoTrack":e})
d=sd()
for c in d['audio'][e]: call("removeClipAt",{"sequenceName":S,"kind":"a","track":e,"atSec":c['start']})
print("copy track",e,"clips",len(d['video'][e]))
call("addVideoEffectToTrack",{"sequenceName":S,"track":e,"effectName":"ブラー (ガウス)"})
for c in d['video'][e]:
    call("setParam",{"sequenceName":S,"kind":"v","track":e,"atSec":c['start'],"comp":2,"prop":5,"value":25})
    call("setParam",{"sequenceName":S,"kind":"v","track":e,"atSec":c['start'],"comp":0,"prop":0,"value":30})
d=sd(); print([len(t) for t in d['video']],[len(t) for t in d['audio']])
