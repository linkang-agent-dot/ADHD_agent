"""
图表4: R级付费对比图 - 分组柱状图或热力图展示各R级付费数据。
"""

from .base_chart import BaseChart
import matplotlib.pyplot as plt
import numpy as np


class RTierChart(BaseChart):
    """R级付费对比图生成器"""

    FILENAME = "4_RTier_Payment.png"

    def generate(self, chart_data: dict) -> str:
        """
        生成R级付费对比图。
        ≤3个活动：分组柱状图；>3个活动：取最近3个+当期。

        Args:
            chart_data: 来自 RTierAnalyzer 的 chart_data

        Returns:
            图表文件路径
        """
        tiers = chart_data.get("tiers", [])
        ts = chart_data.get("time_series", [])
        benchmarks = chart_data.get("benchmarks", [])

        if not tiers or (not ts and not benchmarks):
            return ""

        # 构建展示数据列表：当期 + 各对标
        # 智能选择：如果有显式 benchmarks，用当期 + benchmarks；否则取最近几个历史活动
        if benchmarks:
            # 当期是 time_series 中用 current_data 匹配的那个
            current_data = chart_data.get("current_data", {})
            # 找到当期事件名
            current_event = None
            for item in ts:
                if item.get("data") == current_data:
                    current_event = item
                    break
            if current_event is None and ts:
                current_event = ts[0]

            display_ts = []
            if current_event:
                display_ts.append(current_event)
            display_ts.extend(benchmarks)
        else:
            display_ts = ts[-3:] if len(ts) > 3 else ts

        events = [item.get("event", "") for item in display_ts]

        fig, axes = self.create_subplots(2, 2, figsize=(14, 10))
        metrics = [
            ("revenue", "付费总额"),
            ("pay_rate", "付费率(%)"),
            ("arpu", "ARPU"),
            ("arppu", "ARPPU"),
        ]

        for idx, (metric_key, metric_label) in enumerate(metrics):
            ax = axes[idx // 2][idx % 2]
            x = np.arange(len(tiers))
            width = 0.8 / max(len(display_ts), 1)

            for ei, ts_item in enumerate(display_ts):
                data = ts_item.get("data", {})
                values = [data.get(t, {}).get(metric_key, 0) for t in tiers]
                offset = (ei - len(display_ts) / 2 + 0.5) * width
                color = self.COLORS["palette"][ei % len(self.COLORS["palette"])]

                bars = ax.bar(x + offset, values, width * 0.9,
                            label=ts_item.get("event", ""), color=color, edgecolor="white", zorder=3)

            ax.set_xticks(x)
            ax.set_xticklabels(tiers, fontsize=9)
            ax.set_title(metric_label, fontsize=11, fontweight="bold")
            ax.legend(fontsize=7, loc="upper right")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="y", alpha=0.3)

        fig.suptitle("R级付费数据对比", fontsize=14, fontweight="bold", y=1.02)
        self.add_watermark(fig)
        fig.tight_layout()
        return self.save(fig, self.FILENAME)
