# -*- coding: utf-8 -*-
import random
import statistics
from collections import Counter, defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================
# Unit values (from old system)
# ==============================================================
UV = {
    'train8h':   3.63,    # 8h训练加速, 11111158
    'mechexp':   0.416,   # 机甲经验(50k), 11118004
    'core':      0.624,   # 机能核心, 11118501
    'resbox':    0.125,   # 资源宝箱10w, 11114330
    'oshards':   2.495,   # 万能橙碎, 11116304
    'spd24h':   10.89,    # 24h加速, 11111109
}

CN = {
    'train8h':  '8h训练加速',
    'mechexp':  '机甲经验(5w)',
    'core':     '机能核心',
    'resbox':   '资源宝箱10w',
    'oshards':  '万能橙碎',
    'spd24h':   '24h通用加速',
    'skin':     '机甲皮肤',
}

IDS = {
    'train8h':  11111158,
    'mechexp':  11118004,
    'core':     11118501,
    'resbox':   11114330,
    'oshards':  11116304,
    'spd24h':   11111109,
}

def sv(items):
    return sum(UV[k] * q for k, q in items)

# ==============================================================
# Curve B: 1-2-5-10-18-25 tokens/draw, $5.50/tok
# ==============================================================
LC = [1, 2, 5, 10, 18, 25]
TP = 5.50
LS = [6, 5, 4, 3, 2, 1]
MAX_TOK = sum(LS[i] * LC[i] for i in range(6))
MAX_USD = MAX_TOK * TP

# Target: full-clear ROI = 1.77 → total value = 698.5 * 1.77 = $1,236
TARGET = MAX_USD * 1.77

# ==============================================================
# 20 reward slots — trimmed to hit ROI 1.77
# ==============================================================
LAYERS = [
    # L1: 6 slots, 1tok/draw ($5.50), target ~$17/slot ≈ $102
    [
        [('train8h', 4), ('mechexp', 5)],         # $14.52+$2.08 = $16.60
        [('mechexp', 40)],                         # $16.64
        [('resbox', 100), ('core', 10)],           # $12.50+$6.24 = $18.74
        [('core', 27)],                            # $16.85
        [('train8h', 3), ('resbox', 50)],          # $10.89+$6.25 = $17.14
        [('mechexp', 25), ('core', 10)],           # $10.40+$6.24 = $16.64
    ],
    # L2: 5 slots, 2tok/draw ($11), target ~$30/slot ≈ $150
    [
        [('core', 50)],                            # $31.20
        [('train8h', 8)],                          # $29.04
        [('mechexp', 55), ('core', 12)],           # $22.88+$7.49 = $30.37
        [('resbox', 150), ('core', 16)],           # $18.75+$9.98 = $28.73
        [('core', 40), ('train8h', 2)],            # $24.96+$7.26 = $32.22
    ],
    # L3: 4 slots, 5tok/draw ($27.50), target ~$47/slot ≈ $188
    [
        [('core', 75)],                            # $46.80
        [('spd24h', 4), ('core', 5)],              # $43.56+$3.12 = $46.68
        [('core', 50), ('oshards', 5)],            # $31.20+$12.48 = $43.68
        [('core', 55), ('train8h', 3)],            # $34.32+$10.89 = $45.21
    ],
    # L4: 3 slots, 10tok/draw ($55), target ~$110/slot ≈ $330
    [
        [('core', 140), ('oshards', 10)],          # $87.36+$24.95 = $112.31
        [('core', 110), ('oshards', 14)],          # $68.64+$34.93 = $103.57
        [('core', 100), ('spd24h', 5)],            # $62.40+$54.45 = $116.85
    ],
    # L5: 2 slots, 18tok/draw ($99), target ~$225/slot ≈ $450
    [
        [('core', 230), ('oshards', 30)],          # $143.52+$74.85 = $218.37
        [('core', 250), ('oshards', 28)],          # $156.00+$69.86 = $225.86
    ],
    # L6: skin
    [
        [('skin', 1)],
    ],
]

# Compute values
print("=" * 95)
print("  金字塔机甲Gacha 奖励方案")
print(f"  层消耗: {LC} tokens/draw | Token单价: ${TP} | 满抽: {MAX_TOK}tok = ${MAX_USD:.0f}")
print("=" * 95)

layer_vals = []
grand = 0

for li in range(6):
    layer_v = 0
    for si, slot in enumerate(LAYERS[li]):
        if li == 5:
            v = 0
            desc = CN['skin']
        else:
            v = sv(slot)
            desc = " + ".join(f"{CN[k]}x{q}" for k, q in slot)
        layer_v += v
        grand += v
        cost_str = f"{LC[li]}tok(${LC[li]*TP:.0f})"
        print(f"  L{li+1}-{si+1} | {cost_str:>10} | {desc:40s} | ${v:>7.2f}")
    layer_vals.append(layer_v)
    if li < 5:
        print(f"  {'':>4} | {'':>10} | {'--- Layer ' + str(li+1) + ' total ---':40s} | ${layer_v:>7.2f}")
    print()

roi_full = grand / MAX_USD
print(f"  总奖励价值(不含皮肤): ${grand:.0f}")
print(f"  满抽花费: ${MAX_USD:.0f}")
print(f"  满抽ROI: {roi_full:.2f}")
print()

# ==============================================================
# Simulation
# ==============================================================
def sim(N=200000):
    random.seed(42)
    sv_cache = [[sv(slot) for slot in LAYERS[li]] for li in range(5)]
    results = []
    for _ in range(N):
        rem = [list(range(s)) for s in LS]
        cl = 0
        tok = 0
        val = 0
        draws = 0
        while cl < 5:
            items = rem[cl]
            if not items:
                cl += 1
                continue
            d = random.choice(items)
            draws += 1
            tok += LC[cl]
            if d < len(sv_cache[cl]):
                val += sv_cache[cl][d]
            il = (d == min(items))
            ir = (d == max(items))
            o1 = (len(items) == 1)
            items.remove(d)
            if o1:
                cl += 1
            elif il:
                cl += 1
            elif ir and cl > 0:
                if rem[cl-1]:
                    cl -= 1
        draws += 1
        tok += LC[5]
        cost = tok * TP
        results.append((draws, tok, cost, val, val/cost if cost else 0))
    return results

print("Running 200k simulation...")
res = sim(200000)
N = len(res)

draws_l = sorted([r[0] for r in res])
costs_l = sorted([r[2] for r in res])
vals_l = sorted([r[3] for r in res])
rois_l = sorted([r[4] for r in res])

p = lambda arr, q: arr[int(N*q)]

print()
print("=" * 78)
print("  模拟结果 (20万次)")
print("=" * 78)
print(f"  {'指标':>12} | {'P10':>8} | {'P25':>8} | {'P50':>8} | {'P75':>8} | {'P90':>8} | {'avg':>8}")
print(f"  {'-'*66}")
print(f"  {'抽数':>12} | {p(draws_l,.1):>8} | {p(draws_l,.25):>8} | {p(draws_l,.5):>8} | {p(draws_l,.75):>8} | {p(draws_l,.9):>8} | {statistics.mean(draws_l):>8.1f}")
print(f"  {'花费':>12} | ${p(costs_l,.1):>6.0f} | ${p(costs_l,.25):>6.0f} | ${p(costs_l,.5):>6.0f} | ${p(costs_l,.75):>6.0f} | ${p(costs_l,.9):>6.0f} | ${statistics.mean(costs_l):>6.0f}")
print(f"  {'奖励价值':>12} | ${p(vals_l,.1):>6.0f} | ${p(vals_l,.25):>6.0f} | ${p(vals_l,.5):>6.0f} | ${p(vals_l,.75):>6.0f} | ${p(vals_l,.9):>6.0f} | ${statistics.mean(vals_l):>6.0f}")
print(f"  {'ROI':>12} | {p(rois_l,.1):>8.2f} | {p(rois_l,.25):>8.2f} | {p(rois_l,.5):>8.2f} | {p(rois_l,.75):>8.2f} | {p(rois_l,.9):>8.2f} | {statistics.mean(rois_l):>8.2f}")
print()

# Per-layer ROI
print("  每层单抽ROI:")
for i in range(5):
    c = LC[i] * TP
    avg_v = layer_vals[i] / LS[i]
    print(f"    L{i+1}: 花费${c:>5.1f}/抽, 每格价值${avg_v:>6.1f}, 单抽ROI = {avg_v/c:.2f}")
print(f"    L6: 花费${LC[5]*TP:.0f}/抽 → 出皮肤")
print()

# Cumulative layer experience
print("  累计体验 (假设顺利一路升层):")
cum_cost = 0
cum_val = 0
for i in range(5):
    cum_cost += LS[i] * LC[i] * TP
    cum_val += layer_vals[i]
    cum_roi = cum_val / cum_cost
    print(f"    清完L{i+1}: 累计花费${cum_cost:>6.0f}, 累计价值${cum_val:>7.0f}, 累计ROI={cum_roi:.2f}")
cum_cost += LC[5] * TP
print(f"    出皮肤:  累计花费${cum_cost:>6.0f} (= 满抽${MAX_USD:.0f})")
print()

# Item summary
print("  道具汇总 (全20格):")
totals = defaultdict(int)
for li in range(5):
    for slot in LAYERS[li]:
        for k, q in slot:
            totals[k] += q
for k, q in sorted(totals.items(), key=lambda x: -UV.get(x[0],0)*x[1]):
    print(f"    {CN[k]:12s}: {q:>6}个, ${UV[k]*q:>7.1f}")
print(f"    {'合计':12s}:        ${grand:>7.1f}")
print()

# Old system comparison
print("=" * 78)
print("  vs 老系统对比")
print("=" * 78)
old_items = {
    'train8h':  15,    # 3+12
    'mechexp':  50,    # 50 packs
    'core':     750,   # 50+100+200+400
    'resbox':   300,
    'oshards':  150,   # 50+100
    'spd24h':   12,
}
print(f"  {'道具':12s} | {'老系统':>8} | {'新金字塔':>8} | {'变化':>8}")
print(f"  {'-'*44}")
for k in ['core', 'oshards', 'spd24h', 'train8h', 'mechexp', 'resbox']:
    old_q = old_items.get(k, 0)
    new_q = totals.get(k, 0)
    diff = new_q - old_q
    sign = "+" if diff >= 0 else ""
    print(f"  {CN[k]:12s} | {old_q:>8} | {new_q:>8} | {sign}{diff:>7}")
print()
print(f"  老系统总价值: $1,085  |  新系统总价值: ${grand:.0f}")
print(f"  老系统花费:   $614-710 |  新系统花费:   ${p(costs_l,.1):.0f}-${p(costs_l,.9):.0f}")
print(f"  老系统ROI:    1.77     |  新系统ROI(满): {roi_full:.2f} / ROI(avg): {statistics.mean(rois_l):.2f}")
