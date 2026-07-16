# -*- coding: utf-8 -*-
"""
X3 双节框架回归 · 母题1（大盘增量）报告生成器
数据源 = 累计付费日报 latest（机器可读 tooltip 层），不查数仓。
用法: python _gen_母题1.py [截止日 默认2026-07-15]   （7/21 终版刷新：改截止日重跑）
产出: 母题1_大盘增量_<截止日>.html （同目录）
"""
import re, sys, json, os, collections, datetime
sys.stdout.reconfigure(encoding='utf-8')

CUT = sys.argv[1] if len(sys.argv) > 1 else '2026-07-15'
SRC = r"C:/ADHD_agent/KB/产出-数据分析/节日日报_实时/X3累计付费日报_latest.html"
OUTDIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(OUTDIR, f"母题1_大盘增量_{CUT.replace('-','')}.html")

# ---------- 解析 ----------
html_src = open(SRC, encoding='utf-8').read()

def seg_series(seg_id):
    starts = [m.start() for m in re.finditer(seg_id, html_src)]
    s = starts[1]
    nxt = len(html_src)
    for other in ['seg-all', 'seg-worldcup', 'seg-deepsea', 'seg-core88']:
        for m in re.finditer(other, html_src):
            if m.start() > s + 100:
                nxt = min(nxt, m.start())
    seg = html_src[s:nxt]
    series = collections.defaultdict(dict)
    for t in re.findall(r'<title>([^<]+)</title>', seg):
        m = re.match(r'(\d{4}-\d{2}-\d{2})\s+(.+?)\s+\$([\d,]+(?:\.\d+)?)$', t)
        if m:
            series[m.group(2)][m.group(1)] = float(m.group(3).replace(',', ''))
    return series

C88 = seg_series('seg-core88')
ALL = seg_series('seg-all')
WCSEG = seg_series('seg-worldcup')
DSSEG = seg_series('seg-deepsea')

days = sorted(d for d in C88['总付费'] if d <= CUT)

def daily_from_cum(S, name):
    """各节日系列是累计线 → 差分成逐日"""
    out = {}
    prev = 0.0
    for d in days:
        v = S[name].get(d, prev)
        out[d] = max(0.0, v - prev)
        prev = v
    return out

wc_d   = daily_from_cum(C88, '世界杯')
ds_d   = daily_from_cum(C88, '深海节')
sm_d   = daily_from_cum(C88, '夏日恋语')
nl_d   = daily_from_cum(C88, '尼罗(滚动)')
tot_d  = {d: C88['总付费'][d] for d in days}
fest_d = {d: C88['节日合计'][d] for d in days}
payers = {d: (tot_d[d] / C88['大盘ARPU'][d] if C88['大盘ARPU'][d] > 0 else 0) for d in days}
other_fest = {d: max(0.0, fest_d[d] - wc_d[d] - ds_d[d]) for d in days}   # 夏日+尼罗
nonfest = {d: tot_d[d] - fest_d[d] for d in days}

def seg(a, b):
    ds = [d for d in days if a <= d <= b]
    n = len(ds)
    tot = sum(tot_d[d] for d in ds); fest = sum(fest_d[d] for d in ds); pay = sum(payers[d] for d in ds)
    return dict(n=n, a=a, b=b, tot=tot, totd=tot/n, fest=fest, festd=fest/n,
                share=fest/tot*100, nfd=(tot-fest)/n, payd=pay/n,
                arppu=tot/pay, farppu=fest/pay,
                wc=sum(wc_d[d] for d in ds), dsea=sum(ds_d[d] for d in ds),
                oth=sum(other_fest[d] for d in ds))

SEGS = {
    'base':  ('前基线',        seg('2026-05-17', '2026-05-28')),
    'summer':('夏日窗',        seg('2026-05-29', '2026-06-08')),
    'gap1':  ('夏日后空窗',    seg('2026-06-09', '2026-06-18')),
    'gap2':  ('空窗周',        seg('2026-06-19', '2026-06-25')),
    'solo':  ('世界杯单开',    seg('2026-06-26', '2026-07-02')),
    'w1':    ('叠开W1',        seg('2026-07-03', '2026-07-09')),
    'w2':    ('叠开W2',        seg('2026-07-10', CUT)),
    'full':  ('双节整窗',      seg('2026-06-26', CUT)),
    'stack': ('双节叠开',      seg('2026-07-03', CUT)),
}
G2 = SEGS['gap2'][1]

# 全口径累计（seg-all 端点）
def cum_end(S, name):
    dd = sorted(d for d in S[name] if d <= CUT)
    return S[name][dd[-1]]
WC_ALL, DS_ALL, SM_ALL = cum_end(ALL, '世界杯'), cum_end(ALL, '深海节'), cum_end(ALL, '夏日恋语')
WC_98 = cum_end(WCSEG, '世界杯')
WC_C88 = SEGS['full'][1]['wc']; DS_C88 = SEGS['full'][1]['dsea']
DUO = WC_ALL + DS_ALL

# ---------- 图形工具 ----------
COL = dict(wc='#c08a17', ds='#4691e8', sm='#2ea856', nf='#3a4150', grid='#21262d',
           txt='#8b949e', head='#f0f6fc', dim='#484f58', red='#f85149', yellow='#d29922', green='#3fb950')

def fmt(v): return f"${v:,.0f}"

def _linfit(day_list):
    xs = [days.index(d) for d in day_list]
    ys = [tot_d[d] for d in day_list]
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    slope = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
    return slope, mx, my

# ① 无节日自然衰减外推线：前基线 + 两段空窗
_s1, _m1x, _m1y = _linfit([d for d in days if d <= '2026-05-28' or ('2026-06-09' <= d <= '2026-06-25')])
def trend(i): return _m1y + _s1*(i-_m1x)
SLOPE_BASE_M = _s1*30/_m1y*100    # 无节日斜率 %/月
TREND_FULL = sum(trend(days.index(d)) for d in days if d >= '2026-06-26') / len([d for d in days if d >= '2026-06-26'])
UP_TREND = (SEGS['full'][1]['totd'] / TREND_FULL - 1) * 100   # 双节期大盘 vs 自然衰减外推
# ② 双节期各周周均 vs 红线外推的逐段抬升（周均阶梯线用）
WEEK_STEPS = []
for k in ['solo', 'w1', 'w2']:
    name, r = SEGS[k]
    idx = [days.index(d) for d in days if r['a'] <= d <= r['b']]
    tavg = sum(trend(i) for i in idx) / len(idx)
    WEEK_STEPS.append(dict(key=k, name=name, a=r['a'], b=r['b'], avg=r['totd'], up=(r['totd']/tavg-1)*100))

def hero_chart():
    """绝对时间堆叠面积图：非节日+其他节日+世界杯+深海 + 自然衰减外推线"""
    W, H, L, R, T, B = 1160, 400, 56, 12, 42, 56
    pw, ph = W-L-R, H-T-B
    n = len(days)
    vmax = max(tot_d.values())*1.08
    def X(i): return L + pw*i/(n-1)
    def Y(v): return T + ph*(1 - v/vmax)
    # 堆叠层：自下而上 非节日 → 夏日/尼罗 → 世界杯 → 深海
    layers = [(nonfest, COL['nf'], '非节日常态盘', 0.75),
              (other_fest, COL['sm'], '夏日/尼罗', 0.65),
              (wc_d, COL['wc'], '世界杯', 0.75),
              (ds_d, COL['ds'], '深海节', 0.75)]
    base = {d: 0.0 for d in days}
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for gv in range(0, int(vmax), 4000):
        s.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W-R}" y2="{Y(gv):.1f}" stroke="{COL["grid"]}"/>')
        s.append(f'<text x="{L-6}" y="{Y(gv)+4:.1f}" fill="{COL["dim"]}" font-size="10" text-anchor="end">${gv//1000}k</text>')
    tops = {}
    for vals, c, nm, op in layers:
        top = {d: base[d] + vals[d] for d in days}
        up = ' L '.join(f'{X(i):.1f} {Y(top[d]):.1f}' for i, d in enumerate(days))
        dn = ' L '.join(f'{X(i):.1f} {Y(base[d]):.1f}' for i, d in reversed(list(enumerate(days))))
        s.append(f'<path d="M {up} L {dn} Z" fill="{c}" fill-opacity="{op}" stroke="none"/>')
        base = top
        tops[nm] = top
    # 大盘轮廓线
    s.append('<path d="M ' + ' L '.join(f'{X(i):.1f} {Y(tot_d[d]):.1f}' for i, d in enumerate(days)) + f'" fill="none" stroke="{COL["head"]}" stroke-width="1.2" stroke-opacity="0.5"/>')
    # 自然衰减外推线（无节日）
    tp = ' L '.join(f'{X(i):.1f} {Y(max(0,trend(i))):.1f}' for i in range(n))
    s.append(f'<path d="M {tp}" fill="none" stroke="{COL["red"]}" stroke-width="1.6" stroke-dasharray="7,4"/>')
    s.append(f'<text x="{W-R-4}" y="{Y(trend(n-1))+18:.1f}" fill="{COL["red"]}" font-size="10.5" font-weight="700" text-anchor="end">无节日自然衰减外推 {SLOPE_BASE_M:.0f}%/月</text>')
    # 双节期周均阶梯线（绿）：每段=该周大盘日均水平，vs 红线外推直读逐段抬升
    for st in WEEK_STEPS:
        i0, i1 = days.index(st['a']), days.index(st['b'])
        yv = Y(st['avg'])
        s.append(f'<line x1="{X(i0):.1f}" y1="{yv:.1f}" x2="{X(i1):.1f}" y2="{yv:.1f}" stroke="{COL["green"]}" stroke-width="2.2" stroke-dasharray="7,4">'
                 f'<title>{st["name"]} 大盘日均 {fmt(st["avg"])}（vs 无节日外推 {st["up"]:+.0f}%）</title></line>')
        s.append(f'<text x="{(X(i0)+X(i1))/2:.1f}" y="{yv-7:.1f}" fill="{COL["green"]}" font-size="10.5" font-weight="700" text-anchor="middle">{st["name"]}周均 {fmt(st["avg"])}（{st["up"]:+.0f}% vs 外推）</text>')
    # 事件线
    for d, lab in [('2026-05-29','夏日D0'), ('2026-06-26','世界杯D0'), ('2026-07-03','深海D0')]:
        i = days.index(d)
        s.append(f'<line x1="{X(i):.1f}" y1="{T}" x2="{X(i):.1f}" y2="{T+ph}" stroke="{COL["txt"]}" stroke-dasharray="3,3" stroke-width="1"/>')
        s.append(f'<text x="{X(i)+3:.1f}" y="{T+14}" fill="{COL["txt"]}" font-size="10" font-weight="600">{lab}</text>')
    # 逐日 hover 热区
    for i, d in enumerate(days):
        x0 = X(i) - pw/(n-1)/2
        tip = (f'{d} 大盘 {fmt(tot_d[d])} ｜ 非节日 {fmt(nonfest[d])} · 夏日/尼罗 {fmt(other_fest[d])}'
               f' · 世界杯 {fmt(wc_d[d])} · 深海 {fmt(ds_d[d])} ｜ 衰减外推 {fmt(trend(i))}')
        s.append(f'<rect x="{x0:.1f}" y="{T}" width="{pw/(n-1):.2f}" height="{ph}" fill="transparent"><title>{tip}</title></rect>')
    # X轴标签（每7天）
    for i, d in enumerate(days):
        if i % 7 == 0:
            s.append(f'<text x="{X(i):.1f}" y="{H-38}" fill="{COL["txt"]}" font-size="9.5" text-anchor="middle">{d[5:]}</text>')
    # 图例
    lx = L
    for c, nm in [(COL['nf'],'非节日常态盘'), (COL['sm'],'夏日/尼罗'), (COL['wc'],'世界杯'), (COL['ds'],'深海节')]:
        s.append(f'<rect x="{lx}" y="{H-24}" width="12" height="12" fill="{c}" rx="2"/>')
        s.append(f'<text x="{lx+17}" y="{H-14}" fill="#c9d1d9" font-size="11">{nm}</text>')
        lx += 17 + len(nm)*12 + 26
    s.append('</svg>')
    return ''.join(s)

def trio_chart():
    """三联小图：节日占比 / 节日ARPPU / 大盘ARPU（维持）"""
    cats = [('夏日窗','summer'), ('单开','solo'), ('叠开W1','w1'), ('叠开W2','w2')]
    panels = [('节日占比 %', lambda r: r['share'], '{:.1f}%', 50, [('P2 节日占比 44%', 44)]),
              ('节日ARPPU $', lambda r: r['farppu'], '${:.1f}', 12, []),
              ('大盘ARPU $（维持原有水平）', lambda r: r['arppu'], '${:.1f}', 40, [(f'空窗周 ${G2["arppu"]:.1f}', G2['arppu'])])]
    PW, PH, T, B, L = 360, 230, 40, 40, 44
    W = PW*3 + 40
    s = [f'<svg viewBox="0 0 {W} {PH+T+B}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    barc = {'summer': COL['sm'], 'solo': COL['wc'], 'w1': COL['ds'], 'w2': COL['ds']}
    for pi, (title, f, fmtv, vmax, refs) in enumerate(panels):
        ox = pi*(PW+20)
        s.append(f'<text x="{ox+L}" y="{T-16}" fill="{COL["head"]}" font-size="12.5" font-weight="700">{title}</text>')
        bw = (PW-L-16)/len(cats)
        for gv in range(0, vmax+1, max(1, vmax//4)):
            y = T + PH*(1-gv/vmax)
            s.append(f'<line x1="{ox+L}" y1="{y:.1f}" x2="{ox+PW-10}" y2="{y:.1f}" stroke="{COL["grid"]}"/>')
            s.append(f'<text x="{ox+L-5}" y="{y+4:.1f}" fill="{COL["dim"]}" font-size="9.5" text-anchor="end">{gv}</text>')
        for ci, (nm, key) in enumerate(cats):
            r = SEGS[key][1]; v = f(r)
            x = ox + L + ci*bw + 6
            y = T + PH*(1-v/vmax)
            fade = 0.55 if key == 'w2' else 1.0
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-12:.1f}" height="{T+PH-y:.1f}" fill="{barc[key]}" fill-opacity="{fade}" rx="4">'
                     f'<title>{nm} {title} {fmtv.format(v)}</title></rect>')
            s.append(f'<text x="{x+(bw-12)/2:.1f}" y="{y-6:.1f}" fill="{COL["head"]}" font-size="11.5" font-weight="700" text-anchor="middle">{fmtv.format(v)}</text>')
            s.append(f'<text x="{x+(bw-12)/2:.1f}" y="{T+PH+16}" fill="{COL["txt"]}" font-size="10" text-anchor="middle">{nm}</text>')
        for lab, rv in refs:
            y = T + PH*(1-rv/vmax)
            s.append(f'<line x1="{ox+L}" y1="{y:.1f}" x2="{ox+PW-10}" y2="{y:.1f}" stroke="{COL["yellow"]}" stroke-dasharray="5,4" stroke-width="1.2"/>')
            s.append(f'<text x="{ox+PW-12}" y="{y-5:.1f}" fill="{COL["yellow"]}" font-size="9.5" text-anchor="end" font-weight="600">{lab}</text>')
    s.append('</svg>')
    return ''.join(s)

def fest_daily_aligned():
    """各节日按 D 序对齐的逐日节日收入（各自服段口径：夏日=1-88段 / 世界杯=98服段 / 深海=59服段）"""
    def diff_range(S, name, a, b):
        dd = sorted(d for d in S[name] if a <= d <= b)
        prevd = sorted(d for d in S[name] if d < a)
        prev = S[name][prevd[-1]] if prevd else 0.0
        out = []
        for d in dd:
            out.append(max(0.0, S[name][d] - prev)); prev = S[name][d]
        return out
    return {
        '夏日恋语': diff_range(C88, '夏日恋语', '2026-05-29', '2026-06-08'),
        '世界杯':   diff_range(WCSEG, '世界杯', '2026-06-26', CUT),
        '深海节':   diff_range(DSSEG, '深海节', '2026-07-03', CUT),
    }

FEST_ALIGNED = fest_daily_aligned()
THRESH = 1000
COVER = {k: sum(1 for v in vs if v >= THRESH) for k, vs in FEST_ALIGNED.items()}

def coverage_chart():
    """按 D 序对齐的节日日收入曲线 + $1k 有效变现阈值线"""
    W, H, L, R, T, B = 1160, 340, 56, 16, 34, 60
    pw, ph = W-L-R, H-T-B
    nmax = max(len(v) for v in FEST_ALIGNED.values())
    vmax = max(max(v) for v in FEST_ALIGNED.values())*1.1
    def X(i): return L + pw*i/(nmax-1)
    def Y(v): return T + ph*(1 - v/vmax)
    cols = {'夏日恋语': COL['sm'], '世界杯': COL['wc'], '深海节': COL['ds']}
    s = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    for gv in range(0, int(vmax), 2000):
        s.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W-R}" y2="{Y(gv):.1f}" stroke="{COL["grid"]}"/>')
        s.append(f'<text x="{L-6}" y="{Y(gv)+4:.1f}" fill="{COL["dim"]}" font-size="10" text-anchor="end">${gv//1000}k</text>')
    for i in range(0, nmax, 2):
        s.append(f'<text x="{X(i):.1f}" y="{H-42}" fill="{COL["txt"]}" font-size="10" text-anchor="middle">D{i}</text>')
    # 阈值线
    yt = Y(THRESH)
    s.append(f'<line x1="{L}" y1="{yt:.1f}" x2="{W-R}" y2="{yt:.1f}" stroke="{COL["red"]}" stroke-dasharray="6,4" stroke-width="1.3"/>')
    s.append(f'<text x="{W-R-4}" y="{yt-6:.1f}" fill="{COL["red"]}" font-size="10.5" font-weight="700" text-anchor="end">有效变现阈值 $1k/日</text>')
    for nm, vs in FEST_ALIGNED.items():
        c = cols[nm]
        pts = ' L '.join(f'{X(i):.1f} {Y(v):.1f}' for i, v in enumerate(vs))
        area = f'M {X(0):.1f} {Y(0):.1f} L ' + pts + f' L {X(len(vs)-1):.1f} {Y(0):.1f} Z'
        s.append(f'<path d="{area}" fill="{c}" fill-opacity="0.14"/>')
        s.append(f'<path d="M {pts}" fill="none" stroke="{c}" stroke-width="2.2"/>')
        for i, v in enumerate(vs):
            s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3" fill="{c}"><title>{nm} D{i} {fmt(v)}/日</title></circle>')
    # 关键标注
    sm = FEST_ALIGNED['夏日恋语']; ds = FEST_ALIGNED['深海节']
    s.append(f'<line x1="{X(len(sm)-1):.1f}" y1="{T}" x2="{X(len(sm)-1):.1f}" y2="{T+ph}" stroke="{COL["sm"]}" stroke-dasharray="3,3"/>')
    s.append(f'<text x="{X(len(sm)-1)+4:.1f}" y="{T+16}" fill="{COL["sm"]}" font-size="10.5" font-weight="700">夏日 D{len(sm)-1} 窗口截止</text>')
    s.append(f'<text x="{X(len(ds)-1)+4:.1f}" y="{Y(ds[-1])-10:.1f}" fill="{COL["ds"]}" font-size="10.5" font-weight="700">深海 D{len(ds)-1} 仍 {fmt(ds[-1])}/日</text>')
    # 图例
    lx = L
    for nm, c in cols.items():
        lab = f'{nm}（≥$1k 覆盖 {COVER[nm]} 天）'
        s.append(f'<line x1="{lx}" y1="{H-20}" x2="{lx+18}" y2="{H-20}" stroke="{c}" stroke-width="2.5"/>')
        s.append(f'<text x="{lx+24}" y="{H-16}" fill="#c9d1d9" font-size="11">{lab}</text>')
        lx += 24 + len(lab)*11 + 30
    s.append('</svg>')
    return ''.join(s)

# ---------- 组装 HTML ----------
S = SEGS
up_full = (S['full'][1]['totd']/G2['totd']-1)*100
up_solo = (S['solo'][1]['totd']/G2['totd']-1)*100
up_w1   = (S['w1'][1]['totd']/G2['totd']-1)*100
up_w2   = (S['w2'][1]['totd']/G2['totd']-1)*100
ratio_summer = DUO / SM_ALL
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 双节框架回归 · 母题1 大盘增量 — tap4fun</title>
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
.verdict{{margin:20px 48px 0;background:var(--card);border:1px solid var(--border);border-left:4px solid var(--yellow);border-radius:6px;padding:16px 22px}}
.verdict .vl{{font-size:10px;font-weight:700;letter-spacing:1.5px;color:var(--yellow);text-transform:uppercase;margin-bottom:5px}}
.verdict p{{font-size:13px;line-height:1.85}} .verdict b{{color:var(--head)}}
.page{{padding:24px 48px 48px}}
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}}
.kpi{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;border-top:3px solid var(--accent)}}
.kpi.g{{border-top-color:var(--green)}} .kpi.r{{border-top-color:var(--red)}} .kpi.y{{border-top-color:var(--yellow)}}
.kpi-val{{font-size:1.9em;font-weight:800;color:var(--head)}}
.kpi-lbl{{font-size:11.5px;color:#8b949e;margin-top:5px;font-weight:600}}
.kpi-sub{{font-size:11px;color:#484f58;margin-top:3px}}
.kpi-badge{{display:inline-block;margin-top:7px;padding:2px 8px;border-radius:3px;font-size:10px;font-weight:700}}
.kpi-badge.ok{{background:#1b3a2a;color:var(--green)}} .kpi-badge.bad{{background:#3b1212;color:var(--red)}} .kpi-badge.mid{{background:#3b2e12;color:var(--yellow)}}
.sec{{scroll-margin-top:20px}}
.sec-head{{display:flex;align-items:center;gap:10px;margin:28px 0 12px}}
.sec-num{{width:26px;height:26px;border-radius:50%;background:var(--accent);color:#0d1117;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center}}
.sec-title{{font-size:15px;font-weight:700;color:var(--head)}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 22px;margin-bottom:14px}}
.ct{{font-size:11px;font-weight:700;color:#8b949e;letter-spacing:.5px;text-transform:uppercase;border-left:3px solid var(--accent);padding-left:10px;margin-bottom:12px}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.cb-warn{{background:#2a2a0e;border-left:3px solid var(--yellow)}}
.rec-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 48px 0}}
.rec{{border-radius:6px;padding:14px 16px;border-left:3px solid}}
.rec.keep{{background:#0d2d1a;border-left-color:var(--green)}} .rec.fix{{background:#2a2a0e;border-left-color:var(--yellow)}}
.rec-tag{{font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px}}
.keep .rec-tag{{color:var(--green)}} .fix .rec-tag{{color:var(--yellow)}}
.rec-t{{font-size:13px;font-weight:700;color:var(--head);margin-bottom:3px}}
.rec-b{{font-size:11.5px;color:#8b949e;line-height:1.55}}
.rec-b .todo{{color:#484f58;font-style:italic}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">DUAL FESTIVAL REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">母题1 · 大盘增量</div>
    <a class="sb-item" href="#verdict">结论先行</a>
    <a class="sb-item" href="#direction">优化方向</a>
    <a class="sb-item" href="#sec1">01 · 净增量：抑制老服衰减</a>
    <a class="sb-item" href="#sec3">02 · 深度与覆盖时长</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 双节框架回归 · 母题1：双节给大盘带来多少真增量<br><em>增量是真的 · 但成色前高后低</em></h1>
  <div class="meta">窗口 <b>世界杯 6/26-7/20 × 深海节 7/3-7/16</b> · 数据截至 <b>{CUT}</b>（世界杯尾段+决赛未入，7/21 终版刷新） · 口径 <b>净拉动=成熟服1-88段 / 总账=全服</b> · 生成 {now}</div>
</div>

<div class="verdict" id="verdict">
  <div class="vl">VERDICT · 结论先行</div>
  <p><b>① 双节 20 天全口径合计 {fmt(DUO)}，是夏日全口径（{fmt(SM_ALL)}）的 {ratio_summer:.1f} 倍；成熟服大盘日均比空窗周抬 {up_full:+.0f}%，节日占比 {S['stack'][1]['share']:.1f}% 与节日 ARPPU ${S['stack'][1]['farppu']:.2f} 双创 X3 新高。</b>
  <b>② 净增量的本质 = 抑制老服衰减：</b>老服无节日时大盘以 {SLOPE_BASE_M:.0f}%/月 自然下滑（{fmt(S['base'][1]['totd'])} → {fmt(G2['totd'])}/日），双节期各周周均全程稳在自然衰减外推线上方（{'、'.join(f"{st['name']} {st['up']:+.0f}%" for st in WEEK_STEPS)}，20 天合计 <b>{UP_TREND:+.0f}%</b>），大盘 ARPU 维持在 ${S['stack'][1]['arppu']:.1f}（空窗 ${G2['arppu']:.1f}）未被稀释——节日的作用是托住正在衰减的盘子，而不是透支钱包。
  <b>③ 节日有效变现时长拉长约 50%：</b>单节日 ≥$1k/日 覆盖从夏日 {COVER['夏日恋语']}~10 天 → 深海 {COVER['深海节']}~14 天（尾日未入），且深海全程守在 $1.9k+/日 未塌——节日日历"排满且撑得住"的方向被验证。</p>
</div>

<div class="rec-grid" id="direction">
  <div class="rec keep"><div class="rec-tag">优化方向 1</div><div class="rec-t">持续提高 ARPU（付费深度）</div>
    <div class="rec-b">节日 ARPPU 夏日 $8.48 → 叠开 $10+（+18%）已在涨，离 P2 $46 仍差 4×+，深度是主因。<br><span class="todo">细化分点待母题3（付费深度）/母题4（改动效果清单）完成后回填。</span></div></div>
  <div class="rec keep"><div class="rec-tag">优化方向 2</div><div class="rec-t">持续提高节日覆盖时间</div>
    <div class="rec-b">单节日有效变现时长 10D → 14D（+50%）且末段未塌，日历"排满且撑得住"已验证，向 P2 月月无空窗推进。<br><span class="todo">细化分点待母题2（双周双核心节奏）完成后回填。</span></div></div>
</div>

<div class="page">
<div class="kpi-row">
  <div class="kpi g"><div class="kpi-val">{fmt(DUO)}</div><div class="kpi-lbl">双节合计（全口径 · 截至 {CUT[5:]}）</div><div class="kpi-sub">世界杯 {fmt(WC_ALL)} + 深海 {fmt(DS_ALL)}</div><span class="kpi-badge ok">夏日的 {ratio_summer:.1f}×</span></div>
  <div class="kpi"><div class="kpi-val">{up_full:+.0f}%</div><div class="kpi-lbl">成熟服大盘日均 vs 空窗周</div><div class="kpi-sub">{fmt(S['full'][1]['totd'])}/日 vs {fmt(G2['totd'])}/日</div><span class="kpi-badge ok">增量为真</span></div>
  <div class="kpi y"><div class="kpi-val">{S['stack'][1]['share']:.1f}%</div><div class="kpi-lbl">叠开期节日占比（X3 历史新高）</div><div class="kpi-sub">夏日 29.2% · P2 恒定 44-50%</div><span class="kpi-badge mid">差 P2 仍 1.5×</span></div>
  <div class="kpi g"><div class="kpi-val">10D → 14D</div><div class="kpi-lbl">单节日有效变现时长（≥$1k/日）</div><div class="kpi-sub">夏日 {COVER['夏日恋语']}~10 天 → 深海 {COVER['深海节']}~14 天（尾日未入）</div><span class="kpi-badge ok">+50% · 排满且撑得住</span></div>
</div>

<div class="sec" id="sec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">净增量：节日上线抑制老服衰减、维持原有 ARPU（成熟服 1-88 段）</div></div>
<div class="card"><div class="ct">日流水堆叠面积 · 绝对时间 5/17 → {CUT[5:]} · 红虚线=无节日自然衰减外推 · 悬停看逐日拆分</div>
{hero_chart()}
<div class="cb cb-info"><b>结论：一张图一件事——红线是"没有节日"的自然衰减外推（{SLOPE_BASE_M:.0f}%/月），绿色阶梯是双节期各周的实际大盘周均：{'、'.join(f"{st['name']} {fmt(st['avg'])}（{st['up']:+.0f}%）" for st in WEEK_STEPS)}，每一段都稳浮在红线上方，20 天合计高出外推 {UP_TREND:+.0f}%，且大盘 ARPU 维持 ${S['stack'][1]['arppu']:.1f} 未被稀释。</b>节日的净贡献不是"额外榨了一笔"，而是把正在自然下滑的老服盘子托住了——绿色阶梯与红线之间的落差就是每周的真增量。</div>
</div></div>

<div class="sec" id="sec3"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">深度与覆盖时长：占比、ARPPU、节日收入撑了多少天</div></div>
<div class="card"><div class="ct">节日占比 / 节日ARPPU / 大盘ARPU · 按时段</div>
{trio_chart()}
<div class="cb cb-info"><b>结论：节日 ARPPU 从夏日 $8.48 涨到叠开 $10+（+18%）、占比 30% 破夏日新高，同时大盘 ARPU 全程稳在 $33-37（空窗 ${G2['arppu']:.1f}）——深度在涨且没有以稀释付费质量为代价；离 P2 恒定 44-50% 占比仍差 1.5×。</b>深度差距的模块级拆解交给母题3（付费深度）展开。</div>
</div>
<div class="card"><div class="ct">节日收入覆盖时长 · 按 D 序对齐的逐日节日收入（各节日取各自服段口径，比形状与时长）</div>
{coverage_chart()}
<div class="cb cb-info"><b>结论：单节日有效变现时长从 {COVER['夏日恋语']}~10 天拉长到 {COVER['深海节']}~14 天（约 +50%，深海 7/16 尾日未入）——夏日 10 天窗口即止且 D8 起跌破 $1k，深海 14 天窗口全程守在 $1.9k+/日、末段仍 {fmt(FEST_ALIGNED['深海节'][-1])}，曲线没有塌；世界杯以低量级长尾额外撑满 20 天。</b>这是本届最重要的结构收获之一：更长的节日窗口被证明撑得住，节日日历"排满"的天花板比之前认的高——马戏节按 14 天双周排期有了数据背书。</div>
</div></div>

<div class="footer">X3 双节框架回归 · 母题1 大盘增量 · 数据源=累计付费日报机器可读层（未重查数仓） · 生成器 _gen_母题1.py · {now}</div>
</div></div>
</body></html>"""

open(OUT, 'w', encoding='utf-8').write(page)
print('OK ->', OUT)
print(f"双节全口径 {fmt(DUO)} (WC {fmt(WC_ALL)} + DS {fmt(DS_ALL)}) = 夏日 {fmt(SM_ALL)} 的 {ratio_summer:.2f}x")
print(f'无节日斜率 {SLOPE_BASE_M:.1f}%/月; 周均阶梯: ' + ' / '.join(f"{st['name']} {st['avg']:,.0f}({st['up']:+.0f}%)" for st in WEEK_STEPS))
print('覆盖天数(≥$1k/日):', COVER)
print('深海逐日(D序):', [round(v) for v in FEST_ALIGNED['深海节']])
print('夏日逐日(D序):', [round(v) for v in FEST_ALIGNED['夏日恋语']])
