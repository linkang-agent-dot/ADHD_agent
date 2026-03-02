"""
分析器1: 触达转化分析 - 漏斗转化率计算与瓶颈检测。
"""

from .base_analyzer import BaseAnalyzer, AnalysisResult
from typing import List


class ReachAnalyzer(BaseAnalyzer):
    """
    触达转化分析器。

    分析逻辑：
    1. 计算各阶段转化率（stage N+1 / stage N）
    2. 如有 comparison，对比各阶段转化率变化
    3. 找到转化率最低的环节（瓶颈点）
    4. 判断是否存在异常流失（某环节转化率 < 30% 或相比对标下降 > 15%）
    """

    def analyze(self, data: dict) -> AnalysisResult:
        rc = data.get("reach_conversion", {})
        stages = rc.get("stages", [])

        # 多对标支持：优先读取 comparisons 数组，兼容单个 comparison
        comparisons = rc.get("comparisons", [])
        if not comparisons:
            single_comp = rc.get("comparison", {})
            if single_comp and single_comp.get("stages"):
                comparisons = [single_comp]

        result = AnalysisResult(module_name="触达分析")
        details = []
        suggestions = []

        # 1. 计算当期各阶段转化率
        conv_rates = []
        for i in range(1, len(stages)):
            prev_users = stages[i - 1]["users"]
            curr_users = stages[i]["users"]
            rate = (curr_users / prev_users * 100) if prev_users > 0 else 0
            conv_rates.append({
                "from": stages[i - 1]["stage"],
                "to": stages[i]["stage"],
                "rate": round(rate, 1),
                "users_from": prev_users,
                "users_to": curr_users,
            })

        # 2. 找到瓶颈点（转化率最低的环节）
        if conv_rates:
            bottleneck = min(conv_rates, key=lambda x: x["rate"])
            details.append(
                f"漏斗瓶颈: {bottleneck['from']} → {bottleneck['to']}，转化率 {bottleneck['rate']}%"
            )

        # 3. 整体转化率（首层到末层）
        if len(stages) >= 2:
            overall_rate = round(stages[-1]["users"] / stages[0]["users"] * 100, 2) if stages[0]["users"] > 0 else 0
            details.append(f"整体转化率（{stages[0]['stage']} → {stages[-1]['stage']}）: {overall_rate}%")

        # 4. 对比分析（支持多对标）
        all_comp_data = []  # 存储所有对标的转化率，供图表使用
        primary_comp_conv_rates = []  # 主对标的转化率，用于异常判断

        for comp_idx, comp in enumerate(comparisons):
            comp_stages = comp.get("stages", [])
            comp_event = comp.get("benchmark_event", f"对标{comp_idx + 1}")
            comp_conv_rates = []

            if comp_stages and len(comp_stages) >= 2:
                for i in range(1, len(comp_stages)):
                    prev_users = comp_stages[i - 1]["users"]
                    curr_users = comp_stages[i]["users"]
                    rate = (curr_users / prev_users * 100) if prev_users > 0 else 0
                    comp_conv_rates.append(round(rate, 1))

                all_comp_data.append({
                    "event": comp_event,
                    "stages": comp_stages,
                    "conv_rates": comp_conv_rates,
                })

                if comp_idx == 0:
                    primary_comp_conv_rates = comp_conv_rates

                # 输出对比详情
                for i, cr in enumerate(conv_rates):
                    if i < len(comp_conv_rates):
                        change = round(cr["rate"] - comp_conv_rates[i], 1)
                        direction = "提升" if change > 0 else "下降"
                        details.append(
                            f"{cr['from']}→{cr['to']}: 当期 {cr['rate']}% vs {comp_event} {comp_conv_rates[i]}%（{direction} {abs(change)}pp）"
                        )

        # 5. 异常判断
        severity = "正常"
        has_critical = False
        for cr in conv_rates:
            is_pay_stage = "付费" in cr["to"]
            threshold = 5 if is_pay_stage else 30
            if cr["rate"] < threshold:
                severity = "异常"
                has_critical = True
                suggestions.append(f"{cr['from']}→{cr['to']} 转化率仅 {cr['rate']}%，建议检查该环节用户流失原因")

        # 对比下降超过15%（以主对标为基准判断）
        for i, cr in enumerate(conv_rates):
            if i < len(primary_comp_conv_rates):
                drop = primary_comp_conv_rates[i] - cr["rate"]
                if drop > 15:
                    severity = "严重" if severity != "严重" else severity
                    has_critical = True
                    suggestions.append(
                        f"{cr['from']}→{cr['to']} 相比主对标下降 {drop:.1f}pp，需重点排查"
                    )

        if not has_critical:
            result.conclusion = "触达通路正常，各环节转化率在合理范围内"
        else:
            bottleneck_name = bottleneck["from"] + "→" + bottleneck["to"] if conv_rates else "未知"
            result.conclusion = f"触达存在问题，{bottleneck_name} 环节存在显著流失"

        result.severity = severity
        result.details = details
        result.suggestions = suggestions
        result.chart_data = {
            "stages": stages,
            "conv_rates": conv_rates,
            "comparisons": all_comp_data,
            "comparison": comparisons[0] if comparisons else {},  # 向后兼容
            "comp_conv_rates": primary_comp_conv_rates,
        }
        result.raw_metrics = {
            "conv_rates": conv_rates,
            "overall_rate": overall_rate if len(stages) >= 2 else 0,
        }

        return result
