import random
import statistics
from collections import Counter

def simulate(N=200000, stage_reward_draws=0):
    """
    stage_reward_draws: how many free draws each stage reward trigger gives
    """
    random.seed(42)
    all_draws = []
    all_paid_draws = []

    for _ in range(N):
        layer_sizes = [6, 5, 4, 3, 2, 1]
        num_layers = len(layer_sizes)
        remaining = [list(range(size)) for size in layer_sizes]

        current_layer = 0
        total_draws = 0
        upgrade_count = 0
        free_draws = 0
        accumulated_upgrades_for_stage = 0

        while current_layer < num_layers - 1:
            items = remaining[current_layer]

            if not items:
                upgrade_count += 1
                accumulated_upgrades_for_stage += 1
                if accumulated_upgrades_for_stage == 4:
                    free_draws += stage_reward_draws
                    accumulated_upgrades_for_stage = 0
                current_layer += 1
                continue

            drawn = random.choice(items)
            total_draws += 1

            is_leftmost = (drawn == min(items))
            is_rightmost = (drawn == max(items))
            only_one = (len(items) == 1)

            items.remove(drawn)

            if only_one:
                upgrade_count += 1
                accumulated_upgrades_for_stage += 1
                if accumulated_upgrades_for_stage == 4:
                    free_draws += stage_reward_draws
                    accumulated_upgrades_for_stage = 0
                current_layer += 1
            elif is_leftmost:
                upgrade_count += 1
                accumulated_upgrades_for_stage += 1
                if accumulated_upgrades_for_stage == 4:
                    free_draws += stage_reward_draws
                    accumulated_upgrades_for_stage = 0
                current_layer += 1
            elif is_rightmost and current_layer > 0:
                if remaining[current_layer - 1]:
                    current_layer -= 1

        total_draws += 1  # skin
        paid_draws = max(total_draws - free_draws, 6)  # at least 6 draws (minimum path)
        all_draws.append(total_draws)
        all_paid_draws.append(paid_draws)

    return all_draws, all_paid_draws

print("=" * 80)
print("PYRAMID GACHA PRICING MODEL")
print("Structure: 6-5-4-3-2-1 (21 slots total, skin at top)")
print("=" * 80)

# Run different stage reward scenarios
for srd in [0, 1, 2, 3]:
    draws, paid = simulate(200000, stage_reward_draws=srd)
    draws_s = sorted(draws)
    paid_s = sorted(paid)
    N = len(draws)

    print(f"\n--- Stage reward = {srd} free draws (per trigger, triggers every 4 upgrades) ---")
    print(f"Total draws:  avg={statistics.mean(draws):.1f}, P50={draws_s[N//2]}, P10={draws_s[N//10]}, P90={draws_s[int(N*0.9)]}")
    print(f"Paid draws:   avg={statistics.mean(paid):.1f}, P50={paid_s[N//2]}, P10={paid_s[N//10]}, P90={paid_s[int(N*0.9)]}")
    print()

    # Find best (tokens_per_draw, token_price) combo to hit ~$600 avg
    print(f"  {'tok/draw':>8} | {'tok price':>9} | {'avg $':>7} | {'P10 $':>7} | {'P25 $':>7} | {'P50 $':>7} | {'P75 $':>7} | {'P90 $':>7}")
    print(f"  {'-'*72}")

    best_combos = []
    for tpd in [5, 6, 7, 8]:
        for tp in [5.00, 5.50, 6.00, 6.50]:
            avg_cost = statistics.mean(paid) * tpd * tp
            if 560 <= avg_cost <= 680:
                p10 = paid_s[N//10] * tpd * tp
                p25 = paid_s[N//4] * tpd * tp
                p50 = paid_s[N//2] * tpd * tp
                p75 = paid_s[int(N*0.75)] * tpd * tp
                p90 = paid_s[int(N*0.9)] * tpd * tp
                print(f"  {tpd:>8} | ${tp:.2f}/tok | ${avg_cost:>5.0f} | ${p10:>5.0f} | ${p25:>5.0f} | ${p50:>5.0f} | ${p75:>5.0f} | ${p90:>5.0f}")

print()
print("=" * 80)
print("KEY COMPARISON WITH OLD SYSTEM")
print("=" * 80)
print("Old system: 12 draws fixed, ~10% at $620, ~90% at $710, avg ~$665")
print("Old token value: ~$5.89/token, escalating consumption per draw")
print()
print("NOTE: With pyramid 6-5-4-3-2-1, avg player draws ~17/21 items (81%)")
print("      P90 player draws ALL 21 items. Variance much wider than old system.")
print("      Stage rewards help compress the cost spread and front-load value.")
