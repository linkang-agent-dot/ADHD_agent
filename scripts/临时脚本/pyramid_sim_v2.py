import random
import statistics
from collections import Counter

def simulate(N, layer_costs, token_price, stage_reward_tokens=0):
    """
    layer_costs: [cost_L1, cost_L2, ..., cost_L6] tokens per draw on each layer
    token_price: $ per token
    stage_reward_tokens: free tokens given per stage reward trigger (every 4 upgrades)
    """
    random.seed(42)
    all_total_tokens = []
    all_paid_tokens = []
    all_draws = []
    all_draws_per_layer = []

    for _ in range(N):
        layer_sizes = [6, 5, 4, 3, 2, 1]
        num_layers = len(layer_sizes)
        remaining = [list(range(size)) for size in layer_sizes]

        current_layer = 0
        total_draws = 0
        total_tokens = 0
        upgrade_count = 0
        acc_upgrades = 0
        free_tokens = 0
        dpl = [0] * num_layers

        while current_layer < num_layers - 1:
            items = remaining[current_layer]

            if not items:
                upgrade_count += 1
                acc_upgrades += 1
                if acc_upgrades == 4:
                    free_tokens += stage_reward_tokens
                    acc_upgrades = 0
                current_layer += 1
                continue

            drawn = random.choice(items)
            total_draws += 1
            total_tokens += layer_costs[current_layer]
            dpl[current_layer] += 1

            is_leftmost = (drawn == min(items))
            is_rightmost = (drawn == max(items))
            only_one = (len(items) == 1)
            items.remove(drawn)

            if only_one:
                upgrade_count += 1
                acc_upgrades += 1
                if acc_upgrades == 4:
                    free_tokens += stage_reward_tokens
                    acc_upgrades = 0
                current_layer += 1
            elif is_leftmost:
                upgrade_count += 1
                acc_upgrades += 1
                if acc_upgrades == 4:
                    free_tokens += stage_reward_tokens
                    acc_upgrades = 0
                current_layer += 1
            elif is_rightmost and current_layer > 0:
                if remaining[current_layer - 1]:
                    current_layer -= 1

        # Skin draw on top layer
        total_draws += 1
        total_tokens += layer_costs[num_layers - 1]
        dpl[num_layers - 1] += 1

        paid_tokens = max(total_tokens - free_tokens, 0)
        all_total_tokens.append(total_tokens)
        all_paid_tokens.append(paid_tokens)
        all_draws.append(total_draws)
        all_draws_per_layer.append(dpl)

    paid_costs = [t * token_price for t in all_paid_tokens]
    total_costs = [t * token_price for t in all_total_tokens]
    return {
        'draws': all_draws,
        'total_tokens': all_total_tokens,
        'paid_tokens': all_paid_tokens,
        'paid_costs': paid_costs,
        'total_costs': total_costs,
        'draws_per_layer': all_draws_per_layer,
    }

def report(label, layer_costs, token_price, stage_tokens, N=200000):
    res = simulate(N, layer_costs, token_price, stage_tokens)
    costs = res['paid_costs']
    tokens = res['paid_tokens']
    draws = res['draws']
    costs_s = sorted(costs)
    n = len(costs)

    # Per-layer token spend
    dpl = res['draws_per_layer']
    layer_avg_draws = [statistics.mean([d[i] for d in dpl]) for i in range(6)]
    layer_avg_tokens = [layer_avg_draws[i] * layer_costs[i] for i in range(6)]

    max_tokens = sum(layer_costs[i] * [6,5,4,3,2,1][i] for i in range(6))

    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"  Layer costs: {layer_costs} tokens/draw")
    print(f"  Token price: ${token_price:.2f}")
    print(f"  Stage reward: {stage_tokens} tokens per trigger")
    print(f"  Max tokens (all 21 draws): {max_tokens} = ${max_tokens*token_price:.0f}")
    print(f"{'='*70}")
    print(f"  Avg draws: {statistics.mean(draws):.1f}")
    print(f"  Avg tokens spent: {statistics.mean(tokens):.0f}")
    print()
    print(f"  {'':>6} | {'P10':>7} | {'P25':>7} | {'P50':>7} | {'P75':>7} | {'P90':>7} | {'avg':>7}")
    print(f"  {'-'*55}")
    p = lambda q: costs_s[int(n*q)]
    print(f"  {'Cost':>6} | ${p(0.1):>5.0f} | ${p(0.25):>5.0f} | ${p(0.5):>5.0f} | ${p(0.75):>5.0f} | ${p(0.9):>5.0f} | ${statistics.mean(costs):>5.0f}")
    print()

    print(f"  Per-layer breakdown:")
    print(f"  {'Layer':>7} | {'slots':>5} | {'tok/draw':>8} | {'avg draws':>9} | {'avg tokens':>10} | {'avg $':>7} | {'% of total':>10}")
    print(f"  {'-'*72}")
    total_tok = sum(layer_avg_tokens)
    for i in range(6):
        pct = layer_avg_tokens[i] / total_tok * 100 if total_tok > 0 else 0
        print(f"  {'L'+str(i+1):>7} | {[6,5,4,3,2,1][i]:>5} | {layer_costs[i]:>8} | {layer_avg_draws[i]:>9.2f} | {layer_avg_tokens[i]:>10.1f} | ${layer_avg_tokens[i]*token_price:>5.0f} | {pct:>8.1f}%")
    print(f"  {'Total':>7} | {'21':>5} | {'':>8} | {sum(layer_avg_draws):>9.2f} | {total_tok:>10.1f} | ${total_tok*token_price:>5.0f} |")
    print()

    # Cost distribution
    c = Counter([int(round(x, -1)) for x in costs])  # round to nearest $10
    print(f"  Cost distribution (rounded to $10):")
    for bucket in sorted(c.keys()):
        pct = c[bucket]/n*100
        cumul = sum(c[b] for b in c if b <= bucket)/n*100
        if pct >= 1.0:
            bar = '#' * int(pct)
            print(f"    ${bucket:>4}: {pct:4.1f}% (cumul {cumul:5.1f}%) {bar}")


# =====================================================
# Test multiple cost curves
# =====================================================
print("OLD SYSTEM REFERENCE:")
print("  Draw costs (tokens): 1,2,4,4,6,6,10,10,18,18,18,18 = 115 total")
print("  Token value: $5.89  |  Total: $614  |  10%@$620, 90%@$710")
print()

# Curve A: Gentle (1-2-4-8-15-20)
report("A: Gentle (1-2-4-8-15-20)", [1,2,4,8,15,20], 5.50, 0)

# Curve B: Moderate (1-2-5-10-18-25)
report("B: Moderate (1-2-5-10-18-25)", [1,2,5,10,18,25], 5.50, 0)

# Curve C: Steep (1-3-6-12-20-30)
report("C: Steep (1-3-6-12-20-30)", [1,3,6,12,20,30], 5.50, 0)

# Curve D: Very steep (2-4-8-15-25-35)
report("D: Punchy (2-4-8-15-25-35)", [2,4,8,15,25,35], 5.00, 0)

# Curve E: Match old system feel (1-2-4-10-18-20)
report("E: Old-system-like (1-2-4-10-18-20)", [1,2,4,10,18,20], 5.50, 0)

# Now test with stage rewards on the best-fitting curves
# Find which curves land near $600, then add stage rewards

print("\n\n" + "="*70)
print("  WITH STAGE REWARDS (best curves near $600)")
print("="*70)

# Pick the ones close to $600 and add stage reward variants
report("B + stage 10tok", [1,2,5,10,18,25], 5.50, 10)
report("C + stage 15tok", [1,3,6,12,20,30], 5.50, 15)
report("E + stage 10tok", [1,2,4,10,18,20], 5.50, 10)
