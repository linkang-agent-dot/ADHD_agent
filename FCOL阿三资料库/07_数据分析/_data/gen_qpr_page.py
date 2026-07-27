# -*- coding: utf-8 -*-
"""永恒8卡质价比页：有效能力值(位置加权)/工资 + 145阈上超额/工资。口径=裸值+3+8卡15+球员等级5(+4)+队套6"""
import json, os
SP = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(SP, 'el_tm_attrs_full.json'), encoding='utf-8'))
el_list = json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']
B = 3 + 15 + 4 + 6  # +28
# 位置权重（核心3/重要2/版本1.5/边缘1，未列=0）
W = {
 'ST': {'sprintspeed':3,'acceleration':3,'finishing':3,'longshots':3,'curve':3,'reactions':3,
        'shotpower':2,'positioning':2,'dribbling':2,'ballcontrol':2,'agility':2,'balance':2,'composure':2,
        'headingaccuracy':1.5,'strength':1.5,'stamina':1.5,'volleys':1.5,'jumping':1.5,
        'shortpassing':1,'vision':1,'crossing':1},
 'WG': {'sprintspeed':3,'acceleration':3,'dribbling':3,'ballcontrol':3,'agility':3,
        'finishing':2,'curve':2,'crossing':2,'balance':2,'reactions':2,
        'longshots':1.5,'volleys':1.5,'shotpower':1.5,
        'shortpassing':1,'vision':1,'stamina':1,'strength':1,'composure':1},
 'CAM': {'shortpassing':3,'vision':3,'longshots':3,'dribbling':3,'ballcontrol':3,
        'finishing':2,'curve':2,'agility':2,'balance':2,'reactions':2,'composure':2,'shotpower':2,
        'longpassing':1.5,'sprintspeed':1.5,'acceleration':1.5,
        'stamina':1,'strength':1,'positioning':1},
 'CM': {'shortpassing':3,'vision':3,'longpassing':3,'dribbling':3,'ballcontrol':3,'reactions':3,
        'agility':2,'balance':2,'stamina':2,'composure':2,'sprintspeed':2,'acceleration':2,
        'longshots':1.5,'standingtackle':1.5,'interceptions':1.5,
        'strength':1,'marking':1,'finishing':1},
 'CDM': {'marking':3,'standingtackle':3,'interceptions':3,'stamina':3,'strength':3,
        'shortpassing':2,'reactions':2,'sprintspeed':2,'acceleration':2,'aggression':2,'balance':2,
        'slidingtackle':1.5,'headingaccuracy':1.5,'longpassing':1.5,
        'ballcontrol':1,'composure':1,'jumping':1},
 'CB': {'sprintspeed':3,'acceleration':3,'marking':3,'standingtackle':3,'interceptions':3,'strength':3,'headingaccuracy':3,
        'reactions':2,'jumping':2,'aggression':2,'balance':2,'slidingtackle':2,
        'shortpassing':1,'stamina':1,'ballcontrol':1,'composure':1},
 'FB': {'sprintspeed':3,'acceleration':3,'marking':3,'standingtackle':3,'interceptions':3,'crossing':3,
        'stamina':2,'strength':2,'reactions':2,'agility':2,'slidingtackle':2,
        'shortpassing':1,'dribbling':1,'headingaccuracy':1,'jumping':1,'balance':1},
 'GK': {'gkdiving':3,'gkhandling':3,'gkkicking':1.5,'gkreflexes':3,'gkpositioning':3,'reactions':2,'jumping':1.5},
}
POSMAP = {'ST':'ST','CF':'ST','LW':'WG','RW':'WG','RM':'WG','LM':'WG','CAM':'CAM','CM':'CM','CDM':'CDM','CB':'CB','LB':'FB','RB':'FB','GK':'GK'}
rows = []
for p in el_list:
    name = p['name']
    el = d[name]['EL']
    pos = p['pos1']
    w = W[POSMAP[pos]]
    num = den = exc = 0.0
    for k, wt in w.items():
        if k not in el['attr']: continue
        v = int(el['attr'][k]['value']) + B
        num += wt * v; den += wt
        exc += wt * max(0, v - 145)
    eff = num / den
    sal = int(el['salary'])
    rows.append({'name': name, 'pos': pos, 'ovr': int(p['pos1val']), 'sal': sal,
                 'eff': eff, 'qpr': eff / sal, 'exc': exc, 'excq': exc / sal})
rows.sort(key=lambda r: -r['qpr'])
CNPOS = {'ST':'中锋','CF':'前锋','LW':'左边锋','RW':'右边锋','RM':'右中场','LM':'左中场','CAM':'前腰','CM':'中前卫','CDM':'后腰','CB':'中卫','LB':'左后卫','RB':'右后卫','GK':'门将'}
trs = ''
for i, r in enumerate(rows, 1):
    hl = ' class="hl"' if i <= 5 else ''
    trs += '<tr%s><td>%d</td><td class="nm">%s</td><td>%s</td><td>%d</td><td>%d</td><td>%.1f</td><td class="q">%.2f</td><td>%.0f</td><td class="q2">%.1f</td></tr>' % (
        hl, i, r['name'], CNPOS.get(r['pos'], r['pos']), r['ovr'], r['sal'], r['eff'], r['qpr'], r['exc'], r['excq'])
# 权重表展示
wtab = ''
for pk, w in W.items():
    items = sorted(w.items(), key=lambda x: -x[1])
    wtab += '<tr><td>%s</td><td style="text-align:left">%s</td></tr>' % (pk, '，'.join('%s×%g' % (k, v) for k, v in items))
html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>永恒8卡·质价比榜(有效能力值/工资)</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0}'
'.wrap{max-width:1050px;margin:0 auto;padding:22px 16px 60px}'
'h1{color:#ffd35c;font-size:20px}h2{color:#7ec8ff;font-size:16px;margin-top:26px}'
'.note{color:#8b93a7;font-size:12.5px;line-height:1.6}'
'table{border-collapse:collapse;width:100%;font-size:12.8px;margin-top:8px}'
'th{background:#1d2740;color:#9fb4d8;padding:4px 8px;position:sticky;top:0}'
'td{padding:3px 8px;border-bottom:1px solid #1d2438;text-align:center}'
'td.nm{text-align:left;font-weight:bold;color:#fff}td.q{color:#5cff8f;font-weight:bold}td.q2{color:#ffd35c}'
'tr.hl td{background:#20304e}'
'</style></head><body><div class="wrap">'
'<h1>永恒 8 卡 · 质价比榜（每点工资买到多少有效能力值）</h1>'
'<div class="note">口径：接口裸值+3(游戏显示) + 8卡强化+15 + 球员等级5(+4假设) + 队套+6 = +28。<br>'
'<b>有效能力值</b>=位置加权均值（权重表见页底：核心×3/重要×2/版本项×1.5/边缘×1/无关×0，按阿三属性框架自定，可挑战）。<br>'
'<b>质价比</b>=有效能力值÷工资；<b>阈上超额/薪</b>=Σ权重×max(0,属性−145)÷工资——按阈值机制，145线以上的点数才是"买到刀刃上"的部分，该列更能区分"高价值高薪"与"低价值低薪"。</div>'
'<h2>全榜（按质价比）</h2>'
'<table><tr><th>#</th><th>球员</th><th>位置</th><th>8卡前1强总评</th><th>工资</th><th>有效能力值</th><th>质价比</th><th>阈上加权点</th><th>阈上/薪</th></tr>'
+ trs + '</table>'
'<h2>位置权重表（全公开）</h2><table><tr><th>位置组</th><th>权重</th></tr>' + wtab + '</table>'
'</div></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\永恒8卡_质价比榜_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html)
os.replace(tmp, P)
# 控制台摘要
print('TOP15 质价比:')
for i, r in enumerate(rows[:15], 1):
    print('%2d %-22s %-4s 薪%-3d 有效%.1f 质价比%.2f | 阈上/薪%.1f' % (i, r['name'], r['pos'], r['sal'], r['eff'], r['qpr'], r['excq']))
print('\nTOP10 阈上超额/薪:')
for i, r in enumerate(sorted(rows, key=lambda x: -x['excq'])[:10], 1):
    print('%2d %-22s %-4s 薪%-3d 阈上/薪%.1f (质价比%.2f)' % (i, r['name'], r['pos'], r['sal'], r['excq'], r['qpr']))
print('page ok')
