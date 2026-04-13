# -*- coding: utf-8 -*-
"""
从 _tmp_hist_subact_v2.json 自动生成子活动横向对比 HTML 表格
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_hist_subact_v2.json', encoding='utf-8') as f:
    data = json.load(f)

festivals = ['万圣节', '感恩节', '圣诞节', '春节', '情人节', '科技节']
icons = {'万圣节': '🎃', '感恩节': '🦃', '圣诞节': '🎄', '春节': '🧧', '情人节': '💝', '科技节': '🔬'}

# 子活动类型列表及模块标签
sub_configs = [
    ("挖孔小游戏", "tag-game", "小游戏"),
    ("弹珠/GACHA", "tag-visual", "外显"),
    ("推币机", "tag-game", "小游戏"),
    ("大富翁", "tag-game", "小游戏"),
    ("挖矿小游戏", "tag-game", "小游戏"),
    ("通行证/BP", "tag-hybrid", "混合"),
    ("限时特惠", "tag-hybrid", "混合"),
    ("预购连锁", "tag-hybrid", "混合"),
    ("对对碰", "tag-game", "小游戏"),
    ("行军表情/特效", "tag-visual", "外显"),
    ("其他礼包", "tag-hybrid", "混合"),
]

# 构建各子活动 × 各节日数据
def get_sub_rev(fest_name, sub_name):
    subs = data.get(fest_name, {}).get('subtypes', [])
    for s in subs:
        if s['sub'] == sub_name:
            return s['revenue'], s['share']
    return None, None

# 分析趋势
def trend_desc(sub_name):
    vals = []
    for fn in festivals:
        r, _ = get_sub_rev(fn, sub_name)
        vals.append(r)
    # 统计
    non_null = [(i, v) for i, v in enumerate(vals) if v and v > 500]
    if len(non_null) < 2:
        return "新活动/数据不足", "var(--text-muted)"
    last_v = non_null[-1][1]
    prev_v = non_null[-2][1]
    peak_v = max(v for _, v in non_null)
    peak_i = [v for _, v in non_null].index(peak_v)
    peak_fn = festivals[non_null[peak_i][0]]

    if last_v == peak_v:
        return f"↑ 科技节创新高", "var(--green)"
    elif last_v > prev_v:
        return f"↑ 环比+{(last_v/prev_v-1)*100:.0f}%，峰值{peak_fn}${peak_v/1000:.0f}K", "var(--green)"
    elif last_v / peak_v > 0.85:
        return f"→ 稳定，峰值{peak_fn}${peak_v/1000:.0f}K", "var(--text-muted)"
    else:
        chg = (last_v / prev_v - 1) * 100
        return f"↓ 环比{chg:+.0f}%，峰值{peak_fn}${peak_v/1000:.0f}K", "var(--orange)" if chg > -20 else "var(--red)"

# 找各节日各子活动的最大值（用于高亮）
def find_max(sub_name):
    best_fn, best_v = None, 0
    for fn in festivals:
        r, _ = get_sub_rev(fn, sub_name)
        if r and r > best_v:
            best_v = r
            best_fn = fn
    return best_fn

print("=== 核心对比：数据验证 ===")
for sub, _, _ in sub_configs[:8]:
    print(f"\n{sub}:")
    for fn in festivals:
        r, pct = get_sub_rev(fn, sub)
        if r:
            print(f"  {fn}: ${r:,.0f} ({pct}%)")
        else:
            print(f"  {fn}: —")

# 生成 HTML 表格
print("\n\n=== 生成 HTML ===")
rows_html = []
for sub_name, tag_class, mod in sub_configs:
    max_fn = find_max(sub_name)
    trend, trend_color = trend_desc(sub_name)
    cells = []
    for fn in festivals:
        r, pct = get_sub_rev(fn, sub_name)
        if r and r > 500:
            is_max = (fn == max_fn)
            is_tech = (fn == '科技节')
            style_parts = []
            if is_max:
                style_parts.append("color:var(--green);font-weight:700")
            elif is_tech:
                style_parts.append("color:var(--accent)")
            style = f' style="{";".join(style_parts)}"' if style_parts else ""
            bold_s = " bold" if is_tech else ""
            star = " ★" if is_max else ""
            cells.append(f'<td class="num{bold_s}"{style}>${r:,.0f}<br><span style="color:var(--text-muted);font-size:11px">{pct}%</span>{star}</td>')
        else:
            cells.append('<td class="num" style="color:var(--text-muted)">—</td>')
    td_cells = "\n          ".join(cells)
    row = f"""        <tr>
          <td><span class="tag {tag_class}">{mod}</span> {sub_name}</td>
          {td_cells}
          <td style="color:{trend_color};font-weight:600;font-size:12px">{trend}</td>
        </tr>"""
    rows_html.append(row)

full_html = "\n".join(rows_html)
# 保存到文件以便粘贴
with open(r'C:\ADHD_agent\_tmp_subact_table_rows.html', 'w', encoding='utf-8') as f:
    f.write(full_html)
print(f"HTML rows 已保存到 _tmp_subact_table_rows.html ({len(rows_html)} 行)")
