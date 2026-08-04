# -*- coding: utf-8 -*-
"""永恒全位置拉通页：已定稿位置的分数+名次并排（当前=中锋(定稿)+边锋(已裁待锁)）
跨位置比较用名次口径（得分率因各位置权重表属性数不同不可直接比）。
新增位置：往 MODELS 里加一项(权重表+逆足系数)即可。"""
import json, os, itertools
SP = os.path.dirname(os.path.abspath(__file__))
full = json.load(open(os.path.join(SP, 'el_tm_attrs_full.json'), encoding='utf-8'))
el_list = json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']
stats = json.load(open(os.path.join(SP, 'el_stats.json'), encoding='utf-8'))
uid2 = {p['uid']: p['name'] for p in el_list}
wf = {uid2[u]: int(r['player']['foot_weak']) for u, r in stats.items() if u in uid2}
B = 28
PENS = {
 '中锋': {5: 1.0, 4: 0.90, 3: 0.75, 2: 0.65},
 '边锋': {5: 1.0, 4: 0.95, 3: 0.75, 2: 0.65},
 '前腰': {5: 1.0, 4: 0.95, 3: 0.75, 2: 0.65},
 '中场': {5: 1.0, 4: 0.95, 3: 0.85, 2: 0.75},
 '后腰': {5: 1.0, 4: 0.95, 3: 0.90, 2: 0.80},
}
MODELS = {
 '中锋': {5: ['sprintspeed', 'acceleration'],
          3: ['finishing', 'shotpower', 'curve', 'agility', 'ballcontrol', 'balance'],
          2: ['strength', 'reactions', 'longshots', 'headingaccuracy'],
          1: ['stamina', 'jumping', 'volleys', 'shortpassing', 'positioning', 'composure', 'dribbling'],
          0.5: ['vision', 'crossing']},
 '边锋': {5: ['sprintspeed', 'acceleration'],
          3: ['dribbling', 'ballcontrol', 'agility', 'balance', 'curve', 'crossing'],
          2: ['finishing', 'shotpower', 'longshots', 'reactions', 'longpassing', 'strength'],
          1: ['positioning', 'shortpassing', 'vision', 'stamina', 'composure', 'standingtackle'],
          0.5: ['headingaccuracy', 'jumping', 'interceptions', 'aggression', 'volleys']},
 '前腰': {3: ['shortpassing', 'vision', 'ballcontrol', 'dribbling', 'longshots', 'agility', 'curve', 'shotpower'],
          2: ['finishing', 'balance', 'reactions', 'strength', 'sprintspeed', 'acceleration'],
          1: ['positioning', 'composure', 'stamina', 'volleys', 'marking', 'standingtackle', 'interceptions'],
          0.5: ['headingaccuracy', 'jumping', 'aggression', 'crossing', 'longpassing']},
 '中场': {4: ['longshots', 'shotpower', 'shortpassing', 'ballcontrol', 'balance'],
          3: ['sprintspeed', 'acceleration', 'dribbling', 'agility', 'marking', 'standingtackle', 'interceptions', 'strength'],
          2: ['vision', 'stamina', 'reactions', 'curve', 'aggression', 'finishing'],
          1: ['longpassing', 'composure', 'positioning'],
          0.5: ['crossing', 'headingaccuracy', 'jumping', 'volleys', 'slidingtackle']},
 '后腰': {3: ['standingtackle', 'interceptions', 'marking', 'strength', 'balance', 'shortpassing', 'ballcontrol'],
          2: ['sprintspeed', 'acceleration', 'stamina', 'reactions', 'longshots', 'shotpower', 'dribbling', 'agility', 'longpassing'],
          1: ['vision', 'aggression', 'slidingtackle', 'curve', 'finishing', 'composure', 'positioning', 'headingaccuracy', 'jumping', 'volleys']},
}
OFFICIAL = {'中锋': ('ST', 'CF'), '边锋': ('LW', 'RW', 'LM', 'RM'), '前腰': ('CAM',), '中场': ('CM',), '后腰': ('CDM',)}
NAME_CN = {'Cristiano Ronaldo': 'C罗', 'L. Messi': '梅西', 'T. Henry': '亨利', 'Eusébio': '尤西比奥', 'Ronaldo': '大罗',
 'H. Sánchez': '桑切斯', 'A. Shevchenko': '舍瓦', "S. Eto'o": '埃托奥', 'Roberto Carlos': '卡洛斯', 'Ferenc Puskás': '普斯卡什',
 'W. Rooney': '鲁尼', 'L. Suárez': '苏亚雷斯', 'Z. Zidane': '齐达内', 'Z. Ibrahimović': '伊布', 'Fernando Torres': '托雷斯',
 'M. van Basten': '范巴斯滕', 'K. Benzema': '本泽马', 'R. van Persie': '范佩西', 'Kaká': '卡卡', 'Raúl': '劳尔',
 'D. Drogba': '德罗巴', 'B. Cha': '车范根', 'F. Lampard': '兰帕德', 'Y. Touré': '图雷', 'Gabriel Batistuta': '巴蒂',
 'Neymar Jr': '内马尔', 'S. Gerrard': '杰拉德', 'D. Beckham': '贝克汉姆', 'F. Totti': '托蒂', 'Marcelo': '马塞洛',
 'E. Cantona': '坎通纳', 'R. van Nistelrooy': '范尼', 'E. Hazard': '阿扎尔', 'A. Shearer': '希勒', 'F. Rijkaard': '里杰卡尔德',
 'R. Baggio': '巴乔', 'H. Son': '孙兴慜', 'P. Nedvěd': '内德维德', 'L. Thuram': '图拉姆', 'Xavi': '哈维',
 'T. Müller': '穆勒', 'P. Vieira': '维埃拉', 'M. Owen': '欧文', 'Roberto Firmino': '菲尔米诺', 'O. Giroud': '吉鲁',
 'Iniesta': '伊涅斯塔', 'T. Kroos': '克罗斯', 'B. Schweinsteiger': '小猪', 'Rivaldo': '里瓦尔多', 'J. Zanetti': '萨内蒂',
 'M. Essien': '埃辛', 'Casemiro': '卡塞米罗', 'E. Petit': '佩蒂特', 'Cesc Fàbregas': '法布雷加斯', 'Fernando Hierro': '耶罗',
 'R. Ferdinand': '费迪南德', 'F. Cannavaro': '卡纳瓦罗', 'A. Nesta': '内斯塔', 'N. Vidić': '维迪奇', 'Marquinhos': '马尔基尼奥斯',
 'G. Chiellini': '基耶利尼', 'Guti': '古蒂', 'L. Matthäus': '马特乌斯', 'A. Pirlo': '皮尔洛',
 'O. Solskjaer': '索尔斯克亚'}
def tier(v):
    # 07-28: 165档3分->4分
    return 4 if v >= 165 else 2 if v >= 155 else 1 if v >= 145 else 0
def best_patch(vals, W):
    items = []
    for k, v in vals.items():
        w = W.get(k, 0)
        if not w:
            continue
        for t in (145, 155, 165):
            if v < t <= v + 2:
                items.append((t - v, w * (2 if t == 165 else 1)))
                break
    best = 0
    for r in range(1, len(items) + 1):
        for comb in itertools.combinations(items, r):
            if sum(i[0] for i in comb) <= 5:
                best = max(best, sum(i[1] for i in comb))
    return best
def score(el, W, w5, pen):
    vals = {k: int(el['attr'][k]['value']) + B for k in W if k in el['attr']}
    base = sum(W[k] * tier(v) for k, v in vals.items())
    return (base + best_patch(vals, W)) * pen.get(w5, 1.0)
names = [p['name'] for p in el_list if p['pos1'] != 'GK']
posmap = {p['name']: p['pos1'] for p in el_list}
scores = {}
ranks = {}
for m, tiers_ in MODELS.items():
    W = {k: w for w, ks in tiers_.items() for k in ks}
    sc = {n: score(full[n]['EL'], W, wf.get(n, 5), PENS[m]) for n in names}
    order = sorted(names, key=lambda n: -sc[n])
    scores[m] = sc
    ranks[m] = {n: i + 1 for i, n in enumerate(order)}
mnames = list(MODELS)
rows = []
for n in names:
    best = min(ranks[m][n] for m in mnames)
    rows.append((n, best))
rows.sort(key=lambda r: r[1])
trs = ''
for n, best in rows:
    pos = posmap[n]
    cn = NAME_CN.get(n, n)
    cells = ''
    rks = {m: ranks[m][n] for m in mnames}
    fit = min(rks, key=lambda m: rks[m])
    srt = sorted(rks.values())
    if len(srt) > 1 and srt[1] - srt[0] <= 1:
        fit = '双修'
    for m in mnames:
        official = pos in OFFICIAL[m]
        style = 'style="color:#5cff8f;font-weight:bold"' if official else ''
        hot = ' style="background:#20304e"' if fit == m else ''
        cells += '<td %s>%.1f</td><td%s><b>#%d</b></td>' % (style, scores[m][n], hot, rks[m])
    fitcls = {'中锋': 'color:#ffd35c', '边锋': 'color:#7ec8ff', '前腰': 'color:#d69cff', '中场': 'color:#7effd4', '后腰': 'color:#ffab6e', '双修': 'color:#5cff8f'}.get(fit, 'color:#dde3ee')
    trs += ('<tr><td>%d</td><td class="nm">%s<span class="en">%s</span></td><td>%s</td><td>%d逆</td>%s<td style="%s;font-weight:bold">%s</td></tr>'
            % (best, cn, n, pos, wf.get(n, 5), cells, fitcls, fit))
html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>永恒全位置拉通 · 得分与名次</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0;line-height:1.55}'
'.wrap{max-width:1020px;margin:0 auto;padding:24px 14px 70px}'
'h1{color:#ffd35c;font-size:20px}'
'.note{color:#9aa3b8;font-size:12.8px;line-height:1.75;background:#151c2e;border-radius:8px;padding:12px 16px;margin-top:8px}'
'.note b{color:#ffd35c}'
'table{border-collapse:collapse;width:100%;font-size:12.8px;margin-top:12px}'
'th{background:#1d2740;color:#9fb4d8;padding:5px 8px;position:sticky;top:0;cursor:pointer}'
'td{padding:4px 8px;border-bottom:1px solid #1d2438;text-align:center}'
'td.nm{text-align:left;font-weight:bold;color:#fff;white-space:nowrap}'
'.en{display:block;font-weight:normal;color:#5c6579;font-size:10.5px}'
'</style></head><body><div class="wrap">'
'<h1>永恒全位置拉通 · 得分与名次（2026-07-27）</h1>'
'<div class="note">已接入位置：<b>中锋 + 边锋 + 前腰 + 中场 + 后腰（均已定稿）</b>，剩中卫（边后卫不做）。'
'两套权重表属性数不同（满分132 vs 145.5），<b>跨位置比较用名次不用得分率/绝对分</b>；'
'"更适合"=名次更靠前的位置（名次差≤1判双修）。绿色分数=该列是他的官方位置；底色高亮=他的最优位置列。'
'分数均含特训背包+逆足系数（按位置差异化：中锋4逆0.90/3逆0.75，边锋·前腰4逆0.95/3逆0.75，中场4逆0.95/3逆0.85）。点表头可排序。</div>'
'<table><tr><th>最佳名次</th><th>球员</th><th>官方位置</th><th>逆足</th>' + ''.join('<th>%s分</th><th>%s名次</th>' % (m, m) for m in mnames) + '<th>更适合</th></tr>'
+ trs + '</table>'
'<script>'
'function sortT(t,i,th){var rows=Array.prototype.slice.call(t.querySelectorAll("tr")).slice(1);'
'var dir=th.dataset.d==="a"?"d":"a";'
't.querySelectorAll("th").forEach(function(h){delete h.dataset.d;h.textContent=h.textContent.replace(/ [\\u25b2\\u25bc]$/,"")});'
'th.dataset.d=dir;th.textContent=th.textContent+(dir==="a"?" \\u25b2":" \\u25bc");'
'rows.sort(function(r1,r2){var a=(r1.cells[i]?r1.cells[i].innerText:"").trim(),b=(r2.cells[i]?r2.cells[i].innerText:"").trim();'
'var na=parseFloat(a.replace(/[^0-9.+\\-]/g,"")),nb=parseFloat(b.replace(/[^0-9.+\\-]/g,""));'
'var c=(!isNaN(na)&&!isNaN(nb))?na-nb:a.localeCompare(b,"zh");return dir==="a"?c:-c});'
'rows.forEach(function(r){t.appendChild(r)})}'
'document.querySelectorAll("table").forEach(function(t){t.querySelectorAll("tr:first-child th").forEach(function(th,i){'
'th.addEventListener("click",function(){sortT(t,i,th)})})});'
'</script></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\永恒全位置拉通_得分与名次_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html)
os.replace(tmp, P)
print('ok', P)
