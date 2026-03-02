"""
图表7: 礼包付费对比图 - 气泡图/双维柱状图展示礼包表现。
"""

from .base_chart import BaseChart
import matplotlib.pyplot as plt
import numpy as np


class PackageChart(BaseChart):
    """礼包付费对比图生成器"""

    FILENAME = "7_Package_Compare.png"

    def generate(self, chart_data: dict) -> str:
        """
        生成礼包付费对比图（双维柱状图方案）。

        Args:
            chart_data: 来自 PackageAnalyzer 的 chart_data

        Returns:
            图表文件路径
        """
        pkg_stats = chart_data.get("pkg_stats", [])
        comp_packages = chart_data.get("comp_packages", [])

        if not pkg_stats:
            return ""

        fig, ax1 = plt.subplots(figsize=self.FIGSIZE_WIDE)
        fig.set_facecolor("white")

        # 按营收降序（pkg_stats 已经排好序）
        names = [p["name"] for p in pkg_stats]
        revenues = [p["revenue"] for p in pkg_stats]
        payers = [p["payers"] for p in pkg_stats]
        prices = [p["price"] for p in pkg_stats]

        x = np.arange(len(names))
        width = 0.4

        # 营收柱状图
        bars = ax1.bar(x, revenues, width, color=self.COLORS["primary"],
                      edgecolor="white", label="营收", zorder=3)

        # 营收数值标注
        for bar, rev, price in zip(bars, revenues, prices):
            ax1.text(bar.get_x() + bar.get_width() / 2., bar.get_height(),
                    f'{self.format_number(rev, True)}\n(¥{price})',
                    ha="center", va="bottom", fontsize=8)

        ax1.set_ylabel("付费总额", color=self.COLORS["primary"], fontsize=11)
        ax1.tick_params(axis="y", labelcolor=self.COLORS["primary"])

        # 人数折线（右Y轴）
        ax2 = ax1.twinx()
        ax2.plot(x, payers, "o-", color=self.COLORS["secondary"],
                linewidth=2, markersize=8, label="付费人数", zorder=4)

        for xi, p in zip(x, payers):
            ax2.text(xi, p * 1.02, self.format_number(p),
                    ha="center", va="bottom", fontsize=8, color=self.COLORS["secondary"])

        ax2.set_ylabel("付费人数", color=self.COLORS["secondary"], fontsize=11)
        ax2.tick_params(axis="y", labelcolor=self.COLORS["secondary"])

        # 对标数据叠加（多对标支持）
        comparisons = chart_data.get("comparisons", [])
        if not comparisons:
            comp_packages = chart_data.get("comp_packages", [])
            if comp_packages:
                comparisons = [{"event": "对标", "packages": comp_packages}]

        comp_bar_colors = [self.COLORS["gray"], self.COLORS["info"], self.COLORS["warning"], self.COLORS["success"]]
        for ci, comp_item in enumerate(comparisons):
            comp_pkgs = comp_item.get("packages", [])
            comp_event = comp_item.get("event", f"对标{ci+1}")
            color = comp_bar_colors[ci % len(comp_bar_colors)]

            if comp_pkgs:
                comp_map = {p["price"]: p for p in comp_pkgs}
                comp_revs = []
                has_comp_data = False
                for pkg in pkg_stats:
                    comp = comp_map.get(pkg["price"])
                    if comp:
                        comp_revs.append(comp["revenue"])
                        has_comp_data = True
                    else:
                        comp_revs.append(0)

                if has_comp_data:
                    bar_offset = width * (1 + ci)
                    ax1.bar(x + bar_offset, comp_revs, width * 0.8, color=color,
                           edgecolor="white", alpha=0.6, label=f"{comp_event} 营收", zorder=2)

        # 设置 X 轴
        ax1.set_xticks(x)
        ax1.set_xticklabels(names, rotation=25, ha="right", fontsize=9)
        ax1.set_title("商业化礼包付费表现", fontsize=14, fontweight="bold", pad=15)

        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)

        ax1.spines["top"].set_visible(False)
        ax1.grid(axis="y", alpha=0.3)

        self.add_watermark(fig)
        fig.tight_layout()
        return self.save(fig, self.FILENAME)
