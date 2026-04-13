# -*- coding: utf-8 -*-
"""
更新合并规则v5：
1. 通行证 = 高级+初级 合为一套
2. 异族大富翁 = 所有含"异族大富翁"的都归一
3. 弹珠GACHA = 确保所有弹珠都归一（检查有没有遗漏）
4. 顺带检查还有哪些可以进一步合并
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_merge_rules_v4.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

# 读取所有7期实际出现的pack name
with open(r'C:\ADHD_agent\_tmp_hist_v4.json', 'r', encoding='utf-8') as f:
    hist = json.load(f)

all_pack_names = set()
for fest, data in hist.items():
    for p in data.get('top_packs', []):
        all_pack_names.add(p['name'])

print(f"Total unique pack names across 7 periods: {len(all_pack_names)}\n")

# ── 修改1: 通行证 = 高级+初级 合并为一套 ──
# 删除原有两个分开的规则
del rules["节日高级通行证"]
del rules["节日初级通行证"]
# 新增合并后的规则
rules["节日通行证"] = [
    "万圣节高级通行证_2025", "万圣节初级通行证_2025",
    "感恩节高级通行证_2025", "感恩节初级通行证_2025",
    "圣诞节高级通行证_2025", "圣诞节初级通行证_2025",
    "春节高级通行证_2025", "春节初级通行证_2025",
    "科技节高级通行证_2025", "科技节初级通行证_2025",
]
print("OK: 节日通行证 = 高级+初级 合并")

# ── 修改2: 异族大富翁 = 所有含"异族大富翁"的 ──
yizu_names = [n for n in all_pack_names if "异族大富翁" in n]
rules["异族大富翁"] = sorted(yizu_names)
print(f"OK: 异族大富翁 合并 {len(yizu_names)} 个: {yizu_names}")

# ── 修改3: 弹珠GACHA检查 ──
tanzu_names = [n for n in all_pack_names if "弹珠" in n]
print(f"\n弹珠相关所有pack: {tanzu_names}")
print(f"当前弹珠GACHA规则: {rules.get('弹珠GACHA', [])}")
# 确保所有弹珠都在
for tn in tanzu_names:
    if tn not in rules["弹珠GACHA"]:
        rules["弹珠GACHA"].append(tn)
        print(f"  新增: {tn}")

# ── 检查: 还有哪些含"大富翁"但不在任何规则中 ──
all_rule_members = set()
for members in rules.values():
    all_rule_members.update(members)

dafuweng_orphans = [n for n in all_pack_names if "大富翁" in n and n not in all_rule_members]
if dafuweng_orphans:
    print(f"\n大富翁未归组的: {dafuweng_orphans}")
    # 检查是非异族的
    for n in dafuweng_orphans:
        if "异族" not in n:
            rules["大富翁（非异族）"].append(n)
            print(f"  → 归入 大富翁（非异族）: {n}")

# ── 检查: 还有哪些含"通行证"或"bp/BP"但不在任何规则中 ──
all_rule_members = set()
for members in rules.values():
    all_rule_members.update(members)

bp_orphans = [n for n in all_pack_names if ("通行证" in n or "BP" in n or "bp" in n) and n not in all_rule_members]
if bp_orphans:
    print(f"\nBP/通行证未归组的:")
    for n in bp_orphans:
        print(f"  {n}")

# 保存v5
with open(r'C:\ADHD_agent\_tmp_merge_rules_v5.json', 'w', encoding='utf-8') as f:
    json.dump(rules, f, ensure_ascii=False, indent=2)

print(f"\n已保存 v5 规则，共 {len(rules)} 个合并组")
for k, v in rules.items():
    print(f"  {k}: {len(v)} 个成员")
