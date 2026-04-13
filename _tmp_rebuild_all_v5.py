# -*- coding: utf-8 -*-
"""
一体化重建：用v5数据 + v6合并规则，重新生成所有子活动分析
1. 子活动横向对比表
2. 趋势分析（增长/衰减）
3. 模块趋势数据
4. 导出 subact_export_v5.json
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_hist_v5.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

with open(r'C:\ADHD_agent\_tmp_merge_rules_v6.json', 'r', encoding='utf-8') as f:
    merge_rules = json.load(f)

with open(r'C:\ADHD_agent\_tmp_kvk_exclude.json', 'r', encoding='utf-8') as f:
    kvk_exclude = set(json.load(f))

FESTIVALS = raw["festivals"]
FEST_SHORT = {"万圣节": "万", "感恩节": "感", "圣诞节": "圣", "春节": "春",
              "2月独立周期": "独", "情人节": "情", "科技节": "科"}
TYPE2_MODULE = {
    "混合-节日活动-节日特惠":   "节日特惠",
    "混合-节日活动-节日皮肤":   "节日皮肤",
    "混合-节日活动-节日BP":     "节日BP",
    "混合-节日活动-挖矿小游戏": "挖矿小游戏",
}

def classify_pack(name):
    if name in kvk_exclude:
        return ("exclude", None)
    for group, members in merge_rules.items():
        if name in members:
            return ("merge", group)
    return None

# ═══════════════════════════════════
#  Step 1: 合并子活动数据
# ═══════════════════════════════════
activity_data = {}

for fest in FESTIVALS:
    fdata = raw["data"].get(fest, {})
    for p in fdata.get("packs", []):
        name = p["name"]
        rev = p["rev"]
        buyers = p["buyers"]
        mod = TYPE2_MODULE.get(p.get("type2", ""), p.get("module", "其他"))

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
        activity_data[key]["fests"][fest]["buyers"] = max(activity_data[key]["fests"][fest]["buyers"], buyers)

# 计算总收入并排序，过滤掉总收入太低的独立活动（合并组不过滤）
MIN_TOTAL_THRESHOLD = 5000  # $5K 以下的独立活动不显示

merged_names = set()
for members in merge_rules.values():
    merged_names.update(members)

activities = []
for name, d in activity_data.items():
    total = sum(f["rev"] for f in d["fests"].values())
    # 合并组或收入达标的才保留
    is_merged = name in merge_rules or name in merged_names
    if not is_merged and total < MIN_TOTAL_THRESHOLD:
        continue
    activities.append({"name": name, "module": d["module"], "total": total, "fests": d["fests"]})

activities.sort(key=lambda x: -x["total"])

# 模块汇总
module_by_fest = {}
for fest in FESTIVALS:
    module_by_fest[fest] = {}
    fdata = raw["data"].get(fest, {})
    for mod, rev in fdata.get("modules", {}).items():
        module_by_fest[fest][mod] = rev

# 各节日总收入
totals_by_fest = {f: raw["data"].get(f, {}).get("total", 0) for f in FESTIVALS}

print(f"合并后子活动数: {len(activities)}")
print(f"节日总收入: {', '.join(f'{f}=${totals_by_fest[f]/1000:.0f}K' for f in FESTIVALS)}")

# ═══════════════════════════════════
#  Step 2: 导出 subact_export_v5.json
# ═══════════════════════════════════
export = {
    "festivals": FESTIVALS,
    "activities": activities,
    "modules_by_festival": module_by_fest,
    "totals_by_festival": totals_by_fest,
}

with open(r'C:\ADHD_agent\_tmp_subact_export_v5.json', 'w', encoding='utf-8') as f:
    json.dump(export, f, ensure_ascii=False, indent=2)
print("Saved: _tmp_subact_export_v5.json")

# ═══════════════════════════════════
#  Step 3: 生成子活动横向对比 HTML 表格
# ═══════════════════════════════════
def fmt_rev(v):
    if v >= 1000:
        return f"${v/1000:.0f}K"
    return f"${v:.0f}"

rows_html = []
for i, a in enumerate(activities):
    cols = [f'<td style="color:var(--text-muted);font-size:10px">{i+1}</td>',
            f'<td style="font-weight:600">{a["name"]}</td>',
            f'<td style="font-size:10px;color:var(--text-muted)">{a["module"]}</td>',
            f'<td class="num" style="font-weight:700">{fmt_rev(a["total"])}</td>']
    
    for f in FESTIVALS:
        if f in a["fests"]:
            rev = a["fests"][f]["rev"]
            cols.append(f'<td class="num">{fmt_rev(rev)}</td>')
        else:
            cols.append(f'<td class="num" style="color:var(--text-muted)">—</td>')
    
    appear = len(a["fests"])
    cols.append(f'<td class="num" style="font-size:10px">{appear}</td>')
    rows_html.append(f'<tr>{"".join(cols)}</tr>')

subact_table_html = "\n".join(rows_html)

with open(r'C:\ADHD_agent\_tmp_subact_table_v5.html', 'w', encoding='utf-8') as f:
    f.write(subact_table_html)
print(f"Saved: _tmp_subact_table_v5.html ({len(activities)} rows)")

# ═══════════════════════════════════
#  Step 4: 趋势分析
# ═══════════════════════════════════
FEST_IDX = {f: i for i, f in enumerate(FESTIVALS)}

def linear_trend(points):
    n = len(points)
    if n < 2:
        return 0, 0
    xs = list(range(n))
    ys = [p[1] for p in points]
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    ss_xy = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
    ss_xx = sum((xs[i] - x_mean) ** 2 for i in range(n))
    if ss_xx == 0:
        return 0, 0
    slope = ss_xy / ss_xx
    ss_yy = sum((ys[i] - y_mean) ** 2 for i in range(n))
    r2 = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy > 0 else 0
    return slope, r2

multi_period = []
for a in activities:
    appearances = [(f, d["rev"]) for f, d in a["fests"].items()]
    if len(appearances) < 2:
        continue
    appearances.sort(key=lambda x: FEST_IDX[x[0]])

    avg_rev = sum(r for _, r in appearances) / len(appearances)
    slope, r2 = linear_trend(appearances)
    norm_change = slope / avg_rev if avg_rev > 0 else 0
    impact = avg_rev * abs(norm_change)
    direction = "up" if slope > 0 else "down"

    spark = []
    for f in FESTIVALS:
        if f in a["fests"]:
            spark.append(a["fests"][f]["rev"])
        else:
            spark.append(None)

    multi_period.append({
        "name": a["name"], "module": a["module"],
        "appearances": len(appearances),
        "avg_rev": avg_rev, "total_rev": a["total"],
        "first_rev": appearances[0][1], "last_rev": appearances[-1][1],
        "slope": slope, "norm_change": norm_change, "r2": r2,
        "impact": impact, "direction": direction,
        "spark": spark, "fest_data": appearances,
    })

growing = sorted([a for a in multi_period if a["direction"] == "up"], key=lambda x: -x["impact"])
declining = sorted([a for a in multi_period if a["direction"] == "down"], key=lambda x: -x["impact"])

print(f"\n趋势分析: {len(multi_period)} 多期活动 (增长 {len(growing)}, 衰减 {len(declining)})")

# ── 趋势 HTML ──
def spark_svg(spark_data, color, width=200, height=40):
    vals = [(i, v) for i, v in enumerate(spark_data) if v is not None]
    if len(vals) < 2:
        return ""
    max_v = max(v for _, v in vals)
    min_v = min(v for _, v in vals)
    rng = max_v - min_v if max_v > min_v else 1
    points = []
    for idx, val in vals:
        x = idx / 6 * (width - 12) + 6
        y = height - 6 - (val - min_v) / rng * (height - 12)
        points.append((x, y, val))
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in points)
    area_pts = [(points[0][0], height - 2)] + [(x, y) for x, y, _ in points] + [(points[-1][0], height - 2)]
    area_line = " ".join(f"{x:.1f},{y:.1f}" for x, y in area_pts)
    dots = ""
    for i, (x, y, v) in enumerate(points):
        opacity = "1" if i == 0 or i == len(points)-1 else "0.6"
        r_val = "3.5" if i == 0 or i == len(points)-1 else "2.5"
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_val}" fill="{color}" opacity="{opacity}"/>'
    return f'''<svg width="{width}" height="{height}" style="vertical-align:middle">
      <polygon points="{area_line}" fill="{color}" opacity="0.08"/>
      <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2.5" opacity="0.6" stroke-linecap="round" stroke-linejoin="round"/>
      {dots}
    </svg>'''

def gen_trend_row(a, rank, is_growing):
    color = "#22c55e" if is_growing else "#ef4444"
    arrow = "▲" if is_growing else "▼"
    change_pct = a["norm_change"] * 100
    svg = spark_svg(a["spark"], color)
    fest_detail = " → ".join(f"${r/1000:.0f}K" for _, r in a["fest_data"])
    grp = growing if is_growing else declining
    max_impact_val = max(x["impact"] for x in grp) if grp else 1
    bar_width = min(a["impact"] / max_impact_val * 60, 60) if max_impact_val > 0 else 0
    r2_str = f'{a["r2"]:.0%}' if a["r2"] >= 0.5 else f'<span style="opacity:0.4">{a["r2"]:.0%}</span>'
    return f'''<tr>
      <td style="color:var(--text-muted);font-size:11px;text-align:center">{rank}</td>
      <td><div style="font-weight:600;margin-bottom:2px">{a["name"]}</div><div style="font-size:10px;color:var(--text-muted)">{a["module"]} · {a["appearances"]}期</div></td>
      <td class="num" style="font-size:14px;font-weight:600">${a["avg_rev"]/1000:.0f}K</td>
      <td class="num" style="color:{color};font-weight:700;font-size:14px">{arrow} {abs(change_pct):.0f}%</td>
      <td class="num" style="font-size:11px">{r2_str}</td>
      <td><div style="width:{bar_width:.0f}px;height:6px;border-radius:3px;background:{color};opacity:0.5"></div></td>
      <td>{svg}</td>
      <td style="font-size:10px;color:var(--text-muted);white-space:nowrap">{fest_detail}</td>
    </tr>'''

# 气泡图数据
bubble_data = json.dumps([{
    "name": a["name"], "avg_rev": round(a["avg_rev"]),
    "norm_change": round(a["norm_change"]*100, 1),
    "impact": round(a["impact"]), "direction": a["direction"],
} for a in multi_period], ensure_ascii=False)

trend_parts = []
trend_parts.append(f'''
<!-- ══ Section: 子活动趋势分析 ══ -->
<div class="section">
  <div class="section-title">子活动增长 & 衰减趋势分析</div>
  <div style="margin-bottom:10px;font-size:12px;color:var(--text-muted)">
    覆盖 {len(multi_period)} 个出现 2 期以上的子活动 · 基于线性回归 · <b>v5数据（修正独立周期）</b><br>
    <b>影响力 = 期均收入 × |标准化斜率|</b>
  </div>
  <canvas id="trendBubbleChart" width="900" height="420" style="width:100%;max-width:900px;border-radius:10px;background:var(--card-bg);margin-bottom:28px"></canvas>
  <script>
  document.addEventListener('DOMContentLoaded', function() {{
    const canvas = document.getElementById('trendBubbleChart');
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const PAD = {{ left: 80, right: 30, top: 40, bottom: 50 }};
    const plotW = W - PAD.left - PAD.right;
    const plotH = H - PAD.top - PAD.bottom;
    const data = {bubble_data};
    const maxRev = Math.max(...data.map(d => d.avg_rev));
    const maxChange = Math.max(Math.max(...data.map(d => Math.abs(d.norm_change))), 30);
    function xScale(v) {{ return PAD.left + (v + maxChange) / (2 * maxChange) * plotW; }}
    function yScale(v) {{ return PAD.top + plotH - (v / maxRev) * plotH; }}
    const isDark = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim().startsWith('#1');
    ctx.fillStyle = isDark ? '#1a1a2e' : '#fafafa';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    ctx.lineWidth = 1;
    for (let r = 0; r <= maxRev; r += 50000) {{
      const y = yScale(r);
      ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(W - PAD.right, y); ctx.stroke();
      ctx.fillStyle = isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.4)';
      ctx.font = '10px system-ui'; ctx.textAlign = 'right';
      ctx.fillText('$' + (r/1000).toFixed(0) + 'K', PAD.left - 8, y + 3);
    }}
    const zeroX = xScale(0);
    ctx.strokeStyle = isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.15)';
    ctx.lineWidth = 2; ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(zeroX, PAD.top); ctx.lineTo(zeroX, H - PAD.bottom); ctx.stroke();
    ctx.setLineDash([]);
    ctx.font = 'bold 13px system-ui'; ctx.globalAlpha = 0.15;
    ctx.fillStyle = '#ef4444'; ctx.textAlign = 'center';
    ctx.fillText('\\u25c0 \\u8870\\u51cf\\u533a', PAD.left + plotW * 0.2, PAD.top + 22);
    ctx.fillStyle = '#22c55e';
    ctx.fillText('\\u589e\\u957f\\u533a \\u25b6', W - PAD.right - plotW * 0.2, PAD.top + 22);
    ctx.globalAlpha = 1;
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.5)';
    ctx.font = '11px system-ui'; ctx.textAlign = 'center';
    ctx.fillText('\\u2190 \\u8870\\u51cf (\\u6bcf\\u671f\\u53d8\\u5316\\u7387 %) \\u589e\\u957f \\u2192', W / 2, H - 10);
    ctx.save(); ctx.translate(16, H / 2); ctx.rotate(-Math.PI / 2);
    ctx.fillText('\\u671f\\u5747\\u6536\\u5165 ($)', 0, 0); ctx.restore();
    const maxImpact = Math.max(...data.map(d => d.impact));
    data.forEach(d => {{
      const x = xScale(d.norm_change); const y = yScale(d.avg_rev);
      const r = Math.max(6, Math.sqrt(d.impact / maxImpact) * 28);
      const color = d.direction === 'up' ? '#22c55e' : '#ef4444';
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = color; ctx.globalAlpha = 0.2; ctx.fill();
      ctx.globalAlpha = 0.7; ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
      ctx.globalAlpha = 1;
      if (d.impact > maxImpact * 0.08 || d.avg_rev > maxRev * 0.3) {{
        ctx.fillStyle = isDark ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.7)';
        ctx.font = '10px system-ui';
        ctx.textAlign = d.norm_change > 0 ? 'left' : 'right';
        ctx.fillText(d.name, d.norm_change > 0 ? x + r + 4 : x - r - 4, y - r - 2);
      }}
    }});
    ctx.font = '11px system-ui';
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)';
    ctx.textAlign = 'left';
    ctx.fillText('\\u6c14\\u6ce1\\u5927\\u5c0f = \\u5f71\\u54cd\\u529b\\uff08\\u6536\\u5165 \\u00d7 \\u53d8\\u5316\\u7387\\uff09', PAD.left + 4, H - PAD.bottom + 30);
  }});
  </script>
''')

# 增长表
trend_parts.append(f'''
  <div style="margin-bottom:32px">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
      <span style="background:#22c55e;color:#000;font-weight:800;font-size:12px;padding:4px 14px;border-radius:6px">▲ 增长趋势</span>
      <span style="color:var(--text-muted);font-size:12px">{len(growing)} 个活动</span>
    </div>
    <div class="table-wrap"><table><thead><tr>
      <th style="width:28px">#</th><th>活动</th><th class="num">期均收入</th>
      <th class="num">每期变化</th><th class="num">R²</th><th style="width:65px">影响力</th>
      <th style="width:210px">趋势线</th><th>各期收入</th>
    </tr></thead><tbody>
''')
for i, a in enumerate(growing):
    trend_parts.append(gen_trend_row(a, i+1, True))
trend_parts.append('</tbody></table></div></div>')

# 衰减表
trend_parts.append(f'''
  <div>
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
      <span style="background:#ef4444;color:#fff;font-weight:800;font-size:12px;padding:4px 14px;border-radius:6px">▼ 衰减趋势</span>
      <span style="color:var(--text-muted);font-size:12px">{len(declining)} 个活动</span>
    </div>
    <div class="table-wrap"><table><thead><tr>
      <th style="width:28px">#</th><th>活动</th><th class="num">期均收入</th>
      <th class="num">每期衰减</th><th class="num">R²</th><th style="width:65px">影响力</th>
      <th style="width:210px">趋势线</th><th>各期收入</th>
    </tr></thead><tbody>
''')
for i, a in enumerate(declining):
    trend_parts.append(gen_trend_row(a, i+1, False))
trend_parts.append('</tbody></table></div></div>')

# 洞察
trend_parts.append('<div class="insight-box" style="margin-top:24px"><div style="font-weight:700;margin-bottom:8px">趋势分析洞察</div>')
insights = []
if growing:
    t = growing[0]
    insights.append(f'<b style="color:#22c55e">最强增长</b>：{t["name"]}（期均 ${t["avg_rev"]/1000:.0f}K，每期 +{t["norm_change"]*100:.0f}%）')
if declining:
    t = declining[0]
    insights.append(f'<b style="color:#ef4444">最大衰减</b>：{t["name"]}（期均 ${t["avg_rev"]/1000:.0f}K，每期 {t["norm_change"]*100:.0f}%）')
stable_g = [a for a in growing if a["avg_rev"] > 50000 and a["r2"] > 0.5]
if stable_g:
    insights.append(f'<b>稳定增长（高R²）</b>：{"、".join(a["name"] for a in stable_g[:3])}')
stable_d = [a for a in declining if a["avg_rev"] > 50000 and a["r2"] > 0.5]
if stable_d:
    insights.append(f'<b style="color:#ef4444">稳定衰减</b>：{"、".join(a["name"] for a in stable_d[:3])}')
for ins in insights:
    trend_parts.append(f'<div style="margin-bottom:6px;font-size:12px;line-height:1.7">{ins}</div>')
trend_parts.append('</div></div>')

trend_html = "\n".join(trend_parts)
with open(r'C:\ADHD_agent\_tmp_trend_section_v5.html', 'w', encoding='utf-8') as f:
    f.write(trend_html)
print(f"Saved: _tmp_trend_section_v5.html ({len(trend_html)} chars)")

# ═══════════════════════════════════
#  Step 5: 打印摘要
# ═══════════════════════════════════
print(f"\n=== 增长 TOP5 ===")
for a in growing[:5]:
    f_str = " → ".join(f"${r/1000:.0f}K" for _, r in a["fest_data"])
    print(f"  {a['name']:30s}  avg=${a['avg_rev']/1000:.0f}K  +{a['norm_change']*100:.0f}%  R²={a['r2']:.2f}  {f_str}")
print(f"\n=== 衰减 TOP5 ===")
for a in declining[:5]:
    f_str = " → ".join(f"${r/1000:.0f}K" for _, r in a["fest_data"])
    print(f"  {a['name']:30s}  avg=${a['avg_rev']/1000:.0f}K  {a['norm_change']*100:.0f}%  R²={a['r2']:.2f}  {f_str}")

print("\nAll done.")
