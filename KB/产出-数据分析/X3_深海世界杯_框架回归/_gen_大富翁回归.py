# -*- coding: utf-8 -*-
"""
X3 深海大富翁族回归 · 独立报告生成器（07-20 用户定：单独开页，线性编号章节不用小页签）
07-21 v2：加「01 设计回溯·逐件归因」「03 堆件解剖·买家重叠与双周曲线」两章 + 五点大结论带章节跳转 + SKU 档位表。
数据源 = _monopoly_deep.json / _monopoly_design.json / _ds_monopoly_dist.json / _p2_monopoly_may.json
       / _p2_monopoly_fests.json + _kaixiang_deep.json（世界杯开箱对照桶） + _l1_m4.json（深海L1）
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
DZ = json.load(open(os.path.join(HERE, '_monopoly_design.json'), encoding='utf-8'))
DSM = json.load(open(os.path.join(HERE, '_ds_monopoly_dist.json'), encoding='utf-8'))
P2M = json.load(open(os.path.join(HERE, '_p2_monopoly_may.json'), encoding='utf-8'))
P2F = json.load(open(os.path.join(HERE, '_p2_monopoly_fests.json'), encoding='utf-8'))
KD = json.load(open(os.path.join(HERE, '_kaixiang_deep.json'), encoding='utf-8'))
KG = KD['gens']
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
OUT = os.path.join(HERE, f"深海大富翁回归_{END.replace('-','')}.html")

def fmt(v): return f"${v:,.0f}"

FAM_TOT = sum(MD['deepsea_components'][k]['rev'] for k in MD['deepsea_components'])
# 双周拆分（部署 7/3-7/16，W1=7/3-7/9 / W2=7/10-7/16）
W1_DAYS = [d for d in sorted(DZ['daily']) if d <= '2026-07-09']
W2_DAYS = [d for d in sorted(DZ['daily']) if d >= '2026-07-10']
W1_REV = sum(v['rev'] for d in W1_DAYS for v in DZ['daily'][d].values())
W2_REV = sum(v['rev'] for d in W2_DAYS for v in DZ['daily'][d].values())
PC = {r['n']: r for r in DZ['piece_count']}
MULTI_B = sum(r['buyers'] for r in DZ['piece_count'] if r['n'] >= 2)
MULTI_R = sum(r['rev'] for r in DZ['piece_count'] if r['n'] >= 2)
ALL_B = sum(r['buyers'] for r in DZ['piece_count'])

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

def tiers_table():
    """SKU 档位结构 · 四件 × pay_price"""
    tr = ['<table><tr><th class="l">件 / 档位</th><th>买家</th><th>单数</th><th>人均单数</th><th>收入</th><th class="l">读法</th></tr>']
    notes = {
      ('成就礼包', 99.99): '后 6 档同价 $99.99 的实际吸收：<b>唯一人均>1 的深档，但只有 17 人走到</b>（占成就收入 47%）',
      ('成就礼包', 1.99): '阶梯入口：177→147→104→54→43→17 逐档漏斗，$19.99→$49.99 段 -20%、$49.99→$99.99 段 -60%',
      ('罗盘连锁', 4.99): '连锁的复购全在低档（人均 2.1 单）',
      ('罗盘连锁', 49.99): '高档死：$49.99 仅 3 人、<b>$99.99 尾档零购买</b>（限购 5 从未被用）',
      ('BP大富翁线', 19.99): '至尊档买家(368)多于高级档(303)、240 人两档都买——BP 是"直接买满"型消费',
      ('存钱罐', 19.99): '单档单笔，157 人 × 1 单',
    }
    for name in ['成就礼包', '罗盘连锁', 'BP大富翁线', '存钱罐']:
        rows = DZ['tiers'][name]
        for i, t in enumerate(rows):
            label = f"<b>{name}</b>　${t['price']:.2f}" if i == 0 else f"<span class='dim'>{name}</span>　${t['price']:.2f}"
            note = notes.get((name, t['price']), '')
            hl = ' class="row-a"' if (name, t['price']) in [('成就礼包', 99.99), ('罗盘连锁', 49.99)] else ''
            tr.append(f"<tr{hl}><td class='l'>{label}</td><td>{t['buyers']}</td><td>{t['orders']}</td><td>{t['opb']:.1f}</td><td>{fmt(t['rev'])}</td><td class='l dim'>{note}</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

def _badge(b):
    B = {'ok': ('如设计生效', '#2ea856'), 'mid': ('部分/错位', '#d29922'), 'bad': ('缺件', '#f85149')}
    lbl, c = B[b]
    return f"<span style='display:inline-block;padding:1px 8px;border-radius:3px;font-size:10px;font-weight:700;background:{c}22;color:{c};vertical-align:1px'>{lbl}</span>"

def achieve_funnel_table():
    """成就礼包 SKU 漏斗：解锁圈数→到达→购买率（分母=到达的付费玩家）"""
    tr = ['<table><tr><th class="l">档（包id · 价格）</th><th>解锁圈数（≈掷骰次数）</th><th>到达人数</th><th>其中付费玩家</th><th>购买人数</th><th>实际购买率<br><span class="dim">÷到达付费玩家</span></th><th class="l">读法</th></tr>']
    notes = {
      '2801001': '入口档 11%——付费基底下墙前是正常的价格递减曲线（11%→9%→6%→3%→3%）',
      '2801006': '<b>全场最低 1%</b>——$49.99→$99.99 跳档 + 免费墙（350 次）同点叠加，双重劝退',
      '2801007': '过墙后购买率开始回升——U 型右半边',
      '2801011': '<b>最深 10 人里 3 人买（30%）</b>——能走到 300 圈的人付费意愿极强',
    }
    for r in DZ['achieve_funnel']:
        rp = r.get('reach_payer', 0)
        rate = r['buyers']/rp*100 if rp else 0
        cls = ' class="g"' if rate >= 8 else (' class="r"' if rate <= 1.5 else '')
        hl = ' class="row-a"' if r['pack'] in ('2801006', '2801011') else ''
        tr.append(f"<tr{hl}><td class='l'><b>${r['price']:.2f}</b><span class='dim'>　{r['pack']}</span></td>"
                  f"<td>{r['laps']} 圈<span class='dim'>（≈{r['rolls']:,} 次）</span></td><td>{r['reach']:,}</td><td>{rp:,}</td><td>{r['buyers']}</td>"
                  f"<td{cls}><b>{rate:.0f}%</b></td><td class='l dim'>{notes.get(r['pack'], '')}</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

def design_mindmap():
    """设计回溯 · 三支思维导图（礼包设计 / 流程体验 / 数值设计）"""
    ex = DZ['exchange_1202']; fn = DZ['funnel']
    recyc = ex['consume']['amt']/ex['produce']['amt']*100
    branches = [
      ('礼包设计（四件的使命对账）', '#4691e8', [
        ('成就礼包', 'mid', '购买率 U 型（付费基底）：墙前 11%→3% 正常递减、跳档+墙同点断崖 1%、墙后回升到 30%——深处的人肯买，缺的是走到深处的供给。', '#achfunnel', 'SKU 漏斗表'),
        ('罗盘连锁', 'mid', '复购全在 $4.99 档、$99.99 尾档零购买——高档坑没人跳，钱流向成就阶梯。', '#sec2', 'SKU 档位表'),
        ('BP大富翁线', 'ok', '渗透王 431 人 / max $30 封顶——使命完成，但占族收入 39% 易误读成"能收钱"。', '#sec2', '分件解剖'),
        ('存钱罐', 'mid', '88% 买家是族内老面孔——送达层落空，成了深度玩家的顺手加购。', '#sec3', '重叠表'),
      ]),
      ('流程体验（触达 → 跑圈 → 道具 → 墙）', '#2ea856', [
        ('触达漏斗（全路径）', 'ok', f"活跃 {fn['active']:,} → 领罗盘 59% → 掷骰 40% → 进店兑换 22%；掷骰的付费玩家 1,718 人中 610 买族（36%）——触达宽、付费基底转化也不低。", '#sec4', '停留曲线'),
        ('道具使用漏斗', 'ok', f"罗盘发放 {fn['dice_prod_amt']/10000:.0f} 万把、95% 用尽 ≈ 跑了 31.2 万圈（人均 44 圈 / p50≈34 圈）——不积压、供给紧而健康。", '#sec4', '停留曲线'),
        ('进度墙体验', 'bad', '2,258 白嫖撞 350 次墙 -98%，墙前缺 $0.99-4.99 续骰位。', '#sec4', '免费墙图'),
        ('拼图子活动', 'ok', '登录/任务进度钩给免费盘续供，定性生效（无独立付费数据）。', '', ''),
      ]),
      ('数值设计（投放量 · 兑换 · 价位带）', '#d29922', [
        ('免费投放量', 'ok', '塌方点精确落在设计的 350 次；人均投放 214 把 ≈ <b>$60 名义/人</b>（$0.28/把·罗盘=250钻等换），玩满免费盘（350 次墙）≈ $98/人——高名义补贴，付费买的是进度不是面值。', '#sec4', '免费墙图'),
        ('兑换商店（宝珠 1202）', 'mid', f"回收率 {recyc:.0f}%、四成货币沉淀、43% 产出者没兑过——出口可用但吸引力不足。", '', ''),
        ('价位带', 'mid', '$49.99→$99.99 转化 -60% 断崖 + $29.99/59.99 空档——两条预警全应验。', '#sec2', 'SKU 档位表'),
        ('同价互踩', 'mid', '成就与连锁在 $99.99 同价同族，连锁零购买——同价位只留一件。', '#sec2', 'SKU 档位表'),
      ]),
    ]
    s = ['<div class="mm">',
         '<div class="mm-root">深海大富翁族<br>设计回溯</div>',
         '<div class="mm-stem"></div>',
         '<div class="mm-row">']
    for title, c, leaves in branches:
        s.append(f'<div class="mm-col" style="--bc:{c}">')
        s.append(f'<div class="mm-bnode">{title}</div>')
        for name, b, text, href, figname in leaves:
            link = f'　<a class="cl" href="{href}" style="color:#58a6ff;text-decoration:none;font-size:11px;font-weight:700;white-space:nowrap">→ {figname}</a>' if href else ''
            s.append(f'<div class="mm-leaf"><div style="margin-bottom:4px"><b>{name}</b>　{_badge(b)}</div><span style="font-size:11.5px;color:#8b949e">{text}</span>{link}</div>')
        s.append('</div>')
    s.append('</div></div>')
    return ''.join(s)

def piece_chart():
    """堆件解剖 · 买了几件 → 买家数 + ARPPU 阶梯"""
    pcs = DZ['piece_count']
    W, H, L_, T, B = 1160, 300, 60, 56, 54
    panels = [('买家数（1件党占 60%）', lambda r: r['buyers'], '{:.0f}人', max(r['buyers'] for r in pcs)*1.2),
              ('ARPPU $（每多集一件翻一倍+）', lambda r: r['arppu'], '${:.0f}', max(r['arppu'] for r in pcs)*1.2),
              ('单人最高 max $', lambda r: r['mx'], '${:,.0f}', max(r['mx'] for r in pcs)*1.2)]
    PW = (W - 80) / 3
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L_}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">堆件阶梯 · 按"买了族内几件"分组（{ALL_B} 买家）——深度不是单件做深，是横向集件叠出来的</text>')
    for pi, (title, f, fv, vmax) in enumerate(panels):
        ox = 20 + pi*(PW+20)
        sv.append(f'<text x="{ox+30}" y="{T-10}" fill="#8b949e" font-size="11.5" font-weight="700">{title}</text>')
        bw = (PW-40)/4
        for gi, r in enumerate(pcs):
            v = f(r)
            x = ox + 30 + gi*bw
            ph = H - T - B
            y = T + ph*(1-min(1, v/vmax))
            c = ['#3a4150', '#4691e8', '#c08a17', '#f85149'][gi]
            sv.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw-10:.0f}" height="{T+ph-y:.0f}" fill="{c}" rx="3"><title>{r["n"]}件: {fv.format(v)}</title></rect>')
            sv.append(f'<text x="{x+(bw-10)/2:.0f}" y="{y-6:.0f}" fill="#f0f6fc" font-size="10.5" font-weight="700" text-anchor="middle">{fv.format(v)}</text>')
            sv.append(f'<text x="{x+(bw-10)/2:.0f}" y="{H-34}" fill="#8b949e" font-size="10" text-anchor="middle">{r["n"]}件</text>')
    sv.append('</svg>')
    return ''.join(sv)

def overlap_table():
    tr = ['<table style="margin-top:10px"><tr><th class="l">件</th><th>买家</th><th>同时买了族内其他件</th><th>重叠率</th><th class="l">角色判读</th></tr>']
    roles = {'BP大富翁线': '半数是"只买 BP"的轻付费——族的进人口',
             '成就礼包': '2/3 与其他件重叠——深度玩家主坑',
             '罗盘连锁': '8 成重叠——深度玩家的加购件而非独立入口',
             '存钱罐': '9 成重叠——送达层设计落空，实际是深度玩家顺手件'}
    for name in ['BP大富翁线', '成就礼包', '罗盘连锁', '存钱罐']:
        o = DZ['overlap'][name]
        tr.append(f"<tr><td class='l'><b>{name}</b></td><td>{o['buyers']}</td><td>{o['with_other']}</td><td>{o['pct']:.0f}%</td><td class='l dim'>{roles[name]}</td></tr>")
    tr.append(f"<tr><td class='l'><b>合计</b></td><td class='l dim' colspan='4'>买 2 件以上 {MULTI_B} 人（{MULTI_B/ALL_B*100:.0f}% 买家）贡献 {fmt(MULTI_R)}（{MULTI_R/FAM_TOT*100:.0f}% 收入）——族的钱来自「集件」，单件天花板都很矮（1件党 max 仅 $50）</td></tr>")
    tr.append('</table>')
    return ''.join(tr)

def daily_chart():
    """族各件逐日收入 · 堆叠柱 + W1/W2 分界"""
    days = sorted(DZ['daily'])
    comps = ['成就礼包', 'BP大富翁线', '存钱罐', '罗盘连锁']
    cols = {'成就礼包': '#4691e8', 'BP大富翁线': '#c08a17', '存钱罐': '#2ea856', '罗盘连锁': '#a371f7'}
    W, H, L_, R, T, B = 1160, 330, 60, 24, 46, 70
    pw, ph = W-L_-R, H-T-B
    totals = [sum(DZ['daily'][d].get(c, {}).get('rev', 0) for c in comps) for d in days]
    vmax = max(totals)*1.15
    n = len(days); bw = pw/n*0.66
    sv = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    sv.append(f'<text x="{L_}" y="24" fill="#f0f6fc" font-size="13" font-weight="700">族各件逐日收入 · 前半程 {fmt(W1_REV)}（{W1_REV/(W1_REV+W2_REV)*100:.0f}%）/ 后半程 {fmt(W2_REV)}（{W2_REV/(W1_REV+W2_REV)*100:.0f}%）——买断件收钱前置</text>')
    # W2 区底色
    x_w2 = L_ + pw*days.index('2026-07-10')/n
    sv.append(f'<rect x="{x_w2:.0f}" y="{T}" width="{L_+pw-x_w2:.0f}" height="{ph}" fill="#d29922" fill-opacity="0.06"/>')
    sv.append(f'<line x1="{x_w2:.0f}" y1="{T}" x2="{x_w2:.0f}" y2="{T+ph}" stroke="#d29922" stroke-dasharray="4 3"/>')
    sv.append(f'<text x="{x_w2+6:.0f}" y="{T+14}" fill="#d29922" font-size="10.5" font-weight="700">后半程（7/10 起）→</text>')
    for gv in range(0, int(vmax)+1, 1000):
        sv.append(f'<line x1="{L_}" y1="{T+ph*(1-gv/vmax):.0f}" x2="{W-R}" y2="{T+ph*(1-gv/vmax):.0f}" stroke="#21262d"/>')
        sv.append(f'<text x="{L_-6}" y="{T+ph*(1-gv/vmax)+4:.0f}" fill="#484f58" font-size="10" text-anchor="end">{gv//1000}k</text>')
    for i, d in enumerate(days):
        x = L_ + pw*i/n + (pw/n-bw)/2
        y = T + ph
        for c in comps:
            v = DZ['daily'][d].get(c, {}).get('rev', 0)
            hgt = ph*v/vmax
            y -= hgt
            sv.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{hgt:.0f}" fill="{cols[c]}" fill-opacity="0.9"><title>{d} {c} {fmt(v)}</title></rect>')
        sv.append(f'<text x="{x+bw/2:.0f}" y="{y-5:.0f}" fill="#8b949e" font-size="9" text-anchor="middle">{fmt(totals[i])}</text>')
        sv.append(f'<text x="{x+bw/2:.0f}" y="{H-46}" fill="#8b949e" font-size="9" text-anchor="middle">{d[8:]}</text>')
    lx = L_
    for c in comps:
        sv.append(f'<rect x="{lx}" y="{H-30}" width="12" height="12" fill="{cols[c]}" rx="2"/>')
        sv.append(f'<text x="{lx+17}" y="{H-20}" fill="#c9d1d9" font-size="10.5">{c}</text>')
        lx += 17 + len(c)*11 + 26
    sv.append('</svg>')
    return ''.join(sv)

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

BACKTOP = '<div style="text-align:right;margin:-6px 0 8px"><a href="#sec0" style="color:#484f58;font-size:11px;text-decoration:none">↑ 回结论</a></div>'

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
.bigcon a.cl{{color:var(--accent);text-decoration:none;font-size:11.5px;font-weight:700;white-space:nowrap}} .bigcon a.cl:hover{{text-decoration:underline}}
.vlin{{display:block;margin-bottom:14px}}
.vc{{background:#0d2137;border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;font-size:14px;font-weight:700;color:var(--head);line-height:1.9;margin-bottom:10px}}
td b{{color:var(--head)}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
.mm-root{{width:180px;margin:0 auto;background:linear-gradient(135deg,#1b2436,#161b22);border:1.5px solid var(--accent);border-radius:10px;padding:12px;text-align:center;font-weight:800;color:var(--head);font-size:14px;line-height:1.5}}
.mm-stem{{width:2px;height:20px;background:#30363d;margin:0 auto}}
.mm-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;position:relative;padding-top:20px}}
.mm-row::before{{content:'';position:absolute;top:0;left:16.6%;right:16.6%;height:2px;background:#30363d}}
.mm-col::before{{content:'';display:block;width:2px;height:20px;background:#30363d;margin:-20px auto 0}}
.mm-bnode{{border:1.5px solid var(--bc);color:var(--head);text-align:center;border-radius:20px;padding:8px 12px;font-weight:700;font-size:13px;background:#0d1117}}
.mm-leaf{{background:#0d1117;border:1px solid #30363d;border-left:3px solid var(--bc);border-radius:6px;padding:10px 12px;margin-top:10px;font-size:12px;line-height:1.7}}
.mm-leaf b{{color:var(--head)}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">DEEPSEA MONOPOLY REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">深海大富翁族回归</div>
    <a class="sb-item" href="#sec0">结论先行</a>
    <a class="sb-item" href="#sec1">01 · 设计回溯 · 逐件归因</a>
    <a class="sb-item" href="#sec2">02 · 族基本盘 · 分件与SKU档位</a>
    <a class="sb-item" href="#sec3">03 · 堆件解剖 · 重叠与双周曲线</a>
    <a class="sb-item" href="#sec4">04 · 进度停留 · 免费墙</a>
    <a class="sb-item" href="#sec5">05 · 付费深度分布</a>
    <a class="sb-item" href="#sec6">06 · P2 同形式参照</a>
    <a class="sb-item" href="#sec7">07 · 新老服拆分</a>
    <a class="sb-item" href="#sec8">08 · 族扩张 · 历史坐标</a>
    <a class="sb-item" href="#sec9">09 · 结论与动作</a>
    <a class="sb-item" href="母题4_改动效果清单_{END.replace('-','')}.html">← 返回双节回归总页</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 深海大富翁族回归<br><em>压舱石实锤 · 深度=横向集件不是单件做深 · 下一步补分层货架</em></h1>
  <div class="meta">窗口 <b>7/3-7/16 · 59服</b>（深海 7/16 收官=终版数据） · 数据 <b>Trino v1090/v1041 订单+资产</b> · 生成 {now}</div>
</div>

<div class="page">
<div class="sec" id="sec0"><div class="sec-head"><div class="sec-num">00</div><div class="sec-title">结论先行</div></div>
<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{fmt(FAM_TOT)}</div><div class="kpi-lbl">族收入 · 深海最大玩法族</div><div class="kpi-sub">成就 $10.1k + BP线 $10.4k + 罗盘链 $3.3k + 存钱罐 $3.1k（窗口重算口径；L1 归因口径 $21.7k）</div></div>
  <div class="kpi g"><div class="kpi-val">34.2% / 33.0%</div><div class="kpi-lbl">付费玩家付费率 · 新老服通吃</div><div class="kpi-sub">深海收入模块最高（开箱 9.6% / 竞猜 4.4%），两段几乎完全对称</div></div>
  <div class="kpi y"><div class="kpi-val">$17 → $205</div><div class="kpi-lbl">堆件阶梯 · 1件党 vs 4件全买 ARPPU</div><div class="kpi-sub">买2件+的 {MULTI_B} 人（{MULTI_B/ALL_B*100:.0f}%买家）贡献 {MULTI_R/FAM_TOT*100:.0f}% 收入——深度全靠横向集件</div></div>
  <div class="kpi r"><div class="kpi-val">-98%</div><div class="kpi-lbl">免费墙 · 掷骰 350→500 次白嫖塌方</div><div class="kpi-sub">2,258→42 人；能过墙的 93% 是买骰子的人</div></div>
</div>
<div class="bigcon">大结论：<b>大富翁族是深海最成功的改动——{fmt(FAM_TOT)} 压舱、付费率 34% 新老服通吃、免费活跃盘 7,069 人；但它的"深度"是玩家横向集件叠出来的，不是把单件做深。</b><br>
<span style="font-size:13px;line-height:2.1">
① <b>盘子做对了</b>——从老版"纯连锁 $3-6k/月"扩成四件套 {fmt(FAM_TOT)}，付费率 34% 深海最高；但四件的设计使命各有落差（BP 渗透达成 / 存钱罐送达落空 / 连锁高档死 / 成就深档只 17 人走到）<a class="cl" href="#sec1">→ 01 逐件归因</a><a class="cl" href="#sec8">→ 08 历史坐标</a>；<br>
② <b>深度=横向集件</b>——1件党 363 人 ARPPU $17 / max 仅 $50，4件全买 33 人 ARPPU $205 / max $822：每多集一件 ARPPU 翻一倍+，买 2 件以上的 {MULTI_B/ALL_B*100:.0f}% 买家贡献 {MULTI_R/FAM_TOT*100:.0f}% 收入——玩家想多花钱只能"换个坑再买断"，没有纵向加深通道<a class="cl" href="#sec3">→ 03 堆件解剖</a>；<br>
③ <b>进度墙断在供给侧</b>——白嫖 2,258 人玩到 350 次撞免费墙集体阵亡（-98%），能继续的 93% 是买骰子的人；墙是设计意图，缺的是墙前 $0.99-4.99 低价续骰位<a class="cl" href="#sec4">→ 04 免费墙</a>；<br>
④ <b>P2 同形式参照</b>——P2 情人/科技/拓荒也没把大富翁做深（max $550-780、≥$500≈0，X3 $792 不落后），P2 赢在分层货架+只让大富翁占节日盘 6-11%（X3 占深海 ~40% 已超载）<a class="cl" href="#sec6">→ 06 P2 参照</a>；<br>
⑤ <b>动作</b>=本体补"宽入口+中段续命"（低价续骰位），深度增量归盘内其他弹药（模块 A 位置）；马戏节直接复用堆件路径（大富翁全程贯穿，已定）<a class="cl" href="#sec9">→ 09 动作表</a>。
</span></div>
</div>

<div class="sec" id="sec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">设计回溯 · 逐件归因（当初为什么这么设计 → 实际发生了什么）</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">设计回溯收拢成三支：<b style="color:#4691e8">礼包设计</b>（四件的使命对账）· <b style="color:#2ea856">流程体验</b>（触达漏斗→跑圈→道具使用→墙）· <b style="color:#d29922">数值设计</b>（投放量/兑换商店/价位带）。总账：<b>生效 5 · 部分/错位 6 · 缺件 1</b>——流程侧基本全对（触达 59%、罗盘 95% 用尽、投放量精确按设计），问题集中在货架侧（礼包分层与价位带）。</div>
<div class="card"><div class="ct">设计回溯 · 三支导图（设计源=深海节策划案/数值总览 06-25/上线配置记录）</div>
{design_mindmap()}
<div class="cb cb-info">设计文档溯源：核心路线="提高付费深度"（夏日验证 breadth 成功 depth 没起来）；免产骰对标 X2 保守量、覆盖阶段奖前 6 档；成就礼包价位带 $1.99→$99.99×6（数值总览 06-25 已预警"后 6 档 $99.99 重复"与"$29.99/$59.99 价位带断层"）；BP 满级线 16,400=世界杯的 27%（满级 1.8% 事故根因之一）。</div>
</div></div>

<div class="sec" id="sec2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">族基本盘 · 分件与 SKU 档位</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">族收入 {fmt(FAM_TOT)} 由成就礼包($10.1k)与 BP大富翁线($10.4k)两大件扛起，但四件里三件是买断制、硬封顶 $20-687；唯一有复购形态的罗盘连锁（复购 3.1 单、max $255）盘子最小只 138 人——整个族的深度被买断制天花板锁死。</div>
<div class="card"><div class="ct">大富翁族四件解剖 · 收入/买家/ARPPU/复购/max/付费形态</div>
{family_dissect_card()}
</div>
<div class="card"><div class="ct">SKU 档位结构 · 四件 × 档位（买家/单数/人均/收入）</div>
{tiers_table()}
<div class="cb cb-info"><b>档位层的三个结构问题：</b>①成就阶梯 $49.99→$99.99 段转化 -60% 断崖（前四段都在 -20~-48%）——$50-100 之间没有台阶（数值总览预警的"价位带断层"应验）；②唯一人均>1 单的深档（成就 6 连 $99.99）只有 17 人到达——深度设计的服务面太窄；③罗盘连锁 $99.99 尾档限购 5 从未被买过 1 次——同价位钱都流向成就阶梯（同族两件在 $99.99 互相打架，连锁输）。</div>
</div>
<div class="vlin"><div class="vc">成就礼包 SKU 漏斗（付费玩家基底）：购买率是一条 <b>U 型曲线</b>——墙前 11%→3% 是正常价格递减，$99.99 跳档+免费墙同点断崖到 <b>1%（全场最低）</b>，墙后随深度回升 2%→9%→<b>30%</b>。另一个关键发现：<b>免费墙拦住的不只白嫖——到达的付费玩家也从 1,356 被腰斩到 642</b>，这 700+ 没骰子的已付费玩家就是续骰位的现成客群。</div>
<div class="card" id="achfunnel"><div class="ct">成就礼包 11 档 SKU 漏斗 · 解锁圈数（AchievePack 组104）× 到达人数（掷骰 survival 换算）× 实际购买率（÷到达的付费玩家）</div>
{achieve_funnel_table()}
<div class="cb cb-info">口径：<b>购买率分母=到达该圈数阈值的窗口付费玩家</b>（转化率类指标一律用付费玩家基底，免费玩家只稀释不贡献转化——掷骰 7,069 人中付费玩家 1,718）；圈数换算=棋盘 24 格（Island 组2）÷ 骰均 3.5 ≈ <b>1 圈 6.9 次掷骰</b>（估算，未计事件传送/精准罗盘选点）；购买人数按包 id 精确。注意 $99.99 首档（50 圈≈343 次）恰好压在 350 次免费墙上——<b>价格跳档和免费断供发生在同一个位置，1% 的全场最低转化是两个设计叠出来的</b>。</div>
</div></div>

<div class="sec" id="sec3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">堆件解剖 · 买家重叠与双周曲线</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">"堆买断件做大盘子"的微观机制：<b>件数就是深度阶梯</b>——1件党 363 人（60%）ARPPU $17、max 仅 $50；集齐 4 件的 33 人 ARPPU $205、max $822。买 2 件以上的 {MULTI_B} 人（{MULTI_B/ALL_B*100:.0f}%）贡献 {fmt(MULTI_R)}（{MULTI_R/FAM_TOT*100:.0f}%）。玩家不是不肯花，是每个坑 $20-99 就见底，只能横着跳下一个坑。</div>
<div class="card"><div class="ct">按"买了族内几件"分组 · 买家数 / ARPPU / max</div>
{piece_chart()}
{overlap_table()}
</div>
<div class="vlin"><div class="vc">逐日曲线：买断件的钱天然前置——开门三日 $3.1k/$4.3k/$2.5k 收走脉冲后转入 $1.1-1.6k 平台缓降，尾日收官反弹 $2.3k；前半程收走 {W1_REV/(W1_REV+W2_REV)*100:.0f}%、后半程 {W2_REV/(W1_REV+W2_REV)*100:.0f}%。</div>
<div class="card"><div class="ct">族各件逐日收入（悬停看分件金额）</div>
{daily_chart()}
<div class="cb cb-info"><b>归因：</b>成就阶梯/BP/存钱罐都是"上来就买完"型，钱天然集中在前半程（BP 大富翁线开门两日即收走大半）；族里缺一个随进度持续吐钱的复购件——这正是续骰位的位置。<b>大富翁全程贯穿的排期没问题（已定方向）</b>，后半程曲线要靠复购件撑，不靠排期调整。</div>
</div></div>

<div class="sec" id="sec4"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">进度停留曲线 · 免费墙</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">白嫖玩家掷骰一路走到 350 次都还有 2,258 人（免费活跃盘充足、驱动力不缺），但 350→500 次白嫖塌方 -98%（2,258→42）——这是免费骰子耗尽的硬墙；能跨过墙走到 700 次的 483 人里 93% 是族付费玩家（买骰子的人一路走到 max 3,105 次）。断点归因=供给侧（免费投放到 350 次断供），不是需求侧（想不想玩）。</div>
<div class="card"><div class="ct">进度停留 · 累计掷骰次数 survival（全量 / 白嫖 / 族付费三线 · 悬停看人数）</div>
{dice_survival_chart()}
{dice_decay_table()}
<div class="cb cb-info">口径：掷骰次数=航海罗盘 Item_1057(普通)+海神罗盘 Item_1058(精准) change_type=2 消耗次数，对齐阶段奖 OtherReward 组 100 的档位（抽 20/50/100/150/250/350/500/700）。白嫖=掷过骰但未买任何大富翁族包的玩家。<b>免费墙 = 设计意图（免产骰子对标 X2 保守量、覆盖前 6 档，深档靠付费）；问题不在墙本身，在墙前缺一个"$0.99-4.99 再买一把骰子接着走"的低价续骰位</b>——白嫖玩家撞墙时唯一的付费选项是成就礼包一次性阶梯买断，跨度太大接不住。</div>
</div></div>

<div class="sec" id="sec5"><div class="sec-head"><div class="sec-num">05</div><div class="sec-title">付费深度分布（÷该模块全部买家 · 对照世界杯开箱 / P2五月浅盘）</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">大富翁付费额分布中段全程偏陡（$50→$200 连续 -47%/-55%/-57%，成就礼包一次性阶梯、中段无复购位）；对照世界杯开箱平滑走到 $300 撞墙、P2 节日大富翁中段最平（$50→$100 仅 -21%）——三条线三种病。</div>
<div class="card"><div class="ct">大富翁 × 开箱 × P2节日大富翁 · 花到 ≥$X 的买家占比</div>
{ds_monopoly_chart()}
{ds_decay_table()}
<div class="cb cb-info">对 X3 的启示：①中段复购位是大富翁最该抄的（P2 中段平=固定+随机+组队多复购位）；②浅盘模块不必自己做深度，但 X3 缺 P2 那个"深度承接模块"——正是模块 A 随机礼包的位置。同游戏内比较用绝对人数、跨游戏/跨规模用占比（P2 曲线左端占比低=大量 $1-10 微额买家撑大分母，宽入口的形状）。</div>
</div></div>

<div class="sec" id="sec6"><div class="sec-head"><div class="sec-num">06</div><div class="sec-title">P2 同形式参照（情人 / 科技 / 拓荒「节日大富翁」族 · 春节异族形式不同已排除）</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">P2 三节的「节日大富翁」族（与 X3 同形式）：三节 $60.8k-92.8k / 1,841-2,410 买家 / <b>max 全部 $550-780、≥$500≈0——P2 也没把大富翁做深，X3 max $792 单人深度并不落后</b>。P2 赢在两处：①分层货架（$4-6 宽入口件两千人 + $21-30 中段可复购件千人级 + $180 深度件只卖 ~150 人，X3 四件 ARPPU 全挤 $20-36）；②它只让大富翁当浅盘（占节日盘 6-11%），深度交给挖孔/GACHA——X3 大富翁族占深海收入 ~40% 已经超载。</div>
<div class="card"><div class="ct">同形式参照 · X3 深海 vs P2 情人/科技/拓荒（占比口径 · 窗口 14 vs 28 天、服基数不同，只比形状）</div>
{p2fests_chart()}
{p2fests_decay_table()}
</div>
<div class="card"><div class="ct">P2 分层货架解剖（科技窗为代表 · 情人窗单件全族 / 拓荒窗同构）</div>
{p2fests_shelf_card()}
<div class="cb cb-info"><b>启示：</b>①<b>续骰位定位="宽入口+中段续命件"</b>——P2 同形式的钱主要来自宽入口件（两千人小额）和中段可复购件（复购 ~3 单铺给千人级），X3 缺的正是这两件；续骰位直接收入千元级/节（2,258 撞墙白嫖 × 转化 5-10% × $0.99-4.99），价值在接人进漏斗。②<b>大富翁本体不承担深度增量</b>——同形式在 P2 三节的天花板就是 $500-800，深度增量归盘内其他弹药（模块 A 随机礼包位置）。⚠️口径注：跨游戏只比占比与形状；P2 收入=pay_price（v1041 名字匹配）；「2025复活节大富翁礼包」为历史复用名，实际是科技/拓荒窗在售的大富翁阶梯礼包；春节异族大富翁（$250k/随机轨）为春节特有形式，不作同形式参照。</div>
</div></div>

<div class="sec" id="sec7"><div class="sec-head"><div class="sec-num">07</div><div class="sec-title">新老服拆分</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">大富翁族在成熟老服(1170-1870)与年轻服(1880-2010)几乎完全对称：买家 313 vs 297、付费率 34.2% vs 33.0%、ARPPU $44.8 vs $43.2——不像竞猜偏新服、开箱付费率被新服稀释，大富翁族是新老服通吃的稳定压舱石。</div>
<div class="card"><div class="ct">大富翁族 · 新老服拆分（付费率分母=该段窗口总付费人数）</div>
{server_seg_card()}
<div class="cb cb-info">对照：世界杯开箱付费率被扩服稀释到 9.6%（成熟段 13.2%）、竞猜 4.4% 且参与近半来自新服。大富翁族两段付费率都在 33-34%=玩法本身黏性强、不靠新服白嫖盘撑数——这是"压舱石"判定的直接证据，也说明改造对新老服都适用。</div>
</div></div>

<div class="sec" id="sec8"><div class="sec-head"><div class="sec-num">08</div><div class="sec-title">族扩张 · 历史坐标</div></div>
{BACKTOP}
<div class="vlin"><div class="vc">老版航海之路（纯连锁 207xxx）月度收入 $1.4k→$6.2k 随服基数缓涨；深海把大富翁盘子做到 {fmt(FAM_TOT)}，扩张全部来自新增件（成就礼包 $10.1k + BP大富翁线 $10.4k + 存钱罐 $3.1k），连锁本身 $3.3k 与历史月度持平——改动正确地做大了盘子，但做大的方式是"加买断件"，没有做深单件。</div>
<div class="card"><div class="ct">大富翁族扩张 · 老版纯连锁月度 vs 深海四件套</div>
{family_expansion_chart()}
<div class="cb cb-info">历史坐标读法：深海大富翁的成功=把一个月 $3-6k 的连锁小玩法，通过挂成就礼包+双 BP+存钱罐，扩成 {fmt(FAM_TOT)} 的节日压舱族——这条"堆件做大盘子"的路径马戏节可直接复用（承接深海骨架）。</div>
</div></div>

<div class="sec" id="sec9"><div class="sec-head"><div class="sec-num">09</div><div class="sec-title">结论与动作</div></div>
{BACKTOP}
<div class="card">
<table><tr><th class="l">动作</th><th class="l">内容</th><th class="l">依据</th><th class="l">量级预期（收着说）</th></tr>
<tr><td class="l"><b>1. 大富翁本体补低价续骰位</b><br><span class="dim">宽入口 + 中段续命件</span></td>
<td class="l">免费墙前（掷 250-350 次段）挂 $0.99-4.99 可复购续骰包；对应 P2 的"宽入口件+中段可复购件"两层</td>
<td class="l">04 章免费墙（2,258 白嫖撞墙、断点在供给侧）+ 02 章成就 SKU 漏斗（U 型：墙后购买率回升至 30%；<b>到达付费玩家被墙从 1,356 腰斩到 642=续骰位现成客群</b>）+ 06 章 P2 分层货架 + 02 章连锁复购全在 $4.99 档的实证</td>
<td class="l">直接收入千元级/节（2,258 × 转化 5-10% × 低客单）；价值在把最投入的白嫖玩家接进付费漏斗，并给族一个"随进度吐钱"的 W2 点火件</td></tr>
<tr><td class="l"><b>2. 深度增量不放大富翁</b><br><span class="dim">归模块 A（随机礼包）位置</span></td>
<td class="l">大富翁维持浅盘定位；$100+ 深度承接交给皮肤开箱优化方案模块 A；同族内清理 $99.99 打架（连锁尾档零购买可撤，成就深档独占 $99.99 位）</td>
<td class="l">06 章：P2 同形式天花板 $500-800、P2 大富翁只占节日盘 6-11%（深度交挖孔/GACHA）；03 章：深度=集件不是单件；02 章：$99.99 两件互踩</td>
<td class="l">与模块 A 分工互补，不再是二选一</td></tr>
<tr><td class="l"><b>3. 马戏节承接</b><br><span class="dim">复用"堆件做大盘子"路径 + 修两个错位</span></td>
<td class="l">承接深海骨架（成就+连锁+存钱罐+BP 四件套），<b>大富翁全程贯穿（已定方向）</b>；后半程曲线靠复购件撑（03 章：买断件收钱前置）；存钱罐若继续做，把入口铺到非族玩家（88% 重叠=送达落空）</td>
<td class="l">08 章族扩张（堆件路径已验证）+ 07 章新老服通吃（形式普适）+ 01/03 章设计错位清单</td>
<td class="l">深海族 {fmt(FAM_TOT)} 为基线</td></tr>
</table>
<div class="cb cb-info">⏳ 待裁决：续骰位落地宿主——放大富翁本体（骰子红包/低价骰子包）还是并进模块 A 随机礼包统一做。按 06 章分工看两者不冲突：续骰位=本体宽入口件，模块 A=盘内深度承接。</div>
</div></div>

<div class="footer">X3 深海大富翁族回归 · 窗口 7/3-7/16（深海收官终版） · 数据源=Trino v1090/v1041（_monopoly_deep.py / _monopoly_design.py / _p2_monopoly_fests.py） · 生成 {now}</div>
</div>
</div>
</body></html>"""
open(OUT, 'w', encoding='utf-8').write(page)
print('OK ->', OUT)
