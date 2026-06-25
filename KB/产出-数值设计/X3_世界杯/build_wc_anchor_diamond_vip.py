# -*- coding: utf-8 -*-
"""世界杯锚点礼包补 钻石+VIP点数 (之前纯券=有问题)
锚点档(211012-15: $4.99/$19.99/$49.99/$99.99·券20/80/200/400) 价格与券数与A线付费包完全一致
→ 直接克隆同价A线组(211002/006/008/010)的 券+钻+VIP 内容到锚点RewardID。
规则: 同RewardID内col0(seq)必须连续 → 删旧单券行, 整组重排到连续空闲seq 40279-40290。
"""
import csv, sys, os
REPO=r"C:\x3\gdconfig"; P=os.path.join(REPO,"tsv/Reward__Reward.tsv")
DRY="--apply" not in sys.argv
# target RewardID <- template A线 RewardID (同价同券)
MAP=[("211012","211002","$4.99"),("211013","211006","$19.99"),
     ("211014","211008","$49.99"),("211015","211010","$99.99")]
with open(P,encoding="utf-8",newline="") as f: rows=list(csv.reader(f,delimiter="\t"))
hdr,data=rows[:5],rows[5:]
def grp(rid): return [r for r in data if len(r)>1 and r[1]==rid]
# 删旧锚点单券行
old_kill=set(r[0] for tgt,_,_ in MAP for r in grp(tgt))
print("删除旧锚点行 seq:",sorted(old_kill))
data=[r for r in data if r[0] not in old_kill]
# 构造新行
seq=40279; new=[]
for tgt,tpl,price in MAP:
    for r in grp(tpl):
        nr=list(r); nr[0]=str(seq); nr[1]=tgt
        if len(nr)>11: nr[11]=f"世界杯锚点礼包{price}"
        new.append(nr); seq+=1
assert seq==40291, seq
# seq 唯一性 + 组内连续校验
allseq=[int(r[0]) for r in data if r[0].isdigit()]+[int(r[0]) for r in new]
assert len(allseq)==len(set(allseq)), "seq 重复!"
from collections import defaultdict
g=defaultdict(list)
for r in new: g[r[1]].append(int(r[0]))
for rid,ss in g.items():
    assert ss==list(range(min(ss),max(ss)+1)), f"{rid} seq不连续 {ss}"
print(f"新增 {len(new)} 行 (seq 40279-{seq-1}):")
for r in new: print("  "+"\t".join(r))
if DRY:
    print("\n[DRY] 未写盘"); sys.exit()
out=hdr+data+new
with open(P,"w",encoding="utf-8",newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    for r in out: w.writerow(r)
print("[OK] 写盘完成")
