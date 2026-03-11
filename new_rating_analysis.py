import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df_raw = pd.read_excel(r'C:\Users\linkang\Downloads\节日数据评级.xlsx', sheet_name='工作表102')

# 解析数据 - 提取每个活动的信息
activities = []
current_activity = None
current_festival = None
current_content = None

for idx, row in df_raw.iterrows():
    # 检测活动标题行（第一列有活动名，节日时间列有值）
    if pd.notna(row['节日时间']) and row['节日时间'] != 'NaN':
        current_activity = str(row['付费总额'])
        current_festival = str(row['节日时间'])
        current_content = str(row['特殊投放内容']) if pd.notna(row['特殊投放内容']) else ''
        continue
    
    # 跳过表头行
    if row['付费总额'] == '付费总额' or row['R级'] == 'R级':
        continue
    
    # 提取R级数据
    if current_activity and pd.notna(row['R级']):
        r_level = str(row['R级'])
        if r_level == '整体':
            # 整体数据行
            activities.append({
                '活动': current_activity,
                '节日时间': current_festival,
                '投放内容': current_content,
                '总付费额': float(row['付费总额']) if pd.notna(row['付费总额']) else 0,
                '付费人数': int(float(row['付费人数'])) if pd.notna(row['付费人数']) else 0,
                '付费率': float(row['付费率']) * 100 if pd.notna(row['付费率']) else 0,
                '付费ARPU': float(row['付费ARPU']) if pd.notna(row['付费ARPU']) else 0,
                'ARPPU': float(row['ARPPU']) if pd.notna(row['ARPPU']) else 0,
            })
        elif r_level == 'xiaoR':
            # 小R数据，保存付费率
            for act in activities:
                if act['活动'] == current_activity and act['节日时间'] == current_festival:
                    act['小R付费率'] = float(row['付费率']) * 100 if pd.notna(row['付费率']) else 0
                    act['小R付费额'] = float(row['付费总额']) if pd.notna(row['付费总额']) else 0
        elif r_level == 'chaoR':
            # 超R数据
            for act in activities:
                if act['活动'] == current_activity and act['节日时间'] == current_festival:
                    act['超R付费率'] = float(row['付费率']) * 100 if pd.notna(row['付费率']) else 0
                    act['超R付费额'] = float(row['付费总额']) if pd.notna(row['付费总额']) else 0

# 重新解析，确保每个活动有完整数据
activities_clean = []
current_activity = None
current_festival = None
current_content = None
temp_data = {}

for idx, row in df_raw.iterrows():
    val0 = row['付费总额']
    val_festival = row['节日时间']
    val_content = row['特殊投放内容']
    val_rlevel = row['R级']
    
    # 检测活动标题行
    if pd.notna(val_festival) and str(val_festival) not in ['NaN', 'nan', '']:
        # 保存上一个活动
        if current_activity and '整体' in temp_data:
            act_data = temp_data['整体'].copy()
            act_data['活动'] = current_activity
            act_data['节日时间'] = current_festival
            act_data['投放内容'] = current_content
            if 'xiaoR' in temp_data:
                act_data['小R付费率'] = temp_data['xiaoR']['付费率']
                act_data['小R付费额'] = temp_data['xiaoR']['付费额']
            if 'chaoR' in temp_data:
                act_data['超R付费率'] = temp_data['chaoR']['付费率']
                act_data['超R付费额'] = temp_data['chaoR']['付费额']
            activities_clean.append(act_data)
        
        current_activity = str(val0)
        current_festival = str(val_festival)
        current_content = str(val_content) if pd.notna(val_content) else ''
        temp_data = {}
        continue
    
    # 跳过表头行
    if str(val0) == '付费总额':
        continue
    
    # 提取R级数据
    if pd.notna(val_rlevel) and str(val_rlevel) not in ['NaN', 'nan', '']:
        r_level = str(val_rlevel)
        try:
            pay_amount = float(val0) if pd.notna(val0) else 0
            pay_rate = float(row['付费率']) * 100 if pd.notna(row['付费率']) else 0
            pay_arpu = float(row['付费ARPU']) if pd.notna(row['付费ARPU']) else 0
            pay_count = int(float(row['付费人数'])) if pd.notna(row['付费人数']) else 0
            arppu = float(row['ARPPU']) if pd.notna(row['ARPPU']) else 0
            
            if r_level == '整体':
                temp_data['整体'] = {
                    '总付费额': pay_amount,
                    '付费人数': pay_count,
                    '付费率': pay_rate,
                    '付费ARPU': pay_arpu,
                    'ARPPU': arppu
                }
            elif r_level == 'xiaoR':
                temp_data['xiaoR'] = {'付费率': pay_rate, '付费额': pay_amount}
            elif r_level == 'chaoR':
                temp_data['chaoR'] = {'付费率': pay_rate, '付费额': pay_amount}
        except:
            pass

# 保存最后一个活动
if current_activity and '整体' in temp_data:
    act_data = temp_data['整体'].copy()
    act_data['活动'] = current_activity
    act_data['节日时间'] = current_festival
    act_data['投放内容'] = current_content
    if 'xiaoR' in temp_data:
        act_data['小R付费率'] = temp_data['xiaoR']['付费率']
        act_data['小R付费额'] = temp_data['xiaoR']['付费额']
    if 'chaoR' in temp_data:
        act_data['超R付费率'] = temp_data['chaoR']['付费率']
        act_data['超R付费额'] = temp_data['chaoR']['付费额']
    activities_clean.append(act_data)

# 创建DataFrame
df = pd.DataFrame(activities_clean)

# 计算四维度指标
df['超R收入占比'] = df['超R付费额'] / df['总付费额'] * 100
df['分层清晰度'] = df['超R付费率'] / df['小R付费率']

# 处理无穷大
df['分层清晰度'] = df['分层清晰度'].replace([np.inf, -np.inf], 999)
df['分层清晰度'] = df['分层清晰度'].fillna(0)

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

def get_grade(score):
    if score >= 85: return 'S'
    elif score >= 70: return 'A'
    elif score >= 55: return 'B'
    elif score >= 40: return 'C'
    else: return 'D'

# 计算各维度得分
df['变现力得分'] = df['付费ARPU'].apply(score_arpu)
df['转化力得分'] = df['付费率'].apply(score_rate)
df['鲸鱼依赖度得分'] = df['超R收入占比'].apply(score_whale)
df['分层清晰度得分'] = df['分层清晰度'].apply(score_gradient)

# 计算综合得分
df['综合得分'] = (
    df['变现力得分'] * 0.30 + 
    df['转化力得分'] * 0.25 + 
    df['鲸鱼依赖度得分'] * 0.25 + 
    df['分层清晰度得分'] * 0.20
)

df['等级'] = df['综合得分'].apply(get_grade)

# 按综合得分排序
df = df.sort_values('综合得分', ascending=False)

# 打印报告
print('=' * 100)
print('节日活动效果评级分析报告（完整版）')
print('=' * 100)
print(f'\n活动总数: {len(df)}')
print()

# 按等级统计
print('【评级分布】')
print('-' * 60)
grade_counts = df['等级'].value_counts()
for grade in ['S', 'A', 'B', 'C', 'D']:
    count = grade_counts.get(grade, 0)
    pct = count / len(df) * 100
    print(f"{grade}级: {count} 个 ({pct:.1f}%)")
print()

# 输出所有活动评级结果
print('【所有活动评级结果】')
print('-' * 100)
result_df = df[['活动', '节日时间', '投放内容', '付费率', '付费ARPU', '超R收入占比', '分层清晰度', '综合得分', '等级']].copy()
result_df['付费率'] = result_df['付费率'].apply(lambda x: f'{x:.2f}%')
result_df['超R收入占比'] = result_df['超R收入占比'].apply(lambda x: f'{x:.1f}%')
result_df['分层清晰度'] = result_df['分层清晰度'].apply(lambda x: f'{x:.1f}倍')
result_df['付费ARPU'] = result_df['付费ARPU'].apply(lambda x: f'{x:.2f}')
result_df['综合得分'] = result_df['综合得分'].apply(lambda x: f'{x:.0f}')
print(result_df.to_string(index=False))
print()

# 按节日时间分组分析
print('【按节日时间分析】')
print('-' * 60)
for festival in df['节日时间'].unique():
    festival_df = df[df['节日时间'] == festival]
    avg_score = festival_df['综合得分'].mean()
    s_count = len(festival_df[festival_df['等级'] == 'S'])
    a_count = len(festival_df[festival_df['等级'] == 'A'])
    print(f"{festival}: {len(festival_df)}个活动, 平均{avg_score:.1f}分, S级{s_count}个, A级{a_count}个")
print()

# 按投放内容分析
print('【按投放内容分析】')
print('-' * 60)
content_stats = df.groupby('投放内容').agg({
    '综合得分': 'mean',
    '付费ARPU': 'mean',
    '付费率': 'mean',
    '活动': 'count'
}).rename(columns={'活动': '数量'}).sort_values('综合得分', ascending=False)
print(content_stats.to_string())
print()

# Top 10 和 Bottom 5
print('【Top 10 活动】')
print('-' * 60)
top10 = df.head(10)[['活动', '节日时间', '投放内容', '综合得分', '等级']]
print(top10.to_string(index=False))
print()

print('【Bottom 5 活动】')
print('-' * 60)
bottom5 = df.tail(5)[['活动', '节日时间', '投放内容', '综合得分', '等级']]
print(bottom5.to_string(index=False))
print()

# 各维度平均分
print('【各维度平均得分】')
print('-' * 60)
print(f"变现力平均: {df['变现力得分'].mean():.1f}")
print(f"转化力平均: {df['转化力得分'].mean():.1f}")
print(f"鲸鱼依赖度平均: {df['鲸鱼依赖度得分'].mean():.1f}")
print(f"分层清晰度平均: {df['分层清晰度得分'].mean():.1f}")

# ============ 可视化 ============

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.suptitle('节日活动效果评级分析（全量数据）', fontsize=16, fontweight='bold')

colors = {'S': '#2ecc71', 'A': '#3498db', 'B': '#f39c12', 'C': '#e74c3c', 'D': '#95a5a6'}

# 图1: 综合评分柱状图 (Top 15)
ax1 = axes[0, 0]
top15 = df.head(15)
bar_colors = [colors[g] for g in top15['等级']]
bars = ax1.barh(range(len(top15)), top15['综合得分'], color=bar_colors)
ax1.set_yticks(range(len(top15)))
ax1.set_yticklabels(top15['活动'], fontsize=9)
ax1.set_xlabel('综合得分')
ax1.set_title('综合评分排名 (Top 15)')
ax1.set_xlim(0, 100)
for i, (bar, score, grade) in enumerate(zip(bars, top15['综合得分'], top15['等级'])):
    ax1.text(bar.get_width() + 1, i, f'{score:.0f}({grade})', va='center', fontsize=8)
ax1.axvline(x=85, color='green', linestyle='--', alpha=0.5, label='S级线')
ax1.axvline(x=70, color='blue', linestyle='--', alpha=0.5, label='A级线')
ax1.invert_yaxis()
ax1.legend(loc='lower right')

# 图2: 等级分布饼图
ax2 = axes[0, 1]
grade_order = ['S', 'A', 'B', 'C', 'D']
grade_counts_ordered = [grade_counts.get(g, 0) for g in grade_order]
pie_colors = [colors[g] for g in grade_order]
wedges, texts, autotexts = ax2.pie(grade_counts_ordered, labels=grade_order, colors=pie_colors,
                                    autopct='%1.1f%%', startangle=90)
ax2.set_title('活动等级分布')

# 图3: 四象限图
ax3 = axes[1, 0]
scatter = ax3.scatter(df['付费ARPU'], df['超R收入占比'], 
                      s=df['总付费额']/2000 + 50, c=[colors[g] for g in df['等级']], 
                      alpha=0.7, edgecolors='black')
# 只标注Top5
for idx, row in df.head(5).iterrows():
    ax3.annotate(row['活动'][:6], (row['付费ARPU'], row['超R收入占比']), 
                 textcoords="offset points", xytext=(5,5), fontsize=8)
ax3.axhline(y=70, color='gray', linestyle='--', alpha=0.5)
ax3.axvline(x=10, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('变现力 (付费ARPU)')
ax3.set_ylabel('鲸鱼依赖度 (超R收入占比%)')
ax3.set_title('变现力 vs 鲸鱼依赖度\n(气泡大小=总付费额)')
ax3.text(20, 50, '高变现\n低依赖\n(理想)', fontsize=9, ha='center', color='green')
ax3.text(20, 90, '高变现\n高依赖', fontsize=9, ha='center', color='orange')

# 图4: 按节日时间的平均得分
ax4 = axes[1, 1]
festival_scores = df.groupby('节日时间')['综合得分'].mean().sort_values(ascending=True)
bar_colors4 = ['#3498db'] * len(festival_scores)
ax4.barh(range(len(festival_scores)), festival_scores.values, color=bar_colors4)
ax4.set_yticks(range(len(festival_scores)))
ax4.set_yticklabels(festival_scores.index, fontsize=9)
ax4.set_xlabel('平均综合得分')
ax4.set_title('各节日/时间点平均评分')
ax4.axvline(x=70, color='blue', linestyle='--', alpha=0.5, label='A级线')
ax4.legend()

plt.tight_layout()
plt.savefig(r'c:\ADHD_agent\新数据活动评级分析图表.png', dpi=150, bbox_inches='tight')
print('\n图表已保存至: 新数据活动评级分析图表.png')

# 保存Excel
df.to_excel(r'c:\ADHD_agent\新数据活动评级分析结果.xlsx', index=False)
print('数据已保存至: 新数据活动评级分析结果.xlsx')
