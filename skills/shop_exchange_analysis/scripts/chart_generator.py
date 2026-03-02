"""
兑换商店图表生成器
生成 5 张分析图表：饱和度 / 气泡图 / 饼图 / 四象限 / 高价道具
"""

import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

# 中文字体配置
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# 统一配色方案
CATEGORY_COLORS = {
    "主城皮肤": "#FF6B6B",
    "英雄养成": "#4ECDC4",
    "军备养成": "#45B7D1",
    "装备养成": "#96CEB4",
    "加速道具": "#FFEAA7",
    "收藏品": "#DDA0DD",
    "核心材料": "#98D8C8",
    "资源/抽奖": "#F7DC6F",
    "其他": "#BDC3C7",
}


class ShopChartGenerator:
    """兑换商店图表生成器"""

    def __init__(self, items: list[dict], analysis_results: dict, output_dir: str):
        self.items = items
        self.results = analysis_results
        self.output_dir = output_dir
        self.normal_items = [i for i in items if i.get("token_price", 0) < 50000]
        self.special_items = [i for i in items if i.get("token_price", 0) >= 50000]
        os.makedirs(output_dir, exist_ok=True)

    def _get_color(self, category: str) -> str:
        return CATEGORY_COLORS.get(category, "#BDC3C7")

    def generate_all(self) -> list[str]:
        """生成全部图表，返回文件路径列表"""
        charts = []
        charts.append(self.chart_saturation())
        charts.append(self.chart_bubble())
        charts.append(self.chart_category_pie())
        charts.append(self.chart_quadrant())
        if self.special_items:
            charts.append(self.chart_special())
        return [c for c in charts if c]

    # ============================================================
    # 图表1: 兑换饱和度排名（水平条形图）
    # ============================================================
    def chart_saturation(self) -> str:
        items = sorted(self.normal_items, key=lambda x: x.get("saturation_rate", 0))
        if not items:
            return ""

        fig, ax = plt.subplots(figsize=(16, max(8, len(items) * 0.45)))
        colors = [self._get_color(i.get("category", "")) for i in items]
        sats = [i.get("saturation_rate", 0) for i in items]
        names = [i.get("item_name", "") for i in items]

        bars = ax.barh(range(len(items)), sats, color=colors, edgecolor='white',
                       linewidth=0.5, height=0.7)

        # 数值标签
        for idx, val in enumerate(sats):
            ax.text(val + 0.3, idx, f'{val:.2f}%', va='center', fontsize=9, fontweight='bold')

        ax.set_yticks(range(len(items)))
        ax.set_yticklabels(names, fontsize=9)
        ax.set_xlabel("兑换饱和度 (%)", fontsize=12)
        ax.set_title("商店道具兑换饱和度排名", fontsize=16, fontweight='bold', pad=15)

        # 阈值线
        thresholds = self.results.get("saturation", {})
        h_t = thresholds.get("high_threshold", 10)
        m_t = thresholds.get("med_threshold", 5)
        l_t = thresholds.get("low_threshold", 1)

        ax.axvline(x=h_t, color='red', linestyle='--', alpha=0.6)
        ax.axvline(x=m_t, color='orange', linestyle='--', alpha=0.6)
        ax.axvline(x=l_t, color='green', linestyle='--', alpha=0.6)

        # 图例
        cat_in_data = list(set(i.get("category", "") for i in items))
        legend_elements = [Patch(facecolor=self._get_color(c), label=c) for c in cat_in_data if c]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=8, title='道具类别', ncol=2)

        threshold_legend = ax.legend(
            [plt.Line2D([0], [0], color='red', linestyle='--', alpha=0.6),
             plt.Line2D([0], [0], color='orange', linestyle='--', alpha=0.6),
             plt.Line2D([0], [0], color='green', linestyle='--', alpha=0.6)],
            [f'高需求线 ({h_t}%)', f'中需求线 ({m_t}%)', f'低需求线 ({l_t}%)'],
            loc='upper right', fontsize=9
        )

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        path = os.path.join(self.output_dir, 'chart1_saturation.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        return path

    # ============================================================
    # 图表2: 兑换人次 vs 总代币消耗 气泡图
    # ============================================================
    def chart_bubble(self) -> str:
        items = self.normal_items
        if not items:
            return ""

        fig, ax = plt.subplots(figsize=(16, 10))

        for cat in set(i.get("category", "") for i in items):
            subset = [i for i in items if i.get("category", "") == cat]
            users = [i.get("exchange_users", 0) for i in subset]
            tokens = [i.get("total_token_consumption", 0) / 10000 for i in subset]
            sizes = [i.get("exchange_count", 0) / 100 + 20 for i in subset]

            ax.scatter(users, tokens, s=sizes, alpha=0.7,
                      c=self._get_color(cat), label=cat,
                      edgecolors='grey', linewidth=0.5)

        # 标注关键点
        for item in items:
            tc = item.get("total_token_consumption", 0) / 10000
            eu = item.get("exchange_users", 0)
            if tc > 200 or eu > 1000 or item.get("saturation_rate", 0) > 15:
                ax.annotate(item["item_name"], (eu, tc),
                           fontsize=7, ha='center', va='bottom',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

        ax.set_xlabel("兑换人次", fontsize=12)
        ax.set_ylabel("总代币消耗（万）", fontsize=12)
        ax.set_title("兑换人次 vs 总代币消耗（气泡大小=兑换次数）", fontsize=16, fontweight='bold', pad=15)
        ax.legend(fontsize=10, loc='upper left')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # 使用对数轴（如数据跨度大）
        users_all = [i.get("exchange_users", 1) for i in items]
        if max(users_all) / max(min(users_all), 1) > 50:
            ax.set_xscale('log')
            ax.set_yscale('log')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, 'chart2_bubble.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        return path

    # ============================================================
    # 图表3: 分类消费结构（双饼图）
    # ============================================================
    def chart_category_pie(self) -> str:
        cs = self.results.get("consumption_structure", {})
        categories = cs.get("categories", [])
        if not categories:
            return ""

        fig, axes = plt.subplots(1, 2, figsize=(16, 8))

        # 左: 代币消耗占比
        labels = [c["category"] for c in categories]
        token_vals = [c["total_token"] for c in categories]
        colors = [self._get_color(c["category"]) for c in categories]

        wedges, texts, autotexts = axes[0].pie(
            token_vals, labels=labels, autopct='%1.1f%%', colors=colors,
            pctdistance=0.8, startangle=90, textprops={'fontsize': 9}
        )
        for at in autotexts:
            at.set_fontsize(9)
            at.set_fontweight('bold')
        axes[0].set_title("各类别总代币消耗占比", fontsize=14, fontweight='bold')

        # 右: 兑换人次占比
        users_vals = [c["total_users"] for c in categories]
        wedges2, texts2, autotexts2 = axes[1].pie(
            users_vals, labels=labels, autopct='%1.1f%%', colors=colors,
            pctdistance=0.8, startangle=90, textprops={'fontsize': 9}
        )
        for at in autotexts2:
            at.set_fontsize(9)
            at.set_fontweight('bold')
        axes[1].set_title("各类别兑换人次占比", fontsize=14, fontweight='bold')

        plt.suptitle("商店道具分类消费结构分析", fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        path = os.path.join(self.output_dir, 'chart3_category_pie.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        return path

    # ============================================================
    # 图表4: 四象限定位（人均消耗 × 饱和度）
    # ============================================================
    def chart_quadrant(self) -> str:
        items = self.normal_items
        if not items:
            return ""

        fig, ax = plt.subplots(figsize=(14, 10))

        for cat in set(i.get("category", "") for i in items):
            subset = [i for i in items if i.get("category", "") == cat]
            costs = [i.get("avg_token_cost", 0) for i in subset]
            sats = [i.get("saturation_rate", 0) for i in subset]
            sizes = [i.get("exchange_users", 0) / 5 + 30 for i in subset]

            ax.scatter(costs, sats, s=sizes, alpha=0.7,
                      c=self._get_color(cat), label=cat,
                      edgecolors='grey', linewidth=0.5)

        # 标注所有点
        for item in items:
            ax.annotate(item["item_name"],
                       (item.get("avg_token_cost", 0), item.get("saturation_rate", 0)),
                       fontsize=6.5, ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.6))

        # 四象限分割线
        q_data = self.results.get("quadrant", {})
        median_cost = q_data.get("median_cost", 0)
        median_sat = q_data.get("median_saturation", 0)
        ax.axvline(x=median_cost, color='grey', linestyle='--', alpha=0.5)
        ax.axhline(y=median_sat, color='grey', linestyle='--', alpha=0.5)

        # 象限标注
        ax.text(0.02, 0.98, "低消耗 · 高饱和\n（高性价比热门）", transform=ax.transAxes,
                fontsize=10, va='top', ha='left', color='green', fontweight='bold', alpha=0.6)
        ax.text(0.98, 0.98, "高消耗 · 高饱和\n（刚需高价值）", transform=ax.transAxes,
                fontsize=10, va='top', ha='right', color='red', fontweight='bold', alpha=0.6)
        ax.text(0.02, 0.02, "低消耗 · 低饱和\n（低关注度）", transform=ax.transAxes,
                fontsize=10, va='bottom', ha='left', color='grey', fontweight='bold', alpha=0.6)
        ax.text(0.98, 0.02, "高消耗 · 低饱和\n（高门槛低转化）", transform=ax.transAxes,
                fontsize=10, va='bottom', ha='right', color='orange', fontweight='bold', alpha=0.6)

        ax.set_xlabel("平均消耗代币", fontsize=12)
        ax.set_ylabel("兑换饱和度 (%)", fontsize=12)
        ax.set_title("人均代币消耗 vs 兑换饱和度 四象限分析（气泡大小=兑换人次）",
                     fontsize=14, fontweight='bold', pad=15)
        ax.legend(fontsize=9, loc='center right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.2)

        plt.tight_layout()
        path = os.path.join(self.output_dir, 'chart4_quadrant.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        return path

    # ============================================================
    # 图表5: 高价道具/皮肤专项
    # ============================================================
    def chart_special(self) -> str:
        items = self.special_items
        if not items:
            return ""

        fig, ax = plt.subplots(figsize=(14, max(5, len(items) * 0.5 + 2)))
        names = [i.get("item_name", "") for i in items]
        users = [i.get("exchange_users", 0) for i in items]

        bars = ax.bar(range(len(items)), users, color='#FF6B6B', alpha=0.8, edgecolor='white')

        for idx, (u, item) in enumerate(zip(users, items)):
            sat = item.get("saturation_rate", 0)
            ax.text(idx, u + 0.1, f'{int(u)}人\n饱和度{sat:.0f}%',
                   ha='center', va='bottom', fontsize=8, fontweight='bold')

        ax.set_xticks(range(len(items)))
        ax.set_xticklabels(names, rotation=30, ha='right', fontsize=8)
        ax.set_ylabel("兑换人次", fontsize=12)

        price = items[0].get("token_price", 0)
        ax.set_title(f"高价道具兑换情况（单价 {price:,} 代币）",
                     fontsize=14, fontweight='bold', pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        path = os.path.join(self.output_dir, 'chart5_special.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        return path
