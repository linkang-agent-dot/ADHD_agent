# -*- coding: utf-8 -*-
"""更新 HTML 报告中的关键数值（Section 2 & Section 8）"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ── Section 2: 更新春节礼包收入和独立周期收入 ──

# 春节礼包收入: $811,208 → $917,458 (取整)
html = html.replace('$811,208', '$917,458')
changes += html.count('917,458') > 0

# 独立周期礼包收入: $249,956 → $150,458
html = html.replace('$249,956', '$150,458')
changes += 1

# 独立周期描述
html = html.replace(
    '2月独立周期</b>（02-02~02-08，7天）：$250K 节日礼包收入，推币机+一番赏+砍价为主力，独立于春节和情人节之间',
    '2月独立周期</b>（02-02~02-08，7天）：$150K 节日礼包收入，仅含推币机/一番赏/砍价/抢购 4 类活动，其余归入春节'
)
changes += 1

# ── Section 8: 更新模块趋势表的春节和独立周期数据 ──
# 旧数据（春节纯 01-13~02-01）
# 节日特惠: $676,222  节日皮肤: $60,757  节日BP: $61,184  挖矿: $13,045
# 新数据（春节 01-13~02-08 扣独立模块）
# 节日特惠: $764K  节日皮肤: $69K  节日BP: $71K  挖矿: $13K

# 更新春节列标题
html = html.replace(
    '🧧 春节（纯）<br><span style="font-weight:400;color:var(--text-muted)">01-13~02-01</span>',
    '🧧 春节<br><span style="font-weight:400;color:var(--text-muted)">01-13~02-08*</span>'
)
changes += 1

# 更新 JS 图表数据
# 旧: [676222,  60757,  61184, 13045],  // 春节纯 01-13~02-01
html = html.replace(
    '[676222,  60757,  61184, 13045]',
    '[763968, 69148, 71236, 13106]'
)
changes += 1

# 旧: [170246,  64593,  14738,   379],  // 2月独立 02-02~02-08
html = html.replace(
    '[170246,  64593,  14738,   379]',
    '[87520, 57025, 5913, 0]'
)
changes += 1

# 更新 Section 8 表格内春节和独立周期的单元格
# 这些是手工填的数值，需要精确替换
# 春节纯的模块数据在表格中
# 搜索特征行来替换

# 更新春节占比
html = html.replace('春节纯', '春节')
changes += 1

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"完成 {changes} 处修改")
print(f"报告大小: {len(html)} chars")
