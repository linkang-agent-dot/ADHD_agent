# -*- coding: utf-8 -*-
"""永恒评价体系·全位置框架定稿版页面（分位置分算法+否决闸+观点对照）"""
import json, os
SP = os.path.dirname(os.path.abspath(__file__))
full = json.load(open(os.path.join(SP, 'el_tm_attrs_full.json'), encoding='utf-8'))
el_list = json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']
stats = json.load(open(os.path.join(SP, 'el_stats.json'), encoding='utf-8'))
uid2 = {p['uid']: p['name'] for p in el_list}
wf, sk = {}, {}
for uid, rec in stats.items():
    n = uid2.get(uid)
    if n:
        wf[n] = int(rec['player']['foot_weak'])
        sk[n] = int(rec['player'].get('skill_level') or 0)
B = 3 + 15 + 4 + 6
def v(el, k):
    return int(el['attr'][k]['value']) + B if k in el['attr'] else 0
ST_W = {'sprintspeed':5,'acceleration':5,'finishing':3,'positioning':3,'reactions':3,'dribbling':2.5,'ballcontrol':2.5,'agility':2.5,'balance':2.5,'headingaccuracy':1.5,'strength':1.5,'jumping':1.5,'volleys':1.5,'shotpower':1,'longshots':1,'curve':1,'composure':1,'stamina':0.5,'shortpassing':0.5,'vision':0.5}
CAM_145 = ['sprintspeed','acceleration','finishing','shotpower','positioning','shortpassing','vision','curve','dribbling','ballcontrol','agility','balance','reactions','strength','composure']
WG_145 = ['sprintspeed','acceleration','shotpower','longshots','curve','shortpassing','crossing','dribbling','ballcontrol','agility','balance','reactions','stamina','composure']
WG_135 = ['finishing','volleys','positioning','vision','headingaccuracy','strength','jumping']
MID_ALL = ['sprintspeed','acceleration','finishing','shotpower','longshots','positioning','shortpassing','vision','crossing','longpassing','curve','dribbling','ballcontrol','agility','balance','reactions','marking','standingtackle','interceptions','headingaccuracy','slidingtackle','strength','stamina','aggression','jumping','composure']
CB_W = {'sprintspeed':4,'acceleration':4,'standingtackle':3.5,'marking':3,'interceptions':3,'strength':2.5,'headingaccuracy':2.5,'reactions':2.5,'agility':2,'balance':2,'jumping':2,'aggression':1.5,'slidingtackle':1.5}
CB_CORE = ['sprintspeed','acceleration','standingtackle','marking','interceptions','agility','balance','headingaccuracy']
FB_145 = ['sprintspeed','acceleration','marking','standingtackle','interceptions','crossing','stamina','strength','reactions','agility']
VETO_NOTE = {'Y. Touré': '−中场指挥官(特性手术)', 'Z. Ibrahimović': '体重+11kg(物理劣化)'}
OPIN = {'Cristiano Ronaldo':'五神','Ronaldo':'五神·返神','Eusébio':'四神','T. Henry':'五神',"S. Eto'o":'五神·T0手感','Ferenc Puskás':'瓦五神/A胖4逆冲突','E. Hazard':'双神·新特性红利','M. Reus':'被低估双源','L. Messi':'四神·盘带流(模型/网速否决)','Z. Zidane':'五神','Kaká':'双神升档','P. Nedvěd':'四神·夯爆','F. Rijkaard':'四神·优先级>维埃拉','P. Vieira':'三神','L. Thuram':'六轮验证收敛','A. Nesta':'2:1看多','B. Schweinsteiger':'手感顶但市场溢价','Y. Touré':'带货溢价','Raúl':'手感三源否决','Z. Ibrahimović':'双源笨/吃延迟','W. Rooney':'瓦四神/A胖NPC分歧','Roberto Carlos':'五神第一张'}
G_ST = '中锋 ST/CF | 阈上军备(双速x5)'
G_WG = '边锋 LW/RW/RM | 145达标覆盖(不奖励超额)+省钱系数'
G_CAM = '前腰 CAM | 远射155重奖+145覆盖'
G_MID = '中场/后腰 CM/CDM | 破阈覆盖度'
G_CB = '中卫 CB | 双速加权阈上+核心短板惩罚'
G_FB = '边后卫 LB/RB | 达标覆盖+低薪加分(工资洼地)'
G_GK = '门将 | 数值不排位(ID模组>身高>特性>数值)'
res = {}
for p in el_list:
    n = p['name']; pos = p['pos1']
    if pos == 'GK':
        res.setdefault(G_GK, []).append((n, 0, 34, '', '瓦坎达/Reus高薪派 vs 阿三5薪派分歧'))
        continue
    el = full[n]['EL']; sal = int(el['salary'])
    w5 = wf.get(n, 0); flair = sk.get(n, 0)
    veto = []
    if pos in ('ST', 'CF'):
        if w5 <= 3: veto.append('3逆PASS')
        elif w5 == 4: veto.append('4逆=拉完')
        sc = sum(wt * max(0, v(el, k) - 145) for k, wt in ST_W.items()) / sum(ST_W.values())
        grp = G_ST
    elif pos in ('LW', 'RW', 'LM', 'RM'):
        if w5 <= 4: veto.append(str(w5) + '逆(双五需求全场第一)')
        if flair and flair <= 3: veto.append('花式' + str(flair) + '星')
        c145 = sum(1 for k in WG_145 if v(el, k) >= 145)
        c135 = sum(1 for k in WG_135 if v(el, k) >= 135)
        sc = c145 + 0.3 * c135 - 0.15 * (sal - 31)
        grp = G_WG
    elif pos == 'CAM':
        if w5 <= 3: veto.append('3逆PASS')
        c145 = sum(1 for k in CAM_145 if v(el, k) >= 145)
        sc = c145 + 3 * (v(el, 'longshots') >= 155) + 0.5 * sum(1 for k in CAM_145 if v(el, k) >= 155)
        grp = G_CAM
    elif pos in ('CM', 'CDM'):
        c145 = sum(1 for k in MID_ALL if v(el, k) >= 145)
        c155 = sum(1 for k in MID_ALL if v(el, k) >= 155)
        sc = c145 + 0.5 * c155
        grp = G_MID
    elif pos == 'CB':
        sc = sum(wt * max(0, v(el, k) - 145) for k, wt in CB_W.items()) / sum(CB_W.values())
        pen = sum(max(0, 145 - v(el, k)) for k in CB_CORE)
        sc -= 0.5 * pen
        if pen: veto.append('短板惩罚-%.1f' % (0.5 * pen))
        grp = G_CB
    else:
        c145 = sum(1 for k in FB_145 if v(el, k) >= 145)
        sc = c145 - 0.2 * (sal - 34)
        grp = G_FB
    if n in VETO_NOTE: veto.append(VETO_NOTE[n])
    res.setdefault(grp, []).append((n, sc, sal, '；'.join(veto), OPIN.get(n, '')))
secs = ''
for grp in [G_ST, G_WG, G_CAM, G_MID, G_CB, G_FB, G_GK]:
    lst = sorted(res.get(grp, []), key=lambda x: -x[1])
    trs = ''
    for i, (n, sc, sal, veto, op) in enumerate(lst, 1):
        hl = ' class="hl"' if i <= 3 and grp != G_GK else ''
        trs += ('<tr%s><td>%d</td><td class="nm">%s</td><td>%s</td><td>%.1f</td><td class="v">%s</td><td class="o">%s</td></tr>'
                % (hl, i, n, sal, sc, veto, op))
    secs += ('<h2>%s</h2><table><tr><th>#</th><th>球员</th><th>薪</th><th>框架分</th><th>天生否决/警示</th><th>观点层对照</th></tr>%s</table>'
             % (grp, trs))
note = ('依据《全位置属性优先级梳理》：不同位置使用不同算法。口径=裸值+3+8卡15+球员等级5(+4假设)+队套6。'
'天生否决项(逆足按位置差异化/体重/花式)单独过闸不进分数；特性=可投资项仅标注特殊案例。'
'观点层对照列=与职业选手评级的吻合/冲突——本版为历次迭代中与观点层吻合度最高。'
'已知可商榷点：卡洛斯空中白送包未计入边卫达标清单；梅西边锋达标制垫底=「边锋超额数值是浪费溢价」的框架表达。')
html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>永恒评价体系·全位置框架定稿版</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0;line-height:1.6}'
'.wrap{max-width:1060px;margin:0 auto;padding:24px 16px 70px}'
'h1{color:#ffd35c;font-size:20px}h2{color:#7ec8ff;font-size:14.5px;margin-top:26px;border-left:4px solid #7ec8ff;padding-left:9px}'
'.note{color:#8b93a7;font-size:12.5px;line-height:1.7}'
'table{border-collapse:collapse;width:100%;font-size:12.6px;margin-top:6px}'
'th{background:#1d2740;color:#9fb4d8;padding:4px 8px}td{padding:3px 8px;border-bottom:1px solid #1d2438;text-align:center}'
'td.nm{text-align:left;font-weight:bold;color:#fff}td.v{color:#ff9d9d;font-size:11.5px}td.o{color:#8b93a7;font-size:11.5px}'
'tr.hl td{background:#20304e}'
'</style></head><body><div class="wrap">'
'<h1>永恒卡评价体系 · 全位置框架定稿版（2026-07-27）</h1>'
'<div class="note">' + note + '</div>' + secs + '</div></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\永恒评价体系_全位置框架定稿版_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html)
os.replace(tmp, P)
print('ok', P)
