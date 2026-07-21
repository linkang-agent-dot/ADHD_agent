# -*- coding: utf-8 -*-
"""X3 奇观排期错配审计报告 · tap4fun 壳（侧边栏+verdict+KPI+编号章节+静态SVG甘特）。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# ---------- 甘特数据（游戏天数：刻度 N = 第 N 天 0 点；配置 Nd = 第 N+1 天 0 点生效） ----------
# kind: fixed(绿)/today(蓝)/pending(黄点→蓝虚框)/gap(红)
ROWS = [
    ("group", "奇观主线锚点", None),
    ("span", dict(label="3级奇观·永恒之岛 首次报名期", sub="TimeCycle 10301 · 48h",
                  old=(21,23), new=(30,32), kind="fixed", st=("ok","✅ 06-03 X3NEW-792"))),
    ("span", dict(label="永恒之岛 争夺战（报名结束即开打·24h）", sub="UnitConfigWonder 243001 推导",
                  old=(23,24), new=(32,33), kind="fixed", st=("ok","✅ 随报名期推导"))),
    ("pt",   dict(label="奇观赛季首次更新（赛季1→2 切换）", sub="TimeCycle 10501 · 截图“距赛季结束18分钟”来源",
                  old=24, new=33, kind="today", st=("blue","✅ 今日修复 c0064370"))),
    ("group", "结算发奖类活动 —— 错配即「全员第一名」事故源 · 均已只增不改修复", None),
    ("span", dict(label="永恒之岛 赛季1积分活动", sub="旧 101207/TC1207 → 新 101211/TC1211 · RankID 114",
                  old=(18,24), new=(27,33), kind="fixed", st=("ok","✅ e13db23 + dd0e1887"))),
    ("span", dict(label="永恒之岛 赛季2积分活动", sub="旧 101208/TC1208 → 新 101212/TC1212 · RankID 115",
                  old=(33,39), new=(44,50), approx=True, kind="fixed", st=("ok","✅ e13db23 + dd0e1887"))),
    ("span", dict(label="王座个人KE「永恒之主」", sub="旧 100607/TC607 → 新 100608/TC608 · RankID 109",
                  old=(23,24), new=(32,33), kind="fixed", st=("ok","✅ 07-20 e637449b"))),
    ("span", dict(label="武道冠军之路", sub="旧 105501/TC619 → 新 105502/TC624 · RankID 165",
                  old=(22,29), new=(26,33), approx=True, kind="fixed", st=("ok","✅ 07-20 e637449b"))),
    ("group", "展示 / 商店类 —— 第3类清单（07-21 fd69ae8d 已修，11000 除外）", None),
    ("pt",   dict(label="英雄显示·琥珀（赛季2英雄）", sub="TC2007 ← Hero 1009 ShowTimecycleID",
                  old=24, new=33, kind="fixed", st=("ok","✅ 07-21 fd69ae8d 23d→32d"))),
    ("pt",   dict(label="巢穴商店·琥珀商品显示窗", sub="TC10601 ← ShopItemCfg 120402/120405",
                  old=24, new=33, kind="fixed", st=("ok","✅ 07-21 fd69ae8d 23d→32d"))),
    ("pt",   dict(label="每日特惠·学者（奇观1期）", sub="TC9000 ← 每日特惠 DailyPack",
                  old=24, new=33, kind="fixed", st=("ok","✅ 07-21 fd69ae8d 23d→32d"))),
    ("pt",   dict(label="每日特惠·提炼师（奇观2期）", sub="TC9001 ← DailyPack 100",
                  old=39, new=50, approx=True, kind="fixed", st=("ok","✅ fd69ae8d 第8周周一"))),
    ("pt",   dict(label="每日特惠·制盾人（奇观3期）", sub="TC9002 ← DailyPack 101",
                  old=54, new=71, approx=True, kind="fixed", st=("ok","✅ fd69ae8d 第11周周一"))),
    ("pt",   dict(label="全服地图入口开放 ⚠ 功能解锁·影响最大", sub="TC11000 ← FunctionUnlockTask 7312105~30（功能731）",
                  old=24, new=33, kind="pending", st=("warn","⏳ 策划+服务端确认"))),
    ("group", "遗留缺口（07-21 深夜批次已修，仅剩 11000 待服务端确认）", None),
    ("span", dict(label="永恒之岛 赛季3积分活动 —— 已换新排期 101213", sub="101209/TC1209 · IsOn=1 · RankID 116 · 47d起6天/15d循环",
                  old=(48,54), new=(65,71), approx=True, kind="fixed", st=("ok","✅ 07-21 fd69ae8d→101213"))),
]

D0, D1 = 14, 76
GL, GR = 268, 176            # 左标签宽 / 右状态宽
PW = 1160 - GL - GR
RH, GH = 40, 30              # 数据行高 / 分组行高
TOPAX, BOTAX = 40, 30

C = dict(bg="#0d1117", card="#161b22", grid="#21262d", border="#30363d",
         text="#c9d1d9", head="#f0f6fc", mut="#8b949e", dim="#484f58",
         green="#3fb950", red="#f85149", yellow="#d29922", blue="#58a6ff")
STC = {"ok": C["green"], "blue": C["blue"], "warn": C["yellow"], "bad": C["red"]}

def x(d): return GL + (d - D0) / (D1 - D0) * PW

def esc(s): return s.replace("&","&amp;").replace("<","&lt;")

def gantt():
    H = TOPAX + sum(GH if r[0]=="group" else RH for r in ROWS) + BOTAX
    s = [f'<svg viewBox="0 0 1160 {H}" style="width:100%;background:{C["bg"]};border:1px solid {C["border"]};border-radius:6px" font-family="-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif">']
    s.append(f'<defs><marker id="arr" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="{C["mut"]}"/></marker></defs>')
    body_top, body_bot = TOPAX, H - BOTAX
    # 网格 + 轴刻度（上下双排）
    for d in range(15, D1, 5):
        s.append(f'<line x1="{x(d):.1f}" y1="{body_top}" x2="{x(d):.1f}" y2="{body_bot}" stroke="{C["grid"]}"/>')
        for ty in (body_top - 8, body_bot + 16):
            s.append(f'<text x="{x(d):.1f}" y="{ty}" fill="{C["dim"]}" font-size="10" text-anchor="middle">第{d}天</text>')
    # 锚线：第23天(老争夺日) / 第32天(新争夺日)
    for d, col, lab in ((23, C["red"], "第23天 老争夺日"), (32, C["blue"], "第32天 新争夺日")):
        s.append(f'<line x1="{x(d):.1f}" y1="{body_top-4}" x2="{x(d):.1f}" y2="{body_bot}" stroke="{col}" stroke-width="1.6" stroke-dasharray="5 4"/>')
        s.append(f'<text x="{x(d):.1f}" y="{body_top-22}" fill="{col}" font-size="11" font-weight="700" text-anchor="middle">{lab}</text>')
    # 行
    y = TOPAX
    for typ, a, *rest in [(r[0], r[1], r[2] if len(r)>2 else None) for r in ROWS]:
        if typ == "group":
            s.append(f'<rect x="0" y="{y+4}" width="1160" height="{GH-8}" fill="{C["card"]}" rx="4"/>')
            s.append(f'<text x="12" y="{y+GH/2+4}" fill="{C["head"]}" font-size="12" font-weight="700">{esc(a)}</text>')
            y += GH; continue
        r = a; cy = y + RH/2
        s.append(f'<line x1="0" y1="{y+RH}" x2="1160" y2="{y+RH}" stroke="{C["grid"]}"/>')
        # 左标签两行
        s.append(f'<text x="12" y="{cy-3}" fill="{C["text"]}" font-size="11.5" font-weight="600">{esc(r["label"])}</text>')
        s.append(f'<text x="12" y="{cy+11}" fill="{C["dim"]}" font-size="9.5" font-family="Consolas,monospace">{esc(r["sub"])}</text>')
        kind = r["kind"]
        newc = C["blue"] if kind == "today" else C["green"]
        if typ == "span":
            (os_, oe), (ns, ne) = r["old"], r["new"]
            oldfill = "none"
            oldstroke = C["mut"]
            s.append(f'<rect x="{x(os_):.1f}" y="{cy-7}" width="{x(oe)-x(os_):.1f}" height="14" rx="4" fill="{oldfill}" fill-opacity="0.85" stroke="{oldstroke}" stroke-width="1.4" stroke-dasharray="4 3"/>')
            if kind == "gap":
                s.append(f'<rect x="{x(ns):.1f}" y="{cy-7}" width="{x(ne)-x(ns):.1f}" height="14" rx="4" fill="none" stroke="{C["blue"]}" stroke-width="1.4" stroke-dasharray="4 3"/>')
            else:
                s.append(f'<rect x="{x(ns):.1f}" y="{cy-7}" width="{x(ne)-x(ns):.1f}" height="14" rx="4" fill="{newc}"/>')
            a0, a1 = x(oe) + 4, x(ns) - 4
        else:  # pt
            od, nd = r["old"], r["new"]
            if kind == "pending":
                s.append(f'<circle cx="{x(od):.1f}" cy="{cy}" r="6" fill="{C["yellow"]}"/>')
                s.append(f'<circle cx="{x(nd):.1f}" cy="{cy}" r="6" fill="none" stroke="{C["blue"]}" stroke-width="1.6" stroke-dasharray="3 2.5"/>')
            else:
                s.append(f'<circle cx="{x(od):.1f}" cy="{cy}" r="6" fill="none" stroke="{C["mut"]}" stroke-width="1.6" stroke-dasharray="3 2.5"/>')
                s.append(f'<circle cx="{x(nd):.1f}" cy="{cy}" r="6.5" fill="{newc}"/>')
            a0, a1 = x(od) + 9, x(nd) - 9
        if a1 - a0 > 8:
            s.append(f'<line x1="{a0:.1f}" y1="{cy}" x2="{a1:.1f}" y2="{cy}" stroke="{C["mut"]}" stroke-width="1.3" stroke-dasharray="4 3" marker-end="url(#arr)"/>')
        if r.get("approx"):
            s.append(f'<text x="{(x(r["new"][0]) if typ=="span" else x(r["new"]))+2:.1f}" y="{cy-11}" fill="{C["dim"]}" font-size="9">≈周锚</text>')
        cls, txt = r["st"]
        s.append(f'<text x="{1160-GR+10}" y="{cy+4}" fill="{STC[cls]}" font-size="11" font-weight="700">{esc(txt)}</text>')
        y += RH
    s.append('</svg>')
    return "".join(s)

FIG = gantt()

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>X3 奇观排期错配审计 · 巢穴研究提前发奖 — tap4fun</title>
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
.verdict{{margin:20px 48px 0;background:var(--card);border:1px solid var(--border);border-left:4px solid var(--red);border-radius:6px;padding:16px 22px}}
.verdict .vl{{font-size:10px;font-weight:700;letter-spacing:1.5px;color:var(--red);text-transform:uppercase;margin-bottom:5px}}
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
td.mono{{font-family:Consolas,ui-monospace,monospace;font-size:11.5px}}
.g{{color:var(--green);font-weight:700}} .r{{color:var(--red);font-weight:700}} .y{{color:var(--yellow);font-weight:700}}
.row-a{{background:#21262d!important}} .row-a td{{color:var(--head);font-weight:700}}
.cb{{border-radius:6px;padding:10px 14px;margin:10px 0;font-size:12px;line-height:1.7}}
.cb-info{{background:#0d2137;border-left:3px solid var(--accent)}} .cb b{{color:var(--head)}}
.chain{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}}
.chain .step{{background:#0d1117;border:1px solid var(--border);border-radius:6px;padding:10px 12px}}
.chain .n{{font-size:10px;font-weight:800;color:var(--accent)}}
.chain .t{{font-size:12.5px;font-weight:700;color:var(--head);margin:2px 0}}
.chain .d{{font-size:11px;color:#8b949e;line-height:1.55}}
.rec-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.rec{{border-radius:6px;padding:14px 16px;border-left:3px solid}}
.rec.keep{{background:#0d2d1a;border-left-color:var(--green)}} .rec.fix{{background:#2a2a0e;border-left-color:var(--yellow)}} .rec.bad{{background:#3b1212;border-left-color:var(--red)}}
.rec-tag{{font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px}}
.keep .rec-tag{{color:var(--green)}} .fix .rec-tag{{color:var(--yellow)}} .bad .rec-tag{{color:var(--red)}}
.rec-t{{font-size:13px;font-weight:700;color:var(--head);margin-bottom:3px}}
.rec-b{{font-size:11.5px;color:#8b949e;line-height:1.55}}
.footer{{text-align:center;font-size:10.5px;color:#484f58;padding:24px 0;border-top:1px solid var(--border);margin-top:12px}}
</style></head><body>

<nav class="sidebar">
  <div class="sb-logo"><div class="brand">tap<span>4</span>fun</div><div class="sub">WONDER SCHEDULE AUDIT</div></div>
  <div class="sb-nav">
    <div class="sb-label">X3 奇观排期错配审计</div>
    <a class="sb-item" href="#verdict">结论先行</a>
    <a class="sb-item" href="#sec1">01 · 排期迁移甘特</a>
    <a class="sb-item" href="#sec2">02 · 修复落地时间线</a>
    <a class="sb-item" href="#sec3">03 · 第3类清单（交策划）</a>
    <a class="sb-item" href="#sec4">04 · 遗留缺口与行动项</a>
  </div>
</nav>

<div class="content">
<div class="hero-bar">
  <h1>X3 奇观排期错配审计：「巢穴研究」提前发奖<br><em>岛挪 9 天配套没挪 · 空跑结算 · 全员并列第一名</em></h1>
  <div class="meta">分支 <b>dev</b> · 触发 <b>QA 报「赛季还剩 18 分钟结束，永恒岛 8 天后才开，奖励已发且人人第一」</b> · 数据 gdconfig tsv + 服务端 WonderComp/RankSystem · 2026-07-21</div>
</div>

<div class="verdict" id="verdict">
  <div class="vl">VERDICT · 结论先行</div>
  <p><b>① 根因：X3NEW-792（06-03 天下大势 V2）把永恒之岛首次报名从第 21 天挪到第 30 天（TC10301: 20d→29d），但挂在老争夺日「第 23 天」锚点上的一整族配套排期没跟着挪</b>——结算类活动在岛开放前照常开跑、到点结算，全员 0 分同分，排名取并列名次（viewRank），人人并列第 1 按第 1 名档发奖。
  <b>② 截图两个倒计时尾数相同（00:18:37）不是巧合</b>：赛季结束=TC10501（23d 整点）、岛开=TC10301+48h（31d 整点），恰差 8 天。
  <b>③ 修复现状（07-21 深夜批次后）：dev/dev_festival 双线全部修复完毕（dev fd69ae8d #1989 / festival f6709852 #1994），含 101209→101213 与展示/商店类；仅剩 11000 全服地图入口待服务端确认跨服依赖。本地服(3080)已热更并 GM 开启 100201/101211/100608/101213 供实机验证。</b></p>
  <div class="chain">
    <div class="step"><div class="n">STEP ①</div><div class="t">排期错配</div><div class="d">结算类活动仍按老第23天争夺日运行，玩法内容（岛）第30天才解锁</div></div>
    <div class="step"><div class="n">STEP ②</div><div class="t">空跑结算</div><div class="d">活动窗口内无任何可产分玩法，到期照常触发排名结算</div></div>
    <div class="step"><div class="n">STEP ③</div><div class="t">全员同分并列</div><div class="d">RankDetail.viewRank 并列名次：同分共享名次 → 全员 viewRank=1</div></div>
    <div class="step"><div class="n">STEP ④</div><div class="t">全员第 1 名邮件</div><div class="d">按第 1 名档位批量发奖 —— QA 收到的邮件，属 07-20 修复落地前旧配置窗口</div></div>
  </div>
</div>

<div class="page">
<div class="kpi-row">
  <div class="kpi r"><div class="kpi-val">+9 天</div><div class="kpi-lbl">岛屿排期位移 · 配套未同步</div><div class="kpi-sub">10301 第21→30天，D23 锚点全族被甩下</div><span class="kpi-badge bad">错配源头 X3NEW-792</span></div>
  <div class="kpi g"><div class="kpi-val">6 项</div><div class="kpi-lbl">已修复（只增不改，旧行 IsOn=0）</div><div class="kpi-sub">赛季1/2活动 · 王座KE · 冠军之路 · 争夺日 · 今日赛季锚点 10501</div><span class="kpi-badge ok">c0064370 · 导表 #1984 ✓</span></div>
  <div class="kpi r"><div class="kpi-val">1 项</div><div class="kpi-lbl">尚待确认：11000 全服地图入口</div><div class="kpi-sub">功能解锁非纯展示，跨服/KVK 依赖需服务端确认后再挪</div><span class="kpi-badge mid">已修 101209→101213 · festival 已同步</span></div>
</div>

<div class="sec" id="sec1"><div class="sec-head"><div class="sec-num">01</div><div class="sec-title">排期迁移甘特（游戏天数轴 · 第 15 – 75 天）</div></div>
<div class="card">
<div class="ct">虚线框 = 旧排期（已下线/迁移前） · 实心条/点 = 新排期 · 黄点→蓝虚框 = 待策划迁移 · 红条 = 遗留缺口 · 箭头 = 迁移方向</div>
{FIG}
<div class="cb cb-info"><b>读图：</b>横轴为游戏天数（刻度 N = 第 N 天 0 点；配置偏移 Nd = 第 N+1 天 0 点生效，如 29d = 第 30 天开始报名）。红/蓝虚线为老/新争夺日——<b>争夺日的时间条正好从锚线开始铺一天</b>。所有「第一名事故」都发生在仍钉在红线附近的结算类活动；带 ≈周锚 的行按第 N 周周 X 定位，实际日期随开服星期浮动。</div>
</div></div>

<div class="sec" id="sec2"><div class="sec-head"><div class="sec-num">02</div><div class="sec-title">修复落地时间线</div></div>
<div class="card">
<table>
<tr><th>时间</th><th>提交</th><th>分支</th><th class="l">内容</th></tr>
<tr><td class="mono">06-03</td><td class="mono">64d82536</td><td>dev(经qa)</td><td class="l"><span class="r">错配源头</span>：X3NEW-792 天下大势V2 —— 10301 20d→29d、新增阶段353-357（357「世界主宰」D30 解锁3级奇观），配套排期未同步</td></tr>
<tr><td class="mono">07-15</td><td class="mono">5578e755→e13db232</td><td>master→dev</td><td class="l">永恒之岛排期第一轮「直改」方案作废（beta330 双开实锤），改<b>只增不改</b>：新增 TC1211/1212 + 活动 101211/101212</td></tr>
<tr><td class="mono">07-20 10:03</td><td class="mono">dd0e1887</td><td>dev</td><td class="l">旧排期空场下线：101207/101208 IsOn=0</td></tr>
<tr><td class="mono">07-20 16:10</td><td class="mono">e637449b</td><td>dev</td><td class="l">冠军之路(105501→105502) + 王座个人KE(100607→100608) 只增不改对齐第32天争夺日</td></tr>
<tr><td class="mono">07-21 10:24</td><td class="mono">b7ef055a</td><td>dev</td><td class="l">101211/101212 本地化键补齐</td></tr>
<tr><td class="mono">07-21 白天</td><td class="mono">c0064370</td><td>dev</td><td class="l">赛季更新锚点 TC10501：23d→32d（修复"距赛季结束18分钟"错象）· 导表 #1984</td></tr>
<tr><td class="mono">07-21 深夜</td><td class="mono">fd69ae8d</td><td>dev</td><td class="l">收尾：101209→101213（TC1213 第10周周二/21d循环，旧行下线）+ 展示/商店类 5 条对齐 D32 · 导表 #1989</td></tr>
<tr class="row-a"><td class="mono">07-21 深夜</td><td class="mono">f6709852</td><td>dev_festival</td><td class="l">全家桶同步 festival（5新TC+5新活动+5旧行下线+10501+展示商店+Text键，克隆本分支源行防 schema 差异）· 导表 #1994 · 本地服(3080)已热更开活动</td></tr>
</table>
<div class="cb cb-info"><b>QA 收到的全员第一名邮件来自 07-20 修复落地前的旧配置窗口</b>（100607 于第 23 天结算 + 101207 于第 24 天 0 点结算），对应活动现均已下线。</div>
</div></div>

<div class="sec" id="sec3"><div class="sec-head"><div class="sec-num">03</div><div class="sec-title">第 3 类清单：展示/商店类（交策划裁决 · 未擅动）</div></div>
<div class="card">
<table>
<tr><th>TimeCycle</th><th class="l">用途 / 消费方</th><th>目前状态</th><th>预期状态（新时间线）</th><th class="l">改动方案</th></tr>
<tr><td class="mono">2007</td><td class="l">英雄显示·琥珀（赛季2英雄）— Hero 1009 ShowTimecycleID</td><td class="mono">23d</td><td class="mono">32d（赛季2实际开始）</td><td class="l">直改。纯展示窗、无发奖无结算实例</td></tr>
<tr><td class="mono">10601</td><td class="l">巢穴商店·琥珀商品显示 — ShopItemCfg 120402/120405</td><td class="mono">23d</td><td class="mono">32d</td><td class="l">直改，同上</td></tr>
<tr><td class="mono">9000</td><td class="l">每日特惠·学者（奇观1期）— DailyPack</td><td class="mono">23d 00:00:01</td><td class="mono">32d 00:00:01</td><td class="l">直改。商店档位无结算逻辑</td></tr>
<tr><td class="mono">9001</td><td class="l">每日特惠·提炼师（奇观2期）— DailyPack 100</td><td class="mono">38d（老15天节奏）</td><td>第8周周一（21天周锚）</td><td class="l">TriggerType 2→6 填 <b>8 1 00:00:01</b>（与10502同相位）；保守留TT=2填≈49d，<span class="y">二选一交策划</span></td></tr>
<tr><td class="mono">9002</td><td class="l">每日特惠·制盾人（奇观3期）— DailyPack 101</td><td class="mono">53d</td><td>第11周周一</td><td class="l">TT=6 填 <b>11 1 00:00:01</b> 或近似70d，<span class="y">交策划</span></td></tr>
<tr><td class="mono">11000</td><td class="l"><b>全服地图入口开放</b> — FunctionUnlockTask 7312105~30（功能731）</td><td class="mono">23d 起永久</td><td class="mono">32d</td><td class="l"><span class="r">⚠ 玩法功能解锁非纯展示</span>，可能还有跨服匹配/KVK依赖，<b>策划+服务端确认后再动</b></td></tr>
<tr><td class="mono">2008/10602</td><td class="l">雅典娜（赛季3英雄显示/巢穴商店）— Hero 1018 / ShopItemCfg 120403/120406</td><td>第8周周一（TT=6）</td><td>同左</td><td class="l"><span class="g">已对齐，不用动</span>；2008 注释残留"第38天"过时可顺手更正</td></tr>
</table>
</div></div>

<div class="sec" id="sec4"><div class="sec-head"><div class="sec-num">04</div><div class="sec-title">遗留缺口与行动项（3 条）</div></div>
<div class="rec-grid">
  <div class="rec bad"><div class="rec-tag">GAP · 唯一还会发错奖</div><div class="rec-t">1. 101209 赛季3活动仍挂老 TC1209</div><div class="rec-b">47d起6天/15天循环、IsOn=1，与新第3场（第10周周五报名，21天节奏）完全错位——<b>第48-53天将再次空跑结算、全员并列第一</b>。修法=按 101211/101212 同款只增不改补新排期行（5578e75 原计划：第10周周二起/21d循环），旧行 IsOn=0。</div></div>
  <div class="rec fix"><div class="rec-tag">SYNC · 分支</div><div class="rec-t">2. dev_festival 全套未同步</div><div class="rec-b">festival 线只有 10301=29d，7 月这批修复（1211/1212、下线、KE、冠军之路、今日 10501）全缺——新开测试服会完整复现全套事故。走 dev→dev_festival 官方合并流程带过去。</div></div>
  <div class="rec fix"><div class="rec-tag">CONFIRM · 线上</div><div class="rec-t">3. 线上暴露面待确认</div><div class="rec-b">X3NEW-792 于 06-03 进 dev；若 V2 已随版本上 beta/正式服，开服日落在窗口内的服都经历过空跑发奖。策划+运营确认是否需要回收/补偿。</div></div>
  <div class="rec keep"><div class="rec-tag">DONE · 本次</div><div class="rec-t">4. 赛季锚点已补齐（c0064370）</div><div class="rec-b">TC10501 23d→32d，赛季1→2 切换回到「首战争夺结束即切」；"距赛季结束 18 分钟"错象随新配置消失。导表 #1984 SUCCESS，等 QA 环境重部署验证。</div></div>
</div></div>

<div class="footer">口径：游戏天数第 N 天 = 配置偏移 (N-1)d；周锚（第N周周X）按开服日历周，实际日期随开服星期浮动。数据源：gdconfig(origin/dev) TimeCycle/ActvOnline/UnitConfigWonder tsv · x3-project WonderComp/RankSystem/RankDetail。归档：KB\\产出-数值设计\\X3_奇观排期错配\\<br>tap4fun · X3 Wonder Schedule Audit · 2026-07-21</div>
</div></div>
</body></html>"""

path = r'C:\ADHD_agent\KB\产出-数值设计\X3_奇观排期错配\X3奇观排期错配_巢穴研究提前发奖审计_20260721.html'
open(path, 'w', encoding='utf-8').write(html)
print("written", path)
