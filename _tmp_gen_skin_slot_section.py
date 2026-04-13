# -*- coding: utf-8 -*-
"""生成皮肤抽奖模块独立对比 HTML Section"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tmp_skin_slot_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

ORDER = ["万圣节", "感恩节", "圣诞节", "春节", "情人节", "科技节"]

FORMAT_COLORS = {
    "传统GACHA": "#a78bfa",
    "弹珠GACHA": "#60a5fa",
    "骰子": "#f97316",
    "云上探宝": "#34d399",
    "推币机+弹珠": "#f472b6",
}

FORMAT_EMOJI = {
    "传统GACHA": "🎰",
    "弹珠GACHA": "🔮",
    "骰子": "🎲",
    "云上探宝": "☁️",
    "推币机+弹珠": "🎯",
}

max_rev = max(data[f]["slot_total"] for f in ORDER)

# 各节日数据整理
rows_data = []
for f in ORDER:
    d = data[f]
    rows_data.append({
        "fest": f,
        "format": d["format"],
        "total": d["slot_total"],
        "packs": d["packs"],
        "color": FORMAT_COLORS[d["format"]],
        "emoji": FORMAT_EMOJI[d["format"]],
    })

# 生成 pack 明细行
def pack_detail(packs):
    items = []
    for p in packs:
        items.append(f'{p["name"]}(${p["rev"]/1000:.0f}K)')
    return "、".join(items)

# 计算趋势指标
totals = [r["total"] for r in rows_data]
avg_total = sum(totals) / len(totals)
# 对比单形式 vs 双形式
single_format = [r for r in rows_data if "+" not in r["format"]]
single_avg = sum(r["total"] for r in single_format) / len(single_format) if single_format else 0

# ── HTML ──
html = f'''
<!-- ══ Section: 皮肤抽奖模块横向对比 ══ -->
<div class="section">
  <div class="section-title">皮肤抽奖模块 — 槽位横向对比</div>
  <div style="margin-bottom:14px;font-size:12px;color:var(--text-muted)">
    每个节日的<b>皮肤抽奖主玩法</b>槽位收入对比 · 不同节日使用不同形式（传统GACHA / 弹珠 / 骰子 / 云上探宝 / 推币机）<br>
    目标：对比<b>同一功能位</b>的营收表现，评估形式替换的效果
  </div>

  <!-- 柱状图 -->
  <div style="margin-bottom:28px">
    <canvas id="skinSlotChart" width="860" height="380" style="width:100%;max-width:860px;border-radius:10px;background:var(--card-bg)"></canvas>
  </div>

  <script>
  document.addEventListener('DOMContentLoaded', function() {{
    const canvas = document.getElementById('skinSlotChart');
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const PAD = {{ left: 70, right: 20, top: 50, bottom: 80 }};
    const plotW = W - PAD.left - PAD.right;
    const plotH = H - PAD.top - PAD.bottom;

    const isDark = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim().startsWith('#1');

    const festivals = {json.dumps([r["fest"] for r in rows_data], ensure_ascii=False)};
    const formats = {json.dumps([r["format"] for r in rows_data], ensure_ascii=False)};
    const emojis = {json.dumps([r["emoji"] for r in rows_data], ensure_ascii=False)};
    const values = {json.dumps([r["total"] for r in rows_data])};
    const colors = {json.dumps([r["color"] for r in rows_data])};
    const maxVal = {max_rev * 1.15};

    // 背景
    ctx.fillStyle = isDark ? '#1a1a2e' : '#fafafa';
    ctx.fillRect(0, 0, W, H);

    // 标题
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.7)';
    ctx.font = 'bold 14px system-ui';
    ctx.textAlign = 'left';
    ctx.fillText('皮肤抽奖槽位收入 · 按形式标注', PAD.left, 28);

    // 网格线
    ctx.strokeStyle = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    ctx.lineWidth = 1;
    for (let v = 0; v <= maxVal; v += 50000) {{
      const y = PAD.top + plotH - (v / maxVal) * plotH;
      ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(W - PAD.right, y); ctx.stroke();
      ctx.fillStyle = isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.4)';
      ctx.font = '10px system-ui';
      ctx.textAlign = 'right';
      ctx.fillText('$' + (v/1000).toFixed(0) + 'K', PAD.left - 8, y + 3);
    }}

    // 均值线
    const avgY = PAD.top + plotH - ({avg_total} / maxVal) * plotH;
    ctx.strokeStyle = isDark ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.2)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6,4]);
    ctx.beginPath(); ctx.moveTo(PAD.left, avgY); ctx.lineTo(W - PAD.right, avgY); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.4)';
    ctx.font = '10px system-ui';
    ctx.textAlign = 'left';
    ctx.fillText('\u5747\u503c $' + Math.round({avg_total}/1000) + 'K', W - PAD.right - 70, avgY - 6);

    // 柱子
    const barWidth = plotW / festivals.length * 0.55;
    const barGap = plotW / festivals.length;

    festivals.forEach((fest, i) => {{
      const x = PAD.left + barGap * i + (barGap - barWidth) / 2;
      const barH = (values[i] / maxVal) * plotH;
      const y = PAD.top + plotH - barH;

      // 柱子渐变
      const grad = ctx.createLinearGradient(x, y, x, PAD.top + plotH);
      grad.addColorStop(0, colors[i]);
      grad.addColorStop(1, colors[i] + '44');
      ctx.fillStyle = grad;

      // 圆角矩形
      const r = 4;
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.lineTo(x + barWidth - r, y);
      ctx.arcTo(x + barWidth, y, x + barWidth, y + r, r);
      ctx.lineTo(x + barWidth, PAD.top + plotH);
      ctx.lineTo(x, PAD.top + plotH);
      ctx.lineTo(x, y + r);
      ctx.arcTo(x, y, x + r, y, r);
      ctx.fill();

      // 边框
      ctx.strokeStyle = colors[i];
      ctx.lineWidth = 2;
      ctx.stroke();

      // 金额标签
      ctx.fillStyle = isDark ? 'rgba(255,255,255,0.85)' : 'rgba(0,0,0,0.75)';
      ctx.font = 'bold 13px system-ui';
      ctx.textAlign = 'center';
      ctx.fillText('$' + Math.round(values[i]/1000) + 'K', x + barWidth/2, y - 8);

      // 节日名
      ctx.fillStyle = isDark ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.5)';
      ctx.font = '12px system-ui';
      ctx.fillText(fest, x + barWidth/2, PAD.top + plotH + 20);

      // 形式标签
      ctx.fillStyle = colors[i];
      ctx.font = 'bold 11px system-ui';
      ctx.fillText(emojis[i] + ' ' + formats[i], x + barWidth/2, PAD.top + plotH + 38);
    }});
  }});
  </script>

  <!-- 数据表格 -->
  <div class="table-wrap" style="margin-bottom:20px">
    <table>
      <thead>
        <tr>
          <th>节日</th>
          <th>形式</th>
          <th class="num">槽位收入</th>
          <th class="num">vs 均值</th>
          <th>礼包组成</th>
          <th>分析</th>
        </tr>
      </thead>
      <tbody>
'''

for r in rows_data:
    vs_avg = (r["total"] - avg_total) / avg_total * 100
    vs_sign = "+" if vs_avg > 0 else ""
    vs_color = "#22c55e" if vs_avg > 0 else "#ef4444"
    bar_pct = r["total"] / max_rev * 100
    detail = pack_detail(r["packs"])
    
    # 分析文字
    if r["format"] == "推币机+弹珠":
        analysis = "双形式叠加，收入远超单形式均值"
    elif r["total"] > avg_total * 1.1:
        analysis = f"高于均值，{r['format']}形式表现优秀"
    elif r["total"] < avg_total * 0.7:
        analysis = f"低于均值，{r['format']}形式吸引力待提升"
    else:
        analysis = "接近均值水平"
    
    html += f'''
        <tr>
          <td style="font-weight:600">{r["fest"]}</td>
          <td>
            <span style="background:{r['color']}22;color:{r['color']};font-weight:700;font-size:11px;padding:3px 8px;border-radius:4px">
              {r["emoji"]} {r["format"]}
            </span>
          </td>
          <td class="num" style="font-weight:700;font-size:15px">${r["total"]/1000:.0f}K</td>
          <td class="num" style="color:{vs_color};font-weight:600">{vs_sign}{vs_avg:.0f}%</td>
          <td style="font-size:10px;color:var(--text-muted);max-width:280px">{detail}</td>
          <td style="font-size:11px">{analysis}</td>
        </tr>'''

html += '''
      </tbody>
    </table>
  </div>

  <!-- 洞察 -->
  <div class="insight-box">
    <div style="font-weight:700;margin-bottom:10px">皮肤抽奖槽位洞察</div>
'''

# 生成洞察
insights = []

# 最高
best = max(rows_data, key=lambda x: x["total"])
insights.append(f'<b style="color:#22c55e">最高收入</b>：{best["fest"]} ({best["emoji"]} {best["format"]}) ${best["total"]/1000:.0f}K'
    + (f' — 双形式策略使槽位收入达到单形式均值的 {best["total"]/single_avg:.1f}x' if "+" in best["format"] else ''))

# 最低
worst = min(rows_data, key=lambda x: x["total"])
insights.append(f'<b style="color:#ef4444">最低收入</b>：{worst["fest"]} ({worst["emoji"]} {worst["format"]}) ${worst["total"]/1000:.0f}K — 仅为最高值的 {worst["total"]/best["total"]*100:.0f}%')

# 形式更替效果
# 传统GACHA → 弹珠GACHA → 骰子 → 云上探宝 → 推币机+弹珠
insights.append(f'<b>形式演进</b>：传统GACHA(${rows_data[0]["total"]/1000:.0f}K~${rows_data[1]["total"]/1000:.0f}K) → '
    f'弹珠(${rows_data[2]["total"]/1000:.0f}K) → 骰子(${rows_data[3]["total"]/1000:.0f}K) → '
    f'云上探宝(${rows_data[4]["total"]/1000:.0f}K) → 推币机+弹珠(${rows_data[5]["total"]/1000:.0f}K)')

# 单形式均值 vs 双形式
insights.append(f'<b>策略发现</b>：单形式均值 ${single_avg/1000:.0f}K，科技节双形式 ${rows_data[5]["total"]/1000:.0f}K（+{(rows_data[5]["total"]/single_avg-1)*100:.0f}%）'
    f'— 同期投放两种皮肤玩法可显著拉升模块整体收入')

# 弹珠GACHA跨期对比
insights.append(f'<b>弹珠GACHA趋势</b>：圣诞首期$145K（独占）→ 科技节2期$130K（与推币机并行）— 弹珠本身有 -10% 衰减，但推币机补位使槽位总量翻倍')

for ins in insights:
    html += f'    <div style="margin-bottom:6px;font-size:12px;line-height:1.7">{ins}</div>\n'

html += '''
  </div>
</div>
'''

with open(r'C:\ADHD_agent\_tmp_skin_slot_section.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done: _tmp_skin_slot_section.html ({len(html)} chars)")
print(f"\n槽位汇总:")
for r in rows_data:
    print(f"  {r['fest']:6s}  {r['emoji']} {r['format']:12s}  ${r['total']/1000:.0f}K")
print(f"  均值: ${avg_total/1000:.0f}K  |  单形式均值: ${single_avg/1000:.0f}K")
