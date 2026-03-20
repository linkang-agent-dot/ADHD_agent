import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('report_images/2026情人节/input_data.json', encoding='utf-8') as f:
    data = json.load(f)

# Tab3 R级拆分数据
tab3_tier = {
    '对对碰':        {'chaoR': (214, 4616.09), 'daR': (134, 1782.69), 'zhongR': (171, 1638.59), 'xiaoR': (36, 192.6)},
    '送花礼包':      {'chaoR': (93, 46366.23), 'daR': (29, 3703.97), 'zhongR': (29, 459.6), 'xiaoR': (12, 79.88)},
    '情人节BP':      {'chaoR': (653, 20298.34), 'daR': (553, 12269.26), 'zhongR': (890, 13673.2), 'xiaoR': (151, 1436.08)},
    '节日大富翁':    {'chaoR': (582, 59230.34), 'daR': (433, 9348.79), 'zhongR': (693, 6416.37), 'xiaoR': (131, 637.16)},
    '机甲GACHA':     {'chaoR': (174, 55707.84), 'daR': (111, 11591.52), 'zhongR': (169, 7941.97), 'xiaoR': (29, 559.61)},
    '通用转盘':      {'chaoR': (250, 12441.25), 'daR': (195, 4365.43), 'zhongR': (228, 1889.63), 'xiaoR': (42, 156.47)},
    '限时抢购':      {'chaoR': (302, 34070.65), 'daR': (183, 12256.3), 'zhongR': (151, 7947.81), 'xiaoR': (13, 339.86)},
    '聚宝盆':        {'chaoR': (93, 1302.78), 'daR': (102, 1120.98), 'zhongR': (133, 919.92), 'xiaoR': (17, 59.81)},
    '云上探宝':      {'chaoR': (486, 81908.6), 'daR': (399, 25148.58), 'zhongR': (639, 17389.75), 'xiaoR': (124, 1169.49)},
    '挖孔小游戏':    {'chaoR': (606, 166247.66), 'daR': (538, 45781.48), 'zhongR': (967, 29532.07), 'xiaoR': (278, 1896.82)},
}

for act in data['activity_ranking']:
    name = act['name']
    if name in tab3_tier:
        tb = {}
        for tier, (buyers, revenue) in tab3_tier[name].items():
            tb[tier] = {'buyers': buyers, 'revenue': round(revenue, 2)}
        act['tier_breakdown'] = tb

with open('report_images/2026情人节/input_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Verify
for a in data['activity_ranking']:
    tb = a.get('tier_breakdown', {})
    if tb:
        chao_pct = tb.get('chaoR', {}).get('revenue', 0) / a['revenue'] * 100 if a['revenue'] > 0 else 0
        print(f"{a['name']}: chaoR={chao_pct:.1f}%")
    else:
        print(f"{a['name']}: no tier data")
