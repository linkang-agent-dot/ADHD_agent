"""
图表6: 预期 vs 实际偏差对比图（可选，仅 items >= 3 时生成）。
"""

from .base_chart import BaseChart
import matplotlib.pyplot as plt
import numpy as np


class RewardChart(BaseChart):
    """核心奖励偏差图生成器"""

    FILENAME = "6_Reward_Deviation.png"

    def generate(self, chart_data: dict) -> str:
        """
        生成预期vs实际偏差对比图。
        仅在 items >= 3 时生成；否则返回空字符串（用表格嵌入报告）。

        Args:
            chart_data: 来自 RewardAnalyzer 的 chart_data

        Returns:
            图表文件路径，或空字符串
        """
        item_results = chart_data.get("item_results", [])

        if len(item_results) < 3:
            return ""

        fig, ax = self.create_figure(figsize=(12, max(6, len(item_results) * 1.2)))

        names = [r["name"] for r in item_results]
        deviations = [r["deviation"] for r in item_results]

        y = np.arange(len(names))

        # 颜色根据偏差级别
        colors = []
        for r in item_results:
            if r["level"] == "符合预期":
                colors.append(self.COLORS["success"])
            elif r["level"] == "轻微偏差":
                colors.append(self.COLORS["warning"])
            else:
                colors.append(self.COLORS["primary"])

        bars = ax.barh(y, deviations, height=0.5, color=colors, edgecolor="white", zorder=3)

        # 基准线
        ax.axvline(x=0, color=self.COLORS["dark"], linewidth=1, zorder=2)

        # 偏差区间背景
        ax.axvspan(-10, 10, alpha=0.08, color=self.COLORS["success"], zorder=1)
        ax.axvspan(-30, -10, alpha=0.05, color=self.COLORS["warning"], zorder=1)
        ax.axvspan(10, 30, alpha=0.05, color=self.COLORS["warning"], zorder=1)

        # 标注偏差值
        for i, (dev, name) in enumerate(zip(deviations, names)):
            sign = "+" if dev > 0 else ""
            ax.text(dev + (1 if dev >= 0 else -1), i, f"{sign}{dev:.1f}%",
                   va="center", ha="left" if dev >= 0 else "right",
                   fontsize=10, fontweight="bold")

        ax.set_yticks(y)
        ax.set_yticklabels(names, fontsize=10)
        ax.set_xlabel("偏差率(%)", fontsize=11)
        ax.set_title("核心奖励: 预期 vs 实际偏差", fontsize=14, fontweight="bold", pad=15)

        # 图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.COLORS["success"], label="符合预期(±10%)"),
            Patch(facecolor=self.COLORS["warning"], label="轻微偏差(±10%~30%)"),
            Patch(facecolor=self.COLORS["primary"], label="显著偏差(>±30%)"),
        ]
        ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", alpha=0.3)

        self.add_watermark(fig)
        fig.tight_layout()
        return self.save(fig, self.FILENAME)
