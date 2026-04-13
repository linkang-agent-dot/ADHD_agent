"""
基于真实背景色数据生成甘特图 v2
"""
import subprocess, json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from collections import Counter

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ── 获取 sheet 名 ────────────────────────────────────────
meta = json.loads(subprocess.run(
    [gws, 'sheets', 'spreadsheets', 'get', '--params',
     json.dumps({'spreadsheetId': SHEET_ID, 'fields': 'sheets.properties'})],
    capture_output=True, text=True, encoding='utf-8', errors='replace').stdout)
gid_map = {s['properties']['sheetId']: s['properties']['title']
           for s in meta.get('sheets', [])}
july_name = gid_map[1053666315]
aug_name  = gid_map[1914018097]

def fetch_grid(sheet_name, col_end='BJ'):
    params = json.dumps({
        'spreadsheetId': SHEET_ID,
        'ranges': f"'{sheet_name}'!A1:{col_end}60",
        'includeGridData': 'true',
    })
    r = subprocess.run([gws, 'sheets', 'spreadsheets', 'get', '--params', params],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    resp = json.loads(r.stdout)
    if 'error' in resp:
        print("ERROR:", resp['error']); return []
    return resp['sheets'][0]['data'][0].get('rowData', [])

def is_white(bg):
    if not bg: return True
    return bg.get('red',1)>=0.95 and bg.get('green',1)>=0.95 and bg.get('blue',1)>=0.95

def rgb_to_hex(bg):
    return '#{:02X}{:02X}{:02X}'.format(
        int(round(bg.get('red',1)*255)),
        int(round(bg.get('green',1)*255)),
        int(round(bg.get('blue',1)*255)))

def parse_date_cols(rows):
    date_cols = {}
    if len(rows) < 2: return date_cols
    for ci, cell in enumerate(rows[1].get('values', [])):
        val = cell.get('formattedValue', '')
        if val and len(val)==5 and val[2]=='-':
            date_cols[ci] = val
    return date_cols

def extract_ranges(rows, date_cols, month_label, year=2026):
    results = []
    last_cat = ''
    for ri in range(3, len(rows)):
        cells = rows[ri].get('values', [])
        if not cells: continue
        def cv(idx): return cells[idx].get('formattedValue','') if idx<len(cells) else ''
        label=cv(0).strip(); func=cv(1).strip(); dev=cv(2).strip()
        content=cv(3).strip(); t_score=cv(4).strip()
        if not func or not dev: continue
        if label: last_cat = label
        colored = []
        for ci, date_str in date_cols.items():
            if ci >= len(cells): continue
            bg = cells[ci].get('effectiveFormat',{}).get('backgroundColor',{})
            if not is_white(bg):
                colored.append({'col':ci,'date':date_str,'hex':rgb_to_hex(bg),
                                 'text':(cells[ci].get('formattedValue','') or '').strip()})
        if not colored: continue
        dates = [c['date'] for c in colored]
        dom_hex = Counter(c['hex'] for c in colored).most_common(1)[0][0]
        phases = [{'date':c['date'],'label':c['text']} for c in colored if c['text']]
        # 分段检测（颜色变化）
        sorted_c = sorted(colored, key=lambda x: x['date'])
        segments = []
        cur_hex = sorted_c[0]['hex']
        seg_start = sorted_c[0]['date']
        seg_dates = [sorted_c[0]['date']]
        for c in sorted_c[1:]:
            if c['hex'] != cur_hex:
                segments.append({'start':seg_start,'end':seg_dates[-1],'hex':cur_hex})
                cur_hex=c['hex']; seg_start=c['date']; seg_dates=[c['date']]
            else:
                seg_dates.append(c['date'])
        segments.append({'start':seg_start,'end':seg_dates[-1],'hex':cur_hex})
        results.append({
            'month':month_label,'cat':last_cat,'name':func,
            'content':content,'t_score':t_score,
            'start':f'{year}-{min(dates)}','end':f'{year}-{max(dates)}',
            'hex':dom_hex,'phases':phases,'segments':segments,
        })
    return results

# ── 读取数据 ──────────────────────────────────────────────
print("读取7月 (扩展到BJ列)...")
july_rows  = fetch_grid(july_name, 'BJ')
july_dates = parse_date_cols(july_rows)
print(f"  日期列 {len(july_dates)}: {list(july_dates.values())}")
july_acts  = extract_ranges(july_rows, july_dates, '7月')

print("读取8月 (扩展到BJ列)...")
aug_rows  = fetch_grid(aug_name, 'BJ')
aug_dates = parse_date_cols(aug_rows)
print(f"  日期列 {len(aug_dates)}: {list(aug_dates.values())}")
aug_acts  = extract_ranges(aug_rows, aug_dates, '8月')

all_acts = july_acts + aug_acts
print(f"\n共 {len(all_acts)} 条活动：")
for a in all_acts:
    segs = ' | '.join(f"{s['start'][5:]}~{s['end'][5:]}({s['hex']})" for s in a['segments'])
    print(f"  [{a['month']}] {a['cat']:14s}|{a['name']:28s} {a['start'][5:]}→{a['end'][5:]}  {segs}")

# ── 绘图 ─────────────────────────────────────────────────
def parse_dt(s):
    return datetime.strptime(s, '%Y-%m-%d')

n = len(all_acts)
fig, ax = plt.subplots(figsize=(20, max(12, n*0.5+3)))
fig.patch.set_facecolor('#1E1E2E')
ax.set_facecolor('#252535')

y_positions = list(range(n-1, -1, -1))

# 分界线位置
july_count = len(july_acts)

for i, act in enumerate(all_acts):
    y = y_positions[i]

    if act['segments'] and len(act['segments']) > 1:
        # 多段着色
        for seg in act['segments']:
            seg_start = parse_dt(f"2026-{seg['start']}")
            seg_end   = parse_dt(f"2026-{seg['end']}") + timedelta(days=1)
            # 将十六进制颜色转为 matplotlib 颜色
            h = seg['hex'].lstrip('#')
            sr,sg,sb = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
            ax.barh(y, (seg_end-seg_start).days,
                    left=mdates.date2num(seg_start), height=0.65,
                    color=(sr,sg,sb), alpha=0.9, edgecolor='none')
    else:
        start = parse_dt(act['start'])
        end   = parse_dt(act['end']) + timedelta(days=1)
        h = act['hex'].lstrip('#')
        cr,cg,cb = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
        ax.barh(y, (end-start).days,
                left=mdates.date2num(start), height=0.65,
                color=(cr,cg,cb), alpha=0.9, edgecolor='none')

    # 文字标注
    label_x = mdates.date2num(parse_dt(act['start'])) + 0.2
    ax.text(label_x, y, f"  {act['name']}  {act['t_score']}",
            va='center', ha='left', fontsize=7.5, color='#1E1E2E', fontweight='bold')

# 7月/8月分隔线
aug_y = y_positions[july_count - 1] - 0.5
ax.axhline(aug_y, color='#AAB4C8', linewidth=1.5, alpha=0.6)

# 月份标签
if july_acts:
    mid_july = y_positions[0] - (july_count - 1) / 2
    ax.text(mdates.date2num(parse_dt('2026-07-08')), mid_july,
            ' 7月 烟火庆典', fontsize=11, color='#F38BA8', fontweight='bold', va='center')
if aug_acts:
    mid_aug = y_positions[july_count] - (len(aug_acts) - 1) / 2
    ax.text(mdates.date2num(parse_dt('2026-08-05')), mid_aug,
            ' 8月 深海节', fontsize=11, color='#89DCEB', fontweight='bold', va='center')

# 背景淡色分区
if july_acts:
    july_start = parse_dt(min(a['start'] for a in july_acts))
    july_end   = parse_dt(max(a['end'] for a in july_acts)) + timedelta(days=1)
    ax.axvspan(mdates.date2num(july_start), mdates.date2num(july_end), alpha=0.04, color='#F38BA8')
if aug_acts:
    aug_start = parse_dt(min(a['start'] for a in aug_acts))
    aug_end   = parse_dt(max(a['end'] for a in aug_acts)) + timedelta(days=1)
    ax.axvspan(mdates.date2num(aug_start), mdates.date2num(aug_end), alpha=0.04, color='#89DCEB')

# X轴
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.setp(ax.get_xticklabels(), rotation=40, ha='right', fontsize=8, color='#CDD6F4')

# Y轴（分类+名称）
ax.set_yticks(y_positions)
ylabels = [f"{a['cat']} | {a['name']}" for a in all_acts]
ax.set_yticklabels(ylabels, fontsize=7.5, color='#CDD6F4')
ax.set_ylim(-0.8, n-0.2)
ax.tick_params(axis='both', colors='#666')
for spine in ax.spines.values():
    spine.set_edgecolor('#444')

ax.set_title('X2 节日排期甘特图  |  7月烟火庆典 & 8月深海节  (颜色来自表格原色)',
             fontsize=13, color='#CDD6F4', pad=12, fontweight='bold')
plt.tight_layout(pad=1.5)
out = r'C:\ADHD_agent\_gantt_festival_v2.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\n图已保存: {out}")
