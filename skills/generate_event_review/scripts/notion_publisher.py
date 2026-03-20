"""
notion_publisher.py - 生成 Notion 版本的复盘报告内容

功能：
  1. 接收标准化 JSON 数据 + compute_metrics 计算结果
  2. 生成 Notion-flavored Markdown 格式的报告内容字符串
  3. 供 Agent 通过 Notion MCP 的 create-pages 工具发布到 Notion

用法（作为模块导入）：
    from notion_publisher import generate_notion_content
    content = generate_notion_content(data, metrics)

    # 然后通过 Notion MCP create-pages 工具发布:
    # parent: {"page_id": "<parent_page_id>"}
    # pages: [{"properties": {"title": "<标题>"}, "content": content}]
"""

import json
import os
from datetime import datetime
from typing import Any


def _fmt_revenue(value: float) -> str:
    """格式化营收为千分位字符串"""
    return f"{value:,.0f}"


def _fmt_pct(value: float | None, with_sign: bool = True) -> str:
    """格式化百分比"""
    if value is None:
        return "N/A"
    sign = "+" if value > 0 and with_sign else ""
    return f"{sign}{value:.1f}%"


def _color_pct(value: float | None, with_sign: bool = True) -> str:
    """带颜色的百分比（Notion span 格式）"""
    if value is None:
        return "N/A"
    text = _fmt_pct(value, with_sign)
    if value > 0:
        return f'<span color="red">**{text}**</span>'
    elif value < 0:
        return f'<span color="blue">**{text}**</span>'
    else:
        return text


def _summary_text(yoy_revenue: float | None) -> tuple[str, str]:
    """
    根据同比营收变化率生成 Executive Summary 文案。
    返回 (短摘要, 详细描述前缀)
    """
    if yoy_revenue is None:
        return ("数据不足，无法判断同比表现", "")
    if yoy_revenue > 20:
        return (
            "活动表现强劲，大幅超越同期",
            "表现强劲，大幅超越同期。"
        )
    elif yoy_revenue > 0:
        return (
            "活动稳健增长，略优于同期",
            "稳健增长，略优于同期。"
        )
    elif yoy_revenue > -20:
        return (
            "活动表现平稳但略低于同期，需关注",
            "表现平稳但略低于同期，需关注。"
        )
    else:
        return (
            "活动表现不及预期，需深入分析原因",
            "表现不及预期，需深入分析原因。"
        )


def compute_metrics(data: dict) -> dict:
    """
    从标准化输入数据自动计算所有指标，包括趋势判断。
    调用方无需手动构造 metrics dict。

    逻辑：
    - metrics_trend 数组中，与 meta.event_name 匹配的为当期
    - 与 meta.benchmark_event 匹配的为同比对标
    - 当期在数组中的前一个为环比对象
    - trend_pattern 和 trend_description 从近6期营收自动判断

    Returns:
        dict: 可直接传给 generate_notion_content / generate_wiki_content
    """
    meta = data['meta']
    event_name = meta['event_name']
    benchmark_event = meta['benchmark_event']
    mt = data['metrics_trend']

    # 找当期、对标、环比
    current = None
    benchmark = None
    previous = None
    current_idx = -1

    for i, m in enumerate(mt):
        if m['event'] == event_name:
            current = m
            current_idx = i
        if m['event'] == benchmark_event:
            benchmark = m

    # 环比：当期在数组中的前一个（排除对标本身）
    if current_idx > 0:
        prev_candidate = mt[current_idx - 1]
        if prev_candidate['event'] != benchmark_event:
            previous = prev_candidate
        elif current_idx > 1:
            previous = mt[current_idx - 2]

    if current is None:
        # fallback: 取第一个作为当期
        current = mt[0]
    if benchmark is None:
        # fallback: 取最后一个作为对标
        benchmark = mt[-1]

    # 计算同比/环比
    yoy_rev = ((current['revenue'] - benchmark['revenue']) / benchmark['revenue'] * 100) if benchmark['revenue'] > 0 else None
    yoy_arpu = ((current['arpu'] - benchmark['arpu']) / benchmark['arpu'] * 100) if benchmark['arpu'] > 0 else None
    mom_rev = ((current['revenue'] - previous['revenue']) / previous['revenue'] * 100) if previous and previous['revenue'] > 0 else None
    mom_arpu = ((current['arpu'] - previous['arpu']) / previous['arpu'] * 100) if previous and previous['arpu'] > 0 else None

    # 模块占比
    module_share = {}
    mc = None
    for m in data.get('module_trend', []):
        if m['event'] == event_name:
            mc = m
            break
    if mc is None and data.get('module_trend'):
        mc = data['module_trend'][-1]
    if mc:
        total_mod = mc.get('appearance', 0) + mc.get('minigame', 0) + mc.get('hybrid', 0)
        if total_mod > 0:
            module_share = {
                'appearance': mc['appearance'] / total_mod * 100,
                'minigame': mc['minigame'] / total_mod * 100,
                'hybrid': mc['hybrid'] / total_mod * 100,
            }

    # 趋势判断：从近期营收序列自动推断
    # 取当期及之前的数据点（不含对标）
    revenues = [m['revenue'] for m in mt if m['event'] != benchmark_event]
    trend_pattern, trend_description = _detect_trend(revenues, current, previous)

    return {
        'current': current,
        'benchmark': benchmark,
        'previous': previous,
        'yoy_revenue_change': yoy_rev,
        'yoy_arpu_change': yoy_arpu,
        'mom_revenue_change': mom_rev,
        'mom_arpu_change': mom_arpu,
        'module_share': module_share,
        'trend_pattern': trend_pattern,
        'trend_description': trend_description,
    }


def _detect_trend(revenues: list[float], current: dict, previous: dict | None) -> tuple[str, str]:
    """
    从营收序列自动判断趋势类型和描述。

    Returns:
        (trend_pattern, trend_description)
    """
    if len(revenues) < 3:
        return ('数据不足', '历史数据点不足，无法判断趋势')

    # 计算各段变化
    n = len(revenues)
    cur_rev = current['revenue']

    # 近3期趋势
    recent_3 = revenues[-3:]
    recent_up = all(recent_3[i] <= recent_3[i+1] for i in range(len(recent_3)-1))
    recent_down = all(recent_3[i] >= recent_3[i+1] for i in range(len(recent_3)-1))

    # 整体趋势（线性回归斜率方向）
    avg_first_half = sum(revenues[:n//2]) / max(len(revenues[:n//2]), 1)
    avg_second_half = sum(revenues[n//2:]) / max(len(revenues[n//2:]), 1)
    overall_up = avg_second_half > avg_first_half * 1.05

    # 峰值位置
    peak_val = max(revenues)
    peak_idx = revenues.index(peak_val)
    is_peak_recent = peak_idx >= n - 2
    is_peak_mid = n // 4 <= peak_idx <= 3 * n // 4

    # 环比变化
    mom_change = ((cur_rev - previous['revenue']) / previous['revenue'] * 100) if previous and previous['revenue'] > 0 else 0

    # 判断模式
    if recent_up and overall_up:
        pattern = '持续上升'
        desc = '营收连续多期增长，整体处于上升通道'
    elif recent_down and not overall_up:
        pattern = '持续下滑'
        desc = '营收连续多期下降，需警惕下行趋势'
    elif overall_up and mom_change < -10:
        pattern = '冲高回落'
        desc = f'整体处于高位但环比下降 {mom_change:.1f}%，需观察是短期波动还是拐点信号'
    elif not overall_up and mom_change > 10:
        pattern = '触底反弹'
        desc = f'前期低迷但环比回升 {mom_change:+.1f}%，需持续观察反弹力度'
    elif is_peak_mid and cur_rev < peak_val * 0.85:
        pattern = '冲高回落'
        desc = f'峰值出现在中期，当前已回落至峰值的 {cur_rev/peak_val*100:.0f}%'
    elif abs(mom_change) < 5 and not recent_up and not recent_down:
        pattern = '横盘震荡'
        desc = '营收在一定区间内波动，无明显方向性趋势'
    else:
        # 默认：根据环比方向给出判断
        if mom_change > 0:
            pattern = '波动上行'
            desc = f'整体呈波动上行态势，环比增长 {mom_change:+.1f}%'
        else:
            pattern = '波动下行'
            desc = f'整体呈波动下行态势，环比下降 {mom_change:.1f}%'

    return (pattern, desc)


def _build_event_comparison_table(data: dict, event_name: str) -> str:
    """
    生成"节日整体对比"横向宽表。
    每列一个活动，行为：皮肤BUFF、付费总额、人均付费、付费率、ARPU、期间付费占比。
    """
    mt = data['metrics_trend']
    if len(mt) < 2:
        return ''

    # 表头：活动名
    header_cells = '<td></td>\n' + '\n'.join(f'<td>**{m["event"]}**</td>' for m in mt)

    # 皮肤BUFF行（可选）
    has_buff = any(m.get('skin_buff') for m in mt)
    buff_row = ''
    if has_buff:
        buff_cells = '<td>皮肤BUFF</td>\n' + '\n'.join(
            f'<td>{m.get("skin_buff", "-")}</td>' for m in mt)
        buff_row = f'<tr>\n{buff_cells}\n</tr>\n'

    # 付费总额行
    def _color_rev(m):
        v = m['revenue']
        is_current = m['event'] == event_name
        if is_current:
            return f'<span color="red">**\\${_fmt_revenue(v)}**</span>'
        if v >= 900000:
            return f'<span color="red">**\\${_fmt_revenue(v)}**</span>'
        elif v >= 700000:
            return f'<span color="blue">**\\${_fmt_revenue(v)}**</span>'
        return f'\\${_fmt_revenue(v)}'

    rev_cells = '<td>付费总额</td>\n' + '\n'.join(f'<td>{_color_rev(m)}</td>' for m in mt)
    rev_row = f'<tr>\n{rev_cells}\n</tr>'

    # 人均付费行（ARPPU）
    def _arppu_cell(m):
        v = m.get('arppu')
        if v is None:
            return '<td>-</td>'
        is_current = m['event'] == event_name
        if is_current or v >= 150:
            return f'<td><span color="red">**\\${v:.2f}**</span></td>'
        return f'<td>\\${v:.2f}</td>'

    arppu_cells = '<td>付费玩家人均付费</td>\n' + '\n'.join(_arppu_cell(m) for m in mt)
    arppu_row = f'<tr>\n{arppu_cells}\n</tr>'

    # 付费率行（分母=付费玩家数）
    def _calc_pay_rate(m):
        pp = m.get('paying_players')
        if pp and pp > 0:
            arppu = m.get('arppu')
            if arppu and arppu > 0:
                buyers = m['revenue'] / arppu
                return buyers / pp * 100
        return m.get('pay_rate', 0)

    def _pr_cell(m):
        v = _calc_pay_rate(m)
        is_current = m['event'] == event_name
        if is_current or v >= 33:
            return f'<td><span color="red">**{v:.2f}%**</span></td>'
        return f'<td>{v:.2f}%</td>'

    pr_cells = '<td>付费率</td>\n' + '\n'.join(_pr_cell(m) for m in mt)
    pr_row = f'<tr>\n{pr_cells}\n</tr>'

    # ARPU行（分母=付费玩家数）
    def _calc_arpu(m):
        pp = m.get('paying_players')
        if pp and pp > 0:
            return m['revenue'] / pp
        return m.get('arpu', 0)

    def _arpu_cell(m):
        v = _calc_arpu(m)
        is_current = m['event'] == event_name
        if is_current or v >= 50:
            return f'<td><span color="red">**\\${v:.2f}**</span></td>'
        elif v >= 40:
            return f'<td><span color="blue">**\\${v:.2f}**</span></td>'
        return f'<td>\\${v:.2f}</td>'

    arpu_cells = '<td>ARPU</td>\n' + '\n'.join(_arpu_cell(m) for m in mt)
    arpu_row = f'<tr>\n{arpu_cells}\n</tr>'

    # 期间付费占比行（可选）
    has_share = any(m.get('period_pay_share') for m in mt)
    share_row = ''
    if has_share:
        def _share_cell(m):
            v = m.get('period_pay_share')
            if v is None:
                return '<td>-</td>'
            is_current = m['event'] == event_name
            if is_current or v >= 45:
                return f'<td><span color="red">**{v:.2f}%**</span></td>'
            return f'<td>{v:.2f}%</td>'
        share_cells = '<td>期间付费占比</td>\n' + '\n'.join(_share_cell(m) for m in mt)
        share_row = f'<tr>\n{share_cells}\n</tr>\n'

    table = (
        '<table fit-page-width="true" header-row="true" header-column="true">\n'
        f'<tr>\n{header_cells}\n</tr>\n'
        f'{buff_row}'
        f'{rev_row}\n'
        f'{arppu_row}\n'
        f'{pr_row}\n'
        f'{arpu_row}\n'
        f'{share_row}'
        '</table>'
    )
    return table


def _build_tier_arpu_comparison_table(data: dict, event_name: str) -> str:
    """
    生成"节日ARPU对比"横向宽表。
    每列一个活动，行为：xiaoR、zhongR、daR、chaoR 的 ARPU。
    """
    tiers = data.get('user_tier_trend', [])
    if len(tiers) < 2:
        return ''

    # 表头
    header_cells = '<td></td>\n' + '\n'.join(f'<td>**{t["event"]}**</td>' for t in tiers)

    tier_keys = [
        ('small_r', 'xiaoR'),
        ('mid_r', 'zhongR'),
        ('big_r', 'daR'),
        ('super_r', 'chaoR'),
    ]

    rows = []
    for key, label in tier_keys:
        # 跳过全部为0/缺失的行
        vals = [t.get(key, 0) for t in tiers]
        if all(v == 0 for v in vals):
            continue

        def _tier_cell(t, k=key):
            v = t.get(k, 0)
            if v == 0:
                return '<td>-</td>'
            is_current = t['event'] == event_name
            # 高亮逻辑：当期 or 该行最大值
            max_val = max(tt.get(k, 0) for tt in tiers)
            if is_current:
                return f'<td><span color="red">**{v:.2f}**</span></td>'
            elif v == max_val and v > 0:
                return f'<td><span color="red">**{v:.2f}**</span></td>'
            return f'<td>{v:.2f}</td>'

        cells = f'<td>**{label}**</td>\n' + '\n'.join(_tier_cell(t) for t in tiers)
        rows.append(f'<tr>\n{cells}\n</tr>')

    if not rows:
        return ''

    table = (
        '<table fit-page-width="true" header-row="true" header-column="true">\n'
        f'<tr>\n{header_cells}\n</tr>\n'
        + '\n'.join(rows) + '\n</table>'
    )
    return table


def generate_notion_content(data: dict, metrics: dict) -> str:
    """
    生成 Notion-flavored Markdown 格式的完整报告内容。

    Args:
        data: 标准化输入数据（含 meta, metrics_trend, module_trend 等）
        metrics: compute_metrics() 的返回结果

    Returns:
        str: Notion-flavored Markdown 内容，可直接传给 Notion MCP create-pages
    """
    meta = data['meta']
    event_name = meta['event_name']
    benchmark_event = meta['benchmark_event']
    generated_at = datetime.now().strftime('%Y-%m-%d')

    current = metrics['current']
    benchmark = metrics['benchmark']
    previous = metrics.get('previous')

    yoy_rev = metrics.get('yoy_revenue_change')
    yoy_arpu = metrics.get('yoy_arpu_change')
    mom_rev = metrics.get('mom_revenue_change')
    mom_arpu = metrics.get('mom_arpu_change')

    summary_short, summary_prefix = _summary_text(yoy_rev)

    # ── Section 1: Executive Summary ──
    exec_summary_short = (
        f"{event_name}{summary_short}。"
        f"总营收 **${_fmt_revenue(current['revenue'])}**，"
        f"同比增长 **{_fmt_pct(yoy_rev)}**，"
        f"ARPU 同比增长 **{_fmt_pct(yoy_arpu)}**。"
    )

    # ── Section 2: 关键指标表格行 ──
    mom_pay_rate = ""
    yoy_pay_rate = ""
    if previous:
        mom_pr = current['pay_rate'] - previous['pay_rate']
        mom_pay_rate = f"{mom_pr:+.2f}pp"
    if benchmark:
        yoy_pr = current['pay_rate'] - benchmark['pay_rate']
        yoy_pay_rate = _color_pct(yoy_pr).replace('%', 'pp') if yoy_pr != 0 else f"{yoy_pr:+.2f}pp"

    # ── Section 3: 模块结构 ──
    ms = metrics.get('module_share', {})
    # 找到当期模块绝对值
    module_current = None
    for m in data['module_trend']:
        if m['event'] == event_name:
            module_current = m
            break
    if module_current is None:
        module_current = data['module_trend'][-1]

    # ── Section 4: 用户分层表格 ──
    tiers = data['user_tier_trend']
    tier_rows = []
    # 找到当期、前期、对标
    tier_current = tiers[0] if tiers else {}
    tier_benchmark = tiers[-1] if len(tiers) >= 2 else {}
    tier_previous = tiers[1] if len(tiers) >= 3 else tiers[-1] if len(tiers) >= 2 else {}

    for tier_key, tier_label in [('super_r', '超R'), ('big_r', '大R'), ('mid_r', '中R')]:
        cur_val = tier_current.get(tier_key, 0)
        prev_val = tier_previous.get(tier_key, 0)
        bench_val = tier_benchmark.get(tier_key, 0)
        yoy_change = ((cur_val - bench_val) / bench_val * 100) if bench_val > 0 else None
        mom_change = ((cur_val - prev_val) / prev_val * 100) if prev_val > 0 else None
        tier_rows.append(
            f'\t<tr>\n'
            f'\t\t<td>**{tier_label}**</td>\n'
            f'\t\t<td><span color="red">**${cur_val:.2f}**</span></td>\n'
            f'\t\t<td>${prev_val:.2f}</td>\n'
            f'\t\t<td>${bench_val:.2f}</td>\n'
            f'\t\t<td>{_color_pct(yoy_change)}</td>\n'
            f'\t\t<td>{_color_pct(mom_change)}</td>\n'
            f'\t</tr>'
        )
    tier_table_rows = '\n'.join(tier_rows)

    # ── Section 5: 子活动诊断 ──
    keep_items = [s for s in data['sub_activity_detail'] if s['status'] == 'Keep']
    optimize_items = [s for s in data['sub_activity_detail'] if s['status'] == 'Optimize']

    def _format_sub_list_notion(items: list, color: str) -> str:
        lines = []
        for item in items:
            lines.append(
                f'- <span color="{color}">**{item["name"]}**</span> ({item["type"]}) - '
                f'营收 ${_fmt_revenue(item["revenue"])}\n'
                f'\t- {item["reason"]}'
            )
        return '\n'.join(lines) if lines else '- 无'

    keep_list = _format_sub_list_notion(keep_items, 'green')
    optimize_list = _format_sub_list_notion(optimize_items, 'orange')

    # ── Section 6a: 核心大盘指标（R级分层表）──
    core_metrics_table = ''
    core_metrics_insight = ''
    risk_callout = ''
    if 'core_metrics_by_tier' in data:
        cm = data['core_metrics_by_tier']
        rows = []
        for key, label, row_color in [
            ('total', '全体玩家', ''),
            ('paying', '付费玩家', ''),
            ('chaoR', 'chaoR', ' color="red_bg"'),
            ('daR', 'daR', ''),
            ('zhongR', 'zhongR', ''),
            ('xiaoR', 'xiaoR', ''),
        ]:
            t = cm.get(key)
            if not t:
                continue
            rev_fmt = f'**\\${_fmt_revenue(t["event_revenue"])}**' if key == 'total' else (
                f'<span color="red">**\\${_fmt_revenue(t["event_revenue"])}**</span>' if key == 'chaoR'
                else f'\\${_fmt_revenue(t["event_revenue"])}')
            arpu_fmt = f'**\\${t["arpu"]:.2f}**'
            buy_rate_fmt = f'<span color="orange">{t["buy_rate"]:.1f}%</span>' if t.get("buy_rate", 100) < 15 else f'{t["buy_rate"]:.1f}%'
            rows.append(
                f'<tr{row_color}>\n'
                f'<td>**{label}**</td>\n'
                f'<td>{t.get("active", 0):,}</td>\n'
                f'<td>{t.get("buyers", 0):,}</td>\n'
                f'<td>{rev_fmt}</td>\n'
                f'<td>\\${_fmt_revenue(t.get("total_revenue", 0))}</td>\n'
                f'<td>{t.get("event_share", 0):.1f}%</td>\n'
                f'<td>{buy_rate_fmt}</td>\n'
                f'<td>\\${t.get("arppu", 0):.2f}</td>\n'
                f'<td>{arpu_fmt}</td>\n'
                f'</tr>')
        core_metrics_table = (
            '<table fit-page-width="true" header-row="true" header-column="true">\n'
            '<tr>\n<td>分类</td>\n<td>活跃人数</td>\n<td>购买人数</td>\n'
            '<td>节日礼包付费</td>\n<td>总礼包付费</td>\n<td>节日占比</td>\n'
            '<td>购买率</td>\n<td>ARPPU</td>\n<td>ARPU</td>\n</tr>\n'
            + '\n'.join(rows) + '\n</table>'
        )
        # 生成洞察
        total_t = cm.get('total', {})
        chao_t = cm.get('chaoR', {})
        xiao_t = cm.get('xiaoR', {})
        zhong_t = cm.get('zhongR', {})
        insights = []
        if total_t.get('event_share'):
            insights.append(f'\t- 节日礼包仅占总礼包收入的 {total_t["event_share"]:.1f}%，一半收入来自非节日常规礼包，节日活动的付费吸引力有提升空间')
        if chao_t.get('buy_rate') and xiao_t.get('buy_rate'):
            insights.append(f'\t- chaoR 购买率 {chao_t["buy_rate"]:.1f}%，几乎全员付费；xiaoR 仅 {xiao_t["buy_rate"]:.1f}%，转化率极低')
        if chao_t.get('arppu') and zhong_t.get('arppu') and zhong_t['arppu'] > 0:
            ratio = chao_t['arppu'] / zhong_t['arppu']
            insights.append(f'\t- chaoR 的 ARPPU（\\${chao_t["arppu"]:.0f}）是 zhongR（\\${zhong_t["arppu"]:.2f}）的 **{ratio:.1f} 倍**，收入极度依赖头部')
        core_metrics_insight = '\t**关键发现:**\n' + '\n'.join(insights) if insights else ''

    # ── Section 6b: 模块营收明细表 ──
    module_detail_table = ''
    module_detail_insight = ''
    if 'module_detail' in data:
        md = data['module_detail']
        md_rows = []
        for m in md:
            is_top = m.get('share', 0) > 30
            row_color = ' color="yellow_bg"' if is_top else ''
            name = f'<span color="red">**{m["module"]}**</span>' if is_top else m['module']
            rev = f'<span color="red">**\\${_fmt_revenue(m["revenue"])}**</span>' if is_top else f'\\${_fmt_revenue(m["revenue"])}'
            share = f'<span color="red">**{m["share"]:.1f}%**</span>' if is_top else f'{m["share"]:.1f}%'
            arpu = f'<span color="red">**\\${m.get("event_arpu", 0):.2f}**</span>' if is_top else f'\\${m.get("event_arpu", 0):.2f}'
            avg = f'<span color="red">**{m.get("avg_purchases", 0):.1f}次**</span>' if is_top else f'{m.get("avg_purchases", 0):.1f}次'
            md_rows.append(
                f'<tr{row_color}>\n<td>{name}</td>\n<td>{rev}</td>\n<td>{share}</td>\n'
                f'<td>{m.get("buy_times", 0):,}</td>\n<td>\\${m.get("times_arppu", 0):.2f}</td>\n'
                f'<td>{arpu}</td>\n<td>{avg}</td>\n</tr>')
        total_buyers = data.get('core_metrics_by_tier', {}).get('total', {}).get('buyers', 0)
        buyer_note = f' (/{ total_buyers:,}人)' if total_buyers else ''
        module_detail_table = (
            f'<table header-row="true" fit-page-width="true">\n'
            f'<tr>\n<td>模块</td>\n<td>收入</td>\n<td>占比</td>\n<td>购买人次</td>\n'
            f'<td>人次ARPPU</td>\n<td>节日ARPU{buyer_note}</td>\n<td>人均购买次数</td>\n</tr>\n'
            + '\n'.join(md_rows) + '\n</table>'
        )

    # ── Section 6c: 活动效率排名表 ──
    activity_ranking_table = ''
    efficiency_insight = ''
    success_model_insight = ''
    sku_efficiency_insight = ''
    if 'activity_ranking' in data:
        ar = data['activity_ranking']
        ar_rows = []
        t1_revenue = 0
        total_revenue_sum = sum(a['revenue'] for a in ar)
        for i, a in enumerate(ar):
            is_t1 = a.get('event_arpu', 0) >= 10
            row_color = ' color="green_bg"' if is_t1 else ''
            if is_t1:
                t1_revenue += a['revenue']
            # 人均购买次数 = 购买人次 / 去重购买人数
            ub = a.get('unique_buyers', 0)
            bt = a.get('buy_times', 0)
            avg_purch = f'{bt / ub:.1f}次' if ub > 0 else '-'
            ub_fmt = f'{ub:,}' if ub > 0 else '-'
            ar_rows.append(
                f'<tr{row_color}>\n<td>{i+1}</td>\n<td>**{a["name"]}**</td>\n<td>{a["module"]}</td>\n'
                f'<td>**\\${_fmt_revenue(a["revenue"])}**</td>\n<td>{a.get("share", 0):.1f}%</td>\n'
                f'<td>{a.get("buy_times", 0):,}</td>\n<td>{ub_fmt}</td>\n<td>{avg_purch}</td>\n'
                f'<td>\\${a.get("times_arppu", 0):.2f}</td>\n'
                f'<td>\\${a.get("event_arpu", 0):.2f}</td>\n<td>{a.get("sku_count", 0)}</td>\n</tr>')
        activity_ranking_table = (
            '<table header-row="true" fit-page-width="true">\n'
            '<tr>\n<td>#</td>\n<td>活动名</td>\n<td>模块</td>\n<td>收入</td>\n<td>占比</td>\n'
            '<td>购买人次</td>\n<td>去重人数</td>\n<td>人均次数</td>\n<td>人次ARPPU</td>\n<td>节日ARPU</td>\n<td>SKU数</td>\n</tr>\n'
            + '\n'.join(ar_rows) + '\n</table>'
        )
        t1_share = (t1_revenue / total_revenue_sum * 100) if total_revenue_sum > 0 else 0
        t1_count = sum(1 for a in ar if a.get('event_arpu', 0) >= 10)
        efficiency_insight = (
            f'\t**效率梯队:**\n'
            f'\t- <span color="green">**T1**</span>（节日ARPU > 10）：前 {t1_count} 个活动贡献了 **{t1_share:.1f}%** 的收入，是绝对核心\n'
            f'\t- **T2**（ARPU 1\\~10）：有一定贡献但非主力\n'
            f'\t- <span color="gray">**T3**</span>（ARPU < 1）：收入微薄，需评估保留价值'
        )
        # 找广覆盖型和窄覆盖型
        wide = [a for a in ar if a.get('buy_times', 0) > 5000 and a.get('event_arpu', 0) > 20]
        narrow = [a for a in ar if a.get('times_arppu', 0) > 80 and a.get('buy_times', 0) < 500]
        parts = []
        if wide:
            w = wide[0]
            parts.append(f'\t- **广覆盖高频型**: {w["name"]}（{w.get("buy_times",0):,}人次、ARPU \\${w.get("event_arpu",0):.2f}）— 靠小中额分层 + 复购驱动')
        if narrow:
            n = narrow[0]
            parts.append(f'\t- **窄覆盖高客单型**: {n["name"]}（{n.get("buy_times",0):,}人次、ARPPU \\${n.get("times_arppu",0):.2f}）— 靠高R情感/稀缺消费驱动')
        if parts:
            success_model_insight = '\t**两种成功模式:**\n' + '\n'.join(parts)
        # SKU 效率
        sku_items = [(a['name'], a.get('sku_count', 1), a['revenue']) for a in ar if a.get('sku_count', 0) > 0]
        if sku_items:
            sku_items_eff = [(n, s, r, r/s if s > 0 else 0) for n, s, r, in sku_items]
            best = max(sku_items_eff, key=lambda x: x[3])
            worst = min(sku_items_eff, key=lambda x: x[3])
            sku_efficiency_insight = (
                f'\t**SKU 效率对比:**\n'
                f'\t- {best[0]}：{best[1]} 个 SKU 产出 \\${_fmt_revenue(best[2])}，单 SKU 平均 **\\${_fmt_revenue(best[3])}** — 效率最高\n'
                f'\t- {worst[0]}：{worst[1]} 个 SKU 产出 \\${_fmt_revenue(worst[2])}，单 SKU 平均 **\\${_fmt_revenue(worst[3])}** — 效率最低'
            )

    # ── Section 6c-2: 活动R级收入结构表 ──
    tier_revenue_table = ''
    tier_revenue_insight = ''
    has_tier = any(a.get('tier_breakdown') for a in data.get('activity_ranking', []))
    if has_tier:
        tr_rows = []
        high_chao_acts = []  # chaoR占比>70%的活动
        for a in sorted(data['activity_ranking'], key=lambda x: x['revenue'], reverse=True):
            tb = a.get('tier_breakdown', {})
            if not tb:
                continue
            rev = a['revenue']
            chao = tb.get('chaoR', {})
            da = tb.get('daR', {})
            zhong = tb.get('zhongR', {})
            xiao = tb.get('xiaoR', {})

            chao_pct = (chao.get('revenue', 0) / rev * 100) if rev > 0 else 0
            da_pct = (da.get('revenue', 0) / rev * 100) if rev > 0 else 0
            zhong_pct = (zhong.get('revenue', 0) / rev * 100) if rev > 0 else 0
            xiao_pct = (xiao.get('revenue', 0) / rev * 100) if rev > 0 else 0

            chao_arppu = (chao.get('revenue', 0) / chao.get('buyers', 1)) if chao.get('buyers', 0) > 0 else 0
            da_arppu = (da.get('revenue', 0) / da.get('buyers', 1)) if da.get('buyers', 0) > 0 else 0
            zhong_arppu = (zhong.get('revenue', 0) / zhong.get('buyers', 1)) if zhong.get('buyers', 0) > 0 else 0
            xiao_arppu = (xiao.get('revenue', 0) / xiao.get('buyers', 1)) if xiao.get('buyers', 0) > 0 else 0

            # 高危标记：chaoR占比>70%
            is_high_risk = chao_pct > 70
            row_color = ' color="red_bg"' if is_high_risk else ''
            chao_cell = f'<span color="red">**{chao_pct:.1f}%**</span>' if is_high_risk else f'{chao_pct:.1f}%'

            if is_high_risk:
                high_chao_acts.append((a['name'], chao_pct))

            tr_rows.append(
                f'<tr{row_color}>\n<td>**{a["name"]}**</td>\n'
                f'<td>{chao_cell}</td>\n<td>\\${chao_arppu:.0f}</td>\n'
                f'<td>{da_pct:.1f}%</td>\n<td>\\${da_arppu:.0f}</td>\n'
                f'<td>{zhong_pct:.1f}%</td>\n<td>\\${zhong_arppu:.0f}</td>\n'
                f'<td>{xiao_pct:.1f}%</td>\n<td>\\${xiao_arppu:.0f}</td>\n</tr>'
            )

        tier_revenue_table = (
            '<table header-row="true" fit-page-width="true">\n'
            '<tr>\n<td>活动</td>\n'
            '<td>chaoR占比</td>\n<td>chaoR ARPPU</td>\n'
            '<td>daR占比</td>\n<td>daR ARPPU</td>\n'
            '<td>zhongR占比</td>\n<td>zhongR ARPPU</td>\n'
            '<td>xiaoR占比</td>\n<td>xiaoR ARPPU</td>\n</tr>\n'
            + '\n'.join(tr_rows) + '\n</table>'
        )

        # 洞察
        insights = []
        if high_chao_acts:
            names = '、'.join(f'{n}（{p:.0f}%）' for n, p in high_chao_acts)
            insights.append(
                f'\t- <span color="red">**高危活动**</span>：{names} 极度依赖 chaoR，'
                f'若头部用户继续流失，这些活动收入将首当其冲'
            )
        # 找分层最均匀的活动（chaoR占比最低）
        all_chao_pcts = [(a['name'], a.get('tier_breakdown', {}).get('chaoR', {}).get('revenue', 0) / a['revenue'] * 100)
                         for a in data['activity_ranking'] if a.get('tier_breakdown') and a['revenue'] > 0]
        if all_chao_pcts:
            best_balanced = min(all_chao_pcts, key=lambda x: x[1])
            if best_balanced[1] < 50:
                insights.append(
                    f'\t- <span color="green">**分层最健康**</span>：{best_balanced[0]}（chaoR 仅占 {best_balanced[1]:.0f}%），'
                    f'收入来源分散，抗风险能力最强'
                )
        if insights:
            tier_revenue_insight = '\t**R级依赖度分析:**\n' + '\n'.join(insights)

    # ── Section 6d: 历史营收排名 ──
    historical_revenue_table = ''
    if 'historical_revenue' in data:
        hr = sorted(data['historical_revenue'], key=lambda x: x['revenue'], reverse=True)
        hr_rows = []
        for i, h in enumerate(hr):
            is_current = h['event'] == event_name
            row_color = ' color="yellow_bg"' if is_current else ''
            name = f'**{h["event"]}**' if is_current else h['event']
            rev = f'**\\${_fmt_revenue(h["revenue"])}**' if is_current else f'\\${_fmt_revenue(h["revenue"])}'
            hr_rows.append(f'<tr{row_color}>\n<td>{i+1}</td>\n<td>{name}</td>\n<td>{rev}</td>\n</tr>')
        historical_revenue_table = (
            '**历史活动营收排名:**\n\n'
            '<table header-row="true">\n<tr>\n<td>排名</td>\n<td>活动</td>\n<td>营收</td>\n</tr>\n'
            + '\n'.join(hr_rows) + '\n</table>'
        )

    # ── Section 6e: R级人数趋势 ──
    tier_headcount_table = ''
    tier_trend_diagnosis = ''
    if 'tier_headcount_trend' in data:
        th = data['tier_headcount_trend']
        th_rows = []
        for t in th:
            is_current = t['event'] == event_name
            row_color = ' color="yellow_bg"' if is_current else ''
            evt = f'**{t["event"]}**' if is_current else t['event']
            chao_fmt = f'<span color="red">**{t.get("chaoR", 0):,}**</span>' if is_current else f'{t.get("chaoR", 0):,}'
            th_rows.append(
                f'<tr{row_color}>\n<td>{evt}</td>\n<td>{t.get("xiaoR", 0):,}</td>\n'
                f'<td>{t.get("zhongR", 0):,}</td>\n<td>{t.get("daR", 0):,}</td>\n'
                f'<td>{chao_fmt}</td>\n<td>{t.get("total", 0):,}</td>\n</tr>')
        tier_headcount_table = (
            '<table header-row="true" fit-page-width="true">\n'
            '<tr>\n<td>活动</td>\n<td>xiaoR</td>\n<td>zhongR</td>\n<td>daR</td>\n<td>chaoR</td>\n<td>付费总人数</td>\n</tr>\n'
            + '\n'.join(th_rows) + '\n</table>'
        )
        # 趋势诊断
        if len(th) >= 2:
            first = th[0]
            last = th[-1]
            diag_parts = []
            for key, label in [('xiaoR', 'xiaoR'), ('zhongR', 'zhongR'), ('daR', 'daR'), ('chaoR', 'chaoR')]:
                v0 = first.get(key, 0)
                v1 = last.get(key, 0)
                if v0 > 0:
                    change = (v1 - v0) / v0 * 100
                    diag_parts.append((key, label, v0, v1, change))
            up_parts = []
            down_parts = []
            for key, label, v0, v1, change in diag_parts:
                if change > 5:
                    up_parts.append(f'\t- {label}：{v0:,} → {v1:,}（**{change:+.1f}%**）')
                elif change < -5:
                    down_parts.append(f'\t- <span color="red">**{label}：{v0:,} → {v1:,}（{change:+.1f}%）**</span>')
            total_first = first.get('total', 0)
            total_last = last.get('total', 0)
            total_change = ((total_last - total_first) / total_first * 100) if total_first > 0 else 0
            up_callout = ''
            if up_parts:
                up_callout = f'<callout icon="📈" color="green_bg">\n\t**上升通道:** 付费玩家总量 {total_first:,} → {total_last:,}（{total_change:+.1f}%）\n' + '\n'.join(up_parts) + '\n</callout>'
            down_callout = ''
            if down_parts:
                down_callout = '<callout icon="📉" color="red_bg">\n\t**风险信号:**\n' + '\n'.join(down_parts) + '\n</callout>'
            tier_trend_diagnosis = up_callout + ('\n\n' if up_callout and down_callout else '') + down_callout

    # ── Section 6f: 风险预警 callout ──
    if 'tier_headcount_trend' in data:
        th = data['tier_headcount_trend']
        if len(th) >= 2:
            first_chao = th[0].get('chaoR', 0)
            last_chao = th[-1].get('chaoR', 0)
            if first_chao > 0 and last_chao > 0:
                chao_drop = (last_chao - first_chao) / first_chao * 100
                if chao_drop < -10:
                    risk_callout = (
                        f'<callout icon="⚠️" color="red_bg">\n'
                        f'\t**风险预警**: chaoR 人数从{th[0]["event"]}的 {first_chao:,} 持续下滑至{th[-1]["event"]}的 {last_chao:,}，'
                        f'降幅 **{chao_drop:.1f}%**，头部用户流失趋势明显。\n'
                        f'</callout>'
                    )

    # ── Section 6g: Watch 列表 ──
    watch_items = []
    if 'tier_headcount_trend' in data:
        th = data['tier_headcount_trend']
        if len(th) >= 2:
            for key, label in [('chaoR', 'chaoR 流失趋势'), ('daR', 'daR 增长停滞')]:
                v0 = th[0].get(key, 0)
                v1 = th[-1].get(key, 0)
                if v0 > 0:
                    change = (v1 - v0) / v0 * 100
                    if change < -5:
                        watch_items.append(f'- <span color="red">**{label}**</span>：{len(th)} 期连续下滑（{v0:,} → {v1:,}），需要专项分析流失原因并制定留存/召回策略')
                    elif abs(change) < 3:
                        watch_items.append(f'- <span color="red">**{label}**</span>：{len(th)} 期基本持平（{v0:,} → {v1:,}），晋升通道可能不畅')
    watch_list = '\n'.join(watch_items) if watch_items else '- 暂无'

    # ── Section 6i: 日维度营收分析 ──
    daily_revenue_table = ''
    daily_rhythm_insight = ''
    if 'daily_revenue' in data and len(data['daily_revenue']) >= 3:
        dr = data['daily_revenue']
        total_days = len(dr)
        total_rev = sum(d['revenue'] for d in dr)

        # 判断付费节奏类型：前1/3天的营收占比
        first_third = max(1, total_days // 3)
        first_third_rev = sum(dr[i]['revenue'] for i in range(first_third))
        last_third_rev = sum(dr[i]['revenue'] for i in range(total_days - first_third, total_days))
        first_ratio = (first_third_rev / total_rev * 100) if total_rev > 0 else 0
        last_ratio = (last_third_rev / total_rev * 100) if total_rev > 0 else 0

        if first_ratio > 45:
            rhythm_type = '前置型'
            rhythm_color = 'red'
            rhythm_desc = f'前 {first_third} 天贡献了 {first_ratio:.1f}% 的营收，付费高度集中在活动初期，后续衰减明显'
        elif last_ratio > 40:
            rhythm_type = '长尾型'
            rhythm_color = 'green'
            rhythm_desc = f'后 {first_third} 天仍贡献 {last_ratio:.1f}% 营收，付费分布均匀，活动持续吸引力强'
        else:
            rhythm_type = '均匀型'
            rhythm_color = 'blue'
            rhythm_desc = f'前 {first_third} 天占 {first_ratio:.1f}%，后 {first_third} 天占 {last_ratio:.1f}%，付费节奏较为平稳'

        # 找峰值日
        peak_day = max(dr, key=lambda d: d['revenue'])
        valley_day = min(dr, key=lambda d: d['revenue'])

        # 生成表格（按周汇总，避免表格过长）
        week_size = 7
        week_rows = []
        for w_start in range(0, total_days, week_size):
            w_end = min(w_start + week_size, total_days)
            w_days = dr[w_start:w_end]
            w_rev = sum(d['revenue'] for d in w_days)
            w_buyers = sum(d.get('buyers', 0) for d in w_days)
            w_share = (w_rev / total_rev * 100) if total_rev > 0 else 0
            w_label = f'{w_days[0]["date"]} ~ {w_days[-1]["date"]}'
            is_peak = any(d['date'] == peak_day['date'] for d in w_days)
            row_color = ' color="yellow_bg"' if is_peak else ''
            week_rows.append(
                f'<tr{row_color}>\n<td>{w_label}</td>\n<td>\\${_fmt_revenue(w_rev)}</td>\n'
                f'<td>{w_share:.1f}%</td>\n<td>{w_buyers:,}</td>\n</tr>'
            )

        daily_revenue_table = (
            '<table header-row="true">\n'
            '<tr>\n<td>时段</td>\n<td>营收</td>\n<td>占比</td>\n<td>付费人数</td>\n</tr>\n'
            + '\n'.join(week_rows) + '\n</table>'
        )

        daily_rhythm_insight = (
            f'<callout icon="⏱️" color="{rhythm_color}_bg">\n'
            f'\t**付费节奏: <span color="{rhythm_color}">{rhythm_type}</span>**\n'
            f'\t{rhythm_desc}\n'
            f'\t- 峰值日: {peak_day["date"]}（\\${_fmt_revenue(peak_day["revenue"])}）\n'
            f'\t- 谷值日: {valley_day["date"]}（\\${_fmt_revenue(valley_day["revenue"])}）\n'
            f'</callout>'
        )

    # ── Section 6h: 总结 ──
    final_summary = ''
    top_modules = []
    if 'module_detail' in data:
        sorted_mods = sorted(data['module_detail'], key=lambda x: x['revenue'], reverse=True)
        top_modules = [m['module'] for m in sorted_mods[:2]]
    top_mod_text = ' + '.join(top_modules) if top_modules else '核心模块'
    top_activity = keep_items[0]['name'] if keep_items else '头部活动'
    final_summary = (
        f'\t{event_name}活动整体付费结构健康，{top_mod_text}两大模块贡献核心收入，'
        f'{top_activity}是当之无愧的 MVP。'
    )
    if risk_callout:
        final_summary += (
            f'\n\t但最大隐患是 chaoR 人数的持续流失——这批核心用户正在持续流失，'
            f'如果不采取针对性措施，未来 3-4 个活动周期内营收可能出现明显下滑拐点。'
        )

    # ── Section 7: Action Items ──
    # 完全基于数据动态生成，不硬编码任何具体建议
    action_lines = []
    action_lines.append('### P0 - 立即执行\n')

    # 从 Keep 中提取成功模块，生成"持续投入"建议
    keep_modules = {}
    for k in keep_items:
        mod = k.get('type', '未知')
        if mod not in keep_modules:
            keep_modules[mod] = []
        keep_modules[mod].append(k)
    for mod, items in keep_modules.items():
        names = '、'.join(i['name'] for i in items)
        total_rev = sum(i['revenue'] for i in items)
        action_lines.append(
            f'1. **{mod}模块持续投入** - {names}已验证成功（合计 \\${_fmt_revenue(total_rev)}），'
            f'建议持续迭代并探索更多付费点'
        )

    # chaoR 流失专项
    if risk_callout:
        chao_cm = data.get('core_metrics_by_tier', {}).get('chaoR', {})
        chao_share = chao_cm.get('event_share', 0)
        action_lines.append(
            f'1. **chaoR 流失专项分析** - 头部用户持续流失，贡献 {chao_share:.1f}% 节日收入，'
            f'需立即启动流失原因分析和召回策略'
        )

    # P1: 从 Optimize 项动态生成
    action_lines.append('\n### P1 - 下期优化\n')
    for item in optimize_items:
        action_lines.append(
            f'1. **{item["name"]}优化** - {item["reason"]}'
        )

    # xiaoR 转化建议（基于实际数据）
    xiao_t = data.get('core_metrics_by_tier', {}).get('xiaoR', {})
    if xiao_t.get('buy_rate', 100) < 15:
        xiao_active = xiao_t.get('active', 0)
        xiao_buyers = xiao_t.get('buyers', 0)
        action_lines.append(
            f'1. **xiaoR 转化提升** - {xiao_active:,} 活跃中仅 {xiao_buyers:,} 人购买（{xiao_t["buy_rate"]:.1f}%），'
            f'建议增加低门槛付费引导'
        )

    # P2: Watch 项转化为中期规划
    action_lines.append('\n### P2 - 中期规划\n')
    if watch_items:
        for w in watch_items:
            # 从 watch 描述中提取关键信息生成 action
            if 'daR' in w:
                action_lines.append(
                    '1. **daR 晋升通道优化** - 检查中高档付费内容吸引力，促进 zhongR 向 daR 转化'
                )
            elif 'chaoR' in w:
                action_lines.append(
                    '1. **chaoR 留存体系建设** - 建立高R专属内容/权益体系，降低流失率'
                )
    else:
        action_lines.append('1. 暂无中期规划项')

    action_items = '\n'.join(action_lines)

    # ── Section 8: 待人工补充清单 ──
    checklist_lines = []

    # P0 补充项：每个成功模块需要人工明确迭代方向
    if keep_modules:
        checklist_lines.append('### P0 待补充\n')
        for mod, items in keep_modules.items():
            names = '、'.join(i['name'] for i in items)
            checklist_lines.append(
                f'- [ ] **{mod}模块迭代方向** - {names}已验证成功，'
                f'需明确：下期新增哪些付费点？是否有新玩法规划？'
            )
        if risk_callout:
            checklist_lines.append(
                '- [ ] **chaoR 流失根因分析** - 需人工排查：是内容吸引力下降、'
                '竞品分流、还是生命周期自然衰退？是否有定性访谈数据？'
            )

    # P1 补充项：每个 Optimize 项需要具体优化方案
    if optimize_items:
        checklist_lines.append('\n### P1 待补充\n')
        for item in optimize_items:
            checklist_lines.append(
                f'- [ ] **{item["name"]}优化方案** - 需明确：'
                f'具体调整哪些参数？（如奖池结构、档位定价、SKU 精简方案等）'
            )
        # xiaoR 转化
        xiao_t = data.get('core_metrics_by_tier', {}).get('xiaoR', {})
        if xiao_t.get('buy_rate', 100) < 15:
            checklist_lines.append(
                '- [ ] **xiaoR 低门槛付费设计** - 需明确：'
                '计划推出哪些入门级付费内容？定价区间？'
            )

    # P2 补充项：Watch 项需要专项设计
    if watch_items:
        checklist_lines.append('\n### P2 待补充\n')
        for w in watch_items:
            if 'chaoR' in w:
                checklist_lines.append(
                    '- [ ] **chaoR 专属权益体系设计** - 需明确：'
                    '专属内容/权益具体包含哪些？预期投入和上线时间？'
                )
            elif 'daR' in w:
                checklist_lines.append(
                    '- [ ] **daR 晋升通道设计** - 需明确：'
                    '中高档付费内容如何调整？zhongR→daR 转化路径？'
                )

    human_checklist = '\n'.join(checklist_lines) if checklist_lines else '- [ ] 暂无待补充项'

    # ── 组装完整 Notion 内容 ──
    previous_event = tier_previous.get('event', '') if tier_previous else ''

    # 生成两个横向对比宽表
    event_comparison_table = _build_event_comparison_table(data, event_name)
    tier_arpu_comparison_table = _build_tier_arpu_comparison_table(data, event_name)

    # 构建各段内容
    sections = []

    # 头部
    sections.append(f'> 对标活动: {benchmark_event} | 生成时间: {generated_at} | 完整版')
    sections.append('<table_of_contents/>')
    sections.append('---')

    # Section 1: Executive Summary
    sections.append('## 1. Executive Summary')
    sections.append(f'<callout icon="⭐" color="yellow_bg">\n{exec_summary_short}\n</callout>')
    if risk_callout:
        sections.append(risk_callout)
    sections.append('---')

    # Section 2: 节日整体对比（横向宽表）
    sec_num = 2
    if event_comparison_table:
        sections.append(f'## {sec_num}. 节日整体对比')
        sections.append(event_comparison_table)
        sections.append('---')
        sec_num += 1

    # Section 3: 节日ARPU对比（横向宽表）
    if tier_arpu_comparison_table:
        sections.append(f'## {sec_num}. 节日ARPU对比')
        sections.append(tier_arpu_comparison_table)
        sections.append('---')
        sec_num += 1

    # Section: 核心大盘指标（R级分层表）
    if core_metrics_table:
        sections.append(f'## {sec_num}. 核心大盘指标')
        sections.append(core_metrics_table)
        if core_metrics_insight:
            sections.append(f'<callout icon="💡" color="gray_bg">\n{core_metrics_insight}\n</callout>')
        sections.append('---')
        sec_num += 1

    # Section: 核心大盘趋势（仅保留趋势图+趋势判断，KPI表和历史排名已移至节日整体对比）
    sections.append(f'## {sec_num}. 核心大盘趋势')
    sections.append('<callout icon="📊" color="blue_bg">\n\t请在此处插入图表: 1\\_Revenue\\_Trend.png（核心大盘趋势折线图）\n</callout>')
    sections.append(f'**趋势判断: **<span color="red">**{metrics.get("trend_pattern", "N/A")}**</span>')
    sections.append(metrics.get('trend_description', ''))
    sections.append('---')
    sec_num += 1

    # Section: 模块营收结构
    sections.append(f'## {sec_num}. 模块营收结构')
    sections.append('<callout icon="📊" color="blue_bg">\n\t请在此处插入图表: 2\\_Module\\_Structure.png（模块营收堆叠面积图）\n</callout>')
    if module_detail_table:
        sections.append(module_detail_table)
    else:
        # fallback 到简版模块表
        simple_mod = (
            f'<table header-row="true">\n'
            f'<tr>\n<td>模块</td>\n<td>占比</td>\n<td>营收</td>\n</tr>\n'
            f'<tr>\n<td>外显类</td>\n<td>{ms.get("appearance", 0):.1f}%</td>\n<td>\\${_fmt_revenue(module_current["appearance"])}</td>\n</tr>\n'
            f'<tr>\n<td><span color="red">**小游戏**</span></td>\n<td><span color="red">**{ms.get("minigame", 0):.1f}%**</span></td>\n<td><span color="red">**\\${_fmt_revenue(module_current["minigame"])}**</span></td>\n</tr>\n'
            f'<tr>\n<td>混合/养成</td>\n<td>{ms.get("hybrid", 0):.1f}%</td>\n<td>\\${_fmt_revenue(module_current["hybrid"])}</td>\n</tr>\n'
            f'</table>'
        )
        sections.append(simple_mod)
    if module_detail_insight:
        sections.append(f'<callout icon="💡" color="gray_bg">\n{module_detail_insight}\n</callout>')
    sections.append('---')
    sec_num += 1

    # Section: 各活动效率排名
    if activity_ranking_table:
        sections.append(f'## {sec_num}. 各活动效率排名')
        sections.append(activity_ranking_table)
        if efficiency_insight:
            sections.append(f'<callout icon="🎯" color="purple_bg">\n{efficiency_insight}\n</callout>')
        if success_model_insight:
            sections.append(f'<callout icon="🔑" color="orange_bg">\n{success_model_insight}\n</callout>')
        if sku_efficiency_insight:
            sections.append(f'<callout icon="📎" color="gray_bg">\n{sku_efficiency_insight}\n</callout>')
        if tier_revenue_table:
            sections.append(f'### {sec_num}.2 活动R级收入结构')
            sections.append(tier_revenue_table)
            if tier_revenue_insight:
                sections.append(f'<callout icon="🔍" color="red_bg">\n{tier_revenue_insight}\n</callout>')
        sections.append('---')
        sec_num += 1

    # Section: 用户分层趋势（移除tier ARPU对比表，已在节日ARPU对比中展示）
    sections.append(f'## {sec_num}. 用户分层趋势')
    sections.append('<callout icon="📊" color="blue_bg">\n\t请在此处插入图表: 3\\_User\\_Growth.png（用户分层 ARPU 分组柱状图）\n</callout>')
    if tier_headcount_table:
        sections.append(f'### {sec_num}.1 付费玩家人数趋势')
        sections.append(tier_headcount_table)
    if tier_trend_diagnosis:
        sections.append(f'### {sec_num}.2 趋势诊断')
        sections.append(tier_trend_diagnosis)
    sections.append('---')
    sec_num += 1

    # Section: 日维度营收分析（可选）
    if daily_revenue_table:
        sections.append(f'## {sec_num}. 日维度营收分析')
        if daily_rhythm_insight:
            sections.append(daily_rhythm_insight)
        sections.append(daily_revenue_table)
        sections.append('---')
        sec_num += 1

    # Section: 子活动诊断
    sections.append(f'## {sec_num}. 子活动诊断')
    sections.append(f'### {sec_num}.1 Keep - 表现优秀，建议保留')
    sections.append(keep_list)
    sections.append(f'### {sec_num}.2 Optimize - 待优化项')
    sections.append(optimize_list)
    sections.append(f'### {sec_num}.3 Watch - 需持续监控')
    sections.append(watch_list)
    sections.append('---')
    sec_num += 1

    # Section: Action Items
    sections.append(f'## {sec_num}. Action Items')
    sections.append(action_items)
    sections.append('---')
    sec_num += 1

    # Section: 待人工补充清单
    sections.append(f'## {sec_num}. 待人工补充清单')
    sections.append(f'<callout icon="📋" color="orange_bg">\n以下为数据分析无法覆盖的决策项，需人工补充后报告才算完整。\n</callout>')
    sections.append(human_checklist)
    sections.append('---')
    sec_num += 1

    # Section: 总结
    sections.append(f'## {sec_num}. 总结')
    sections.append(f'<callout icon="📝" color="blue_bg">\n{final_summary}\n</callout>')
    sections.append('---')
    sections.append('*本报告由 generate\\_event\\_review Skill 自动生成*')

    content = '\n\n'.join(sections)

    return content


def generate_notion_title(data: dict) -> str:
    """生成 Notion 页面标题"""
    return f"{data['meta']['event_name']} - 活动复盘总结 (自动生成)"


def generate_wiki_content(data: dict, metrics: dict, chart_dir: str = '') -> str:
    """
    生成 Wiki 兼容的报告内容。
    不使用任何 markdown 内联格式(**粗体**、![图片]()等)，
    仅依赖: ## 标题、> 引用、--- 分隔、| 表格 |、- 列表。
    强调文字用【】括号和 Unicode 符号替代。

    Args:
        data: 标准化输入数据
        metrics: compute_metrics() 的返回结果
        chart_dir: 图表文件所在目录的相对路径

    Returns:
        str: Wiki 兼容内容，可直接粘贴
    """
    meta = data['meta']
    event_name = meta['event_name']
    benchmark_event = meta['benchmark_event']
    generated_at = datetime.now().strftime('%Y-%m-%d')

    current = metrics['current']
    benchmark = metrics['benchmark']
    previous = metrics.get('previous')

    yoy_rev = metrics.get('yoy_revenue_change')
    yoy_arpu = metrics.get('yoy_arpu_change')
    mom_rev = metrics.get('mom_revenue_change')
    mom_arpu = metrics.get('mom_arpu_change')

    _, summary_prefix = _summary_text(yoy_rev)

    # ── 工具函数 ──
    def _arrow(value: float | None) -> str:
        if value is None:
            return ''
        return '↑' if value > 0 else ('↓' if value < 0 else '→')

    def _highlight(text: str) -> str:
        """用【】括号强调关键数字"""
        return f'【{text}】'

    # ── 模块 ──
    ms = metrics.get('module_share', {})
    module_current = None
    for m in data['module_trend']:
        if m['event'] == event_name:
            module_current = m
            break
    if module_current is None:
        module_current = data['module_trend'][-1]

    # ── 用户分层 ──
    tiers = data['user_tier_trend']
    tier_current = tiers[0] if tiers else {}
    tier_benchmark = tiers[-1] if len(tiers) >= 2 else {}
    tier_previous = tiers[1] if len(tiers) >= 3 else tiers[-1] if len(tiers) >= 2 else {}

    # 关键指标表格
    prev_pay_rate = previous['pay_rate'] if previous else current['pay_rate']
    metrics_table = (
        f'| 指标 | 数值 | 环比 | 同比 vs {benchmark_event} |\n'
        f'| --- | --- | --- | --- |\n'
        f'| 当期营收 | ${_fmt_revenue(current["revenue"])} | {_arrow(mom_rev)} {_fmt_pct(mom_rev)} | {_arrow(yoy_rev)} {_fmt_pct(yoy_rev)} |\n'
        f'| 当期 ARPU | ${current["arpu"]:.2f} | {_arrow(mom_arpu)} {_fmt_pct(mom_arpu)} | {_arrow(yoy_arpu)} {_fmt_pct(yoy_arpu)} |\n'
        f'| 付费率 | {current["pay_rate"]:.2f}% | {(current["pay_rate"] - prev_pay_rate):+.2f}% | {(current["pay_rate"] - benchmark["pay_rate"]):+.2f}% |'
    )

    # 模块占比表格
    module_table = (
        f'| 模块 | 占比 | 营收 | 备注 |\n'
        f'| --- | --- | --- | --- |\n'
        f'| 外显类 | {ms.get("appearance", 0):.1f}% | ${_fmt_revenue(module_current["appearance"])} | 受单兵种BUFF影响，未衰减 |\n'
        f'| >> 小游戏 | {ms.get("minigame", 0):.1f}% | ${_fmt_revenue(module_current["minigame"])} | >> 本期新增，纯增量收入 |\n'
        f'| 混合/养成 | {ms.get("hybrid", 0):.1f}% | ${_fmt_revenue(module_current["hybrid"])} | 主力营收来源 |'
    )

    # 用户分层表格
    tier_rows = []
    for tier_key, tier_label in [('super_r', '超R'), ('big_r', '大R'), ('mid_r', '中R')]:
        cur_val = tier_current.get(tier_key, 0)
        prev_val = tier_previous.get(tier_key, 0)
        bench_val = tier_benchmark.get(tier_key, 0)
        yoy_c = ((cur_val - bench_val) / bench_val * 100) if bench_val > 0 else None
        mom_c = ((cur_val - prev_val) / prev_val * 100) if prev_val > 0 else None
        tier_rows.append(
            f'| {tier_label} | ${cur_val:.2f} | ${prev_val:.2f} | ${bench_val:.2f} '
            f'| {_arrow(yoy_c)} {_fmt_pct(yoy_c)} | {_arrow(mom_c)} {_fmt_pct(mom_c)} |'
        )

    tier_table = (
        f'| 层级 | {event_name} | {tier_previous.get("event", "")} | {benchmark_event} | 同比 | 环比 |\n'
        f'| --- | --- | --- | --- | --- | --- |\n'
        + '\n'.join(tier_rows)
    )

    # ── 子活动诊断 ──
    keep_items = [s for s in data['sub_activity_detail'] if s['status'] == 'Keep']
    optimize_items = [s for s in data['sub_activity_detail'] if s['status'] == 'Optimize']

    def _format_sub_wiki(items: list, emoji: str) -> str:
        lines = []
        for item in items:
            lines.append(
                f'- {emoji} {item["name"]}（{item["type"]}）— 营收 ${_fmt_revenue(item["revenue"])}'
            )
            lines.append(f'    ∟ {item["reason"]}')
        return '\n'.join(lines) if lines else '- 无'

    keep_list = _format_sub_wiki(keep_items, '[+]')
    optimize_list = _format_sub_wiki(optimize_items, '[!]')

    # ── Action Items ──
    action_lines = []

    # P0: 从 Keep 中按模块聚合生成建议
    keep_modules_wiki = {}
    for k in keep_items:
        mod = k.get('type', '未知')
        if mod not in keep_modules_wiki:
            keep_modules_wiki[mod] = []
        keep_modules_wiki[mod].append(k)

    idx = 1
    for mod, items in keep_modules_wiki.items():
        names = '、'.join(i['name'] for i in items)
        total_rev = sum(i['revenue'] for i in items)
        action_lines.append(
            f'{idx}. 【{mod}模块持续投入】{names}已验证成功（合计 ${_fmt_revenue(total_rev)}），'
            f'建议持续迭代并探索更多付费点'
        )
        idx += 1

    p1_lines = []
    for item in optimize_items:
        p1_lines.append(f'{idx}. 【{item["name"]}优化】{item["reason"]}')
        idx += 1

    p2_lines = []
    # Watch 项转 P2
    if 'tier_headcount_trend' in data and len(data['tier_headcount_trend']) >= 2:
        th = data['tier_headcount_trend']
        for key, label in [('chaoR', 'chaoR 留存体系建设'), ('daR', 'daR 晋升通道优化')]:
            v0 = th[0].get(key, 0)
            v1 = th[-1].get(key, 0)
            if v0 > 0:
                change = (v1 - v0) / v0 * 100
                if change < -5 or abs(change) < 3:
                    p2_lines.append(f'{idx}. 【{label}】{v0:,} → {v1:,}（{change:+.1f}%），需专项优化')
                    idx += 1

    action_items = '\n'.join(action_lines)
    p1_items = '\n'.join(p1_lines)
    p2_items = '\n'.join(p2_lines)

    # ── 待人工补充清单 ──
    checklist_wiki = []

    if keep_modules_wiki:
        checklist_wiki.append('### P0 待补充\n')
        for mod, items in keep_modules_wiki.items():
            names = '、'.join(i['name'] for i in items)
            checklist_wiki.append(
                f'- [ ] {mod}模块迭代方向 - {names}已验证成功，'
                f'需明确：下期新增哪些付费点？是否有新玩法规划？'
            )
        # chaoR 风险
        if 'tier_headcount_trend' in data and len(data['tier_headcount_trend']) >= 2:
            th = data['tier_headcount_trend']
            chao_v0 = th[0].get('chaoR', 0)
            chao_v1 = th[-1].get('chaoR', 0)
            if chao_v0 > 0 and (chao_v1 - chao_v0) / chao_v0 * 100 < -10:
                checklist_wiki.append(
                    '- [ ] chaoR 流失根因分析 - 需人工排查：是内容吸引力下降、'
                    '竞品分流、还是生命周期自然衰退？是否有定性访谈数据？'
                )

    if optimize_items:
        checklist_wiki.append('\n### P1 待补充\n')
        for item in optimize_items:
            checklist_wiki.append(
                f'- [ ] {item["name"]}优化方案 - 需明确：'
                f'具体调整哪些参数？（如奖池结构、档位定价、SKU 精简方案等）'
            )
        xiao_t_w = data.get('core_metrics_by_tier', {}).get('xiaoR', {})
        if xiao_t_w.get('buy_rate', 100) < 15:
            checklist_wiki.append(
                '- [ ] xiaoR 低门槛付费设计 - 需明确：'
                '计划推出哪些入门级付费内容？定价区间？'
            )

    if p2_lines:
        checklist_wiki.append('\n### P2 待补充\n')
        if 'tier_headcount_trend' in data and len(data['tier_headcount_trend']) >= 2:
            th = data['tier_headcount_trend']
            for key, desc in [('chaoR', 'chaoR 专属权益体系设计 - 需明确：专属内容/权益具体包含哪些？预期投入和上线时间？'),
                              ('daR', 'daR 晋升通道设计 - 需明确：中高档付费内容如何调整？zhongR→daR 转化路径？')]:
                v0 = th[0].get(key, 0)
                v1 = th[-1].get(key, 0)
                if v0 > 0:
                    change = (v1 - v0) / v0 * 100
                    if change < -5 or abs(change) < 3:
                        checklist_wiki.append(f'- [ ] {desc}')

    human_checklist_wiki = '\n'.join(checklist_wiki) if checklist_wiki else '- [ ] 暂无待补充项'

    # ── 图表占位（Wiki 需手动插入图片）──
    c1 = os.path.join(chart_dir, '1_Revenue_Trend.png') if chart_dir else '1_Revenue_Trend.png'
    c2 = os.path.join(chart_dir, '2_Module_Structure.png') if chart_dir else '2_Module_Structure.png'
    c3 = os.path.join(chart_dir, '3_User_Growth.png') if chart_dir else '3_User_Growth.png'

    trend_desc = metrics.get('trend_description', '')
    trend_pattern = metrics.get('trend_pattern', 'N/A')

    # ── 分层洞察 ──
    tier_insight_parts = []
    for tier_key, tier_label in [('super_r', '超R'), ('big_r', '大R'), ('mid_r', '中R')]:
        cur_val = tier_current.get(tier_key, 0)
        bench_val = tier_benchmark.get(tier_key, 0)
        yoy_c = ((cur_val - bench_val) / bench_val * 100) if bench_val > 0 else 0
        tier_insight_parts.append(f'{tier_label} {_fmt_pct(yoy_c)}')
    tier_insight_text = (
        f'各层级ARPU同比均实现大幅增长（{", ".join(tier_insight_parts)}），'
        '说明新增内容对全层级用户的付费刺激效果显著。'
    )

    # ── 日维度营收（Wiki 简版）──
    daily_wiki_section = ''
    if 'daily_revenue' in data and len(data['daily_revenue']) >= 3:
        dr = data['daily_revenue']
        total_days = len(dr)
        total_rev_d = sum(d['revenue'] for d in dr)
        first_third = max(1, total_days // 3)
        first_third_rev = sum(dr[i]['revenue'] for i in range(first_third))
        last_third_rev = sum(dr[i]['revenue'] for i in range(total_days - first_third, total_days))
        first_ratio = (first_third_rev / total_rev_d * 100) if total_rev_d > 0 else 0
        last_ratio = (last_third_rev / total_rev_d * 100) if total_rev_d > 0 else 0
        peak_day = max(dr, key=lambda d: d['revenue'])
        valley_day = min(dr, key=lambda d: d['revenue'])

        if first_ratio > 45:
            rhythm_type = '前置型'
            rhythm_desc = f'前 {first_third} 天贡献了 {first_ratio:.1f}% 的营收，付费高度集中在活动初期'
        elif last_ratio > 40:
            rhythm_type = '长尾型'
            rhythm_desc = f'后 {first_third} 天仍贡献 {last_ratio:.1f}% 营收，活动持续吸引力强'
        else:
            rhythm_type = '均匀型'
            rhythm_desc = f'前 {first_third} 天占 {first_ratio:.1f}%，后 {first_third} 天占 {last_ratio:.1f}%，付费节奏平稳'

        daily_wiki_section = (
            f'## 5. 日维度营收分析\n\n'
            f'> 付费节奏: {rhythm_type} — {rhythm_desc}\n'
            f'> 峰值日: {peak_day["date"]}（${_fmt_revenue(peak_day["revenue"])}）｜'
            f' 谷值日: {valley_day["date"]}（${_fmt_revenue(valley_day["revenue"])}）'
        )

    content = f"""# {event_name} — 活动复盘总结

> 对标活动: {benchmark_event} ｜ 生成时间: {generated_at} ｜ 数据来源: Notion

---

## 1. Executive Summary

> {event_name}活动{summary_prefix}总营收 {_highlight('$' + _fmt_revenue(current['revenue']))}，同比增长 {_highlight(_fmt_pct(yoy_rev))}，ARPU 同比增长 {_highlight(_fmt_pct(yoy_arpu))}。

---

## 2. 核心大盘趋势

> [图表] 请手动插入: {c1}

### 趋势判断: {trend_pattern}

{trend_desc}

### 关键指标速览

{metrics_table}

---

## 3. 模块营收结构

> [图表] 请手动插入: {c2}

### 当期模块占比

{module_table}

> [洞察] 混合/养成类仍为主力营收来源（{ms.get('hybrid', 0):.1f}%）。本期最亮眼的变化是【小游戏模块首次独立计入】，占比达{ms.get('minigame', 0):.1f}%，贡献${_fmt_revenue(module_current['minigame'])}营收。关键发现：新增小游戏模块并未挤压原有各模块付费，属于纯增量收入。

---

## 4. 用户分层分析

> [图表] 请手动插入: {c3}

### 用户分层 ARPU 对比

{tier_table}

> [洞察] {tier_insight_text}

---"""

    # 动态章节号，日维度可选插入
    sec = 5

    if daily_wiki_section:
        content += f'\n\n{daily_wiki_section}\n\n---'
        sec += 1

    content += f"""

## {sec}. 子活动诊断

### {sec}.1 Keep — 表现优秀，建议保留

{keep_list}

### {sec}.2 Optimize — 待优化项

{optimize_list}

---

## {sec + 1}. Action Items

### P0 — 立即执行

{action_items}

### P1 — 下期优化

{p1_items}

### P2 — 中期规划

{p2_items}

---

## {sec + 2}. 待人工补充清单

> 以下为数据分析无法覆盖的决策项，需人工补充后报告才算完整。

{human_checklist_wiki}

---

> 本报告由 generate-event-review Skill 自动生成 ｜ 数据来源: Notion"""

    return content
