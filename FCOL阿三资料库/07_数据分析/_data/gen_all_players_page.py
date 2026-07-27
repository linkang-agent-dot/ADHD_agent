# -*- coding: utf-8 -*-
"""66名永恒全量拉通页：有时刻同名卡=EL6卡vsTM8卡对比；无=EL6卡数值直列。口径：+3裸值校准+强化(EL6卡+8/TM8卡+15)+球员等级5(+4假设)+队套6"""
import json, os
SP = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(SP, 'el_tm_attrs_full.json'), encoding='utf-8'))
el_list = json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']
tm_ovr = {p['name']: int(p['pos1val']) for p in json.load(open(os.path.join(SP, 'tm_list.json'), encoding='utf-8'))['db']}
GRP = [('速度',['sprintspeed','acceleration']),('射门',['finishing','shotpower','longshots','positioning','volleys','penalties','curve','freekickaccuracy']),('传球',['shortpassing','vision','crossing','longpassing']),('盘带',['dribbling','ballcontrol','agility','balance','reactions']),('防守',['marking','standingtackle','interceptions','slidingtackle','aggression']),('身体',['strength','stamina','headingaccuracy','jumping','composure'])]
GKG = [('门将',['gkdiving','gkhandling','gkkicking','gkreflexes','gkpositioning'])]
CAL, ET, TT, LV, TC = 3, 8, 15, 4, 6
EB, TB = CAL+ET+LV+TC, CAL+TT+LV+TC
POSORD = {'GK':0,'CB':1,'LB':2,'RB':3,'CDM':4,'CM':5,'RM':6,'LM':7,'CAM':8,'LW':9,'RW':10,'CF':11,'ST':12}

def th_mark(v):
    for th in (165, 155, 145):
        if v >= th: return str(th) + '+'
    return ''

players = sorted(el_list, key=lambda p: (POSORD.get(p['pos1'], 99), -int(p['pos1val'])))
parts, miss = [], []
for p in players:
    name = p['name']
    rec = d.get(name, {})
    if 'EL' not in rec:
        miss.append(name); continue
    el = rec['EL']
    tm = rec.get('TM')
    groups = GKG if p['pos1'] == 'GK' else GRP
    secs = ''
    for gname, keys in groups:
        rows = ''
        for k in keys:
            if k not in el['attr']: continue
            nm = el['attr'][k]['name']
            e6 = int(el['attr'][k]['value']) + EB
            if tm and k in tm['attr']:
                t8 = int(tm['attr'][k]['value']) + TB
                note = ''
                for th in (165, 155, 145):
                    if e6 >= th > t8: note = '永恒独过%d' % th; break
                    if t8 >= th > e6: note = '时刻独过%d' % th; break
                cls = 'up' if e6 > t8 else ('dn' if t8 > e6 else '')
                rows += '<tr class="%s"><td>%s</td><td>%d</td><td>%d</td><td>%+d</td><td class="th">%s</td></tr>' % (cls, nm, t8, e6, e6-t8, note)
            else:
                rows += '<tr><td>%s</td><td class="solo" colspan="3">%d</td><td class="th">%s</td></tr>' % (nm, e6, th_mark(e6))
        secs += '<tr class="g"><td colspan="5">%s</td></tr>%s' % (gname, rows)
    if tm:
        head = '时刻8卡 vs 永恒6卡 ｜ 1强总评 %d→%d ｜ 薪资%s' % (tm_ovr.get(name, 0), int(p['pos1val']), el.get('salary', '?'))
        cols = '<tr><th>属性</th><th>时刻8卡</th><th>永恒6卡</th><th>Δ</th><th>阈值</th></tr>'
    else:
        head = '无时刻同名卡 ｜ 永恒6卡直列 ｜ 1强总评%d ｜ 薪资%s' % (int(p['pos1val']), el.get('salary', '?'))
        cols = '<tr><th>属性</th><th colspan="3">永恒6卡</th><th>阈值</th></tr>'
    parts.append('<div class="pl%s"><h2>%s <span class="pos">%s</span> <span class="m">%s</span></h2><table>%s%s</table></div>' % (
        ' solo' if not tm else '', name, p['pos1'], head, cols, secs))

html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>永恒66人拉通·vs时刻/6卡直列</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0}'
'.wrap{max-width:1180px;margin:0 auto;padding:20px;display:flex;flex-wrap:wrap;gap:16px}'
'h1{width:100%;color:#ffd35c;font-size:19px;margin-bottom:2px}.note{width:100%;color:#8b93a7;font-size:12.5px;line-height:1.6}'
'.pl{background:#171e2e;border:1px solid #263048;border-radius:10px;padding:12px 15px;width:355px}'
'.pl.solo{border-color:#3a3320}'
'h2{font-size:15px;color:#7ec8ff;margin:2px 0 6px}.pos{font-size:11px;background:#243154;border-radius:3px;padding:0 6px}'
'.m{display:block;font-size:11px;color:#8b93a7;font-weight:normal;margin-top:3px}'
'table{border-collapse:collapse;width:100%;font-size:12.3px}'
'th{background:#1d2740;color:#9fb4d8;padding:3px 6px}td{padding:2px 6px;border-bottom:1px solid #1d2438;text-align:center}'
'tr.up td{color:#5cff8f}tr.dn td{color:#ff9d9d}td.th{color:#ffd35c;font-weight:bold}td.solo{color:#dde3ee}'
'tr.g td{background:#1d2438;color:#9fb4d8;text-align:left;font-weight:bold;font-size:11.5px}'
'</style></head><body><div class="wrap">'
'<h1>传奇永恒 66 人拉通 · 有时刻同名卡=6卡vs8卡对比，无=6卡数值直列</h1>'
'<div class="note">口径：接口裸值+3(游戏显示校准) + 强化(永恒6卡+8 / 时刻8卡+15，梅西OVR曲线+埃托奥8卡148双实测) + 球员等级5(假设+4，待确证) + 队套加成+6。'
'按位置排序(GK→后场→中场→前场)，全29项游戏面板分组直列，无优先级预筛、无博主观点。绿=永恒高，红=时刻高，黄=阈值(145/155/165)差异或达标档。金边框=无时刻版直列卡。</div>'
+ ''.join(parts) + '</div></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\永恒66人拉通_vs时刻或6卡直列_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html)
os.replace(tmp, P)
print('page ok, missing:', miss)
