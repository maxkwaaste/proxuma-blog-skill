import re, glob, sys
def boxes(svg):
    fos=[]
    for m in re.finditer(r'<foreignObject class="fo" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg):
        x,y,w,h=map(float,m.groups()); fos.append(('label',x,y,w,h))
    bars=[]
    for m in re.finditer(r'<rect class="bar" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg):
        x,y,w,h=map(float,m.groups()); bars.append(('bar',x,y,w,h))
    vbm=re.search(r'viewBox="0 0 (\d+) (\d+)"', svg); W,H=int(vbm.group(1)),int(vbm.group(2))
    return fos,bars,W,H
def inter(a,b,buf):
    _,ax,ay,aw,ah=a; _,bx,by,bw,bh=b
    return not (ax+aw+buf<=bx or bx+bw+buf<=ax or ay+ah+buf<=by or by+bh+buf<=ay)
buf=8; m=64; fail=0
for f in sorted(glob.glob('0*.svg')):
    svg=open(f).read(); fos,bars,W,H=boxes(svg); items=fos+bars
    hits=[]
    for i in range(len(items)):
        for j in range(i+1,len(items)):
            if items[i][0]=='bar' and items[j][0]=='bar': continue
            if inter(items[i],items[j],buf): hits.append((items[i],items[j]))
    over=[]
    for it in items:
        _,x,y,w,h=it
        if x<m-0.5 or y<m-0.5 or x+w>W-m+0.5 or y+h>H-m+0.5:
            over.append((it,round(min(x-m,(W-m)-(x+w),y-m,(H-m)-(y+h)),1)))
    status='OK' if not hits and not over else 'FAIL'
    if status=='FAIL': fail+=1
    print(f"{f}: {status}  labels={len(fos)} bars={len(bars)}")
    for a,b in hits: print(f"   COLLISION {a} <> {b}")
    for it,mar in over: print(f"   SAFE-AREA OVERFLOW {it} margin={mar}")
print("\nRESULT:", "ALL PASS" if fail==0 else f"{fail} file(s) FAIL")
