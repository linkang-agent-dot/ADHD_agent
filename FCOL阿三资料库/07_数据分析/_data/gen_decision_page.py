# -*- coding: utf-8 -*-
"""时刻8卡vs永恒6卡 换代决策页生成器（①ID固有印象→②刀刃属性→③结论）"""
import json, os
SP = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(SP, 'el_tm_attrs.json'), encoding='utf-8'))
el_list = {p['name']: int(p['pos1val']) for p in json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']}
tm_list = {p['name']: int(p['pos1val']) for p in json.load(open(os.path.join(SP, 'tm_list.json'), encoding='utf-8'))['db']}
CN = {'A. Shevchenko':'舍甫琴科','Z. Ibrahimović':'伊布','Roberto Carlos':'卡洛斯','B. Schweinsteiger':'小猪','T. Kroos':'克罗斯','A. Nesta':'内斯塔','Ronaldo':'大罗',"S. Eto'o":'埃托奥','Y. Touré':'亚亚图雷','R. van Nistelrooy':'范尼','T. Henry':'亨利','Raúl':'劳尔'}
# 分层按阿三《选人标准·中锋篇》原文：核心155+ / 重要145+ / 次要135+；版本项=2026-07头球加强版单列
PRI = {
 'ST': {'核心':['sprintspeed','acceleration','finishing','longshots','curve','reactions'],
        '重要':['shotpower','positioning','dribbling','ballcontrol','agility','balance','composure'],
        '版本':['headingaccuracy','strength','stamina','volleys','jumping'],
        '次要':['shortpassing','vision','crossing']},
 'CM': {'核心':['shortpassing','vision','longshots','dribbling','ballcontrol','reactions'],
        '重要':['longpassing','agility','balance','stamina','composure','sprintspeed'],
        '版本':['headingaccuracy','strength'],
        '次要':['finishing','shotpower','marking','standingtackle','interceptions']},
 'CB': {'核心':['sprintspeed','acceleration','marking','standingtackle','interceptions','strength','headingaccuracy'],
        '重要':['reactions','jumping','aggression','balance'],
        '版本':['slidingtackle'],
        '次要':['shortpassing','stamina','ballcontrol','composure']},
 'LB': {'核心':['sprintspeed','acceleration','marking','standingtackle','interceptions','crossing'],
        '重要':['stamina','strength','reactions','agility'],
        '版本':['headingaccuracy','jumping'],
        '次要':['shortpassing','dribbling','curve']},
}
POS = {'A. Shevchenko':'ST','Z. Ibrahimović':'ST','Ronaldo':'ST',"S. Eto'o":'ST','R. van Nistelrooy':'ST','T. Henry':'ST','Raúl':'ST','B. Schweinsteiger':'CM','T. Kroos':'CM','Y. Touré':'CM','A. Nesta':'CB','Roberto Carlos':'LB'}
# 每人: (时刻印象[观点], 永恒印象[观点], 数据面结论[仅数值可证], 观点面结论[标注出处], 谁驱动判断)
IMP = {
 'Ronaldo': ('时刻~10兆时代标杆', '永恒五神(瓦坎达)·返神(观点)', '核心145→148(+3.0)，0项跨145(时刻8卡核心已过145)；＋中场指挥官特性', '瓦坎达五神/职业第一手；阿三6卡165推演', '数据+观点同向'),
 'T. Henry': ('时刻公认强(口碑)', '永恒五神(瓦坎达)', '核心145→148(+3.7)，0项跨145；非核心白送传中+22/视野+20', '瓦坎达五神；阿三7卡165', '数据+观点同向'),
 "S. Eto'o": ('时刻“可以买”(Reus·观点)', '永恒五神(瓦坎达)·T0手感(多博主·观点)', '核心差全场最小+2.2，0项跨145——时刻8卡与永恒6卡数值几乎无差', '各源一致好评', '数据驱动：平替结论纯数值可证'),
 'A. Shevchenko': ('时刻口碑平稳(观点)', '永恒四神(瓦坎达)·夯(Reus)', '3项跨145(双速/弧线)；头球+16定向补强', '两职业选手一致好评', '数据+观点同向'),
 'R. van Nistelrooy': ('固有印象一般(观点)', '瓦坎达“极其一般”·A胖“4逆拉完”(均为观点)', '4项跨145(全场最大)；逆足4星(客观事实)', 'A胖4逆铁律、瓦坎达不推——注意：4逆致命是经验判断非本次数据可证', '观点驱动：数据红利被逆足经验法则否决'),
 'Raúl': ('时刻平庸(观点)', '三源劝退(观点)', '2项跨145；全属性差额+0.8但超额集中在体力/任意球/长传(对ST权重低)', '拉完了/不好用均为手感评价', '数据+观点同向(数据解释了观点)'),
 'Z. Ibrahimović': ('重心高(A胖·观点)', '单神(瓦坎达·观点)', '体重+11kg(客观·12人唯一)；核心0定向补强；−体力回复特性', '剧笨/吃延迟为手感评价', '数据+观点同向'),
 'Y. Touré': ('时刻8卡“夯”(Reus·观点)', '永恒“有点笨”(瓦坎达·观点)', '−中场指挥官特性(客观)；2项跨145；市价3500兆vs评级(带货抬价有玩家实锤)', '夯vs笨两观点冲突', '数据仲裁：特性删减+溢价支持瓦坎达侧'),
 'B. Schweinsteiger': ('WG版口碑好(观点)', '手感顶级但溢价(瓦坎达·观点)', '2项跨145；1500兆/132能力值(价格客观)', '“WG可替代”为观点', '观点驱动(替代关系未做数值对比)'),
 'T. Kroos': ('户口豪华(客观)', '“尴尬”(瓦坎达·观点)', '组织3项跨145(客观利好)；射门系两代均未达145(客观)', '替代多为观点', '数据驱动：半张卡升级是数值结论'),
 'A. Nesta': ('万年老二(阿三·观点)', '“完全不是一个人”(瓦坎达·观点)', '站位+17定向补强；双速过档', '看多为观点(2:1)', '数据+观点同向，但“捡漏”依赖观点扩散'),
 'Roberto Carlos': ('时刻强(观点)', '五神第一张(瓦坎达·观点)', '2项跨145；头球+27/弹跳+18/凌空+16白送包(客观)；全属性差额+1.4全场第一', '纯怪物为观点', '数据+观点同向'),
}
CAL, E6, T8 = 3, 6+6, 15+6  # 口径v3: 永恒5卡(+6)+队套6 vs 时刻8卡(+15)+队套6
parts = []
order = ['R. van Nistelrooy','A. Nesta',"S. Eto'o",'Y. Touré','A. Shevchenko','Roberto Carlos','Ronaldo','T. Henry','T. Kroos','B. Schweinsteiger','Z. Ibrahimović','Raúl']
for name in order:
    v = d[name]; el, tm = v['EL'], v['TM']
    pos = POS[name]
    cross = [0]
    def tierrows(tier):
        rows = ''
        for k in PRI[pos][tier]:
            if k not in el['attr'] or k not in tm['attr']: continue
            nm = el['attr'][k]['name']
            t8 = int(tm['attr'][k]['value']) + CAL + T8
            e6 = int(el['attr'][k]['value']) + CAL + E6
            note = ''
            for th in (165, 155, 145):
                if e6 >= th > t8:
                    note = '跨' + str(th)
                    if tier in ('核心', '重要'): cross[0] += 1
                    break
                if t8 >= th > e6:
                    note = '倒挂' + str(th); break
            cls = 'up' if e6 > t8 else ('dn' if t8 > e6 else '')
            rows += '<tr class="%s"><td>%s</td><td>%d</td><td>%d</td><td>%+d</td><td class="th">%s</td></tr>' % (cls, nm, t8, e6, e6-t8, note)
        return rows
    trs_core, trs_imp2, trs_ver = tierrows('核心'), tierrows('重要'), tierrows('版本')
    def tiermean(tier):
        vals = [(int(tm['attr'][k]['value'])+CAL+T8, int(el['attr'][k]['value'])+CAL+E6) for k in PRI[pos][tier] if k in el['attr'] and k in tm['attr']]
        a = sum(x for x, _ in vals)/len(vals); b = sum(y for _, y in vals)/len(vals)
        return '%.0f→%.0f(%+.1f)' % (a, b, b-a)
    imp = IMP[name]
    parts.append('''<div class="pl"><h2>%s <span class="pos">%s</span> <span class="m">时刻8卡 vs 永恒5卡(含队套+6) ｜ 1强总评 %d→%d ｜ 核心+重要跨145项：%d</span></h2>
<div class="imp"><b>①ID/固有印象(观点层)</b>：时刻—%s；永恒—%s</div>
<table><tr><th>核心155+(刀刃)</th><th>时刻8卡+队套</th><th>永恒5卡+队套</th><th>Δ</th><th>阈值</th></tr>%s</table>
<table><tr><th>重要145+</th><th>时刻8卡+队套</th><th>永恒5卡+队套</th><th>Δ</th><th>阈值</th></tr>%s</table>
<table><tr><th>版本项(头球加强版)</th><th>时刻8卡+队套</th><th>永恒5卡+队套</th><th>Δ</th><th>阈值</th></tr>%s</table>
<div class="tier">次要层均值 %s</div>
<div class="ver"><b>③数据面</b>：%s<br><b>观点面</b>：%s<br><b>判定驱动</b>：%s</div></div>''' % (
        CN[name], pos, tm_list[name], el_list[name], cross[0], imp[0], imp[1],
        trs_core, trs_imp2, trs_ver, tiermean('次要'), imp[2], imp[3], imp[4]))
html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>时刻8卡 vs 永恒5卡(含队套+6)·换代决策页</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0}'
'.wrap{max-width:1180px;margin:0 auto;padding:20px;display:flex;flex-wrap:wrap;gap:16px}'
'h1{width:100%;color:#ffd35c;font-size:20px;margin-bottom:2px}.note{width:100%;color:#8b93a7;font-size:12.5px;line-height:1.6}'
'.pl{background:#171e2e;border:1px solid #263048;border-radius:10px;padding:12px 15px;width:360px}'
'h2{font-size:16px;color:#7ec8ff;margin:2px 0 6px}.pos{font-size:11px;background:#243154;border-radius:3px;padding:0 6px}'
'.m{display:block;font-size:11px;color:#8b93a7;font-weight:normal;margin-top:3px}'
'.imp{font-size:12px;color:#c9d3e8;background:#1d2438;border-radius:6px;padding:6px 8px;margin:6px 0;line-height:1.5}'
'table{border-collapse:collapse;width:100%;font-size:12.5px}'
'th{background:#1d2740;color:#9fb4d8;padding:3px 6px}td{padding:2px 6px;border-bottom:1px solid #1d2438;text-align:center}'
'tr.up td{color:#5cff8f}tr.dn td{color:#ff9d9d}td.th{color:#ffd35c;font-weight:bold}'
'.tier{font-size:11.5px;color:#8b93a7;margin:6px 0}'
'.ver{font-size:12.5px;color:#ffd35c;background:#221c10;border-radius:6px;padding:6px 8px;line-height:1.5}'
'</style></head><body><div class="wrap">'
'<h1>时刻8卡 vs 永恒5卡(含队套+6) · 换代决策页（①ID固有印象 → ②刀刃属性 → ③结论）</h1>'
'<div class="note">口径：游戏内显示值（详情裸值+3），永恒=5卡+6/时刻=8卡+15，两边另加队套+6(阈值看绝对值)（强化曲线经梅西OVR+埃托奥8卡148双实测校准；集训/战术训练加成未含）。刀刃分层按阿三《属性全解》+《选人标准》：核心须155+（裸卡靠加成堆）、重要须145+、次要135+。<b>此口径下主战场在155线：全场唯一批量155差异=大罗(五项核心155 vs 时刻154)+图雷强壮；「155红利」需永恒7卡起兑现。</b>③数据面文字为6卡口径快照，阈值以表格黄标为准。排序按决策戏剧性。</div>'
+ ''.join(parts) + '</div></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\时刻8卡vs永恒6卡_换代决策页_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html)
os.replace(tmp, P)
print('ok', P)
