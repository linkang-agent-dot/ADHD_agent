# -*- coding: utf-8 -*-
"""
列出所有125个礼包的分组情况，输出为清晰的中文表格供用户审核
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_hist_v4.json', 'r', encoding='utf-8') as f:
    hist = json.load(f)

with open(r'C:\ADHD_agent\_tmp_merge_rules_v5.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

FESTIVALS = ["万圣节", "感恩节", "圣诞节", "春节", "2月独立周期", "情人节", "科技节"]
FEST_SHORT = {"万圣节":"万", "感恩节":"感", "圣诞节":"圣", "春节":"春",
              "2月独立周期":"独", "情人节":"情", "科技节":"科"}

# Collect all packs with their revenue per festival
all_packs = {}  # name -> {festival -> rev}
for fest in FESTIVALS:
    if fest not in hist:
        continue
    for p in hist[fest].get('top_packs', []):
        name = p['name']
        if name not in all_packs:
            all_packs[name] = {"module": p.get("module",""), "fests": {}}
        all_packs[name]["fests"][fest] = p["revenue"]

# Build reverse mapping: pack_name -> group_name
pack_to_group = {}
for group, members in rules.items():
    for m in members:
        pack_to_group[m] = group

# Categorize
grouped = {}   # group_name -> [pack_info]
ungrouped = [] # packs not in any group

for name, info in all_packs.items():
    total = sum(info["fests"].values())
    entry = {"name": name, "module": info["module"], "total": total, "fests": info["fests"]}
    
    if name in pack_to_group:
        g = pack_to_group[name]
        if g not in grouped:
            grouped[g] = []
        grouped[g].append(entry)
    else:
        ungrouped.append(entry)

# Sort groups by total revenue
group_totals = {}
for g, entries in grouped.items():
    group_totals[g] = sum(e["total"] for e in entries)

sorted_groups = sorted(grouped.items(), key=lambda x: -group_totals[x[0]])
ungrouped.sort(key=lambda x: -x["total"])

# Print
print("=" * 100)
print("  子活动合并分组审核表（v5规则）")
print("  共 %d 个礼包，%d 个合并组 + %d 个独立项" % (len(all_packs), len(grouped), len(ungrouped)))
print("=" * 100)

print("\n\n━━━ 第一部分：已设定合并规则的组（%d组）━━━\n" % len(grouped))

for group, entries in sorted_groups:
    gtotal = group_totals[group]
    entries.sort(key=lambda x: -x["total"])
    
    # 出现在哪些节日
    fest_set = set()
    for e in entries:
        fest_set.update(e["fests"].keys())
    fest_marks = " ".join(FEST_SHORT[f] for f in FESTIVALS if f in fest_set)
    
    print(f"┌─ 【{group}】 合并后总计 ${gtotal/1000:.1f}K  出现于: {fest_marks}")
    for e in entries:
        fstr = " ".join(f"{FEST_SHORT[f]}${v/1000:.0f}K" for f, v in 
                        sorted(e["fests"].items(), key=lambda x: FESTIVALS.index(x[0])))
        print(f"│   ${e['total']/1000:>7.1f}K  {e['name']:40s}  [{e['module']}]  {fstr}")
    print(f"└─ 共{len(entries)}项\n")

print("\n\n━━━ 第二部分：未归入任何合并组的独立项（%d个）━━━\n" % len(ungrouped))
print("  以下每项在报告中会各占一行。如果你觉得某些应该合并，告诉我。\n")

for i, e in enumerate(ungrouped):
    fstr = " ".join(f"{FEST_SHORT[f]}${v/1000:.0f}K" for f, v in 
                    sorted(e["fests"].items(), key=lambda x: FESTIVALS.index(x[0])))
    marker = ""
    # 标记可能需要合并的
    for kw in ["GACHA","gacha","每日","礼包","bp","BP","连锁","抢购","周卡","砍价","kvk","酒馆","钓鱼","挖矿","挖孔","对对碰","转盘","鱼鱼"]:
        if kw in e["name"]:
            marker = " ⬅ 待确认"
            break
    print(f"  {i+1:>3d}. ${e['total']/1000:>7.1f}K  {e['name']:40s}  [{e['module']}]  {fstr}{marker}")
