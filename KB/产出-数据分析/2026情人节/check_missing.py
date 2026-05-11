import json, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/linkang/gift_packs.json', encoding='utf-8') as f:
    data = json.load(f)

rows = data['values']
summary = defaultdict(lambda: {'revenue': 0, 'buy_times': 0, 'sku_count': 0})
for r in rows[1:]:
    name = r[1] if len(r) > 1 else ''
    rev = float(r[3]) if len(r) > 3 and r[3] else 0
    buyers = int(r[2]) if len(r) > 2 and r[2] else 0
    summary[name]['revenue'] += rev
    summary[name]['buy_times'] += buyers
    summary[name]['sku_count'] += 1

# Already in ranking (exact match by revenue)
existing = {
    '挖孔小游戏礼包': '挖孔小游戏',
    '云上探宝': '云上探宝',
    '机甲GACHA': '机甲GACHA',
    '节日大富翁': '节日大富翁',
    '限时抢购': '限时抢购',
    '2025情人节送花礼包': '送花礼包',
    '情人节BP': '情人节BP',
    '聚宝盆': '聚宝盆',
}

# 转盘合并
turntable_rev = 0
turntable_bt = 0
turntable_sku = 0

total_rev = 839629
total_buyers = 4496

missing = []
for name, v in sorted(summary.items(), key=lambda x: x[1]['revenue'], reverse=True):
    if name in existing:
        continue
    if '转盘' in name or name == '通用小额随机-转盘':
        turntable_rev += v['revenue']
        turntable_bt += v['buy_times']
        turntable_sku += v['sku_count']
        continue
    if '挖矿' in name:
        # merge 挖矿小游戏活动 + 挖矿小游戏
        pass  # will handle below

    missing.append({
        'name': name,
        'revenue': round(v['revenue'], 2),
        'buy_times': v['buy_times'],
        'sku_count': v['sku_count'],
        'times_arppu': round(v['revenue'] / v['buy_times'], 2) if v['buy_times'] > 0 else 0,
        'event_arpu': round(v['revenue'] / total_buyers, 2),
        'share': round(v['revenue'] / total_rev * 100, 1),
    })

# Merge 挖矿
mining = [m for m in missing if '挖矿' in m['name']]
if mining:
    merged_rev = sum(m['revenue'] for m in mining)
    merged_bt = sum(m['buy_times'] for m in mining)
    merged_sku = sum(m['sku_count'] for m in mining)
    missing = [m for m in missing if '挖矿' not in m['name']]
    missing.append({
        'name': '挖矿小游戏',
        'revenue': round(merged_rev, 2),
        'buy_times': merged_bt,
        'sku_count': merged_sku,
        'times_arppu': round(merged_rev / merged_bt, 2) if merged_bt > 0 else 0,
        'event_arpu': round(merged_rev / total_buyers, 2),
        'share': round(merged_rev / total_rev * 100, 1),
    })

# Print turntable merge info
print(f'转盘合并: +${turntable_rev:,.0f}, +{turntable_bt} buy_times, +{turntable_sku} SKUs')
print()

# Sort by revenue
missing.sort(key=lambda x: x['revenue'], reverse=True)
print(f'Missing activities ({len(missing)}):')
for m in missing:
    print(f"  {m['name']}: ${m['revenue']:,.0f} ({m['share']}%) | {m['buy_times']} times | {m['sku_count']} SKUs | ARPPU ${m['times_arppu']} | ARPU ${m['event_arpu']}")

print(f"\nTotal missing: ${sum(m['revenue'] for m in missing):,.0f}")

# Output as JSON for easy copy
print('\n=== JSON ===')
print(json.dumps(missing, ensure_ascii=False, indent=2))
