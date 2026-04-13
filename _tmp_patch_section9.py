# -*- coding: utf-8 -*-
"""
Replace Section 9 (sub-activity comparison table) in the HTML report
with v4 merged data (7 periods including Feb standalone)
"""
import re

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(r'C:\ADHD_agent\_tmp_subact_table_v4.html', 'r', encoding='utf-8') as f:
    new_rows = f.read().strip()

old_section_start = '<!-- ══ Section 9: 子活动横向对比 ══ -->'
old_section_end = '<!-- 子活动诊断卡片 -->'

start_idx = html.index(old_section_start)
end_idx = html.index(old_section_end)

new_section = f"""{old_section_start}
<div class="section">
  <div class="section-title">子活动横向对比（近7期 · v4合并规则 · 含2月独立周期）</div>
  <div style="margin-bottom:10px;font-size:12px;color:var(--text-muted)">
    分类依据：dim_iap.iap_type2 + v4合并规则（弹珠/大富翁/推币机/皮肤GACHA等同类合并）· 日期为礼包购买覆盖期 · 春节拆为纯春节+2月独立周期 · 按总收入降序 · 共84个子活动
  </div>
  <div class="table-wrap" style="max-height:800px;overflow-y:auto">
    <table>
      <thead>
        <tr>
          <th>子活动（合并后）</th>
          <th>模块</th>
          <th class="num">🎃 万圣节</th>
          <th class="num">🦃 感恩节</th>
          <th class="num">🎄 圣诞节</th>
          <th class="num">🧧 春节纯</th>
          <th class="num" style="color:var(--accent4)">📅 2月独立</th>
          <th class="num">💝 情人节</th>
          <th class="num" style="color:var(--accent)">🔬 科技节</th>
          <th class="num">总计</th>
        </tr>
      </thead>
      <tbody>
{new_rows}
      </tbody>
    </table>
  </div>

  """

html = html[:start_idx] + new_section + html[end_idx:]

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: Section 9 replaced with v4 data (7 periods, 84 activities)")
