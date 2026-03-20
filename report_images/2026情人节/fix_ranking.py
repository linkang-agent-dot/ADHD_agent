import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('report_images/2026情人节/input_data.json', encoding='utf-8') as f:
    data = json.load(f)

# SKU aggregation from tab2
sku_agg = {
    '挖孔小游戏': {'sku_count': 48, 'buy_times': 9392},
    '云上探宝': {'sku_count': 28, 'buy_times': 7144},
    '机甲GACHA': {'sku_count': 8, 'buy_times': 1246},
    '节日大富翁': {'sku_count': 23, 'buy_times': 5024},
    '限时抢购': {'sku_count': 14, 'buy_times': 1354},
    '送花礼包': {'sku_count': 8, 'buy_times': 305},
    '情人节BP': {'sku_count': 14, 'buy_times': 4992},
    '通用转盘': {'sku_count': 65, 'buy_times': 2117},
    '聚宝盆': {'sku_count': 27, 'buy_times': 651},
}

for act in data['activity_ranking']:
    name = act['name']
    if name in sku_agg:
        act['buy_times'] = sku_agg[name]['buy_times']
        act['sku_count'] = sku_agg[name]['sku_count']
        if act['buy_times'] > 0:
            act['times_arppu'] = round(act['revenue'] / act['buy_times'], 2)

with open('report_images/2026情人节/input_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Verify
for a in data['activity_ranking']:
    ub = a.get('unique_buyers', 0)
    bt = a.get('buy_times', 0)
    avg = f'{bt/ub:.1f}' if ub > 0 else '-'
    print(f"{a['name']}: rev=${a['revenue']:,} | ub={ub} | bt={bt} | avg={avg}x | sku={a.get('sku_count',0)} | arppu=${a.get('times_arppu',0):.2f}")
