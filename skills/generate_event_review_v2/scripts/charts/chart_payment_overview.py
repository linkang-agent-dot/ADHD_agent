"""
图表3: 付费整体趋势图 - 多Y轴折线图展示营收/ARPU/付费率趋势。
"""

from .base_chart import BaseChart
import matplotlib.pyplot as plt
import numpy as np


class PaymentOverviewChart(BaseChart):
    """付费整体趋势图生成器"""

    FILENAME = "3_Payment_Overview.png"

    def generate(self, chart_data: dict) -> str:
        """
        生成付费整体趋势图。

        Args:
            chart_data: 来自 PaymentOverviewAnalyzer 的 chart_data

        Returns:
            图表文件路径
        """
        ts = chart_data.get("time_series", [])
        yoy = chart_data.get("yoy_benchmark", {})
        trend_pattern = chart_data.get("trend_pattern", "")

        if not ts:
            return ""

        fig, ax1 = plt.subplots(figsize=self.FIGSIZE_WIDE)
        fig.set_facecolor("white")

        events = [item["event"] for item in ts]
        revenues = [item["revenue"] for item in ts]
        arpus = [item["arpu"] for item in ts]
        pay_rates = [item["pay_rate"] for item in ts]
        x = np.arange(len(events))

        # 主Y轴：营收柱状图 + 折线
        color_rev = self.COLORS["primary"]
        bars = ax1.bar(x, revenues, 0.5, alpha=0.3, color=color_rev, edgecolor=color_rev, linewidth=0.5, zorder=2)
        line1 = ax1.plot(x, revenues, "o-", color=color_rev, linewidth=2, markersize=6, label="营收", zorder=3)

        # 当期标记★
        ax1.plot(x[-1], revenues[-1], marker="*", markersize=15, color=color_rev, zorder=4)

        ax1.set_ylabel("付费总额", color=color_rev, fontsize=11)
        ax1.tick_params(axis="y", labelcolor=color_rev)

        # 副Y轴：ARPU
        ax2 = ax1.twinx()
        color_arpu = self.COLORS["secondary"]
        line2 = ax2.plot(x, arpus, "s-", color=color_arpu, linewidth=2, markersize=5, label="ARPU", zorder=3)
        ax2.set_ylabel("ARPU", color=color_arpu, fontsize=11)
        ax2.tick_params(axis="y", labelcolor=color_arpu)

        # 第二副Y轴：付费率（虚线）
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("outward", 60))
        color_rate = self.COLORS["success"]
        line3 = ax3.plot(x, pay_rates, "^--", color=color_rate, linewidth=1.5, markersize=5, label="付费率", zorder=3)
        ax3.set_ylabel("付费率(%)", color=color_rate, fontsize=11)
        ax3.tick_params(axis="y", labelcolor=color_rate)

        # 同比参考线（多对标支持）
        yoy_benchmarks = chart_data.get("yoy_benchmarks", [])
        if not yoy_benchmarks and yoy and yoy.get("revenue"):
            yoy_benchmarks = [yoy]

        bench_line_colors = [self.COLORS["gray"], self.COLORS["info"], self.COLORS["warning"]]
        bench_line_styles = [":", "-.", "--"]
        for bi, bench in enumerate(yoy_benchmarks):
            if bench.get("revenue"):
                lc = bench_line_colors[bi % len(bench_line_colors)]
                ls = bench_line_styles[bi % len(bench_line_styles)]
                ax1.axhline(y=bench["revenue"], color=lc, linestyle=ls, linewidth=1, alpha=0.7)
                ax1.text(len(events) - 0.5, bench["revenue"],
                        f'{bench.get("event", f"对标{bi+1}")}: {self.format_number(bench["revenue"], True)}',
                        fontsize=8, color=lc, va="bottom")

        # 当期数据标注
        ax1.annotate(
            self.format_number(revenues[-1], True),
            xy=(x[-1], revenues[-1]),
            xytext=(0, 15), textcoords="offset points",
            fontsize=10, fontweight="bold", color=color_rev,
            ha="center",
        )

        # 设置 X 轴
        ax1.set_xticks(x)
        ax1.set_xticklabels(events, rotation=30, ha="right", fontsize=9)

        # 图例
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc="upper left", fontsize=9)

        # 标题
        title = f"付费整体趋势（{trend_pattern}）" if trend_pattern else "付费整体趋势"
        ax1.set_title(title, fontsize=14, fontweight="bold", pad=15)

        ax1.spines["top"].set_visible(False)
        ax1.grid(axis="y", alpha=0.2)

        self.add_watermark(fig)
        fig.tight_layout()
        return self.save(fig, self.FILENAME)
