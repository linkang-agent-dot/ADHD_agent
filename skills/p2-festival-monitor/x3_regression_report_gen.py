# -*- coding: utf-8 -*-
"""回归报告 v5：tap4fun 对外版格式（侧边栏+verdict+KPI卡+编号章节+rec卡）。"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
SC = r'C:\Users\linkang\AppData\Local\Temp\claude\C--Users-linkang\4320db8b-832c-417d-98a5-f5ada22cbf14\scratchpad'
B2  = json.load(open(SC + r'\p2_buckets2.json', encoding='utf-8'))
D   = json.load(open(SC + r'\p2_dist.json', encoding='utf-8'))

def from_b2(key):
    s = B2["series"][key]; v = D[key]
    return {"a": s["a"], "b": s["b"], "buyers": v["buyers"], "mean": v["mean"], "max": v["max"]}

SERIES = [
    ("X3深海·转盘(现役)",    "#f85149", from_b2("X3深海·转盘(连锁+锚点)(D0-D10)"), 2.4, 0.30),
    ("X3世界杯·开箱(最佳)",  "#d29922", from_b2("X3世界杯·开箱族(6/27起D0-D10)"), 2.4, 0.28),
    ("P2圣诞·外圈内圈(目标)","#8b949e", from_b2("P2圣诞24·外圈内圈GACHA(12/20-1/3·15天)"), 1.8, 0.20),
]
A_LABELS = ["$0-10","$10-20","$20-30","$30-40","$40-50","$50-60","$60-70","$70-80","$80-90","$90-100",">$100"]
B_LABELS = [f"${100+i*100}-{200+i*100}" if 200+i*100 < 1000 else f"${(100+i*100)/1000:g}k-{(200+i*100)/1000:g}k" for i in range(19)] + [">$2k"]

def static_chart(key, labels, label_every, annos):
    W,H,ML,MR,MT,MB = 960,320,52,16,14,48
    PW,PH = W-ML-MR, H-MT-MB
    N = len(labels)
    xp = lambda i: ML+(i+0.5)/N*PW
    ymax = 5
    for _,_,v,_,_ in SERIES:
        tot = sum(v["a"]) or 1
        ymax = max(ymax, *[c/tot*100 for c in v[key]])
    ymax = min(100, -(-ymax//5)*5)
    yp = lambda p: MT+(1-p/ymax)*PH
    step = 10 if ymax>50 else (5 if ymax>20 else (2 if ymax>8 else 1))
    s=[f'<svg viewBox="0 0 {W} {H}" style="width:100%;background:#0d1117;border:1px solid #30363d;border-radius:6px">']
    g=0
    while g<=ymax:
        y=yp(g); s.append(f'<line x1="{ML}" y1="{y:.1f}" x2="{W-MR}" y2="{y:.1f}" stroke="#21262d"/>')
        s.append(f'<text x="{ML-8}" y="{y+4:.1f}" fill="#484f58" font-size="10.5" text-anchor="end">{g:g}%</text>')
        g+=step
    for i,b in enumerate(labels):
        if i%label_every==0 or i==N-1:
            s.append(f'<text x="{xp(i):.1f}" y="{H-MB+15}" fill="#8b949e" font-size="9.5" text-anchor="middle" font-weight="600">{b}</text>')
    s.append(f'<text x="{(ML+W-MR)/2}" y="{H-6}" fill="#8b949e" font-size="11" text-anchor="middle">单人在该模块的总付费</text>')
    ly=MT+8
    for name,color,v,wd,op in SERIES:
        tot = sum(v["a"]) or 1
        ys = [c/tot*100 for c in v[key]]
        dp = f'M {xp(0):.1f} {yp(0):.1f} ' + " ".join(f'L {xp(i):.1f} {yp(p):.1f}' for i,p in enumerate(ys)) + f' L {xp(N-1):.1f} {yp(0):.1f} Z'
        s.append(f'<path d="{dp}" fill="{color}" fill-opacity="{op}" stroke="{color}" stroke-width="{wd}"/>')
        for i,p in enumerate(ys):
            if v[key][i]>0: s.append(f'<circle cx="{xp(i):.1f}" cy="{yp(p):.1f}" r="2.4" fill="{color}"/>')
        s.append(f'<line x1="{W-MR-290}" y1="{ly}" x2="{W-MR-270}" y2="{ly}" stroke="{color}" stroke-width="{wd}"/>')
        s.append(f'<text x="{W-MR-264}" y="{ly+4}" fill="#c9d1d9" font-size="10.5">{name}（{v["buyers"]}人·人均${round(v["mean"])}·max${round(v["max"])}）</text>')
        ly+=15
    for (xi,ptop,txt,color) in annos:
        s.append(f'<text x="{xp(xi):.1f}" y="{yp(ptop)-8:.1f}" fill="{color}" font-size="11" font-weight="700" text-anchor="middle">{txt}</text>')
    s.append('</svg>')
    return "".join(s)

figA = static_chart("a", A_LABELS, 1, [(10, 26, "P2 溢出到鲸鱼段 25% vs X3 7-15%", "#8b949e")])
figB = static_chart("b", B_LABELS, 2, [(5, 3.2, "X3 买光墙：转盘$585 / 开箱$960 之后一片空白", "#f85149"),
                                        (14, 1.8, "P2 一路铺到 $2k+", "#8b949e")])

def qrow(name, key, cls=""):
    v = D[key]; g = dict(zip([round(p*100,1) for p in v["pcts"]], v["q"]))
    cells = "".join(f"<td{cls}>${g[p]:,.0f}</td>" for p in [1.0,5.0,10.0,20.0,50.0])
    return f'<tr><td class="l"{cls[7:-1] and ""}>{name}</td>{cells}<td{cls}>${v["max"]:,.0f}</td></tr>'

QT = "\n".join([
  qrow("X3深海·转盘(现役)", "X3深海·转盘(连锁+锚点)(D0-D10)", ' class="r"'),
  qrow("X3夏日·开箱", "X3夏日·开箱族(D0-D10全活动)"),
  qrow("X3世界杯·开箱(最佳)", "X3世界杯·开箱族(6/27起D0-D10)"),
  qrow("X2占星·GACHA(参照)", "X2占星·GACHA(D0-D10)"),
  qrow("P2圣诞·外圈内圈(目标)", "P2圣诞24·外圈内圈GACHA(12/20-1/3·15天)", ' class="g"'),
])

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 抽奖模块回归 · 深海转盘 × 世界杯开箱 — tap4fun</title>
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
.kpi-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:28px}}
.kpi{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px 20px;border-top:3px solid var(--accent)}}
.kpi.g{{border-top-color:var(--green)}} .kpi.r{{border-top-color:var(--red)}}
.kpi-val{{font-size:2em;font-weight:800;color:var(--head)}}
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
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#21262d;color:var(--head);padding:8px 10px;text-align:center;font-weight:600;border-bottom:1px solid var(--border)}}
th.l,td.l{{text-align:left}}
td{{padding:8px 10px;border-bottom:1px solid #21262d;text-align:center}}
tr:hover td{{background:#161b2299}}
.g{{color:var(--green);font-weight:700}} .r{{color:var(--red);font-weight:700}} .y{{color:var(--yellow);font-weight:700}}
.row-a{{background:#21262d!important}} .row-a td{{color:var(--head);font-weight:700}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.rec-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.rec{{border-radius:6px;padding:14px 16px;border-left:3px solid}}
.rec.keep{{background:#0d2d1a;border-left-color:var(--green)}} .rec.fix{{background:#2a2a0e;border-left-color:var(--yellow)}}
.rec-tag{{font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px}}
.keep .rec-tag{{color:var(--green)}} .fix .rec-tag{{color:var(--yellow)}}
.rec-t{{font-size:13px;font-weight:700;color:var(--head);margin-bottom:3px}}
.rec-b{{font-size:11.5px;color:#8b949e;line-height:1.55}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">PAY MODULE REGRESSION</div></div>
  <div class="sb-nav">
    <div class="sb-label">X3 抽奖模块回归</div>
    <a class="sb-item" href="#verdict">结论先行</a>
    <a class="sb-item" href="#sec1">01 · 六代演进对打</a>
    <a class="sb-item" href="#sec2">02 · 0-100刀转化</a>
    <a class="sb-item" href="#sec3">03 · 100刀+转化</a>
    <a class="sb-item" href="#sec4">04 · 付费分位数</a>
    <a class="sb-item" href="#sec5">05 · 调整点</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 抽奖模块回归：深海转盘 × 世界杯开箱<br><em>六代换皮不换形式 · 人均横盘半年 · 唯一爬升=世界杯开箱</em></h1>
  <div class="meta">窗口 <b>深海/世界杯 D0-D10 在途</b> · 对标 <b>P2圣诞外圈内圈(15天全活动)</b> · 数据 v1090/v1041 订单+资产 · 2026-07-13</div>
</div>

<div class="verdict" id="verdict">
  <div class="vl">VERDICT · 结论先行</div>
  <p><b>① X3 抽奖六代换皮不换形式，人均横盘 $33-48 半年；唯一爬升 = 世界杯开箱 $65（锚点可复购 + 外显进付费档），它是外圈内圈方案的底座</b>，差 P2 圣诞（$154）还有 2.4×。
  <b>② 深海转盘判定落后形态：不修补、下节换弹药</b>（复购 2.1 单，连锁档档限购 1 锁死）。
  <b>③ 缺口两段论：0-100 刀段只是略低（形式+阶段奖励可修）；100 刀+ 段是断崖（需高级皮肤+深度循环投放造内容承接）。</b></p>
</div>

<div class="page">
<div class="kpi-row">
  <div class="kpi"><div class="kpi-val">$65</div><div class="kpi-lbl">世界杯开箱 ARPPU · 复购 5.4 单</div><div class="kpi-sub">六代唯一爬升（+35%），锚点复购+外显进档</div><span class="kpi-badge ok">X3 最佳 · 底座</span></div>
  <div class="kpi r"><div class="kpi-val">$44</div><div class="kpi-lbl">深海转盘 ARPPU · 复购 2.1 单</div><div class="kpi-sub">逐档连锁限购最死的一版，全指标垫底</div><span class="kpi-badge bad">判退役</span></div>
  <div class="kpi g"><div class="kpi-val">$154</div><div class="kpi-lbl">P2圣诞外圈内圈 ARPPU · 溢出率 25.4%</div><div class="kpi-sub">单人上限 $8,219 无墙 · 15天 $22.2万</div><span class="kpi-badge mid">目标形态</span></div>
</div>

<div class="sec" id="sec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">核心对打：X3 抽奖模块六代演进 × P2</div></div>
<div class="card">
<table>
<tr><th class="l">模块（时间序）</th><th>窗口</th><th>收入</th><th>买家</th><th>人均(ARPPU)</th><th>复购(单/人)</th><th>$100+溢出率</th><th>天花板(最大单人)</th></tr>
<tr><td class="l">X3元旦·开箱（天马福箱）</td><td>1/1-1/15</td><td>$10,945</td><td>235</td><td>$47</td><td>4.2</td><td>9.8%</td><td>$690</td></tr>
<tr><td class="l">X3情人节·开箱（致她的信）</td><td>2/6-2/16</td><td>$10,232</td><td>246</td><td>$42</td><td>3.3</td><td>10.6%</td><td>$910</td></tr>
<tr><td class="l">X3春节·开箱（剑舞迎春）</td><td>2/16-3/2</td><td>$12,784</td><td>309</td><td>$41</td><td>3.5</td><td>6.5%</td><td>$740</td></tr>
<tr><td class="l">X3尼罗·转盘（滚动1-7月累计）</td><td>滚动</td><td>$25,689</td><td>771</td><td>$33</td><td>2.8</td><td>6.0%</td><td>$1,879*</td></tr>
<tr><td class="l">X3夏日·开箱（复用情人包）</td><td>5/29-6/8</td><td>$11,775</td><td>245</td><td>$48</td><td>4.2</td><td>13.9%</td><td>$550</td></tr>
<tr><td class="l y">X3世界杯·开箱（福箱）</td><td>6/26-7/13</td><td>$13,918</td><td>213</td><td class="y">$65</td><td class="y">5.4</td><td>14.5%</td><td>$960</td></tr>
<tr><td class="l r">X3深海·转盘（现役）</td><td>7/3-7/13</td><td class="r">$5,477</td><td class="r">124</td><td class="r">$44</td><td class="r">2.1</td><td class="r">6.6%</td><td>$585</td></tr>
<tr><td class="l">X2占星·GACHA（参照·双轨）</td><td>5/12-5/21</td><td>$7,257</td><td>115</td><td>$63</td><td>3.1</td><td class="y">20.0%</td><td>$480</td></tr>
<tr class="row-a"><td class="l">P2圣诞·外圈内圈GACHA（目标）</td><td>15天</td><td>$222,232</td><td>1,447</td><td>$154</td><td>4.6</td><td>25.4%</td><td>$8,219</td></tr>
</table>
<div class="cb cb-info"><b>结论：换皮不换形式=白换。</b>前五代换了五次皮、人均横盘 $33-48 半年（形式全同：连锁+锚点+$500-900 买光墙）；唯一一次涨=世界杯 +35%，只因为改了两处形式（锚点可复购+外显进付费档）。升级路径已被验证两级：随机双轨（X2 占星，溢出 20%）→ 三层皮肤+无墙（P2 圣诞，溢出 25%、$154）。*尼罗为数月滚动累计特例。</div>
</div></div>

<div class="sec" id="sec2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">0-100 刀玩家转化 —— 略低：调 gacha 形式 + 各节点阶段奖励</div></div>
<div class="card"><div class="ct">图A · 大众段 $0-100（每$10一档 · 纵轴=买家占比 · 末档=溢出到鲸鱼段）</div>
{figA}
<div class="cb cb-info"><b>结论：0-100 刀段 X3 只是略低、不缺人——大众盘（$50 以下）与 P2 完全打平，短板只在把人推过 $100 的能力</b>（溢出率 P2 25.4% vs 世界杯 14.5% / 深海转盘 6.6%）。对应调整=调 gacha 形式（随机双轨+$0.99 入口）+ 前 100 刀各节点阶段奖励宝箱。</div>
</div></div>

<div class="sec" id="sec3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">100 刀+ 玩家转化 —— 断崖：新增高级皮肤 + 深度循环投放</div></div>
<div class="card"><div class="ct">图B · 鲸鱼段 $100+（每$100一档 · 分母同为该模块全部买家）</div>
{figB}
<div class="cb cb-info"><b>结论：100 刀+ 段是断崖不是斜坡——X3 在 $500-960 处被货架买光墙一刀切断，之后没有任何可买的东西；P2 圣诞同段连续铺到 $2k+（排行皮肤中位 $2,529）。这段不是调参数能修的，必须新增内容承接：排行高级皮肤 + 冲深度的循环抽奖投放。</b></div>
</div></div>

<div class="sec" id="sec4"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">付费分位数对比（该分位买家在此模块的付费额）</div></div>
<div class="card">
<table>
<tr><th class="l">模块</th><th>top1%</th><th>top5%</th><th>top10%</th><th>top20%</th><th>中位数</th><th>最大单人</th></tr>
{QT}
</table>
<div class="cb cb-info"><b>结论：X3 输鲸鱼不输大众。</b>中位买家五家一个价；差距从 top20% 开始拉开，top1% 拉到量级差（X3 转盘 $585 / 世界杯 $745 vs P2 圣诞 $2,515）。世界杯 top5%（$280）已到 X2 占星（$310）水平=X3 内部天花板，再往上只能靠新形式+新内容。</div>
</div></div>

<div class="sec" id="sec5"><div class="sec-head"><div class="sec-num">05</div><div class="sec-title">调整点（4 条）</div></div>
<div class="rec-grid">
  <div class="rec keep"><div class="rec-tag">NEW · 形式</div><div class="rec-t">1. 新增外圈内圈换皮抽奖</div><div class="rec-b">世界杯开箱底座 + 随机双轨 + $0.99 入口 + 跨服排行。依据：六代横盘证明换皮无效、世界杯 +35% 证明改形式见效；X2 双轨溢出率 20%、P2 圣诞 25.4%。</div></div>
  <div class="rec fix"><div class="rec-tag">FIX · 0-100段</div><div class="rec-t">2. 前 100 刀新增阶段奖励宝箱</div><div class="rec-b">累抽/累充里程碑。依据：图A $10-100 段 X3 各档占比略低于 P2，阶段宝箱是最轻的推档手段。</div></div>
  <div class="rec fix"><div class="rec-tag">FIX · 形式</div><div class="rec-t">3. 新增每日随机礼包</div><div class="rec-b">补"缺随机礼包"的形式空位。依据：P2 随机包 ROI 优 0.25-0.31、专吸鲸鱼（异族大富翁随机 57 人 $81k）；X3 全系无随机轨。</div></div>
  <div class="rec keep"><div class="rec-tag">NEW · 100+段</div><div class="rec-t">4. 深度投放品质强化</div><div class="rec-b">跨服排行英雄皮肤新增限定互动/交互解锁；跨服排行主城皮肤搬运 P2 高级主城皮（带动画）。依据：图B 断崖=100+ 段无内容承接；P2 圣诞排行皮上榜线 $1,444/中位 $2,529、获得者贡献总盘 65%。</div></div>
</div></div>

<div class="footer">口径：X3=v1090 订单 pay_status=1；包族=210N01-11连锁双号+210N12-15券锚点；P2圣诞=2024圣诞节GACHA固定+随机（v1041）。分析用交互分位图与皮肤节点明细：《P2三大节拉通_X3动作优先级_20260709.html》。待查桩：深海猎手潜艇/福箱大奖获取价。<br>tap4fun · X3 Pay Module Regression · 2026-07-13</div>
</div></div>
</body></html>"""

path = r'C:\ADHD_agent\KB\产出-数据分析\X3vsP2_节日付费结构对比\X3节日核心付费模块回归优化_20260713.html'
open(path, 'w', encoding='utf-8').write(html)
print("v5 written")
