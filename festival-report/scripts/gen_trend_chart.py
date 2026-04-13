# -*- coding: utf-8 -*-
"""
生成子活动趋势分析：增长 vs 衰减
排序逻辑：
  - 影响力 = 期均收入 × |斜率/期均| （基于线性回归的标准化变化率）
  - 优先展示：基础收入高且变动大的
  - 后置展示：基础收入低的
"""
import json, sys, io, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_subact_export_v4.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

FESTIVALS = data["festivals"]
FEST_IDX = {f: i for i, f in enumerate(FESTIVALS)}

def linear_trend(points):
    """简单线性回归，返回斜率和R²"""
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
for a in data["activities"]:
    appearances = [(f, d["rev"]) for f, d in a["fests"].items()]
    if len(appearances) < 2:
        continue

    appearances.sort(key=lambda x: FEST_IDX[x[0]])

    first_rev = appearances[0][1]
    last_rev = appearances[-1][1]
    avg_rev = sum(r for _, r in appearances) / len(appearances)

    # 线性回归趋势
    slope, r2 = linear_trend(appearances)
    
    # 标准化变化率 = slope / avg_rev（每期变化占均值的比例）
    norm_change = slope / avg_rev if avg_rev > 0 else 0

    # 影响力 = 期均收入 × |标准化变化率|
    impact = avg_rev * abs(norm_change)
    
    # 方向
    direction = "up" if slope > 0 else "down"

    # sparkline 数据
    spark = []
    for f in FESTIVALS:
        if f in a["fests"]:
            spark.append(a["fests"][f]["rev"])
        else:
            spark.append(None)

    multi_period.append({
        "name": a["name"],
        "module": a["module"],
        "appearances": len(appearances),
        "avg_rev": avg_rev,
        "total_rev": a["total"],
        "first_rev": first_rev,
        "last_rev": last_rev,
        "slope": slope,
        "norm_change": norm_change,
        "r2": r2,
        "impact": impact,
        "direction": direction,
        "spark": spark,
        "fest_data": appearances,
    })

growing = [a for a in multi_period if a["direction"] == "up"]
declining = [a for a in multi_period if a["direction"] == "down"]

growing.sort(key=lambda x: -x["impact"])
declining.sort(key=lambda x: -x["impact"])

print(f"多期活动: {len(multi_period)} 个")
print(f"  增长: {len(growing)} 个")
print(f"  衰减: {len(declining)} 个")

# ────────── 生成 HTML ──────────

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
        r = "3.5" if i == 0 or i == len(points)-1 else "2.5"
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity="{opacity}"/>'
    
    return f'''<svg width="{width}" height="{height}" style="vertical-align:middle">
      <polygon points="{area_line}" fill="{color}" opacity="0.08"/>
      <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2.5" opacity="0.6" stroke-linecap="round" stroke-linejoin="round"/>
      {dots}
    </svg>'''


def gen_row(a, rank, is_growing):
    color = "#22c55e" if is_growing else "#ef4444"
    arrow = "▲" if is_growing else "▼"
    change_pct = a["norm_change"] * 100
    
    svg = spark_svg(a["spark"], color)
    fest_detail = " → ".join(f"${r/1000:.0f}K" for _, r in a["fest_data"])
    
    # 影响力指示条
    max_impact_val = max(x["impact"] for x in (growing if is_growing else declining)) if (growing if is_growing else declining) else 1
    bar_width = min(a["impact"] / max_impact_val * 60, 60) if max_impact_val > 0 else 0
    
    # R² 信号强度
    r2_str = f'{a["r2"]:.0%}' if a["r2"] >= 0.5 else f'<span style="opacity:0.4">{a["r2"]:.0%}</span>'
    
    return f'''<tr>
      <td style="color:var(--text-muted);font-size:11px;text-align:center">{rank}</td>
      <td>
        <div style="font-weight:600;margin-bottom:2px">{a["name"]}</div>
        <div style="font-size:10px;color:var(--text-muted)">{a["module"]} · {a["appearances"]}期</div>
      </td>
      <td class="num" style="font-size:14px;font-weight:600">${a["avg_rev"]/1000:.0f}K</td>
      <td class="num" style="color:{color};font-weight:700;font-size:14px">{arrow} {abs(change_pct):.0f}%</td>
      <td class="num" style="font-size:11px">{r2_str}</td>
      <td>
        <div style="width:{bar_width:.0f}px;height:6px;border-radius:3px;background:{color};opacity:0.5"></div>
      </td>
      <td>{svg}</td>
      <td style="font-size:10px;color:var(--text-muted);white-space:nowrap">{fest_detail}</td>
    </tr>'''


# ── 气泡散点图数据 ──
bubble_data = []
for a in multi_period:
    bubble_data.append({
        "name": a["name"],
        "avg_rev": round(a["avg_rev"], 0),
        "norm_change": round(a["norm_change"] * 100, 1),
        "impact": round(a["impact"], 0),
        "direction": a["direction"],
        "appearances": a["appearances"],
    })

bubble_json = json.dumps(bubble_data, ensure_ascii=False)

# ── 完整HTML Section ──

html_parts = []
html_parts.append(f'''
<!-- ══ Section 11: 子活动趋势分析 ══ -->
<div class="section">
  <div class="section-title">子活动增长 & 衰减趋势分析</div>
  <div style="margin-bottom:10px;font-size:12px;color:var(--text-muted)">
    覆盖 {len(multi_period)} 个出现 2 期以上的子活动，基于线性回归分析趋势方向和强度<br>
    <b>影响力 = 期均收入 × |标准化斜率|</b>（高收入 + 大变动 = 高影响力，优先展示）
  </div>

  <!-- 气泡散点图 -->
  <div style="margin-bottom:28px">
    <canvas id="trendBubbleChart" width="900" height="420" style="width:100%;max-width:900px;border-radius:10px;background:var(--card-bg)"></canvas>
  </div>

  <script>
  document.addEventListener('DOMContentLoaded', function() {{
    const canvas = document.getElementById('trendBubbleChart');
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const PAD = {{ left: 80, right: 30, top: 40, bottom: 50 }};
    const plotW = W - PAD.left - PAD.right;
    const plotH = H - PAD.top - PAD.bottom;

    const data = {bubble_json};

    const maxRev = Math.max(...data.map(d => d.avg_rev));
    const changes = data.map(d => d.norm_change);
    const maxChange = Math.max(Math.max(...changes.map(Math.abs)), 30);

    function xScale(v) {{ return PAD.left + (v + maxChange) / (2 * maxChange) * plotW; }}
    function yScale(v) {{ return PAD.top + plotH - (v / maxRev) * plotH; }}

    const isDark = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim().startsWith('#1');

    // 背景
    ctx.fillStyle = isDark ? '#1a1a2e' : '#fafafa';
    ctx.fillRect(0, 0, W, H);

    // 网格
    ctx.strokeStyle = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    ctx.lineWidth = 1;
    for (let r = 0; r <= maxRev; r += 50000) {{
      const y = yScale(r);
      ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(W - PAD.right, y); ctx.stroke();
      ctx.fillStyle = isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.4)';
      ctx.font = '10px system-ui';
      ctx.textAlign = 'right';
      ctx.fillText('$' + (r/1000).toFixed(0) + 'K', PAD.left - 8, y + 3);
    }}

    // 0线
    const zeroX = xScale(0);
    ctx.strokeStyle = isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.15)';
    ctx.lineWidth = 2;
    ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(zeroX, PAD.top); ctx.lineTo(zeroX, H - PAD.bottom); ctx.stroke();
    ctx.setLineDash([]);

    // 区域标签
    ctx.font = 'bold 13px system-ui';
    ctx.globalAlpha = 0.15;
    ctx.fillStyle = '#ef4444';
    ctx.textAlign = 'center';
    ctx.fillText('◀ 衰减区', PAD.left + plotW * 0.2, PAD.top + 22);
    ctx.fillStyle = '#22c55e';
    ctx.fillText('增长区 ▶', W - PAD.right - plotW * 0.2, PAD.top + 22);
    ctx.globalAlpha = 1;

    // X轴标签
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.5)';
    ctx.font = '11px system-ui';
    ctx.textAlign = 'center';
    ctx.fillText('← 衰减 (每期变化率 %) 增长 →', W / 2, H - 10);

    // Y轴标签
    ctx.save();
    ctx.translate(16, H / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('期均收入 ($)', 0, 0);
    ctx.restore();

    // 气泡
    const maxImpact = Math.max(...data.map(d => d.impact));
    data.forEach(d => {{
      const x = xScale(d.norm_change);
      const y = yScale(d.avg_rev);
      const r = Math.max(6, Math.sqrt(d.impact / maxImpact) * 28);
      const color = d.direction === 'up' ? '#22c55e' : '#ef4444';

      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.2;
      ctx.fill();
      ctx.globalAlpha = 0.7;
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.globalAlpha = 1;

      // 只给高影响力的标注名称
      if (d.impact > maxImpact * 0.08 || d.avg_rev > maxRev * 0.3) {{
        ctx.fillStyle = isDark ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.7)';
        ctx.font = '10px system-ui';
        ctx.textAlign = d.norm_change > 0 ? 'left' : 'right';
        const labelX = d.norm_change > 0 ? x + r + 4 : x - r - 4;
        ctx.fillText(d.name, labelX, y - r - 2);
      }}
    }});

    // 图例
    ctx.font = '11px system-ui';
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)';
    ctx.textAlign = 'left';
    ctx.fillText('气泡大小 = 影响力（收入 × 变化率）', PAD.left + 4, H - PAD.bottom + 30);
  }});
  </script>
''')

# 增长表格
html_parts.append(f'''
  <div style="margin-top:4px;margin-bottom:32px">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
      <span style="background:#22c55e;color:#000;font-weight:800;font-size:12px;padding:4px 14px;border-radius:6px;letter-spacing:1px">▲ 增长趋势</span>
      <span style="color:var(--text-muted);font-size:12px">{len(growing)} 个活动 · 按影响力排序</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th style="width:28px">#</th>
            <th>活动</th>
            <th class="num">期均收入</th>
            <th class="num">每期变化</th>
            <th class="num" title="线性回归R²，衡量趋势稳定性">R²</th>
            <th style="width:65px" title="影响力 = 期均收入 × |变化率|">影响力</th>
            <th style="width:210px">趋势线</th>
            <th>各期收入</th>
          </tr>
        </thead>
        <tbody>
''')

for i, a in enumerate(growing):
    html_parts.append(gen_row(a, i+1, True))

html_parts.append('''
        </tbody>
      </table>
    </div>
  </div>
''')

# 衰减表格
html_parts.append(f'''
  <div>
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
      <span style="background:#ef4444;color:#fff;font-weight:800;font-size:12px;padding:4px 14px;border-radius:6px;letter-spacing:1px">▼ 衰减趋势</span>
      <span style="color:var(--text-muted);font-size:12px">{len(declining)} 个活动 · 按影响力排序</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th style="width:28px">#</th>
            <th>活动</th>
            <th class="num">期均收入</th>
            <th class="num">每期衰减</th>
            <th class="num" title="线性回归R²，衡量趋势稳定性">R²</th>
            <th style="width:65px" title="影响力 = 期均收入 × |变化率|">影响力</th>
            <th style="width:210px">趋势线</th>
            <th>各期收入</th>
          </tr>
        </thead>
        <tbody>
''')

for i, a in enumerate(declining):
    html_parts.append(gen_row(a, i+1, False))

html_parts.append('''
        </tbody>
      </table>
    </div>
  </div>

  <!-- 分析洞察 -->
  <div class="insight-box" style="margin-top:24px">
    <div style="font-weight:700;margin-bottom:8px">趋势分析洞察</div>
''')

# 自动洞察
insights = []

# Top 增长
if growing:
    top_g = growing[0]
    insights.append(f'<b style="color:#22c55e">最强增长</b>：{top_g["name"]}（期均 ${top_g["avg_rev"]/1000:.0f}K，每期 +{top_g["norm_change"]*100:.0f}%），最新一期 ${top_g["last_rev"]/1000:.0f}K')

# Top 衰减
if declining:
    top_d = declining[0]
    insights.append(f'<b style="color:#ef4444">最大衰减</b>：{top_d["name"]}（期均 ${top_d["avg_rev"]/1000:.0f}K，每期 {top_d["norm_change"]*100:.0f}%），最新一期 ${top_d["last_rev"]/1000:.0f}K')

# 高收入稳定增长（avg_rev > 50K, R² > 0.5, growing）
stable_growers = [a for a in growing if a["avg_rev"] > 50000 and a["r2"] > 0.5]
if stable_growers:
    names = "、".join(a["name"] for a in stable_growers[:3])
    insights.append(f'<b>稳定增长（高R²）</b>：{names} — 高收入且趋势确定性强，可加大投入')

# 高收入稳定衰减
stable_decliners = [a for a in declining if a["avg_rev"] > 50000 and a["r2"] > 0.5]
if stable_decliners:
    names = "、".join(a["name"] for a in stable_decliners[:3])
    insights.append(f'<b style="color:#ef4444">稳定衰减（需关注）</b>：{names} — 高收入但持续下滑，需考虑换新或创新')

# 新星：出现2期、增长大
new_stars = [a for a in growing if a["appearances"] == 2 and a["avg_rev"] > 30000]
if new_stars:
    names = "、".join(a["name"] for a in new_stars[:3])
    insights.append(f'<b style="color:#f59e0b">潜力新星</b>：{names} — 仅2期数据但表现上升，值得持续观察')

for ins in insights:
    html_parts.append(f'    <div style="margin-bottom:6px;font-size:12px;line-height:1.7">{ins}</div>')

html_parts.append('''
  </div>
</div>
''')

trend_html = "\n".join(html_parts)

with open(r'C:\ADHD_agent\_tmp_trend_section.html', 'w', encoding='utf-8') as f:
    f.write(trend_html)

# ── 保存趋势数据供后续使用 ──
export = {
    "growing": [{
        "name": a["name"], "module": a["module"],
        "avg_rev": round(a["avg_rev"]),
        "norm_change_pct": round(a["norm_change"]*100, 1),
        "r2": round(a["r2"], 2),
        "impact": round(a["impact"]),
        "appearances": a["appearances"],
        "fest_data": a["fest_data"],
    } for a in growing],
    "declining": [{
        "name": a["name"], "module": a["module"],
        "avg_rev": round(a["avg_rev"]),
        "norm_change_pct": round(a["norm_change"]*100, 1),
        "r2": round(a["r2"], 2),
        "impact": round(a["impact"]),
        "appearances": a["appearances"],
        "fest_data": a["fest_data"],
    } for a in declining],
}

with open(r'C:\ADHD_agent\_tmp_trend_data.json', 'w', encoding='utf-8') as f:
    json.dump(export, f, ensure_ascii=False, indent=2)

# 打印预览
print("\n=== 增长（线性回归） ===")
for i, a in enumerate(growing):
    fest_str = " → ".join(f"${r/1000:.0f}K" for _, r in a["fest_data"])
    print(f"  {i+1}. {a['name']:24s}  avg=${a['avg_rev']/1000:.0f}K  slope=${a['slope']/1000:.1f}K/期  R²={a['r2']:.2f}  norm={a['norm_change']*100:+.0f}%  {fest_str}")

print(f"\n=== 衰减（线性回归） ===")
for i, a in enumerate(declining):
    fest_str = " → ".join(f"${r/1000:.0f}K" for _, r in a["fest_data"])
    print(f"  {i+1}. {a['name']:24s}  avg=${a['avg_rev']/1000:.0f}K  slope=${a['slope']/1000:.1f}K/期  R²={a['r2']:.2f}  norm={a['norm_change']*100:+.0f}%  {fest_str}")

print(f"\nDone: _tmp_trend_section.html ({len(trend_html)} chars)")
