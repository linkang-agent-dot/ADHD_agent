# -*- coding: utf-8 -*-
"""
用v4合并规则 + 7期数据（含2月独立周期），生成子活动横向对比表
"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_hist_v4.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(r'C:\ADHD_agent\_tmp_merge_rules_v6.json', 'r', encoding='utf-8') as f:
    merge_rules = json.load(f)

with open(r'C:\ADHD_agent\_tmp_kvk_exclude.json', 'r', encoding='utf-8') as f:
    kvk_exclude = set(json.load(f))

FESTIVALS = ["万圣节", "感恩节", "圣诞节", "春节", "2月独立周期", "情人节", "科技节"]
FEST_SHORT = {"万圣节": "万", "感恩节": "感", "圣诞节": "圣", "春节": "春",
              "2月独立周期": "独", "情人节": "情", "科技节": "科"}

def classify_pack(name):
    """Return (merged_group, standalone_label) or None"""
    if name in kvk_exclude:
        return ("exclude", None)
    for group, members in merge_rules.items():
        if name in members:
            return ("merge", group)
    return None

# Build table: { activity_name -> { festival -> {"rev", "buyers"} } }
activity_data = {}

for fest in FESTIVALS:
    if fest not in data:
        continue
    for p in data[fest].get("top_packs", []):
        name = p["name"]
        rev = p["revenue"]
        buyers = p["buyers"]
        mod = p.get("module", "")
        
        result = classify_pack(name)
        if result and result[0] == "exclude":
            continue
        if result:
            _, group = result
            key = group
        else:
            key = name
        
        if key not in activity_data:
            activity_data[key] = {"module": mod, "fests": {}}
        if fest not in activity_data[key]["fests"]:
            activity_data[key]["fests"][fest] = {"rev": 0, "buyers": 0}
        activity_data[key]["fests"][fest]["rev"] += rev
        activity_data[key]["fests"][fest]["buyers"] += buyers

# Sort by total revenue
for k, v in activity_data.items():
    v["total_rev"] = sum(f["rev"] for f in v["fests"].values())
    v["fest_count"] = len(v["fests"])

sorted_acts = sorted(activity_data.items(), key=lambda x: -x[1]["total_rev"])

# Filter: keep items with total > $500 or appeared in 2+ festivals
filtered = [(k, v) for k, v in sorted_acts if v["total_rev"] > 500 or v["fest_count"] >= 2]

print(f"Total unique activities: {len(sorted_acts)}")
print(f"After filtering (>$500 or 2+ fests): {len(filtered)}")
print()

# Generate HTML table rows
html_rows = []
for i, (name, info) in enumerate(filtered):
    mod = info["module"]
    cells = [f'<td>{name}</td>', f'<td>{mod}</td>']
    
    for fest in FESTIVALS:
        fd = info["fests"].get(fest)
        if fd:
            rev_k = fd["rev"] / 1000
            cells.append(f'<td>${rev_k:.1f}K</td>')
        else:
            cells.append('<td>-</td>')
    
    total_k = info["total_rev"] / 1000
    cells.append(f'<td><strong>${total_k:.1f}K</strong></td>')
    
    row_class = ' class="alt"' if i % 2 == 1 else ''
    html_rows.append(f'<tr{row_class}>{"".join(cells)}</tr>')

# Save HTML fragment
html_content = "\n".join(html_rows)
with open(r'C:\ADHD_agent\_tmp_subact_table_v4.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Print preview
print(f"{'活动名称':30s} {'模块':8s}  " + "  ".join(f"{FEST_SHORT[f]:>5s}" for f in FESTIVALS) + "  总计")
print("-" * 120)
for name, info in filtered[:50]:
    mod = info["module"][:6]
    vals = []
    for fest in FESTIVALS:
        fd = info["fests"].get(fest)
        if fd:
            vals.append(f"${fd['rev']/1000:>6.1f}K")
        else:
            vals.append(f"{'  -':>8s}")
    total_k = info["total_rev"] / 1000
    print(f"  {name[:28]:28s} {mod:6s}  {'  '.join(vals)}  ${total_k:>7.1f}K")

# Summary by module per festival
print("\n\n===== 模块汇总 =====")
for fest in FESTIVALS:
    if fest not in data:
        continue
    d = data[fest]
    total = d["total"]
    mods = d.get("modules", {})
    print(f"\n{fest} ({d['start']}~{d['end']})  total=${total:,.0f}")
    for m, v in sorted(mods.items(), key=lambda x: -x[1]["rev"]):
        print(f"  {m:12s}  ${v['rev']:>10,.0f}  ({v['pct']}%)")

# Save full structured data for HTML generation
export = {
    "festivals": FESTIVALS,
    "activities": [
        {"name": k, "module": v["module"], "total": v["total_rev"],
         "fests": {f: {"rev": d["rev"], "buyers": d["buyers"]} 
                   for f, d in v["fests"].items()}}
        for k, v in filtered
    ],
    "modules_by_festival": {
        f: data[f]["modules"] for f in FESTIVALS if f in data
    },
    "totals_by_festival": {
        f: data[f]["total"] for f in FESTIVALS if f in data
    },
}
with open(r'C:\ADHD_agent\_tmp_subact_export_v4.json', 'w', encoding='utf-8') as f:
    json.dump(export, f, ensure_ascii=False, indent=2)

print(f"\n\nDone: {len(filtered)} activities, saved HTML + JSON")
