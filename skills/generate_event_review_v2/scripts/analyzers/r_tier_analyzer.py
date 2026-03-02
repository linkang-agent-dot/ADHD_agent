"""
分析器4: R级付费分析 - R级结构分析与活动定位判断。
"""

from .base_analyzer import BaseAnalyzer, AnalysisResult


class RTierAnalyzer(BaseAnalyzer):
    """
    R级付费分析器。

    分析逻辑：
    1. 各R级 revenue/pay_rate/arpu/arppu 的环比、同比变化
    2. 各R级占总营收比例，分析付费结构是否健康
    3. 活动定位判断（高R向/普惠型/全面提升型）
    4. 检测R级之间的异常交叉现象
    """

    def analyze(self, data: dict) -> AnalysisResult:
        rtp = data.get("r_tier_payment", {})
        tiers = rtp.get("tiers", [])
        ts = rtp.get("time_series", [])
        meta = data.get("meta", {})

        # 多对标支持：优先读取 benchmarks 数组
        benchmarks = rtp.get("benchmarks", [])

        result = AnalysisResult(module_name="R级付费分析")
        details = []
        suggestions = []

        if len(ts) < 2 and not benchmarks:
            result.conclusion = "R级数据不足，无法分析"
            result.severity = "关注"
            return result

        # 智能识别当前活动：优先用 meta.event_name 匹配，否则取最后一条
        current = None
        current_idx = -1
        event_name = meta.get("event_name", "")
        if event_name:
            for i, item in enumerate(ts):
                if event_name in item.get("event", "") or item.get("event", "") in event_name:
                    current = item
                    current_idx = i
                    break
        if current is None:
            current = ts[-1] if ts else {}
            current_idx = len(ts) - 1

        # 确定对比对象列表
        compare_list = []  # [{event, data}, ...]
        if benchmarks:
            # 使用显式标注的对标活动
            compare_list = benchmarks
        else:
            # 向后兼容：从时间序列中取相邻活动
            if current_idx + 1 < len(ts):
                compare_list = [ts[current_idx + 1]]
            elif current_idx - 1 >= 0:
                compare_list = [ts[current_idx - 1]]

        # 主对比（第一个对标）
        previous = compare_list[0] if compare_list else {}

        current_data = current.get("data", {})
        previous_data = previous.get("data", {})

        # 1. 各R级营收占比 & 与主对标对比
        total_revenue = sum(current_data.get(t, {}).get("revenue", 0) for t in tiers)
        tier_shares = {}
        tier_changes = {}

        for tier in tiers:
            curr = current_data.get(tier, {})
            prev = previous_data.get(tier, {})
            revenue = curr.get("revenue", 0)
            share = round(revenue / total_revenue * 100, 1) if total_revenue > 0 else 0
            tier_shares[tier] = share

            changes = {}
            for key in ["revenue", "pay_rate", "arpu", "arppu"]:
                changes[key] = self._calc_change_rate(curr.get(key, 0), prev.get(key, 0))
            tier_changes[tier] = changes

            detail_str = (
                f"{tier}: 营收占比 {share}%, vs {previous.get('event', '对标')} 营收 {self._format_change(changes['revenue'])}, "
                f"付费率 {self._format_change(changes['pay_rate'])}, ARPU {self._format_change(changes['arpu'])}"
            )
            details.append(detail_str)

        # 1.5 其他对标的简要对比
        all_bench_changes = {}  # {bench_event: {tier: {key: change}}}
        for bench_idx, bench in enumerate(compare_list):
            if bench_idx == 0:
                all_bench_changes[bench.get("event", "对标1")] = tier_changes
                continue
            bench_data = bench.get("data", {})
            bench_tier_changes = {}
            for tier in tiers:
                curr = current_data.get(tier, {})
                b = bench_data.get(tier, {})
                changes = {}
                for key in ["revenue", "pay_rate", "arpu", "arppu"]:
                    changes[key] = self._calc_change_rate(curr.get(key, 0), b.get(key, 0))
                bench_tier_changes[tier] = changes
                details.append(
                    f"{tier} vs {bench.get('event', f'对标{bench_idx+1}')}: "
                    f"营收 {self._format_change(changes['revenue'])}, "
                    f"付费率 {self._format_change(changes['pay_rate'])}"
                )
            all_bench_changes[bench.get("event", f"对标{bench_idx+1}")] = bench_tier_changes

        # 2. 活动定位判断
        top_tier = tiers[0] if tiers else "超R"
        top_share = tier_shares.get(top_tier, 0)
        mid_low_tiers = tiers[2:] if len(tiers) > 2 else []
        mid_low_rate_boost = any(
            tier_changes.get(t, {}).get("pay_rate", 0) > 10 for t in mid_low_tiers
        )

        all_positive = all(
            tier_changes.get(t, {}).get("revenue", 0) > 0 for t in tiers
        )

        if top_share > 50:
            positioning = "高R向活动"
            positioning_detail = f"{top_tier}营收占比达 {top_share}%，活动对高付费用户吸引力强"
        elif mid_low_rate_boost:
            positioning = "普惠型活动"
            positioning_detail = "中小R付费率提升显著，活动覆盖面广"
        elif all_positive:
            positioning = "全面提升型活动"
            positioning_detail = "各R级均实现增长，活动设计均衡"
        else:
            positioning = "结构性变化活动"
            positioning_detail = "部分R级增长、部分下滑，需关注结构变化"

        details.append(f"活动定位: {positioning} - {positioning_detail}")

        # 3. 异常交叉检测
        severity = "正常"
        for i, tier in enumerate(tiers):
            change = tier_changes.get(tier, {}).get("revenue", 0)
            if change < -20:
                severity = "异常" if severity != "严重" else severity
                suggestions.append(f"{tier} 营收vs主对标下降 {abs(change):.1f}%，建议排查原因")
            elif change < -10:
                if severity == "正常":
                    severity = "关注"

        if len(tiers) >= 2:
            top_change = tier_changes.get(tiers[0], {}).get("revenue", 0)
            bottom_change = tier_changes.get(tiers[-1], {}).get("revenue", 0)
            if top_change < -10 and bottom_change > 10:
                details.append(f"交叉现象: {tiers[0]} 下降但 {tiers[-1]} 上升，付费重心下移")
                suggestions.append("高付费用户贡献减弱，建议优化高价值内容吸引力")

        result.conclusion = f"{positioning}。{positioning_detail}"
        result.severity = severity
        result.details = details
        result.suggestions = suggestions
        result.chart_data = {
            "tiers": tiers,
            "time_series": ts,
            "benchmarks": compare_list,
            "current_data": current_data,
            "tier_shares": tier_shares,
        }
        result.raw_metrics = {
            "tier_shares": tier_shares,
            "tier_changes": tier_changes,
            "all_bench_changes": all_bench_changes,
            "activity_positioning": positioning,
            "total_revenue": total_revenue,
        }

        return result
