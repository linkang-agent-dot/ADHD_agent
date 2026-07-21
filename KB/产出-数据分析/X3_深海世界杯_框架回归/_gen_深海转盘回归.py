# -*- coding: utf-8 -*-
"""
X3 深海转盘回归 · 独立报告生成器（07-21 用户定：直接复刻开箱回归模板）
数据源 = _l1_m4.json（深海 59 服主口径） / _kx_top20.json（Top20 阶梯） / _top20_assets.json（核心投放缩略图）
用法: python _gen_深海转盘回归.py   （深海 7/16 收官=数据终版不再变；但文件名随 _l1_m4.json 的 END 拼——7/21 世界杯终版刷新后要重跑对齐，同大富翁/开箱页）
builder 复制自 _gen_开箱回归.py（先例：改转盘视图只改本生成器）。
"""
import sys, json, os, datetime
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, '_l1_m4.json'), encoding='utf-8'))
END = L['END']
DS = L['深海节']; dm = DS['modules']; PD = DS['payers']
T20 = json.load(open(os.path.join(HERE, '_kx_top20.json'), encoding='utf-8'))
A64 = json.load(open(os.path.join(HERE, '_top20_assets.json'), encoding='utf-8'))
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
OUT = os.path.join(HERE, f"深海转盘回归_{END.replace('-','')}.html")

def fmt(v): return f"${v:,.0f}"

WHEEL = dm['转盘连锁5档']; BPW = dm['BP转盘线(130035/46)']; ANC = dm['藏宝图锚点4档']; WISH = dm['许愿池']
FAM_REV = WHEEL['rev'] + BPW['rev'] + ANC['rev']          # 转盘族=连锁+BP转盘线+锚点（许愿池只作参照）
ZT = [v['tot'] for v in T20['深海_转盘top20']]
N_TOP = sum(1 for v in ZT if v == max(ZT))                # 齐顶人数
QVALS = sorted({int(v) for v in ZT}, reverse=True)        # 量子化取值集合

# 大富翁族（对照）
MONO_KEYS = ['大富翁成就礼包', 'BP大富翁线(130036/37)', '存钱罐', '大富翁罗盘连锁']
MONO_REV = sum(dm[k]['rev'] for k in MONO_KEYS)

# ============ builders ============

def wheel_table():
    rows = [
      ('转盘连锁5档（幸运转盘 1025）', WHEEL, '连锁直购 · 逐档限购', '判退役核心证据：ARPPU/复购六代垫底档'),
      ('BP转盘线 130035/46（远航日志）', BPW, '通行证 · 硬封顶 $30', '渗透工具：买家全族最多但深度为零（max=$30 买满即封顶）'),
      ('藏宝图锚点 13021-24', ANC, '锚点直购 · 获取路径修复', '<b>13 天零购买</b>——仅起价格锚作用'),
    ]
    tr = ['<table><tr><th class="l">模块（7/3-' + END[5:] + ' · 59服）</th><th>收入</th><th>买家</th><th>付费玩家付费率*</th><th>ARPPU</th><th>复购</th><th>max</th><th class="l">付费形态</th><th class="l">判读</th></tr>']
    for name, m, form, note in rows:
        hl = ' class="row-a"' if '连锁' in name and '罗盘' not in name else ''
        tr.append(f"<tr{hl}><td class='l'><b>{name}</b></td><td>{fmt(m['rev'])}</td><td>{m['buyers']}</td>"
                  f"<td>{m['payrate']:.1f}%</td><td>${m['arppu']:.1f}</td><td>{m['opb']:.1f}</td><td>{fmt(m['max'])}</td>"
                  f"<td class='l dim'>{form}</td><td class='l' style='font-size:11px'>{note}</td></tr>")
    tr.append(f"<tr><td class='l'><b>转盘族合计（连锁+BP线+锚点）</b></td><td><b>{fmt(FAM_REV)}</b></td>"
              f"<td class='l dim' colspan='7'>占深海总盘 {FAM_REV/DS['total']*100:.0f}%（大富翁族 {fmt(MONO_REV)} 占 {MONO_REV/DS['total']*100:.0f}%）——W1 核心位产出不到 W2 核心位的一半</td></tr>")
    tr.append('</table>')
    tr.append(f"<div class='dim' style='margin-top:6px'>*付费玩家付费率 = 模块买家 ÷ 深海窗口 59 服总付费人数（{PD:,}）。</div>")
    return ''.join(tr)

def top20_chart():
    """Top20 阶梯：深海转盘族加粗 · 对照夏日/世界杯开箱"""
    series = [('深海·转盘族', [v['tot'] for v in T20['深海_转盘top20']], '#4691e8'),
              ('世界杯·老服开箱', [v['tot'] for v in T20['世界杯_老服top20']], '#c08a17'),
              ('世界杯·全服开箱', [v['tot'] for v in T20['世界杯_全服top20']], '#8b949e'),
              ('夏日·老服开箱', [v['tot'] for v in T20['夏日_老服top20']], '#2ea856')]
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
    s.append(f'<text x="{L_+pw/2:.1f}" y="{H-20}" fill="#8b949e" font-size="10.5" text-anchor="middle">模块付费额排名（第1~20名）</text>')
    yv = Y(max(ZT))
    s.append(f'<line x1="{L_}" y1="{yv:.1f}" x2="{W-R}" y2="{yv:.1f}" stroke="#f85149" stroke-width="1" stroke-dasharray="5 4"/>')
    s.append(f'<text x="{W-R-4}" y="{yv-6:.1f}" fill="#f85149" font-size="10.5" font-weight="700" text-anchor="end">买光墙 {fmt(max(ZT))}（Top{N_TOP} 齐顶）</text>')
    for nm, vals, c in series:
        wgt = 2.4 if '转盘' in nm else 1.7
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

def quantize_card():
    from collections import Counter
    cnt = Counter(int(v) for v in ZT)
    tr = ['<table><tr><th class="l">Top20 取值（全部量子化）</th>' + ''.join(f'<th>${q}</th>' for q in QVALS) + '</tr>']
    cells = []
    for q in QVALS:
        cls = ' class="row-a"' if q == max(QVALS) else ''
        cells.append(f'<td{cls}>{cnt[q]}人</td>')
    tr.append('<tr><td class="l"><b>人数</b></td>' + ''.join(cells) + '</tr>')
    tr.append('</table>')
    tr.append(f'<div class="dim" style="margin-top:6px">Top20 合计 {fmt(sum(ZT))}——每个值都是"逐档限购买光到第 N 档"的固定组合值，没有一个连续自由值；对照世界杯开箱 Top20 全连续值（可复购+锚点）+塔尖 $1,415/$1,330。<b>想多花钱的人被逐档限购硬拒在 {fmt(max(ZT))}</b>。</div>')
    return ''.join(tr)

def prize_notes():
    cards = [
      ('#4691e8', '深海转盘 · 核心大奖', A64['sub'],
       '<b>深海猎手·潜艇行军皮 15065</b>（奖池组321超级大奖；ActvLuckyWheel 1025 c6=321 / c12=本服榜2000）——外显钩子在，但逐档限购 $585 买光墙把深度锁死，Top4 齐顶封顶值。'),
      ('#c08a17', '对照 · 世界杯开箱大奖', A64['soccer'],
       '<b>足球宝贝·爱莉希雅皮肤 5304001</b>——同样挂皮肤大奖，载体=可复购连锁+锚点：max $1,415 首破 $707 买光墙。<b>同一个钩子，深度差在载体形态不在大奖本身</b>——判退役的是"逐档限购转盘"这个形态，不是随机玩法/外显大奖本身。'),
    ]
    h = ['<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:12px">']
    for c, t, img, txt in cards:
        imghtml = (f'<img src="{img}" style="height:96px;max-width:100%;object-fit:contain;border-radius:4px;display:block;margin:0 auto 8px">'
                   if img else '<div style="height:96px;display:flex;align-items:center;justify-content:center;color:#484f58;font-size:22px;margin-bottom:8px">—</div>')
        h.append(f'<div style="background:#0d1117;border:1px solid #30363d;border-top:3px solid {c};border-radius:6px;padding:12px">'
                 f'<div style="font-size:10.5px;font-weight:700;color:{c};letter-spacing:.5px;margin-bottom:8px">{t}</div>'
                 f'{imghtml}<div style="font-size:11px;line-height:1.7;color:#8b949e">{txt}</div></div>')
    h.append('</div>')
    return ''.join(h)

def family_vs_table():
    rows = [
      ('转盘族（W1 核心）', [('转盘连锁5档', WHEEL), ('BP转盘线', BPW), ('藏宝图锚点', ANC)]),
      ('大富翁族（W2 核心）', [(k.replace('(130036/37)',''), dm[k]) for k in MONO_KEYS]),
    ]
    tr = ['<table><tr><th class="l">族 / 件</th><th>收入</th><th>买家</th><th>付费玩家付费率</th><th>ARPPU</th><th>复购</th><th>max</th></tr>']
    for fam, items in rows:
        tot = sum(m['rev'] for _, m in items)
        tr.append(f'<tr class="row-a"><td class="l"><b>{fam}</b></td><td><b>{fmt(tot)}</b></td><td class="l dim" colspan="5">占深海总盘 {tot/DS["total"]*100:.0f}%</td></tr>')
        for nm, m in items:
            tr.append(f"<tr><td class='l' style='padding-left:26px'>{nm}</td><td>{fmt(m['rev'])}</td><td>{m['buyers']}</td>"
                      f"<td>{m['payrate']:.1f}%</td><td>${m['arppu']:.1f}</td><td>{m['opb']:.1f}</td><td>{fmt(m['max'])}</td></tr>")
    tr.append('</table>')
    tr.append(f"<div class='dim' style='margin-top:6px'>同窗同服段同分母（{PD:,}），绝对值可直比。买家为各件独立计数（未跨件去重）。</div>")
    return ''.join(tr)

# ============ 预生成片段 ============
HT_WHEEL = wheel_table()
HT_TOP20 = top20_chart()
HT_QUANT = quantize_card()
HT_PRIZE = prize_notes()
HT_FAMVS = family_vs_table()

# ============ page ============
page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 深海转盘回归 — tap4fun</title>
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
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">DEEPSEA WHEEL REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">深海转盘回归</div>
    <a class="sb-item" href="#secwheel">结论先行</a>
    <a class="sb-item" href="#wsec1">01 · 转盘族基本盘</a>
    <a class="sb-item" href="#wsec2">02 · Top20 买光墙 · 大奖对照</a>
    <a class="sb-item" href="#wsec3">03 · 两族对打 · 节奏</a>
    <a class="sb-item" href="#wsec4">04 · 结论与动作</a>
    <a class="sb-item" href="母题4_改动效果清单_{END.replace('-','')}.html">← 返回双节回归总页</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 深海转盘回归<br><em>判退役坐实 · 逐档限购第三次锁死复购 · 钩子没错、载体错了</em></h1>
  <div class="meta">窗口 <b>7/3-{END[5:]} · 59服</b>（深海 7/16 收官=终版数据） · 数据 <b>Trino v1090 订单全口径（_l1_m4.json）</b> · 生成 {now}</div>
</div>

<div class="page">
<div class="sec" id="secwheel"><div class="sec-head"><div class="sec-num">★</div><div class="sec-title">深海转盘回归 · 整体结论（7/3-{END[5:]} · 59服）</div></div>
<div class="bigcon">总判词：<b>转盘连锁形式判退役坐实（母题4 · D2 证伪档）</b>——ARPPU ${WHEEL['arppu']:.0f} / 复购 {WHEEL['opb']:.1f} 单（六代垫底档），锚点 4 档 13 天零购买；逐档限购形式第三次证明锁死复购。核心结论：<br>
<span style="font-size:13px;line-height:2.05">
① <b>本体退役证据链齐</b>——转盘连锁 {fmt(WHEEL['rev'])} / {WHEEL['buyers']} 人，ARPPU ${WHEEL['arppu']:.0f}、复购 {WHEEL['opb']:.1f} 单双双垫底；转盘族合计 {fmt(FAM_REV)} 只有大富翁族（{fmt(MONO_REV)}）的一半不到 <a class="con-link" href="#wh1">01 · 基本盘 ↓</a><br>
② <b>买光墙可视化</b>——Top20 全部是逐档限购的量子化固定组合值（{'/'.join(f'${q}' for q in QVALS)}），Top{N_TOP} 齐顶 {fmt(max(ZT))} 封顶：想多花钱的人被规则硬拒 <a class="con-link" href="#wh2">02 · Top20 阶梯 ↓</a><br>
③ <b>钩子没错、载体错了</b>——核心大奖潜艇行军皮 15065（组321超级大奖）外显钩子在场，但深度被限购锁死；对照世界杯开箱同样挂皮肤大奖、载体=可复购连锁，max $1,415 破墙——<b>判退役的是"逐档限购转盘"这个形态，不是随机玩法/外显大奖本身</b> <a class="con-link" href="#wh2">02 · 大奖对照 ↓</a><br>
④ <b>藏宝图锚点 4 档零购买</b>——13 天 $0，纯价格锚；"锚点=获取路径修复"的设计目的没有产生付费 <a class="con-link" href="#wh1">01 · 基本盘 ↓</a><br>
⑤ <b>BP转盘线是渗透工具不是深度工具</b>——{BPW['buyers']} 人买（付费率 {BPW['payrate']:.1f}%）但 max $30 买满即封顶，转盘族近半收入压在一条封顶 $30 的 BP 上 <a class="con-link" href="#wh1">01 · 基本盘 ↓</a><br>
⑥ <b>节奏证伪（D1 关联）</b>——设计=W1 转盘铺量→W2 大富翁攻深度，部署层全部 7/3 同开 14 天无错峰：弹药带没做出来，转盘在 W2 被大富翁全面盖过 <a class="con-link" href="#wh3">03 · 两族对打 ↓</a>
</span></div>

<div class="kpi-row">
  <div class="kpi r"><div class="kpi-val">${WHEEL['arppu']:.0f} · {WHEEL['opb']:.1f}单</div><div class="kpi-lbl">转盘连锁 ARPPU/复购 · 六代垫底档</div><div class="kpi-sub">{fmt(WHEEL['rev'])} / {WHEEL['buyers']} 人 · 判退役核心指标</div></div>
  <div class="kpi y"><div class="kpi-val">Top{N_TOP} 齐顶 {fmt(max(ZT))}</div><div class="kpi-lbl">买光墙 · Top20 全量子值</div><div class="kpi-sub">逐档限购组合值 {'/'.join(f'${q}' for q in QVALS[:4])}… · 无一连续自由值</div></div>
  <div class="kpi r"><div class="kpi-val">$0</div><div class="kpi-lbl">藏宝图锚点 13021-24 · 13天零购买</div><div class="kpi-sub">4 档纯价格锚 · 获取路径修复无付费效果</div></div>
  <div class="kpi"><div class="kpi-val">{fmt(FAM_REV)}</div><div class="kpi-lbl">转盘族合计 · 占深海 {FAM_REV/DS['total']*100:.0f}%</div><div class="kpi-sub">大富翁族 {fmt(MONO_REV)}（{MONO_REV/DS['total']*100:.0f}%）的一半不到 · 近半压在封顶 $30 的 BP 线上</div></div>
</div>

<div class="sec" id="wsec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">转盘族基本盘（连锁 / BP线 / 锚点）</div><a class="backtop" href="#secwheel">↑ 整体结论</a></div></div>
<div class="vlin" id="wh1"><div class="vc">转盘族三件的形态问题各自独立：连锁=逐档限购锁死复购（{WHEEL['opb']:.1f} 单）、BP线=硬封顶 $30（渗透 {BPW['payrate']:.1f}% 全族最高但深度为零）、锚点=零购买——族里没有一件能承接"想继续花钱"的人。</div>
<div class="card"><div class="ct">转盘族逐件 · 收入/三件套/复购/max/形态判读</div>
{HT_WHEEL}
<div class="cb cb-info">读法：转盘连锁复购 {WHEEL['opb']:.1f} 单 vs 尼罗同型转盘复购 2.2、世界杯开箱 4.5——逐档限购的连锁（开箱夏日/情人、深海转盘）复购全部压在 2 上下，可复购形态 3+：<b>复购能力=形态属性，不是题材属性</b>（六代对比数据见开箱独立页 01 章）。</div>
</div></div>

<div class="sec" id="wsec2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">Top20 买光墙 · 核心大奖对照</div><a class="backtop" href="#secwheel">↑ 整体结论</a></div></div>
<div class="vlin" id="wh2"><div class="vc">Top20 付费额全部是"买光到第 N 档"的量子化固定值（{'/'.join(f'${q}' for q in QVALS)}），Top{N_TOP} 齐顶 {fmt(max(ZT))} 封顶——与世界杯开箱 Top20 连续值+塔尖 $1,415 同图对照，同一种外显大奖钩子，深度差完全来自载体形态（逐档限购 vs 可复购）。</div>
<div class="card"><div class="ct">Top20 付费额度阶梯 · 深海转盘族（加粗）vs 夏日/世界杯开箱 · 悬停看每名次金额</div>
{HT_TOP20}
{HT_QUANT}
{HT_PRIZE}
</div></div>

<div class="sec" id="wsec3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">两族对打 · 双周节奏（D1 关联）</div><a class="backtop" href="#secwheel">↑ 整体结论</a></div></div>
<div class="vlin" id="wh3"><div class="vc">同窗同服段同分母直比：大富翁族 {fmt(MONO_REV)}（占深海 {MONO_REV/DS['total']*100:.0f}%）vs 转盘族 {fmt(FAM_REV)}（{FAM_REV/DS['total']*100:.0f}%）——设计里"W1 转盘铺量、W2 大富翁攻深度"的分工，实际部署 7/3 全同开 14 天：节奏证伪（D1），转盘全程被大富翁盖过，退役判定没有"没排好期"的借口。</div>
<div class="card"><div class="ct">转盘族 vs 大富翁族 · 逐件对打（分母统一 {PD:,}）</div>
{HT_FAMVS}
<div class="cb cb-info">对照读法：两族各有一条 BP 线（转盘线 {BPW['buyers']} 人 / 大富翁线 {dm['BP大富翁线(130036/37)']['buyers']} 人，双双 max $30 封顶）——BP 差距是挂靠玩法的人气差；玩法本体差距更大（连锁 {fmt(WHEEL['rev'])} vs 成就+罗盘 {fmt(dm['大富翁成就礼包']['rev']+dm['大富翁罗盘连锁']['rev'])}）。大富翁族的深度解剖见 <a href="深海大富翁回归_{END.replace('-','')}.html" style="color:var(--accent)">深海大富翁回归</a>。</div>
</div></div>

<div class="sec" id="wsec4"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">结论与动作</div><a class="backtop" href="#secwheel">↑ 整体结论</a></div></div>
<div class="card">
<table><tr><th class="l">动作</th><th class="l">内容</th><th class="l">依据</th></tr>
<tr><td class="l"><b>1. 转盘形式退役</b></td>
<td class="l">马戏节克隆深海骨架时，转盘位不再照抄逐档限购转盘；<b>逐档限购不再用于随机模块</b>（三连实证：开箱 $707 墙 / 转盘 {fmt(max(ZT))} 墙 / 大富翁买断件 $792 墙）</td>
<td class="l">01 章六代复购对比 + 02 章买光墙</td></tr>
<tr><td class="l"><b>2. 外显大奖保留 · 换可复购载体</b></td>
<td class="l">潜艇皮这类大奖钩子有效，投放进可复购形态（连锁开箱式 / 随机双轨）；转盘位候选承接=强消耗扭蛋机（X2→X3 搬运案在途，宿主待方案过审定）</td>
<td class="l">02 章大奖对照（同钩子·载体决定深度）</td></tr>
<tr><td class="l"><b>3. 锚点档要么带真获取要么删</b></td>
<td class="l">藏宝图锚点式"纯价格锚"零购买、零作用证据——下届同位置要么给真实获取价值（对齐开箱券锚点 $4.99 小额位），要么不配</td>
<td class="l">01 章锚点 $0</td></tr>
<tr><td class="l"><b>4. 双周节奏要在部署层做出来</b></td>
<td class="l">错峰部署（W2 核心 D7 后再开）才有弹药带——D1 教训，马戏节排期执行项</td>
<td class="l">03 章同开证伪</td></tr>
</table>
</div></div>

<div class="footer">X3 深海转盘回归 · 窗口 7/3-{END[5:]}（深海收官终版） · 数据源=Trino v1090（_l1_refresh.py → _l1_m4.json / _refresh_inline.py → _kx_top20.json） · 生成 {now}</div>
</div>
</div>
</body></html>"""
open(OUT, 'w', encoding='utf-8').write(page)
print('OK ->', OUT)
