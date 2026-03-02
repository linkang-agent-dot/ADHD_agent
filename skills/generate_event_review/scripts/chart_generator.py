"""
chart_generator.py - 节日总结 Wiki 图表自动生成器

功能：
  1. 解析标准化 JSON 输入数据
  2. 生成 3 张高清图表：
     - 1_Revenue_Trend.png   (核心大盘趋势折线图)
     - 2_Module_Structure.png (模块营收堆叠面积图)
     - 3_User_Growth.png     (用户分层 ARPU 分组柱状图)
  3. 计算关键指标变化率（同比/环比）

用法：
  python chart_generator.py --input data.json [--output_dir report_images/event_name]
  或作为模块导入：
    from chart_generator import generate_all_charts
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')  # 非交互式后端，适合服务器环境
import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# 全局配置
# ============================================================

def setup_matplotlib():
    """配置 matplotlib 中文字体和全局样式"""
    plt.style.use('ggplot')
    plt.rcParams['font.sans-serif'] = [
        'SimHei', 'Microsoft YaHei', 'Noto Sans CJK SC',
        'PingFang SC', 'Arial', 'DejaVu Sans'
    ]
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.dpi'] = 150
    plt.rcParams['savefig.bbox'] = 'tight'


def _check_chinese_font_available() -> bool:
    """检查系统是否有可用的中文字体"""
    from matplotlib.font_manager import fontManager
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'Noto Sans CJK SC', 'PingFang SC']
    for font in fontManager.ttflist:
        if font.name in chinese_fonts:
            return True
    return False


# ============================================================
# 数据校验
# ============================================================

def validate_input(data: dict) -> list[str]:
    """
    校验输入数据完整性，返回错误列表。
    空列表表示校验通过。
    """
    errors = []

    # 检查必需字段
    required_keys = ['meta', 'metrics_trend', 'module_trend', 'user_tier_trend', 'sub_activity_detail', 'module_classification']
    for key in required_keys:
        if key not in data:
            errors.append(f"缺少必需字段: {key}")

    if errors:
        return errors

    # 检查 meta
    meta = data['meta']
    if not meta.get('event_name'):
        errors.append("meta.event_name 不能为空")
    if not meta.get('benchmark_event'):
        errors.append("meta.benchmark_event 不能为空")

    # 检查 metrics_trend 长度
    if len(data['metrics_trend']) < 6:
        errors.append(f"metrics_trend 至少需要 6 个数据点，当前只有 {len(data['metrics_trend'])} 个")

    # 检查 module_trend 长度
    if len(data['module_trend']) < 6:
        errors.append(f"module_trend 至少需要 6 个数据点，当前只有 {len(data['module_trend'])} 个")

    # 检查 user_tier_trend 长度
    if len(data['user_tier_trend']) < 2:
        errors.append(f"user_tier_trend 至少需要 2 个数据点，当前只有 {len(data['user_tier_trend'])} 个")

    # 检查每条 metrics_trend 记录
    for i, item in enumerate(data['metrics_trend']):
        for field in ['event', 'revenue', 'arpu', 'pay_rate']:
            if field not in item:
                errors.append(f"metrics_trend[{i}] 缺少字段: {field}")

    # 检查每条 module_trend 记录
    for i, item in enumerate(data['module_trend']):
        for field in ['event', 'appearance', 'minigame', 'hybrid']:
            if field not in item:
                errors.append(f"module_trend[{i}] 缺少字段: {field}")

    # 检查每条 user_tier_trend 记录
    for i, item in enumerate(data['user_tier_trend']):
        for field in ['event', 'super_r', 'big_r', 'mid_r']:
            if field not in item:
                errors.append(f"user_tier_trend[{i}] 缺少字段: {field}")

    # 检查 sub_activity_detail
    for i, item in enumerate(data['sub_activity_detail']):
        for field in ['name', 'type', 'revenue', 'status', 'reason']:
            if field not in item:
                errors.append(f"sub_activity_detail[{i}] 缺少字段: {field}")
        if item.get('status') not in ('Keep', 'Optimize', None):
            errors.append(f"sub_activity_detail[{i}].status 必须为 'Keep' 或 'Optimize'，当前值: {item.get('status')}")

    # 检查 module_classification
    valid_modules = {'外显', '小游戏', '养成', '混合'}
    module_aliases = {'养成线': '养成', '外显类': '外显', '小游戏类': '小游戏', '混合类': '混合', '混合/养成': '混合'}
    mc = data['module_classification']
    if not mc:
        errors.append("module_classification 至少需要 1 条分类映射")
    else:
        for i, item in enumerate(mc):
            if not item.get('name'):
                errors.append(f"module_classification[{i}] 缺少字段: name")
            if not item.get('module'):
                errors.append(f"module_classification[{i}] 缺少字段: module")
            else:
                mod = item['module']
                # 自动修正别名
                if mod in module_aliases:
                    item['module'] = module_aliases[mod]
                elif mod not in valid_modules:
                    errors.append(
                        f"module_classification[{i}].module 必须为 {valid_modules} 之一，"
                        f"当前值: {item['module']}"
                    )

    return errors


# ============================================================
# 指标计算
# ============================================================

def compute_metrics(data: dict) -> dict:
    """
    计算关键指标变化率（同比/环比），返回用于报告填充的计算结果。
    """
    metrics = data['metrics_trend']
    meta = data['meta']

    # 找到当期活动和对标活动
    current_event_name = meta['event_name']
    benchmark_event_name = meta['benchmark_event']

    current = None
    benchmark = None
    previous = None  # 环比对象（当期前一个活动）

    for i, m in enumerate(metrics):
        if m['event'] == current_event_name or i == len(metrics) - 2:
            # 如果名称匹配，或者是倒数第二个（当期数据默认位置）
            current = m
            if i > 0:
                previous = metrics[i - 1]
        if m['event'] == benchmark_event_name or i == len(metrics) - 1:
            benchmark = m

    # 如果没找到精确匹配，用位置推断
    if current is None:
        current = metrics[-2] if len(metrics) >= 2 else metrics[-1]
    if benchmark is None:
        benchmark = metrics[-1]
    if previous is None and len(metrics) >= 3:
        previous = metrics[-3]

    result = {
        'current': current,
        'benchmark': benchmark,
        'previous': previous,
    }

    # 同比变化率 (YoY)
    if benchmark and benchmark['revenue'] > 0:
        result['yoy_revenue_change'] = (current['revenue'] - benchmark['revenue']) / benchmark['revenue'] * 100
        result['yoy_arpu_change'] = (current['arpu'] - benchmark['arpu']) / benchmark['arpu'] * 100
    else:
        result['yoy_revenue_change'] = None
        result['yoy_arpu_change'] = None

    # 环比变化率 (MoM)
    if previous and previous['revenue'] > 0:
        result['mom_revenue_change'] = (current['revenue'] - previous['revenue']) / previous['revenue'] * 100
        result['mom_arpu_change'] = (current['arpu'] - previous['arpu']) / previous['arpu'] * 100
    else:
        result['mom_revenue_change'] = None
        result['mom_arpu_change'] = None

    # 趋势判断（基于最近6个月的营收斜率 + 形态分析）
    revenues = [m['revenue'] for m in metrics[:-1]]  # 排除对标点
    if len(revenues) >= 3:
        x_fit = np.arange(len(revenues))
        slope, _ = np.polyfit(x_fit, revenues, 1)
        result['trend_slope'] = slope

        # V型反转检测：找到最低点，判断前半段下降、后半段上升
        min_idx = int(np.argmin(revenues))
        min_val = revenues[min_idx]
        max_val = max(revenues)

        # 检查是否存在 V 型形态：
        # 条件1: 最低点不在首尾（说明有先降后升）
        # 条件2: 最低点前有显著下降（从起点下降超过30%）
        # 条件3: 最低点后有显著回升（从谷底回升超过30%）
        is_v_shape = False
        if 0 < min_idx < len(revenues) - 1:
            drop_from_start = (revenues[0] - min_val) / revenues[0] if revenues[0] > 0 else 0
            rise_from_bottom = (revenues[-1] - min_val) / min_val if min_val > 0 else 0
            if drop_from_start > 0.3 and rise_from_bottom > 0.3:
                is_v_shape = True

        # 判断近期趋势（后半段斜率）
        mid = len(revenues) // 2
        recent_revenues = revenues[mid:]
        recent_x = np.arange(len(recent_revenues))
        recent_slope, _ = np.polyfit(recent_x, recent_revenues, 1)

        if is_v_shape:
            result['trend_pattern'] = 'V型反转'
            result['trend_description'] = '经历前期下滑后强势反弹，整体呈V型反转态势'
        elif recent_slope > 0 and slope > 0:
            result['trend_pattern'] = '上升通道'
            result['trend_description'] = '营收持续走高，处于健康上升通道'
        elif recent_slope > 0 and slope <= 0:
            # 整体斜率为负但近期在上升 -> 恢复中
            result['trend_pattern'] = '触底回升'
            result['trend_description'] = '整体仍低于高点，但近期呈恢复上升态势'
        elif recent_slope < 0 and slope < 0:
            result['trend_pattern'] = '下降通道'
            result['trend_description'] = '营收呈下滑趋势，需关注核心指标健康度'
        elif recent_slope < 0 and slope >= 0:
            result['trend_pattern'] = '冲高回落'
            result['trend_description'] = '整体处于高位但近期出现回调，需观察后续走势'
        else:
            result['trend_pattern'] = '横盘震荡'
            result['trend_description'] = '营收波动较小，处于平稳运行状态'
    else:
        result['trend_slope'] = 0
        result['trend_pattern'] = '数据不足'
        result['trend_description'] = '历史数据点不足，无法判断趋势'

    # 模块占比计算
    module_current = None
    module_data = data['module_trend']
    for m in module_data:
        if m['event'] == current_event_name:
            module_current = m
            break
    if module_current is None and len(module_data) >= 2:
        module_current = module_data[-2]  # 倒数第二个（排除对标）
    if module_current is None:
        module_current = module_data[-1]

    total_module = module_current['appearance'] + module_current['minigame'] + module_current['hybrid']
    if total_module > 0:
        result['module_share'] = {
            'appearance': module_current['appearance'] / total_module * 100,
            'minigame': module_current['minigame'] / total_module * 100,
            'hybrid': module_current['hybrid'] / total_module * 100,
        }
    else:
        result['module_share'] = {'appearance': 0, 'minigame': 0, 'hybrid': 0}

    return result


# ============================================================
# 图表生成
# ============================================================

# 配色方案
COLORS = {
    'primary': '#1a535c',
    'secondary': '#4ecdc4',
    'accent': '#ff6b6b',
    'warn': '#ffe66d',
    'appearance': '#ff9999',
    'minigame': '#66b3ff',
    'hybrid': '#99ff99',
    'highlight': '#d62828',
}


def generate_chart_1_revenue_trend(data: dict, output_dir: str) -> str:
    """
    图1: 核心大盘趋势折线图
    X轴: 活动时间节点
    Y轴(左): 总营收
    标注: 趋势线、关键数据点
    """
    metrics = data['metrics_trend']
    use_cn = _check_chinese_font_available()

    events = [m['event'] for m in metrics]
    revenues = [m['revenue'] for m in metrics]
    arpus = [m['arpu'] for m in metrics]

    # 分离当期数据和对标数据
    main_events = events[:-1]
    main_revenues = revenues[:-1]
    benchmark_label = events[-1]
    benchmark_revenue = revenues[-1]

    x_main = np.arange(len(main_events))
    revenue_unit = [r / 10000 for r in main_revenues]
    benchmark_unit = benchmark_revenue / 10000

    fig, ax1 = plt.subplots(figsize=(13, 6.5))

    # 绘制主趋势线
    line1 = ax1.plot(x_main, revenue_unit, marker='o', linewidth=2.5,
                     color=COLORS['accent'], label='营收 (万$)' if use_cn else 'Revenue ($10k)',
                     markersize=8, zorder=5)

    # 高亮当期（倒数第二个点 = 最新活动）
    current_idx = len(main_events) - 1
    ax1.plot(current_idx, revenue_unit[current_idx], marker='*', markersize=18,
             color=COLORS['highlight'], zorder=6)

    # 添加对标虚线参考
    ax1.axhline(y=benchmark_unit, color=COLORS['secondary'], linestyle='--',
                alpha=0.7, linewidth=1.5,
                label=f'{benchmark_label}: {benchmark_unit:.1f}万' if use_cn
                else f'{benchmark_label}: {benchmark_unit:.1f}')

    # 趋势拟合线
    if len(x_main) >= 3:
        z = np.polyfit(x_main, revenue_unit, 1)
        p = np.poly1d(z)
        ax1.plot(x_main, p(x_main), "r--", alpha=0.4, linewidth=1.5,
                 label='趋势线' if use_cn else 'Trend Line')

    # 数据标注（自动避免顶部截断）
    max_revenue = max(revenue_unit)
    ax1.set_ylim(0, max_revenue * 1.25)  # 留出25%空间给标注

    for i, val in enumerate(revenue_unit):
        offset_y = 12 if i % 2 == 0 else -18
        ax1.annotate(f'{val:.1f}', (x_main[i], val),
                     textcoords="offset points", xytext=(0, offset_y),
                     ha='center', fontsize=9, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # ARPU 副轴
    ax2 = ax1.twinx()
    ax2.plot(x_main, [m['arpu'] for m in metrics[:-1]], marker='s', linewidth=1.5,
             color=COLORS['primary'], alpha=0.6, linestyle='--',
             label='ARPU ($)', markersize=6)
    ax2.set_ylabel('ARPU ($)', color=COLORS['primary'], fontsize=11)
    ax2.tick_params(axis='y', labelcolor=COLORS['primary'])

    # 样式设置
    ax1.set_xticks(x_main)
    ax1.set_xticklabels(main_events, fontsize=10, fontweight='bold', rotation=15, ha='right')
    ax1.set_ylabel('营收 (万$)' if use_cn else 'Revenue ($10k)', color=COLORS['accent'], fontsize=12)
    ax1.tick_params(axis='y', labelcolor=COLORS['accent'])
    title = f'{data["meta"]["event_name"]} - 核心大盘趋势' if use_cn else f'{data["meta"]["event_name"]} - Key Metrics Trend'
    ax1.set_title(title, pad=20, fontsize=15, fontweight='bold')

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    ax1.grid(True, alpha=0.3)
    plt.tight_layout()

    filepath = os.path.join(output_dir, '1_Revenue_Trend.png')
    plt.savefig(filepath)
    plt.close()
    return filepath


def generate_chart_2_module_structure(data: dict, output_dir: str) -> str:
    """
    图2: 模块营收堆叠面积图
    X轴: 活动时间节点
    Y轴: 各模块营收占比
    """
    modules = data['module_trend']
    use_cn = _check_chinese_font_available()

    # 排除最后一个对标数据点（如果 module_trend 比 metrics_trend 少则全部使用）
    events = [m['event'] for m in modules]
    appearance = [m['appearance'] / 10000 for m in modules]
    minigame = [m['minigame'] / 10000 for m in modules]
    hybrid = [m['hybrid'] / 10000 for m in modules]

    x = np.arange(len(events))

    labels = ['外显类', '小游戏', '混合/养成'] if use_cn else ['Appearance', 'Mini-games', 'Hybrid']

    fig, ax = plt.subplots(figsize=(13, 6.5))

    ax.stackplot(x, appearance, minigame, hybrid,
                 labels=labels,
                 colors=[COLORS['appearance'], COLORS['minigame'], COLORS['hybrid']],
                 alpha=0.85)

    # 在顶部标注总量
    totals = [a + g + h for a, g, h in zip(appearance, minigame, hybrid)]
    for i, total in enumerate(totals):
        ax.annotate(f'{total:.1f}', (x[i], total),
                    textcoords="offset points", xytext=(0, 8),
                    ha='center', fontsize=9, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(events, fontsize=10, fontweight='bold', rotation=15, ha='right')
    title = f'{data["meta"]["event_name"]} - 模块营收结构' if use_cn else f'{data["meta"]["event_name"]} - Module Revenue Structure'
    ax.set_title(title, pad=20, fontsize=15, fontweight='bold')
    ax.set_ylabel('营收 (万$)' if use_cn else 'Revenue ($10k)', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    filepath = os.path.join(output_dir, '2_Module_Structure.png')
    plt.savefig(filepath)
    plt.close()
    return filepath


def generate_chart_3_user_growth(data: dict, output_dir: str) -> str:
    """
    图3: 用户分层 ARPU 分组柱状图
    X轴: 用户层级 (超R / 大R / 中R)
    Y轴: ARPU
    分组: 各活动时间节点
    """
    tiers = data['user_tier_trend']
    use_cn = _check_chinese_font_available()

    tier_labels = ['超R', '大R', '中R'] if use_cn else ['Super R', 'Big R', 'Mid R']
    event_names = [t['event'] for t in tiers]

    # 每个活动对应 [super_r, big_r, mid_r]
    tier_data = []
    for t in tiers:
        tier_data.append([t['super_r'], t['big_r'], t['mid_r']])

    n_events = len(event_names)
    n_tiers = len(tier_labels)
    x = np.arange(n_tiers)
    width = 0.8 / n_events  # 动态计算柱宽

    # 配色循环
    bar_colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent'],
                  COLORS['warn'], '#9b59b6', '#3498db']

    fig, ax = plt.subplots(figsize=(11, 6.5))

    for i, (event_name, values) in enumerate(zip(event_names, tier_data)):
        offset = (i - n_events / 2 + 0.5) * width
        bars = ax.bar(x + offset, values, width, label=event_name,
                      color=bar_colors[i % len(bar_colors)], alpha=0.9)

        # 数据标注
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylabel('ARPU ($)', fontsize=12)
    title = f'{data["meta"]["event_name"]} - 用户分层 ARPU 对比' if use_cn else f'{data["meta"]["event_name"]} - User Tier ARPU Comparison'
    ax.set_title(title, fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(tier_labels, fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    filepath = os.path.join(output_dir, '3_User_Growth.png')
    plt.savefig(filepath)
    plt.close()
    return filepath


# ============================================================
# 主入口
# ============================================================

def generate_all_charts(data: dict, output_dir: str | None = None) -> dict:
    """
    根据输入数据生成所有图表和计算指标。

    Args:
        data: 符合 input_template.json 规范的数据字典
        output_dir: 图片输出目录。默认为 report_images/{event_name}/

    Returns:
        dict: {
            'charts': [chart1_path, chart2_path, chart3_path],
            'metrics': computed_metrics_dict,
            'output_dir': output_dir
        }
    """
    setup_matplotlib()

    # 校验
    errors = validate_input(data)
    if errors:
        raise ValueError(f"输入数据校验失败:\n" + "\n".join(f"  - {e}" for e in errors))

    # 确定输出目录
    if output_dir is None:
        event_name_safe = data['meta']['event_name'].replace(' ', '_').replace('/', '_')
        output_dir = os.path.join('report_images', event_name_safe)

    os.makedirs(output_dir, exist_ok=True)

    # 计算指标
    metrics = compute_metrics(data)

    # 生成图表
    chart1 = generate_chart_1_revenue_trend(data, output_dir)
    chart2 = generate_chart_2_module_structure(data, output_dir)
    chart3 = generate_chart_3_user_growth(data, output_dir)

    print(f"[OK] 3 张图表已保存至: {output_dir}")
    print(f"  - {chart1}")
    print(f"  - {chart2}")
    print(f"  - {chart3}")

    return {
        'charts': [chart1, chart2, chart3],
        'metrics': metrics,
        'output_dir': output_dir,
    }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='节日总结图表自动生成器')
    parser.add_argument('--input', '-i', required=True, help='输入 JSON 数据文件路径')
    parser.add_argument('--output_dir', '-o', default=None, help='图片输出目录（默认: report_images/{event_name}/）')
    args = parser.parse_args()

    # 读取输入数据
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] 输入文件不存在: {input_path}")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    try:
        result = generate_all_charts(data, args.output_dir)
        print(f"\n[DONE] 趋势形态: {result['metrics'].get('trend_pattern', 'N/A')}")
        print(f"[DONE] 趋势描述: {result['metrics'].get('trend_description', 'N/A')}")

        yoy = result['metrics'].get('yoy_revenue_change')
        if yoy is not None:
            print(f"[DONE] 同比营收变化: {yoy:+.1f}%")

        mom = result['metrics'].get('mom_revenue_change')
        if mom is not None:
            print(f"[DONE] 环比营收变化: {mom:+.1f}%")

    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
