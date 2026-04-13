# -*- coding: utf-8 -*-
import json

with open(r'C:\ADHD_agent\_tmp_hist_v3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

festivals = ["万圣节", "感恩节", "圣诞节", "春节", "情人节", "科技节"]

all_packs = {}
for fn in festivals:
    for p in data[fn].get('top_packs', []):
        name = p['name']
        if name not in all_packs:
            all_packs[name] = {"festivals": {}, "module": p['module']}
        all_packs[name]["festivals"][fn] = p['revenue']

sorted_packs = sorted(all_packs.items(), key=lambda x: -sum(x[1]["festivals"].values()))

lines = []
lines.append(f"total {len(sorted_packs)} unique pack names\n")
for name, info in sorted_packs:
    total = sum(info["festivals"].values())
    appears = list(info["festivals"].keys())
    mod = info["module"]
    revs = "  ".join(f"{fn}:{info['festivals'][fn]:,.0f}" for fn in festivals if fn in info["festivals"])
    lines.append(f"[{mod}] ${total:>10,.0f}  {len(appears)}p  {name}  ||  {revs}")

with open(r'C:\ADHD_agent\_tmp_all_packs.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("done")
