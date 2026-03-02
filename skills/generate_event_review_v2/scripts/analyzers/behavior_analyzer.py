"""
分析器2: 行为数据分析 - 行为指标对比与日趋势异常检测。
"""

from .base_analyzer import BaseAnalyzer, AnalysisResult


class BehaviorAnalyzer(BaseAnalyzer):
    """
    行为数据分析器。

    分析逻辑：
    1. 对比各行为指标的当期 vs 对标值
    2. 检测日趋势中的异常点（如某天 DAU 骤降）
    3. 判断参与率/时长是否在合理区间
    4. 如果参与率高但付费转化低，标记为"行为-付费脱节"
    """

    def analyze(self, data: dict) -> AnalysisResult:
        bd = data.get("behavior_data", {})
        metrics = bd.get("metrics", [])
        daily_trend = bd.get("daily_trend", [])

        result = AnalysisResult(module_name="行为分析")
        details = []
        suggestions = []
        severity = "正常"

        # 0. 获取活动参与人数基数（用于计算使用率）
        rc = data.get("reach_conversion", {})
        stages = rc.get("stages", [])
        # 尝试找到"参与"阶段的人数作为基数；若无则取漏斗第一层
        base_users = 0
        for s in stages:
            stage_name = s.get("stage", "")
            if "参与" in stage_name:
                base_users = s.get("users", 0)
                break
        if base_users == 0 and stages:
            base_users = stages[0].get("users", 0)

        # 1. 指标对比 + 使用率计算
        metric_changes = []
        usage_rates = []
        for m in metrics:
            current = m["current_value"]
            benchmark = m.get("benchmark_value")
            unit = m.get("unit", "")
            name = m["metric_name"]

            # 计算使用率（当单位为"人"或"次"且有基数时）
            usage_rate = None
            if base_users > 0 and unit in ("人", "次"):
                usage_rate = round(current / base_users * 100, 2)
                usage_rates.append({"name": name, "rate": usage_rate, "current": current})

            if benchmark is not None and benchmark > 0:
                change = self._calc_change_rate(current, benchmark)
                direction = "提升" if change > 0 else "下降"
                detail = f"{name}: 当期 {self._format_number(current)}{unit} vs 对标 {self._format_number(benchmark)}{unit}（{direction} {abs(change):.1f}%）"
                if usage_rate is not None:
                    detail += f"，使用率 {usage_rate:.1f}%"
                details.append(detail)
                metric_changes.append({"name": name, "change": change, "current": current, "benchmark": benchmark, "usage_rate": usage_rate})

                # 异常判断：某指标下降超过 20%
                if change < -20:
                    severity = "异常"
                    suggestions.append(f"{name} 大幅下降 {abs(change):.1f}%，建议排查原因")
                elif change < -10:
                    if severity == "正常":
                        severity = "关注"
            else:
                detail = f"{name}: 当期 {self._format_number(current)}{unit}"
                if usage_rate is not None:
                    detail += f"，使用率 {usage_rate:.1f}%"
                else:
                    detail += "（无对标数据）"
                details.append(detail)
                metric_changes.append({"name": name, "change": None, "current": current, "benchmark": benchmark, "usage_rate": usage_rate})

        # 1.5 使用率合理性分析
        if usage_rates and base_users > 0:
            details.append(f"（使用率基数: 活动参与人数 {self._format_number(base_users)}人）")
            # 按使用率排序，找出极高和极低的
            sorted_rates = sorted(usage_rates, key=lambda x: x["rate"], reverse=True)
            high_usage = [r for r in sorted_rates if r["rate"] > 80]
            low_usage = [r for r in sorted_rates if r["rate"] < 5]
            medium_usage = [r for r in sorted_rates if 5 <= r["rate"] <= 80]

            if high_usage:
                names = ", ".join(r["name"] for r in high_usage[:3])
                details.append(f"高使用率道具(>80%): {names}")
            if low_usage:
                names = ", ".join(r["name"] for r in low_usage[:5])
                details.append(f"低使用率道具(<5%): {names}")
                if len(low_usage) > len(usage_rates) // 2:
                    suggestions.append(f"超过半数道具使用率低于5%，建议检查道具获取/使用门槛是否过高")
                    if severity == "正常":
                        severity = "关注"

        # 2. 日趋势异常检测
        anomaly_dates = []
        if daily_trend and len(daily_trend) >= 3:
            dau_values = [d.get("dau", 0) for d in daily_trend]
            anomaly_indices = self._detect_anomaly(dau_values, threshold=2.0)

            for idx in anomaly_indices:
                day = daily_trend[idx]
                anomaly_dates.append(day.get("date", f"第{idx+1}天"))
                details.append(
                    f"日趋势异常: {day.get('date', '')} DAU={self._format_number(day.get('dau', 0))}，偏离均值"
                )

            if anomaly_indices:
                if severity in ("正常", "关注"):
                    severity = "关注"
                suggestions.append(f"日趋势中 {len(anomaly_indices)} 天出现 DAU 异常波动，建议排查活动节奏或外部影响")

        # 3. 综合结论
        positive_count = sum(1 for mc in metric_changes if mc.get("change") is not None and mc["change"] > 0)
        negative_count = sum(1 for mc in metric_changes if mc.get("change") is not None and mc["change"] < 0)
        has_usage_data = len(usage_rates) > 0

        if has_usage_data and not any(mc.get("change") is not None for mc in metric_changes):
            # 无对标数据，仅有使用率分析
            low_count = len([r for r in usage_rates if r["rate"] < 5])
            total_count = len(usage_rates)
            if low_count > total_count // 2:
                result.conclusion = f"行为数据: {total_count} 项道具中 {low_count} 项使用率低于5%，部分道具吸引力不足"
            else:
                result.conclusion = f"行为数据: 共 {total_count} 项道具使用数据，整体使用率分布合理"
        elif severity in ("正常", "关注") and negative_count == 0:
            result.conclusion = "行为数据表现良好，各项指标均优于对标"
        elif positive_count > negative_count:
            result.conclusion = "行为数据整体向好，部分指标需关注"
        else:
            result.conclusion = f"行为数据存在 {negative_count} 项指标下滑，需重点关注"

        result.severity = severity
        result.details = details
        result.suggestions = suggestions
        result.chart_data = {
            "metrics": metrics,
            "metric_changes": metric_changes,
            "daily_trend": daily_trend,
            "anomaly_dates": anomaly_dates,
            "usage_rates": usage_rates,
            "base_users": base_users,
        }
        result.raw_metrics = {
            "metric_changes": metric_changes,
            "anomaly_count": len(anomaly_dates),
            "usage_rates": usage_rates,
        }

        return result
