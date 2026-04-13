import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ── 颜色方案 ──────────────────────────────────────────────
CAT_COLORS = {
    '节日付费':     '#E74C3C',
    '抽奖小游戏':   '#E67E22',
    '节日BP':       '#F39C12',
    '强消耗':       '#D35400',
    '进度小游戏':   '#27AE60',
    '活跃带付费':   '#16A085',
    '大地图玩法':   '#2980B9',
    '礼包付费':     '#8E44AD',
    '行军表情':     '#2C3E50',
    '联动礼包':     '#7F8C8D',
    '节日卡包':     '#BDC3C7',
    '随机玩法':     '#95A5A6',
    '主城/行军投放':'#1ABC9C',
}

JULY_START  = datetime(2026, 7,  8)
JULY_END    = datetime(2026, 7, 29)
AUG_START   = datetime(2026, 8,  5)
AUG_END     = datetime(2026, 8, 26)

def d(month, day):
    return datetime(2026, month, day)

# ── 活动数据  [label, cat, start, end, note, is_new] ──────
activities = [
    # ────── 7月 ──────
    ("7月 | 累充（节日付费）",         '节日付费',     d(7,8),  d(7,29), "T48.5",   False),
    ("7月 | 节日BP+集结礼包",          '节日BP',       d(7,8),  d(7,29), "换皮",    False),
    ("7月 | 强消耗扭蛋机",             '强消耗',       d(7,8),  d(7,29), "复用",    False),
    ("7月 | 普通大富翁（进度小游戏）", '进度小游戏',   d(7,8),  d(7,29), "换皮",    False),
    ("7月 | 掉落转付费",               '活跃带付费',   d(7,8),  d(7,29), "T48.2",   False),
    ("7月 | 7日活动",                  '活跃带付费',   d(7,8),  d(7,29), "复用",    False),
    ("7月 | 巨猿",                     '大地图玩法',   d(7,8),  d(7,29), "复用",    False),
    ("7月 | 周卡",                     '礼包付费',     d(7,8),  d(7,29), "T26",     False),
    ("7月 | 抢购礼包",                 '礼包付费',     d(7,8),  d(7,29), "T61.5",   False),
    ("7月 | 小额转盘 ★",               '礼包付费',     d(7,8),  d(7,29), "T60 新",  True),
    ("7月 | 行军表情",                 '行军表情',     d(7,8),  d(7,29), "T23",     False),
    ("7月 | 联动礼包-柜台",            '联动礼包',     d(7,8),  d(7,29), "换皮",    False),
    ("7月 | 节日卡包系统",             '节日卡包',     d(7,8),  d(7,29), "换皮",    False),
    ("7月 | 付费率宝箱",               '随机玩法',     d(7,8),  d(7,29), "复用",    False),
    ("7月 | 挖孔小游戏（主城特效）★",  '主城/行军投放',d(7,8),  d(7,29), "T83.5 新",True),
    ("7月 | 主城特效系统 ★",           '主城/行军投放',d(7,8),  d(7,29), "搬运 新", True),

    # ────── 8月 ──────
    ("8月 | 累充+排行+乐透",           '节日付费',     d(8,5),  d(8,26), "升级",    False),
    ("8月 | 周年庆皮肤抽奖 ★",         '抽奖小游戏',   d(8,5),  d(8,26), "T73.5 新",True),
    ("8月 | GACHA每日礼包 ★",          '抽奖小游戏',   d(8,5),  d(8,26), "换皮 新", True),
    ("8月 | 长节日BP+集结礼包",        '节日BP',       d(8,5),  d(8,26), "换皮",    False),
    ("8月 | 强消耗扭蛋机",             '强消耗',       d(8,5),  d(8,26), "复用",    False),
    ("8月 | 普通大富翁（进度小游戏）", '进度小游戏',   d(8,5),  d(8,26), "换皮",    False),
    ("8月 | 掉落转付费",               '活跃带付费',   d(8,5),  d(8,26), "T48.2",   False),
    ("8月 | 7日活动",                  '活跃带付费',   d(8,5),  d(8,26), "复用",    False),
    ("8月 | 巨猿",                     '大地图玩法',   d(8,5),  d(8,26), "复用",    False),
    ("8月 | 周卡",                     '礼包付费',     d(8,5),  d(8,26), "T26",     False),
    ("8月 | 抢购礼包",                 '礼包付费',     d(8,5),  d(8,26), "T61.5",   False),
    ("8月 | 砍价 ★",                   '礼包付费',     d(8,5),  d(8,26), "T80 新",  True),
    ("8月 | 团购礼包",                 '礼包付费',     d(8,5),  d(8,26), "T59",     False),
    ("8月 | 行军表情",                 '行军表情',     d(8,5),  d(8,26), "T23",     False),
    ("8月 | 联动礼包-柜台",            '联动礼包',     d(8,5),  d(8,26), "换皮",    False),
    ("8月 | 节日卡包系统",             '节日卡包',     d(8,5),  d(8,26), "换皮",    False),
    ("8月 | 付费率宝箱",               '随机玩法',     d(8,5),  d(8,26), "复用",    False),
    ("8月 | 挖孔小游戏（主城特效）",   '主城/行军投放',d(8,5),  d(8,26), "T83.5",   False),
    ("8月 | 钓鱼行军特效 ★",           '主城/行军投放',d(8,5),  d(8,26), "T75 新",  True),
]

# ── 绘图 ─────────────────────────────────────────────────
n = len(activities)
fig_h = max(14, n * 0.44 + 3)
fig, ax = plt.subplots(figsize=(18, fig_h))
fig.patch.set_facecolor('#1E1E2E')
ax.set_facecolor('#252535')

y_positions = list(range(n - 1, -1, -1))  # 从上到下

for i, (label, cat, start, end, note, is_new) in enumerate(activities):
    y = y_positions[i]
    color = CAT_COLORS.get(cat, '#888')
    alpha = 0.95 if is_new else 0.72
    bar_end = end + timedelta(days=1)

    # 背景条（加粗边框区分新内容）
    ax.barh(y, (bar_end - start).days, left=mdates.date2num(start),
            height=0.62, color=color, alpha=alpha,
            linewidth=2.0 if is_new else 0.5,
            edgecolor='#FFD700' if is_new else color)

    # 三阶段分割线（节日付费 / 进度小游戏 / 节日BP）
    if '进度小游戏' in label or '节日付费' in label or '节日BP' in label or '累充' in label:
        fest_start = start
        seg = (end - start).days // 3
        for k in range(1, 3):
            divider = fest_start + timedelta(days=seg * k)
            ax.vlines(mdates.date2num(divider), y - 0.31, y + 0.31,
                      colors='white', linewidth=1, alpha=0.5, linestyle='--')

    # 分割线（7月/8月之间）
    if '8月 | 累充' in label:
        ax.axhline(y + 0.75, color='#AAB4C8', linewidth=1.2, linestyle='-', alpha=0.4)

    # 文字标注
    ax.text(mdates.date2num(start) + 0.3, y, f" {label.split('|')[1].strip()}  {note}",
            va='center', ha='left', fontsize=7.8,
            color='white', fontweight='bold' if is_new else 'normal')

# ── X 轴（日期）─────────────────────────────────────────
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=8, color='#CDD6F4')

# 7月/8月分区背景
ax.axvspan(mdates.date2num(JULY_START), mdates.date2num(JULY_END + timedelta(days=1)),
           alpha=0.05, color='#F38BA8')
ax.axvspan(mdates.date2num(AUG_START), mdates.date2num(AUG_END + timedelta(days=1)),
           alpha=0.05, color='#89DCEB')

# 标注节日名
ax.text(mdates.date2num(JULY_START + timedelta(days=1)), n - 0.5,
        '[ 7月 烟火庆典 ]', fontsize=10, color='#F38BA8', fontweight='bold', va='top')
ax.text(mdates.date2num(AUG_START + timedelta(days=1)), n - 0.5 - 16.5,
        '[ 8月 深海节 ]', fontsize=10, color='#89DCEB', fontweight='bold', va='top')

# ── Y 轴 ────────────────────────────────────────────────
ax.set_yticks([])
ax.set_ylim(-0.8, n - 0.2)

# ── 今日线 ───────────────────────────────────────────────
today = datetime(2026, 4, 7)
# 今日不在范围内，跳过

# ── 图例 ─────────────────────────────────────────────────
patches = [mpatches.Patch(color=v, label=k, alpha=0.85) for k, v in CAT_COLORS.items()]
new_patch = mpatches.Patch(facecolor='#555', edgecolor='#FFD700', linewidth=2, label='★ 本期新增')
ax.legend(handles=patches + [new_patch], loc='lower right',
          fontsize=7.5, ncol=2, framealpha=0.3,
          labelcolor='white', facecolor='#1E1E2E', edgecolor='#444')

ax.set_title('X2 节日排期甘特图  |  7月烟火庆典 & 8月深海节',
             fontsize=14, color='#CDD6F4', pad=14, fontweight='bold')
ax.tick_params(colors='#888', axis='both')
for spine in ax.spines.values():
    spine.set_edgecolor('#444')

plt.tight_layout(pad=1.5)
out = r'C:\ADHD_agent\_gantt_festival.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"saved: {out}")
