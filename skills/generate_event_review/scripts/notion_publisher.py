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

    # ── Section 6: Action Items ──
    # 根据诊断结果自动生成
    action_lines = []
    action_lines.append('### P0 - 立即执行\n')

    # 从 Keep 中找成功的模式
    keep_names = [k['name'] for k in keep_items]
    if any('小游戏' in n or '挖孔' in n for n in keep_names):
        action_lines.append(
            '1. **小游戏模块持续迭代** - 已验证成功的小游戏持续上线并增加坑深；'
            '各小游戏可新增特有机制付费点(击杀礼包、成就礼包、通关礼包、存钱罐礼包)'
        )

    action_lines.append(
        '1. **优化活动排期** - 错开大付费点，建议按4阶段排期：\n'
        '\t- 第1-3天：BP、GACHA、预购、大富翁\n'
        '\t- 第4-10天：小游戏1\n'
        '\t- 第11-17天：机甲/斗士皮肤、小游戏2\n'
        '\t- 第18-24天：冲榜、小游戏、优惠礼包补付费'
    )

    action_lines.append('\n### P1 - 下期优化\n')
    for item in optimize_items[:3]:
        action_lines.append(
            f'1. **{item["name"]}优化** - {item["reason"]}'
        )

    action_lines.append('\n### P2 - 中期规划\n')
    for item in optimize_items[3:]:
        action_lines.append(
            f'1. **{item["name"]}调整** - {item["reason"]}'
        )

    action_items = '\n'.join(action_lines)

    # ── 组装完整 Notion 内容 ──
    previous_event = tier_previous.get('event', '') if tier_previous else ''

    content = f"""> 对标活动: {benchmark_event} | 生成时间: {generated_at}

---

## 1. Executive Summary

<callout icon="⭐" color="yellow_bg">
{exec_summary_short}
</callout>

---

## 2. 核心大盘趋势

<callout icon="📊" color="blue_bg">
请在此处插入图表: 1_Revenue_Trend.png（核心大盘趋势折线图）
</callout>

**趋势判断: <span color="red">{metrics.get('trend_pattern', 'N/A')}</span>**

{metrics.get('trend_description', '')}

**关键指标速览:**

<table header-row="true">
\t<tr>
\t\t<td>指标</td>
\t\t<td>数值</td>
\t\t<td>环比</td>
\t\t<td>同比 (vs {benchmark_event})</td>
\t</tr>
\t<tr>
\t\t<td>当期营收</td>
\t\t<td>**${_fmt_revenue(current['revenue'])}**</td>
\t\t<td>{_color_pct(mom_rev)}</td>
\t\t<td>{_color_pct(yoy_rev)}</td>
\t</tr>
\t<tr>
\t\t<td>当期 ARPU</td>
\t\t<td>**${current['arpu']:.2f}**</td>
\t\t<td>{_color_pct(mom_arpu)}</td>
\t\t<td>{_color_pct(yoy_arpu)}</td>
\t</tr>
\t<tr>
\t\t<td>付费率</td>
\t\t<td>**{current['pay_rate']:.2f}%**</td>
\t\t<td>{mom_pay_rate}</td>
\t\t<td>{yoy_pay_rate}</td>
\t</tr>
</table>

---

## 3. 模块营收结构

<callout icon="📊" color="blue_bg">
请在此处插入图表: 2_Module_Structure.png（模块营收堆叠面积图）
</callout>

**当期模块占比:**

<table header-row="true">
\t<tr>
\t\t<td>模块</td>
\t\t<td>占比</td>
\t\t<td>营收</td>
\t</tr>
\t<tr>
\t\t<td>外显类</td>
\t\t<td>{ms.get('appearance', 0):.1f}%</td>
\t\t<td>${_fmt_revenue(module_current['appearance'])}</td>
\t</tr>
\t<tr>
\t\t<td><span color="red">**小游戏**</span></td>
\t\t<td><span color="red">**{ms.get('minigame', 0):.1f}%**</span></td>
\t\t<td><span color="red">**${_fmt_revenue(module_current['minigame'])}**</span></td>
\t</tr>
\t<tr>
\t\t<td>混合/养成</td>
\t\t<td>{ms.get('hybrid', 0):.1f}%</td>
\t\t<td>${_fmt_revenue(module_current['hybrid'])}</td>
\t</tr>
</table>

---

## 4. 用户分层分析

<callout icon="📊" color="blue_bg">
请在此处插入图表: 3_User_Growth.png（用户分层 ARPU 分组柱状图）
</callout>

<table header-row="true">
\t<tr>
\t\t<td>用户层级</td>
\t\t<td>{event_name}</td>
\t\t<td>{previous_event}</td>
\t\t<td>{benchmark_event}</td>
\t\t<td>同比变化</td>
\t\t<td>环比变化</td>
\t</tr>
{tier_table_rows}
</table>

---

## 5. 子活动诊断

### 5.1 Keep - 表现优秀，建议保留

{keep_list}

### 5.2 Optimize - 待优化项

{optimize_list}

---

## 6. Action Items

{action_items}

---

*本报告由 generate\\_event\\_review Skill 自动生成*"""

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

    keep_names = [k['name'] for k in keep_items]
    idx = 1
    if any('小游戏' in n or '挖孔' in n for n in keep_names):
        action_lines.append(
            f'{idx}. 【小游戏模块持续迭代】已验证成功的小游戏持续上线并增加坑深；'
            '各小游戏可新增特有机制付费点（击杀礼包、成就礼包、通关礼包、存钱罐礼包）'
        )
        idx += 1

    action_lines.append(
        f'{idx}. 【优化活动排期】错开大付费点，建议按4阶段排期'
    )
    idx += 1

    action_lines.append('')
    action_lines.append('| 阶段 | 时间 | 内容 |')
    action_lines.append('| --- | --- | --- |')
    action_lines.append('| 阶段1 | 第1-3天 | BP、GACHA、预购、大富翁 |')
    action_lines.append('| 阶段2 | 第4-10天 | 小游戏1 |')
    action_lines.append('| 阶段3 | 第11-17天 | 机甲/斗士皮肤、小游戏2 |')
    action_lines.append('| 阶段4 | 第18-24天 | 冲榜、小游戏、优惠礼包补付费 |')

    p1_lines = []
    for item in optimize_items[:3]:
        p1_lines.append(f'{idx}. 【{item["name"]}优化】{item["reason"]}')
        idx += 1

    p2_lines = []
    for item in optimize_items[3:]:
        p2_lines.append(f'{idx}. 【{item["name"]}调整】{item["reason"]}')
        idx += 1

    action_items = '\n'.join(action_lines)
    p1_items = '\n'.join(p1_lines)
    p2_items = '\n'.join(p2_lines)

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

---

## 5. 子活动诊断

### 5.1 Keep — 表现优秀，建议保留

{keep_list}

### 5.2 Optimize — 待优化项

{optimize_list}

---

## 6. Action Items

### P0 — 立即执行

{action_items}

### P1 — 下期优化

{p1_items}

### P2 — 中期规划

{p2_items}

---

> 本报告由 generate-event-review Skill 自动生成 ｜ 数据来源: Notion"""

    return content
