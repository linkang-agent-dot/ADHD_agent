"""
图表1: 触达漏斗图 - 水平漏斗图展示各阶段转化率。
"""

from .base_chart import BaseChart
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


class ReachFunnelChart(BaseChart):
    """触达漏斗图生成器"""

    FILENAME = "1_Reach_Funnel.png"

    def generate(self, chart_data: dict) -> str:
        """
        生成触达漏斗图。

        Args:
            chart_data: 来自 ReachAnalyzer 的 chart_data

        Returns:
            图表文件路径
        """
        stages = chart_data.get("stages", [])
        conv_rates = chart_data.get("conv_rates", [])

        # 多对标支持
        comparisons = chart_data.get("comparisons", [])
        if not comparisons:
            single_comp = chart_data.get("comparison", {})
            if single_comp and single_comp.get("stages"):
                comparisons = [single_comp]

        if not stages:
            return ""

        fig, ax = self.create_figure(self.FIGSIZE_TALL)

        n = len(stages)
        max_users = stages[0]["users"]
        bar_height = 0.6
        y_positions = list(range(n - 1, -1, -1))  # 从上到下

        # 渐变色：从深到浅
        colors = plt.cm.Reds(np.linspace(0.8, 0.3, n))

        for i, (stage, y) in enumerate(zip(stages, y_positions)):
            width = stage["users"] / max_users if max_users > 0 else 0
            bar = ax.barh(y, width, height=bar_height, color=colors[i],
                         edgecolor="white", linewidth=1, zorder=3)

            # 标注人数
            label = f'{stage["stage"]}\n{self.format_number(stage["users"])}人'
            ax.text(width + 0.02, y, label, va="center", ha="left", fontsize=10, fontweight="bold")

            # 标注转化率（非首层）
            if i > 0 and i - 1 < len(conv_rates):
                rate = conv_rates[i - 1]["rate"]
                ax.text(width / 2, y + bar_height / 2 + 0.05, f"↓ {rate}%",
                       va="bottom", ha="center", fontsize=9, color="#555555")

        # 多对标虚线（不同颜色）
        comp_line_colors = [self.COLORS["gray"], self.COLORS["secondary"], self.COLORS["info"], self.COLORS["warning"]]
        comp_line_styles = ["--", "-.", ":", "--"]
        for ci, comp in enumerate(comparisons):
            comp_stages = comp.get("stages", [])
            comp_event = comp.get("benchmark_event", comp.get("event", f"对标{ci+1}"))
            line_color = comp_line_colors[ci % len(comp_line_colors)]
            line_style = comp_line_styles[ci % len(comp_line_styles)]

            if comp_stages:
                for i, cs in enumerate(comp_stages):
                    if i < n:
                        comp_width = cs["users"] / max_users if max_users > 0 else 0
                        y = y_positions[i]
                        ax.plot([comp_width, comp_width], [y - bar_height / 2, y + bar_height / 2],
                               color=line_color, linestyle=line_style, linewidth=1.5, alpha=0.7)

                ax.plot([], [], color=line_color, linestyle=line_style, label=f'对标: {comp_event}')

        if comparisons:
            ax.legend(loc="lower right", fontsize=9)

        ax.set_xlim(0, 1.35)
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_title("玩家触达转化漏斗", fontsize=14, fontweight="bold", pad=15)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.xaxis.set_visible(False)

        self.add_watermark(fig)
        fig.tight_layout()
        return self.save(fig, self.FILENAME)
