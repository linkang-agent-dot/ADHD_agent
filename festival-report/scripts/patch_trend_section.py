# -*- coding: utf-8 -*-
"""在 Section 9 和 Section 10 之间插入趋势分析 Section"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(r'C:\ADHD_agent\_tmp_trend_section.html', 'r', encoding='utf-8') as f:
    trend = f.read()

marker = '<!-- ══ Section 10: 活动诊断 ══ -->'
if marker not in html:
    print("ERROR: 找不到 Section 10 标记")
    sys.exit(1)

html = html.replace(marker, trend + '\n\n' + marker)

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done: 趋势分析已插入报告（{len(trend)} chars）")
print(f"报告总大小: {len(html)} chars")
