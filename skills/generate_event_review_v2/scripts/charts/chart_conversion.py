"""
图表5: 付费面积图 - 叠加半透明面积展示当期 vs 对标的付费人数分布。

参考风格：X轴=价位（连续），Y轴=付费人数，
两条平滑曲线填充半透明面积，直观展示付费面积的衰减变化。
"""

from .base_chart import BaseChart
import matplotlib.pyplot as plt
import numpy as np


class ConversionChart(BaseChart):
    """付费面积图生成器"""

    FILENAME = "5_Conversion_Compare.png"

    def generate(self, chart_data: dict) -> str:
        """
        生成付费面积图。

        Args:
            chart_data: 来自 ConversionAnalyzer 的 chart_data

        Returns:
            图表文件路径
        """
        sorted_tiers = chart_data.get("sorted_tiers", [])

        # 多对标支持
        all_comps = chart_data.get("all_comps", [])
        if not all_comps:
            sorted_comp = chart_data.get("sorted_comp", [])
            if sorted_comp:
                all_comps = [{"event": "对标活动", "sorted_tiers": sorted_comp}]

        if not sorted_tiers:
            return ""

        fig, ax = self.create_figure(figsize=(14, 7))

        # === 构建平滑的付费人数分布曲线 ===
        curr_prices, curr_payers = self._aggregate_and_smooth(sorted_tiers)

        # 绘制当期面积
        ax.fill_between(curr_prices, curr_payers, alpha=0.45,
                        color=self.COLORS["primary"], label="当期节日", zorder=3 + len(all_comps))
        ax.plot(curr_prices, curr_payers, color=self.COLORS["primary"],
                linewidth=1.5, alpha=0.8, zorder=4 + len(all_comps))

        # 多对标数据面积
        comp_colors = [self.COLORS["secondary"], self.COLORS["success"], self.COLORS["warning"],
                       self.COLORS["info"], self.COLORS["gray"]]
        all_prices = [t["price"] for t in sorted_tiers]

        for ci, comp_item in enumerate(all_comps):
            comp_tiers = comp_item.get("sorted_tiers", [])
            comp_event = comp_item.get("event", f"对标{ci+1}")
            color = comp_colors[ci % len(comp_colors)]

            if comp_tiers:
                comp_prices, comp_payers = self._aggregate_and_smooth(comp_tiers)
                ax.fill_between(comp_prices, comp_payers, alpha=max(0.2, 0.35 - ci * 0.05),
                                color=color, label=comp_event, zorder=2 + ci)
                ax.plot(comp_prices, comp_payers, color=color,
                        linewidth=1.5, alpha=0.7, zorder=3 + ci)
                all_prices += [t["price"] for t in comp_tiers]

        # === 样式 ===
        ax.set_xlabel("价位（元）", fontsize=12)
        ax.set_ylabel("付费人数", fontsize=12)
        ax.set_title("付费面积图", fontsize=16, fontweight="bold", pad=15)
        ax.legend(loc="upper right", fontsize=12, framealpha=0.9)

        ax.grid(axis="both", alpha=0.2, linestyle="-", color="#ccc")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        x_max = max(all_prices) * 1.05 if all_prices else 100
        ax.set_xlim(0, x_max)
        ax.set_ylim(bottom=0)

        self.add_watermark(fig)
        fig.tight_layout()
        return self.save(fig, self.FILENAME)

    def _aggregate_and_smooth(self, tiers: list, bin_width: float = None) -> tuple:
        """
        将离散价位数据聚合并生成平滑曲线，用于面积图绘制。

        策略：
        1. 先按固定宽度 bin 聚合（避免噪点太多）
        2. 用高斯核平滑使曲线自然

        Returns:
            (prices_array, payers_array) 用于 fill_between
        """
        if not tiers:
            return np.array([0]), np.array([0])

        prices = np.array([t["price"] for t in tiers])
        payers = np.array([t["payers"] for t in tiers])
        max_price = prices.max()

        # 自动确定 bin 宽度：约 30-50 个 bin
        if bin_width is None:
            bin_width = max(max_price / 40, 5)

        # Bin 聚合
        bin_edges = np.arange(0, max_price + bin_width * 2, bin_width)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        bin_values = np.zeros(len(bin_centers))

        for p, n in zip(prices, payers):
            idx = int(p / bin_width)
            if 0 <= idx < len(bin_values):
                bin_values[idx] += n

        # 高斯平滑（sigma = 1.5 个 bin）
        sigma = 1.5
        kernel_size = int(sigma * 4) + 1
        kernel = np.exp(-0.5 * (np.arange(-kernel_size, kernel_size + 1) / sigma) ** 2)
        kernel /= kernel.sum()

        # 边界填充后卷积
        padded = np.pad(bin_values, kernel_size, mode="edge")
        smoothed = np.convolve(padded, kernel, mode="same")[kernel_size:-kernel_size]

        # 确保非负
        smoothed = np.maximum(smoothed, 0)

        # 首尾补零使面积闭合
        x_out = np.concatenate([[0], bin_centers, [bin_centers[-1] + bin_width]])
        y_out = np.concatenate([[0], smoothed, [0]])

        return x_out, y_out
