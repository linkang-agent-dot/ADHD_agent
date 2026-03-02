"""
图表基类 - 统一字体/样式/DPI/配色方案。
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np


class BaseChart:
    """图表基类，统一配置"""

    # 全局配置
    DPI = 150
    FIGSIZE_STANDARD = (12, 7)
    FIGSIZE_WIDE = (14, 7)
    FIGSIZE_TALL = (12, 8)
    FONT_FAMILY = None

    # 配色方案
    COLORS = {
        "primary": "#E74C3C",
        "secondary": "#3498DB",
        "success": "#2ECC71",
        "warning": "#F39C12",
        "info": "#9B59B6",
        "gray": "#95A5A6",
        "light_gray": "#D5DBDB",
        "dark": "#2C3E50",
        "tier_colors": {
            "超R": "#E74C3C",
            "大R": "#F39C12",
            "中R": "#3498DB",
            "小R": "#2ECC71",
            "非R": "#95A5A6",
        },
        "palette": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C", "#E67E22", "#34495E"],
    }

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._detect_chinese_font()

    def _detect_chinese_font(self):
        """检测并设置可用中文字体"""
        candidates = [
            "Microsoft YaHei", "SimHei", "PingFang SC",
            "Hiragino Sans GB", "WenQuanYi Micro Hei", "Noto Sans CJK SC",
        ]
        available_fonts = {f.name for f in fm.fontManager.ttflist}

        for font_name in candidates:
            if font_name in available_fonts:
                self.FONT_FAMILY = font_name
                break

        if self.FONT_FAMILY:
            plt.rcParams["font.sans-serif"] = [self.FONT_FAMILY]
        else:
            plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]

        plt.rcParams["axes.unicode_minus"] = False

    def create_figure(self, figsize=None) -> tuple:
        """创建标准化的 Figure 和 Axes"""
        if figsize is None:
            figsize = self.FIGSIZE_STANDARD
        fig, ax = plt.subplots(figsize=figsize)
        fig.set_facecolor("white")
        return fig, ax

    def create_subplots(self, nrows=1, ncols=1, figsize=None) -> tuple:
        """创建子图"""
        if figsize is None:
            figsize = self.FIGSIZE_WIDE
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        fig.set_facecolor("white")
        return fig, axes

    def save(self, fig, filename: str) -> str:
        """保存图表为 PNG，返回路径"""
        filepath = os.path.join(self.output_dir, filename)
        fig.savefig(filepath, dpi=self.DPI, bbox_inches="tight", facecolor="white", edgecolor="none")
        plt.close(fig)
        return filepath

    def format_number(self, value, is_currency=False) -> str:
        """格式化数字"""
        if is_currency:
            if value >= 10000:
                return f"¥{value/10000:.1f}万"
            return f"¥{value:,.0f}"
        if isinstance(value, float) and value != int(value):
            return f"{value:,.1f}"
        return f"{value:,.0f}"

    def add_watermark(self, fig, text="活动复盘 V2"):
        """添加水印"""
        fig.text(0.98, 0.02, text, fontsize=8, color="#CCCCCC",
                 ha="right", va="bottom", alpha=0.5)
