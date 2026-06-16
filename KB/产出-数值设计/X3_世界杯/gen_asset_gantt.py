# -*- coding: utf-8 -*-
"""世界杯竞猜 · 资产进包排期甘特图（给 leader 看）。
受众关心:有哪些资产/什么状态/能否赶上每周三封包。砍掉逐场实例数/付费总坑等运营细节。
赛程核实2026-06-16(FIFA/Wiki)。封包=每周三。改资产状态→改 ASSETS 重跑。
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 时间轴: day0 = 6/16(周二,今天)。x=天偏移
DAY0 = "06/16"
TOTAL = 35  # 6/16 ~ 7/20
def d(mmdd):  # mm/dd -> day offset from 6/16
    m, dd = map(int, mmdd.split("/")); base_m, base_d = 6, 16
    return (m - base_m) * 30 + (dd - base_d) if m == 6 else (30 - base_d) + dd  # 6月30天近似
# 精确点位(手算,2026年6月有30天)
def off(mmdd):
    m, dd = map(int, mmdd.split("/"))
    return (dd - 16) if m == 6 else (30 - 16) + dd  # 6/16=0 ... 6/30=14, 7/1=15...

# 周三封包
BUILDS = ["06/17", "06/24", "07/01", "07/08", "07/15"]
# 赛事轮次里程碑
ROUNDS = [("06/28", "32强"), ("07/04", "16强"), ("07/09", "8强"), ("07/14", "四强"), ("07/18", "季军"), ("07/19", "决赛")]

# 资产: (名称, 是什么, 状态key, 进包档, 首投日, 首投标签)
# 状态: ready=已就绪 / art=美术齐待落仓+DK / todo=待产
ASSETS = [
    ("竞猜界面 ActvType64",   "UI框架+代码+prefab(互斥/购买)", "ready", "06/24", "06/28", "32强"),
    ("入口图标 DK_WC_ActvIcon","活动入口图(金奖杯)",          "ready", "06/24", "06/28", "32强"),
    ("真券 item1146",          "世界杯抽奖券道具(配置)",        "ready", "06/24", "06/28", "32强"),
    ("48 队徽+队伍板",         "竞猜界面队伍展示·已落仓+DK",     "ready", "06/24", "06/28", "32强"),
    ("48 头像框(国旗款)",      "R16球队款·已落仓+DK(Personalise)","ready","06/24", "07/04", "16强"),
    ("48 聊天表情(GIF)",       "8强球队款·已落仓+DK(Emoticons)", "ready", "06/24", "07/09", "8强"),
    ("自选头像框宝箱图标",     "$9.99宝箱·图标完,待注册DK+建道具","cfg",  "06/24", "07/09", "8强"),
    ("自选表情宝箱图标",       "$19.99宝箱·图标完,待注册DK+建道具","cfg", "06/24", "07/14", "四强"),
    ("四强专属国旗框 ×8",      "单国旗裹框(库56概念图打底)",     "todo",  "07/08", "07/14", "四强"),
]
ST = {"ready": ("✅ 已就绪(落仓+DK)", "#3fae8a"), "cfg": ("🟡 图标完·待配DK+道具", "#d4a93f"), "todo": ("🔴 待产(R16后)", "#d05a4f")}

LEFT = 360; DAYW = 21; TRACK = TOTAL * DAYW; ROWH = 38
def x(mmdd): return LEFT + off(mmdd) * DAYW

H = ['''<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>世界杯竞猜·资产进包排期</title><style>
:root{--bg:#1a1d24;--ink:#e8e6df;--mut:#9a9486;--line:#363b47}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;padding:26px 22px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--mut);font-size:12.5px;margin-bottom:14px;line-height:1.7}.sub b{color:#d9b65a}
.chart{position:relative;border:1px solid var(--line);border-radius:10px;background:#1e222b;overflow-x:auto}
.hd{position:relative;height:46px;border-bottom:1px solid var(--line)}
.bld{position:absolute;top:0;height:100%;border-left:2px dashed #c98b3a;opacity:.85}
.bld span{position:absolute;top:3px;left:4px;font-size:10.5px;color:#e0a94a;white-space:nowrap}
.rnd{position:absolute;top:24px;font-size:10.5px;color:#7fb0e0;white-space:nowrap;transform:translateX(-50%)}
.rnd i{display:block;width:1px;height:0}
.row{position:relative;height:38px;border-bottom:1px solid #2a2f3a}
.row:hover{background:#232733}
.lbl{position:absolute;left:0;top:0;width:360px;height:100%;padding:5px 10px;border-right:1px solid var(--line)}
.lbl .nm{font-size:12.5px;font-weight:600}.lbl .ds{font-size:10.5px;color:var(--mut)}
.bar{position:absolute;height:18px;top:10px;border-radius:9px;display:flex;align-items:center;padding:0 8px;font-size:10.5px;color:#11141a;font-weight:700;white-space:nowrap;box-shadow:inset 0 -2px 0 rgba(0,0,0,.15)}
.stbadge{position:absolute;right:10px;top:9px;font-size:10.5px;font-weight:600}
.gridline{position:absolute;top:0;bottom:0;width:1px;background:#262b35}
.note{margin-top:14px;color:var(--mut);font-size:12px;line-height:1.9}.note b{color:#d9b65a}
.take{background:#202531;border:1px solid var(--line);border-radius:8px;padding:13px 15px;margin:14px 0;font-size:13px;line-height:1.85}
.take b{color:#5fd0a0}.take .risk{color:#e88}
.legend{display:flex;gap:18px;flex-wrap:wrap;margin:8px 0 14px;font-size:12px}.legend span{display:inline-flex;align-items:center;gap:6px}.dot{width:12px;height:12px;border-radius:3px}
</style></head><body>''']

H.append('<h1>⚽ 世界杯竞猜 · 资产进包排期 <span style="color:#9a9486;font-size:13px;font-weight:400">（对齐每周三封包 + 真实赛程）</span></h1>')
H.append('<div class="sub">活动 <b>6/28 32强 → 7/19 决赛</b> · 封包 <b>每周三</b>（6/24 / 7/1 / 7/8 / 7/15）· 假设 周三封包→当周内上线 · 赛程核实 2026-06-16</div>')

# 结论(leader takeaway)
H.append('<div class="take">📌 <b>一句话结论：核心资产已就绪可进 6/24 首包</b>——界面/入口图/真券/48队徽板/48头像框/48聊天表情 <b>全部已落仓+DK注册完毕</b>（仓库核实）；'
         '剩 <b>2 个自选宝箱</b>(图标已做完，待注册DK+建道具，半天工作量) + '
         '<span class="risk">四强专属国旗框</span>(R16定8强后产8支、进7/8封包、7/14上线，库56概念图打底，紧但可行)。</div>')

H.append('<div class="legend">'
         + ''.join(f'<span><i class="dot" style="background:{c}"></i>{t}</span>' for t, c in ST.values())
         + '<span><i class="dot" style="background:#c98b3a"></i>📦 周三封包</span></div>')

W = LEFT + TRACK + 90
H.append(f'<div class="chart" style="min-width:{W}px">')
# 表头:封包线 + 轮次
H.append(f'<div class="hd" style="width:{W}px">')
H.append(f'<div class="lbl" style="border-bottom:none;font-weight:700;font-size:12px;padding-top:14px">资产 / 是什么</div>')
for b in BUILDS:
    H.append(f'<div class="bld" style="left:{x(b)}px"><span>📦{b}</span></div>')
for r, nm in ROUNDS:
    H.append(f'<div class="rnd" style="left:{x(r)}px">▼{nm}<br>{r}</div>')
H.append('</div>')
# 资产行
for nm, ds, stk, bld, dep, deplbl in ASSETS:
    label, color = ST[stk]
    bx = x(bld); ex = x(dep)
    H.append(f'<div class="row" style="width:{W}px">')
    # 封包竖线(淡)
    for b in BUILDS:
        H.append(f'<div class="gridline" style="left:{x(b)}px"></div>')
    H.append(f'<div class="lbl"><div class="nm">{nm}</div><div class="ds">{ds}</div></div>')
    bar_w = max(ex - bx, 46)
    H.append(f'<div class="bar" style="left:{bx}px;width:{bar_w}px;background:{color}">📦{bld[3:] if False else bld}→{deplbl}</div>')
    H.append('</div>')
H.append('</div>')

H.append('<div class="note">'
         '★ 资产就绪即可<b>提前进首包(6/24)</b>，由配置/导表在对应轮次开启投放——不必等到投放日才进包。<br>'
         '★ <b>待落仓+DK</b>(48头像框/48表情/48队徽)：美术已齐，剩客户端落仓 + DK 注册，工作量明确、无设计风险。<br>'
         '★ <span style="color:#e88">四强国旗框</span>是唯一时间敏感项：依赖 R16 赛果(7/7)定 8 强 → 7/8 封包窗口仅 1~2 天，建议 R16 结束当天即清洗库存概念图。<br>'
         '★ 复用现成：48 头像框 / 48 聊天表情 / 48 队徽队伍板（美术早已产出，非新增）。'
         '</div></body></html>')

OUT = r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\世界杯竞猜_资产进包排期.html"
open(OUT, "w", encoding="utf-8").write('\n'.join(H))
print("生成:", OUT)
