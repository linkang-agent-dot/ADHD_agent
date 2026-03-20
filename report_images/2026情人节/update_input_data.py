"""
更新 input_data.json，补充 daily_revenue / unique_buyers / core_metrics_by_tier / tier_headcount_trend 等字段
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('report_images/2026情人节/input_data.json', encoding='utf-8') as f:
    data = json.load(f)

# === 1. daily_revenue (from 完整数据梳理 tab, rows 25-48) ===
data['daily_revenue'] = [
    {'date': '2026-02-10', 'revenue': 3357.66, 'buyers': 174},
    {'date': '2026-02-11', 'revenue': 40330.14, 'buyers': 1115},
    {'date': '2026-02-12', 'revenue': 39315.09, 'buyers': 1320},
    {'date': '2026-02-13', 'revenue': 27596.53, 'buyers': 908},
    {'date': '2026-02-14', 'revenue': 30654.63, 'buyers': 1064},
    {'date': '2026-02-15', 'revenue': 42052.69, 'buyers': 1025},
    {'date': '2026-02-16', 'revenue': 22836.71, 'buyers': 989},
    {'date': '2026-02-17', 'revenue': 75951.49, 'buyers': 1400},
    {'date': '2026-02-18', 'revenue': 48479.50, 'buyers': 1425},
    {'date': '2026-02-19', 'revenue': 45091.20, 'buyers': 1088},
    {'date': '2026-02-20', 'revenue': 60018.57, 'buyers': 1410},
    {'date': '2026-02-21', 'revenue': 44390.21, 'buyers': 1146},
    {'date': '2026-02-22', 'revenue': 46433.48, 'buyers': 1170},
    {'date': '2026-02-23', 'revenue': 62442.92, 'buyers': 1221},
    {'date': '2026-02-24', 'revenue': 11726.02, 'buyers': 650},
    {'date': '2026-02-25', 'revenue': 14755.22, 'buyers': 574},
    {'date': '2026-02-26', 'revenue': 20487.66, 'buyers': 627},
    {'date': '2026-02-27', 'revenue': 48710.08, 'buyers': 787},
    {'date': '2026-02-28', 'revenue': 35808.41, 'buyers': 785},
    {'date': '2026-03-01', 'revenue': 24457.09, 'buyers': 535},
    {'date': '2026-03-02', 'revenue': 46517.82, 'buyers': 688},
    {'date': '2026-03-03', 'revenue': 35500.14, 'buyers': 444},
    {'date': '2026-03-04', 'revenue': 10455.22, 'buyers': 310},
    {'date': '2026-03-05', 'revenue': 9627.83, 'buyers': 712},
]

# === 2. core_metrics_by_tier (from 完整数据梳理 tab, rows 2-8) ===
data['core_metrics_by_tier'] = {
    'total':  {'active': 20439, 'buyers': 4496, 'event_revenue': 839629.16, 'total_revenue': 1703981.12, 'event_share': 49.27, 'buy_rate': 22.0, 'arppu': 186.75, 'arpu': 41.08},
    'paying': {'active': 13615, 'buyers': 4496, 'event_revenue': 839629.16, 'total_revenue': 1703981.12, 'event_share': 49.27, 'buy_rate': 33.02, 'arppu': 186.75, 'arpu': 61.67},
    'xiaoR':  {'active': 7122, 'buyers': 795, 'event_revenue': 11808.21, 'total_revenue': 36513.32, 'event_share': 32.34, 'buy_rate': 11.16, 'arppu': 14.85, 'arpu': 1.66},
    'zhongR': {'active': 3990, 'buyers': 1919, 'event_revenue': 122480.56, 'total_revenue': 309789.21, 'event_share': 39.54, 'buy_rate': 48.1, 'arppu': 63.83, 'arpu': 30.7},
    'daR':    {'active': 1357, 'buyers': 890, 'event_revenue': 160330.15, 'total_revenue': 354556.82, 'event_share': 45.22, 'buy_rate': 65.59, 'arppu': 180.15, 'arpu': 118.15},
    'chaoR':  {'active': 1146, 'buyers': 892, 'event_revenue': 545010.24, 'total_revenue': 1003121.77, 'event_share': 54.33, 'buy_rate': 77.84, 'arppu': 611.0, 'arpu': 475.58},
}

# === 3. tier_headcount_trend (from 完整数据梳理 tab, rows 15-20) ===
events_hist = ['圣诞节', '感恩节', '万圣节', '音乐节', '周年庆', '登月节',
               '深海节', '拓荒节', '复活节', '科技节', '2026情人节', '2025春节']
xiaoR_hc  = [7892, 7209, 7539, 8613, 10149, 8618, 10299, 9840, 12216, 11898, 12791, 13074]
zhongR_hc = [4234, 4043, 4120, 4481, 4941, 4533, 5039, 4942, 5444, 5427, 5492, 5662]
daR_hc    = [1418, 1411, 1386, 1443, 1538, 1426, 1473, 1401, 1457, 1432, 1395, 1429]
chaoR_hc  = [1108, 1093, 1071, 1059, 1075, 993, 1001, 931, 961, 923, 875, 902]
paying_hc = [14652, 13756, 14116, 15596, 17703, 15570, 17812, 17114, 20078, 19680, 20553, 21067]

data['tier_headcount_trend'] = []
for i, evt in enumerate(events_hist):
    data['tier_headcount_trend'].append({
        'event': evt,
        'xiaoR': xiaoR_hc[i],
        'zhongR': zhongR_hc[i],
        'daR': daR_hc[i],
        'chaoR': chaoR_hc[i],
        'total': paying_hc[i],
    })

# === 4. activity_ranking with unique_buyers (from 详细活动付费数据 tab) ===
# Tab 3 raw data: name -> (unique_buyers, revenue)
tab3 = {
    '对对碰': (555, 8229.97),
    '送花礼包': (163, 50609.68),
    '情人节BP': (2247, 47676.88),
    '节日大富翁': (1839, 75632.66),
    '机甲GACHA': (483, 75800.94),
    '情人节七日': (126, 1302.39),
    '挖矿小游戏活动': (880, 12487.80),
    '挖矿小游戏': (209, 3360.53),
    '转盘折扣小额': (17, 194.79),
    '情人节自选周卡': (176, 7988.18),
    '节日特惠卡': (685, 14680.42),
    '情人节-强消耗（扭蛋机）': (373, 7429.56),
    '通用转盘': (715, 18852.78),
    '限时抢购': (649, 54614.62),
    '2025深海节累充服务器礼包': (559, 6574.41),
    '聚宝盆': (345, 3403.49),
    '2025周年庆累充服务器礼包': (135, 2808.65),
    '掉落转付费礼包': (592, 4143.04),
    '2026情人节-行军表情': (2035, 10164.63),
    '挖孔小游戏': (2389, 243458.03),
    '预购连锁': (270, 26997.30),
    '云上探宝': (1648, 125616.42),
    '2026情人节-行军特效': (751, 15012.49),
    '情人节bingo活动宝箱礼包': (338, 1686.62),
    '情人节组队BP': (1485, 20809.17),
}

# Name mapping: tab3 name -> sub_activity_detail name (where they differ)
name_map = {
    '挖孔小游戏礼包': '挖孔小游戏',
    '通用小额随机-转盘': '通用转盘',
    '2025情人节送花礼包': '送花礼包',
}

total_event_buyers = 4496
total_sub_rev = sum(a['revenue'] for a in data['sub_activity_detail'])

activity_ranking = []
for act in sorted(data['sub_activity_detail'], key=lambda x: x['revenue'], reverse=True):
    name = act['name']
    rev = act['revenue']
    mod = act['type']

    # Find unique_buyers
    ub = 0
    if name in tab3:
        ub = tab3[name][0]
    else:
        for t3name, (t3ub, t3rev) in tab3.items():
            mapped = name_map.get(t3name, t3name)
            if mapped == name:
                ub = t3ub
                break

    share = round(rev / total_sub_rev * 100, 1) if total_sub_rev > 0 else 0
    event_arpu = round(rev / total_event_buyers, 2) if total_event_buyers > 0 else 0

    entry = {
        'name': name,
        'module': mod,
        'revenue': rev,
        'share': share,
        'unique_buyers': ub,
        'event_arpu': event_arpu,
    }
    activity_ranking.append(entry)

data['activity_ranking'] = activity_ranking

# === 5. historical_revenue (from metrics_trend) ===
data['historical_revenue'] = [
    {'event': mt['event'], 'revenue': mt['revenue']}
    for mt in data['metrics_trend']
]

# === Save ===
with open('report_images/2026情人节/input_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done!')
print(f"daily_revenue: {len(data['daily_revenue'])} days")
print(f"activity_ranking: {len(data['activity_ranking'])} activities, unique_buyers example: {data['activity_ranking'][0]}")
print(f"tier_headcount_trend: {len(data['tier_headcount_trend'])} periods")
print(f"core_metrics_by_tier keys: {list(data['core_metrics_by_tier'].keys())}")
print(f"historical_revenue: {len(data['historical_revenue'])} events")
