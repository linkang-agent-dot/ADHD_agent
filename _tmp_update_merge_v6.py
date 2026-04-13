# -*- coding: utf-8 -*-
"""
v6 合并规则：根据用户反馈更新
"""
import json

with open(r'C:\ADHD_agent\_tmp_merge_rules_v5.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

with open(r'C:\ADHD_agent\_tmp_hist_v4.json', 'r', encoding='utf-8') as f:
    hist = json.load(f)

all_names = set()
for fest, data in hist.items():
    for p in data.get('top_packs', []):
        all_names.add(p['name'])

# ── 1. 挖矿小游戏（不含挖孔）──
rules["挖矿小游戏"] = [n for n in all_names if "挖矿" in n]
print(f"挖矿小游戏: {rules['挖矿小游戏']}")

# ── 2. 集结 → 归入节日通行证 ──
jiejie = [n for n in all_names if "集结" in n]
rules["节日通行证"].extend(jiejie)
print(f"集结归入通行证: {jiejie}")

# ── 3. KVK 排除列表（不合并，直接过滤掉）──
kvk_names = [n for n in all_names if "kvk" in n.lower() or "KVK" in n]
print(f"KVK 排除: {kvk_names}")

# ── 4. 砍价系列 ──
rules["砍价系列"] = [n for n in all_names if "砍价" in n]
print(f"砍价系列: {rules['砍价系列']}")

# ── 5. 一番赏 ──
rules["一番赏"] = [n for n in all_names if "一番赏" in n]
print(f"一番赏: {rules['一番赏']}")

# ── 6. 钓鱼系列 ──
rules["钓鱼系列"] = [n for n in all_names if "钓鱼" in n]
print(f"钓鱼系列: {rules['钓鱼系列']}")

# ── 7. 强消耗 ──
rules["强消耗"] = [n for n in all_names if "强消耗" in n]
print(f"强消耗: {rules['强消耗']}")

# ── 8. 累充服务器 ──
rules["累充服务器"] = [n for n in all_names if "累充服务器" in n]
print(f"累充服务器: {rules['累充服务器']}")

# ── 9. 自选周卡补漏 ──
for n in all_names:
    if "自选周卡" in n or "周卡" in n:
        if n not in rules["自选周卡"]:
            rules["自选周卡"].append(n)
            print(f"自选周卡补漏: {n}")

# ── 10. 周年庆返场补漏（S3-5） ──
for n in all_names:
    if "周年庆" in n and "返场" in n and n not in rules["周年庆返场"]:
        rules["周年庆返场"].append(n)
        print(f"周年庆返场补漏: {n}")

# 保存
with open(r'C:\ADHD_agent\_tmp_merge_rules_v6.json', 'w', encoding='utf-8') as f:
    json.dump(rules, f, ensure_ascii=False, indent=2)

# 同时保存KVK排除列表
with open(r'C:\ADHD_agent\_tmp_kvk_exclude.json', 'w', encoding='utf-8') as f:
    json.dump(kvk_names, f, ensure_ascii=False, indent=2)

print(f"\n共 {len(rules)} 个合并组，{len(kvk_names)} 个排除项")
for k, v in sorted(rules.items(), key=lambda x: -len(x[1])):
    print(f"  {k}: {len(v)}项")
