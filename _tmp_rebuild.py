import json

with open(r'C:\ADHD_agent\_tmp_acts_with_dates.json', encoding='utf-8') as f:
    acts = json.load(f)

with open(r'C:\ADHD_agent\_tmp_july_v2.json', encoding='utf-8') as f:
    july_new = json.load(f)

# 颜色映射
color_map = {
    '节日付费':'#C9DAF8','节日BP':'#C9DAF8','进度小游戏':'#C9DAF8',
    '核心付费点':'#FCE5CD','主城特效投放':'#FCE5CD','节日卡包':'#FCE5CD',
    '强消耗活动':'#FCE5CD','活跃类带小额付费活动：每周一个':'#FCE5CD',
    '付费深度礼包':'#D0E0E3','联动礼包：行军表情礼包':'#FCE5CD',
    '联动礼包：连锁装饰礼包':'#FCE5CD','付费率礼包':'#D0E0E3',
    '大地图玩法':'#D0E0E3',
}

def to_act(a, month):
    cat = a['cat']
    # 合并类别名称
    cat_clean = cat
    if '联动礼包' in cat: cat_clean = '联动礼包'
    if '活跃' in cat: cat_clean = '活跃带小额付费'
    if '主城特效' in cat: cat_clean = '主城特效'
    hex_color = color_map.get(cat, color_map.get(cat_clean, '#EEEEEE'))
    phases = [{'date': p['date'], 'label': p['text']} for p in a.get('phases', [])]
    return {
        'month': month,
        'cat': cat_clean,
        'name': a['name'],
        'content': a['content'],
        't_score': a['t'] if a['t'] != '暂无评分' else '暂无',
        'start': f"2026-{a['start']}",
        'end': f"2026-{a['end']}",
        'hex': hex_color,
        'phases': phases,
        'segments': [],
    }

july_acts = [to_act(a, '7月') for a in july_new if a['has_color']]
aug_acts  = [a for a in acts if a['month'] == '8月']

new_acts = july_acts + aug_acts

with open(r'C:\ADHD_agent\_tmp_acts_with_dates.json', 'w', encoding='utf-8') as f:
    json.dump(new_acts, f, ensure_ascii=False, indent=2)

print(f"7月 {len(july_acts)} 条 + 8月 {len(aug_acts)} 条 = {len(new_acts)} 条，已更新")
for a in july_acts:
    print(f"  [{a['cat']:20s}] {a['name']:28s} {a['content']:4s} T:{a['t_score']:8s} {a['start']}->{a['end']}")
