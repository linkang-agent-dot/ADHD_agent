# -*- coding: utf-8 -*-
"""
列出所有6期里出现的礼包名称，按出现频率和总收入排序，方便找合并规则
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_hist_v3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

festivals = ["万圣节", "感恩节", "圣诞节", "春节", "情人节", "科技节"]

# name -> {festival: rev}
all_packs = {}
for fn in festivals:
    for p in data[fn].get('top_packs', []):
        name = p['name']
        if name not in all_packs:
            all_packs[name] = {"festivals": {}, "module": p['module']}
        all_packs[name]["festivals"][fn] = p['revenue']

# 按总收入排序
sorted_packs = sorted(all_packs.items(), key=lambda x: -sum(x[1]["festivals"].values()))

print(f"共 {len(sorted_packs)} 个不同的礼包名称\n")
for name, info in sorted_packs:
    total = sum(info["festivals"].values())
    appears = list(info["festivals"].keys())
    mod = info["module"]
    print(f"  [{mod:6s}] ${total:>10,.0f}  {len(appears)}期  {name}")
    for fn in festivals:
        if fn in info["festivals"]:
            rev = info["festivals"][fn]
            print(f"           {fn}: ${rev:,.0f}")
