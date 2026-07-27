# -*- coding: utf-8 -*-
"""永恒6卡vs时刻8卡 29项全量对照页(球员等级5+队套6, 无优先级预筛无观点)。改LV常数后直接重跑。"""
import json, os
SP = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(SP,'el_tm_attrs.json'), encoding='utf-8'))
el_list = {p['name']: int(p['pos1val']) for p in json.load(open(os.path.join(SP,'el_list.json'), encoding='utf-8'))['db']}
tm_list = {p['name']: int(p['pos1val']) for p in json.load(open(os.path.join(SP,'tm_list.json'), encoding='utf-8'))['db']}
CN = {'A. Shevchenko':'舍甫琴科','Z. Ibrahimović':'伊布','Roberto Carlos':'卡洛斯','B. Schweinsteiger':'施魏因施泰格','T. Kroos':'克罗斯','A. Nesta':'内斯塔','Ronaldo':'大罗',"S. Eto'o":'埃托奥','Y. Touré':'亚亚图雷','R. van Nistelrooy':'范尼','T. Henry':'亨利','Raúl':'劳尔'}
GRP = [('速度',['sprintspeed','acceleration']),('射门',['finishing','shotpower','longshots','positioning','volleys','penalties','curve','freekickaccuracy']),('传球',['shortpassing','vision','crossing','longpassing']),('盘带',['dribbling','ballcontrol','agility','balance','reactions']),('防守',['marking','standingtackle','interceptions','slidingtackle','aggression']),('身体',['strength','stamina','headingaccuracy','jumping','composure'])]
CAL, ET, TT, LV, TC = 3, 8, 15, 4, 6   # 口径/永恒6卡/时刻8卡/球员等级5(假设+4)/队套6
EB, TB = CAL+ET+LV+TC, CAL+TT+LV+TC
parts = []
for name in ['Roberto Carlos','A. Nesta','A. Shevchenko','R. van Nistelrooy','T. Henry','Raúl','Z. Ibrahimović',"S. Eto'o",'Ronaldo','Y. Touré','B. Schweinsteiger','T. Kroos']:
    v = d[name]; el, tm = v['EL'], v['TM']
    secs = ''
    for gname, keys in GRP:
        rows = ''
        for k in keys:
            if k not in el['attr'] or k not in tm['attr']: continue
            nm = el['attr'][k]['name']
            t8 = int(tm['attr'][k]['value']) + TB; e6 = int(el['attr'][k]['value']) + EB
            note = ''
            for th in (165,155,145):
                if e6 >= th > t8: note = '永恒独过%d' % th; break
                if t8 >= th > e6: note = '时刻独过%d' % th; break
            cls = 'up' if e6 > t8 else ('dn' if t8 > e6 else '')
            rows += '<tr class="%s"><td>%s</td><td>%d</td><td>%d</td><td>%+d</td><td class="th">%s</td></tr>' % (cls,nm,t8,e6,e6-t8,note)
        secs += '<tr class="g"><td colspan="5">%s</td></tr>%s' % (gname, rows)
    parts.append('<div class="pl"><h2>%s <span class="m">1强总评 时刻%d/永恒%d</span></h2><table><tr><th>属性</th><th>时刻8卡</th><th>永恒6卡</th><th>Δ</th><th>阈值差异</th></tr>%s</table></div>' % (CN[name], tm_list[name], el_list[name], secs))
html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>永恒6卡vs时刻8卡·29项全量</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0}.wrap{max-width:1180px;margin:0 auto;padding:20px;display:flex;flex-wrap:wrap;gap:16px}'
'h1{width:100%;color:#ffd35c;font-size:19px}.note{width:100%;color:#8b93a7;font-size:12.5px}'
'.pl{background:#171e2e;border:1px solid #263048;border-radius:10px;padding:12px 15px;width:355px}'
'h2{font-size:15px;color:#7ec8ff}.m{display:block;font-size:11px;color:#8b93a7;font-weight:normal}'
'table{border-collapse:collapse;width:100%;font-size:12.3px}th{background:#1d2740;color:#9fb4d8;padding:3px 6px}td{padding:2px 6px;border-bottom:1px solid #1d2438;text-align:center}'
'tr.up td{color:#5cff8f}tr.dn td{color:#ff9d9d}td.th{color:#ffd35c;font-weight:bold}tr.g td{background:#1d2438;color:#9fb4d8;text-align:left;font-weight:bold;font-size:11.5px}'
'</style></head><body><div class="wrap"><h1>永恒6卡 vs 时刻8卡 · 29项全量（球员等级5+队套6）</h1>'
'<div class="note">数值=裸值+3+强化(6卡+8/8卡+15)+球员等级5(假设+4)+队套6；无优先级预筛、无观点。</div>'
+ ''.join(parts) + '</div></body></html>')
P = os.path.join(os.path.dirname(SP), '永恒6卡vs时刻8卡_29项全量_等级5队套6_20260727.html')
tmp = P + '.tmp'
open(tmp,'w',encoding='utf-8').write(html)
os.replace(tmp, P)
print('ok', P)
