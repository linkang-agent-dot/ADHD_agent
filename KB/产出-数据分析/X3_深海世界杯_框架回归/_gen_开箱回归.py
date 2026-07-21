# -*- coding: utf-8 -*-
"""
X3 世界杯开箱回归 · 独立报告生成器（07-21 用户定：照竞猜回归先例，把母题4·02章摘出成页，线性编号章节）
数据源 = _l1_m4.json / _wc_bench.json / _kaixiang.json / _kaixiang_deep.json / _anchor.json
       / _kx_payrate.json / _ticket_summer.json / _ticket_sources.json / _kx_top20.json / _top20_assets.json
用法: python _gen_开箱回归.py   （终版刷新：随 8 数据脚本 + _refresh_inline.py 之后重跑，文件名随 _l1_m4.json 的 END 联动）
builder 复制自 _gen_母题4.py（竞猜/大富翁页同款先例：改开箱视图只改本生成器）。
"""
import sys, json, os, datetime
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, '_l1_m4.json'), encoding='utf-8'))
B = json.load(open(os.path.join(HERE, '_wc_bench.json'), encoding='utf-8'))
END = L['END']
WC = L['世界杯']; wm = WC['modules']
KX = B['WC开箱族合并']
K3 = json.load(open(os.path.join(HERE, '_kaixiang.json'), encoding='utf-8'))
G_VT = K3['情人节开箱(致她的信)']; G_SM = K3['夏日开箱(复用情人包)']; G_WC = K3['世界杯开箱(福箱)']
KD = json.load(open(os.path.join(HERE, '_kaixiang_deep.json'), encoding='utf-8'))
KG = KD['gens']; PS = KD['perserver']
AN = json.load(open(os.path.join(HERE, '_anchor.json'), encoding='utf-8'))
PR = json.load(open(os.path.join(HERE, '_kx_payrate.json'), encoding='utf-8'))
TKS = json.load(open(os.path.join(HERE, '_ticket_summer.json'), encoding='utf-8'))
T20 = json.load(open(os.path.join(HERE, '_kx_top20.json'), encoding='utf-8'))
A64 = json.load(open(os.path.join(HERE, '_top20_assets.json'), encoding='utf-8'))
GEN_COL = {'元旦开箱': '#4691e8', '情人节开箱': '#8b949e', '夏日开箱': '#2ea856', '世界杯开箱': '#c08a17'}
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
OUT = os.path.join(HERE, f"世界杯开箱回归_{END.replace('-','')}.html")

def fmt(v): return f"${v:,.0f}"

# ============ builders（复制自 _gen_母题4.py 02 章） ============

def kx_table():
    gens = [('情人节开箱', G_VT, '2/6-2/16 · 55服'), ('夏日开箱', G_SM, '5/29-6/8 · 88服'), ('世界杯开箱', G_WC, f'6/26-{END[5:]} · 全服')]
    tr = ['<table><tr><th class="l">代际（各自窗口·服段）</th><th>收入</th><th>买家</th><th>付费玩家付费率*</th><th>ARPPU</th><th>复购</th><th>p50</th><th>p90</th><th>$100+占比</th><th>$500+占比</th><th>max</th><th>锚点买家(占比)</th></tr>']
    for name, g, meta in gens:
        m = g['合并']; a = g['锚点']; pr = KG[name]['payrate']
        hl = ' class="row-a"' if '世界杯' in name else ''
        tr.append(f"<tr{hl}><td class='l'><b>{name}</b><span class='dim'>　{meta}</span></td>"
                  f"<td>{fmt(m['rev'])}</td><td>{m['buyers']}</td><td>{pr:.1f}%<span class='dim'>／{KG[name]['total_payers']:,}</span></td>"
                  f"<td>${m['arppu']:.0f}</td><td>{m['opb']:.1f}</td>"
                  f"<td>${m['p50']:.0f}</td><td>${m['p90']:.0f}</td><td>{m['over100']:.1f}%</td><td>{m['over500']:.1f}%</td>"
                  f"<td><b>{fmt(m['max'])}</b></td><td>{a['buyers']}人（{a['buyers']/m['buyers']*100:.0f}%）</td></tr>")
    tr.append('</table>')
    tr.append("<div class='dim' style='margin-top:6px'>*付费玩家付费率 = 开箱买家 ÷ 有开箱流水的服上同窗总付费人数（分母随部署面变化：情人 3,540 / 夏日 1,205 / 世界杯 4,047——夏日 20.3% 偏高主因是分母面窄，跨代比较看买家数与 ARPPU 更稳）</div>")
    return ''.join(tr)

def kx_panels():
    """四联小图：ARPPU / 买家规模 / 锚点买家占比 / max"""
    gens = [('情人', G_VT, '#8b949e'), ('夏日', G_SM, '#2ea856'), ('世界杯', G_WC, '#c08a17')]
    panels = [('ARPPU $（横盘）', lambda g: g['合并']['arppu'], '${:.0f}', 60),
              ('买家规模（受服数/窗口加持）', lambda g: g['合并']['buyers'], '{:.0f}', 420),
              ('锚点买家占开箱买家 %', lambda g: g['锚点']['buyers']/g['合并']['buyers']*100, '{:.0f}%', 50),
              ('单人最高 max $', lambda g: g['合并']['max'], '${:,.0f}', 1500)]
    PW, PH, T_, B_, L_ = 270, 190, 38, 36, 46
    W = PW*4 + 60
    s = [f'<svg viewBox="0 0 {W} {PH+T_+B_}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for pi, (title, f, fv, vmax) in enumerate(panels):
        ox = pi*(PW+20)
        s.append(f'<text x="{ox+L_}" y="{T_-14}" fill="#f0f6fc" font-size="12" font-weight="700">{title}</text>')
        bw = (PW-L_-10)/3
        for gi, (nm, g, c) in enumerate(gens):
            v = f(g)
            x = ox + L_ + gi*bw + 6
            y = T_ + PH*(1-min(1, v/vmax))
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-12:.1f}" height="{T_+PH-y:.1f}" fill="{c}" rx="4"><title>{nm} {fv.format(v)}</title></rect>')
            s.append(f'<text x="{x+(bw-12)/2:.1f}" y="{y-6:.1f}" fill="#f0f6fc" font-size="11" font-weight="700" text-anchor="middle">{fv.format(v)}</text>')
            s.append(f'<text x="{x+(bw-12)/2:.1f}" y="{T_+PH+16}" fill="#8b949e" font-size="10" text-anchor="middle">{nm}</text>')
    s.append('</svg>')
    return ''.join(s)

def kx_dist_chart(bucket_key, buckets_n, bucket_w, xlab_fn, tail_lab, title):
    W, H, L_, R, T, B_ = 1160, 330, 52, 16, 30, 62
    pw, ph = W-L_-R, H-T-B_
    cols = buckets_n + 1
    series = []
    for gen in ['元旦开箱','情人节开箱','夏日开箱','世界杯开箱']:
        g = KG[gen]; total = g['buyers']
        bk = {int(k): v for k, v in g[bucket_key].items()}
        vals = [bk.get(i, 0)/total*100 for i in (range(buckets_n) if bucket_key=='bucketA' else range(1, buckets_n+1))]
        vals.append(bk.get(buckets_n if bucket_key=='bucketA' else 20, 0)/total*100)
        series.append((gen, vals))
    vmax = max(max(v) for _, v in series)*1.12
    def X(i): return L_ + pw*(i+0.5)/cols
    def Y(v): return T + ph*(1-v/vmax)
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    step = max(2, int(vmax//5))
    for gv in range(0, int(vmax)+1, step):
        s.append(f'<line x1="{L_}" y1="{Y(gv):.1f}" x2="{W-R}" y2="{Y(gv):.1f}" stroke="#21262d"/>')
        s.append(f'<text x="{L_-6}" y="{Y(gv)+4:.1f}" fill="#484f58" font-size="10" text-anchor="end">{gv}%</text>')
    for i in range(cols):
        if cols > 15 and i % 2 == 1 and i < buckets_n:
            continue
        lab = xlab_fn(i) if i < buckets_n else tail_lab
        s.append(f'<text x="{X(i):.1f}" y="{H-46}" fill="#8b949e" font-size="9" text-anchor="middle">{lab}</text>')
    for gen, vals in series:
        c = GEN_COL[gen]; wgt = 2.6 if gen == '世界杯开箱' else 1.6
        pts = ' L '.join(f'{X(i):.1f} {Y(v):.1f}' for i, v in enumerate(vals))
        s.append(f'<path d="M {X(0):.1f} {Y(0):.1f} L {pts} L {X(cols-1):.1f} {Y(0):.1f} Z" fill="{c}" fill-opacity="0.12"/>')
        s.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(vals):
            s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.4" fill="{c}"><title>{gen} {xlab_fn(i) if i<buckets_n else tail_lab}: {v:.1f}% 买家</title></circle>')
    lx = L_
    for gen in ['元旦开箱','情人节开箱','夏日开箱','世界杯开箱']:
        g = KG[gen]
        lab = f"{gen}（{g['buyers']}人·max{fmt(g['max'])}）"
        s.append(f'<line x1="{lx}" y1="{H-22}" x2="{lx+18}" y2="{H-22}" stroke="{GEN_COL[gen]}" stroke-width="2.4"/>')
        s.append(f'<text x="{lx+23}" y="{H-18}" fill="#c9d1d9" font-size="10.5">{lab}</text>')
        lx += 23 + len(lab)*10 + 22
    s.append(f'<text x="{L_}" y="{T-10}" fill="#f0f6fc" font-size="12" font-weight="700">{title}</text>')
    s.append('</svg>')
    return ''.join(s)

def kx_top20_chart():
    """Top20 付费额度阶梯：夏日老服 vs 世界杯老服 vs 世界杯全服 vs 深海转盘族"""
    series = [('夏日·老服', [v['tot'] for v in T20['夏日_老服top20']], '#2ea856'),
              ('世界杯·老服', [v['tot'] for v in T20['世界杯_老服top20']], '#c08a17'),
              ('世界杯·全服', [v['tot'] for v in T20['世界杯_全服top20']], '#8b949e'),
              ('深海·转盘族', [v['tot'] for v in T20['深海_转盘top20']], '#4691e8')]
    W, H, L_, R, T, B_ = 1160, 300, 56, 16, 34, 54
    pw, ph = W-L_-R, H-T-B_
    vmax = max(max(v) for _, v, _ in series)*1.1
    def X(i): return L_ + pw*i/19
    def Y(v): return T + ph*(1-v/vmax)
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for gv in range(0, int(vmax), 250):
        s.append(f'<line x1="{L_}" y1="{Y(gv):.1f}" x2="{W-R}" y2="{Y(gv):.1f}" stroke="#21262d"/>')
        s.append(f'<text x="{L_-6}" y="{Y(gv)+4:.1f}" fill="#484f58" font-size="10" text-anchor="end">${gv}</text>')
    for i in range(20):
        s.append(f'<text x="{X(i):.1f}" y="{H-36}" fill="#8b949e" font-size="9.5" text-anchor="middle">{i+1}</text>')
    s.append(f'<text x="{L_+pw/2:.1f}" y="{H-20}" fill="#8b949e" font-size="10.5" text-anchor="middle">开箱付费额排名（第1~20名）</text>')
    for nm, vals, c in series:
        wgt = 2.4 if '世界杯·老服' in nm else 1.7
        pts = ' L '.join(f'{X(i):.1f} {Y(v):.1f}' for i, v in enumerate(vals))
        s.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(vals):
            s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3" fill="{c}"><title>{nm} 第{i+1}名 ${v:,.0f}</title></circle>')
    lx = L_
    for nm, vals, c in series:
        lab = f"{nm}（top20合计 ${sum(vals):,.0f}）"
        s.append(f'<line x1="{lx}" y1="{T-14}" x2="{lx+18}" y2="{T-14}" stroke="{c}" stroke-width="2.4"/>')
        s.append(f'<text x="{lx+23}" y="{T-10}" fill="#c9d1d9" font-size="10.5">{lab}</text>')
        lx += 23 + len(lab)*10.5 + 26
    s.append('</svg>')
    return ''.join(s)

def top20_notes():
    """Top20 各代核心投放注释条（带图）"""
    cards = [
      ('#2ea856', '夏日/情人开箱 · 核心投放', A64.get('semiramis'),
       '<b>奖池无皮肤大奖</b>（组113无超级大奖行，顶配=传奇技能书/玫瑰花瓣），<b>皮肤挂在排行榜</b>：情人跨服 Top20=永恒誓约·赛米拉 5301702（获取 4 人·获取ARPPU $411·门槛~$210，另有常驻 210718 直售 $49.99）；夏日复用赛米拉+海泽尔做开箱排行。渗透 20.1% 靠的是券稀缺，不是奖池大奖。'),
      ('#c08a17', '世界杯开箱 · 超级大奖', A64['soccer'],
       '<b>足球宝贝·爱莉希雅皮肤 5304001</b>——首个把皮肤挂进开箱<b>奖池</b>当超级大奖的开箱（前两代皮肤走排行榜 Top20/直售，不进奖池）；中层没被拉动（$100-500 占比反降），钩子在、坑位浅。'),
      ('#c08a17', '世界杯跨服榜 1-5 名 · 头衔', A64['title'],
       '<b>世界之巅头衔 82004</b>（组30581-84）——点燃塔尖 $1,415/$1,330 两人=头衔竞争付费力的直接证据；第 3 名起回落，缺向下分层。'),
      ('#4691e8', '深海转盘 · 核心大奖', A64['sub'],
       '<b>深海猎手·潜艇行军皮 15065</b>（奖池组321超级大奖）——外显钩子在，但逐档限购 $585 买光墙把深度锁死，Top3 齐顶封顶值。'),
    ]
    h = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px">']
    for c, t, img, txt in cards:
        imghtml = (f'<img src="{img}" style="height:96px;max-width:100%;object-fit:contain;border-radius:4px;display:block;margin:0 auto 8px">'
                   if img else '<div style="height:96px;display:flex;align-items:center;justify-content:center;color:#484f58;font-size:22px;margin-bottom:8px">—</div>')
        h.append(f'<div style="background:#0d1117;border:1px solid #30363d;border-top:3px solid {c};border-radius:6px;padding:12px">'
                 f'<div style="font-size:10.5px;font-weight:700;color:{c};letter-spacing:.5px;margin-bottom:8px">{t}</div>'
                 f'{imghtml}<div style="font-size:11px;line-height:1.7;color:#8b949e">{txt}</div></div>')
    h.append('</div>')
    return ''.join(h)

def anchor_card():
    gens = [('元旦锚点','纯券·无钻VIP'), ('情人节锚点','纯券·无钻VIP'), ('夏日锚点','纯券·无钻VIP'), ('世界杯锚点','✦补钻石+VIP(6/24)')]
    kx_buyers = {'元旦锚点':'元旦开箱','情人节锚点':'情人节开箱','夏日锚点':'夏日开箱','世界杯锚点':'世界杯开箱'}
    tr = ['<table><tr><th class="l">代际（无服过滤口径*）</th><th class="l">配置状态</th><th>收入</th><th>买家</th><th>占开箱买家</th><th>ARPPU</th><th>复购</th><th>max</th></tr>']
    for name, cfg in gens:
        a = AN[name]; kb = KG[kx_buyers[name]]['buyers']
        hl = ' class="row-a"' if '世界杯' in name else ''
        tr.append(f"<tr{hl}><td class='l'><b>{name}</b></td><td class='l'>{cfg}</td><td>{fmt(a['rev'])}</td><td>{a['buyers']}</td>"
                  f"<td>{a['buyers']/kb*100:.0f}%</td><td>${a['arppu']:.1f}</td><td>{a['opb']:.1f}</td><td>{fmt(a['max'])}</td></tr>")
    tr.append('</table>')
    tr.append('<div style="height:10px"></div><table><tr><th class="l">世界杯锚点按档</th><th>收入</th><th>买家</th><th>ARPPU</th><th>复购</th><th>max</th></tr>')
    for t in ['WC档$4.99','WC档$19.99','WC档$49.99','WC档$99.99']:
        a = AN[t]
        tr.append(f"<tr><td class='l'><b>{t.replace('WC档','')}</b></td><td>{fmt(a['rev'])}</td><td>{a['buyers']}</td><td>${a['arppu']:.1f}</td><td>{a['opb']:.1f}</td><td>{fmt(a['max'])}</td></tr>")
    tr.append('</table>')
    tr.append("<div class='dim' style='margin-top:6px'>*本卡四代统一不加服过滤（各代全部部署服），与 01 章历史数据对比表（按服段筛选）绝对值不同；占开箱买家分母=同口径开箱族买家。</div>")
    return ''.join(tr)

def perserver_card():
    rows = []
    for label, win in [('世界杯开箱', f'6/26-{END[5:]}·拉通'), ('夏日开箱', '5/29-6/8·11天拉通')]:
        ps = PS[label]; n = len(ps)
        tot = sum(r['rev'] for r in ps); t1 = sorted(r['top1'] for r in ps)
        b = sum(r['buyers'] for r in ps)
        t1_100 = sum(1 for v in t1 if v >= 100)
        rows.append((label, win, n, tot/n, b/n, t1[n//2], max(t1), t1_100, t1_100/n*100))
    tr = ['<table><tr><th class="l">代际（拉通口径）</th><th>有开箱流水的服</th><th>服均收入</th><th>服均买家</th><th>每服top1中位</th><th>每服top1最高</th><th>top1≥$100的服</th></tr>']
    for label, win, n, avg, bavg, t1med, t1max, n100, p100 in rows:
        hl = ' class="row-a"' if '世界杯' in label else ''
        tr.append(f"<tr{hl}><td class='l'><b>{label}</b><span class='dim'>　{win}</span></td><td>{n}</td><td>{fmt(avg)}</td>"
                  f"<td>{bavg:.1f}</td><td>{fmt(t1med)}</td><td>{fmt(t1max)}</td><td>{n100}（{p100:.0f}%）</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

ps_rev = {'夏日': {r['sid']: r for r in PS['夏日开箱']}, '世界杯': {r['sid']: r for r in PS['世界杯开箱']}}
def agg(label, lo, hi):
    P = PR[f"{label}_payers"]; K = PR[f"{label}_kxbuyers"]; RV = ps_rev[label]
    pay = sum(v for k, v in P.items() if lo <= int(k) <= hi)
    kb = sum(v for k, v in K.items() if lo <= int(k) <= hi)
    rev = sum(r['rev'] for sid, r in RV.items() if lo <= int(sid) <= hi)
    return dict(kb=kb, pay=pay, pr=kb/pay*100 if pay else 0, rev=rev, arppu=rev/kb if kb else 0)

def payrate_drill():
    """开箱付费率下钻：同服段对齐 + 券供给对比 + 档位买家梯子"""
    rows_a = [('夏日 · 老服成熟段 1000-1870（同段基准）', agg('夏日', 1000, 1870), '#2ea856'),
              ('世界杯 · 老服成熟段 1000-1870', agg('世界杯', 1000, 1870), '#c08a17'),
              ('世界杯 · 年轻老服 1880-1970', agg('世界杯', 1880, 1970), '#c08a17'),
              ('世界杯 · 扩服新服 1980-2250', agg('世界杯', 1980, 2250), '#c08a17')]
    t = ['<table><tr><th class="l">新老服拆分（同段对齐）</th><th>收入</th><th>开箱买家</th><th>该段总付费人数</th><th>付费玩家付费率</th><th>ARPPU</th></tr>']
    for name, m, c in rows_a:
        hl = ' class="row-a"' if '世界杯 · 老服成熟段' in name else ''
        bar = f'<div style="height:8px;width:{m["pr"]*10:.0f}px;max-width:220px;background:{c};border-radius:4px;display:inline-block;margin-right:8px;vertical-align:middle"></div>'
        t.append(f"<tr{hl}><td class='l'><b>{name}</b></td><td>{fmt(m['rev'])}</td><td>{m['kb']}</td><td>{m['pay']:,}</td>"
                 f"<td class='l'>{bar}<b>{m['pr']:.1f}%</b></td><td>${m['arppu']:.0f}</td></tr>")
    t.append('</table>')

    _tsrc = json.load(open(os.path.join(HERE, '_ticket_sources.json'), encoding='utf-8'))
    _free = next(x for x in _tsrc if x['src'] == '免费竞猜档')
    wc_free = int(float(_free['qty'])); wc_free_u = _free['u']
    sm_u, sm_q = TKS['summer_total']['u'], TKS['summer_total']['qty']
    wc_u, wc_q = TKS['wc_total']['u'], float(TKS['wc_total']['qty'])
    t.append('<div style="height:12px"></div><table><tr><th class="l">开箱券供给对比（获取侧 asset 全量）</th><th>券触达人数</th><th>总发放量</th><th>人均</th></tr>')
    t.append(f"<tr><td class='l'><b>夏日券 1134</b>（无大众免费水管）</td><td>{sm_u:,}</td><td>{sm_q:,.0f}</td><td>{sm_q/sm_u:.0f} 张</td></tr>")
    t.append(f"<tr class='row-a'><td class='l'><b>世界杯券 1146</b>（竞猜免费档+中奖邮件两条大水管）</td><td>{wc_u:,}<span class='dim'>（×{wc_u/sm_u:.1f}）</span></td><td>{wc_q:,.0f}<span class='dim'>（×{wc_q/sm_q:.1f}）</span></td><td>{wc_q/wc_u:.0f} 张</td></tr>")
    t.append(f"<tr><td class='l'>└ 其中：竞猜免费档直发</td><td>{wc_free_u:,}</td><td>{wc_free:,}</td><td class='dim'>另有中奖邮件加送（百万级）</td></tr>")
    t.append('</table>')

    sm_t = {x['iap']: x['buyers'] for x in PR['夏日_tiers']}
    wc_t = {x['iap']: x['buyers'] for x in PR['世界杯_tiers']}
    t.append('<div style="height:12px"></div><table><tr><th class="l">档位买家梯子（连锁5档 + 锚点首档）</th><th>$4.99</th><th>$9.99</th><th>$19.99</th><th>$49.99</th><th>$99.99</th><th>锚点$4.99</th></tr>')
    t.append(f"<tr><td class='l'><b>夏日</b></td><td><b>{sm_t.get('210702',0)}</b></td><td>{sm_t.get('210704',0)}</td><td>{sm_t.get('210706',0)}</td><td>{sm_t.get('210708',0)}</td><td>{sm_t.get('210710',0)}</td><td>{sm_t.get('210712',0)}</td></tr>")
    t.append(f"<tr><td class='l'><b>世界杯（全服）</b></td><td><b>{wc_t.get('211002',0)}</b></td><td>{wc_t.get('211004',0)}</td><td>{wc_t.get('211006',0)}</td><td>{wc_t.get('211008',0)}</td><td>{wc_t.get('211010',0)}</td><td>{wc_t.get('211012',0)}</td></tr>")
    t.append('</table>')
    return ''.join(t)

# ============ 预生成片段（避免 f-string 转义坑）============
HT_TABLE = kx_table()
HT_PANELS = kx_panels()
HT_DISTA = kx_dist_chart('bucketA', 10, 10, lambda i: f'${i*10}-{i*10+10}', '>$100', '图A · 大众段 $0-100（每$10一档 · 纵轴=买家占比）')
HT_DISTB = kx_dist_chart('bucketB', 19, 100, lambda i: (f'${(i+1)*100}-{(i+2)*100}' if i < 9 else f'${(i+1)/10:.1f}k-{(i+2)/10:.1f}k'), '>$2k', '图B · $100 以上（每$100一档 · 横轴=单人付费区间）')
HT_TOP20 = kx_top20_chart()
HT_NOTES = top20_notes()
HT_ANCHOR = anchor_card()
HT_PERSRV = perserver_card()
HT_PAYRATE = payrate_drill()

SM_OLD = agg('夏日', 1000, 1870)     # 夏日老服成熟段
WC_OLD = agg('世界杯', 1000, 1870)   # 世界杯老服成熟段
TICKET_X = TKS['wc_total']['u'] / TKS['summer_total']['u']   # 券触达倍数

# ============ page ============
page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 世界杯开箱回归 — tap4fun</title>
<style>
:root{{--dark:#0d1117;--card:#161b22;--border:#30363d;--text:#c9d1d9;--head:#f0f6fc;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--dark);color:var(--text);font-size:13.5px;display:flex;min-height:100vh}}
.sidebar{{width:220px;background:var(--dark);border-right:1px solid var(--border);position:fixed;top:0;left:0;bottom:0;overflow-y:auto;z-index:10}}
.sb-logo{{padding:20px 18px 12px;border-bottom:1px solid var(--border)}}
.sb-logo .brand{{font-size:18px;font-weight:800;color:var(--head)}} .sb-logo .brand span{{color:var(--accent)}}
.sb-logo .sub{{font-size:10.5px;color:#484f58;margin-top:2px;letter-spacing:.5px}}
.sb-nav{{padding:12px 0}}
.sb-item{{display:block;padding:9px 18px;font-size:12.5px;color:#8b949e;text-decoration:none;border-left:3px solid transparent}}
.sb-item:hover{{background:#21262d;color:var(--head)}}
.sb-label{{padding:10px 18px 4px;font-size:10px;font-weight:700;letter-spacing:1.5px;color:#484f58;text-transform:uppercase}}
.content{{margin-left:220px;flex:1}}
.hero-bar{{background:linear-gradient(135deg,#0d1117,#161b22);border-bottom:1px solid var(--border);padding:28px 48px}}
.hero-bar h1{{font-size:1.5em;font-weight:800;color:var(--head);line-height:1.3}}
.hero-bar h1 em{{color:var(--yellow);font-style:normal}}
.hero-bar .meta{{font-size:11.5px;color:#484f58;margin-top:6px}} .hero-bar .meta b{{color:var(--accent)}}
.page{{padding:24px 48px 48px}}
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}}
.kpi{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;border-top:3px solid var(--accent)}}
.kpi.g{{border-top-color:var(--green)}} .kpi.r{{border-top-color:var(--red)}} .kpi.y{{border-top-color:var(--yellow)}}
.kpi-val{{font-size:1.9em;font-weight:800;color:var(--head)}}
.kpi-lbl{{font-size:11.5px;color:#8b949e;margin-top:5px;font-weight:600}}
.kpi-sub{{font-size:11px;color:#484f58;margin-top:3px}}
.sec{{scroll-margin-top:20px}}
.sec-head{{display:flex;align-items:center;gap:10px;margin:28px 0 12px}}
.sec-num{{width:26px;height:26px;border-radius:50%;background:var(--accent);color:#0d1117;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center}}
.sec-title{{font-size:15px;font-weight:700;color:var(--head)}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 22px;margin-bottom:14px}}
.ct{{font-size:11px;font-weight:700;color:#8b949e;letter-spacing:.5px;text-transform:uppercase;border-left:3px solid var(--accent);padding-left:10px;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#21262d;color:var(--head);padding:8px 10px;text-align:center;font-weight:600;border-bottom:1px solid var(--border)}}
th.l,td.l{{text-align:left}}
td{{padding:9px 10px;border-bottom:1px solid #21262d;text-align:center;vertical-align:top;line-height:1.6}}
tr:hover td{{background:#161b2299}}
.dim{{color:#484f58;font-size:11px}}
.row-a{{background:#21262d!important}} .row-a td{{color:var(--head);font-weight:700}}
td.r{{color:var(--red);font-weight:700}} td.g{{color:var(--green)}} td.y{{color:var(--yellow);font-weight:700}}
.bigcon{{background:linear-gradient(135deg,#1b2436,#161b22);border:1px solid var(--border);border-left:4px solid var(--yellow);border-radius:8px;padding:16px 20px;font-size:14.5px;line-height:2;color:var(--text);margin-bottom:14px}} .bigcon b{{color:var(--head)}}
.con-link{{font-size:11px;font-weight:700;color:var(--accent);text-decoration:none;background:#0d2137;border:1px solid #1f6feb44;border-radius:20px;padding:1px 10px;margin-left:2px}}
.con-link:hover{{background:#1f6feb;color:#fff}}
.backtop{{margin-left:auto;font-size:11px;font-weight:600;color:#8b949e;text-decoration:none;border:1px solid var(--border);border-radius:20px;padding:3px 11px}}
.backtop:hover{{color:var(--head);background:#21262d}}
.vlin{{display:block;margin-bottom:14px}}
.vc{{background:#0d2137;border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;font-size:14px;font-weight:700;color:var(--head);line-height:1.9;margin-bottom:10px}}
td b{{color:var(--head)}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">WC LUCKYBOX REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">世界杯开箱回归</div>
    <a class="sb-item" href="#seckx">结论先行</a>
    <a class="sb-item" href="#ksec1">01 · 历史数据对比</a>
    <a class="sb-item" href="#ksec2">02 · 付费深度分布 · 转化率</a>
    <a class="sb-item" href="#ksec3">03 · 皮肤/头衔 · Top20</a>
    <a class="sb-item" href="#ksec4">04 · 付费率下钻 · 券供给</a>
    <a class="sb-item" href="#ksec5">05 · 本服排行榜</a>
    <a class="sb-item" href="#ksec6">06 · 锚点礼包</a>
    <a class="sb-item" href="母题4_改动效果清单_{END.replace('-','')}.html">← 返回双节回归总页</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 世界杯开箱回归<br><em>本体接近夏日 · 未被叠开与竞猜挤压 · 唯一结构性正信号 = 外显进付费档</em></h1>
  <div class="meta">窗口 <b>6/26-{END[5:]} · 全服</b>（跨窗对比一律用老服段 1000-1870） · 数据 <b>Trino v1090 订单+资产</b> · 生成 {now}</div>
</div>

<div class="page">
<div class="sec" id="seckx"><div class="sec-head"><div class="sec-num">★</div><div class="sec-title">世界杯开箱回归 · 整体结论（6/26-{END[5:]}）</div></div>
<div class="bigcon">总判词：<b>世界杯开箱本体付费效果接近夏日，没有受到双节叠开和竞猜礼包的挤压，效果稳定——可以继续开；本服排行榜目前效果比较有限，需要调整投放提升吸引力。</b>人均三代横盘（ARPPU ${G_VT['合并']['arppu']:.0f} → ${G_SM['合并']['arppu']:.0f} → ${G_WC['合并']['arppu']:.0f}、复购 {G_WC['合并']['opb']:.1f} 单持平），收入放大到 {fmt(KX['rev'])}（族口径 · 三代最高）主要来自服基数与 20 天长窗。五条核心结论：<br>
<span style="font-size:13px;line-height:2.05">
① <b>头衔+排行榜有效（仅限玩家对深度有需求的排行）</b>——跨服榜 1-5 名挂"世界之巅"头衔，点燃塔尖 $1,415/$1,330 两个极值=六代首次破 $707 买光墙；但只传导到前 2 名，缺向下分层的梯子 <a class="con-link" href="#kx4">03 · Top20 阶梯 ↓</a><br>
② <b>本服排行榜需增加有效投放</b>——窗口近 2 倍长，每服 top1 中位 $60 反而低于夏日 $75、服均仅持平（客户端本服 Tab 已确认露出，"效果有限"判定坐实） <a class="con-link" href="#kx6">05 · 本服排行榜 ↓</a><br>
③ <b>特殊形式礼包加付费深度有效：没有挤压到原有活动付费</b>——开箱本体三代横盘稳定的前提下，竞猜/外显档是净增量；竞猜抢走的不是开箱的钱，是开箱的低档买家（券免费供给替代 $4.99 入场档） <a class="con-link" href="#kx1">01 · 历史数据对比 ↓</a><br>
④ <b>世界杯皮肤转视频基本不影响收入（Top20 稳定）</b>——可拓展皮肤投放量、提升皮肤品质，做双层排行榜需求（类似 P2 主城皮肤高低档分层） <a class="con-link" href="#kx4">03 · 皮肤/头衔 ↓</a><br>
⑤ <b>锚点礼包加 VIP 点数：无影响</b>——买家 ×2.8 为服基数效应；「可复购」归因经配置 diff 证伪（限购配置与前代完全一致） <a class="con-link" href="#kx5">06 · 锚点礼包 ↓</a>
</span></div>

<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{fmt(KX['rev'])}</div><div class="kpi-lbl">开箱族收入 · {KX['buyers']} 买家（三代最多）</div><div class="kpi-sub">连锁 {fmt(wm['开箱福箱连锁']['rev'])} + 券锚点 {fmt(wm['开箱券锚点(可复购)']['rev'])} · 全服口径</div></div>
  <div class="kpi"><div class="kpi-val">${G_WC['合并']['arppu']:.0f}</div><div class="kpi-lbl">ARPPU · 三代横盘</div><div class="kpi-sub">情人 ${G_VT['合并']['arppu']:.0f} → 夏日 ${G_SM['合并']['arppu']:.0f} → 世界杯 ${G_WC['合并']['arppu']:.0f} · 复购 {G_WC['合并']['opb']:.1f} 单</div></div>
  <div class="kpi y"><div class="kpi-val">{fmt(G_WC['合并']['max'])}</div><div class="kpi-lbl">单人 max · 六代首次破 $707 买光墙</div><div class="kpi-sub">跨服榜头衔塔尖竞争（Top2 $1,415/$1,330 · 第 3 名起回落 $535）</div></div>
  <div class="kpi r"><div class="kpi-val">{SM_OLD['pr']:.1f}% → {WC_OLD['pr']:.1f}%</div><div class="kpi-lbl">老服成熟段付费率（同段对齐）</div><div class="kpi-sub">券触达 ×{TICKET_X:.1f} 免费供给替代低档买家 · ARPPU 反升（${SM_OLD['arppu']:.0f}→${WC_OLD['arppu']:.0f}）</div></div>
</div>

<div class="cb cb-info" style="margin:0 0 14px">后续动作已立项 = <b>皮肤开箱优化方案 v1</b>（【$100前】随机礼包双轨 / 【$100后】累充加 $500 档直投老行军皮自选宝箱 / 【货架】外显直售）<a class="con-link" style="margin-left:6px" href="../../产出-数值设计/X3_皮肤开箱优化/皮肤开箱优化方案_v1_20260716.html">方案页 →</a></div>

<div class="sec" id="ksec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">历史数据对比（情人节 / 夏日 / 世界杯）</div><a class="backtop" href="#seckx">↑ 整体结论</a></div></div>
<div class="vlin" id="kx1"><div class="vc">人均三代横盘（${G_VT['合并']['arppu']:.0f} → ${G_SM['合并']['arppu']:.0f} → ${G_WC['合并']['arppu']:.0f}）、复购持平——本体效果 = 正常水平；规模（买家 {G_WC['合并']['buyers']}）与 max 极值（{fmt(G_WC['合并']['max'])}）的增长主要来自服基数和 20 天长窗。</div>
<div class="card"><div class="ct">历史数据对比 · 绝对值受服数/窗口影响，看比率 · 付费率分母见表下注</div>
{HT_TABLE}<div style="height:10px"></div>{HT_PANELS}
<div class="cb cb-info">⚠️引用口径注：07-13 报告的"人均 $65 / +35% 爬升"是 D0-D10 同窗口径，全窗被长尾稀释后不成立——引用开箱人均数据一律以本表全窗口径（三代横盘）为准。</div>
</div></div>

<div class="sec" id="ksec2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">付费深度分布 · 转化率（四代 · 含元旦）</div><a class="backtop" href="#seckx">↑ 整体结论</a></div></div>
<div class="vlin" id="kx2"><div class="vc">大众段（$0-100）四代分布几乎完全重合——形式改动没有改变大众付费结构。</div>
<div class="card"><div class="ct">四代开箱付费分布 · 大众段（纵轴=买家占比）</div>
{HT_DISTA}
</div></div>
<div class="vlin" id="kx3"><div class="vc">中层（$100-500）没有加深，世界杯只在最右端开了一条缝（max {fmt(G_WC['合并']['max'])}，六代首次过 $707）——皮肤大奖只点燃 1-2 个个体，$100+ 占比反而略降（16%→14%→12%）。</div>
<div class="card"><div class="ct">四代开箱付费分布 · $100 以上（分母同为该代全部买家）</div>
{HT_DISTB}
<div class="cb cb-info">转化率卡点（皮肤开箱优化方案的核心依据）：花到 ≥$200 还有 8.0%、≥$300 还有 5.2%、<b>≥$500 骤降到 0.8%</b>（夏日同构 5.7%→0.4%）——玩家走得到 $200-300、走不过 $500，不是不肯花是没目标（对照 P2 圣诞 GACHA ≥$500 存留 -51% 正常斜率）；$200-500 投放位=卡点入口。</div>
</div></div>

<div class="sec" id="ksec3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">皮肤 / 头衔 · Top20 付费阶梯</div><a class="backtop" href="#seckx">↑ 整体结论</a></div></div>
<div class="vlin" id="kx4"><div class="vc">头衔在塔尖有效、但只传导到前 2 名——跨服榜第 1-5 名挂"世界之巅"头衔（配置实证），全服 Top2 的 $1,415/$1,330 极值就是争头衔的塔尖竞争；但第 3 名起立刻回落到 $535，Top20 群体、分位数 p95/p99 都没被拉起——头衔证明了外显竞争的付费力，缺的是向下分层的梯子（P2 式 top3 染色/top30 分层让更多人咬）。老服 ARPPU $48→$52 的"深度提高"主要是构成效应（免费券替代低档买家后的均值抬升），不是群体加深。</div>
<div class="card"><div class="ct">Top20 付费额度阶梯 · 悬停看每名次金额 · 下方=各代核心投放注释</div>
{HT_TOP20}
{HT_NOTES}
<div class="cb cb-info">读法对照 P2 圣诞（上榜线 $1,444/上榜者中位 $2,529，排行皮肤+染色分层让 Top30 互相咬）：X3 头衔只有 1 档、皮肤 top20+ 人人一样，没有分层就没有梯队——世界杯全服 Top2 与第 3 名之间 $800 的断崖就是"缺梯子"的形状。皮肤大奖（足球宝贝 5304001，首次进开箱奖池；前两代皮肤挂排行榜 Top20）未系统性抬头部：p95/p99（$302/$460）均在历代区间内——<b>有钩没梯</b>。</div>
</div></div>

<div class="sec" id="ksec4"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">付费率下钻 · 新老服 × 券供给</div><a class="backtop" href="#seckx">↑ 整体结论</a></div></div>
<div class="vlin" id="kx7"><div class="vc">付费率差距两层：①新服稀释——扩服段只有 {agg('世界杯',1980,2250)['pr']:.1f}%，把全口径拉到 9.6%；②老服成熟段真实下降 {SM_OLD['pr']:.1f}% → {WC_OLD['pr']:.1f}%（买家 {SM_OLD['kb']} → {WC_OLD['kb']} 近腰斩），主因是券供给结构变了：世界杯把开箱券做成竞猜大众奖励，券触达 ×{TICKET_X:.1f}（{TKS['summer_total']['u']:,} → {TKS['wc_total']['u']:,} 人），免费供给替代了 $4.99 入场档的购买动机。夏日付费率的"强点"= 券稀缺、想抽就得买。ARPPU 反而更高（${WC_OLD['arppu']:.0f} vs ${SM_OLD['arppu']:.0f}）——竞猜抢走的不是开箱的钱，是开箱的低档买家。</div>
<div class="card"><div class="ct">新老服拆分 · 券供给对比 · 档位买家梯子</div>
{HT_PAYRATE}
<div class="cb cb-info">口径注：①窗口机械效应已排除——世界杯 20 天成熟段总付费人数（{WC_OLD['pay']:,}）反而少于夏日 11 天（{SM_OLD['pay']:,}），分母没有被长窗撑大；②券来源按 reason 前缀分类有少量污染，但两代总供给/触达对比与免费竞猜档直发数（894尾0）干净；③中奖邮件加送券为"其他"桶主体（百万级）。<b>启示：抽奖券的免费发放量要和入场档定价联动设计——大众免费水管开多大，入场档就废多少</b>（马戏节扭蛋机照此校准）。</div>
</div></div>

<div class="sec" id="ksec5"><div class="sec-head"><div class="sec-num">05</div><div class="sec-title">本服排行榜（W5）</div><a class="backtop" href="#seckx">↑ 整体结论</a></div></div>
<div class="vlin" id="kx6"><div class="vc">本服排行榜效果有限（客户端本服 Tab 已确认露出，判定坐实）——窗口近 2 倍长，每服 top1 中位 $60 反而低于夏日 $75，服均仅持平；需要调整投放提升吸引力。</div>
<div class="card"><div class="ct">逐服开箱付费对比 · 榜=活动全程拉通累计</div>
{HT_PERSRV}
<div class="cb cb-info">露出已确认（07-21）：客户端本服 Tab 实际有显示——"效果有限"是投放吸引力问题，不是"没上线"。后续投放调整已在皮肤开箱优化方案落地=本服榜前 3 名象征性投放（累充 $500 档皮肤自选宝箱为深度主承接）。</div>
</div></div>

<div class="sec" id="ksec6"><div class="sec-head"><div class="sec-num">06</div><div class="sec-title">锚点礼包（W2/W4/W5 关联）</div><a class="backtop" href="#seckx">↑ 整体结论</a></div></div>
<div class="vlin" id="kx5"><div class="vc">锚点 = 正常的 $4.99 小额位；买家 153 人的增长主要是服基数效应（扩服 28+年轻服），不是改动的正向效果；「可复购」是伪归因（配置与前代完全一致）。</div>
<div class="card"><div class="ct">锚点礼包四代对比 + 世界杯锚点按档拆分</div>
{HT_ANCHOR}
<div class="cb cb-info">配置 diff：211012-15 与情人 210712-15 限购列完全一致（差异仅 id/备注/奖励组），情人锚点 max $910 证明前代本来就能复购。95% 买家集中 $4.99 档、高档无人（$49.99 两人 / $99.99 三人）= 价格锚+小额位定位的正常发挥；锚点 ARPPU $19（轻量复购者）拉渗透不拉深度，当不了深度工具。</div>
</div></div>

<div class="footer">X3 世界杯开箱回归 · 窗口 6/26-{END[5:]} · 数据源=Trino v1090（_kaixiang_compare.py / _kaixiang_deep.py / _anchor_compare.py / _kx_payrate.py / _refresh_inline.py） · 生成 {now}</div>
</div>
</div>
</body></html>"""
open(OUT, 'w', encoding='utf-8').write(page)
print('OK ->', OUT)
