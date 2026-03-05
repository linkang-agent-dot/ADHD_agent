import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 原始数据
data = {
    '活动': ['打孔小游戏', 'gacha春节礼包', '钓鱼', '异族大富翁', 'MJ8', '行军表情', '挖矿'],
    '投放内容': ['往期主城特效', '新主城皮肤', '独立玩法主城皮肤', '行军特效套装', '独立玩法行军特效', '新行军表情', '养成线'],
    '付费ARPU': [12.21, 7.47, 6.52, 19.91, 4.82, 1.59, 1.14],
    '付费率': [15.27, 10.32, 10.26, 12.10, 9.35, 3.94, 7.67],
    '超R收入占比': [69.8, 67.8, 75.3, 87.4, 80.5, 83.9, 15.8],
    '分层清晰度': [16, 21, 26, 31, 29, 101, 2.9],
    '总付费额': [167822.81, 102639.64, 89563, 273612.99, 66232.34, 21807.47, 15664.42]
}

df = pd.DataFrame(data)

# 评分函数
def score_arpu(x):
    if x >= 15: return 100
    elif x >= 10: return 80
    elif x >= 5: return 60
    elif x >= 2: return 40
    else: return 20

def score_rate(x):
    if x >= 15: return 100
    elif x >= 10: return 80
    elif x >= 7: return 60
    elif x >= 4: return 40
    else: return 20

def score_whale(x):
    if 50 <= x <= 70: return 100
    elif 70 < x <= 80: return 80
    elif 40 <= x < 50: return 60
    elif 80 < x <= 90: return 40
    else: return 20

def score_gradient(x):
    if 15 <= x <= 25: return 100
    elif (10 <= x < 15) or (25 < x <= 35): return 80
    elif (5 <= x < 10) or (35 < x <= 50): return 60
    elif 50 < x <= 100: return 40
    else: return 20

# 计算各维度得分
df['变现力得分'] = df['付费ARPU'].apply(score_arpu)
df['转化力得分'] = df['付费率'].apply(score_rate)
df['鲸鱼依赖度得分'] = df['超R收入占比'].apply(score_whale)
df['分层清晰度得分'] = df['分层清晰度'].apply(score_gradient)

# 计算综合得分 (权重: 变现30%, 转化25%, 鲸鱼25%, 分层20%)
df['综合得分'] = (df['变现力得分'] * 0.30 + 
                 df['转化力得分'] * 0.25 + 
                 df['鲸鱼依赖度得分'] * 0.25 + 
                 df['分层清晰度得分'] * 0.20)

# 评级
def get_grade(score):
    if score >= 85: return 'S'
    elif score >= 70: return 'A'
    elif score >= 55: return 'B'
    elif score >= 40: return 'C'
    else: return 'D'

df['等级'] = df['综合得分'].apply(get_grade)

# 按综合得分排序
df = df.sort_values('综合得分', ascending=False)

print('=' * 80)
print('节日活动效果评级分析报告')
print('=' * 80)
print()

# 输出评级结果
print('【综合评级结果】')
print('-' * 60)
result_df = df[['活动', '投放内容', '综合得分', '等级']].copy()
print(result_df.to_string(index=False))
print()

# 输出各维度得分
print('【各维度得分明细】')
print('-' * 60)
detail_df = df[['活动', '变现力得分', '转化力得分', '鲸鱼依赖度得分', '分层清晰度得分', '综合得分', '等级']].copy()
print(detail_df.to_string(index=False))
print()

# 统计分析
print('【统计分析】')
print('-' * 60)
grade_counts = df['等级'].value_counts()
print(f"活动总数: {len(df)}")
for grade in ['S', 'A', 'B', 'C', 'D']:
    count = grade_counts.get(grade, 0)
    print(f"{grade}级活动: {count} 个")
print()
print(f"平均综合得分: {df['综合得分'].mean():.1f}")
print(f"最高分: {df['综合得分'].max():.1f} ({df.iloc[0]['活动']})")
print(f"最低分: {df['综合得分'].min():.1f} ({df.iloc[-1]['活动']})")
print()

# 各维度平均分
print('【各维度平均得分】')
print('-' * 60)
print(f"变现力平均: {df['变现力得分'].mean():.1f}")
print(f"转化力平均: {df['转化力得分'].mean():.1f}")
print(f"鲸鱼依赖度平均: {df['鲸鱼依赖度得分'].mean():.1f}")
print(f"分层清晰度平均: {df['分层清晰度得分'].mean():.1f}")

# ============ 可视化 ============

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('节日活动效果评级分析', fontsize=16, fontweight='bold')

# 图1: 综合评分柱状图
ax1 = axes[0, 0]
colors = {'S': '#2ecc71', 'A': '#3498db', 'B': '#f39c12', 'C': '#e74c3c', 'D': '#95a5a6'}
bar_colors = [colors[g] for g in df['等级']]
bars = ax1.barh(df['活动'], df['综合得分'], color=bar_colors)
ax1.set_xlabel('综合得分')
ax1.set_title('综合评分排名')
ax1.set_xlim(0, 100)
for bar, score, grade in zip(bars, df['综合得分'], df['等级']):
    ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
             f'{score:.0f} ({grade})', va='center', fontsize=10)
ax1.axvline(x=85, color='green', linestyle='--', alpha=0.5, label='S级线')
ax1.axvline(x=70, color='blue', linestyle='--', alpha=0.5, label='A级线')
ax1.axvline(x=55, color='orange', linestyle='--', alpha=0.5, label='B级线')
ax1.legend(loc='lower right')

# 图2: 雷达图 - 各活动四维度对比
ax2 = axes[0, 1]
categories = ['变现力', '转化力', '鲸鱼依赖度\n(健康度)', '分层清晰度']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

ax2 = plt.subplot(222, polar=True)
ax2.set_theta_offset(np.pi / 2)
ax2.set_theta_direction(-1)
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(categories, fontsize=9)

# 只画前4个活动（避免太乱）
line_colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
for idx, (_, row) in enumerate(df.head(4).iterrows()):
    values = [row['变现力得分'], row['转化力得分'], row['鲸鱼依赖度得分'], row['分层清晰度得分']]
    values += values[:1]
    ax2.plot(angles, values, 'o-', linewidth=2, label=row['活动'], color=line_colors[idx])
    ax2.fill(angles, values, alpha=0.1, color=line_colors[idx])
ax2.set_ylim(0, 100)
ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
ax2.set_title('Top 4活动四维度对比', y=1.08)

# 图3: 四象限图 (变现力 vs 鲸鱼依赖度)
ax3 = axes[1, 0]
scatter = ax3.scatter(df['付费ARPU'], df['超R收入占比'], 
                      s=df['总付费额']/1000, c=[colors[g] for g in df['等级']], 
                      alpha=0.7, edgecolors='black')
for idx, row in df.iterrows():
    ax3.annotate(row['活动'], (row['付费ARPU'], row['超R收入占比']), 
                 textcoords="offset points", xytext=(5,5), fontsize=9)
ax3.axhline(y=70, color='gray', linestyle='--', alpha=0.5)
ax3.axvline(x=10, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('变现力 (付费ARPU)')
ax3.set_ylabel('鲸鱼依赖度 (超R收入占比%)')
ax3.set_title('变现力 vs 鲸鱼依赖度\n(气泡大小=总付费额)')
ax3.text(15, 50, '高变现\n低依赖\n(理想)', fontsize=9, ha='center', color='green')
ax3.text(15, 90, '高变现\n高依赖\n(风险)', fontsize=9, ha='center', color='red')
ax3.text(3, 50, '低变现\n低依赖', fontsize=9, ha='center', color='gray')
ax3.text(3, 90, '低变现\n高依赖\n(差)', fontsize=9, ha='center', color='gray')

# 图4: 各维度得分堆叠条形图
ax4 = axes[1, 1]
activities = df['活动'].tolist()
x = np.arange(len(activities))
width = 0.2

rects1 = ax4.bar(x - 1.5*width, df['变现力得分'], width, label='变现力', color='#3498db')
rects2 = ax4.bar(x - 0.5*width, df['转化力得分'], width, label='转化力', color='#2ecc71')
rects3 = ax4.bar(x + 0.5*width, df['鲸鱼依赖度得分'], width, label='鲸鱼依赖度', color='#f39c12')
rects4 = ax4.bar(x + 1.5*width, df['分层清晰度得分'], width, label='分层清晰度', color='#9b59b6')

ax4.set_ylabel('得分')
ax4.set_title('各维度得分对比')
ax4.set_xticks(x)
ax4.set_xticklabels(activities, rotation=45, ha='right')
ax4.legend(loc='upper right')
ax4.set_ylim(0, 120)
ax4.axhline(y=60, color='gray', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig(r'c:\ADHD_agent\活动评级分析图表.png', dpi=150, bbox_inches='tight')
print()
print('图表已保存至: 活动评级分析图表.png')

# 保存数据
df.to_excel(r'c:\ADHD_agent\活动评级分析结果.xlsx', index=False)
print('数据已保存至: 活动评级分析结果.xlsx')
