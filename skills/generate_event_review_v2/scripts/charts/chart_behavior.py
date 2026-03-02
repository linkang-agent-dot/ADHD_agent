"""
图表2: 行为数据图 - 分组柱状图展示当期 vs 对标指标对比。
"""

from .base_chart import BaseChart
import matplotlib.pyplot as plt
import numpy as np


class BehaviorChart(BaseChart):
    """行为数据对比图生成器"""

    FILENAME = "2_Behavior_Data.png"

    def generate(self, chart_data: dict) -> str:
        """
        生成行为数据对比柱状图。

        Args:
            chart_data: 来自 BehaviorAnalyzer 的 chart_data

        Returns:
            图表文件路径
        """
        metrics = chart_data.get("metrics", [])
        metric_changes = chart_data.get("metric_changes", [])

        if not metrics:
            return ""

        fig, ax = self.create_figure()

        names = [m["metric_name"] for m in metrics]
        current_values = [m["current_value"] for m in metrics]
        benchmark_values = [m.get("benchmark_value", 0) for m in metrics]
        has_benchmark = any(v > 0 for v in benchmark_values)

        x = np.arange(len(names))
        width = 0.35 if has_benchmark else 0.5

        # 当期柱子
        bars1 = ax.bar(x - (width / 2 if has_benchmark else 0), current_values, width,
                       label="当期", color=self.COLORS["primary"], edgecolor="white", zorder=3)

        # 对标柱子
        if has_benchmark:
            bars2 = ax.bar(x + width / 2, benchmark_values, width,
                          label="对标", color=self.COLORS["gray"], edgecolor="white", zorder=3)

        # 变化率标注
        for i, mc in enumerate(metric_changes):
            change = mc.get("change")
            if change is None:
                continue
            color = self.COLORS["success"] if change > 0 else self.COLORS["primary"]
            sign = "+" if change > 0 else ""
            y_pos = max(current_values[i], benchmark_values[i] if has_benchmark else 0) * 1.05
            ax.text(x[i], y_pos, f"{sign}{change:.1f}%", ha="center", va="bottom",
                   fontsize=9, fontweight="bold", color=color)

        # 柱子顶部标注数值
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                   self.format_number(height), ha="center", va="bottom", fontsize=8)

        ax.set_xticks(x)
        ax.set_xticklabels(names, fontsize=10)
        ax.set_title("行为数据对比", fontsize=14, fontweight="bold", pad=15)
        ax.legend(loc="upper right", fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", alpha=0.3)

        self.add_watermark(fig)
        fig.tight_layout()
        return self.save(fig, self.FILENAME)
