# -*- coding: utf-8 -*-
import random, statistics, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# ── 道具单价 (from old system) ──
UV = {
    'train8h': 3.63, 'mechexp': 0.416, 'core': 0.624,
    'resbox': 0.125, 'oshards': 2.495, 'spd24h': 10.89,
}
CN = {
    'train8h': '8h训练加速', 'mechexp': '机甲经验(5w)', 'core': '机能核心',
    'resbox': '资源宝箱10w', 'oshards': '万能橙碎', 'spd24h': '24h通用加速',
}
IDS = {
    'train8h': 11111158, 'mechexp': 11118004, 'core': 11118501,
    'resbox': 11114330, 'oshards': 11116304, 'spd24h': 11111109,
}

def sv(items): return sum(UV[k]*q for k,q in items)

# ── 结构参数 ──
LC = [1, 2, 5, 10, 18, 25]   # 每层消耗token
TP = 5.50                     # token单价
LS = [6, 5, 4, 3, 2, 1]      # 每层格数
MAX_T = sum(LS[i]*LC[i] for i in range(6))  # 127
MAX_C = MAX_T * TP                          # $698.50

# ── 奖励设计 (20格 + 1皮肤) ──
# 目标: 满抽总价值 ≈ $1,236 → ROI = 1.77
# 道具配比对齐老系统: 核心~40%, 橙碎~34%, 24h~13%, 训练~6%, 经验~4%, 资源~3%

LAYERS = [
    # ─── L1: 6格, 1tok($5.5)/抽, ~$17/格 ───
    [
        [('train8h',4), ('mechexp',5)],       # $16.60
        [('mechexp',40)],                      # $16.64
        [('resbox',100), ('core',10)],         # $18.74
        [('core',27)],                         # $16.85
        [('train8h',3), ('resbox',50)],        # $17.14
        [('mechexp',25), ('core',10)],         # $16.64
    ],
    # ─── L2: 5格, 2tok($11)/抽, ~$30/格 ───
    [
        [('core',50)],                         # $31.20
        [('train8h',8)],                       # $29.04
        [('mechexp',55), ('core',12)],         # $30.37
        [('resbox',150), ('core',16)],         # $28.73
        [('core',40), ('train8h',2)],          # $32.22
    ],
    # ─── L3: 4格, 5tok($27.5)/抽, ~$46/格 ───
    [
        [('core',50), ('oshards',5)],          # $43.68
        [('spd24h',4), ('core',5)],            # $46.68
        [('core',50), ('oshards',6)],          # $46.17
        [('core',40), ('spd24h',1), ('train8h',3)],  # $46.74
    ],
    # ─── L4: 3格, 10tok($55)/抽, ~$110/格 ───
    [
        [('core',100), ('oshards',20)],                # $112.30
        [('core',80), ('oshards',15), ('spd24h',2)],   # $109.13
        [('spd24h',6), ('core',50), ('oshards',5)],    # $109.02
    ],
    # ─── L5: 2格, 18tok($99)/抽, ~$236/格 ───
    [
        [('core',125), ('oshards',60)],                # $227.70
        [('core',125), ('oshards',58), ('spd24h',2)],  # $244.49
    ],
    # ─── L6: 皮肤 ───
    [[('skin',1)]],
]

# ══════════════════════════════════════════════════════
#  打印奖励表
# ══════════════════════════════════════════════════════
print("=" * 95)
print("  P2 金字塔机甲Gacha — 奖励方案")
print(f"  消耗曲线: {LC} tok/抽 | Token=${TP} | 满抽={MAX_T}tok=${MAX_C:.0f}")
print("=" * 95)

ltotals = []
grand = 0
for li in range(6):
    lt = 0
    for si, slot in enumerate(LAYERS[li]):
        if li == 5:
            v = 0; desc = "【机甲皮肤】"
        else:
            v = sv(slot)
            desc = " + ".join(f"{CN[k]}x{q}" for k,q in slot)
        lt += v; grand += v
        c = f"{LC[li]}tok(${LC[li]*TP:.0f})"
        print(f"  L{li+1}-{si+1} | {c:>11} | {desc:45s} | ${v:>7.2f}")
    ltotals.append(lt)
    if li < 5:
        print(f"       |             | {'─ Layer '+str(li+1)+' 合计 ─':45s} | ${lt:>7.2f}")
    print()

roi_full = grand / MAX_C
print(f"  ◆ 全部奖励价值(不含皮肤): ${grand:.0f}")
print(f"  ◆ 满抽花费: ${MAX_C:.0f}")
print(f"  ◆ 满抽 ROI: {roi_full:.2f}")

# ══════════════════════════════════════════════════════
#  道具配比对比
# ══════════════════════════════════════════════════════
print()
totals = defaultdict(int)
for li in range(5):
    for slot in LAYERS[li]:
        for k,q in slot: totals[k] += q

old_items = {'core':750,'oshards':150,'spd24h':12,'train8h':15,'mechexp':50,'resbox':300}

print("  ┌────────────┬────────┬────────┬──────────┬──────────┬──────────┐")
print("  │ 道具       │ 老系统 │ 新方案 │ 老$值    │ 新$值    │ 老占比   │")
print("  ├────────────┼────────┼────────┼──────────┼──────────┼──────────┤")
for k in ['core','oshards','spd24h','train8h','mechexp','resbox']:
    oq = old_items[k]; nq = totals[k]
    ov = oq*UV[k]; nv = nq*UV[k]
    opct = ov/1085*100; npct = nv/grand*100
    print(f"  │ {CN[k]:10s} │ {oq:>6} │ {nq:>6} │ ${ov:>7.0f} │ ${nv:>7.0f} │ {opct:>5.1f}%→{npct:.1f}% │")
old_total = sum(old_items[k]*UV[k] for k in old_items)
print(f"  ├────────────┼────────┼────────┼──────────┼──────────┼──────────┤")
print(f"  │ 合计       │        │        │ ${old_total:>7.0f} │ ${grand:>7.0f} │          │")
print(f"  └────────────┴────────┴────────┴──────────┴──────────┴──────────┘")

# ══════════════════════════════════════════════════════
#  模拟 (20万次)
# ══════════════════════════════════════════════════════
print("\n  Running 200k simulation...\n")

def sim(N=200000):
    random.seed(42)
    svc = [[sv(s) for s in LAYERS[li]] for li in range(5)]
    out = []
    for _ in range(N):
        rem = [list(range(s)) for s in LS]
        cl=0; tok=0; val=0; draws=0
        while cl < 5:
            it = rem[cl]
            if not it: cl+=1; continue
            d = random.choice(it); draws+=1; tok+=LC[cl]
            if d < len(svc[cl]): val += svc[cl][d]
            il=(d==min(it)); ir=(d==max(it)); o1=(len(it)==1)
            it.remove(d)
            if o1: cl+=1
            elif il: cl+=1
            elif ir and cl>0 and rem[cl-1]: cl-=1
        draws+=1; tok+=LC[5]
        cost = tok*TP
        out.append((draws, tok, cost, val))
    return out

res = sim()
N = len(res)

costs = sorted(r[2] for r in res)
vals  = sorted(r[3] for r in res)
draws = sorted(r[0] for r in res)
rois  = sorted(r[3]/r[2] for r in res)

p = lambda a,q: a[int(N*q)]
avg = lambda a: sum(a)/len(a)

print("  ┌──────────────┬────────┬────────┬────────┬────────┬────────┬────────┐")
print("  │ 指标         │ P10    │ P25    │ P50    │ P75    │ P90    │ avg    │")
print("  ├──────────────┼────────┼────────┼────────┼────────┼────────┼────────┤")
print(f"  │ 抽数         │ {p(draws,.1):>6} │ {p(draws,.25):>6} │ {p(draws,.5):>6} │ {p(draws,.75):>6} │ {p(draws,.9):>6} │ {avg(draws):>6.1f} │")
print(f"  │ 花费         │ ${p(costs,.1):>4.0f} │ ${p(costs,.25):>4.0f} │ ${p(costs,.5):>4.0f} │ ${p(costs,.75):>4.0f} │ ${p(costs,.9):>4.0f} │ ${avg(costs):>4.0f} │")
print(f"  │ 奖励价值     │ ${p(vals,.1):>4.0f} │ ${p(vals,.25):>4.0f} │ ${p(vals,.5):>4.0f} │ ${p(vals,.75):>4.0f} │ ${p(vals,.9):>4.0f} │ ${avg(vals):>4.0f} │")
print(f"  │ ROI          │ {p(rois,.1):>6.2f} │ {p(rois,.25):>6.2f} │ {p(rois,.5):>6.2f} │ {p(rois,.75):>6.2f} │ {p(rois,.9):>6.2f} │ {avg(rois):>6.2f} │")
print("  └──────────────┴────────┴────────┴────────┴────────┴────────┴────────┘")

# ── 累计体验 ──
print()
print("  逐层累计 (最顺路径: 每层直接升层):")
cc=0; cv=0
for i in range(5):
    cc += LS[i]*LC[i]*TP; cv += ltotals[i]
    print(f"    清完L{i+1}: 花费${cc:>5.0f}, 价值${cv:>6.0f}, 累计ROI={cv/cc:.2f}")
cc += LC[5]*TP
print(f"    出皮肤: 花费${cc:>5.0f} (满抽)")

# ── 单层ROI ──
print()
print("  单抽ROI:")
for i in range(5):
    c = LC[i]*TP; v = ltotals[i]/LS[i]
    print(f"    L{i+1}: ${c:.0f}/抽 → 每格${v:.0f}, ROI={v/c:.2f}")
print(f"    L6: ${LC[5]*TP:.0f}/抽 → 出皮肤")

# ── vs 老系统 ──
print()
print("  ┌────────────────┬──────────────┬──────────────┐")
print("  │                │ 老Gacha      │ 新金字塔     │")
print("  ├────────────────┼──────────────┼──────────────┤")
print(f"  │ 总奖励价值     │ $1,085       │ ${grand:>10,.0f} │")
print(f"  │ 平均花费       │ ~$665        │ ${avg(costs):>10,.0f} │")
print(f"  │ 花费范围       │ $620-$710    │ ${p(costs,.1):.0f}-${p(costs,.9):.0f}     │")
print(f"  │ ROI(满)        │ 1.77         │ {roi_full:>12.2f} │")
print(f"  │ ROI(avg)       │ 1.77         │ {avg(rois):>12.2f} │")
print(f"  │ 前$200体验     │ 5/12抽       │ ~13抽到L4    │")
print("  └────────────────┴──────────────┴──────────────┘")
print(f"\n  * 老系统所有人抽满12次=固定ROI; 新系统ROI随抽数浮动")
print(f"  * 运气差的玩家(满抽$698)拿ROI={roi_full:.2f}，比老系统更多奖励作为补偿")
