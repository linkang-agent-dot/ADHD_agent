"""
分析器5: 付费转化分析 - 转化衰减比例分析与分布偏移检测。

核心思路：玩家总量逐年下滑，用绝对人数变化判断不精确。
改用「转化比例分布」（各档位付费人数占总付费人数的比例）来评估，
这样排除了玩家基数变化的干扰，能精准反映付费结构的真实变化。
"""

import math
from .base_analyzer import BaseAnalyzer, AnalysisResult


class ConversionAnalyzer(BaseAnalyzer):
    """
    付费转化分析器（转化衰减比例版）。

    分析逻辑：
    1. AI 区间自动划分（按衰减率断层或对数等距）
    2. 当期与对标各自计算「比例分布」（区间人数 / 总付费人数）
    3. 对比比例偏移（share shift），而非绝对人数变化
    4. 面积衰减分析：累积分布对比
    5. 综合定性判断
    """

    def analyze(self, data: dict) -> AnalysisResult:
        pc = data.get("payment_conversion", {})
        current = pc.get("current", {})
        price_tiers = current.get("price_tiers", [])

        # 多对标支持：优先读取 comparisons 数组，兼容单个 comparison
        comparisons = pc.get("comparisons", [])
        if not comparisons:
            single_comp = pc.get("comparison", {})
            if single_comp and single_comp.get("price_tiers"):
                comparisons = [single_comp]

        result = AnalysisResult(module_name="付费转化分析")
        details = []
        suggestions = []

        if len(price_tiers) < 3:
            result.conclusion = "价位数据不足，无法分析"
            result.severity = "关注"
            return result

        # 1. 按价位升序排列
        sorted_tiers = sorted(price_tiers, key=lambda x: x["price"])

        # 处理所有对标数据
        all_sorted_comps = []
        for comp in comparisons:
            comp_tiers = comp.get("price_tiers", [])
            comp_event = comp.get("event", "对标")
            if comp_tiers:
                all_sorted_comps.append({
                    "event": comp_event,
                    "sorted_tiers": sorted(comp_tiers, key=lambda x: x["price"]),
                })
        # 主对标（第一个）
        primary_comp = all_sorted_comps[0] if all_sorted_comps else None
        sorted_comp = primary_comp["sorted_tiers"] if primary_comp else []

        # 2. AI 区间划分
        intervals = self._auto_segment(sorted_tiers)
        details.append(f"AI 自动划分为 {len(intervals)} 个价位区间")

        # 总付费人数（用于计算比例）
        total_payers_current = sum(t["payers"] for t in sorted_tiers)
        total_revenue = sum(t["price"] * t["purchases"] for t in sorted_tiers)

        # 3. 每个区间计算「比例分布」，支持多个对标
        interval_stats = []
        for interval in intervals:
            label = interval["label"]
            low = interval["low"]
            high = interval["high"]

            # 当期
            tiers_in_range = [t for t in sorted_tiers if low <= t["price"] <= high]
            payers = sum(t["payers"] for t in tiers_in_range)
            purchases = sum(t["purchases"] for t in tiers_in_range)
            interval_revenue = sum(t["price"] * t["purchases"] for t in tiers_in_range)
            revenue_share = round(interval_revenue / total_revenue * 100, 1) if total_revenue > 0 else 0
            payer_share = round(payers / total_payers_current * 100, 2) if total_payers_current > 0 else 0

            stat = {
                "label": label, "low": low, "high": high,
                "payers": payers, "purchases": purchases,
                "revenue": interval_revenue, "revenue_share": revenue_share,
                "payer_share": payer_share,
                "comp_data": [],  # 多对标数据
            }

            # 计算每个对标的区间数据
            for comp_item in all_sorted_comps:
                c_tiers = comp_item["sorted_tiers"]
                c_event = comp_item["event"]
                total_c_payers = sum(t["payers"] for t in c_tiers)
                comp_in_range = [t for t in c_tiers if low <= t["price"] <= high]
                comp_payers = sum(t["payers"] for t in comp_in_range)
                comp_share = round(comp_payers / total_c_payers * 100, 2) if total_c_payers > 0 else 0
                share_shift = round(payer_share - comp_share, 2)
                stat["comp_data"].append({
                    "event": c_event,
                    "comp_payers": comp_payers,
                    "comp_payer_share": comp_share,
                    "share_shift": share_shift,
                    "total_payers": total_c_payers,
                })

            # 向后兼容：主对标写入 stat 顶层
            if stat["comp_data"]:
                primary = stat["comp_data"][0]
                stat["comp_payer_share"] = primary["comp_payer_share"]
                stat["comp_payers"] = primary["comp_payers"]
                stat["share_shift"] = primary["share_shift"]

            interval_stats.append(stat)

        # 4. 输出比例分布对比（所有对标）
        for stat in interval_stats:
            detail_str = f"  {stat['label']}: 当期 {stat['payer_share']:.1f}%"
            for cd in stat["comp_data"]:
                shift = cd["share_shift"]
                shift_dir = "↑" if shift > 0 else "↓"
                detail_str += f" | vs {cd['event']} {cd['comp_payer_share']:.1f}%（{shift_dir}{abs(shift):.1f}pp）"
            detail_str += f", 营收占比 {stat['revenue_share']}%"
            details.append(detail_str)

        # 5. 转化衰减比例分析（主对标）
        if len(interval_stats) >= 2:
            details.append("转化衰减比例（高价位 / 低价位人数比）:")
            for i in range(1, len(interval_stats)):
                prev = interval_stats[i - 1]
                curr = interval_stats[i]
                if prev["payers"] > 0:
                    decay_ratio_current = round(curr["payers"] / prev["payers"] * 100, 1)
                else:
                    decay_ratio_current = 0

                detail_str = f"  {prev['label']} → {curr['label']}: 当期衰减率 {decay_ratio_current}%"

                if prev.get("comp_payers", 0) > 0 and "comp_payers" in curr:
                    decay_ratio_comp = round(curr["comp_payers"] / prev["comp_payers"] * 100, 1)
                    decay_diff = round(decay_ratio_current - decay_ratio_comp, 1)
                    direction = "改善" if decay_diff > 0 else "恶化"
                    detail_str += f" vs 主对标 {decay_ratio_comp}%（{direction} {abs(decay_diff):.1f}pp）"

                details.append(detail_str)

        # 6. 异常判断 - 基于比例偏移（主对标）
        severity = "正常"
        for stat in interval_stats:
            shift = stat.get("share_shift", 0)
            if abs(shift) > 5:
                direction = "上升" if shift > 0 else "下降"
                details.append(f"结构性变化: {stat['label']} 占比 {direction} {abs(shift):.1f}pp")

        low_interval_shifts = [s for s in interval_stats if s.get("share_shift", 0) > 3 and s["low"] <= intervals[0]["high"]]
        high_interval_drops = [s for s in interval_stats if s.get("share_shift", 0) < -3 and s["low"] > intervals[0]["high"]]

        if low_interval_shifts and high_interval_drops:
            severity = "关注"
            suggestions.append("付费结构向低价位集中，高价位占比下降，建议增强中高价位商品吸引力")
        elif high_interval_drops and not low_interval_shifts:
            severity = "关注"
            suggestions.append("高价位占比下降，整体付费深度可能不足")

        # 检查衰减加速
        decay_worsened_count = 0
        if len(interval_stats) >= 2 and sorted_comp:
            for i in range(1, len(interval_stats)):
                prev = interval_stats[i - 1]
                curr = interval_stats[i]
                if prev["payers"] > 0 and prev.get("comp_payers", 0) > 0:
                    ratio_c = curr["payers"] / prev["payers"]
                    ratio_comp = curr.get("comp_payers", 0) / prev["comp_payers"]
                    if ratio_c < ratio_comp * 0.8:
                        decay_worsened_count += 1

            if decay_worsened_count >= (len(interval_stats) - 1) // 2:
                severity = "异常"
                suggestions.append("多个价位段转化衰减加速，建议全面检查商品定价与内容吸引力")

        # 综合结论
        if severity == "正常":
            result.conclusion = "付费转化比例分布稳定，各价位段结构合理"
        elif severity == "关注":
            result.conclusion = "付费转化结构有偏移，部分价位段占比变化需关注"
        else:
            result.conclusion = "付费转化衰减加速，多价位段结构性恶化"

        result.severity = severity
        result.details = details
        result.suggestions = suggestions
        result.chart_data = {
            "sorted_tiers": sorted_tiers,
            "sorted_comp": sorted_comp,  # 主对标（向后兼容）
            "all_comps": all_sorted_comps,  # 所有对标
            "intervals": intervals,
            "interval_stats": interval_stats,
            "total_payers_current": total_payers_current,
            "total_payers_comp": sum(t["payers"] for t in sorted_comp) if sorted_comp else 0,
        }
        result.raw_metrics = {
            "intervals": intervals,
            "interval_stats": interval_stats,
            "total_revenue": total_revenue,
        }

        return result

    def _auto_segment(self, sorted_tiers: list) -> list:
        """
        AI 自动划分价位区间。

        策略:
        1. 计算相邻档位 payers 衰减率
        2. 在衰减率断层（>40%）处划分
        3. 兜底: 对数等距分 3~5 组
        """
        if len(sorted_tiers) <= 3:
            return self._log_equal_segment(sorted_tiers, 3)

        # 计算衰减率
        decay_rates = []
        for i in range(1, len(sorted_tiers)):
            prev_payers = sorted_tiers[i - 1]["payers"]
            curr_payers = sorted_tiers[i]["payers"]
            if prev_payers > 0:
                decay = (prev_payers - curr_payers) / prev_payers
            else:
                decay = 0
            decay_rates.append(decay)

        # 找断层点（衰减率 > 40%）
        breakpoints = [0]  # 起始索引
        for i, rate in enumerate(decay_rates):
            if rate > 0.4:
                breakpoints.append(i + 1)
        breakpoints.append(len(sorted_tiers))

        # 至少分 2 组，最多 6 组
        if len(breakpoints) - 1 < 2 or len(breakpoints) - 1 > 6:
            return self._log_equal_segment(sorted_tiers, min(5, max(3, len(sorted_tiers) // 2)))

        # 构建区间
        intervals = []
        labels = ["低额", "中低额", "中额", "中高额", "高额", "超高额"]
        for i in range(len(breakpoints) - 1):
            start_idx = breakpoints[i]
            end_idx = breakpoints[i + 1] - 1
            low = sorted_tiers[start_idx]["price"]
            high = sorted_tiers[end_idx]["price"]
            label_idx = min(i, len(labels) - 1)

            if low == high:
                label = f"{labels[label_idx]}({low})"
            else:
                label = f"{labels[label_idx]}({low}-{high})"

            intervals.append({"label": label, "low": low, "high": high})

        return intervals

    def _log_equal_segment(self, sorted_tiers: list, n_groups: int) -> list:
        """对数等距分组"""
        prices = [t["price"] for t in sorted_tiers]
        min_price = min(prices)
        max_price = max(prices)

        if min_price <= 0:
            min_price = 1

        log_min = math.log10(min_price)
        log_max = math.log10(max_price)
        step = (log_max - log_min) / n_groups

        intervals = []
        labels = ["低额", "中低额", "中额", "中高额", "高额", "超高额"]

        for i in range(n_groups):
            low = 10 ** (log_min + step * i)
            high = 10 ** (log_min + step * (i + 1))

            if i == 0:
                low = min(prices)
            if i == n_groups - 1:
                high = max(prices)

            low = round(low, 0)
            high = round(high, 0)
            label_idx = min(i, len(labels) - 1)

            if low == high:
                label = f"{labels[label_idx]}({int(low)})"
            else:
                label = f"{labels[label_idx]}(≤{int(high)})" if i == 0 else f"{labels[label_idx]}({int(low)}-{int(high)})"

            intervals.append({"label": label, "low": low, "high": high})

        return intervals
