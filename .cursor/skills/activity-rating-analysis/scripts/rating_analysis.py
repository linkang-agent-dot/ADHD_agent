"""
节日活动付费效果评级系统
基于1041游戏付费效果分析报告设计

评分维度：
1. 付费深度(ARPPU) - 40% - 核心：让付费用户花更多
2. 转化广度(付费率) - 30% - 拉动更多人付费  
3. 综合变现(ARPU) - 20% - 整体变现效率
4. R级健康度 - 10% - 超R占比60-70%最佳

使用方式：
python rating_analysis.py --input <Excel文件路径> [--output <输出目录>]
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import re
import argparse
import os

sys.stdout.reconfigure(encoding='utf-8')

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ============ 评分函数 ============

def score_arppu(x):
    """ARPPU评分（权重40%）"""
    if x >= 100: return 100
    elif x >= 70: return 90
    elif x >= 50: return 80
    elif x >= 35: return 70
    elif x >= 25: return 60
    elif x >= 15: return 45
    else: return 30

def score_pay_rate(x):
    """付费率评分（权重30%）"""
    if x >= 15: return 100
    elif x >= 12: return 90
    elif x >= 10: return 80
    elif x >= 8: return 70
    elif x >= 6: return 55
    elif x >= 4: return 40
    else: return 25

def score_arpu(x):
    """ARPU评分（权重20%）"""
    if x >= 20: return 100
    elif x >= 15: return 90
    elif x >= 10: return 80
    elif x >= 7: return 70
    elif x >= 5: return 60
    elif x >= 3: return 45
    else: return 30

def score_r_health(x):
    """R级健康度评分（权重10%）"""
    if 60 <= x <= 70: return 100
    elif 55 <= x < 60: return 85
    elif 70 < x <= 75: return 85
    elif 50 <= x < 55: return 70
    elif 75 < x <= 80: return 70
    elif 45 <= x < 50: return 55
    elif 80 < x <= 85: return 55
    elif x > 85: return 40
    else: return 40

def get_grade(score):
    """等级划分"""
    if score >= 85: return 'S'
    elif score >= 75: return 'A'
    elif score >= 65: return 'B'
    elif score >= 50: return 'C'
    else: return 'D'

def get_tier(score):
    """梯队划分"""
    if score >= 80: return 'T1'
    elif score >= 65: return 'T2'
    else: return 'T3'


# ============ 同名活动合并 ============

def extract_base_name(name):
    """提取基础活动名（去掉期数、节日后缀等）"""
    name = str(name)
    
    # 特殊映射
    name_mappings = {
        '弹珠抽奖': '弹珠抽奖',
        '弹珠第二期': '弹珠抽奖',
        '弹珠抽奖第': '弹珠抽奖',
        '多条件连锁第': '多条件连锁',
        '多条件连锁': '多条件连锁',
        '小额转盘': '小额转盘',
    }
    for pattern, base in name_mappings.items():
        if name.startswith(pattern):
            return base
    
    # 通用规则
    base = re.sub(r'[-]?(圣诞节|复活节|万圣节|周年庆|音乐节|登月节|返场版本).*$', '', name)
    base = re.sub(r'[-_]?第[一二三四五六七八九十\d]+期.*$', '', base)
    base = re.sub(r'[-_]?\d+期.*$', '', base)
    base = re.sub(r'[（\(][^）\)]*[）\)]', '', base)
    base = re.sub(r'[-_]+$', '', base).strip()
    
    return base if base else name


# ============ 数据解析 ============

def parse_activity_data(input_file, sheet_name=None):
    """解析活动数据Excel"""
    
    # 尝试读取Excel
    if sheet_name:
        df_raw = pd.read_excel(input_file, sheet_name=sheet_name)
    else:
        # 尝试自动检测sheet
        xl = pd.ExcelFile(input_file)
        sheet_name = xl.sheet_names[0]
        df_raw = pd.read_excel(input_file, sheet_name=sheet_name)
    
    # 检查是否有必需的列
    required_cols = ['付费总额', '付费率', 'R级']
    missing_cols = [col for col in required_cols if col not in df_raw.columns]
    
    if missing_cols:
        # 尝试另一种格式：简化格式
        return parse_simple_format(df_raw)
    
    return parse_complex_format(df_raw)


def parse_complex_format(df_raw):
    """解析复杂格式（带R级分层的数据）"""
    activities_clean = []
    current_activity = None
    current_festival = None
    current_content = None
    temp_data = {}
    
    for idx, row in df_raw.iterrows():
        val0 = row.get('付费总额', row.iloc[0] if len(row) > 0 else None)
        val_festival = row.get('节日时间', None)
        val_content = row.get('特殊投放内容', row.get('投放内容', ''))
        val_rlevel = row.get('R级', None)
        
        if pd.notna(val_festival) and str(val_festival) not in ['NaN', 'nan', '']:
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
        
        if str(val0) == '付费总额':
            continue
        
        if pd.notna(val_rlevel) and str(val_rlevel) not in ['NaN', 'nan', '']:
            r_level = str(val_rlevel)
            try:
                pay_amount = float(val0) if pd.notna(val0) else 0
                pay_rate = float(row['付费率']) * 100 if pd.notna(row['付费率']) else 0
                pay_arpu = float(row.get('付费ARPU', 0)) if pd.notna(row.get('付费ARPU', None)) else 0
                pay_count = int(float(row.get('付费人数', 0))) if pd.notna(row.get('付费人数', None)) else 0
                arppu = float(row.get('ARPPU', 0)) if pd.notna(row.get('ARPPU', None)) else 0
                
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
    
    # 处理最后一个活动
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
    
    return pd.DataFrame(activities_clean)


def parse_simple_format(df_raw):
    """解析简化格式（每行一个活动）"""
    # 假设列名：活动名, 付费总额, 付费人数, 付费率, ARPPU, ARPU, 超R付费额, 小R付费额
    df = df_raw.copy()
    
    # 重命名列（如果需要）
    col_mapping = {
        '活动名': '活动',
        '活动名称': '活动',
        '付费总额': '总付费额',
        '付费arpu': '付费ARPU',
        '付费arppu': 'ARPPU',
    }
    df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns}, inplace=True)
    
    # 计算超R收入占比（如果有超R付费额）
    if '超R付费额' in df.columns and '总付费额' in df.columns:
        df['超R收入占比'] = df['超R付费额'] / df['总付费额'] * 100
    
    return df


# ============ 主分析函数 ============

def analyze_activities(df_raw_activities, output_dir='.'):
    """分析活动数据并生成报告"""
    
    # 同名活动合并
    df_raw_activities['基础活动名'] = df_raw_activities['活动'].apply(extract_base_name)
    
    agg_cols = {
        '总付费额': 'sum',
        '付费人数': 'sum',
        '付费率': 'mean',
        '付费ARPU': 'mean',
        'ARPPU': 'mean',
        '节日时间': 'first',
        '投放内容': 'first',
        '活动': lambda x: list(x)
    }
    
    # 添加可选的R级数据聚合
    if '小R付费率' in df_raw_activities.columns:
        agg_cols['小R付费率'] = 'mean'
        agg_cols['小R付费额'] = 'sum'
    if '超R付费率' in df_raw_activities.columns:
        agg_cols['超R付费率'] = 'mean'
        agg_cols['超R付费额'] = 'sum'
    
    df_grouped = df_raw_activities.groupby('基础活动名').agg(agg_cols).reset_index()
    df_grouped['上线次数'] = df_grouped['活动'].apply(len)
    df_grouped['原始活动'] = df_grouped['活动'].apply(lambda x: ', '.join(x))
    df_grouped['活动'] = df_grouped['基础活动名']
    
    # 计算单次平均付费额
    df_grouped['累计总付费额'] = df_grouped['总付费额']
    df_grouped['单次平均付费额'] = df_grouped['总付费额'] / df_grouped['上线次数']
    
    df = df_grouped.copy()
    print(f"原始活动数: {len(df_raw_activities)}, 合并后活动数: {len(df)}")
    
    # 计算超R收入占比
    if '超R付费额' in df.columns:
        df['超R收入占比'] = df['超R付费额'] / df['累计总付费额'] * 100
    else:
        df['超R收入占比'] = 65  # 默认值
    
    # 计算各维度得分
    df['付费深度得分'] = df['ARPPU'].apply(score_arppu)
    df['转化广度得分'] = df['付费率'].apply(score_pay_rate)
    df['综合变现得分'] = df['付费ARPU'].apply(score_arpu)
    df['R级健康度得分'] = df['超R收入占比'].apply(score_r_health)
    
    # 综合得分
    df['综合得分'] = (
        df['付费深度得分'] * 0.40 +
        df['转化广度得分'] * 0.30 +
        df['综合变现得分'] * 0.20 +
        df['R级健康度得分'] * 0.10
    )
    
    df['等级'] = df['综合得分'].apply(get_grade)
    df['梯队'] = df['综合得分'].apply(get_tier)
    df = df.sort_values('综合得分', ascending=False)
    
    # 生成可视化
    generate_charts(df, output_dir)
    
    # 导出Excel
    export_cols = ['活动', '上线次数', '梯队', '等级', '综合得分',
                   '付费深度得分', '转化广度得分', '综合变现得分', 'R级健康度得分',
                   'ARPPU', '付费率', '付费ARPU', '超R收入占比',
                   '单次平均付费额', '累计总付费额', '投放内容', '原始活动']
    export_cols = [c for c in export_cols if c in df.columns]
    
    output_xlsx = os.path.join(output_dir, '活动评级结果.xlsx')
    df[export_cols].to_excel(output_xlsx, index=False)
    print(f'数据已保存至: {output_xlsx}')
    
    # 打印结果摘要
    print_summary(df)
    
    return df


def generate_charts(df, output_dir):
    """生成可视化图表"""
    
    fig = plt.figure(figsize=(18, 14))
    fig.suptitle('节日活动付费效果评级分析\n(付费深度40% + 转化广度30% + 综合变现20% + R级健康10%)', 
                 fontsize=14, fontweight='bold')
    
    colors = {'S': '#2ecc71', 'A': '#3498db', 'B': '#f39c12', 'C': '#e74c3c', 'D': '#95a5a6'}
    tier_colors = {'T1': '#2ecc71', 'T2': '#f39c12', 'T3': '#e74c3c'}
    
    # 图1: 综合评分排名
    ax1 = fig.add_subplot(2, 2, 1)
    top15 = df.head(15)
    bar_colors = [colors[g] for g in top15['等级']]
    bars = ax1.barh(range(len(top15)), top15['综合得分'], color=bar_colors)
    ax1.set_yticks(range(len(top15)))
    ax1.set_yticklabels(top15['活动'], fontsize=9)
    ax1.set_xlabel('综合得分')
    ax1.set_title('综合评分排名 (Top 15)')
    ax1.set_xlim(0, 100)
    for i, (bar, score, grade, tier) in enumerate(zip(bars, top15['综合得分'], top15['等级'], top15['梯队'])):
        ax1.text(bar.get_width() + 1, i, f'{score:.0f}({grade}/{tier})', va='center', fontsize=8)
    ax1.axvline(x=85, color='green', linestyle='--', alpha=0.5, label='S级线')
    ax1.axvline(x=75, color='blue', linestyle='--', alpha=0.5, label='A级线')
    ax1.axvline(x=65, color='orange', linestyle='--', alpha=0.5, label='B级线')
    ax1.invert_yaxis()
    ax1.legend(loc='lower right', fontsize=8)
    
    # 图2: 雷达图
    ax2 = fig.add_subplot(2, 2, 2, polar=True)
    categories = ['付费深度\n(ARPPU)', '转化广度\n(付费率)', '综合变现\n(ARPU)', 'R级健康度']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ax2.set_theta_offset(np.pi / 2)
    ax2.set_theta_direction(-1)
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories, fontsize=9)
    
    line_colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    for idx, (_, row) in enumerate(df.head(4).iterrows()):
        values = [row['付费深度得分'], row['转化广度得分'], row['综合变现得分'], row['R级健康度得分']]
        values += values[:1]
        ax2.plot(angles, values, 'o-', linewidth=2, label=row['活动'][:8], color=line_colors[idx])
        ax2.fill(angles, values, alpha=0.1, color=line_colors[idx])
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
    ax2.set_title('Top 4活动四维度对比', y=1.08)
    
    # 图3: ARPPU vs 付费率 散点图
    ax3 = fig.add_subplot(2, 2, 3)
    sizes = df['单次平均付费额']/1500 + 50
    scatter = ax3.scatter(df['付费率'], df['ARPPU'],
                          s=sizes, c=[tier_colors[t] for t in df['梯队']],
                          alpha=0.7, edgecolors='black', zorder=5)
    
    for i, (idx, row) in enumerate(df.iterrows()):
        short_name = row['活动'][:6]
        offset_x = 0.1 + (i % 3) * 0.05
        offset_y = 2 if i % 2 == 0 else -3
        ax3.annotate(short_name, (row['付费率'], row['ARPPU']),
                     xytext=(offset_x, offset_y), textcoords='offset points',
                     fontsize=6, ha='left', va='center', zorder=6,
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.7, edgecolor='none'))
    
    ax3.set_xlabel('转化广度 (付费率%)', fontsize=10)
    ax3.set_ylabel('付费深度 (ARPPU)', fontsize=10)
    ax3.set_title('付费深度 vs 转化广度\n(气泡大小=单次平均付费额，颜色=梯队)', fontsize=11)
    
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#2ecc71', label='T1 (≥80分)'),
                       Patch(facecolor='#f39c12', label='T2 (65-79分)'),
                       Patch(facecolor='#e74c3c', label='T3 (<65分)')]
    ax3.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    # 图4: 各维度得分对比
    ax4 = fig.add_subplot(2, 2, 4)
    top10 = df.head(10)
    x = np.arange(len(top10))
    width = 0.2
    
    ax4.bar(x - 1.5*width, top10['付费深度得分'], width, label='付费深度(40%)', color='#3498db')
    ax4.bar(x - 0.5*width, top10['转化广度得分'], width, label='转化广度(30%)', color='#2ecc71')
    ax4.bar(x + 0.5*width, top10['综合变现得分'], width, label='综合变现(20%)', color='#f39c12')
    ax4.bar(x + 1.5*width, top10['R级健康度得分'], width, label='R级健康(10%)', color='#9b59b6')
    
    ax4.set_xlabel('活动')
    ax4.set_ylabel('得分')
    ax4.set_title('Top 10活动各维度得分对比')
    ax4.set_xticks(x)
    ax4.set_xticklabels([name[:6] for name in top10['活动']], rotation=45, ha='right', fontsize=8)
    ax4.legend(loc='upper right', fontsize=8)
    ax4.set_ylim(0, 110)
    
    plt.tight_layout()
    output_png = os.path.join(output_dir, '活动评级分析图表.png')
    plt.savefig(output_png, dpi=150, bbox_inches='tight')
    print(f'图表已保存至: {output_png}')


def print_summary(df):
    """打印结果摘要"""
    print()
    print('=== 评级结果摘要 ===')
    print(f"T1梯队活动: {len(df[df['梯队']=='T1'])}个")
    print(f"T2梯队活动: {len(df[df['梯队']=='T2'])}个")
    print(f"T3梯队活动: {len(df[df['梯队']=='T3'])}个")
    print()
    print('Top 5活动:')
    for i, (_, row) in enumerate(df.head(5).iterrows()):
        print(f"  {i+1}. {row['活动']} - {row['综合得分']:.0f}分 ({row['等级']}/{row['梯队']})")


# ============ 主入口 ============

def main():
    parser = argparse.ArgumentParser(description='节日活动付费效果评级系统')
    parser.add_argument('--input', '-i', required=True, help='输入Excel文件路径')
    parser.add_argument('--output', '-o', default='.', help='输出目录（默认当前目录）')
    parser.add_argument('--sheet', '-s', default=None, help='Excel Sheet名称')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f'错误: 文件不存在 - {args.input}')
        sys.exit(1)
    
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    print(f'正在分析: {args.input}')
    df_raw = parse_activity_data(args.input, args.sheet)
    analyze_activities(df_raw, args.output)


if __name__ == '__main__':
    main()
