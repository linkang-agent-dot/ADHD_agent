# -*- coding: utf-8 -*-
"""在模块趋势(Section 8)和子活动横向对比(Section 9)之间插入皮肤抽奖模块对比"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(r'C:\ADHD_agent\_tmp_skin_slot_section.html', 'r', encoding='utf-8') as f:
    section = f.read()

marker = '<!-- ══ Section 9: 子活动横向对比 ══ -->'
if marker not in html:
    print("ERROR: 找不到 Section 9 标记")
    sys.exit(1)

html = html.replace(marker, section + '\n\n' + marker)

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done: 皮肤抽奖模块对比已插入（{len(section)} chars）")
print(f"报告总大小: {len(html)} chars")
