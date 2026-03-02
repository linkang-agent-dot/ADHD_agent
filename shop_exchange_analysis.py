"""
游戏商店兑换数据分析与可视化
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# 创建输出目录
output_dir = r'c:\ADHD_agent\report_images\shop_exchange'
os.makedirs(output_dir, exist_ok=True)

# 原始数据
data = [
    ["万能英雄碎片-橙色", 72, 1139, 15.82, 9491.67, 600, 150, 10.55],
    ["英雄升星-橙色-大", 28, 216, 7.71, 9257.14, 1200, 50, 15.43],
    ["高级奖池抽奖券", 23, 155, 6.74, 1010.87, 150, 200, 3.37],
    ["军备图纸", 79, 520, 6.58, 987.34, 150, 1000, 0.66],
    ["收藏品-橙色升星道具-传说", 185, 1525, 8.24, 618.24, 75, 200, 4.12],
    ["装备材料-纳米材料", 344, 6624, 19.26, 770.23, 40, 2000, 0.96],
    ["机能核心", 33, 969, 29.36, 2936.36, 100, 500, 5.87],
    ["军备零件箱", 336, 4722, 14.05, 210.80, 15, 5000, 0.28],
    ["2小时加速", 87, 4471, 51.39, 5139.08, 100, 999, 5.14],
    ["60分钟训练加速", 50, 1203, 24.06, 1443.60, 60, 9999, 0.24],
    ["高级资源自选宝箱10w", 48, 2215, 46.15, 2768.75, 60, 9999, 0.46],
    ["万能英雄碎片-橙色②", 424, 6225, 14.68, 8808.96, 600, 150, 9.79],
    ["英雄升星-橙色-大②", 60, 715, 11.92, 14300.00, 1200, 50, 23.83],
    ["装备突破材料-晶体元件", 617, 6222, 10.08, 3025.28, 300, 200, 5.04],
    ["军备图纸②", 171, 409, 2.39, 358.77, 150, 1000, 0.24],
    ["收藏品-红色升星道具-超凡", 1425, 24522, 17.21, 2581.26, 150, 150, 11.47],
    ["装备材料-纳米材料②", 3161, 57131, 18.07, 722.95, 40, 2000, 0.90],
    ["机能核心②", 372, 5039, 13.55, 1354.57, 100, 500, 2.71],
    ["T6军备养成-高分子材料", 427, 3858, 9.04, 4517.56, 500, 50, 18.07],
    ["高级重铸矿晶", 176, 1803, 10.24, 8195.45, 800, 30, 34.15],
    ["2小时加速②", 489, 12391, 25.34, 2533.95, 100, 999, 2.54],
    ["60分钟训练加速②", 489, 17063, 34.89, 2093.62, 60, 9999, 0.35],
    ["高级资源自选宝箱10w②", 292, 34255, 117.31, 7038.70, 60, 9999, 1.17],
    ["主城皮肤-春节初级2024-S3", 2, 2, 1.00, 120000.00, 120000, 1, 100.00],
    ["主城皮肤-登月节初级2024-S3", 1, 1, 1.00, 120000.00, 120000, 1, 100.00],
    ["主城皮肤-沙滩节初级2024-S3", 2, 2, 1.00, 120000.00, 120000, 1, 100.00],
    ["主城皮肤-春节初级2024-S6", 2, 2, 1.00, 120000.00, 120000, 1, 100.00],
    ["主城皮肤-登月节初级2024-S6", 2, 2, 1.00, 120000.00, 120000, 1, 100.00],
    ["主城皮肤-复活节初级2024-S6", 2, 2, 1.00, 120000.00, 120000, 1, 100.00],
    ["返场主城皮肤自选宝箱-S6", 4, 6, 1.50, 180000.00, 120000, 4, 37.50],
    ["主城皮肤-春节初级2024-2-S6", 1, 1, 1.00, 120000.00, 120000, 1, 100.00],
]

columns = ["道具名称", "兑换人次", "兑换次数", "人均兑换次数", "平均消耗代币", "代币价格", "限购数量", "兑换饱和度"]
df = pd.DataFrame(data, columns=columns)

# 添加分类标签
def categorize(name):
    if "皮肤" in name:
        return "主城皮肤"
    elif "英雄" in name or "升星" in name:
        return "英雄养成"
    elif "军备" in name or "T6" in name:
        return "军备养成"
    elif "装备" in name or "纳米" in name or "晶体" in name or "重铸" in name:
        return "装备养成"
    elif "加速" in name:
        return "加速道具"
    elif "收藏品" in name:
        return "收藏品"
    elif "机能核心" in name:
        return "核心材料"
    elif "资源" in name or "奖池" in name:
        return "资源/抽奖"
    else:
        return "其他"

df["类别"] = df["道具名称"].apply(categorize)

# 计算总代币消耗 = 兑换次数 × 代币价格
df["总代币消耗"] = df["兑换次数"] * df["代币价格"]

# 定义颜色方案
category_colors = {
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

# ==================== 图表1: 兑换饱和度分析（排除皮肤） ====================
fig, ax = plt.subplots(figsize=(16, 10))
df_no_skin = df[df["类别"] != "主城皮肤"].sort_values("兑换饱和度", ascending=True)

colors = [category_colors.get(c, "#BDC3C7") for c in df_no_skin["类别"]]
bars = ax.barh(range(len(df_no_skin)), df_no_skin["兑换饱和度"], color=colors, edgecolor='white', linewidth=0.5, height=0.7)

# 添加数值标签
for i, (val, name) in enumerate(zip(df_no_skin["兑换饱和度"], df_no_skin["道具名称"])):
    ax.text(val + 0.3, i, f'{val:.2f}%', va='center', fontsize=9, fontweight='bold')

ax.set_yticks(range(len(df_no_skin)))
ax.set_yticklabels(df_no_skin["道具名称"], fontsize=9)
ax.set_xlabel("兑换饱和度 (%)", fontsize=12)
ax.set_title("商店道具兑换饱和度排名（不含皮肤）", fontsize=16, fontweight='bold', pad=15)

# 添加阈值线
ax.axvline(x=10, color='red', linestyle='--', alpha=0.6, label='高需求线 (10%)')
ax.axvline(x=5, color='orange', linestyle='--', alpha=0.6, label='中需求线 (5%)')
ax.axvline(x=1, color='green', linestyle='--', alpha=0.6, label='低需求线 (1%)')
ax.legend(loc='lower right', fontsize=10)

# 添加图例
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=cat) for cat, color in category_colors.items() if cat != "主城皮肤"]
ax2_legend = ax.legend(handles=legend_elements, loc='lower right', fontsize=8, title='道具类别', 
                       bbox_to_anchor=(1.0, 0.0), ncol=2)
ax.add_artist(ax2_legend)
# 重新添加阈值线图例
threshold_legend = ax.legend(
    [plt.Line2D([0], [0], color='red', linestyle='--', alpha=0.6),
     plt.Line2D([0], [0], color='orange', linestyle='--', alpha=0.6),
     plt.Line2D([0], [0], color='green', linestyle='--', alpha=0.6)],
    ['高需求线 (10%)', '中需求线 (5%)', '低需求线 (1%)'],
    loc='upper right', fontsize=9
)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'chart1_saturation.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图表1 已生成: 兑换饱和度分析")

# ==================== 图表2: 兑换人次 vs 总代币消耗 气泡图 ====================
fig, ax = plt.subplots(figsize=(16, 10))
df_no_skin = df[df["类别"] != "主城皮肤"]

for cat in df_no_skin["类别"].unique():
    subset = df_no_skin[df_no_skin["类别"] == cat]
    sizes = subset["兑换次数"] / 100 + 20  # 气泡大小基于兑换次数
    ax.scatter(subset["兑换人次"], subset["总代币消耗"] / 10000, 
              s=sizes, alpha=0.7, 
              c=category_colors.get(cat, "#BDC3C7"),
              label=cat, edgecolors='grey', linewidth=0.5)

# 标注关键点
for _, row in df_no_skin.iterrows():
    if row["总代币消耗"] / 10000 > 200 or row["兑换人次"] > 1000 or row["兑换饱和度"] > 15:
        ax.annotate(row["道具名称"], (row["兑换人次"], row["总代币消耗"] / 10000),
                   fontsize=7, ha='center', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

ax.set_xlabel("兑换人次", fontsize=12)
ax.set_ylabel("总代币消耗（万）", fontsize=12)
ax.set_title("兑换人次 vs 总代币消耗 气泡图（气泡大小=兑换次数）", fontsize=16, fontweight='bold', pad=15)
ax.legend(fontsize=10, loc='upper left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'chart2_bubble.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图表2 已生成: 兑换人次 vs 总代币消耗气泡图")

# ==================== 图表3: 各类别代币消耗占比 ====================
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# 左: 代币消耗占比
cat_consumption = df.groupby("类别")["总代币消耗"].sum().sort_values(ascending=False)
colors_pie = [category_colors.get(c, "#BDC3C7") for c in cat_consumption.index]
wedges, texts, autotexts = axes[0].pie(cat_consumption, labels=cat_consumption.index, 
                                        autopct='%1.1f%%', colors=colors_pie,
                                        pctdistance=0.8, startangle=90,
                                        textprops={'fontsize': 9})
for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_fontweight('bold')
axes[0].set_title("各类别总代币消耗占比", fontsize=14, fontweight='bold')

# 右: 兑换人次占比
cat_users = df.groupby("类别")["兑换人次"].sum().sort_values(ascending=False)
colors_pie2 = [category_colors.get(c, "#BDC3C7") for c in cat_users.index]
wedges2, texts2, autotexts2 = axes[1].pie(cat_users, labels=cat_users.index, 
                                           autopct='%1.1f%%', colors=colors_pie2,
                                           pctdistance=0.8, startangle=90,
                                           textprops={'fontsize': 9})
for autotext in autotexts2:
    autotext.set_fontsize(9)
    autotext.set_fontweight('bold')
axes[1].set_title("各类别兑换人次占比", fontsize=14, fontweight='bold')

plt.suptitle("商店道具分类消费结构分析", fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'chart3_category_pie.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图表3 已生成: 分类消费结构分析")

# ==================== 图表4: 人均消耗 vs 饱和度 四象限分析 ====================
fig, ax = plt.subplots(figsize=(14, 10))
df_no_skin = df[df["类别"] != "主城皮肤"]

for cat in df_no_skin["类别"].unique():
    subset = df_no_skin[df_no_skin["类别"] == cat]
    sizes = subset["兑换人次"] / 5 + 30
    ax.scatter(subset["平均消耗代币"], subset["兑换饱和度"],
              s=sizes, alpha=0.7,
              c=category_colors.get(cat, "#BDC3C7"),
              label=cat, edgecolors='grey', linewidth=0.5)

# 标注所有点
for _, row in df_no_skin.iterrows():
    ax.annotate(row["道具名称"], (row["平均消耗代币"], row["兑换饱和度"]),
               fontsize=6.5, ha='center', va='bottom',
               bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.6))

# 四象限线
median_cost = df_no_skin["平均消耗代币"].median()
median_sat = df_no_skin["兑换饱和度"].median()
ax.axvline(x=median_cost, color='grey', linestyle='--', alpha=0.5)
ax.axhline(y=median_sat, color='grey', linestyle='--', alpha=0.5)

# 象限标注
ax.text(0.02, 0.98, "低消耗·高饱和\n（高性价比热门）", transform=ax.transAxes,
        fontsize=10, va='top', ha='left', color='green', fontweight='bold', alpha=0.6)
ax.text(0.98, 0.98, "高消耗·高饱和\n（刚需高价值）", transform=ax.transAxes,
        fontsize=10, va='top', ha='right', color='red', fontweight='bold', alpha=0.6)
ax.text(0.02, 0.02, "低消耗·低饱和\n（低关注度）", transform=ax.transAxes,
        fontsize=10, va='bottom', ha='left', color='grey', fontweight='bold', alpha=0.6)
ax.text(0.98, 0.02, "高消耗·低饱和\n（高门槛低转化）", transform=ax.transAxes,
        fontsize=10, va='bottom', ha='right', color='orange', fontweight='bold', alpha=0.6)

ax.set_xlabel("平均消耗代币", fontsize=12)
ax.set_ylabel("兑换饱和度 (%)", fontsize=12)
ax.set_title("人均代币消耗 vs 兑换饱和度 四象限分析（气泡大小=兑换人次）", fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=9, loc='center right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'chart4_quadrant.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图表4 已生成: 四象限分析")

# ==================== 图表5: 皮肤道具专项分析 ====================
fig, ax = plt.subplots(figsize=(14, 6))
df_skin = df[df["类别"] == "主城皮肤"]

bars = ax.bar(range(len(df_skin)), df_skin["兑换人次"], color='#FF6B6B', alpha=0.8, edgecolor='white')

for i, (val, sat) in enumerate(zip(df_skin["兑换人次"], df_skin["兑换饱和度"])):
    ax.text(i, val + 0.1, f'{int(val)}人\n饱和度{sat:.0f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')

ax.set_xticks(range(len(df_skin)))
ax.set_xticklabels(df_skin["道具名称"], rotation=30, ha='right', fontsize=8)
ax.set_ylabel("兑换人次", fontsize=12)
ax.set_title("主城皮肤兑换情况（限购1件 / 单价120,000代币）", fontsize=14, fontweight='bold', pad=15)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'chart5_skin.png'), dpi=150, bbox_inches='tight')
plt.close()
print("✅ 图表5 已生成: 皮肤道具分析")

# ==================== 输出统计摘要 ====================
print("\n" + "="*60)
print("📊 商店兑换数据分析摘要")
print("="*60)

total_token = df["总代币消耗"].sum()
print(f"\n💰 总代币消耗: {total_token:,.0f} ({total_token/10000:,.0f}万)")
print(f"👥 不重复道具数: {len(df)}")

print("\n📈 兑换饱和度 TOP 5（不含皮肤）:")
top5 = df_no_skin.nlargest(5, "兑换饱和度")[["道具名称", "兑换饱和度", "兑换人次", "代币价格"]]
for _, row in top5.iterrows():
    print(f"  • {row['道具名称']}: {row['兑换饱和度']:.2f}% | {int(row['兑换人次'])}人 | 单价{int(row['代币价格'])}")

print("\n📉 兑换饱和度 BOTTOM 5（不含皮肤）:")
bot5 = df_no_skin.nsmallest(5, "兑换饱和度")[["道具名称", "兑换饱和度", "兑换人次", "代币价格"]]
for _, row in bot5.iterrows():
    print(f"  • {row['道具名称']}: {row['兑换饱和度']:.2f}% | {int(row['兑换人次'])}人 | 单价{int(row['代币价格'])}")

print("\n🏆 兑换人次 TOP 5:")
top_users = df.nlargest(5, "兑换人次")[["道具名称", "兑换人次", "兑换次数"]]
for _, row in top_users.iterrows():
    print(f"  • {row['道具名称']}: {int(row['兑换人次'])}人 | {int(row['兑换次数'])}次")

print("\n📦 各类别代币消耗:")
for cat, val in cat_consumption.items():
    pct = val / total_token * 100
    print(f"  • {cat}: {val/10000:,.0f}万 ({pct:.1f}%)")

print(f"\n✅ 所有图表已保存至: {output_dir}")
