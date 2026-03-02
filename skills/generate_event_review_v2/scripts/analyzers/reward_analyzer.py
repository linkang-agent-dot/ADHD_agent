"""
分析器6: 核心奖励分析 - 预期 vs 实际偏差评估。
"""

from .base_analyzer import BaseAnalyzer, AnalysisResult


class RewardAnalyzer(BaseAnalyzer):
    """
    核心奖励分析器。

    分析逻辑：
    1. 对比每个核心奖励的 expected vs actual
    2. 偏差率计算
    3. 判断标准：±10% 符合预期 / ±10%~30% 轻微偏差 / >±30% 显著偏差
    4. 评估成本偏差
    5. 综合判定数值设计
    """

    def analyze(self, data: dict) -> AnalysisResult:
        cr = data.get("core_reward", {})
        items = cr.get("items", [])

        result = AnalysisResult(module_name="数值设计评估")
        details = []
        suggestions = []

        if not items:
            result.conclusion = "无核心奖励数据"
            result.severity = "关注"
            return result

        severity_counts = {"符合预期": 0, "轻微偏差": 0, "显著偏差": 0}
        item_results = []
        # 分类收集，用于精简报告输出
        significant_details = []  # 显著偏差
        minor_details = []        # 轻微偏差
        normal_count = 0          # 符合预期的计数

        for item in items:
            name = item["reward_name"]
            expected = item["expected_value"]
            actual = item["actual_value"]
            unit = item.get("unit", "")

            # 产出偏差
            if expected != 0:
                deviation = self._calc_change_rate(actual, expected)
            else:
                deviation = 0 if actual == 0 else 100

            abs_dev = abs(deviation)
            if abs_dev <= 10:
                level = "符合预期"
            elif abs_dev <= 30:
                level = "轻微偏差"
            else:
                level = "显著偏差"

            severity_counts[level] += 1

            detail = f"{name}: 预期 {expected}{unit} / 实际 {actual}{unit}（偏差 {deviation:+.1f}%，{level}）"

            # 成本偏差
            expected_cost = item.get("expected_cost")
            actual_cost = item.get("actual_cost")
            cost_unit = item.get("cost_unit", "元")
            cost_deviation = None
            if expected_cost and actual_cost:
                cost_deviation = self._calc_change_rate(actual_cost, expected_cost)
                detail += f"，成本偏差 {cost_deviation:+.1f}%"

            # 按偏差级别分类
            if level == "显著偏差":
                significant_details.append(detail)
            elif level == "轻微偏差":
                minor_details.append(detail)
            else:
                normal_count += 1

            item_results.append({
                "name": name,
                "expected": expected,
                "actual": actual,
                "unit": unit,
                "deviation": deviation,
                "level": level,
                "expected_cost": expected_cost,
                "actual_cost": actual_cost,
                "cost_deviation": cost_deviation,
            })

            if level == "显著偏差":
                direction = "高于" if deviation > 0 else "低于"
                suggestions.append(f"{name} 实际产出 {direction} 预期 {abs_dev:.1f}%，建议排查概率/数值配置")

        # 精简 details：只展示偏差项 + 汇总正常项
        MAX_MINOR_SHOW = 10  # 轻微偏差最多展示10条
        for d in significant_details:
            details.append(d)
        if minor_details:
            for d in minor_details[:MAX_MINOR_SHOW]:
                details.append(d)
            if len(minor_details) > MAX_MINOR_SHOW:
                details.append(f"...及其余 {len(minor_details) - MAX_MINOR_SHOW} 项轻微偏差（略）")
        if normal_count > 0:
            details.append(f"另有 {normal_count} 项奖励符合预期（偏差 ≤10%），此处省略")

        # 综合评判
        if severity_counts["显著偏差"] > 0:
            severity = "异常"
            conclusion = f"数值设计存在 {severity_counts['显著偏差']} 项显著偏差，需排查"
        elif severity_counts["轻微偏差"] > len(items) // 2:
            severity = "关注"
            conclusion = "数值设计整体偏差较多，建议复查"
        else:
            severity = "正常"
            conclusion = "数值设计整体符合预期"

        result.conclusion = conclusion
        result.severity = severity
        result.details = details
        result.suggestions = suggestions
        result.chart_data = {
            "items": items,
            "item_results": item_results,
        }
        result.raw_metrics = {
            "item_results": item_results,
            "severity_counts": severity_counts,
        }

        return result
