# -*- coding: utf-8 -*-
"""
X3 深海节 功能模块回归 · 独立报告生成器（累充 / 签到 / 酒馆 · 各一图）
数据源 = _func_modules.json（_func_modules.py 产出：累充转化/签到每天人数/酒馆任务完成率）
壳 = 复刻礼包模块回归的 tap4fun 线性壳。深海 7/16 收官=数据终版。兑换=另一 agent 负责，不在本页。
用法: python _gen_功能模块回归.py
"""
import sys, json, os, datetime
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, '_func_modules.json'), encoding='utf-8'))
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
OUT = os.path.join(HERE, "深海节功能模块回归_20260716.html")
RC = F['recharge']; SI = F['signin']; TV = F['tavern']

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
.page{padding:24px 48px 48px;max-width:1000px}
.kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:28px}
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
.dim{color:#8b949e;font-size:11.5px;margin-top:8px;line-height:1.7}
.bigcon{background:linear-gradient(135deg,#1b2436,#161b22);border:1px solid var(--border);border-left:4px solid var(--yellow);border-radius:8px;padding:16px 20px;font-size:14px;line-height:2;color:var(--text);margin-bottom:14px} .bigcon b{color:var(--head)}
.vc{background:#0d2137;border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;font-size:14px;font-weight:700;color:var(--head);line-height:1.9;margin-bottom:12px}
.vc.g{background:#0d2a18;border-left-color:var(--green)} .vc.y{background:#2a2410;border-left-color:var(--yellow)}
.backtop{margin-left:auto;font-size:11px;font-weight:600;color:#8b949e;text-decoration:none;border:1px solid var(--border);border-radius:20px;padding:3px 11px}
.footer{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}
@media(max-width:820px){.sidebar{display:none}.content{margin-left:0}.kpi-row{grid-template-columns:1fr}.page{padding:20px}}
</style>"""

def bars(pairs, w=760, colors=None, unit='', h=250, note=''):
    """竖条：pairs=[(label,value,sublabel)]"""
    maxv = max(v for _,v,_ in pairs) or 1
    n=len(pairs); gap=14; bw=(w-70-gap*(n-1))/n; base=h-40
    svg=[f'<svg viewBox="0 0 {w} {h}" style="width:100%;max-width:{w}px;height:auto">']
    for i,(lab,v,sub) in enumerate(pairs):
        x=55+i*(bw+gap); bh=(v/maxv)*(base-26); y=base-bh
        c=(colors[i] if colors and i<len(colors) else '#58a6ff')
        svg.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="3" fill="{c}" opacity="0.88"/>')
        svg.append(f'<text x="{x+bw/2:.0f}" y="{y-6:.0f}" fill="#f0f6fc" font-size="12.5" font-weight="700" text-anchor="middle">{v:,}{unit}</text>')
        svg.append(f'<text x="{x+bw/2:.0f}" y="{base+16:.0f}" fill="#8b949e" font-size="11" text-anchor="middle">{lab}</text>')
        if sub: svg.append(f'<text x="{x+bw/2:.0f}" y="{base+30:.0f}" fill="#484f58" font-size="10" text-anchor="middle">{sub}</text>')
    svg.append('</svg>')
    return f'<div style="text-align:center;padding:6px 0">{"".join(svg)}</div>' + (f'<div class="dim">{note}</div>' if note else '')

def linechart(points, w=760, h=250, note=''):
    """折线：points=[(label,value)]"""
    maxv=max(v for _,v in points) or 1; n=len(points)
    L,R,T,B=48,20,24,40; iw=w-L-R; ih=h-T-B
    xs=[L+(iw*i/(n-1)) for i in range(n)]; ys=[T+ih-(v/maxv*ih) for _,v in points]
    pts=" ".join(f"{x:.0f},{y:.0f}" for x,y in zip(xs,ys))
    svg=[f'<svg viewBox="0 0 {w} {h}" style="width:100%;max-width:{w}px;height:auto">']
    for gy in range(5):
        yy=T+ih*gy/4; svg.append(f'<line x1="{L}" y1="{yy:.0f}" x2="{w-R}" y2="{yy:.0f}" stroke="#21262d"/>')
        svg.append(f'<text x="{L-6}" y="{yy+3:.0f}" fill="#484f58" font-size="9" text-anchor="end">{maxv*(4-gy)//4:,}</text>')
    svg.append(f'<polyline points="{pts}" fill="none" stroke="#58a6ff" stroke-width="2.5"/>')
    for (lab,v),x,y in zip(points,xs,ys):
        svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3" fill="#58a6ff"/>')
        svg.append(f'<text x="{x:.0f}" y="{y-8:.0f}" fill="#c9d1d9" font-size="9.5" text-anchor="middle">{v:,}</text>')
        svg.append(f'<text x="{x:.0f}" y="{h-14:.0f}" fill="#8b949e" font-size="9" text-anchor="middle" transform="rotate(0 {x:.0f} {h-14})">{lab}</text>')
    svg.append('</svg>')
    return f'<div style="text-align:center;padding:6px 0">{"".join(svg)}</div>' + (f'<div class="dim">{note}</div>' if note else '')

# ===== 结论先行 =====
si_d0=SI[0]['u']; si_peak2=max(x['u'] for x in SI[7:])
rc_part=RC['participants']; rc_t100=next(t['reached'] for t in RC['tiers'] if t['tier_usd']==100)
rc_dead=[t['tier_usd'] for t in RC['tiers'] if t['reached']==0]
tv_avg=sum(t['full_rate'] for t in TV)/len(TV)
concl = f"""<div class="bigcon">总判词：<b>累充 / 签到 / 酒馆=深海的「免费向 & 充值牵引」层，触达远大于付费模块（签到 D0 {si_d0:,} 人 / 酒馆每阶段 4-6k 人=付费买家的一个量级以上），是拉活跃的健康底座</b>。逐条：<br>
① <b>累充=覆盖卡点但高档有档无钩</b>：{rc_part} 名白名单充值者，逐档到 ≥$100 {rc_t100} 人（{rc_t100/rc_part*100:.0f}%），但 <b>≥$1,000 起 4 档全 0 人</b>——档位铺到 $2,000、奖励却是纯资源返利，高 R 没有独占目标可冲 <a class="backtop" href="#s1">01 ↓</a><br>
② <b>签到=最广触达+两期结构</b>：D0 {si_d0:,} 人（≈付费买家的 10×）、随天数衰减，7/10 第二期开启回弹到 {si_peak2:,} 人——免费日常钩子有效、两期设计拉了一次回流 <a class="backtop" href="#s2">02 ↓</a><br>
③ <b>酒馆=参与广、任务完成率高</b>：跨服每阶段 4-6k 人参与，全 7 阶段完成率 {min(t['full_rate'] for t in TV):.0f}-{max(t['full_rate'] for t in TV):.0f}%（均值 {tv_avg:.0f}%）——任务量与难度设计健康，玩家进来基本都能打完 <a class="backtop" href="#s3">03 ↓</a>
</div>"""

kpi = f"""<div class="kpi-row">
  <div class="kpi y"><div class="kpi-val">$1,000+ 归零</div><div class="kpi-lbl">累充顶 4 档到达人数</div><div class="kpi-sub">{rc_part}人参与·覆盖到$700(12人)·再往上纯资源返利无钩</div></div>
  <div class="kpi g"><div class="kpi-val">{si_d0:,} 人</div><div class="kpi-lbl">签到 D0 参与 · ≈付费买家 10×</div><div class="kpi-sub">最广免费触达·第二期回弹 {si_peak2:,} 人</div></div>
  <div class="kpi g"><div class="kpi-val">{tv_avg:.0f}%</div><div class="kpi-lbl">酒馆 7 阶段平均完成率</div><div class="kpi-sub">跨服每阶段 4-6k 人·任务设计健康</div></div>
</div>"""

# ===== 01 累充 =====
rc_pairs=[(f"≥${t['tier_usd']:,}", t['reached'], f"{t['reached']/rc_part*100:.0f}%") for t in RC['tiers']]
rc_colors=['#3fb950','#3fb950','#58a6ff','#58a6ff','#d29922','#d29922','#f85149','#f85149','#f85149','#f85149']
c1 = '<div class="sec" id="s1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">累充转化（深海馈赠 100598 · 累计充值领奖）</div><a class="backtop" href="#top">↑ 结论</a></div></div>'
c1 += f'<div class="vc y">判定：<b>覆盖卡点段、但高档有档无钩</b>——{rc_part} 名充值者逐档递减到 ≥$700 仅 12 人，<b>≥$1,000 起 4 档全 0</b>；档位铺到 $2,000 但奖励纯资源返利，缺高 R 冲刺的独占目标</div>'
c1 += '<div class="card"><div class="ct">累充逐档到达（白名单累计充值 · 标准 X3 十档 · 深海59服 7/3-16）</div>'
c1 += bars(rc_pairs, colors=rc_colors, unit='人',
    note=f'参与者=窗口内买过 ≥1 累充白名单包（45 包）共 <b>{rc_part}</b> 人。逐档：≥$10 {rc_pairs[0][1]}人 → ≥$100 {rc_t100}人（{rc_t100/rc_part*100:.0f}%）→ ≥$400 {[p[1] for p in rc_pairs][4]}人 → ≥$700 {[p[1] for p in rc_pairs][5]}人 → <b>$1,000 以上 4 档全 0</b>。累充把档位一路铺到 $2,000，但顶段无人到达——与开箱/大富翁回归同一结论：<b>高档缺独占外显目标、光给资源返利拉不动大 R</b>。')
c1 += '</div>'

# ===== 02 签到 =====
si_pairs=[(x['d'][5:], x['u']) for x in SI]
c2 = '<div class="sec" id="s2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">签到每天人数（101406 · 2 期）</div><a class="backtop" href="#top">↑ 结论</a></div></div>'
c2 += f'<div class="vc g">判定：<b>最广免费触达 + 两期结构有效</b>——D0 {si_d0:,} 人（≈付费买家 10×），随天数衰减到千级，<b>7/10 第二期开启把人数回弹到 {si_peak2:,}</b>，之后再自然衰减</div>'
c2 += '<div class="card"><div class="ct">签到每天参与人数（深海59服 · 7/3-16）</div>'
c2 += linechart(si_pairs,
    note=f'D0 {si_d0:,} 人是深海全期触达最广的入口（付费买家才 1,815）。曲线两段式：第一期 7/3-9 衰减到 {SI[6]["u"]:,}，<b>第二期 7/10 开启回弹到 {si_peak2:,}</b>（两期签到设计拉了一次回流），末段 {SI[-1]["u"]} 人。免费日常钩子=拉活跃、不直接变现，健康即可，不追付费。')
c2 += '</div>'

# ===== 03 酒馆 =====
tv_pairs=[(f"{t['name']}", t['participants'], f"完成{t['full_rate']:.0f}%") for t in TV]
tv_colors=['#3fb950' if t['full_rate']>=70 else ('#d29922' if t['full_rate']>=55 else '#f85149') for t in TV]
c3 = '<div class="sec" id="s3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">酒馆任务完成率（最佳酒馆 10071704 · 跨服 7 阶段）</div><a class="backtop" href="#top">↑ 结论</a></div></div>'
c3 += f'<div class="vc g">判定：<b>参与广、完成率高、设计健康</b>——跨服每阶段 4-6k 人参与，7 阶段完成率 {min(t["full_rate"] for t in TV):.0f}-{max(t["full_rate"] for t in TV):.0f}%（均值 {tv_avg:.0f}%），玩家进来基本都能打完；最低是「突发危机」阶段（入门率 {[t for t in TV if t["name"]=="突发危机"][0]["entry_rate"]:.0f}%）</div>'
c3 += '<div class="card"><div class="ct">酒馆逐阶段参与人数 + 完成率（完成=达该阶段顶档积分 · 7/3-12）</div>'
c3 += bars(tv_pairs, colors=tv_colors, unit='人',
    note='柱高=该阶段参与人数（跨服，非付费门槛，4-6k 人量级=远超付费买家）；柱下=完成率（达顶档积分 70k，一掷千金档为 50k）。7 阶段完成率 '
    + ' / '.join(f'{t["name"]}{t["full_rate"]:.0f}%' for t in TV)
    + f'。整体均值 {tv_avg:.0f}%、入门率普遍 90%+，说明任务量与难度匹配活动时长——玩家愿意打、也打得完。唯一偏低=<b>突发危机</b>（入门率 {[t for t in TV if t["name"]=="突发危机"][0]["entry_rate"]:.0f}%，危机型任务启动门槛略高）。酒馆是跨服赛事拉活跃/竞争的模块，完成率高=健康，不直接对标付费。')
c3 += '</div>'

page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>X3 深海节功能模块回归 — tap4fun</title>
{CSS}</head><body>
<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">DEEPSEA FUNCTIONAL MODULES</div></div>
  <div class="sb-nav">
    <div class="sb-label">深海节功能模块回归</div>
    <a class="sb-item" href="#top">结论先行</a>
    <a class="sb-item" href="#s1">01 · 累充转化</a>
    <a class="sb-item" href="#s2">02 · 签到每天人数</a>
    <a class="sb-item" href="#s3">03 · 酒馆任务完成率</a>
    <a class="sb-item" href="深海节礼包模块回归_20260716.html">← 深海礼包模块回归</a>
  </div>
</nav>
<div class="content">
<div class="hero-bar" id="top">
  <h1>X3 深海节 · 功能模块回归<br><em>累充转化 · 签到每天人数 · 酒馆任务完成率</em></h1>
  <div class="meta">窗口 <b>7/3-16 · 59服</b>（深海 7/16 收官=终版） · 数据 <b>Trino v1090 订单 + 行为表</b>（累充=订单累计 / 签到·酒馆=ods_user_activity） · 兑换商店=另 agent 负责不在本页 · 生成 {now}</div>
</div>
<div class="page">
<div class="sec"><div class="sec-head"><div class="sec-num">★</div><div class="sec-title">整体结论（累充 / 签到 / 酒馆 · 深海免费向&充值牵引层）</div></div>
{concl}
{kpi}
{c1}
{c2}
{c3}
<div class="footer">X3 深海节功能模块回归 · 累充=订单累计充值(白名单45包) / 签到·酒馆=ods_user_activity 行为表 · 兑换商店另 agent 负责 · 生成 {now}</div>
</div></div></body></html>"""
open(OUT,'w',encoding='utf-8').write(page)
print('saved', OUT)
