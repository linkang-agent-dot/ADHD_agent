# -*- coding: utf-8 -*-
"""
用v5数据打补丁到HTML报告：
1. 替换子活动横向对比表的 tbody
2. 替换趋势分析整个 Section
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. 替换子活动横向对比的 tbody ──
with open(r'C:\ADHD_agent\_tmp_subact_table_v5.html', 'r', encoding='utf-8') as f:
    new_tbody = f.read()

# 找到 Section 9 的 tbody
s9_marker = '<!-- ══ Section 9: 子活动横向对比 ══ -->'
s9_idx = html.find(s9_marker)
if s9_idx < 0:
    print("ERROR: 找不到 Section 9")
    sys.exit(1)

# 在 Section 9 内找 <tbody> ... </tbody>
tbody_start = html.find('<tbody>', s9_idx)
tbody_end = html.find('</tbody>', tbody_start)
if tbody_start < 0 or tbody_end < 0:
    print("ERROR: 找不到 Section 9 的 tbody")
    sys.exit(1)

old_tbody = html[tbody_start + len('<tbody>'):tbody_end]
html = html[:tbody_start + len('<tbody>')] + '\n' + new_tbody + '\n' + html[tbody_end:]

# 更新 Section 9 标题里的数字
html = html.replace(
    '子活动横向对比（近7期 · v4合并规则 · 含2月独立周期）',
    '子活动横向对比（近7期 · v6合并规则 · v5数据修正独立周期）'
)
# 更新描述里的活动数
html = re.sub(r'共\d+个子活动', f'共86个子活动', html)

print(f"1. 子活动表 tbody 已替换 (86 rows)")

# ── 2. 替换趋势分析 Section ──
with open(r'C:\ADHD_agent\_tmp_trend_section_v5.html', 'r', encoding='utf-8') as f:
    new_trend = f.read()

# 找旧的趋势 Section（可能有两个标记格式）
trend_marker = '<!-- ══ Section 11: 子活动趋势分析 ══ -->'
trend_marker2 = '<!-- ══ Section: 子活动趋势分析 ══ -->'

# 尝试找 "子活动增长 & 衰减趋势分析" 标题所在的 section
trend_title = '子活动增长 &amp; 衰减趋势分析'
trend_title2 = '子活动增长 & 衰减趋势分析'

# 找到趋势分析 section 的开始
trend_start = -1
for marker in [trend_marker, trend_marker2]:
    pos = html.find(marker)
    if pos >= 0:
        trend_start = pos
        break

if trend_start < 0:
    # 如果找不到注释标记，找 section-title
    for t in [trend_title, trend_title2]:
        pos = html.find(t)
        if pos >= 0:
            # 往回找到 <div class="section">
            search_back = html.rfind('<div class="section">', 0, pos)
            if search_back >= 0:
                # 再往回找可能的注释
                comment_pos = html.rfind('<!--', max(0, search_back - 100), search_back)
                trend_start = comment_pos if comment_pos >= 0 else search_back
                break

if trend_start < 0:
    print("WARNING: 找不到趋势分析 Section，将在活动诊断前插入")
    diag_marker = '<!-- ══ Section 10: 活动诊断 ══ -->'
    diag_pos = html.find(diag_marker)
    if diag_pos < 0:
        print("ERROR: 也找不到活动诊断 Section")
        sys.exit(1)
    html = html[:diag_pos] + new_trend + '\n\n' + html[diag_pos:]
    print(f"2. 趋势分析已插入（新增）")
else:
    # 找这个 section 的结束（下一个 <!-- ══ 或 <div class="section">）
    # 找到 </div> 结束标签 - section 由 <div class="section"> 开头
    # 需要匹配嵌套的 div
    
    # 简单方法：找下一个 <!-- ══ Section
    next_section = html.find('<!-- ══ Section', trend_start + 10)
    if next_section < 0:
        next_section = html.find('<!-- ══ Section', trend_start + 10)
    
    # 也找 "<!-- ══ Section 10" 或类似
    next_markers = []
    for m in ['<!-- ══ Section 10:', '<!-- ══ Section 9:', '<!-- ══ Section: Action']:
        p = html.find(m, trend_start + 10)
        if p >= 0:
            next_markers.append(p)
    
    if next_markers:
        trend_end = min(next_markers)
    elif next_section >= 0:
        trend_end = next_section
    else:
        print("ERROR: 找不到趋势 Section 的结束位置")
        sys.exit(1)
    
    html = html[:trend_start] + new_trend + '\n\n' + html[trend_end:]
    print(f"2. 趋势分析 Section 已替换")

# ── 3. 更新近期节日横向对比表中春节和独立周期的数据 ──
# 春节(纯)行：之前是 01-13~02-01，现在变成 01-13~02-08（扣独立模块）
# 独立周期行：之前是 $250K全量，现在是 $150K（只含4类）

# 更新春节行的节日礼包收入
html = html.replace(
    '📅 春节（纯）',
    '📅 春节'
)

print(f"3. 标题修正完成")

with open(r'C:\ADHD_agent\_tech_fest_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n报告总大小: {len(html)} chars")
print("Done!")
