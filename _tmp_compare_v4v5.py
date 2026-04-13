# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('_tmp_subact_export_v4.json', 'r', encoding='utf-8') as f:
    v4 = json.load(f)
with open('_tmp_subact_export_v5.json', 'r', encoding='utf-8') as f:
    v5 = json.load(f)

print(f"v4: {len(v4['activities'])} activities, festivals={v4['festivals']}")
print(f"v5: {len(v5['activities'])} activities, festivals={v5['festivals']}")

print(f"\nv4 totals: {v4['totals_by_festival']}")
print(f"v5 totals: {v5['totals_by_festival']}")

# 按名字建索引
v4_map = {a['name']: a for a in v4['activities']}
v5_map = {a['name']: a for a in v5['activities']}

# 只在v5出现的
only_v5 = [n for n in v5_map if n not in v4_map]
only_v4 = [n for n in v4_map if n not in v5_map]

print(f"\n只在v4: {len(only_v4)}")
for n in only_v4[:10]:
    print(f"  {n}: ${v4_map[n]['total']/1000:.0f}K")
print(f"\n只在v5: {len(only_v5)}")
for n in only_v5[:10]:
    print(f"  {n}: ${v5_map[n]['total']/1000:.0f}K")

# 对比TOP10差异
print("\n=== v4 TOP20 ===")
for a in v4['activities'][:20]:
    line = f"  {a['name']:35s} ${a['total']/1000:.0f}K"
    for f in v4['festivals']:
        if f in a['fests']:
            line += f"  {f[:2]}=${a['fests'][f]['rev']/1000:.0f}K"
    print(line)

print("\n=== v5 TOP20 ===")
for a in v5['activities'][:20]:
    line = f"  {a['name']:35s} ${a['total']/1000:.0f}K"
    for f in v5['festivals']:
        if f in a['fests']:
            line += f"  {f[:2]}=${a['fests'][f]['rev']/1000:.0f}K"
    print(line)

# 对比共同活动的差异
print("\n=== 差异较大的活动 (|v5-v4| > $5K) ===")
diffs = []
for name in v4_map:
    if name in v5_map:
        diff = v5_map[name]['total'] - v4_map[name]['total']
        if abs(diff) > 5000:
            diffs.append((name, v4_map[name]['total'], v5_map[name]['total'], diff))
diffs.sort(key=lambda x: -abs(x[3]))
for name, v4t, v5t, diff in diffs[:20]:
    sign = "+" if diff > 0 else ""
    print(f"  {name:35s}  v4=${v4t/1000:.0f}K  v5=${v5t/1000:.0f}K  diff={sign}${diff/1000:.0f}K")

# 检查春节和独立周期各活动变化
print("\n=== 春节活动数据对比 ===")
for name in sorted(v4_map.keys()):
    v4f = v4_map[name]['fests']
    v5f = v5_map.get(name, {}).get('fests', {})
    v4_cny = v4f.get('春节', {}).get('rev', 0)
    v4_feb = v4f.get('2月独立周期', {}).get('rev', 0)
    v5_cny = v5f.get('春节', {}).get('rev', 0)
    v5_feb = v5f.get('2月独立周期', {}).get('rev', 0)
    if abs(v4_cny - v5_cny) > 1000 or abs(v4_feb - v5_feb) > 1000:
        print(f"  {name:35s}  春节: v4=${v4_cny/1000:.0f}K→v5=${v5_cny/1000:.0f}K  独立: v4=${v4_feb/1000:.0f}K→v5=${v5_feb/1000:.0f}K")
