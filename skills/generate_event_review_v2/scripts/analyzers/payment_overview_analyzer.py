"""
分析器3: 付费整体分析 - 环比/同比/趋势形态判断。
"""

from .base_analyzer import BaseAnalyzer, AnalysisResult
import math


class PaymentOverviewAnalyzer(BaseAnalyzer):
    """
    付费整体分析器。

    分析逻辑：
    1. 计算环比变化（最后一条 vs 倒数第二条）
    2. 计算同比变化（当期 vs yoy_benchmark）
    3. 趋势形态判断（上升/V型/下降/震荡）
    4. 四大指标各自评估
    5. 综合评估效果
    """

    def analyze(self, data: dict) -> AnalysisResult:
        po = data.get("payment_overview", {})
        ts = po.get("time_series", [])
        meta = data.get("meta", {})

        # 支持多基准对比：优先读取 yoy_benchmarks 数组，兼容单个 yoy_benchmark
        yoy_benchmarks = po.get("yoy_benchmarks", [])
        if not yoy_benchmarks:
            single_yoy = po.get("yoy_benchmark", {})
            if single_yoy:
                yoy_benchmarks = [single_yoy]
        # 主基准为数组第一个元素（后续综合评估以此为准）
        yoy = yoy_benchmarks[0] if yoy_benchmarks else {}

        result = AnalysisResult(module_name="付费整体分析")
        details = []
        suggestions = []

        if len(ts) < 2:
            result.conclusion = "付费数据不足，无法分析"
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
            current = ts[-1]
            current_idx = len(ts) - 1

        # 其余活动为历史对比
        other_events = [item for i, item in enumerate(ts) if i != current_idx]

        # 1. 当前活动核心指标
        details.append(
            f"当前活动: {current.get('event', '')}, 营收 {self._format_number(current.get('revenue', 0))}, "
            f"付费率 {current.get('pay_rate', 0) * 100 if current.get('pay_rate', 0) < 1 else current.get('pay_rate', 0):.2f}%, "
            f"ARPU {current.get('arpu', 0):.2f}, ARPPU {current.get('arppu', 0):.2f}"
        )

        # 2. 与其他活动横向对比
        if other_events:
            avg_revenue = sum(e.get("revenue", 0) for e in other_events) / len(other_events)
            avg_pay_rate = sum(e.get("pay_rate", 0) for e in other_events) / len(other_events)
            avg_arpu = sum(e.get("arpu", 0) for e in other_events) / len(other_events)
            avg_arppu = sum(e.get("arppu", 0) for e in other_events) / len(other_events)

            rev_vs_avg = self._calc_change_rate(current.get("revenue", 0), avg_revenue) if avg_revenue > 0 else 0
            pr_vs_avg = self._calc_change_rate(current.get("pay_rate", 0), avg_pay_rate) if avg_pay_rate > 0 else 0
            arpu_vs_avg = self._calc_change_rate(current.get("arpu", 0), avg_arpu) if avg_arpu > 0 else 0
            arppu_vs_avg = self._calc_change_rate(current.get("arppu", 0), avg_arppu) if avg_arppu > 0 else 0

            details.append(
                f"vs 历史均值: 营收 {self._format_change(rev_vs_avg)}, "
                f"付费率 {self._format_change(pr_vs_avg)}, "
                f"ARPU {self._format_change(arpu_vs_avg)}, "
                f"ARPPU {self._format_change(arppu_vs_avg)}"
            )

            # 付费率排名
            all_pay_rates = [(e.get("event", ""), e.get("pay_rate", 0)) for e in ts]
            all_pay_rates.sort(key=lambda x: x[1], reverse=True)
            pr_rank = next((i + 1 for i, (name, _) in enumerate(all_pay_rates) if name == current.get("event", "")), 0)
            details.append(f"付费率排名: {pr_rank}/{len(all_pay_rates)}（{'最高' if pr_rank == 1 else '第' + str(pr_rank) + '名'}）")

            # ARPPU排名
            all_arppu = [(e.get("event", ""), e.get("arppu", 0)) for e in ts]
            all_arppu.sort(key=lambda x: x[1], reverse=True)
            arppu_rank = next((i + 1 for i, (name, _) in enumerate(all_arppu) if name == current.get("event", "")), 0)
            details.append(f"ARPPU排名: {arppu_rank}/{len(all_arppu)}（{'最高' if arppu_rank == 1 else '第' + str(arppu_rank) + '名'}）")

        # 3. 同比变化（支持多对标）
        yoy_changes = {}  # 主基准的变化，用于后续综合评估
        all_yoy_changes = []  # 所有对标的变化
        for bench_idx, bench in enumerate(yoy_benchmarks):
            bench_changes = {}
            for key in ["revenue", "pay_rate", "arpu", "arppu"]:
                bench_changes[key] = self._calc_change_rate(current.get(key, 0), bench.get(key, 0))
            all_yoy_changes.append({"event": bench.get("event", f"对标{bench_idx+1}"), "changes": bench_changes})
            if bench_idx == 0:
                yoy_changes = bench_changes  # 主基准

            details.append(
                f"vs {bench.get('event', f'对标{bench_idx+1}')}: 营收 {self._format_change(bench_changes['revenue'])}, "
                f"付费率 {self._format_change(bench_changes['pay_rate'])}, "
                f"ARPU {self._format_change(bench_changes['arpu'])}, "
                f"ARPPU {self._format_change(bench_changes['arppu'])}"
            )

        # 4. 趋势形态判断（用全部历史数据）
        revenues = [item.get("revenue", 0) for item in ts]
        trend_pattern = self._detect_trend_pattern(revenues)
        details.append(f"趋势形态: {trend_pattern}")

        # 5. 综合评估 — 基于当前活动在整体中的定位
        severity = "正常"

        # 核心逻辑：比较当前 vs 同比 或 vs 历史均值
        if yoy_changes:
            ref_revenue_change = yoy_changes.get("revenue", 0)
            ref_label = "同比"
        elif other_events:
            ref_revenue_change = rev_vs_avg
            ref_label = "vs历史均值"
        else:
            ref_revenue_change = 0
            ref_label = ""

        # 判断付费率高低
        pay_rate_val = current.get("pay_rate", 0)
        # 标准化为百分比
        pr_pct = pay_rate_val * 100 if pay_rate_val < 1 else pay_rate_val
        arppu_val = current.get("arppu", 0)

        conclusion_parts = []
        if pr_vs_avg > 10:
            conclusion_parts.append(f"付费率表现优异（{self._format_change(pr_vs_avg)} vs 历史均值）")
        elif pr_vs_avg > 0:
            conclusion_parts.append(f"付费率高于历史均值（{self._format_change(pr_vs_avg)}）")

        if arppu_vs_avg < -15:
            conclusion_parts.append(f"ARPPU偏低（{self._format_change(arppu_vs_avg)} vs 历史均值）")
            severity = "关注"
            suggestions.append("ARPPU低于历史均值，建议检查高价位商品/礼包的吸引力，或分析付费深度是否足够")
        elif arppu_vs_avg < 0:
            conclusion_parts.append(f"ARPPU略低（{self._format_change(arppu_vs_avg)} vs 历史均值）")

        if ref_revenue_change < -20:
            severity = "异常"
            conclusion_parts.insert(0, f"营收{ref_label}下降 {abs(ref_revenue_change):.1f}%")
            suggestions.append(f"营收{ref_label}显著下滑，需深入分析原因")
        elif ref_revenue_change < 0:
            if severity == "正常":
                severity = "关注"
            conclusion_parts.insert(0, f"营收{ref_label}下降 {abs(ref_revenue_change):.1f}%")
            suggestions.append(f"营收略有下滑，建议分析具体R级和模块表现")
        elif ref_revenue_change > 20:
            conclusion_parts.insert(0, f"营收{ref_label}大幅增长 {ref_revenue_change:.1f}%")
        elif ref_revenue_change > 0:
            conclusion_parts.insert(0, f"营收{ref_label}增长 {ref_revenue_change:.1f}%")

        conclusion = "，".join(conclusion_parts) if conclusion_parts else "付费数据整体表现平稳"

        # 检查各指标是否有严重下滑（同比）
        check_changes = yoy_changes if yoy_changes else {}
        for key, label in [("pay_rate", "付费率"), ("arpu", "ARPU"), ("arppu", "ARPPU")]:
            val = check_changes.get(key, 0)
            if val < -15:
                details.append(f"同比警告: {label} 下降 {abs(val):.1f}%")

        result.conclusion = conclusion
        result.severity = severity
        result.details = details
        result.suggestions = suggestions
        result.chart_data = {
            "time_series": ts,
            "current": current,
            "yoy_benchmarks": yoy_benchmarks,
            "yoy_benchmark": yoy,  # 向后兼容
            "trend_pattern": trend_pattern,
        }
        result.raw_metrics = {
            "yoy_changes": yoy_changes,
            "all_yoy_changes": all_yoy_changes,
            "vs_avg": {"revenue": rev_vs_avg if other_events else 0, "pay_rate": pr_vs_avg if other_events else 0, "arpu": arpu_vs_avg if other_events else 0, "arppu": arppu_vs_avg if other_events else 0} if other_events else {},
            "trend_pattern": trend_pattern,
            "current_revenue": current.get("revenue", 0),
            "current_arpu": current.get("arpu", 0),
            "current_arppu": current.get("arppu", 0),
            "current_pay_rate": current.get("pay_rate", 0),
        }

        return result

    def _detect_trend_pattern(self, values: list) -> str:
        """
        基于最近数据点判断趋势形态。

        Returns:
            "上升通道" / "V型反转" / "下降通道" / "横盘震荡"
        """
        if len(values) < 3:
            return "数据不足"

        recent = values[-6:] if len(values) >= 6 else values

        # 计算差分
        diffs = [recent[i] - recent[i - 1] for i in range(1, len(recent))]
        positive_count = sum(1 for d in diffs if d > 0)
        negative_count = sum(1 for d in diffs if d < 0)

        # 检查V型: 前半段下降，后半段上升
        mid = len(recent) // 2
        first_half = recent[:mid]
        second_half = recent[mid:]

        if len(first_half) >= 2 and len(second_half) >= 2:
            first_trend = first_half[-1] - first_half[0]
            second_trend = second_half[-1] - second_half[0]

            if first_trend < 0 and second_trend > 0 and abs(second_trend) > abs(first_trend) * 0.5:
                return "V型反转"

        # 变异系数判断震荡
        mean = sum(recent) / len(recent)
        if mean > 0:
            variance = sum((v - mean) ** 2 for v in recent) / len(recent)
            cv = math.sqrt(variance) / mean
            if cv < 0.05:
                return "横盘震荡"

        # 单调性判断
        if positive_count >= len(diffs) * 0.7:
            return "上升通道"
        elif negative_count >= len(diffs) * 0.7:
            return "下降通道"
        else:
            return "横盘震荡"
