"""生成日维度营收折线图"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

with open('C:/ADHD_agent/report_images/2026情人节/input_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

dr = data['daily_revenue']
dates = [d['date'][5:] for d in dr]  # MM-DD
revenues = [d['revenue'] / 1000 for d in dr]  # 转为千美元
buyers = [d['buyers'] for d in dr]

fig, ax1 = plt.subplots(figsize=(14, 5))

# 营收柱状图
colors = ['#FF6B6B' if r == max(revenues) else '#4ECDC4' for r in revenues]
bars = ax1.bar(dates, revenues, color=colors, alpha=0.7, width=0.6)
ax1.set_ylabel('日营收 ($K)', fontsize=11)
ax1.set_ylim(0, max(revenues) * 1.25)

# 在柱子上标注金额
for i, (bar, rev) in enumerate(zip(bars, revenues)):
    if rev > 40 or rev == min(revenues):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'${rev:.1f}K', ha='center', va='bottom', fontsize=7, fontweight='bold')

# 付费人数折线（右轴）
ax2 = ax1.twinx()
ax2.plot(dates, buyers, color='#FF8C00', marker='o', markersize=4, linewidth=2, label='付费人数')
ax2.set_ylabel('付费人数', fontsize=11, color='#FF8C00')
ax2.tick_params(axis='y', labelcolor='#FF8C00')
ax2.set_ylim(0, max(buyers) * 1.3)

# 标题和样式
ax1.set_title('2026情人节 · 日维度营收 & 付费人数', fontsize=14, fontweight='bold', pad=12)
ax1.tick_params(axis='x', rotation=45, labelsize=8)

# 添加周分隔线
for i in [7, 14, 21]:
    if i < len(dates):
        ax1.axvline(x=i-0.5, color='gray', linestyle='--', alpha=0.3)

# 图例
ax2.legend(loc='upper right', fontsize=9)

plt.tight_layout()
plt.savefig('C:/ADHD_agent/report_images/2026情人节/4_Daily_Revenue.png', dpi=150, bbox_inches='tight')
print('Done: 4_Daily_Revenue.png')
