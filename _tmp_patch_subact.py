# -*- coding: utf-8 -*-
import re

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(r'C:\ADHD_agent\_tmp_subact_table_v3.html', 'r', encoding='utf-8') as f:
    new_rows = f.read()

# Find Section 9 tbody
section9_marker = 'Section 9'
idx_s9 = html.index(section9_marker)
tbody_tag = '<tbody>'
idx_tbody_start = html.index(tbody_tag, idx_s9) + len(tbody_tag)
idx_tbody_end = html.index('</tbody>', idx_tbody_start)
old_tbody = html[idx_tbody_start:idx_tbody_end]

html = html[:idx_tbody_start] + '\n' + new_rows + '\n      ' + html[idx_tbody_end:]

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: Section 9 tbody replaced")
