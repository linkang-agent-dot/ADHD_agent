# -*- coding: utf-8 -*-
"""球员×位置分矩阵 v2：全位置统一「加权阈上」制（同量纲），点行弹详情逐项拆解。"""
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
TH = 145
CNK = {'sprintspeed':'速度','acceleration':'加速','finishing':'射术','shotpower':'射门力量','longshots':'远射','positioning':'站位','volleys':'凌空','penalties':'点球','shortpassing':'短传','vision':'视野','crossing':'传中','longpassing':'长传','freekickaccuracy':'任意球','curve':'弧线','dribbling':'盘带','ballcontrol':'控球','agility':'灵活','balance':'平衡','reactions':'反应','marking':'人盯人','standingtackle':'抢断','interceptions':'拦截','headingaccuracy':'头球','slidingtackle':'铲断','strength':'强壮','stamina':'体力','aggression':'侵略性','jumping':'弹跳','composure':'冷静'}
# ===== 全位置统一加权阈上制：只有权重表不同（依据《全位置属性优先级梳理》）=====
W = {
 'st': {'sprintspeed':5,'acceleration':5,'finishing':3,'positioning':3,'reactions':3,
        'dribbling':2.5,'ballcontrol':2.5,'agility':2.5,'balance':2.5,
        'headingaccuracy':1.5,'strength':1.5,'jumping':1.5,'volleys':1.5,
        'shotpower':1,'longshots':1,'curve':1,'composure':1,
        'stamina':0.5,'shortpassing':0.5,'vision':0.5},
 'wg': {'sprintspeed':5,'acceleration':5,'dribbling':3,'ballcontrol':3,'agility':3,
        'balance':2.5,'reactions':2.5,'curve':2,'crossing':2,
        'finishing':1.5,'shotpower':1.5,'longshots':1.5,'shortpassing':1.5,'stamina':1.5,
        'composure':1,'vision':1,'volleys':1,
        'headingaccuracy':0.5,'strength':0.5},
 'cam': {'longshots':3.5,'shortpassing':3,'vision':3,'dribbling':3,'ballcontrol':3,
         'agility':2.5,'balance':2.5,'reactions':2.5,
         'finishing':2,'shotpower':2,'curve':2,'sprintspeed':2,'acceleration':2,
         'composure':1.5,'positioning':1.5,
         'strength':1,'longpassing':1,
         'headingaccuracy':0.5,'stamina':0.5},
 'cm': {'shortpassing':3,'vision':3,'longpassing':3,'ballcontrol':3,'dribbling':2.5,
        'reactions':2.5,'sprintspeed':2,'acceleration':2,'stamina':2,'balance':2,
        'composure':1.5,'standingtackle':1.5,'interceptions':1.5,'strength':1.5,
        'longshots':1,'marking':1,'agility':1},
 'cdm': {'standingtackle':3.5,'interceptions':3.5,'marking':3,'strength':2.5,'stamina':2.5,
         'sprintspeed':2,'acceleration':2,'reactions':2,'shortpassing':2,
         'aggression':1.5,'slidingtackle':1.5,'headingaccuracy':1.5,'longpassing':1.5,'ballcontrol':1.5,
         'dribbling':1,'longshots':1,'balance':1},
 'cb': {'sprintspeed':4,'acceleration':4,'standingtackle':3.5,'marking':3,'interceptions':3,
        'strength':2.5,'headingaccuracy':2.5,'reactions':2.5,
        'agility':2,'balance':2,'jumping':2,
        'aggression':1.5,'slidingtackle':1.5,
        'shortpassing':0.5,'composure':0.5},
 'fb': {'sprintspeed':4.5,'acceleration':4.5,'standingtackle':3,'interceptions':3,'marking':2.5,
        'crossing':2.5,'stamina':2.5,'reactions':2,'agility':2,
        'strength':1.5,'slidingtackle':1.5,'balance':1.5,
        'shortpassing':1,'dribbling':1,'headingaccuracy':1,'jumping':1},
}
COLCN = {'st':'中锋','wg':'边锋','cam':'前腰','cm':'中场','cdm':'后腰','cb':'中卫','fb':'边卫'}
VETO_NOTE = {'Y. Touré': '−指挥官', 'Z. Ibrahimović': '+11kg'}
WGPOS = ('LW','RW','LM','RM')
def gv(el, k):
    return int(el['attr'][k]['value']) + B if k in el['attr'] else 0
def score(el, w):
    return sum(wt * max(0, gv(el, k) - TH) for k, wt in w.items()) / sum(w.values())
rows = []
for p in el_list:
    n = p['name']
    if p['pos1'] == 'GK':
        continue
    el = full[n]['EL']; sal = int(el['salary'])
    w5 = wf.get(n, 0); flair = sk.get(n, 0)
    warn = []
    if w5 <= 3: warn.append(str(w5) + '逆')
    elif w5 == 4: warn.append('4逆')
    if flair and flair <= 3: warn.append('花' + str(flair))
    if n in VETO_NOTE: warn.append(VETO_NOTE[n])
    attrs_disp = {k: gv(el, k) for k in CNK if k in el['attr']}
    r = {'n': n, 'p1': p['pos1'], 'p2': p.get('pos2') or '', 'sal': sal, 'wf': w5, 'fl': flair,
         'a': attrs_disp, 'warn': '/'.join(warn),
         'bst': int(p['pos1'] in ('ST','CF') or p.get('pos2') in ('ST','CF')),
         'bwg': int(p['pos1'] in WGPOS or p.get('pos2') in WGPOS),
         'bcam': int(p['pos1'] == 'CAM' or p.get('pos2') == 'CAM'),
         'bcm': int(p['pos1'] == 'CM' or p.get('pos2') == 'CM'),
         'bcdm': int(p['pos1'] == 'CDM' or p.get('pos2') == 'CDM'),
         'bcb': int(p['pos1'] == 'CB' or p.get('pos2') == 'CB'),
         'bfb': int(p['pos1'] in ('LB','RB') or p.get('pos2') in ('LB','RB'))}
    for c, w in W.items():
        r[c] = round(score(el, w), 1)
    rows.append(r)
DATA = json.dumps(rows, ensure_ascii=False)
CFG = json.dumps({'W': W, 'CNK': CNK, 'COLCN': COLCN, 'TH': TH}, ensure_ascii=False)
def wlist(d):
    return '，'.join('%s×%g' % (CNK[k], v) for k, v in sorted(d.items(), key=lambda x: -x[1]))
CALC = ''.join(
    '<b>%s分</b>（Σ权重=%g）：%s。<br><br>' % (COLCN[c], sum(w.values()), wlist(w))
    for c, w in W.items())
CALC_DOC = (
'<h2 style="color:#ffd35c;font-size:15px;margin-top:30px">框架分计算说明</h2>'
'<div class="note">'
'<b>统一公式（全位置同构，中锋模板推广）</b>：分 = Σ[位置权重 × max(0, 属性显示值 − 145)] ÷ Σ权重。<br>'
'即：只统计145阈值线以上的部分，加权平均。全列同量纲，可跨位置比较。<br>'
'属性显示值 = fifaaddict裸值 + 3(游戏显示校准) + 15(8卡强化,双实测) + 4(球员等级5,假设待确证) + 6(队套) = 裸值+28。<br><br>'
+ CALC +
'<b>警示列（不进分数的天生项）</b>：逆足（中锋4逆=拉完/边锋要双五/前腰54可用/中场后腰54起步/中卫最宽松）、花式≤3星、已知个案（图雷−中场指挥官、伊布+11kg）。<br>'
'<b>已知局限</b>：球员等级+4为假设；特性/动作模组/模型手感不进公式；边锋「能省则省」原则请结合工资列自行取舍（低3-4薪、分低10%以内的边锋=更优解）。'
'</div>')
html_head = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>永恒65人x全位置 框架分矩阵v2</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0;line-height:1.55}'
'.wrap{max-width:1220px;margin:0 auto;padding:22px 14px 70px}'
'h1{color:#ffd35c;font-size:19px}'
'.note{color:#8b93a7;font-size:12.3px;line-height:1.7}'
'table{border-collapse:collapse;width:100%;font-size:12.4px;margin-top:10px}'
'th{background:#1d2740;color:#9fb4d8;padding:5px 7px;cursor:pointer;user-select:none;position:sticky;top:0}'
'th:hover{background:#2a3a5e}'
'td{padding:3px 7px;border-bottom:1px solid #1d2438;text-align:center}'
'td.nm{text-align:left;font-weight:bold;color:#fff;white-space:nowrap;cursor:pointer}'
'td.off{font-weight:bold;color:#5cff8f}'
'td.w{color:#ff9d9d;font-size:11.3px}'
'#modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:50;align-items:flex-start;justify-content:center;overflow:auto;padding:30px 10px}'
'.mbox{background:#161d2d;border:1px solid #33436b;border-radius:12px;max-width:900px;width:100%;padding:16px 20px;position:relative}'
'.mbox h3{color:#ffd35c;margin:2px 0 10px;font-size:16px}'
'#mclose{position:absolute;top:10px;right:14px;cursor:pointer;color:#8b93a7;font-size:18px}'
'.sec{background:#1c2438;border-radius:8px;padding:8px 12px;margin:8px 0;font-size:12.3px;line-height:1.8}'
'.sec b{color:#7ec8ff}'
'.grid{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}'
'.it{background:#0f1420;border-radius:4px;padding:1px 7px;font-size:11.6px;color:#aab3c7}'
'.it.g{color:#5cff8f}.it.y{color:#ffd35c}.it i{font-style:normal;font-size:10px;opacity:.75}'
'.g{color:#5cff8f}.r{color:#ff9d9d}'
'</style></head><body><div class="wrap">'
'<h1>永恒 65 人 × 全位置框架分矩阵 v2（统一加权阈上制 · 点列头排序 · 点球员看逐项计算）</h1>'
'<div class="note">全位置统一公式=Σ权重×max(0,属性−145)÷Σ权重（中锋模板推广，全列同量纲可跨位置比较）。'
'<b style="color:#5cff8f">绿色加粗</b>=官方定位。完整权重表见页底。警示列=天生否决项（不进分数，按位置自行过闸）。</div>'
'<table id="t"><thead><tr>'
'<th data-k="n">球员</th><th data-k="p1">定位</th><th data-k="sal">薪</th><th data-k="wf">逆足</th><th data-k="fl">花式</th>'
'<th data-k="st">中锋</th><th data-k="wg">边锋</th><th data-k="cam">前腰</th><th data-k="cm">中场</th><th data-k="cdm">后腰</th><th data-k="cb">中卫</th><th data-k="fb">边卫</th>'
'<th data-k="warn">警示</th></tr></thead><tbody></tbody></table>'
+ CALC_DOC +
'</div>'
'<div id="modal"><div class="mbox"><span id="mclose">✕</span><div id="mbody"></div></div></div>'
'<script>')
js = ('const D=' + DATA + ';const C=' + CFG + ';'
'let key="st",asc=false;'
'const COLS=["st","wg","cam","cm","cdm","cb","fb"];'
'const BOLD={st:"bst",wg:"bwg",cam:"bcam",cm:"bcm",cdm:"bcdm",cb:"bcb",fb:"bfb"};'
'function render(){'
'const tb=document.querySelector("#t tbody");tb.innerHTML="";'
'const s=[...D].sort((a,b)=>{const x=a[key],y=b[key];if(typeof x=="string")return asc?String(x).localeCompare(y):String(y).localeCompare(x);return asc?x-y:y-x;});'
's.forEach(r=>{'
'const tr=document.createElement("tr");'
'let h="<td class=nm>"+r.n+"</td><td>"+r.p1+(r.p2?"/"+r.p2:"")+"</td><td>"+r.sal+"</td><td>"+r.wf+"</td><td>"+r.fl+"</td>";'
'COLS.forEach(c=>{h+="<td class=\\""+(r[BOLD[c]]?"off":"")+"\\">"+r[c].toFixed(1)+"</td>";});'
'h+="<td class=w>"+r.warn+"</td>";'
'tr.innerHTML=h;tr.style.cursor="pointer";'
'tr.addEventListener("click",()=>showDetail(r));'
'tb.appendChild(tr);});}'
'function nm(k){return C.CNK[k]||k;}'
'function mark(v){return v>=165?"165+":v>=155?"155+":v>=145?"145+":v>=135?"135+":"";}'
'function showDetail(r){'
'const a=r.a;'
'let h="<h3>"+r.n+"（"+r.p1+(r.p2?"/"+r.p2:"")+"｜薪"+r.sal+"｜逆足"+r.wf+"｜花式"+r.fl+(r.warn?"｜警示:"+r.warn:"")+"）</h3>";'
'h+="<div class=sec><b>全属性（裸值+28口径）</b><div class=grid>";'
'Object.keys(C.CNK).forEach(k=>{if(a[k]===undefined)return;const v=a[k];'
'h+="<span class=\\"it "+(v>=155?"g":v>=145?"y":"")+"\\">"+nm(k)+" "+v+" <i>"+mark(v)+"</i></span>";});'
'h+="</div></div>";'
'COLS.forEach(c=>{'
'const w=C.W[c];let ws=0,tot=0,parts=[];'
'for(const k in w){const wt=w[k];ws+=wt;const v=a[k]||0;const ct=wt*Math.max(0,v-C.TH);'
'if(ct>0)parts.push([nm(k)+"("+v+")",wt,ct]);tot+=ct;}'
'parts.sort((x,y)=>y[2]-x[2]);'
'const zero=Object.keys(w).filter(k=>(a[k]||0)<C.TH).map(k=>nm(k)+"("+(a[k]||0)+")");'
'h+="<div class=sec><b>"+C.COLCN[c]+"分 = 加权阈上合计"+tot.toFixed(1)+" ÷ Σ权重"+ws+" = "+(tot/ws).toFixed(2)+"</b><br>"'
'+parts.map(p=>p[0]+"×"+p[1]+"→+"+p[2].toFixed(1)).join("， ")'
'+(zero.length?"<br>零贡献(未过145)：<span class=r>"+zero.join("、")+"</span>":"")+"</div>";'
'});'
'document.getElementById("mbody").innerHTML=h;'
'document.getElementById("modal").style.display="flex";}'
'document.getElementById("modal").addEventListener("click",e=>{if(e.target.id=="modal")document.getElementById("modal").style.display="none";});'
'document.getElementById("mclose").addEventListener("click",()=>document.getElementById("modal").style.display="none");'
'document.querySelectorAll("#t th").forEach(th=>th.addEventListener("click",()=>{const k=th.dataset.k;if(key==k)asc=!asc;else{key=k;asc=false;}render();}));'
'render();'
'</script></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\永恒65人x全位置_框架分矩阵_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html_head + js)
os.replace(tmp, P)
print('ok', P)
# 控制台各列Top5
for c in W:
    rs = sorted(rows, key=lambda r: -r[c])[:5]
    print(COLCN[c], 'Top5:', ', '.join('%s %.1f' % (r['n'], r[c]) for r in rs))
