# -*- coding: utf-8 -*-
"""元旦/尼罗/情人节/新春 锚点礼包(纯券) 补 钻石(1002)+VIP点数(2022)
对齐世界杯口径: 券20/80/200/400 -> 钻2500/10000/25000/50000 + VIP25/100/250/500
规则: 同RewardID内col0(seq)连续 -> 删旧单券行, 整组重排到连续空闲 40291+。
"""
import csv, sys, os
REPO=r"C:\x3\gdconfig"; P=os.path.join(REPO,"tsv/Reward__Reward.tsv")
DRY="--apply" not in sys.argv
GROUPS=[210512,210513,210514,210515, 210612,210613,210614,210615,
        210712,210713,210714,210715, 210812,210813,210814,210815]
TIER={20:(2500,25), 80:(10000,100), 200:(25000,250), 400:(50000,500)}
with open(P,encoding="utf-8",newline="") as f: rows=list(csv.reader(f,delimiter="\t"))
hdr,data=rows[:5],rows[5:]
def find(g):
    rs=[r for r in data if len(r)>1 and r[1]==str(g)]
    assert len(rs)==1, f"grp{g} expected 1 row got {len(rs)}"
    return rs[0]
old_kill=set(find(g)[0] for g in GROUPS)
print("删除旧锚点单券行 seq:",sorted(old_kill,key=int))
seq=40291; new=[]
for g in GROUPS:
    tpl=find(g); qty=int(tpl[5]); dia,vip=TIER[qty]
    note=tpl[11] if len(tpl)>11 else ""
    # 券行(克隆原行,新seq)
    t=list(tpl); t[0]=str(seq); seq+=1; new.append(t)
    # 钻石
    d=list(tpl); d[0]=str(seq); d[3]="1002"; d[4]="钻石"; d[5]=str(dia); seq+=1; new.append(d)
    # VIP点数
    v=list(tpl); v[0]=str(seq); v[3]="2022"; v[4]="VIP点数"; v[5]=str(vip); seq+=1; new.append(v)
# 校验: seq唯一 + 组内连续
data2=[r for r in data if r[0] not in old_kill]
allseq=[int(r[0]) for r in data2 if r[0].isdigit()]+[int(r[0]) for r in new]
assert len(allseq)==len(set(allseq)), "seq重复"
from collections import defaultdict
g2=defaultdict(list)
for r in new: g2[r[1]].append(int(r[0]))
for rid,ss in g2.items():
    assert ss==list(range(min(ss),max(ss)+1)), f"{rid} seq不连续 {ss}"
    assert len(ss)==3, f"{rid} 行数!=3"
print(f"新增 {len(new)} 行 (seq 40291-{seq-1}), 共{len(g2)}组每组3行")
for r in new:
    print("  "+"\t".join(r))
if DRY:
    print("\n[DRY] 未写盘"); sys.exit()
out=hdr+data2+new
with open(P,"w",encoding="utf-8",newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    for r in out: w.writerow(r)
print("[OK] 写盘完成")
