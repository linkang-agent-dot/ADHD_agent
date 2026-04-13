# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_subact_export_v4.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== 所有含关键词的活动（检查是否需要进一步合并）===\n")

groups = {
    "弹珠/GACHA相关": ["弹珠", "GACHA", "gacha"],
    "通行证/BP相关": ["通行证", "BP", "bp"],
    "异族大富翁相关": ["异族大富翁"],
    "大富翁相关": ["大富翁"],
}

for group_name, keywords in groups.items():
    print(f"\n{'='*60}")
    print(f"  {group_name}")
    print(f"{'='*60}")
    matches = []
    for a in data['activities']:
        n = a['name']
        if any(kw in n for kw in keywords):
            fests = {k: v['rev'] for k, v in a['fests'].items()}
            matches.append((n, a['total'], a['module'], fests))
    
    matches.sort(key=lambda x: -x[1])
    for name, total, mod, fests in matches:
        fest_str = "  ".join(f"{k[:2]}:${v/1000:.0f}K" for k, v in fests.items())
        print(f"  ${total/1000:>7.1f}K  {name:35s}  [{mod}]  {fest_str}")
