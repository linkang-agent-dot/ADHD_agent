# -*- coding: utf-8 -*-
"""永恒中锋评价·定稿版页面
公式(用户逐档裁定,2026-07-27):
  终分 = [Σ(属性档位分×档位权重) + 最优特训增益] × 逆足系数
  档位分: 显示值>=165→4(07-28上调) / >=155→2 / >=145→1 / <145→0
  权重: 双速x5 | 射术·射门力量·弧线·灵活·控球·平衡x3 | 强壮·反应·远射·头球x2
        | 体力·弹跳·凌空·短传·站位·冷静·盘带x1 | 传中·视野x0.5 | 其余x0
  特训: 全卡+5点/单项<=2点, 背包求最大档位增益
  逆足: 5逆x1.0 / 4逆x0.90 / 3逆x0.75（07-27按位置差异化）
  口径: 接口裸值 +3显示 +8卡强化15 +球员等级4(假设待确证) +队套6 = +28
全员(68人非门将)都算中锋分, >=80进榜; 身高体重模型仅参考不计分。
"""
import json, os, itertools
SP = os.path.dirname(os.path.abspath(__file__))
full = json.load(open(os.path.join(SP, 'el_tm_attrs_full.json'), encoding='utf-8'))
el_list = json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']
stats = json.load(open(os.path.join(SP, 'el_stats.json'), encoding='utf-8'))
uid2 = {p['uid']: p['name'] for p in el_list}
info = {}
for u, r in stats.items():
    if u in uid2:
        pl = r['player']
        info[uid2[u]] = (int(pl['foot_weak']), pl['height'], pl['weight'], pl.get('bodytype_name', ''))
B = 28
TIERS = {5: ['sprintspeed', 'acceleration'],
         3: ['finishing', 'shotpower', 'curve', 'agility', 'ballcontrol', 'balance'],
         2: ['strength', 'reactions', 'longshots', 'headingaccuracy'],
         1: ['stamina', 'jumping', 'volleys', 'shortpassing', 'positioning', 'composure', 'dribbling'],
         0.5: ['vision', 'crossing']}
W = {k: w for w, ks in TIERS.items() for k in ks}
MAXS = sum(W.values()) * 4
CN = {'sprintspeed': '速度', 'acceleration': '加速', 'finishing': '射术', 'shotpower': '射门力量', 'longshots': '远射',
      'positioning': '站位', 'volleys': '凌空', 'shortpassing': '短传', 'vision': '视野', 'curve': '弧线',
      'dribbling': '盘带', 'ballcontrol': '控球', 'agility': '灵活', 'balance': '平衡', 'reactions': '反应',
      'headingaccuracy': '头球', 'strength': '强壮', 'stamina': '体力', 'jumping': '弹跳', 'composure': '冷静', 'crossing': '传中'}
CN0 = {'longpassing': '长传', 'freekickaccuracy': '任意球', 'penalties': '点球', 'marking': '人盯人',
       'standingtackle': '抢断', 'interceptions': '拦截', 'slidingtackle': '铲断', 'aggression': '侵略性'}
CN_ALL = {**CN, **CN0}
NAME_CN = {'Cristiano Ronaldo': 'C罗', 'L. Messi': '梅西', 'T. Henry': '亨利', 'Eusébio': '尤西比奥', 'Ronaldo': '大罗',
 'H. Sánchez': '桑切斯', 'A. Shevchenko': '舍瓦', "S. Eto'o": '埃托奥', 'Roberto Carlos': '卡洛斯', 'Ferenc Puskás': '普斯卡什',
 'W. Rooney': '鲁尼', 'L. Suárez': '苏亚雷斯', 'Z. Zidane': '齐达内', 'Z. Ibrahimović': '伊布', 'Fernando Torres': '托雷斯',
 'M. van Basten': '范巴斯滕', 'K. Benzema': '本泽马', 'R. van Persie': '范佩西', 'Kaká': '卡卡', 'Raúl': '劳尔',
 'D. Drogba': '德罗巴', 'B. Cha': '车范根', 'F. Lampard': '兰帕德', 'Y. Touré': '图雷', 'Gabriel Batistuta': '巴蒂',
 'Neymar Jr': '内马尔', 'S. Gerrard': '杰拉德', 'D. Beckham': '贝克汉姆', 'F. Totti': '托蒂', 'Marcelo': '马塞洛',
 'E. Cantona': '坎通纳', 'R. van Nistelrooy': '范尼', 'E. Hazard': '阿扎尔', 'A. Shearer': '希勒', 'F. Rijkaard': '里杰卡尔德',
 'R. Baggio': '巴乔', 'H. Son': '孙兴慜', 'P. Nedvěd': '内德维德', 'L. Thuram': '图拉姆', 'Xavi': '哈维',
 'T. Müller': '穆勒', 'P. Vieira': '维埃拉', 'M. Owen': '欧文', 'Roberto Firmino': '菲尔米诺', 'O. Giroud': '吉鲁',
 'L. Matthäus': '马特乌斯', 'A. Pirlo': '皮尔洛', 'O. Solskjaer': '索尔斯克亚'}
COMMENT = {
 'C罗': '没弱点，闭眼用。12项三档全场最多，唯一0档是短传',
 '梅西': '客串中锋全场第二——速度手感全满，但169cm/67kg瘦小模型没身体，数值行模型不行',
 '亨利': '又快又稳没人追得上，但188cm挂瘦小模型：有身高没对抗',
 '尤西比奥': '亨利平替，各项都齐，买到即巅峰',
 '大罗': '快+会带球，正面拿他没办法；中场指挥官手感在公式外，实战上限比名次高',
 '桑切斯': '小快灵全能，速度164特训1点解锁双速165',
 '舍瓦': '快+会抢点，就干中锋的活；一堆属性卡线，特训+10精确治愈，冲7逻辑成立',
 '埃托奥': '成品卡：属性全在档位正中，特训+0.5全场最低，买来就是这样不会更好',
 '卡洛斯': '后卫客串中锋比一半正牌强，168cm健硕小钢炮，速度射门强壮全有',
 '普斯卡什': '技术流古典前锋，特训+12能解锁双速165，但只有4逆(已扣5%)',
 '鲁尼': '啥都会啥都不顶尖，阵容缺哪补哪，当不了核心',
 '苏亚雷斯': '鲁尼偏射手版，射术弧线平衡三档',
 '齐达内': '大个子技术流客串支点',
 '伊布': '站桩支点，禁区里强跑不动；195cm/95kg全场最大架子，但体重被官方+了11kg，转身有隐性惩罚',
 '托雷斯': '直线快马功能单一，特训后双速满档',
 '范巴斯滕': '教科书终结者就干最后一下，双速平庸',
 '本泽马': '全场最平的分布，没有短板也没有记忆点',
 '范佩西': '阵地战射手（射术弧线控球凌空三档），反击用不上他',
 '卡卡': '前腰客串支点，速度带球都在线',
 '劳尔': '哪都不差哪都不尖，"劳尔悖论"的数值实体',
 '德罗巴': '重型支点，档位分布配不上身价人设；特训+12练前练后两张卡',
 '车范根': '极端速度单核：双速100%但技术56%宽度48%，跑得到拿不稳',
 '索尔斯克亚': '34薪双五情怀卡：特训后仍仅79分，双速无165且强壮不过145，低于主力线',
 '马特乌斯': '中场客串，仅作全能数值参考；主场看中场/后腰榜',
 '皮尔洛': '组织型中场客串，双速与对抗不足，不建议真打中锋',
 '兰帕德': '中场客串支点意外能看，89kg大体格',
 '图雷': '数值能客串中锋，但-中场指挥官特性=手感笨(公式外老坑)',
 '巴蒂': '固定炮台：重炮三件套三档全场对抗组并列第一，双速拖后腿',
 '内马尔': '边锋客串，瘦小模型',
 '杰拉德': '中场客串支点，远射包在中锋公式里贬值',
 '贝克汉姆': '4逆已扣5%，客串仅参考',
 '托蒂': '技术底子在，档位强度不够的名气卡',
 '马塞洛': '边卫客串，速度手感型',
 '坎通纳': '四组均匀但全不高，低配版鲁尼',
 '范尼': '"全员163"体质：16项挤在157-164差一口气，三档仅3项+4逆。信165阈值论就绕开，不信就是被系统性低估',
 '阿扎尔': '边锋客串，手感组扎实',
 '希勒': '上世纪炮台，双速33%追不上现版本防线；特训+16全场最大但练完也中游',
 '里杰卡尔德': '后腰客串，对抗组高',
 '巴乔': '优雅但全面偏软，冷静是唯一三档',
 '孙兴慜': '正职左边锋，客串中锋88.5及格线上，等边锋算法才是主场',
 '内德维德': '前腰客串，远射红利在中锋公式里用不上',
 '图拉姆': '中卫客串到86分，速度对抗双全',
 '哈维': '170cm传球大师客串中锋纯属数值巧合，别真用',
 '穆勒': '空间阅读者跑不到自己算出来的空间：宽度71%全场前列vs双速33%',
 '维埃拉': '192cm瘦小竹竿，客串仅参考',
 '欧文': '这张卡官方就没给速度(162/163)，速度人设是别的赛季的印象；零三档+强壮139+4逆',
 '菲尔米诺': '工兵型伪九号，对抗组17%零三档，数值模型无处安放',
 '吉鲁': '全模型唯一双速交白卷(145不到)的中锋，纯桥头堡',
}
def tier(v):
    # 07-28: 165档3分->4分(145/155不变)
    return 4 if v >= 165 else 2 if v >= 155 else 1 if v >= 145 else 0
def best_patch(vals):
    items = []
    for k, v in vals.items():
        w = W.get(k, 0)
        if not w:
            continue
        for th in (145, 155, 165):
            if v < th <= v + 2:
                items.append((th - v, w * (2 if th == 165 else 1), CN[k], th))
                break
    best = (0, [])
    for r in range(1, len(items) + 1):
        for comb in itertools.combinations(items, r):
            if sum(i[0] for i in comb) <= 5:
                g = sum(i[1] for i in comb)
                if g > best[0]:
                    best = (g, list(comb))
    return best
PEN = {5: 1.0, 4: 0.90, 3: 0.75, 2: 0.65}
rows = []
detail = {}
for p in el_list:
    n = p['name']
    if p['pos1'] == 'GK':
        continue
    el = full[n]['EL']
    vals = {k: int(el['attr'][k]['value']) + B for k in W if k in el['attr']}
    base = sum(W[k] * tier(v) for k, v in vals.items())
    g, alloc = best_patch(vals)
    w5, h, wt, bt = info.get(n, (5, 0, 0, ''))
    fin = (base + g) * PEN.get(w5, 1.0)
    plan = '+'.join('%s%d点→%d' % (cn, c, th) for c, w, cn, th in alloc)
    rows.append((n, p['pos1'], w5, base, g, fin, fin / MAXS * 100, h, wt, bt, plan, int(el['salary'])))
    trained = {cn2: th2 for c2, w2, cn2, th2 in alloc}
    items = []
    for k in list(W) + list(CN0):
        if k not in el['attr']:
            continue
        v = int(el['attr'][k]['value']) + B
        w = W.get(k, 0)
        tv = trained.get(CN_ALL[k], 0)
        items.append([CN_ALL[k], v, tier(v), w, round(w * tier(v), 1), tv, tier(tv) if tv else 0])
    items.sort(key=lambda x: (-x[3], -x[4], -x[1]))
    detail[NAME_CN.get(n, n)] = {'items': items, 'base': base, 'gain': g, 'plan': plan or '无可训项',
                                 'w5': w5, 'pen': PEN.get(w5, 1.0), 'fin': round(fin, 1),
                                 'phy': '%dcm / %dkg / %s' % (h, wt, bt)}
# 工资定价线：只用28名正牌中锋拟合 终分~工资，残差=同工资档超出/欠了多少分
_st = [(r[11], r[5]) for r in rows if r[1] in ('ST', 'CF')]
_N = len(_st)
_sx = sum(s for s, f in _st); _sy = sum(f for s, f in _st)
_sxx = sum(s * s for s, f in _st); _sxy = sum(s * f for s, f in _st)
SLOPE = (_N * _sxy - _sx * _sy) / (_N * _sxx - _sx * _sx)
INTC = (_sy - SLOPE * _sx) / _N
rows.sort(key=lambda r: -r[5])
trs = ''
for i, (n, pos, w5, base, g, fin, pct, h, wt, bt, plan, sal) in enumerate(rows, 1):
    if fin < 80 and pos not in ('ST', 'CF'):
        continue
    cn = NAME_CN.get(n, n)
    cross = '' if pos in ('ST', 'CF') else ' cross'
    low = ' low' if fin < 80 else ''
    res = fin - (INTC + SLOPE * sal)
    rcls = 'style="color:#5cff8f;font-weight:bold"' if res >= 7 else ('style="color:#ff7b7b;font-weight:bold"' if res <= -7 else 'style="color:#8b93a7"')
    trs += ('<tr class="r%s%s" onclick="pop(\'%s\')"><td>%d</td><td class="nm">%s<span class="en">%s</span></td><td>%s</td><td>%d逆</td>'
            '<td class="sc">%.1f</td><td>%.0f%%</td><td>%.1f<span class="tg">+%.1f</span></td>'
            '<td>%d</td><td %s>%+.1f</td>'
            '<td class="ph">%dcm/%dkg·%s</td><td class="pl">%s</td><td class="cm">%s</td></tr>'
            % (cross, low, cn, i, cn, n, pos, w5, fin, pct, base, g, sal, rcls, res, h, wt, bt, plan or '—', COMMENT.get(cn, '')))
# ===== vs 时刻 模块（与主榜同三档制145/155/165，两卡同权重同特训同逆足；含时刻独有卡） =====
TH4 = (145, 155, 165)  # 07-27用户裁定:时刻计分与永恒一致,135档作废
TMONLY_CN = {'Pelé': '贝利', 'D. Maradona': '马拉多纳', 'F. Beckenbauer': '贝肯鲍尔', 'J. Cruyff': '克鲁伊夫',
 'G. Müller': '盖德·穆勒', 'L. Matthäus': '马特乌斯', 'Garrincha': '加林查', 'Ronaldinho': '小罗',
 'Jairzinho': '雅伊尔济尼奥', 'P. Maldini': '马尔蒂尼', 'Zico': '济科', 'F. Baresi': '巴雷西', 'R. Gullit': '古利特',
 'G. Best': '乔治·贝斯特', 'B. Charlton': '博比·查尔顿', 'Cafu': '卡福', 'D. Bergkamp': '博格坎普',
 'Luís Figo': '菲戈', 'A. Pirlo': '皮尔洛', 'M. Ballack': '巴拉克', 'Carlos Alberto': '卡洛斯·阿尔贝托',
 'R. Koeman': '科曼', 'I. Rush': '拉什', 'A. Del Piero': '皮耶罗', 'P. Lahm': '拉姆', 'Xabi Alonso': '哈维·阿隆索',
 'K. Dalglish': '达格利什', 'P. Scholes': '斯科尔斯', 'M. Klose': '克洛泽', 'C. Puyol': '普约尔',
 'B. Moore': '博比·摩尔', 'Dunga': '邓加', 'C. Seedorf': '西多夫', 'C. Makélélé': '马克莱莱',
 'D. Trezeguet': '特雷泽盖', 'Park Ji Sung': '朴智星', 'R. Keane': '罗伊·基恩', 'M. Desailly': '德塞利',
 'H. Stoichkov': '斯托伊奇科夫', 'H. Crespo': '克雷斯波', 'F. Ribéry': '里贝里', 'G. Hagi': '哈吉',
 'Butragueño': '布特拉格诺', 'G. Lineker': '莱因克尔', 'M. Laudrup': '大劳德鲁普', 'L. Blanc': '布兰克',
 'G. Bale': '贝尔', 'G. Zambrotta': '赞布罗塔'}
def tier4(v):
    n = sum(1 for t in TH4 if v >= t)
    return 4 if n == 3 else n
def best_patch4(vals):
    items = []
    for k, v in vals.items():
        w = W.get(k, 0)
        if not w:
            continue
        for t in TH4:
            if v < t <= v + 2:
                items.append((t - v, w * (2 if t == 165 else 1), CN_ALL.get(k, k), t))
                break
    best = (0, [])
    for r in range(1, len(items) + 1):
        for comb in itertools.combinations(items, r):
            if sum(i[0] for i in comb) <= 5:
                g = sum(i[1] for i in comb)
                if g > best[0]:
                    best = (g, list(comb))
    return best
def score4(attrs, Bx, w5):
    vals = {k: int(attrs[k]['value']) + Bx for k in W if k in attrs}
    base = sum(W[k] * tier4(v) for k, v in vals.items())
    g, alloc = best_patch4(vals)
    return (base + g) * PEN.get(w5, 1.0), base, g, alloc, vals
def tm_detail(attrs, Bx):
    its = []
    for k in list(W) + [k2 for k2 in CN_ALL if k2 not in W]:
        if k not in attrs:
            continue
        v = int(attrs[k]['value']) + Bx
        w = W.get(k, 0)
        its.append([CN_ALL[k], v, tier4(v), w, round(w * tier4(v), 1)])
    its.sort(key=lambda x: (-x[3], -x[4], -x[1]))
    return its
tm_rows = []
dtl = {}
for p in el_list:
    n = p['name']
    rec = full[n]
    if not rec.get('TM') or p['pos1'] == 'GK':
        continue
    w5 = info.get(n, (5, 0, 0, ''))[0]
    t8, tb, tg, talloc, _ = score4(rec['TM']['attr'], 28, w5)
    e6 = score4(rec['EL']['attr'], 21, w5)[0]   # 永恒6卡=+3+8+4+6
    e8 = score4(rec['EL']['attr'], 28, w5)[0]
    tsal = int(rec['TM'].get('salary') or 0)
    esal = int(rec['EL']['salary'])
    cnm = NAME_CN.get(n, n)
    tm_rows.append((n, cnm, p['pos1'], t8, e6, e8, e8 - t8, tsal, esal, w5))
    dtl[cnm] = {'items': tm_detail(rec['TM']['attr'], 28), 'base': tb, 'gain': tg,
                'plan': '+'.join('%s%d点→%d' % (c2, c1, t2) for c1, w2, c2, t2 in talloc) or '无可训项',
                'w5': w5, 'pen': PEN.get(w5, 1.0), 'fin': round(t8, 1),
                'phy': '%scm / %skg' % (rec['TM'].get('height', '?'), rec['TM'].get('weight', '?'))}
TMONLY_PATH = os.path.join(SP, 'tm_only_attrs.json')
if os.path.exists(TMONLY_PATH):
    for n, rec in json.load(open(TMONLY_PATH, encoding='utf-8')).items():
        if rec.get('pos1') == 'GK':
            continue
        w5 = int(rec.get('db', {}).get('foot_weak') or 5)
        t8, tb, tg, talloc, _ = score4(rec['attr'], 28, w5)
        tsal = int(rec.get('salary') or 0)
        cnm = TMONLY_CN.get(n, n)
        tm_rows.append((n, cnm, rec.get('pos1', '?'), t8, None, None, None, tsal, None, w5))
        dtl[cnm] = {'items': tm_detail(rec['attr'], 28), 'base': tb, 'gain': tg,
                    'plan': '+'.join('%s%d点→%d' % (c2, c1, t2) for c1, w2, c2, t2 in talloc) or '无可训项',
                    'w5': w5, 'pen': PEN.get(w5, 1.0), 'fin': round(t8, 1),
                    'phy': '%scm / %skg · 时刻独有(无永恒版)' % (rec.get('height', '?'), rec.get('weight', '?'))}
tm_rows.sort(key=lambda r: -r[3])
tm_trs = ''
for i, (n, cn, pos, t8, e6, e8, d, tsal, esal, w5) in enumerate(tm_rows, 1):
    tq = t8 / tsal if tsal else 0
    if e8 is None:
        tm_trs += ('<tr class="tmo" onclick="popT(\'%s\')"><td>%d</td><td class="nm">%s<span class="en">%s</span></td><td>%s</td>'
                   '<td>%.1f</td><td>%d</td><td>%.2f</td>'
                   '<td>—</td><td>—</td><td>—</td><td>—</td><td style="color:#8b93a7">无永恒</td></tr>'
                   % (cn, i, cn, n, pos, t8, tsal, tq))
        continue
    dcls = ' style="color:#ff7b7b;font-weight:bold"' if d < 35 else (' style="color:#5cff8f"' if d >= 50 else '')
    eq = e8 / esal if esal else 0
    qcls = ' style="color:#5cff8f;font-weight:bold"' if tq > eq else ''
    tm_trs += ('<tr onclick="popT(\'%s\')"><td>%d</td><td class="nm">%s<span class="en">%s</span></td><td>%s</td>'
               '<td>%.1f</td><td>%d</td><td%s>%.2f</td>'
               '<td>%.1f</td><td>%.1f</td><td>%d</td><td>%.2f</td><td%s>%+.1f</td></tr>'
               % (cn, i, cn, n, pos, t8, tsal, qcls, tq, e6, e8, esal, eq, dcls, d))
html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>永恒中锋评价·定稿版</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0;line-height:1.55}'
'.wrap{max-width:1240px;margin:0 auto;padding:24px 14px 70px}'
'h1{color:#ffd35c;font-size:20px}h2{color:#7ec8ff;font-size:15px;margin-top:24px}'
'.note{color:#9aa3b8;font-size:12.8px;line-height:1.75;background:#151c2e;border-radius:8px;padding:12px 16px}'
'.note b{color:#ffd35c}'
'table{border-collapse:collapse;width:100%;font-size:12.4px;margin-top:10px}'
'th{background:#1d2740;color:#9fb4d8;padding:5px 7px;position:sticky;top:0}'
'td{padding:4px 7px;border-bottom:1px solid #1d2438;text-align:center}'
'td.nm{text-align:left;font-weight:bold;color:#fff;white-space:nowrap}'
'.en{display:block;font-weight:normal;color:#5c6579;font-size:10.5px}'
'td.sc{color:#5cff8f;font-weight:bold;font-size:13.5px}'
'td.cm{text-align:left;color:#c9d2e4;font-size:12px;max-width:330px}'
'td.pl{text-align:left;color:#8b93a7;font-size:11px;max-width:200px}'
'td.ph{color:#9aa3b8;font-size:11.5px;white-space:nowrap}'
'.tg{color:#ffd35c;font-size:10.5px;margin-left:3px}'
'tr.cross td.nm{color:#7ec8ff}'
'tr.low td{opacity:.55}'
'tbody tr{cursor:pointer}tbody tr:hover td{background:#1a2540}'
'#ov{display:none;position:fixed;inset:0;background:rgba(5,8,16,.82);z-index:50}'
'#md{position:fixed;top:4vh;left:50%;transform:translateX(-50%);width:min(680px,94vw);max-height:90vh;overflow-y:auto;'
'background:#141b2d;border:1px solid #2a3555;border-radius:10px;padding:18px 22px;z-index:51}'
'#md h3{color:#ffd35c;margin:0 0 4px;font-size:17px}'
'#md .sub{color:#8b93a7;font-size:12px;margin-bottom:10px}'
'#md table{font-size:12.3px}#md td,#md th{padding:2px 8px}'
'#md .t3{color:#5cff8f;font-weight:bold}#md .t4{color:#4dffc6;font-weight:bold}#md .t2{color:#dde3ee}#md .t1{color:#c9a44a}#md .t0{color:#ff7b7b}'
'tr.tmo td.nm{color:#e8b4ff}'
'#md .w0{opacity:.45}'
'#md .sum{margin-top:10px;background:#1d2740;border-radius:7px;padding:9px 13px;font-size:13px;line-height:1.9}'
'#md .sum b{color:#5cff8f}'
'#md .x{position:sticky;top:0;float:right;color:#8b93a7;cursor:pointer;font-size:20px;line-height:1}'
'</style></head><body><div class="wrap">'
'<h1>永恒中锋评价 · 定稿版（2026-07-27，用户逐档裁定权重）</h1>'
'<div class="note"><b>终分 = [ Σ(属性档位分 × 档位权重) + 最优特训增益 ] × 逆足系数</b><br>'
'档位分：显示值≥165→<b>4</b>（07-28上调） / ≥155→2 / ≥145→1 / ＜145→0（阈值机制：突破档位才算数，档内堆点无效）<br>'
'权重：<b>双速×5</b>（占比22.7%）｜<b>射术·射门力量·弧线·灵活·控球·平衡×3</b>（40.9%）｜<b>强壮·反应·远射·头球×2</b>（18.2%）｜'
'<b>体力·弹跳·凌空·短传·站位·冷静·盘带×1</b>（15.9%）｜<b>传中·视野×0.5</b>（2.3%）｜其余×0<br>'
'特训：全卡共+5点、单项≤2点，按背包求最大档位增益（卡在143-144/153-154/163-164的属性可被推过线）<br>'
'逆足：5逆×1.0 / 4逆×0.90 / 3逆×0.75（07-27调）　｜　口径：接口裸值+3显示+8卡强化15+<b>球员等级4(假设待游戏内确证)</b>+队套6<br>'
'得分率=终分÷满分176（07-28档位上调后）。<b>全员68人(非门将)都算中锋分，≥80进榜</b>；蓝名=非中锋客串（仅数值参考，无准入门槛）；'
'灰行=不足80的正牌中锋（明确别当中锋买）。身高/体重/模型仅参考不计分。<br>'
'<b>工资残差</b>=终分 − 市场定价线（用28名正牌中锋拟合 终分≈' + '%.0f+%.1f×工资' % (INTC, SLOPE) + '，1点工资≈%.1f分）' % SLOPE + '——'
'同工资档下超出/欠了多少分：<span style="color:#5cff8f">绿≥+7超模</span> / <span style="color:#ff7b7b">红≤−7工资坑</span>。'
'非中锋行的残差是"按中锋定价看"仅参考。</div>'
'<table><tr><th>#</th><th>球员</th><th>官方位置</th><th>逆足</th><th>终分</th><th>得分率</th><th>原分+特训</th><th>薪</th><th>工资残差</th><th>身材/模型</th><th>最优特训方案</th><th>评语</th></tr>'
+ trs + '</table>'
'<h2>模型层备注</h2><div class="note">'
'公式外因素（买前自查）：①特性——大罗+中场指挥官封神/图雷-指挥官手感笨/渗透者需高AI，特性是可投资项；'
'②体重造假——伊布被官方+11kg（唯一物理劣化）；③模型手感——梅西169瘦小打中锋数值行模型不行；'
'④范尼问题——"全员163"体质是阈值制最大受害者，信不信165阈值论决定他被低估还是被如实定价。</div>'
'<h2>vs 时刻：同名卡对比 + 时刻独有卡（按时刻8卡分排名）</h2>'
'<div class="note">口径：两边同用中锋权重+特训+逆足；档位与主榜一致（145/155/165=1/2/3，'
'07-27起时刻计分与永恒统一，<b>本表分数与主榜同量纲可直接比</b>）。永恒6卡=强化+8口径（现实持有状态）。<br>'
'<b>加减(永恒8卡−时刻8卡)读法：加减小=溢价大=避雷（花永恒的钱买不到提升）；加减大=永恒真升级。</b>'
'红=加减&lt;35（智商税区：欧文+20.9全场最小/巴乔/车范根）；绿=加减≥50（换代刀刃：亨利+52/马塞洛+59/兰帕德+57/图雷+55.5，'
'中场组整体+49~57——时刻中场是重灾区，永恒换代收益最高的是中场）。'
'紫名行=<b>时刻独有</b>（贝利/马拉多纳/克鲁伊夫等51人无永恒版，永恒列显—）。<b>全表可点击</b>：点任意行弹出该时刻卡29项属性的档位/权重/得分清单+特训方案+逆足算式。</div>'
'<table><tr><th>#</th><th>球员</th><th>官方位置</th><th>时刻8卡</th><th>时刻薪</th><th>时刻每薪</th><th>永恒6卡</th><th>永恒8卡</th><th>永恒薪</th><th>永恒每薪</th><th>加减</th></tr>'
+ tm_trs + '</table>'
'<div class="note" style="margin-top:6px">每薪=该卡8卡分÷自己的工资（与主榜同量纲）。<b>时刻薪普遍低3-5点</b>，'
'绿色=时刻每薪&gt;永恒每薪（工资效率上时刻更划算——预算/工资帽紧时的参考）。</div>'
'</div>'
'<div id="ov" onclick="hide()"></div><div id="md" style="display:none"></div>'
'<script>var D=' + json.dumps(detail, ensure_ascii=False) + ';\n'
'function hide(){document.getElementById("ov").style.display="none";document.getElementById("md").style.display="none"}\n'
'function pop(n){var d=D[n];if(!d)return;var h="<span class=x onclick=hide()>&times;</span><h3>"+n+" · 中锋分算分清单</h3>"\n'
'+"<div class=sub>"+d.phy+"　|　"+d.w5+"逆足</div>"\n'
'+"<table><tr><th>属性</th><th>显示值</th><th>档位</th><th>权重</th><th>得分</th></tr>";\n'
'for(var i=0;i<d.items.length;i++){var it=d.items[i];\n'
'var tv=it[5]||0,tt=it[6]||0;var tc=tv?tt:it[2];\n'
'var vx=tv?(it[1]+"→<b>"+tv+"</b>"):it[1];var dx=tv?(it[2]+"档→<b>"+tt+"档</b>"):(it[2]+"档");\n'
'h+="<tr class=\'"+(it[3]?"":"w0")+"\'><td>"+it[0]+(tv?" <span style=\'color:#ffd35c;font-size:10px\'>[特训]</span>":"")+"</td><td class=t"+tc+">"+vx+"</td><td class=t"+tc+">"+dx+"</td><td>"+(it[3]?"×"+it[3]:"×0")+"</td><td class=t"+tc+">"+(it[3]?it[4]:"—")+"</td></tr>";}\n'
'h+="</table><div class=sum>基础分 <b>"+d.base.toFixed(1)+"</b>　＋　特训 <b>+"+d.gain.toFixed(1)+"</b>（"+d.plan+"）<br>"\n'
'+"× 逆足系数 <b>"+d.pen+"</b>（"+d.w5+"逆）　＝　终分 <b>"+d.fin+"</b></div>";\n'
'var m=document.getElementById("md");m.innerHTML=h;m.style.display="block";document.getElementById("ov").style.display="block"}\n'
'var DT=' + json.dumps(dtl, ensure_ascii=False) + ';\n'
'function popT(n){var d=DT[n];if(!d)return;var h="<span class=x onclick=hide()>&times;</span><h3>"+n+" · 时刻8卡属性清单（145/155/165三档制，与主榜同口径）</h3>"\n'
'+"<div class=sub>"+d.phy+"　|　"+d.w5+"逆足</div>"\n'
'+"<table><tr><th>属性</th><th>显示值</th><th>档位</th><th>权重</th><th>得分</th></tr>";\n'
'for(var i=0;i<d.items.length;i++){var it=d.items[i];var tc=Math.min(it[2],4);\n'
'h+="<tr class=\'"+(it[3]?"":"w0")+"\'><td>"+it[0]+"</td><td class=t"+tc+">"+it[1]+"</td><td class=t"+tc+">"+it[2]+"档</td><td>"+(it[3]?"×"+it[3]:"×0")+"</td><td class=t"+tc+">"+(it[3]?it[4]:"—")+"</td></tr>";}\n'
'h+="</table><div class=sum>基础分 <b>"+d.base.toFixed(1)+"</b>　＋　特训 <b>+"+d.gain.toFixed(1)+"</b>（"+d.plan+"）<br>"\n'
'+"× 逆足系数 <b>"+d.pen+"</b>（"+d.w5+"逆）　＝　时刻分 <b>"+d.fin+"</b></div>";\n'
'var m=document.getElementById("md");m.innerHTML=h;m.style.display="block";document.getElementById("ov").style.display="block"}\n'
'document.addEventListener("keydown",function(e){if(e.key==="Escape")hide()});\n'
'function sortT(t,i,th){var rows=Array.prototype.slice.call(t.querySelectorAll("tr")).slice(1);'
'var dir=th.dataset.d==="a"?"d":"a";'
't.querySelectorAll("th").forEach(function(h){delete h.dataset.d;h.textContent=h.textContent.replace(/ [\\u25b2\\u25bc]$/,"")});'
'th.dataset.d=dir;th.textContent=th.textContent+(dir==="a"?" \\u25b2":" \\u25bc");'
'rows.sort(function(r1,r2){var a=(r1.cells[i]?r1.cells[i].innerText:"").trim(),b=(r2.cells[i]?r2.cells[i].innerText:"").trim();'
'var na=parseFloat(a.replace(/[^0-9.+\\-]/g,"")),nb=parseFloat(b.replace(/[^0-9.+\\-]/g,""));'
'var c=(!isNaN(na)&&!isNaN(nb))?na-nb:a.localeCompare(b,"zh");return dir==="a"?c:-c});'
'rows.forEach(function(r){t.appendChild(r)})}\n'
'document.querySelectorAll(".wrap table").forEach(function(t){t.querySelectorAll("tr:first-child th").forEach(function(th,i){'
'th.style.cursor="pointer";th.title="\\u70b9\\u51fb\\u6392\\u5e8f";th.addEventListener("click",function(){sortT(t,i,th)})})});\n'
'</script></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\永恒中锋评价_定稿版_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html)
os.replace(tmp, P)
print('ok', P)
