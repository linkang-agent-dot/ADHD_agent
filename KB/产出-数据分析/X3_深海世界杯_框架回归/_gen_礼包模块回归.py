# -*- coding: utf-8 -*-
"""
X3 深海节 尾部礼包模块回归 · 独立报告生成器（一页合并·中等深度）
覆盖 4 模块：每日礼包(102993) / 节日周卡(109101) / 拜访礼包(105605) / 装饰阶梯(106103)
数据源 = _l1_m4.json(深海59服主口径) + _gift_drill.json(逐档/漏斗/口径校正) + _daily_clean.json(每日礼包去首充污染)
壳 = 复刻 _gen_深海转盘回归.py 的 tap4fun 线性壳。深海 7/16 收官=数据终版不再变。
用法: python _gen_礼包模块回归.py
"""
import sys, json, os, datetime
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
L  = json.load(open(os.path.join(HERE, '_l1_m4.json'), encoding='utf-8'))
G  = json.load(open(os.path.join(HERE, '_gift_drill.json'), encoding='utf-8'))
DC = json.load(open(os.path.join(HERE, '_daily_clean.json'), encoding='utf-8'))
LAD = json.load(open(os.path.join(HERE, '_ladder_clean.json'), encoding='utf-8'))
IMG = json.load(open(os.path.join(HERE, '_gift_imgs.json'), encoding='utf-8'))
END = L['END']; DS = L['深海节']; dm = DS['modules']; PD = DS['payers']; TOT = DS['total']
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
OUT = os.path.join(HERE, f"深海节礼包模块回归_{END.replace('-','')}.html")
def f(v): return f"${v:,.0f}"
pb = G['payer_base']

# ---- 模块数据（每日礼包用去污染 clean 值，其余用 L1）----
DAILY = DC['clean']                              # buyers/orders/rev/max
WEEK  = dm['节日周卡']; VISIT = dm['拜访礼包']; DECOR = dm['装饰礼包']
# 自窗付费率分母
PB_DAILY = pb['每日礼包7/3-9']['payers']         # 1430
PB_WEEK  = pb['周卡7/9-16']['payers']            # 1293
PB_DECOR = pb['装饰7/6-16']['payers']            # 1582
PB_FULL  = pb['深海全窗7/3-16']['payers']        # 1815

daily_pr_own = DAILY['buyers']/PB_DAILY*100
week_pr_own  = WEEK['buyers']/PB_WEEK*100
decor_pr_own = DECOR['buyers']/PB_DECOR*100
visit_pr     = VISIT['buyers']/PB_FULL*100
daily_arppu  = DAILY['rev']/DAILY['buyers']
daily_opb    = DAILY['orders']/DAILY['buyers']

# 第N日漏斗 (800005-009)
FUNNEL = {r['iap']: r for r in G['daily_by_iap'] if r['iap'] in ('800005','800006','800007','800008','800009')}
fn = [FUNNEL[k]['buyers'] for k in ('800005','800006','800007','800008','800009')]
BUYALL = DC['tier_dist']  # 买N档人数
buyall5 = next((x['u'] for x in BUYALL if x['n']==5), 0)
buy1    = next((x['u'] for x in BUYALL if x['n']==1), 0)
# 周卡逐档
WK = {r['iap']: r for r in G['weekly_by_iap']}
# 装饰逐档 + 链
DEC = {r['iap']: r for r in G['decor_by_iap']}
dchain = [DEC['211016']['buyers'], DEC['211017']['buyers'], DEC['211018']['buyers']]
dtier = {x['n_tiers']: x['users'] for x in G['decor_tier_count_dist']}

# ============ SVG 柱状图 helper ============
def barchart(pairs, unit='人', w=560, colors=None, note=''):
    """pairs=[(label, value, sub)]; 竖条 SVG"""
    maxv = max(v for _,v,_ in pairs) or 1
    n = len(pairs); gap=18; bw=(w-80-gap*(n-1))/n; h=210; base=h-34
    colors = colors or ['#58a6ff']*n
    svg=[f'<svg viewBox="0 0 {w} {h}" style="width:100%;max-width:{w}px;height:auto">']
    for i,(lab,v,sub) in enumerate(pairs):
        x=60+i*(bw+gap); bh=(v/maxv)*(base-24); y=base-bh
        c=colors[i] if i<len(colors) else '#58a6ff'
        svg.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="3" fill="{c}" opacity="0.85"/>')
        svg.append(f'<text x="{x+bw/2:.0f}" y="{y-6:.0f}" fill="#f0f6fc" font-size="13" font-weight="700" text-anchor="middle">{v}{unit}</text>')
        svg.append(f'<text x="{x+bw/2:.0f}" y="{base+15:.0f}" fill="#8b949e" font-size="11" text-anchor="middle">{lab}</text>')
        if sub: svg.append(f'<text x="{x+bw/2:.0f}" y="{base+29:.0f}" fill="#484f58" font-size="10" text-anchor="middle">{sub}</text>')
    svg.append('</svg>')
    return f'<div style="text-align:center;padding:8px 0">{"".join(svg)}</div>' + (f'<div class="dim" style="text-align:center">{note}</div>' if note else '')

def dsn_card(key, cap, how, aim, note=''):
    """设计回溯：原验收图在前，文字收进可展开二级"""
    return (f'<div class="card"><div class="ct dsn">设计回溯 · 原验收图</div><div class="dsn-wrap">'
            f'<img class="dsn-img" src="{IMG[key]}" alt="{key} 设计验收图">'
            f'<div class="dsn-side"><div style="font-size:12.5px;color:#c9d1d9;line-height:1.7;margin-bottom:8px">{cap}</div>'
            f'<details class="dfold"><summary>设计详情：怎么设计的 / 想达成什么</summary><div class="dgrid">'
            f'<div class="dbox dsn"><h4>怎么设计的</h4>{how}</div>'
            f'<div class="dbox act"><h4>想达成什么</h4>{aim}</div></div></details>'
            f'{note}</div></div></div>')

CSS = """<style>
:root{--dark:#0d1117;--card:#161b22;--border:#30363d;--text:#c9d1d9;--head:#f0f6fc;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--dark);color:var(--text);font-size:13.5px;display:flex;min-height:100vh}
.sidebar{width:220px;background:var(--dark);border-right:1px solid var(--border);position:fixed;top:0;left:0;bottom:0;overflow-y:auto;z-index:10}
.sb-logo{padding:20px 18px 12px;border-bottom:1px solid var(--border)}
.sb-logo .brand{font-size:18px;font-weight:800;color:var(--head)} .sb-logo .brand span{color:var(--accent)}
.sb-logo .sub{font-size:10.5px;color:#484f58;margin-top:2px;letter-spacing:.5px}
.sb-nav{padding:12px 0}
.sb-item{display:block;padding:9px 18px;font-size:12.5px;color:#8b949e;text-decoration:none;border-left:3px solid transparent}
.sb-item:hover{background:#21262d;color:var(--head);border-left-color:var(--accent)}
.sb-label{padding:10px 18px 4px;font-size:10px;font-weight:700;letter-spacing:1.5px;color:#484f58;text-transform:uppercase}
.content{margin-left:220px;flex:1}
.hero-bar{background:linear-gradient(135deg,#0d1117,#161b22);border-bottom:1px solid var(--border);padding:28px 48px}
.hero-bar h1{font-size:1.5em;font-weight:800;color:var(--head);line-height:1.3}
.hero-bar h1 em{color:var(--yellow);font-style:normal}
.hero-bar .meta{font-size:11.5px;color:#484f58;margin-top:6px} .hero-bar .meta b{color:var(--accent)}
.page{padding:24px 48px 48px;max-width:1080px}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;border-top:3px solid var(--accent)}
.kpi.g{border-top-color:var(--green)} .kpi.r{border-top-color:var(--red)} .kpi.y{border-top-color:var(--yellow)}
.kpi-val{font-size:1.9em;font-weight:800;color:var(--head)}
.kpi-lbl{font-size:11.5px;color:#8b949e;margin-top:5px;font-weight:600}
.kpi-sub{font-size:11px;color:#484f58;margin-top:3px}
.sec{scroll-margin-top:20px}
.sec-head{display:flex;align-items:center;gap:10px;margin:30px 0 12px}
.sec-num{width:26px;height:26px;border-radius:50%;background:var(--accent);color:#0d1117;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center;flex:none}
.sec-title{font-size:15px;font-weight:700;color:var(--head)}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 22px;margin-bottom:14px}
.ct{font-size:11px;font-weight:700;color:#8b949e;letter-spacing:.5px;text-transform:uppercase;border-left:3px solid var(--accent);padding-left:10px;margin-bottom:12px}
.ct.dsn{border-left-color:var(--yellow)}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#21262d;color:var(--head);padding:8px 10px;text-align:center;font-weight:600;border-bottom:1px solid var(--border)}
th.l,td.l{text-align:left}
td{padding:9px 10px;border-bottom:1px solid #21262d;text-align:center;vertical-align:top;line-height:1.6}
tr:hover td{background:#161b2299}
.dim{color:#8b949e;font-size:11px;margin-top:6px}
.row-a{background:#21262d!important} .row-a td{color:var(--head);font-weight:700}
td.r{color:var(--red);font-weight:700} td.g{color:var(--green);font-weight:700} td.y{color:var(--yellow);font-weight:700}
.bigcon{background:linear-gradient(135deg,#1b2436,#161b22);border:1px solid var(--border);border-left:4px solid var(--yellow);border-radius:8px;padding:16px 20px;font-size:14.5px;line-height:2;color:var(--text);margin-bottom:14px} .bigcon b{color:var(--head)}
.con-link{font-size:11px;font-weight:700;color:var(--accent);text-decoration:none;background:#0d2137;border:1px solid #1f6feb44;border-radius:20px;padding:1px 10px;margin-left:2px}
.con-link:hover{background:#1f6feb;color:#fff}
.backtop{margin-left:auto;font-size:11px;font-weight:600;color:#8b949e;text-decoration:none;border:1px solid var(--border);border-radius:20px;padding:3px 11px}
.backtop:hover{color:var(--head);background:#21262d}
.vc{background:#0d2137;border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;font-size:14px;font-weight:700;color:var(--head);line-height:1.9;margin-bottom:12px}
.vc.g{background:#0d2a18;border-left-color:var(--green)} .vc.r{background:#2a1315;border-left-color:var(--red)} .vc.y{background:#2a2410;border-left-color:var(--yellow)}
.badge{display:inline-block;font-size:10.5px;font-weight:700;border-radius:20px;padding:2px 10px;margin-left:6px;vertical-align:middle}
.b-ok{background:#0d2a18;color:var(--green);border:1px solid #238636} .b-part{background:#2a2410;color:var(--yellow);border:1px solid #9e6a03} .b-bad{background:#2a1315;color:var(--red);border:1px solid #b62324}
td b{color:var(--head)}
.dgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.dbox{background:#0d1117;border:1px solid var(--border);border-radius:6px;padding:12px 15px;font-size:12px;line-height:1.75}
.dbox h4{font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;font-weight:700}
.dbox.dsn{border-left:3px solid var(--yellow)} .dbox.act{border-left:3px solid var(--accent)}
.dsn-wrap{display:flex;gap:18px;align-items:flex-start;flex-wrap:wrap}
.dsn-img{border:1px solid var(--border);border-radius:8px;max-height:300px;width:auto;background:#0d1117;flex:none}
.dsn-side{flex:1;min-width:260px}
details.dfold{background:#0d1117;border:1px solid var(--border);border-radius:6px;margin-top:2px}
details.dfold>summary{cursor:pointer;padding:10px 14px;font-size:12px;font-weight:700;color:var(--head);list-style:none;user-select:none}
details.dfold>summary::-webkit-details-marker{display:none}
details.dfold>summary::before{content:'▸ ';color:var(--accent)} details.dfold[open]>summary::before{content:'▾ '}
details.dfold[open]>summary{border-bottom:1px solid var(--border)}
.dfold .dgrid{padding:12px 14px;margin:0}
.footer{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}
@media(max-width:820px){.sidebar{display:none}.content{margin-left:0}.kpi-row{grid-template-columns:1fr 1fr}.dgrid{grid-template-columns:1fr}.page{padding:20px}}
</style>"""

# ============ 结论先行 KPI ============
GIFT_REV = DAILY['rev'] + WEEK['rev'] + VISIT['rev'] + DECOR['rev']
SUMMER = LAD['夏日装饰(647)']['tiers']; NILE = LAD['尼罗装饰(648)']['tiers']
DSDEC = LAD['深海装饰(700)']['tiers']; SIREN = LAD['海妖破冰-提亚马特(605)']['tiers']
kpi = f"""<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{DAILY['buyers']}人 · {daily_pr_own:.0f}%</div><div class="kpi-lbl">每日礼包买家/付费率 · 4 模块最强</div><div class="kpi-sub">$4.99×5 低价入口=付费率+每日转化最好 · 保留推广</div></div>
  <div class="kpi g"><div class="kpi-val">99人 买全 5 日</div><div class="kpi-lbl">每日礼包完成核心 · 复购 {daily_opb:.1f} 单</div><div class="kpi-sub">40% 走到第 5 日 · 完成激励有效（终奖 BUG 已修复正常发放）</div></div>
  <div class="kpi"><div class="kpi-val">{f(GIFT_REV)}</div><div class="kpi-lbl">4 礼包模块合计 · 占深海 {GIFT_REV/TOT*100:.0f}%</div><div class="kpi-sub">尾部模块：单个 {f(DECOR['rev'])}~{f(DAILY['rev'])} · 均非收入大头</div></div>
  <div class="kpi y"><div class="kpi-val">同价差 {SIREN[0]['buyers']//DSDEC[0]['buyers']}×</div><div class="kpi-lbl">海妖破冰 {SIREN[0]['buyers']}人 vs 装饰 {DSDEC[0]['buyers']}人（同 $19.99×3）</div><div class="kpi-sub">断档留存几乎一样 · 差距在产品(养成 vs 装饰)不在机制</div></div>
</div>"""

concl = f"""<div class="bigcon">总判词：<b>4 个尾部礼包模块=深海的「宽度与货架」层，合计 {f(GIFT_REV)}（占深海 {GIFT_REV/TOT*100:.0f}%）不是收入大头</b>——每日礼包这类低价入口是最健康的形态；拜访/周卡本次形态即如此、保持或再观察；装饰阶梯的断档是该形式的常态，提升方向清楚。逐条：<br>
<span style="font-size:13px;line-height:2.05">
① <b>每日礼包=4 模块最健康形态，继续保留</b>：{DAILY['buyers']} 买家 / 自窗付费率 {daily_pr_own:.0f}%（$4.99×5 天低价入口）=付费率与每日付费转化全场最好；第 1→2 日流失后稳住、40% 走到第 5 日、99 人买全=完成激励有效（买全终奖 100 藏宝图 BUG 已修复、现正常发放） <a class="con-link" href="#gsec1">01 ↓</a><br>
② <b>拜访礼包=这个形式就这样，保持即可</b>：{VISIT['buyers']} 个大 R 各买 1 次 $99.99 门头包（付费率 {visit_pr:.1f}%），ARPPU $100；门头外显本就是高价单档形态、免费拜访玩法拉活跃=预期内，无需改动 <a class="con-link" href="#gsec3">03 ↓</a><br>
③ <b>周卡=本次不具代表性，下节日再看</b>：上线偏晚（7/9 随客户端包晚 6 天）且无新内容，自窗校正付费率 {week_pr_own:.1f}%；建议<b>下个节日跟第二个主要模块一起上线再评估效果</b>，本届数据仅作观察 <a class="con-link" href="#gsec2">02 ↓</a><br>
④ <b>装饰阶梯断档=该形式常态，非深海缺陷</b>：深海 {dchain[0]}→{dchain[1]}（{dchain[1]/dchain[0]*100:.0f}%）→{dchain[2]}（{dchain[2]/dchain[0]*100:.0f}%），与同价同结构的<b>夏日（{SUMMER[1]['ret']:.0f}%/{SUMMER[2]['ret']:.0f}%）/ 尼罗（{NILE[1]['ret']:.0f}%/{NILE[2]['ret']:.0f}%）/ 海妖破冰（{SIREN[1]['ret']:.0f}%/{SIREN[2]['ret']:.0f}%）几乎一致</b>——$19.99×3 flat 阶梯链的档间留存是形式常量（~40-54%/~28-42%），深海不比同行差；<b>关键洞察：海妖破冰同为 $19.99×3，档1 却 {SIREN[0]['buyers']:,} 人（装饰的 {SIREN[0]['buyers']//DSDEC[0]['buyers']}×）——同价同机制，差两个量级的是产品中心度（英雄养成 vs 装饰外显），不是阶梯机制、也不是定价</b> <a class="con-link" href="#gsec4">04 ↓</a><br>
⑤ <b>共性启示</b>：每日礼包 $4.99 低价入口=X3 跑广度+带续购的最优解、值得推广；装饰这类外显阶梯断档正常、盘子天生小（受限于产品是"锦上添花"而非"养成刚需"），想放量得靠内容更想要，别指望改机制/降价 <a class="con-link" href="#gsec5">05 ↓</a>
</span></div>"""

# ============ 章节 helper ============
def sec_head(num, title, anchor):
    return f'<div class="sec" id="{anchor}"><div class="sec-head"><div class="sec-num">{num}</div><div class="sec-title">{title}</div><a class="backtop" href="#top">↑ 结论</a></div></div>'

def l1row(name, m, buyers, pr, arppu, opb, mx):
    return (f'<tr><td class="l"><b>{name}</b></td><td>{f(m["rev"])}</td><td>{buyers}</td>'
            f'<td>{pr:.1f}%</td><td>${arppu:.1f}</td><td>{opb:.1f}单</td><td>${mx:.0f}</td></tr>')

# ---- 01 每日礼包 ----
c1 = sec_head('01', '每日礼包（102993 · ActvType29 进度礼包 · 砰然心动）', 'gsec1')
c1 += '<div class="vc g">判定：<b>4 模块最健康形态，继续保留</b>——256 人 / 自窗付费率 %.0f%% 全场最强，$4.99 低价入口跑广度、99 人买全=完成激励有效 <span class="badge b-ok">达预期·保留</span></div>' % daily_pr_own
c1 += dsn_card('每日礼包',
  '每日礼包（Type29 进度礼包·砰然心动）：5 档「第 N 日礼包」<b>全 $4.99</b>，逐日解锁，<b>买全 5 档送藏宝图×100</b>终奖；仅上前 7 天。图=X3 验收实机截图。',
  '5 档 800005-009 全 $4.99（GiftPriceCfg105）；每档 Reward 组 40500（航海罗盘×10+藏宝图×20+钻石×2500+VIP×25，标称 ROI 2300%）；买全 5 档额外送藏宝图×100（组 40600）。仅上前 7 天（7/3-9，Type29 固定 7 天）。',
  '低价入口 + 每日回访：$4.99 拉最广付费面，用「买全终奖」把人留到第 5 天。深海把常驻每日礼包做成独立 Type29 节日活动（克隆方向 A）。',
  note="<div class=\"dim\">⚠️ 口径修正：L1 按 <code>iap LIKE '8000%'</code> 会混入首充进度礼包 800000-004（另一产品），本页已剔除，只算 800005-009：<b>256 买家 / $3,603</b>（L1 原值 $3,805/293 含污染）。</div>")
c1 += '<div class="card"><div class="ct">L1 三件套（自窗 7/3-9 · 分母=同窗 59 服总付费 %d 人）</div><table><tr><th class="l">模块</th><th>收入</th><th>买家</th><th>付费率</th><th>ARPPU</th><th>复购</th><th>max</th></tr>' % PB_DAILY
c1 += l1row('每日礼包 800005-009', DAILY, DAILY['buyers'], daily_pr_own, daily_arppu, daily_opb, DAILY['max']) + '</table></div>'
c1 += '<div class="card"><div class="ct">第 N 日购买漏斗（每档买家数 · 800005→800009）</div>'
c1 += barchart([('第1日',fn[0],'800005'),('第2日',fn[1],'800006'),('第3日',fn[2],'800007'),('第4日',fn[3],'800008'),('第5日',fn[4],'800009')],
    colors=['#3fb950','#58a6ff','#58a6ff','#58a6ff','#58a6ff'],
    note='第 1 日 %d 人入场 → 第 2 日 %d（%.0f%%）后基本稳住，第 5 日 %d 人=入场的 %.0f%%。入场后留存扎实，是 4 模块唯一有健康每日回访曲线的。' % (fn[0],fn[1],fn[1]/fn[0]*100,fn[4],fn[4]/fn[0]*100))
c1 += """<div class="dim" style="margin-top:12px">买全档数分布：买 1 档止步 <b>%d 人</b>（%.0f%%），<b>买全 5 档 %d 人</b>=完成核心——这 99 人拿到买全终奖（100 藏宝图），完成激励有效（该终奖曾有领取 BUG，已修复、现正常发放）。综合看，$4.99×5 天低价形式的付费率与每日付费转化在深海全模块里最好，<b>形式健康、继续保留</b>。</div></div>""" % (buy1, buy1/DAILY['buyers']*100, buyall5)

# ---- 02 周卡 ----
c2 = sec_head('02', '节日周卡（109101 · 自选周卡 · 每天 10 选 4 领 7 天）', 'gsec2')
c2 += '<div class="vc y">判定：<b>本次不具代表性——上线偏晚（晚 6 天）且无新内容，建议下个节日跟第二个主要模块一起上线再评估</b>；本届数据仅作观察（自窗付费率 %.1f%%，$49.99 全包档是收入引擎） <span class="badge b-part">再观察</span></div>' % week_pr_own
c2 += dsn_card('周卡',
  '节日周卡（自选周卡）：4 档 <b>$9.99 / $19.99 / $29.99 + $49.99 全包</b>，7 天每天 10 选 4 自选好礼；<b>晚 6 天随新客户端包上线</b>。图=X3 验收实机截图。',
  '4 档 Pack 2026101-104=$9.99/$19.99/$29.99 基础三档 + $49.99 全包；7 天每天 10 选 4 自选（夏日恋语周卡骨架，ROI 2.75x）。晚 6 天开（7/9 随新客户端包、不热更），跑到 7/16。',
  '第二周 depth 核心之一：用「自选 + 连续 7 天领取」拉中段复购、提客单。')
c2 += '<div class="card"><div class="ct">L1 三件套 + 口径校正（迟开只跑 7/9-16）</div><table><tr><th class="l">口径</th><th>收入</th><th>买家</th><th>付费率</th><th>ARPPU</th><th>复购</th><th>max</th></tr>'
c2 += f'<tr><td class="l">全窗分母（7/3-16 · {PB_FULL}人）<span class="dim">L1 默认</span></td><td>{f(WEEK["rev"])}</td><td>{WEEK["buyers"]}</td><td class="r">{WEEK["payrate"]:.1f}%</td><td>${WEEK["arppu"]:.1f}</td><td>{WEEK["opb"]:.1f}单</td><td>${WEEK["max"]:.0f}</td></tr>'
c2 += f'<tr class="row-a"><td class="l">自窗分母（7/9-16 · {PB_WEEK}人）<span class="dim">校正后</span></td><td>{f(WEEK["rev"])}</td><td>{WEEK["buyers"]}</td><td class="g">{week_pr_own:.1f}%</td><td>${WEEK["arppu"]:.1f}</td><td>{WEEK["opb"]:.1f}单</td><td>${WEEK["max"]:.0f}</td></tr></table>'
c2 += '<div class="dim">用全窗总付费人数当分母会低估周卡付费率（它根本没在前 6 天卖）；自窗校正把 3.6%%→%.1f%%——但仍是 4 模块偏低档，迟开+客户端包依赖直接压缩了触达窗口。</div></div>' % week_pr_own
c2 += '<div class="card"><div class="ct">逐档表现（买家数 / 收入）</div>'
c2 += barchart([('基础 $9.99',WK['2026101']['buyers'],f(WK['2026101']['rev'])),('$19.99',WK['2026102']['buyers'],f(WK['2026102']['rev'])),('$29.99',WK['2026103']['buyers'],f(WK['2026103']['rev'])),('全包 $49.99',WK['2026104']['buyers'],f(WK['2026104']['rev']))],
    colors=['#58a6ff','#58a6ff','#58a6ff','#d29922'],
    note='$9.99 基础档买家最多（%d 人=最广入口），但 <b>$49.99 全包吃走 %.0f%% 收入（%d 人 / %s）</b>=收入引擎；玩家用"直接买全包"替代逐档。复购 %.1f 单、几乎人人单笔买断（唯一例外=1 名 $260/7 单的重复购买者）。' % (WK['2026101']['buyers'], WK['2026104']['rev']/WEEK['rev']*100, WK['2026104']['buyers'], f(WK['2026104']['rev']), WEEK['opb']))
c2 += '</div>'

# ---- 03 拜访礼包 ----
c3 = sec_head('03', '拜访礼包（105605 · 海滨之约 · 门头三件套）', 'gsec3')
c3 += '<div class="vc">判定：<b>这个形式就这样，保持即可</b>——门头外显本就是高价单档形态，%d 个大 R 各买 1 次 $99.99（ARPPU $100），免费拜访玩法拉活跃=预期内，无需改动 <span class="badge b-ok">保持</span></div>' % VISIT['buyers']
c3 += dsn_card('拜访',
  '拜访礼包（海滨之约）：单包 <b>$99.99 门头三件套</b>（横梁/地板/墙纸 + 钻 5 万 + VIP 500）；免费拜访玩法发藏宝图。图=X3 验收实机截图。',
  '单包 211020=$99.99 门头三件套（解锁道具 152017-19 + 钻 5 万 + VIP 500）。免费拜访玩法：每次拜访得藏宝图×1、里程碑（10/20/30/50 次）各得藏宝图×5。窗口 14 天（设计原为 7 天）。',
  '门头外显 + 拜访社交：免费藏宝图驱动全民拜访活跃，$99.99 门头包收愿意为居所外显付费的大 R。')
c3 += '<div class="card"><div class="ct">L1 三件套（全窗 7/3-16 · 分母 %d 人）</div><table><tr><th class="l">模块</th><th>收入</th><th>买家</th><th>付费率</th><th>ARPPU</th><th>复购</th><th>max</th></tr>' % PB_FULL
c3 += l1row('拜访礼包 211020', VISIT, VISIT['buyers'], visit_pr, VISIT['arppu'], VISIT['opb'], VISIT['max']) + '</table>'
c3 += '<div class="dim">28 个大 R 各买 1 次 $99.99=$2,800，ARPPU 恰好 $100、复购 1.0。客单最高、触达小=门头外显高价单档形态的固有特征（尼罗 210617 门头包同为 $99.99 单档）。免费藏宝图领取与付费买断解耦（买包≠拜访计数硬条件），拜访玩法负责拉活跃、$99.99 包收愿意为居所外显付费的大 R——<b>各司其职，这个形式保持即可</b>。</div></div>'

# ---- 04 装饰阶梯 ----
c4 = sec_head('04', '装饰阶梯礼包（106103 · ChainPack700 · 深海居所）', 'gsec4')
c4 += '<div class="vc y">判定：<b>断档（%d→%d→%d）是该形式常态、非深海缺陷</b>——与夏日/尼罗/海妖破冰同价链一致；盘子小是产品定位（外显 vs 养成）决定的，不是机制/定价 <span class="badge b-part">形式常态·盘子受产品限</span></div>' % (dchain[0],dchain[1],dchain[2])
c4 += dsn_card('装饰',
  '装饰阶梯礼包（深海居所·ChainPack700）：3 档<b>全 $19.99</b> 按序解锁，每包发<b>同一件椰风遮阳椅</b> + 藏宝图 40/60/80 递增。图=X3 验收实机截图。',
  'ChainPack 700 阶梯链 3 档 211016-018 全 $19.99；阶梯=必须按序买。每包发椰风遮阳椅×1（三档同一件家具）+ 藏宝图 40/60/80 递增。D3（7/6）开。曾漏建活动壳致不显示（已修）。',
  '居所外显 + 阶梯递进：用"买得越多送越多藏宝图"引导逐档买满 3 档。',
  note='<div class="dim">深海本节无新家具，档差只靠藏宝图数量（40/60/80）——设计层就定的（对齐总览白纸黑字），非配置 bug。</div>')
c4 += '<div class="card"><div class="ct">L1 三件套（自窗 7/6-16 · 分母 %d 人）</div><table><tr><th class="l">模块</th><th>收入</th><th>买家</th><th>付费率</th><th>ARPPU</th><th>复购</th><th>max</th></tr>' % PB_DECOR
c4 += l1row('装饰阶梯 211016-018', DECOR, DECOR['buyers'], decor_pr_own, DECOR['arppu'], DECOR['opb'], DECOR['max']) + '</table></div>'
c4 += '<div class="card"><div class="ct">阶梯链断档（逐档到达买家）</div>'
c4 += barchart([('第1档 $19.99',dchain[0],'211016'),('第2档 $19.99',dchain[1],'211017'),('第3档 $19.99',dchain[2],'211018')],
    colors=['#3fb950','#d29922','#f85149'],
    note='入场 %d 人 → 第 2 档 %d（-%.0f%% 腰斩）→ 第 3 档 %d（-%.0f%%）。仅 %.0f%% 走完全链。' % (dchain[0],dchain[1],(dchain[0]-dchain[1])/dchain[0]*100,dchain[2],(dchain[1]-dchain[2])/dchain[1]*100,dchain[2]/dchain[0]*100))
c4 += '<div class="dim" style="margin-top:12px">买 1 档止步 %d 人、买 2 档 %d 人、<b>买全 3 档 %d 人</b>（忠实核心，贡献 max $60）。断档看着陡，但要判断是不是"深海问题"，得跟同形式的其他阶梯链比 ↓</div></div>' % (dtier.get(1,0), dtier.get(2,0), dtier.get(3,0))
# 四链同价对比（全 $19.99×3）
c4 += '<div class="card"><div class="ct">$19.99×3 阶梯链同价对比 · 夏日/尼罗/深海装饰 vs 海妖破冰礼包</div><table>'
c4 += '<tr><th class="l">阶梯链（全 $19.99×3）</th><th class="l">产品性质</th><th>档1 入场</th><th>档2（留存）</th><th>档3（留存）</th></tr>'
c4 += f'<tr><td class="l"><b>夏日装饰</b> 210917-19</td><td class="l">外显装饰</td><td>{SUMMER[0]["buyers"]}人</td><td>{SUMMER[1]["buyers"]}（{SUMMER[1]["ret"]:.0f}%）</td><td>{SUMMER[2]["buyers"]}（{SUMMER[2]["ret"]:.0f}%）</td></tr>'
c4 += f'<tr><td class="l"><b>尼罗装饰</b> 210630-32</td><td class="l">外显装饰</td><td>{NILE[0]["buyers"]}人</td><td>{NILE[1]["buyers"]}（{NILE[1]["ret"]:.0f}%）</td><td>{NILE[2]["buyers"]}（{NILE[2]["ret"]:.0f}%）</td></tr>'
c4 += f'<tr class="row-a"><td class="l"><b>深海装饰</b> 211016-18</td><td class="l">外显装饰</td><td>{DSDEC[0]["buyers"]}人</td><td>{DSDEC[1]["buyers"]}（{DSDEC[1]["ret"]:.0f}%）</td><td>{DSDEC[2]["buyers"]}（{DSDEC[2]["ret"]:.0f}%）</td></tr>'
c4 += f'<tr><td class="l"><b>海妖破冰礼包</b> 2009001-03</td><td class="l">英雄养成（同价对标）</td><td class="g">{SIREN[0]["buyers"]:,}人</td><td>{SIREN[1]["buyers"]}（{SIREN[1]["ret"]:.0f}%）</td><td>{SIREN[2]["buyers"]}（{SIREN[2]["ret"]:.0f}%）</td></tr>'
c4 += '</table>'
c4 += f'<div class="dim" style="margin-top:10px">同为 $19.99×3 阶梯链，两个结论：<br>① <b>断档是形式常量，深海不比同行差</b>——四条链档2 留存全落在 {min(SUMMER[1]["ret"],NILE[1]["ret"],DSDEC[1]["ret"],SIREN[1]["ret"]):.0f}-{max(SUMMER[1]["ret"],NILE[1]["ret"],DSDEC[1]["ret"],SIREN[1]["ret"]):.0f}%、档3 落在 {min(SUMMER[2]["ret"],NILE[2]["ret"],DSDEC[2]["ret"],SIREN[2]["ret"]):.0f}-{max(SUMMER[2]["ret"],NILE[2]["ret"],DSDEC[2]["ret"],SIREN[2]["ret"]):.0f}%，深海（{DSDEC[1]["ret"]:.0f}%/{DSDEC[2]["ret"]:.0f}%）就在中间；$19.99×3 flat 阶梯天生就是"少数人付全款"的形态。<br>② <b>差两个量级的是产品不是机制</b>——海妖破冰同价同结构，档1 却 {SIREN[0]["buyers"]:,} 人（装饰的 {SIREN[0]["buyers"]//DSDEC[0]["buyers"]}×），因为它卖的是<b>英雄养成刚需</b>、装饰卖的是<b>锦上添花的外显</b>。同样 $19.99、同样阶梯，付费人数差两个量级——<b>装饰盘子小是产品定位决定的，不是阶梯机制或定价的锅</b>。想把装饰放量，得让外显内容更"想要"，光调机制/降价没用。<br>③ <b>同为外显，内容有变化就留得住</b>——夏日装饰档间留存最高（{SUMMER[1]["ret"]:.0f}%/{SUMMER[2]["ret"]:.0f}%），正因它<b>每档给不同装饰（多款家具）</b>；深海三档发同一件椰风遮阳椅，续档只多藏宝图，留存自然低一截。<b>长期解=做装饰升级系统</b>（逐档解锁升级款/不同外显，让"买下一档"本身有外显获得感），而不是同一件家具卖三遍。</div></div>'

# ---- 05 结论与动作 ----
c5 = sec_head('05', '横向对比 · 结论与动作', 'gsec5')
c5 += '<div class="card"><div class="ct">4 模块横向对比（付费率=各自自窗校正口径）</div><table>'
c5 += '<tr><th class="l">模块</th><th>收入</th><th>买家</th><th>付费率(自窗)</th><th>ARPPU</th><th>复购</th><th>max</th><th class="l">一句话判定</th></tr>'
c5 += f'<tr><td class="l"><b>每日礼包</b></td><td>{f(DAILY["rev"])}</td><td class="g">{DAILY["buyers"]}</td><td class="g">{daily_pr_own:.0f}%</td><td>${daily_arppu:.1f}</td><td>{daily_opb:.1f}单</td><td>${DAILY["max"]:.0f}</td><td class="l">🟢 低价入口=付费率/每日转化最好，继续保留</td></tr>'
c5 += f'<tr><td class="l"><b>节日周卡</b></td><td>{f(WEEK["rev"])}</td><td>{WEEK["buyers"]}</td><td class="y">{week_pr_own:.1f}%</td><td>${WEEK["arppu"]:.1f}</td><td>{WEEK["opb"]:.1f}单</td><td>${WEEK["max"]:.0f}</td><td class="l">🟡 晚开+无新内容，下节日跟主模块一起上再看</td></tr>'
c5 += f'<tr><td class="l"><b>拜访礼包</b></td><td>{f(VISIT["rev"])}</td><td>{VISIT["buyers"]}</td><td>{visit_pr:.1f}%</td><td>${VISIT["arppu"]:.0f}</td><td>{VISIT["opb"]:.1f}单</td><td>${VISIT["max"]:.0f}</td><td class="l">⚪ 门头高价单档=固有形态，保持即可</td></tr>'
c5 += f'<tr><td class="l"><b>装饰阶梯</b></td><td>{f(DECOR["rev"])}</td><td>{DECOR["buyers"]}</td><td class="y">{decor_pr_own:.1f}%</td><td>${DECOR["arppu"]:.1f}</td><td>{DECOR["opb"]:.1f}单</td><td>${DECOR["max"]:.0f}</td><td class="l">⚪ 断档正常(≈夏日/尼罗/海妖破冰)，盘子受产品定位限</td></tr>'
c5 += '</table><div class="dim">跨模块 ARPU 排位（统一深海 59 服全窗分母 %d 人）：每日礼包 $%.2f > 周卡 $%.2f > 拜访 $%.2f > 装饰 $%.2f——四者都是尾部量级，合计占深海 %.0f%%。</div></div>' % (PB_FULL, DAILY['rev']/PB_FULL, WEEK['rev']/PB_FULL, VISIT['rev']/PB_FULL, DECOR['rev']/PB_FULL, GIFT_REV/TOT*100)
c5 += """<div class="card"><div class="ct">动作清单（带依据）</div><table>
<tr><th class="l">模块</th><th class="l">动作</th><th class="l">依据</th></tr>
<tr><td class="l"><b>每日礼包</b></td><td class="l">🟢 <b>继续保留并推广该形式</b>（$4.99×5 天低价入口）</td><td class="l">付费率 %.0f%% + 每日付费转化全场最好，是 X3 稀缺的宽承接位；99 人买全=完成激励有效（终奖 BUG 已修复正常发放）（01 章）</td></tr>
<tr><td class="l"><b>拜访礼包</b></td><td class="l">⚪ <b>保持即可，无需改动</b></td><td class="l">门头外显本就是高价单档形态，%d 大 R 买断=预期内，免费拜访玩法拉活跃各司其职（03 章）</td></tr>
<tr><td class="l"><b>节日周卡</b></td><td class="l">🟡 <b>下个节日跟第二个主要模块一起上线再评估</b></td><td class="l">本届晚开 6 天（随客户端包）且无新内容，数据不具代表性、仅作观察（02 章）</td></tr>
<tr><td class="l"><b>装饰阶梯</b></td><td class="l">🟢 <b>短期=每档做不同装饰</b>（照夏日，别三档发同一件椰风椅）<br>🔵 <b>长期=做装饰升级系统</b>（逐档解锁升级款外显，让"买下一档"有外显获得感）</td><td class="l">夏日每档给不同家具→留存最高（%.0f%%/%.0f%%）vs 深海三档同一件（%.0f%%/%.0f%%）；断档是形式常量，内容有变化/升级才留得住（04 章）</td></tr>
</table></div>""" % (daily_pr_own, VISIT['buyers'], SUMMER[1]['ret'], SUMMER[2]['ret'], DSDEC[1]['ret'], DSDEC[2]['ret'])

page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>X3 深海节礼包模块回归 — tap4fun</title>
{CSS}</head><body>
<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">DEEPSEA GIFT-PACK REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">深海节礼包模块回归</div>
    <a class="sb-item" href="#top">结论先行</a>
    <a class="sb-item" href="#gsec1">01 · 每日礼包</a>
    <a class="sb-item" href="#gsec2">02 · 节日周卡</a>
    <a class="sb-item" href="#gsec3">03 · 拜访礼包</a>
    <a class="sb-item" href="#gsec4">04 · 装饰阶梯</a>
    <a class="sb-item" href="#gsec5">05 · 结论与动作</a>
    <a class="sb-item" href="母题4_改动效果清单_{END.replace('-','')}.html">← 返回双节回归总页</a>
  </div>
</nav>
<div class="content">
<div class="hero-bar" id="top">
  <h1>X3 深海节 · 尾部礼包模块回归<br><em>每日礼包 · 节日周卡 · 拜访礼包 · 装饰阶梯</em></h1>
  <div class="meta">窗口 <b>7/3-{END[5:]} · 59服</b>（深海 7/16 收官=终版数据） · 数据 <b>Trino v1090 订单全口径</b> · 各模块按自身活动窗口校正付费率 · 生成 {now}</div>
</div>
<div class="page">
<div class="sec" id="secall"><div class="sec-head"><div class="sec-num">★</div><div class="sec-title">整体结论（4 礼包模块 · 7/3-{END[5:]} · 59服）</div></div>
{concl}
{kpi}
{c1}
{c2}
{c3}
{c4}
{c5}
<div class="footer">X3 深海节尾部礼包模块回归 · 数据 Trino v1090 深海 59 服全口径 · 每日礼包已剔除首充污染(800000-004) · 生成 {now}</div>
</div></div></body></html>"""

open(OUT, 'w', encoding='utf-8').write(page)
print('saved', OUT)
