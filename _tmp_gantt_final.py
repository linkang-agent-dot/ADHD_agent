import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timedelta
import json

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ── 读取真实数据 ──────────────────────────────────────────
with open(r'C:\ADHD_agent\_tmp_acts_with_dates.json', encoding='utf-8') as f:
    acts = json.load(f)

def dt(s):
    return datetime.strptime(s, '%Y-%m-%d')

# ── 新增活动标记（7月或8月首次出现） ─────────────────────
NEW_ACTS = {
    '挖孔小游戏', '主城特效系统', '小额转盘',          # 7月新
    '弹珠GACHA', 'GACHA每日礼包', '团购礼包', '砍价',  # 8月新
    '付费率宝箱', '联动礼包-shop-柜台',
}

# ── 颜色映射（基于分类，兼顾可读性）────────────────────
CAT_COLOR = {
    '节日付费':   '#E8A0A0',
    '节日BP':     '#F4C97A',
    '进度小游戏': '#7DC9A0',
    '抽奖类小游戏':'#A0C4E8',
    '强消耗活动': '#D4A8D4',
    '活跃类带小额付费活动：每周一个': '#B0C8E0',
    '大地图玩法': '#A8C8B0',
    '付费率礼包': '#E8D4A0',
    '付费深度礼包':'#E0B88C',
    '深度礼包类付费':'#E0B88C',
    '行军表情+节日装饰柜台': '#C8C8C8',
    '行军表情':   '#C8C8C8',
    '联动礼包':   '#D4C4B0',
    '节日卡包':   '#B8D4E0',
    '主城特效投放':'#88C8C0',
    '随机玩法付费':'#D0C0E8',
}
DEFAULT_COLOR = '#AAAAAA'

# ── 分组排序：7月在上，8月在下 ───────────────────────────
july_acts = [a for a in acts if a['month'] == '7月']
aug_acts  = [a for a in acts if a['month'] == '8月']

# 按上线日期升序排列（内部再按分类聚合）
def sort_key(a):
    return (a['start'], a['cat'], a['name'])

july_acts.sort(key=sort_key)
aug_acts.sort(key=sort_key)

all_acts = july_acts + aug_acts
n = len(all_acts)
sep_idx = len(july_acts)  # 分割线位置

# ── 绘图 ─────────────────────────────────────────────────
fig_h = n * 0.48 + 5
fig, ax = plt.subplots(figsize=(22, fig_h))
fig.patch.set_facecolor('#16161E')
ax.set_facecolor('#1E1E2C')

y_pos = list(range(n - 1, -1, -1))  # 从上往下

# 背景条纹（奇偶行区分）
for i in range(n):
    y = y_pos[i]
    ax.axhspan(y - 0.4, y + 0.4, color='white', alpha=0.02 if i % 2 == 0 else 0)

# 7月/8月背景色带
july_min = dt(min(a['start'] for a in july_acts))
july_max = dt(max(a['end'] for a in july_acts)) + timedelta(days=1)
aug_min  = dt(min(a['start'] for a in aug_acts))
aug_max  = dt(max(a['end'] for a in aug_acts)) + timedelta(days=1)
ax.axvspan(mdates.date2num(july_min), mdates.date2num(july_max), alpha=0.06, color='#F38BA8', zorder=0)
ax.axvspan(mdates.date2num(aug_min),  mdates.date2num(aug_max),  alpha=0.06, color='#89B4FA', zorder=0)

# Week 分界线（竖线）
week_lines = [
    datetime(2026, 7,  8, 0, 0),  # 7月灰度
    datetime(2026, 7, 15, 23, 59),  # 7月 week1 结束
    datetime(2026, 8,  5, 0, 0),  # 8月灰度
    datetime(2026, 8, 12, 23, 59),  # 8月 week1 结束
    datetime(2026, 8, 19, 23, 59),  # 8月 week2 结束
]
for wl in week_lines:
    ax.axvline(mdates.date2num(wl), color='#444466', linewidth=0.8, linestyle='--', alpha=0.7, zorder=1)

# Week 标签
week_labels = [
    (datetime(2026, 7, 9),  datetime(2026, 7, 15), 'W1', '#F38BA8'),
    (datetime(2026, 7, 16), datetime(2026, 7, 22), 'W2', '#F38BA8'),
    (datetime(2026, 8, 6),  datetime(2026, 8, 12), 'W1', '#89B4FA'),
    (datetime(2026, 8, 13), datetime(2026, 8, 19), 'W2', '#89B4FA'),
    (datetime(2026, 8, 20), datetime(2026, 8, 26), 'W3', '#89B4FA'),
]
for ws, we, label, color in week_labels:
    mid = mdates.date2num(ws) + (mdates.date2num(we) - mdates.date2num(ws)) / 2
    ax.text(mid, n - 0.1, label, ha='center', va='bottom', fontsize=8,
            color=color, alpha=0.8, fontweight='bold')

# 绘制活动条
for i, act in enumerate(all_acts):
    y = y_pos[i]
    color = CAT_COLOR.get(act['cat'], DEFAULT_COLOR)
    is_new = act['name'] in NEW_ACTS
    s = dt(act['start'])
    e = dt(act['end']) + timedelta(days=1)
    duration = (e - s).days

    # 主条
    bar = ax.barh(y, duration, left=mdates.date2num(s),
                  height=0.60, color=color, alpha=0.92,
                  linewidth=1.8 if is_new else 0.3,
                  edgecolor='#FFD700' if is_new else color,
                  zorder=2)

    # 分阶段标记（相位线）
    for ph in act.get('phases', []):
        try:
            ph_dt = datetime(2026, int(ph['date'][:2]), int(ph['date'][3:]))
            ax.vlines(mdates.date2num(ph_dt), y - 0.30, y + 0.30,
                      colors='white', linewidth=1.2, alpha=0.6, linestyle=':', zorder=3)
        except:
            pass

    # 文字标注（活动名 + T分）
    t_str = f"  T{act['t_score']}" if act['t_score'] not in ('暂无评分', '', '-') else ''
    new_tag = ' ★' if is_new else ''
    label_text = f" {act['name']}{new_tag}{t_str}"

    # 根据条宽度决定文字放在内部还是外部
    text_color = '#1E1E2C' if duration >= 5 else '#E0E0E0'
    text_x = mdates.date2num(s) + 0.3
    ax.text(text_x, y, label_text, va='center', ha='left',
            fontsize=7.8, color=text_color, fontweight='bold' if is_new else 'normal',
            zorder=4, clip_on=True)

# 7月/8月分割线
sep_y = (y_pos[sep_idx - 1] + y_pos[sep_idx]) / 2
ax.axhline(sep_y, color='#AAAACC', linewidth=1.5, alpha=0.5, zorder=3)

# 月份大标签
ax.text(mdates.date2num(july_min) + 0.3, sep_y + (sep_idx) / 2,
        '7月  烟火庆典', fontsize=13, color='#F38BA8',
        fontweight='bold', va='center', alpha=0.5, zorder=1)
ax.text(mdates.date2num(aug_min) + 0.3, sep_y - (n - sep_idx) / 2,
        '8月  深海节', fontsize=13, color='#89B4FA',
        fontweight='bold', va='center', alpha=0.5, zorder=1)

# ── Y轴：活动名（左侧） ────────────────────────────────
ax.set_yticks(y_pos)
ylabels = []
for a in all_acts:
    cat_short = a['cat'].replace('活跃类带小额付费活动：每周一个', '活跃小额').replace('主城特效投放', '主城特效').replace('付费深度礼包', '深度礼包').replace('深度礼包类付费', '深度礼包').replace('行军表情+节日装饰柜台', '行军+联动').replace('抽奖类小游戏', '抽奖小游戏')
    ylabels.append(f"{cat_short}")
ax.set_yticklabels(ylabels, fontsize=7.5, color='#9090B0')
ax.set_ylim(-0.8, n + 0.4)

# ── X轴（日期）────────────────────────────────────────
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7.5, color='#8080A0')

# 设置X轴范围（覆盖两个月）
x_min = mdates.date2num(datetime(2026, 7, 7))
x_max = mdates.date2num(datetime(2026, 8, 28))
ax.set_xlim(x_min, x_max)

# 网格线
ax.xaxis.grid(True, color='#333355', linewidth=0.5, alpha=0.5, zorder=0)
ax.set_axisbelow(True)

# ── 图例 ─────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor=v, label=k.replace('活跃类带小额付费活动：每周一个','活跃小额').replace('主城特效投放','主城特效').replace('行军表情+节日装饰柜台','行军+联动').replace('付费深度礼包','深度礼包').replace('深度礼包类付费','深度礼包').replace('抽奖类小游戏','抽奖小游戏'), alpha=0.9)
    for k, v in CAT_COLOR.items() if any(a['cat'] == k for a in all_acts)
]
new_item = mpatches.Patch(facecolor='#555555', edgecolor='#FFD700', linewidth=2, label='★ 本期新增')
ax.legend(handles=legend_items + [new_item],
          loc='lower right', ncol=3, fontsize=7,
          framealpha=0.4, facecolor='#1E1E2C', edgecolor='#444466',
          labelcolor='#C0C0D0')

# ── 标题和样式 ─────────────────────────────────────────
ax.set_title('X2 节日排期甘特图  |  7月 烟火庆典（14天）& 8月 深海节（21天）',
             fontsize=14, color='#CDD6F4', pad=16, fontweight='bold')
ax.tick_params(colors='#666688', axis='both', length=3)
for spine in ax.spines.values():
    spine.set_edgecolor('#333355')

plt.tight_layout(pad=2.0)
out = r'C:\ADHD_agent\_gantt_festival_final.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"保存: {out}")
