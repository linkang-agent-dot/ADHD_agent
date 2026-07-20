# -*- coding: utf-8 -*-
"""
X3 深海大富翁族回归 · 独立报告生成器（07-20 用户定：单独开页，线性编号章节不用小页签）
数据源 = _monopoly_deep.json / _ds_monopoly_dist.json / _p2_monopoly_may.json / _p2_monopoly_fests.json
       + _kaixiang_deep.json（世界杯开箱对照桶） + _l1_m4.json（深海L1）
用法: python _gen_大富翁回归.py
builder 复制自 _gen_母题4.py（竞猜页同款先例：改大富翁视图只改本生成器）。
"""
import sys, json, os, datetime
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, '_l1_m4.json'), encoding='utf-8'))
END = L['END']
DS = L['深海节']; dm = DS['modules']
MD = json.load(open(os.path.join(HERE, '_monopoly_deep.json'), encoding='utf-8'))
DSM = json.load(open(os.path.join(HERE, '_ds_monopoly_dist.json'), encoding='utf-8'))
P2M = json.load(open(os.path.join(HERE, '_p2_monopoly_may.json'), encoding='utf-8'))
P2F = json.load(open(os.path.join(HERE, '_p2_monopoly_fests.json'), encoding='utf-8'))
KD = json.load(open(os.path.join(HERE, '_kaixiang_deep.json'), encoding='utf-8'))
KG = KD['gens']
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
OUT = os.path.join(HERE, f"深海大富翁回归_{END.replace('-','')}.html")

def fmt(v): return f"${v:,.0f}"

FAM_TOT = sum(MD['deepsea_components'][k]['rev'] for k in MD['deepsea_components'])

# ============ builders（复制自 _gen_母题4.py D3 章） ============

def family_dissect_card():
    order=['成就礼包','BP大富翁线','存钱罐','罗盘连锁']
    form={'成就礼包':'阶梯买断','BP大富翁线':'通行证 · 硬封顶$30','存钱罐':'单笔买断','罗盘连锁':'连锁 · 可复购'}
    comp=MD['deepsea_components']; tot=sum(comp[k]['rev'] for k in order)
    tr=['<table><tr><th class="l">族内件</th><th>收入</th><th>买家</th><th>ARPPU</th><th>复购</th><th>max</th><th class="l">付费形态</th></tr>']
    for k in order:
        m=comp[k]; hl=' class="row-a"' if k=='罗盘连锁' else ''
        tr.append(f"<tr{hl}><td class='l'><b>{k}</b></td><td>{fmt(m['rev'])}</td><td>{m['buyers']}</td><td>${m['arppu']:.1f}</td><td>{m['opb']:.1f}单</td><td>{fmt(m['max'])}</td><td class='l dim'>{form[k]}</td></tr>")
    tr.append(f"<tr><td class='l'><b>族合计</b></td><td><b>{fmt(tot)}</b></td><td class='l dim' colspan='5'>四件里三件是买断制（复购 1-2 单、硬封顶 $20-687）；唯一可复购的罗盘连锁（3.1 单/max $255）只覆盖 138 人</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

def dice_survival_chart():
    TH = [1,20,50,100,150,250,350,500,700]
    allv  = [MD['survival']['all'][str(t)] for t in TH]
    freev = [MD['survival']['free'][str(t)] for t in TH]
    payv  = [MD['survival']['payer'][str(t)] for t in TH]
    series = [
      (f"全量掷骰玩家", allv,  '#4691e8', 2.4),
      (f"白嫖玩家",     freev, '#8b949e', 1.9),
      (f"族付费玩家",   payv,  '#c08a17', 2.2),
    ]
    W,H,L_,R,T,B = 1160,344,58,132,46,56
    pw,ph = W-L_-R, H-T-B
    vmax = max(allv)*1.1
    def X(i): return L_+pw*i/(len(TH)-1)
    def Y(v): return T+ph*(1-v/vmax)
    sv=[f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L_}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">大富翁进度停留 · 累计掷骰次数 ≥N 的玩家数（横轴=阶段奖档 抽20/50/…/700）</text>')
    for gv in range(0,int(vmax)+1,1000):
        sv.append(f'<line x1="{L_}" y1="{Y(gv):.0f}" x2="{W-R}" y2="{Y(gv):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L_-6}" y="{Y(gv)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">{gv//1000 if gv else 0}k</text>')
    ia,ib = TH.index(350), TH.index(500)
    sv.append(f'<rect x="{X(ia):.0f}" y="{T}" width="{X(ib)-X(ia):.0f}" height="{ph}" fill="#f85149" fill-opacity="0.09"/>')
    dropf = (freev[ib]/freev[ia]-1)*100
    sv.append(f'<text x="{(X(ia)+X(ib))/2:.0f}" y="{T+15}" fill="#f85149" font-size="11" font-weight="700" text-anchor="middle">免费墙</text>')
    sv.append(f'<text x="{(X(ia)+X(ib))/2:.0f}" y="{T+30}" fill="#f85149" font-size="10" text-anchor="middle">白嫖 {freev[ia]:,}→{freev[ib]:,} ({dropf:.0f}%)</text>')
    for i,t in enumerate(TH):
        sv.append(f'<text x="{X(i):.0f}" y="{H-36}" fill="#8b949e" font-size="10.5" text-anchor="middle">≥{t}</text>')
    for nm,vals,c,wgt in series:
        pts=' L '.join(f'{X(i):.0f} {Y(v):.0f}' for i,v in enumerate(vals))
        sv.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i,v in enumerate(vals):
            sv.append(f'<circle cx="{X(i):.0f}" cy="{Y(v):.0f}" r="3" fill="{c}"><title>{nm} ≥{TH[i]}次: {v:,}人</title></circle>')
    ly=T+8
    labels=[(f"全量 {MD['dice_total_players']:,}人",'#4691e8'),(f"白嫖 {MD['dice_free']:,}人",'#8b949e'),(f"族付费 {MD['dice_payers']}人",'#c08a17')]
    for nm,c in labels:
        sv.append(f'<line x1="{W-R+8}" y1="{ly}" x2="{W-R+24}" y2="{ly}" stroke="{c}" stroke-width="2.6"/>')
        sv.append(f'<text x="{W-R+28}" y="{ly+4}" fill="#c9d1d9" font-size="10">{nm}</text>')
        ly+=20
    sv.append('</svg>')
    return ''.join(sv)

def dice_decay_table():
    TH=[1,20,50,100,150,250,350,500,700]
    cols={'全量':[MD['survival']['all'][str(t)] for t in TH],
          '白嫖':[MD['survival']['free'][str(t)] for t in TH],
          '族付费':[MD['survival']['payer'][str(t)] for t in TH]}
    tr=['<table style="margin-top:10px"><tr><th class="l">档间</th>'+''.join(f'<th>{k}</th>' for k in cols)+'<th class="l">读法</th></tr>']
    notes={('350','500'):'免费骰子耗尽墙：白嫖塌方、付费不掉'}
    for i in range(len(TH)-1):
        seg=f"≥{TH[i]} → ≥{TH[i+1]}"
        cells=[]
        for k,vals in cols.items():
            d=(vals[i+1]/vals[i]-1)*100
            cls=' class="r"' if d<=-60 else (' class="g"' if d>=-40 else '')
            cells.append(f'<td{cls}>{d:+.0f}%<span class="dim">（{vals[i]:,}→{vals[i+1]:,}）</span></td>')
        note=notes.get((str(TH[i]),str(TH[i+1])),'')
        tr.append(f'<tr><td class="l"><b>{seg}</b></td>'+''.join(cells)+f'<td class="l dim">{note}</td></tr>')
    tr.append('</table>')
    tr.append(f'<div class="dim" style="margin-top:6px">分位：全量 p50={MD["dice_pct_all"]["p50"]:.0f}次 / p99={MD["dice_pct_all"]["p99"]:.0f}；族付费 p50={MD["dice_pct_payer"]["p50"]:.0f}次 / p99={MD["dice_pct_payer"]["p99"]:.0f} / max={MD["dice_pct_payer"]["mx"]:.0f}。红=塌方≤-60%，绿=常数带≥-40%。</div>')
    return ''.join(tr)

def ds_monopoly_chart():
    TH = [10,20,50,100,200,300,500,1000]
    ds_v = [DSM['surv'][str(t)] for t in TH]
    kx_v = []
    g = KG['世界杯开箱']
    bA = {int(k): v for k, v in g['bucketA'].items()}
    bB = {int(k): v for k, v in g['bucketB'].items()}
    for t in TH:
        kx_v.append(sum(v for k, v in bA.items() if k >= t//10) if t < 100 else sum(v for k, v in bB.items() if k >= t//100))
    p2_v = [P2M['surv'][str(t)] for t in TH]
    ds_n, kx_n, p2_n = DSM['buyers'], g['buyers'], P2M['buyers']
    series = [
      (f"深海大富翁族（{ds_n}买家·max {fmt(DSM['max'])}）", [v/ds_n*100 for v in ds_v], ds_v, ds_n, '#4691e8'),
      (f"世界杯开箱（{kx_n}买家·max {fmt(g['max'])}）", [v/kx_n*100 for v in kx_v], kx_v, kx_n, '#c08a17'),
      (f"P2节日大富翁·5月拓荒窗（{p2_n:,}买家·max {fmt(P2M['max'])}）", [v/p2_n*100 for v in p2_v], p2_v, p2_n, '#8b949e'),
    ]
    W, H, L_, R, T, B = 1160, 330, 64, 24, 44, 56
    pw, ph = W-L_-R, H-T-B
    vmax = max(max(v) for _, v, _, _, _ in series)*1.12
    def X(i): return L_ + pw*i/(len(TH)-1)
    def Y(v): return T + ph*(1-v/vmax)
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L_}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">大富翁 × 开箱 × P2节日大富翁 · 花到 ≥$X 的买家占比（÷该模块全部买家）</text>')
    for gv in range(0, int(vmax)+1, 10):
        sv.append(f'<line x1="{L_}" y1="{Y(gv):.0f}" x2="{W-R}" y2="{Y(gv):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L_-6}" y="{Y(gv)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">{gv}%</text>')
    for i, t in enumerate(TH):
        sv.append(f'<text x="{X(i):.0f}" y="{H-36}" fill="#8b949e" font-size="10.5" text-anchor="middle">≥${t:,}</text>')
    ia, ib = TH.index(50), TH.index(200)
    sv.append(f'<rect x="{X(ia):.0f}" y="{T}" width="{X(ib)-X(ia):.0f}" height="{ph}" fill="#d29922" fill-opacity="0.07"/>')
    sv.append(f'<text x="{(X(ia)+X(ib))/2:.0f}" y="{T+16}" fill="#d29922" font-size="11" font-weight="700" text-anchor="middle">中段：深海大富翁 -47%/-55%/-57% vs P2 -35%/-21%/-50%（复购位差）</text>')
    for nm, pcts, cnts, n, c in series:
        wgt = 2.4 if '深海' in nm else 1.8
        pts = ' L '.join(f'{X(i):.0f} {Y(v):.0f}' for i, v in enumerate(pcts))
        sv.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(pcts):
            sv.append(f'<circle cx="{X(i):.0f}" cy="{Y(v):.0f}" r="3" fill="{c}"><title>{nm} ≥${TH[i]:,}: {v:.1f}%（{cnts[i]}人）</title></circle>')
    _ds_p = [v/ds_n*100 for v in ds_v]; _p2_p = [v/p2_n*100 for v in p2_v]
    for pcts, vals, c, dy in [(_ds_p, ds_v, '#4691e8', -14), (_p2_p, p2_v, '#8b949e', 16)]:
        for i in range(len(vals)-1):
            if vals[i] <= 0: continue
            drop = (vals[i+1]/vals[i]-1)*100
            cc = '#f85149' if drop <= -60 else c
            sv.append(f'<text x="{(X(i)+X(i+1))/2:.0f}" y="{(Y(pcts[i])+Y(pcts[i+1]))/2+dy:.0f}" fill="{cc}" font-size="9.5" font-weight="600" text-anchor="middle">{drop:+.0f}%</text>')
    lx = L_
    for nm, pcts, cnts, n, c in series:
        sv.append(f'<line x1="{lx}" y1="{H-16}" x2="{lx+16}" y2="{H-16}" stroke="{c}" stroke-width="2.2"/>')
        sv.append(f'<text x="{lx+21}" y="{H-12}" fill="#c9d1d9" font-size="10.5">{nm}</text>')
        lx += 21 + len(nm)*10.5 + 24
    sv.append('</svg>')
    return ''.join(sv)

def ds_decay_table():
    TH = [10,20,50,100,200,300,500,1000]
    g = KG['世界杯开箱']
    bA = {int(k): v for k, v in g['bucketA'].items()}
    bB = {int(k): v for k, v in g['bucketB'].items()}
    kx_v = [(sum(v for k, v in bA.items() if k >= t//10) if t < 100 else sum(v for k, v in bB.items() if k >= t//100)) for t in TH]
    cols = {'深海大富翁族': [DSM['surv'][str(t)] for t in TH],
            '世界杯开箱': kx_v,
            'P2节日大富翁(5月)': [P2M['surv'][str(t)] for t in TH]}
    tr = ['<table style="margin-top:10px"><tr><th class="l">段</th>' + ''.join(f'<th>{k}</th>' for k in cols) + '<th class="l">参照</th></tr>']
    for i in range(len(TH)-1):
        seg = f"≥${TH[i]:,} → ≥${TH[i+1]:,}"
        cells = []
        for k, vals in cols.items():
            if vals[i] <= 0:
                cells.append('<td>—</td>'); continue
            d = (vals[i+1]/vals[i]-1)*100
            cls = ' class="r"' if d <= -60 else (' class="g"' if d >= -40 else '')
            cells.append(f'<td{cls}>{d:+.0f}%<span class="dim">（{vals[i]}→{vals[i+1]}人）</span></td>')
        ref = '自然常数带 -30~40%' if i == 0 else ''
        tr.append(f'<tr><td class="l"><b>{seg}</b></td>' + ''.join(cells) + f'<td class="l dim">{ref}</td></tr>')
    tr.append('</table>')
    tr.append('<div class="dim" style="margin-top:6px">绿=在自然常数带内（≥-40%）；红=塌方（≤-60%）；括号内为人数。</div>')
    return ''.join(tr)

def p2fests_chart():
    TH = [10, 20, 50, 100, 200, 300, 500, 1000]
    ds_v = [DSM['surv'][str(t)] for t in TH]
    ds_n = DSM['buyers']
    series = [
      (f"深海大富翁族（{ds_n}买家·max {fmt(DSM['max'])}·14天）", [v/ds_n*100 for v in ds_v], ds_v, '#4691e8'),
    ]
    for fest, c in [('情人节', '#d2699e'), ('科技节', '#a371f7'), ('拓荒节', '#2ea856')]:
        w = P2F['windows'][fest]
        vv = [w['surv'][str(t)] for t in TH]
        series.append((f"P2{fest}·节日大富翁族（{w['buyers']:,}买家·max {fmt(w['max'])}）", [v/w['buyers']*100 for v in vv], vv, c))
    W, H, L_, R, T, B = 1160, 340, 64, 24, 44, 72
    pw, ph = W-L_-R, H-T-B
    vmax = max(max(v) for _, v, _, _ in series)*1.12
    def X(i): return L_ + pw*i/(len(TH)-1)
    def Y(v): return T + ph*(1-v/vmax)
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L_}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">同形式参照 · P2 三节「节日大富翁」族 vs X3 深海大富翁族 · 花到 ≥$X 的买家占比（÷该模块全部买家）</text>')
    for gv in range(0, int(vmax)+1, 10):
        sv.append(f'<line x1="{L_}" y1="{Y(gv):.0f}" x2="{W-R}" y2="{Y(gv):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L_-6}" y="{Y(gv)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">{gv}%</text>')
    for i, t in enumerate(TH):
        sv.append(f'<text x="{X(i):.0f}" y="{H-52}" fill="#8b949e" font-size="10.5" text-anchor="middle">≥${t:,}</text>')
    ia = TH.index(300)
    sv.append(f'<rect x="{X(ia):.0f}" y="{T}" width="{X(len(TH)-1)-X(ia):.0f}" height="{ph}" fill="#d29922" fill-opacity="0.07"/>')
    sv.append(f'<text x="{(X(ia)+X(len(TH)-1))/2:.0f}" y="{T+16}" fill="#d29922" font-size="11" font-weight="700" text-anchor="middle">同形式共同天花板：$300→500 P2 三节全部 -90%+ 塌方、≥$500≈0 —— P2 也没把大富翁做深</text>')
    for nm, pcts, cnts, c in series:
        wgt = 2.4 if '深海' in nm else 1.7
        pts = ' L '.join(f'{X(i):.0f} {Y(v):.0f}' for i, v in enumerate(pcts))
        sv.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="{wgt}"/>')
        for i, v in enumerate(pcts):
            sv.append(f'<circle cx="{X(i):.0f}" cy="{Y(v):.0f}" r="3" fill="{c}"><title>{nm} ≥${TH[i]:,}: {v:.1f}%（{cnts[i]:,}人）</title></circle>')
    ly = H-30
    lx = L_
    for nm, pcts, cnts, c in series:
        sv.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+16}" y2="{ly}" stroke="{c}" stroke-width="2.2"/>')
        sv.append(f'<text x="{lx+21}" y="{ly+4}" fill="#c9d1d9" font-size="10.5">{nm}</text>')
        lx += 21 + len(nm)*9.2 + 20
        if lx > W-320: lx = L_; ly += 18
    sv.append('</svg>')
    return ''.join(sv)

def p2fests_decay_table():
    TH = [10, 20, 50, 100, 200, 300, 500, 1000]
    cols = {'深海大富翁族': [DSM['surv'][str(t)] for t in TH]}
    for fest in ['情人节', '科技节', '拓荒节']:
        cols[f'P2{fest}'] = [P2F['windows'][fest]['surv'][str(t)] for t in TH]
    tr = ['<table style="margin-top:10px"><tr><th class="l">段</th>' + ''.join(f'<th>{k}</th>' for k in cols) + '<th class="l">参照</th></tr>']
    for i in range(len(TH)-1):
        seg = f"≥${TH[i]:,} → ≥${TH[i+1]:,}"
        cells = []
        for k, vals in cols.items():
            if vals[i] <= 0:
                cells.append('<td>—</td>'); continue
            d = (vals[i+1]/vals[i]-1)*100
            cls = ' class="r"' if d <= -60 else (' class="g"' if d >= -40 else '')
            cells.append(f'<td{cls}>{d:+.0f}%<span class="dim">（{vals[i]:,}→{vals[i+1]:,}）</span></td>')
        ref = '自然常数带 -30~40%' if i == 0 else ('同形式共同天花板' if TH[i] == 300 else '')
        tr.append(f'<tr><td class="l"><b>{seg}</b></td>' + ''.join(cells) + f'<td class="l dim">{ref}</td></tr>')
    tr.append('</table>')
    tr.append('<div class="dim" style="margin-top:6px">绿=常数带内（≥-40%）；红=塌方（≤-60%）。X3 中段（$50→$200）-55%/-57% 仍比 P2（-30~-53%）偏陡，但 $300→$500 段反而是 P2 三节全塌（-90%+）、X3 -60%——同形式深水区两边都没有货架。</div>')
    return ''.join(tr)

def p2fests_shelf_card():
    w = P2F['windows']['科技节']; c = w['components']
    layer = [
      ('节日大富翁', '宽入口件', '$0.99-4.99 小额进人，两千人级、复购 1.1 单——X3 无对应件（族内最低入口=BP $9.99）'),
      ('2025复活节大富翁礼包', '中段可复购件', '复购 3.2 单铺给 1,542 人——X3 对应件=罗盘连锁（复购 3.1 单）但只覆盖 138 人'),
      ('节日大富翁组队礼包', '社交件', '组队解锁小额档——X3 无对应件'),
      ('节日大富翁礼包', '深度件', 'ARPPU $181 只卖 163 人，max $447 收口——X3 对应件=成就礼包（max $687 但 ARPPU $36=没分层）'),
    ]
    tr = ['<table><tr><th class="l">P2 件（科技窗）</th><th>收入</th><th>买家</th><th>ARPPU</th><th>复购</th><th>max</th><th class="l">层位 · 与 X3 对照</th></tr>']
    for nm, lay, note in layer:
        m = c[nm]
        tr.append(f"<tr><td class='l'><b>{nm}</b></td><td>{fmt(m['rev'])}</td><td>{m['buyers']:,}</td><td>${m['arppu']:.1f}</td><td>{m['opb']:.1f}单</td><td>{fmt(m['max'])}</td><td class='l dim'><b>{lay}</b>：{note}</td></tr>")
    f3 = [(f, P2F['windows'][f]) for f in ['情人节', '科技节', '拓荒节']]
    sums = ' · '.join(f"{f} {fmt(v['rev'])}/{v['buyers']:,}人/max {fmt(v['max'])}" for f, v in f3)
    tr.append(f"<tr><td class='l'><b>三节合计参照</b></td><td class='l dim' colspan='6'>{sums}——ARPPU $27-40、max 全部 $550-780，<b>P2 同形式也是宽入口浅盘</b>（情人窗单件即全族，科技/拓荒四件分层）。</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

def server_seg_card():
    seg=MD['server_seg']; names={'mature':'成熟老服 1170-1870','young':'年轻服 1880-2010'}
    tr=['<table><tr><th class="l">服段</th><th>大富翁族买家</th><th>收入</th><th>付费玩家付费率*</th><th>ARPPU</th></tr>']
    for s in ['mature','young']:
        m=seg[s]
        tr.append(f"<tr><td class='l'><b>{names[s]}</b></td><td>{m['buyers']}</td><td>{fmt(m['rev'])}</td><td>{m['payrate']:.1f}%<span class='dim'>（分母{m['payers']:,}）</span></td><td>${m['arppu']:.1f}</td></tr>")
    tr.append('</table>')
    tr.append('<div class="dim" style="margin-top:6px">*付费玩家付费率=该服段大富翁族买家÷该服段窗口总付费人数。两段付费率(34.2%/33.0%)与 ARPPU($44.8/$43.2)几乎完全对称=新老服通吃的稳定压舱石。</div>')
    return ''.join(tr)

def family_expansion_chart():
    months=MD['chain_by_month']; comp=MD['deepsea_components']
    ds_tot=sum(comp[k]['rev'] for k in comp)
    bars=[(m['m'][5:]+'月\n连锁', m['rev'], '#3a4150') for m in months]
    bars.append(('深海\n四件套', ds_tot, '#4691e8'))
    W,H,L_,R,T,B=1160,300,56,20,64,54
    pw,ph=W-L_-R,H-T-B
    vmax=max(b[1] for b in bars)*1.14
    n=len(bars); bw=pw/n*0.6
    sv=[f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L_}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">大富翁族扩张 · 老版航海之路(纯连锁 207xxx)月度 vs 深海四件套(窗口收入)</text>')
    sv.append(f'<text x="{L_}" y="43" fill="#8b949e" font-size="11">连锁本身月度 $3-6k 随服基数缓涨；深海把盘子做到 {fmt(ds_tot)} 全靠新增件（成就礼包+BP大富翁线+存钱罐）</text>')
    for i,(nm,v,c) in enumerate(bars):
        x=L_+pw*i/n+(pw/n-bw)/2; y=T+ph*(1-v/vmax)
        sv.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{T+ph-y:.0f}" fill="{c}" rx="3"><title>{nm} {fmt(v)}</title></rect>')
        sv.append(f'<text x="{x+bw/2:.0f}" y="{y-6:.0f}" fill="#f0f6fc" font-size="10" font-weight="700" text-anchor="middle">{fmt(v)}</text>')
        for li,seg in enumerate(nm.split("\n")):
            sv.append(f'<text x="{x+bw/2:.0f}" y="{H-32+li*13}" fill="#8b949e" font-size="9.5" text-anchor="middle">{seg}</text>')
    sv.append('</svg>')
    return ''.join(sv)

# ============ page ============
page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 深海大富翁族回归 — tap4fun</title>
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
td.r{{color:var(--red);font-weight:700}} td.g{{color:var(--green)}}
.bigcon{{background:linear-gradient(135deg,#1b2436,#161b22);border:1px solid var(--border);border-left:4px solid var(--yellow);border-radius:8px;padding:16px 20px;font-size:14.5px;line-height:2;color:var(--text);margin-bottom:14px}} .bigcon b{{color:var(--head)}}
.vlin{{display:block;margin-bottom:14px}}
.vc{{background:#0d2137;border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;font-size:14px;font-weight:700;color:var(--head);line-height:1.9;margin-bottom:10px}}
td b{{color:var(--head)}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">DEEPSEA MONOPOLY REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">深海大富翁族回归</div>
    <a class="sb-item" href="#sec0">结论先行</a>
    <a class="sb-item" href="#sec1">01 · 族基本盘与分件解剖</a>
    <a class="sb-item" href="#sec2">02 · 进度停留曲线 · 免费墙</a>
    <a class="sb-item" href="#sec3">03 · 付费深度分布</a>
    <a class="sb-item" href="#sec4">04 · P2 同形式参照</a>
    <a class="sb-item" href="#sec5">05 · 新老服拆分</a>
    <a class="sb-item" href="#sec6">06 · 族扩张 · 历史坐标</a>
    <a class="sb-item" href="#sec7">07 · 结论与动作</a>
    <a class="sb-item" href="母题4_改动效果清单_{END.replace('-','')}.html">← 返回双节回归总页</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 深海大富翁族回归<br><em>压舱石实锤 · 深度靠堆买断件 · 下一步补分层货架而非做深本体</em></h1>
  <div class="meta">窗口 <b>7/3-7/16 · 59服</b>（深海 7/16 收官=终版数据） · 数据 <b>Trino v1090/v1041 订单+资产</b> · 生成 {now}</div>
</div>

<div class="page">
<div class="sec" id="sec0"><div class="sec-head"><div class="sec-num">00</div><div class="sec-title">结论先行</div></div>
<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{fmt(FAM_TOT)}</div><div class="kpi-lbl">族收入 · 深海最大玩法族</div><div class="kpi-sub">成就 $10.1k + BP线 $10.4k + 罗盘链 $3.3k + 存钱罐 $3.1k（窗口重算口径；L1 归因口径 $21.7k）</div></div>
  <div class="kpi g"><div class="kpi-val">34.2% / 33.0%</div><div class="kpi-lbl">付费玩家付费率 · 新老服通吃</div><div class="kpi-sub">深海收入模块最高（开箱 9.6% / 竞猜 4.4%），两段几乎完全对称</div></div>
  <div class="kpi"><div class="kpi-val">7,069 人</div><div class="kpi-lbl">免费活跃盘 · 总掷骰 214 万次</div><div class="kpi-sub">白嫖 6,459 + 族付费 610；免费驱动力充足</div></div>
  <div class="kpi r"><div class="kpi-val">-98%</div><div class="kpi-lbl">免费墙 · 掷骰 350→500 次白嫖塌方</div><div class="kpi-sub">2,258→42 人；能过墙的 93% 是买骰子的人</div></div>
</div>
<div class="bigcon">大结论：<b>大富翁族是深海最成功的改动——{fmt(FAM_TOT)} 压舱、付费率 34% 新老服通吃、免费活跃盘 7,069 人；但它的"深度"是堆买断件堆出来的，不是把单件做深。</b><br>
<span style="font-size:13px;line-height:2.1">
① <b>盘子做对了</b>——从老版"纯连锁 $3-6k/月"扩成"成就+连锁+存钱罐+BP 四件套 {fmt(FAM_TOT)}"，付费率 34% 是深海最高的收入模块；<br>
② <b>但深度靠堆件不靠做深</b>——四件里三件是买断制（复购 1-2 单、硬封顶 $20-687），唯一可复购的罗盘连锁只覆盖 138 人；<br>
③ <b>进度停留证明瓶颈在"续骰位"缺失</b>——白嫖玩家一路玩到 350 次（免费活跃充足），撞到 350→500 免费墙时集体阵亡（-98%），能继续的 93% 是掏钱买骰子的人：断点是<b>供给侧（免费骰子耗尽）而非驱动力</b>；<br>
④ <b>P2 同形式参照（情人/科技/拓荒「节日大富翁」）</b>——P2 也没把大富翁做深（三节 max $550-780、≥$500≈0，X3 max $792 不落后），P2 赢在分层货架（宽入口件两千人+中段可复购件千人+深度件 $180×150 人，X3 四件全挤 $20-36 中段）；且 X3 大富翁族已占深海收入 ~40%（P2 同形式仅占节日盘 6-11%）——<b>大富翁在 X3 已超载，深度增量本来就不该指望它</b>；<br>
⑤ <b>动作</b>=大富翁本体补"宽入口+中段续命"（低价续骰位），深度增量归盘内其他弹药（皮肤开箱优化方案模块 A 位置）——与 P2"大富翁当浅盘、深度交挖孔/GACHA"的分工一致。
</span></div>
</div>

<div class="sec" id="sec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">族基本盘与分件解剖</div></div>
<div class="vlin"><div class="vc">族收入 {fmt(FAM_TOT)} 由成就礼包($10.1k)与 BP大富翁线($10.4k)两大件扛起，但四件里三件是买断制、硬封顶 $20-687；唯一有复购形态的罗盘连锁（复购 3.1 单、max $255）盘子最小只 138 人——整个族的深度被买断制天花板锁死，这是"中段陡"和"免费墙无人续费"的同一个根因。</div>
<div class="card"><div class="ct">大富翁族四件解剖 · 收入/买家/ARPPU/复购/max/付费形态</div>
{family_dissect_card()}
<div class="cb cb-info">读法：BP大富翁线渗透最广（431 人）但 $30 硬封顶（$9.99+$19.99 两通行证），是渗透工具不是深度工具；存钱罐单笔 $20 买断；成就礼包阶梯买断有一定深度（max $687）但复购仅 2.0 单。<b>族里能"越玩越买"的载体（连锁）只服务了 138 人——补中段复购位=把这个能力铺给撞免费墙的几千白嫖玩家。</b></div>
</div></div>

<div class="sec" id="sec2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">进度停留曲线 · 免费墙</div></div>
<div class="vlin"><div class="vc">白嫖玩家掷骰一路走到 350 次都还有 2,258 人（免费活跃盘充足、驱动力不缺），但 350→500 次白嫖塌方 -98%（2,258→42）——这是免费骰子耗尽的硬墙；能跨过墙走到 700 次的 483 人里 93% 是族付费玩家（买骰子的人一路走到 max 3,105 次）。断点归因=供给侧（免费投放到 350 次断供），不是需求侧（想不想玩）。</div>
<div class="card"><div class="ct">进度停留 · 累计掷骰次数 survival（全量 / 白嫖 / 族付费三线 · 悬停看人数）</div>
{dice_survival_chart()}
{dice_decay_table()}
<div class="cb cb-info">口径：掷骰次数=航海罗盘 Item_1057(普通)+海神罗盘 Item_1058(精准) change_type=2 消耗次数，对齐阶段奖 OtherReward 组 100 的档位（抽 20/50/100/150/250/350/500/700）。白嫖=掷过骰但未买任何大富翁族包的玩家。<b>免费墙 = 设计意图（免产骰子对标 X2 保守量、覆盖前 6 档，深档靠付费）；问题不在墙本身，在墙前缺一个"$0.99-4.99 再买一把骰子接着走"的低价续骰位</b>——白嫖玩家撞墙时唯一的付费选项是成就礼包一次性阶梯买断，跨度太大接不住。</div>
</div></div>

<div class="sec" id="sec3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">付费深度分布（÷该模块全部买家 · 对照世界杯开箱 / P2五月浅盘）</div></div>
<div class="vlin"><div class="vc">大富翁付费额分布中段全程偏陡（$50→$200 连续 -47%/-55%/-57%，成就礼包一次性阶梯、中段无复购位）；对照世界杯开箱平滑走到 $300 撞墙、P2 节日大富翁中段最平（$50→$100 仅 -21%）——三条线三种病。</div>
<div class="card"><div class="ct">大富翁 × 开箱 × P2节日大富翁 · 花到 ≥$X 的买家占比</div>
{ds_monopoly_chart()}
{ds_decay_table()}
<div class="cb cb-info">对 X3 的启示：①中段复购位是大富翁最该抄的（P2 中段平=固定+随机+组队多复购位）；②浅盘模块不必自己做深度，但 X3 缺 P2 那个"深度承接模块"——正是模块 A 随机礼包的位置。同游戏内比较用绝对人数、跨游戏/跨规模用占比（P2 曲线左端占比低=大量 $1-10 微额买家撑大分母，宽入口的形状）。</div>
</div></div>

<div class="sec" id="sec4"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">P2 同形式参照（情人 / 科技 / 拓荒「节日大富翁」族 · 春节异族形式不同已排除）</div></div>
<div class="vlin"><div class="vc">P2 三节的「节日大富翁」族（与 X3 同形式）：三节 $60.8k-92.8k / 1,841-2,410 买家 / <b>max 全部 $550-780、≥$500≈0——P2 也没把大富翁做深，X3 max $792 单人深度并不落后</b>。P2 赢在两处：①分层货架（$4-6 宽入口件两千人 + $21-30 中段可复购件千人级 + $180 深度件只卖 ~150 人，X3 四件 ARPPU 全挤 $20-36）；②它只让大富翁当浅盘（占节日盘 6-11%），深度交给挖孔/GACHA——X3 大富翁族占深海收入 ~40% 已经超载。</div>
<div class="card"><div class="ct">同形式参照 · X3 深海 vs P2 情人/科技/拓荒（占比口径 · 窗口 14 vs 28 天、服基数不同，只比形状）</div>
{p2fests_chart()}
{p2fests_decay_table()}
</div>
<div class="card"><div class="ct">P2 分层货架解剖（科技窗为代表 · 情人窗单件全族 / 拓荒窗同构）</div>
{p2fests_shelf_card()}
<div class="cb cb-info"><b>启示：</b>①<b>续骰位定位="宽入口+中段续命件"</b>——P2 同形式的钱主要来自宽入口件（两千人小额）和中段可复购件（复购 ~3 单铺给千人级），X3 缺的正是这两件；续骰位直接收入千元级/节（2,258 撞墙白嫖 × 转化 5-10% × $0.99-4.99），价值在接人进漏斗。②<b>大富翁本体不承担深度增量</b>——同形式在 P2 三节的天花板就是 $500-800，深度增量归盘内其他弹药（模块 A 随机礼包位置）。⚠️口径注：跨游戏只比占比与形状；P2 收入=pay_price（v1041 名字匹配）；「2025复活节大富翁礼包」为历史复用名，实际是科技/拓荒窗在售的大富翁阶梯礼包；春节异族大富翁（$250k/随机轨）为春节特有形式，不作同形式参照。</div>
</div></div>

<div class="sec" id="sec5"><div class="sec-head"><div class="sec-num">05</div><div class="sec-title">新老服拆分</div></div>
<div class="vlin"><div class="vc">大富翁族在成熟老服(1170-1870)与年轻服(1880-2010)几乎完全对称：买家 313 vs 297、付费率 34.2% vs 33.0%、ARPPU $44.8 vs $43.2——不像竞猜偏新服、开箱付费率被新服稀释，大富翁族是新老服通吃的稳定压舱石。</div>
<div class="card"><div class="ct">大富翁族 · 新老服拆分（付费率分母=该段窗口总付费人数）</div>
{server_seg_card()}
<div class="cb cb-info">对照：世界杯开箱付费率被扩服稀释到 9.6%（成熟段 13.2%）、竞猜 4.4% 且参与近半来自新服。大富翁族两段付费率都在 33-34%=玩法本身黏性强、不靠新服白嫖盘撑数——这是"压舱石"判定的直接证据，也说明改造对新老服都适用。</div>
</div></div>

<div class="sec" id="sec6"><div class="sec-head"><div class="sec-num">06</div><div class="sec-title">族扩张 · 历史坐标</div></div>
<div class="vlin"><div class="vc">老版航海之路（纯连锁 207xxx）月度收入 $1.4k→$6.2k 随服基数缓涨；深海把大富翁盘子做到 {fmt(FAM_TOT)}，扩张全部来自新增件（成就礼包 $10.1k + BP大富翁线 $10.4k + 存钱罐 $3.1k），连锁本身 $3.3k 与历史月度持平——改动正确地做大了盘子，但做大的方式是"加买断件"，没有做深单件。</div>
<div class="card"><div class="ct">大富翁族扩张 · 老版纯连锁月度 vs 深海四件套</div>
{family_expansion_chart()}
<div class="cb cb-info">历史坐标读法：深海大富翁的成功=把一个月 $3-6k 的连锁小玩法，通过挂成就礼包+双 BP+存钱罐，扩成 {fmt(FAM_TOT)} 的节日压舱族——这条"堆件做大盘子"的路径马戏节可直接复用（承接深海骨架）。</div>
</div></div>

<div class="sec" id="sec7"><div class="sec-head"><div class="sec-num">07</div><div class="sec-title">结论与动作</div></div>
<div class="card">
<table><tr><th class="l">动作</th><th class="l">内容</th><th class="l">依据</th><th class="l">量级预期（收着说）</th></tr>
<tr><td class="l"><b>1. 大富翁本体补低价续骰位</b><br><span class="dim">宽入口 + 中段续命件</span></td>
<td class="l">免费墙前（掷 250-350 次段）挂 $0.99-4.99 可复购续骰包；对应 P2 的"宽入口件+中段可复购件"两层</td>
<td class="l">02 章免费墙（2,258 白嫖撞墙、断点在供给侧）+ 04 章 P2 分层货架（宽入口两千人/中段复购件千人级）</td>
<td class="l">直接收入千元级/节（2,258 × 转化 5-10% × 低客单）；价值在把最投入的白嫖玩家接进付费漏斗</td></tr>
<tr><td class="l"><b>2. 深度增量不放大富翁</b><br><span class="dim">归模块 A（随机礼包）位置</span></td>
<td class="l">大富翁维持浅盘定位；$100+ 深度承接交给皮肤开箱优化方案模块 A</td>
<td class="l">04 章：P2 同形式天花板 $500-800、P2 大富翁只占节日盘 6-11%（深度交挖孔/GACHA）；X3 大富翁已占深海 ~40% 超载</td>
<td class="l">与模块 A 分工互补，不再是二选一</td></tr>
<tr><td class="l"><b>3. 马戏节承接</b><br><span class="dim">复用"堆件做大盘子"路径</span></td>
<td class="l">承接深海骨架（成就+连锁+存钱罐+BP 四件套）；错峰部署（D1 教训：同开=没弹药带）</td>
<td class="l">06 章族扩张（堆件路径已验证）+ 05 章新老服通吃（形式普适）</td>
<td class="l">深海族 {fmt(FAM_TOT)} 为基线</td></tr>
</table>
<div class="cb cb-info">⏳ 待裁决：续骰位落地宿主——放大富翁本体（骰子红包/低价骰子包）还是并进模块 A 随机礼包统一做。按 04 章分工看两者不冲突：续骰位=本体宽入口件，模块 A=盘内深度承接。</div>
</div></div>

<div class="footer">X3 深海大富翁族回归 · 窗口 7/3-7/16（深海收官终版） · 数据源=Trino v1090/v1041（_monopoly_deep.py / _p2_monopoly_fests.py） · 生成 {now}</div>
</div>
</div>
</body></html>"""
open(OUT, 'w', encoding='utf-8').write(page)
print('OK ->', OUT)
