# -*- coding: utf-8 -*-
"""生成分组审核表markdown"""
import json

with open(r'C:\ADHD_agent\_tmp_hist_v4.json', 'r', encoding='utf-8') as f:
    hist = json.load(f)
with open(r'C:\ADHD_agent\_tmp_merge_rules_v5.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

FESTIVALS = ["万圣节", "感恩节", "圣诞节", "春节", "2月独立周期", "情人节", "科技节"]
FS = {"万圣节":"万", "感恩节":"感", "圣诞节":"圣", "春节":"春",
      "2月独立周期":"独", "情人节":"情", "科技节":"科"}

all_packs = {}
for fest in FESTIVALS:
    if fest not in hist:
        continue
    for p in hist[fest].get('top_packs', []):
        n = p['name']
        if n not in all_packs:
            all_packs[n] = {"mod": p.get("module",""), "fests": {}}
        all_packs[n]["fests"][fest] = p["revenue"]

pack_to_group = {}
for g, members in rules.items():
    for m in members:
        pack_to_group[m] = g

grouped = {}
ungrouped = []
for name, info in all_packs.items():
    total = sum(info["fests"].values())
    entry = {"name": name, "mod": info["mod"], "total": total, "fests": info["fests"]}
    if name in pack_to_group:
        g = pack_to_group[name]
        grouped.setdefault(g, []).append(entry)
    else:
        ungrouped.append(entry)

group_totals = {g: sum(e["total"] for e in entries) for g, entries in grouped.items()}
sorted_groups = sorted(grouped.items(), key=lambda x: -group_totals[x[0]])
ungrouped.sort(key=lambda x: -x["total"])

lines = []
lines.append("# 子活动合并分组审核表（v5）\n")
lines.append(f"共 **{len(all_packs)}** 个礼包 → **{len(grouped)}** 个合并组 + **{len(ungrouped)}** 个独立项\n")
lines.append("---\n")

lines.append("## 第一部分：已合并的组（%d组）\n" % len(grouped))
lines.append("> 每组在报告中显示为**1行**，组内成员收入合并计算\n")

for group, entries in sorted_groups:
    gt = group_totals[group]
    entries.sort(key=lambda x: -x["total"])
    fest_set = set()
    for e in entries:
        fest_set.update(e["fests"].keys())
    fest_marks = " ".join(FS[f] for f in FESTIVALS if f in fest_set)
    
    lines.append(f"\n### 【{group}】 ${gt/1000:.1f}K · {fest_marks}\n")
    lines.append("| 礼包名 | 收入 | 出现节日 |")
    lines.append("|---|---:|---|")
    for e in entries:
        fstr = " ".join(f"{FS[f]}${v/1000:.0f}K" for f, v in 
                        sorted(e["fests"].items(), key=lambda x: FESTIVALS.index(x[0])))
        lines.append(f"| {e['name']} | ${e['total']/1000:.1f}K | {fstr} |")

lines.append("\n---\n")
lines.append("## 第二部分：独立项（%d个）— 每项各占一行\n" % len(ungrouped))
lines.append("> 如果觉得某些应该合并，请告诉我编号\n")
lines.append("| # | 礼包名 | 收入 | 模块 | 出现节日 | 建议 |")
lines.append("|---|---|---:|---|---|---|")

for i, e in enumerate(ungrouped, 1):
    fstr = " ".join(f"{FS[f]}${v/1000:.0f}K" for f, v in
                    sorted(e["fests"].items(), key=lambda x: FESTIVALS.index(x[0])))
    suggest = ""
    n = e["name"]
    if "挖矿" in n or "挖孔" in n:
        suggest = "→ 合入【挖矿小游戏】？"
    elif "黑五" in n:
        suggest = "→ 合入【黑五系列】？"
    elif "集结奖励" in n or "集结" in n:
        suggest = "→ 合入【集结奖励】？"
    elif "砍价" in n:
        suggest = "→ 合入【砍价系列】？"
    elif "kvk" in n or "KVK" in n:
        suggest = "→ 合入【KVK系列】？"
    elif "酒馆" in n:
        suggest = "→ 合入【酒馆BP】？"
    elif "钓鱼" in n:
        suggest = "→ 合入【钓鱼系列】？"
    elif "累充" in n or "累充" in n:
        suggest = "→ 合入【累充服务器】？"
    elif "GACHA" in n or "gacha" in n:
        suggest = "→ 待归组"
    elif "bp" in n.lower():
        suggest = "→ 待归组BP"
    elif "周卡" in n:
        suggest = "→ 合入【自选周卡】？"
    elif "连锁" in n:
        suggest = "→ 待归组"
    elif "强消耗" in n:
        suggest = "→ 合入【强消耗】？"
    
    lines.append(f"| {i} | {n} | ${e['total']/1000:.1f}K | {e['mod']} | {fstr} | {suggest} |")

with open(r'C:\ADHD_agent\_tmp_merge_review.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print("Done: saved _tmp_merge_review.md")
