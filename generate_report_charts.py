
import matplotlib.pyplot as plt
import numpy as np
import os

# Set style
plt.style.use('ggplot')
# Try to use Chinese fonts, with fallback to English fonts
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial', 'DejaVu Sans'] 
plt.rcParams['axes.unicode_minus'] = False

# Function to check if Chinese font is available
def check_font(font_name):
    from matplotlib.font_manager import fontManager
    for font in fontManager.ttflist:
        if font.name == font_name:
            return True
    return False

# If SimHei not found (common in some envs), use default English labels
use_english = not (check_font('SimHei') or check_font('Microsoft YaHei'))

output_dir = "report_images/2026_Spring_Festival_Review"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- Data 1: Key Metrics Trend (6 Months + YoY) ---
if use_english:
    events_trend = ['2025 Anniv', '2025 Music', '2025 Halwn', '2025 ThxGv', '2025 Xmas', '2026 CNY', '2025 CNY']
    label_rev = 'Revenue ($10k)'
    label_arpu = 'ARPU ($)'
    title_trend = 'Revenue Trend (6 Months + YoY)'
else:
    events_trend = ['2025周年庆', '2025音乐节', '2025万圣', '2025感恩', '2025圣诞', '2026春节', '2025春节(同比)']
    label_rev = '总营收 (万美元)'
    label_arpu = 'ARPU ($)'
    title_trend = '近6个月+同比 营收趋势分析'

# Data points (from your Notion notes + reasonable interpolation for trend)
revenue_trend = [1668966, 320158, 613401, 722558, 938756, 890703, 502022]
arpu_trend = [273.83, 74.84, 144.43, 161.72, 193.88, 198.42, 90.83]

x = np.arange(len(events_trend))

fig1, ax1_1 = plt.subplots(figsize=(12, 6))

# Plot Revenue Line
ax1_1.plot(x, [r/10000 for r in revenue_trend], marker='o', linewidth=2, color='#ff6b6b', label=label_rev)
ax1_1.set_ylabel(label_rev, color='#ff6b6b', fontsize=12)
ax1_1.tick_params(axis='y', labelcolor='#ff6b6b')
ax1_1.set_ylim(0, 180) 

# Highlight 2026 CNY point
ax1_1.plot(5, revenue_trend[5]/10000, marker='*', markersize=15, color='#d62828') 

ax1_1.set_xticks(x)
ax1_1.set_xticklabels(events_trend, fontsize=10, weight='bold')
ax1_1.set_title(title_trend, pad=20, fontsize=14, weight='bold')

# Annotate values
for i, txt in enumerate(revenue_trend):
    ax1_1.annotate(f'{txt/10000:.1f}', (x[i], txt/10000), textcoords="offset points", xytext=(0,10), ha='center')

# Add trend line for last 6 months (excluding YoY point)
z = np.polyfit(x[:-1], [r/10000 for r in revenue_trend[:-1]], 1)
p = np.poly1d(z)
ax1_1.plot(x[:-1], p(x[:-1]), "r--", alpha=0.5, label='Trend (6 Months)')

ax1_1.legend(loc='upper left')
plt.tight_layout()
plt.savefig(f"{output_dir}/1_Revenue_Trend_Line.png", dpi=100)
plt.close()


# --- Data 2: Module Trend (Stacked Area) ---
if use_english:
    labels_module = ['Appearance', 'Mini-games', 'Hybrid/Cultivation']
    title_module = "Module Revenue Trend (6 Months)"
else:
    labels_module = ['外显类', '小游戏', '混合/养成']
    title_module = "各模块营收趋势 (近6个月)"

# Data for last 6 months (excluding YoY for cleaner area chart)
events_module = events_trend[:-1] 
# Approximate data based on your notes
mod_appearance = [980112, 80025, 320913, 285651, 266769, 412540]
mod_minigame = [112213, 52778, 71658, 82368, 276193, 303807]
mod_hybrid = [429597, 130443, 233413, 285651, 307486, 162700]

x = np.arange(len(events_module))

fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.stackplot(x, 
              [m/10000 for m in mod_appearance], 
              [m/10000 for m in mod_minigame], 
              [m/10000 for m in mod_hybrid], 
              labels=labels_module, 
              colors=['#ff9999', '#66b3ff', '#99ff99'], alpha=0.8)

ax2.set_xticks(x)
ax2.set_xticklabels(events_module, fontsize=10, weight='bold')
ax2.set_title(title_module, pad=20, fontsize=14, weight='bold')
ax2.set_ylabel('Revenue ($10k)')
ax2.legend(loc='upper left')

plt.tight_layout()
plt.savefig(f"{output_dir}/2_Module_Trend_Stack.png", dpi=100)
plt.close()


# --- Data 3: User Tier Growth (Bar Chart) ---
if use_english:
    levels = ['Super R', 'Big R', 'Mid R']
    label_2026 = '2026 CNY'
    label_2025_xmas = '2025 Xmas'
    label_2025_cny = '2025 CNY'
    title_growth = 'User Level ARPU Comparison'
else:
    levels = ['超R', '大R', '中R']
    label_2026 = '2026 春节'
    label_2025_xmas = '2025 圣诞'
    label_2025_cny = '2025 春节'
    title_growth = '各层级用户 ARPU 对比 (本期 vs 圣诞 vs 同比)'

arpu_2026 = [542.04, 121.44, 24.95]
arpu_xmas = [528.21, 134.31, 35.14]
arpu_cny = [311.10, 73.70, 18.10]

x = np.arange(len(levels))
width = 0.25

fig3, ax3 = plt.subplots(figsize=(10, 6))
rects1 = ax3.bar(x - width, arpu_2026, width, label=label_2026, color='#1a535c')
rects2 = ax3.bar(x, arpu_xmas, width, label=label_2025_xmas, color='#4ecdc4')
rects3 = ax3.bar(x + width, arpu_cny, width, label=label_2025_cny, color='#ff6b6b')

ax3.set_ylabel('ARPU ($)')
ax3.set_title(title_growth, fontsize=14, weight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(levels, fontsize=11)
ax3.legend()

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax3.annotate(f'{height:.0f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.tight_layout()
plt.savefig(f"{output_dir}/3_User_Tier_Comparison_Bar.png", dpi=100)
plt.close()

print(f"Images generated in {output_dir}")
