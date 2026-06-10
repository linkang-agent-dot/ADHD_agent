# -*- coding: utf-8 -*-
"""CELL-level merge anomaly: a cell master changed (master!=base) but merge result dropped (result!=master)."""
import subprocess, re, sys
REPO=r"D:\UGit\x2gdconf"
# 用法: python merge_anomaly_audit.py <BASE> <MASTER(被合并保护方)> <DEV(合入方)> <RESULT(合并commit)>
# 检测: 合并是否丢掉了 MASTER 自己改过的格(cell级)。DEV 仅用于参考展示。
_a=[x for x in __import__("sys").argv[1:]]
if len(_a)>=4:
    BASE,MASTER,DEV,RESULT=_a[0],_a[1],_a[2],_a[3]
else:
    BASE="64bbe3ee111b1f4e75f7e27f0b3989c1c3a4153d"
    MASTER="51620db028e628de4a9fd20e14ef34bed3c21bb0"
    DEV="7b678c64ffb17c6e0deb1522444f44a5f3932f33"
    RESULT="afc308f40"
ID_RE=re.compile(r"^\d{3,}$")
def show(ref,path):
    r=subprocess.run(["git","-C",REPO,"show",f"{ref}:{path}"],capture_output=True)
    return None if r.returncode!=0 else r.stdout.decode("utf-8")
def detect_idcol(lines):
    for col in (1,0,2):
        hit=tot=0
        for l in lines[1:300]:
            c=l.split("\t")
            if len(c)>col:
                tot+=1
                if ID_RE.match(c[col].strip()): hit+=1
        if tot and hit/tot>0.6: return col
    return 1
def rows(txt,idcol):
    d={}
    if txt is None: return d
    for l in txt.replace("\r","").split("\n"):
        c=l.split("\t")
        if len(c)>idcol and ID_RE.match(c[idcol].strip()):
            key=c[idcol].strip()+"|"+(c[idcol+1].strip() if len(c)>idcol+1 else "")
            d[key]=c
    return d
files=subprocess.run(["git","-C",REPO,"diff","--name-only",BASE,RESULT,"--","fo/config/","fo/json/"],capture_output=True).stdout.decode().split("\n")
files=[f for f in files if f.strip() and f.endswith(".tsv")]
sys.stdout.reconfigure(encoding="utf-8")
total=0
hdrs={}
for f in files:
    bt=show(BASE,f); mt=show(MASTER,f); dt=show(DEV,f); rt=show(RESULT,f)
    if mt is None or rt is None: continue
    mlines=mt.replace("\r","").split("\n")
    idcol=detect_idcol(mlines)
    hdr=mlines[0].split("\t")
    b=rows(bt,idcol); m=rows(mt,idcol); d=rows(dt,idcol); r=rows(rt,idcol)
    file_anom=[]
    for k,mc in m.items():
        bc=b.get(k); rc=r.get(k)
        if bc is None:
            # master-added row (not in base). anomaly if missing from result.
            if rc is None: file_anom.append((k,"(master新增行)","结果中不存在",""));
            continue
        if rc is None:
            # result dropped the row. ONLY a real anomaly if master changed it vs base
            # (else it's dev's restructure/deletion of a row master never touched — false positive)
            if mc != bc:
                file_anom.append((k,"(整行)","master改过且结果删除了该行",""))
            continue
        # cell level
        n=max(len(mc),len(bc),len(rc))
        for j in range(n):
            mv=mc[j] if j<len(mc) else ""
            bv=bc[j] if j<len(bc) else ""
            rv=rc[j] if j<len(rc) else ""
            if mv!=bv and rv!=mv:   # master changed this cell, result doesn't have master's value
                col=hdr[j] if j<len(hdr) else f"col{j}"
                dv=(d.get(k)[j] if d.get(k) and j<len(d.get(k)) else "?")
                file_anom.append((k,col,f"master={mv[:40]} / 结果={rv[:40]}", f"dev={dv[:40]}"))
    if file_anom:
        total+=len(file_anom)
        print(f"\n######## {f} (idcol={idcol}) 真异常cell: {len(file_anom)} ########")
        for k,col,info,extra in file_anom[:20]:
            print(f"  [{k.split('|')[0]}] {col}: {info}  {extra}")
        if len(file_anom)>20: print(f"   ...(还有{len(file_anom)-20})")
print(f"\n==== cell级真异常合计: {total} ====")
