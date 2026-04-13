import re

with open(r'C:\ADHD_agent\节日排期报告_7月8月.md', encoding='utf-8') as f:
    content = f.read()

# Fix 1: 强消耗扭蛋机 -> 强消耗
content = content.replace('强消耗扭蛋机 | 复用 | 50 |', '强消耗 | 复用 | 50 |')

# Fix 2: 掉落转付费 换皮 -> 复用
content = content.replace('掉落转付费 | **换皮** | 48.2 |', '掉落转付费 | 复用 | 48.2 |')

# Fix 3: 每日付费率礼包 换皮 -> 每日节日付费率礼包 复用
content = content.replace('每日付费率礼包 | **换皮** | 暂无 |', '每日节日付费率礼包 | 复用 | 暂无 |')

# Fix 4: 对照表
content = content.replace('掉落转付费 | Week1（复用→换皮）', '掉落转付费 | Week1（复用）')

# Fix 5: 去掉风险表里已过期的那行
old_line = '|| 🟡 P2 | **7月 掉落转付费 / 每日付费率礼包 开发方式为"换皮"** | 之前误记为复用，实际需要换皮开发量 | 评估换皮工作量是否已纳入排期 |'
content = content.replace(old_line, '')

# Fix 6: 更新页脚
content = content.replace(
    '*报告生成：2026-04-07 | 数据二次核对版 | 配套甘特图：`_gantt_festival_final.png`*',
    '*报告生成：2026-04-07 | 数据三次核对版 | 配套甘特图：`_gantt_festival_final.png`*'
)

with open(r'C:\ADHD_agent\节日排期报告_7月8月.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Checking fixed lines...')
for i, line in enumerate(content.splitlines(), 1):
    if any(x in line for x in ['强消耗', '掉落转付费', '每日节日', '数据三次']):
        print(f'  L{i}: {line[:90]}')
