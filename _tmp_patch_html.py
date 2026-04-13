# -*- coding: utf-8 -*-
"""
用生成的 top20 和 rest 替换 HTML 报告中的排名表
"""
import re

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(r'C:\ADHD_agent\_tmp_rank_top20.html', 'r', encoding='utf-8') as f:
    top20 = f.read()

with open(r'C:\ADHD_agent\_tmp_rank_rest.html', 'r', encoding='utf-8') as f:
    rest = f.read()

# Replace top20: between <!-- Top 20 --> and </tbody>
old_top20_start = '      <tbody id="rank-body">\n        <!-- Top 20 -->\n'
old_top20_end = '      </tbody>\n    </table>'

idx_start = html.index(old_top20_start) + len(old_top20_start)
idx_end = html.index(old_top20_end, idx_start)
old_top20_content = html[idx_start:idx_end]

html = html[:idx_start] + top20 + '\n' + html[idx_end:]

# Replace rest: between <details><summary> tbody and </tbody></table></details>
rest_marker = '▼ 展开查看剩余'
idx_details = html.index(rest_marker)
tbody_start_str = '<tbody>\n'
idx_tbody = html.index(tbody_start_str, idx_details) + len(tbody_start_str)
idx_tbody_end = html.index('        </tbody>\n      </table>\n    </details>', idx_tbody)
old_rest = html[idx_tbody:idx_tbody_end]

html = html[:idx_tbody] + rest + '\n' + html[idx_tbody_end:]

# Update the summary text count
html = html.replace('剩余 29 条礼包（#21 ~ #49）', '剩余 31 条礼包（#21 ~ #51）')

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: rank table replaced")
