import random
import statistics
from collections import Counter

def simulate_detailed():
    layer_sizes = [6, 5, 4, 3, 2, 1]
    num_layers = len(layer_sizes)
    remaining = [list(range(size)) for size in layer_sizes]

    current_layer = 0
    total_draws = 0
    upgrade_count = 0
    downgrade_count = 0
    draws_per_layer = [0] * num_layers

    while current_layer < num_layers - 1:
        items = remaining[current_layer]

        # Edge case: arrived at an empty layer (all items previously drawn)
        # Auto-bounce: if no items, treat as free upgrade
        if not items:
            upgrade_count += 1
            current_layer += 1
            continue

        drawn = random.choice(items)
        total_draws += 1
        draws_per_layer[current_layer] += 1

        is_leftmost = (drawn == min(items))
        is_rightmost = (drawn == max(items))
        only_one = (len(items) == 1)

        items.remove(drawn)

        if only_one:
            # Rule 5: only 1 item left = always upgrade
            upgrade_count += 1
            current_layer += 1
        elif is_leftmost:
            upgrade_count += 1
            current_layer += 1
        elif is_rightmost and current_layer > 0:
            # Downgrade: check if lower layer has items
            if remaining[current_layer - 1]:
                downgrade_count += 1
                current_layer -= 1
            # else: lower layer empty, downgrade ignored (stay)

    # Draw the skin on top layer
    total_draws += 1
    draws_per_layer[num_layers - 1] += 1

    stage_reward_triggers = upgrade_count // 4

    # Sanity check
    # net = upgrade_count - downgrade_count should equal 5
    # (some upgrades are "free bounces" from empty layers, but they still count)

    return {
        'draws': total_draws,
        'upgrades': upgrade_count,
        'downgrades': downgrade_count,
        'stage_triggers': stage_reward_triggers,
        'draws_per_layer': draws_per_layer,
    }

random.seed(42)
N = 200000
results = [simulate_detailed() for _ in range(N)]

draws = [r['draws'] for r in results]
ups = [r['upgrades'] for r in results]
downs = [r['downgrades'] for r in results]
stages = [r['stage_triggers'] for r in results]

# Verify sanity
mismatches = sum(1 for r in results if r['upgrades'] - r['downgrades'] != 5)
print(f"Sanity check: {mismatches} mismatches (expect 0)")
print()

print("=== Core Metrics ===")
print(f"Avg draws: {statistics.mean(draws):.2f}")
print(f"Median draws: {statistics.median(draws):.0f}")
print(f"Min / Max: {min(draws)} / {max(draws)}")
print(f"Avg upgrades: {statistics.mean(ups):.2f}")
print(f"Avg downgrades: {statistics.mean(downs):.2f}")
print()

print("=== Stage Reward Triggers ===")
sc = Counter(stages)
for k in sorted(sc.keys()):
    print(f"  {k} times: {sc[k]/N*100:.1f}%")
print()

print("=== Draws per Layer (avg) ===")
layer_names = [6, 5, 4, 3, 2, 1]
for i in range(6):
    layer_draws = [r['draws_per_layer'][i] for r in results]
    print(f"  Layer {i+1} ({layer_names[i]} slots): {statistics.mean(layer_draws):.2f} draws")
print()

draws_sorted = sorted(draws)
p10 = draws_sorted[int(N*0.1)]
p25 = draws_sorted[int(N*0.25)]
p50 = draws_sorted[int(N*0.5)]
p75 = draws_sorted[int(N*0.75)]
p90 = draws_sorted[int(N*0.9)]

print("=== Draw Distribution ===")
print(f"P10={p10}, P25={p25}, P50={p50}, P75={p75}, P90={p90}")
c = Counter(draws)
for d in sorted(c.keys()):
    pct = c[d]/N*100
    cumul = sum(c[dd] for dd in c if dd <= d) / N * 100
    bar = '#' * int(pct * 2)
    if pct >= 0.3:
        print(f"  {d:3d} draws: {pct:5.1f}% (cumul {cumul:5.1f}%) {bar}")
print()

# Pricing table
print("=== Pricing Scenarios (no stage rewards) ===")
print(f"{'tokens/draw':>12} | {'token avg':>10} | {'avg cost':>10} | {'P10':>8} | {'P50':>8} | {'P90':>8}")
print("-" * 72)
for tpd in [6, 7, 8, 9, 10]:
    for tp in [5.50, 6.00]:
        avg_c = statistics.mean(draws) * tpd * tp
        p10_c = p10 * tpd * tp
        p50_c = p50 * tpd * tp
        p90_c = p90 * tpd * tp
        print(f"  {tpd:>9} | ${tp:.2f}/tok | ${avg_c:>7.0f} | ${p10_c:>5.0f} | ${p50_c:>5.0f} | ${p90_c:>5.0f}")

print()
print("=== Upgrade Count Distribution ===")
uc = Counter(ups)
for k in sorted(uc.keys()):
    pct = uc[k]/N*100
    if pct >= 0.5:
        print(f"  {k} upgrades: {pct:.1f}%")
