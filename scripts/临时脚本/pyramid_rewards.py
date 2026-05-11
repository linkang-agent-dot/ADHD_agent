import random
import statistics
from collections import Counter, defaultdict

# ==============================================================
# Unit values (from old system)
# ==============================================================
UNIT_VALUES = {
    '8h训练加速':     3.63,    # 11111158, 480 min training
    '机甲经验':       0.416,   # 11118004, per pack (50k exp)
    '机能核心':       0.624,   # 11118501
    '资源宝箱10w':    0.125,   # 11114330
    '万能橙碎':       2.495,   # 11116304
    '24h加速':       10.89,    # 11111109, 1440 min general
}

ITEM_IDS = {
    '8h训练加速':   '11111158',
    '机甲经验':     '11118004',
    '机能核心':     '11118501',
    '资源宝箱10w':  '11114330',
    '万能橙碎':     '11116304',
    '24h加速':     '11111109',
}

def slot_value(items):
    """items = [(name, qty), ...]"""
    return sum(UNIT_VALUES[name] * qty for name, qty in items)

# ==============================================================
# Layer costs (Curve B: 1-2-5-10-18-25 tokens/draw, $5.50/tok)
# ==============================================================
LAYER_COSTS_TOK = [1, 2, 5, 10, 18, 25]
TOKEN_PRICE = 5.50
LAYER_COSTS_USD = [c * TOKEN_PRICE for c in LAYER_COSTS_TOK]
LAYER_SIZES = [6, 5, 4, 3, 2, 1]

# ==============================================================
# Target: ROI ~1.77 for full-clear player
# Max cost = sum(size * cost) = 6*1+5*2+4*5+3*10+2*18+1*25 = 127 tok = $698.50
# Target total value = 698.50 * 1.77 = $1,236.3
# ==============================================================
MAX_TOKENS = sum(LAYER_SIZES[i] * LAYER_COSTS_TOK[i] for i in range(6))
MAX_COST = MAX_TOKENS * TOKEN_PRICE
TARGET_TOTAL = MAX_COST * 1.77
print(f"Max tokens: {MAX_TOKENS}, Max cost: ${MAX_COST:.0f}")
print(f"Target total reward value: ${TARGET_TOTAL:.0f} (ROI=1.77)")
print()

# ==============================================================
# Design 20 reward slots (L6 = skin, not counted)
# Target per-layer values that hit $1,236 total
# ==============================================================

# Layer 1: 6 slots x ~$17 = ~$102
L1_SLOTS = [
    [('8h训练加速', 4), ('机甲经验', 5)],              # $14.52+$2.08 = $16.60
    [('机甲经验', 40)],                                # $16.64
    [('资源宝箱10w', 100), ('机能核心', 10)],           # $12.50+$6.24 = $18.74
    [('机能核心', 27)],                                # $16.85
    [('8h训练加速', 3), ('资源宝箱10w', 50)],           # $10.89+$6.25 = $17.14
    [('机甲经验', 25), ('机能核心', 10)],               # $10.40+$6.24 = $16.64
]

# Layer 2: 5 slots x ~$30 = ~$150
L2_SLOTS = [
    [('机能核心', 50)],                                # $31.20
    [('8h训练加速', 8)],                               # $29.04
    [('机甲经验', 55), ('机能核心', 12)],               # $22.88+$7.49 = $30.37
    [('资源宝箱10w', 150), ('机能核心', 16)],           # $18.75+$9.98 = $28.73
    [('机能核心', 40), ('8h训练加速', 2)],              # $24.96+$7.26 = $32.22
]

# Layer 3: 4 slots x ~$48 = ~$192
L3_SLOTS = [
    [('机能核心', 75)],                                # $46.80
    [('24h加速', 4), ('机能核心', 5)],                  # $43.56+$3.12 = $46.68
    [('机能核心', 55), ('万能橙碎', 6)],                # $34.32+$14.97 = $49.29
    [('机能核心', 60), ('8h训练加速', 3)],              # $37.44+$10.89 = $48.33
]

# Layer 4: 3 slots x ~$120 = ~$360
L4_SLOTS = [
    [('机能核心', 150), ('万能橙碎', 10)],              # $93.60+$24.95 = $118.55
    [('机能核心', 120), ('万能橙碎', 15)],              # $74.88+$37.43 = $112.31
    [('机能核心', 100), ('24h加速', 5)],                # $62.40+$54.45 = $116.85
]

# Layer 5: 2 slots x ~$250 = ~$500
L5_SLOTS = [
    [('机能核心', 250), ('万能橙碎', 35)],              # $156.00+$87.33 = $243.33
    [('机能核心', 280), ('万能橙碎', 30)],              # $174.72+$74.85 = $249.57
]

# Layer 6: skin (no value counted for ROI)
L6_SLOTS = [
    [('机甲皮肤', 1)],
]

ALL_LAYERS = [L1_SLOTS, L2_SLOTS, L3_SLOTS, L4_SLOTS, L5_SLOTS, L6_SLOTS]

# ==============================================================
# Validate values
# ==============================================================
print("=" * 90)
print(f"{'Layer':>5} | {'Slot':>4} | {'Cost/draw':>9} | {'Rewards':40s} | {'Value':>8}")
print("-" * 90)

layer_totals = []
grand_total = 0

for li, (layer_slots, size, cost_tok) in enumerate(zip(ALL_LAYERS, LAYER_SIZES, LAYER_COSTS_TOK)):
    layer_total = 0
    for si, slot_items in enumerate(layer_slots):
        if li == 5:  # skin layer
            val = 0
            desc = "机甲皮肤"
        else:
            val = slot_value(slot_items)
            desc = " + ".join(f"{name}x{qty}" for name, qty in slot_items)
        layer_total += val
        grand_total += val
        cost_usd = cost_tok * TOKEN_PRICE
        print(f"  L{li+1} | {si+1:>4} | {cost_tok}tok(${cost_usd:.0f}) | {desc:40s} | ${val:>7.2f}")
    layer_totals.append(layer_total)
    print(f"  {'':>4} | {'':>4} | {'':>9} | {'Layer total:':40s} | ${layer_total:>7.2f}")
    print("-" * 90)

print(f"  {'':>4} | {'':>4} | {'':>9} | {'GRAND TOTAL (excl skin):':40s} | ${grand_total:>7.2f}")
print(f"  ROI (full clear): ${grand_total:.0f} / ${MAX_COST:.0f} = {grand_total/MAX_COST:.2f}")
print()

# ==============================================================
# Run simulation with actual reward tracking
# ==============================================================
def simulate_full(N=200000):
    random.seed(42)
    all_data = []

    # Pre-compute slot values per layer (excluding skin)
    slot_vals = []
    for li in range(5):
        layer_vals = [slot_value(items) for items in ALL_LAYERS[li]]
        slot_vals.append(layer_vals)

    for _ in range(N):
        remaining = [list(range(size)) for size in LAYER_SIZES]
        current_layer = 0
        total_tokens = 0
        total_value = 0
        total_draws = 0
        tokens_at_200 = None  # track when player hits ~$200

        while current_layer < 5:  # layers 0-4 are reward layers
            items = remaining[current_layer]
            if not items:
                current_layer += 1
                continue

            drawn = random.choice(items)
            total_draws += 1
            total_tokens += LAYER_COSTS_TOK[current_layer]

            # Track reward value
            slot_idx = drawn  # position = slot index within this layer
            if slot_idx < len(slot_vals[current_layer]):
                total_value += slot_vals[current_layer][slot_idx]

            is_leftmost = (drawn == min(items))
            is_rightmost = (drawn == max(items))
            only_one = (len(items) == 1)
            items.remove(drawn)

            # Check $200 milestone
            if tokens_at_200 is None and total_tokens * TOKEN_PRICE >= 200:
                tokens_at_200 = (total_tokens, total_value, current_layer + 1, total_draws)

            if only_one:
                current_layer += 1
            elif is_leftmost:
                current_layer += 1
            elif is_rightmost and current_layer > 0:
                if remaining[current_layer - 1]:
                    current_layer -= 1

        # Skin draw
        total_draws += 1
        total_tokens += LAYER_COSTS_TOK[5]

        cost = total_tokens * TOKEN_PRICE
        roi = total_value / cost if cost > 0 else 0

        all_data.append({
            'draws': total_draws,
            'tokens': total_tokens,
            'cost': cost,
            'value': total_value,
            'roi': roi,
            'at_200': tokens_at_200,
        })

    return all_data

print("Running simulation (200k runs)...")
data = simulate_full(200000)

costs = sorted([d['cost'] for d in data])
rois = sorted([d['roi'] for d in data])
values = sorted([d['value'] for d in data])
draws = sorted([d['draws'] for d in data])
N = len(data)

print()
print("=" * 70)
print("SIMULATION RESULTS")
print("=" * 70)
print(f"{'':>15} | {'P10':>8} | {'P25':>8} | {'P50':>8} | {'P75':>8} | {'P90':>8} | {'avg':>8}")
print("-" * 70)
p = lambda arr, q: arr[int(N*q)]
print(f"  {'Draws':>13} | {p(draws,0.1):>8} | {p(draws,0.25):>8} | {p(draws,0.5):>8} | {p(draws,0.75):>8} | {p(draws,0.9):>8} | {statistics.mean([d['draws'] for d in data]):>8.1f}")
print(f"  {'Cost':>13} | ${p(costs,0.1):>6.0f} | ${p(costs,0.25):>6.0f} | ${p(costs,0.5):>6.0f} | ${p(costs,0.75):>6.0f} | ${p(costs,0.9):>6.0f} | ${statistics.mean(costs):>6.0f}")
print(f"  {'Reward Value':>13} | ${p(values,0.1):>6.0f} | ${p(values,0.25):>6.0f} | ${p(values,0.5):>6.0f} | ${p(values,0.75):>6.0f} | ${p(values,0.9):>6.0f} | ${statistics.mean(values):>6.0f}")
print(f"  {'ROI':>13} | {p(rois,0.1):>8.2f} | {p(rois,0.25):>8.2f} | {p(rois,0.5):>8.2f} | {p(rois,0.75):>8.2f} | {p(rois,0.9):>8.2f} | {statistics.mean([d['roi'] for d in data]):>8.2f}")
print()

# $200 milestone analysis
at_200_data = [d['at_200'] for d in data if d['at_200']]
if at_200_data:
    print("=== $200 Milestone (front-loaded experience) ===")
    layers_at_200 = [d[2] for d in at_200_data]
    draws_at_200 = [d[3] for d in at_200_data]
    values_at_200 = [d[1] for d in at_200_data]
    print(f"  Avg layer reached: {statistics.mean(layers_at_200):.1f}")
    print(f"  Avg draws done: {statistics.mean(draws_at_200):.1f}")
    print(f"  Avg reward value: ${statistics.mean(values_at_200):.0f}")
    print(f"  Avg ROI at $200: {statistics.mean(values_at_200)/200:.2f}")
    lc = Counter(layers_at_200)
    print(f"  Layer distribution at $200:")
    for k in sorted(lc.keys()):
        print(f"    On Layer {k}: {lc[k]/len(at_200_data)*100:.1f}%")
print()

# Compare with old system
print("=" * 70)
print("COMPARISON WITH OLD SYSTEM")
print("=" * 70)
print(f"  {'':>20} | {'Old Gacha':>12} | {'New Pyramid':>12}")
print(f"  {'-'*48}")
print(f"  {'Total reward value':>20} | ${'1,085':>11} | ${statistics.mean(values):>10.0f}*")
print(f"  {'Avg cost':>20} | ${'665':>11} | ${statistics.mean(costs):>10.0f}")
print(f"  {'ROI (avg player)':>20} | {'1.77':>12} | {statistics.mean([d['roi'] for d in data]):>12.2f}")
print(f"  {'ROI (full clear)':>20} | {'1.77':>12} | {sum(layer_totals)/MAX_COST:>12.2f}")
print(f"  {'Cost range':>20} | {'$620-$710':>12} | ${p(costs,0.1):.0f}-${p(costs,0.9):.0f}")
print(f"  * avg player gets ~80% of all slot values")
print()

# Per-layer ROI
print("=== Per-Layer ROI ===")
for i in range(5):
    cost_per_draw = LAYER_COSTS_TOK[i] * TOKEN_PRICE
    avg_val = layer_totals[i] / LAYER_SIZES[i]
    roi = avg_val / cost_per_draw
    print(f"  L{i+1}: draw cost ${cost_per_draw:>5.1f}, avg slot value ${avg_val:>6.1f}, ROI per draw = {roi:.2f}")
print()

# Item totals across all 20 slots
print("=== Total Item Quantities (all 20 reward slots) ===")
item_totals = defaultdict(int)
for li in range(5):
    for slot_items in ALL_LAYERS[li]:
        for name, qty in slot_items:
            item_totals[name] += qty

for name, qty in sorted(item_totals.items(), key=lambda x: -UNIT_VALUES.get(x[0], 0) * x[1]):
    uv = UNIT_VALUES.get(name, 0)
    total_v = uv * qty
    print(f"  {name:12s}: {qty:>6} (${total_v:>7.1f})")
print(f"  {'TOTAL':12s}: {'':>6}  ${grand_total:>7.1f}")
