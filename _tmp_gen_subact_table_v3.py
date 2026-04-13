# -*- coding: utf-8 -*-
"""
用 _tmp_hist_v3.json 的 top_packs 数据生成子活动横向对比 HTML 表格
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_hist_v3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

festivals = ["万圣节", "感恩节", "圣诞节", "春节", "情人节", "科技节"]

# 收集所有子活动名称，按科技节排序
all_names = set()
for fn in festivals:
    fdata = data.get(fn, {})
    for p in fdata.get('top_packs', []):
        all_names.add(p['name'])

# 建立 name → {festival: {rev, buyers}} 的映射
name_data = {}
for fn in festivals:
    fdata = data.get(fn, {})
    for p in fdata.get('top_packs', []):
        if p['name'] not in name_data:
            name_data[p['name']] = {}
        name_data[p['name']][fn] = {
            "rev": p['revenue'],
            "buyers": p['buyers'],
            "module": p['module'],
        }

# 按科技节收入排序，科技节没有的放后面
def sort_key(name):
    d = name_data.get(name, {})
    tech = d.get("科技节", {}).get("rev", 0)
    max_rev = max((d.get(fn, {}).get("rev", 0) for fn in festivals), default=0)
    return (-tech, -max_rev)

sorted_names = sorted(name_data.keys(), key=sort_key)

# 只取收入 > $5000 的（至少在某期 > 5K）
filtered = []
for name in sorted_names:
    d = name_data[name]
    max_rev = max((d.get(fn, {}).get("rev", 0) for fn in festivals), default=0)
    if max_rev >= 5000:
        filtered.append(name)

TYPE2_CSS = {
    "节日特惠": "tag-game",
    "节日皮肤": "tag-visual",
    "节日BP": "tag-hybrid",
    "挖矿小游戏": "tag-mine",
}

rows = []
for name in filtered:
    d = name_data[name]
    # get module from most recent data
    mod = ""
    for fn in reversed(festivals):
        if fn in d:
            mod = d[fn].get("module", "")
            break
    css = TYPE2_CSS.get(mod, "tag-game")

    cells = [f'<td>{name}</td>', f'<td><span class="tag {css}">{mod}</span></td>']
    for fn in festivals:
        if fn in d:
            rev = d[fn]["rev"]
            cells.append(f'<td class="num">${rev:,.0f}</td>')
        else:
            cells.append('<td class="num" style="color:var(--text-muted)">—</td>')

    rows.append(f'        <tr>{"".join(cells)}</tr>')

html = '\n'.join(rows)
with open(r'C:\ADHD_agent\_tmp_subact_table_v3.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Generated {len(filtered)} rows")
