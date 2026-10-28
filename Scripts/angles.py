import xml.etree.ElementTree as ET, re, gzip, sys
src,dst=sys.argv[1],sys.argv[2]
raw=open(src,'rb').read()
txt=gzip.decompress(raw).decode('utf-8')
open('q2.xml','w',encoding='utf-8').write(txt)
r=ET.parse('q2.xml').getroot()
byid={}
for e in r:
    k=e.attrib.get('ObjectID') or e.attrib.get('ObjectUID')
    if k: byid[k]=e
T=254016000000
plans={
 'オペラ寄席東京 3min_20261024':[1,2,3,2,1,3,2,3,0,2,3,1,2,3,2,0,3,2,1,3,2,3],
 'オペラ寄席東京 1min_20261024':[1,2,3,0,2,3,0,1,3,2,0],
 'オペラ寄席東京 1min_v2_20261024':[1,3,2,0,1,2,3,0,2,1,3],
}
changes={}
for s_ in r:
    if s_.tag!='Sequence': continue
    n=s_.findtext('Name')
    if n not in plans: continue
    vg=byid[s_.find('TrackGroups')[0].find('Second').attrib['ObjectRef']]
    bystart={}
    for trref in vg.find('TrackGroup/Tracks'):
        tr=byid[trref.attrib['ObjectURef']]
        for ti in tr.find('ClipTrack/ClipItems/TrackItems'):
            it=byid[ti.attrib['ObjectRef']]
            scn=it.find('ClipTrackItem/SubClip')
            if scn is None: continue
            sc=byid[scn.attrib['ObjectRef']]
            if sc.findtext('Name')!='マルチカメラ_全体 本編': continue
            _s=it.find('ClipTrackItem/TrackItem/Start'); st=int(_s.text) if _s is not None else 0
            bystart.setdefault(st,[]).append(sc.find('Clip').attrib['ObjectRef'])
    starts=sorted(bystart)
    print(n,len(starts),'pieces',sum(len(v) for v in bystart.values()),'clips')
    for k,st in enumerate(starts):
        for cid in bystart[st]: changes[cid]=plans[n][k%len(plans[n])]
for cid,ang in changes.items():
    a=txt.index('<VideoClip ObjectID="%s"'%cid); b=txt.index('</VideoClip>',a)
    blk=txt[a:b]
    blk=re.sub(r'\s*<SelectedTrackIndex>\d+</SelectedTrackIndex>','',blk)
    blk=re.sub(r'\s*<IsMulticam>\w+</IsMulticam>','',blk)
    blk=blk.replace('</ClipID>','</ClipID>\n\t\t\t<SelectedTrackIndex>%d</SelectedTrackIndex>'%ang,1)
    blk=blk.replace('</OutPoint>','</OutPoint>\n\t\t\t<IsMulticam>true</IsMulticam>',1)
    assert '<SelectedTrackIndex>' in blk and '<IsMulticam>' in blk,cid
    txt=txt[:a]+blk+txt[b:]
open(dst,'wb').write(gzip.compress(txt.encode('utf-8')))
print('written',dst)
