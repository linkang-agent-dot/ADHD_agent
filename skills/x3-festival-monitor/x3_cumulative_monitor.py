#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X3 大盘累计付费监控 — 近 2 个月滚动窗口，全折线图：日流水 / 累计付费 / ARPU
   页签 = 不同服段版本（全服 / 各节日开启范围），图上竖线标注各节日上线时间点。

与单节日日报（x3_deepsea_daily.py 等）的分工：
  - 单节日日报 = 某节日的 D0 对齐深挖（模块/R级/同期对比），服段按该节日投放范围
  - 本监控   = 大盘视角：总付费 vs 节日付费（已上线全部节日）的日流水/累计/ARPU 折线，
               回答「节日贡献了大盘多少、ARPU 被节日抬了多少」；
               服段页签让同一服 cohort 内比较曲线（不同节日开启范围不同，全服口径会稀释）

口径：
  - 数仓 TRINO_HF / v1090.ods_user_order，pay_status=1
  - USD 口径同其它 X3 脚本：usd 取 actual_charge，其余取 pay_price（TOKEN 的 actual_charge 是代币单位×100，不能取）
  - 日切 = 北京日（数仓原生 partition_date；大盘总览，不做单节日的 UTC D0 对齐）
  - 节日归属 = 静态谓词 + 时间窗，CASE 链每单只记一个节日（新节日优先），跨节日复用包
    (130020/130021/1002001) 按时间窗归属：7/3 前世界杯窗内归世界杯，7/3 起深海窗内归深海，夏日窗内归夏日
  - 尼罗是滚动回归（无统一窗口/无固定服段），只认 2106xx 专属包，不设页签
  - ARPU 口径 = 流水 / 当日总付费人数（节日 ARPU 分母也是总付费人数，见 feedback_x3_festival_arpu_denominator）

新节日上线时：FESTIVALS 头部加一项（谓词+窗口+颜色+D0标注），需要的话 SEGMENTS 加该节日服段页签。
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-to-sql", "scripts"))
from _datain_api import execute_sql

DATASOURCE = "TRINO_HF"
WINDOW_DAYS = 61  # 近 2 个月（含今天的滚动窗口）——只管折线图 x 轴范围
# 累计/占比 KPI 与累计曲线的起算点 = 夏日节 D0（X3"节日时代"起点，2026-07-06 用户定）：
# 窗口开头那段无节日在线的日子会稀释累计占比，KPI 失真 → 累计从 5/29 起算，折线图窗口不变。
# 若滚动窗口起点晚于它，取窗口起点。
CUM_START = "2026-05-29"
OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-数据分析\节日日报_实时"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REV_EXPR = "(CASE WHEN o.currency_type = 'usd' THEN o.actual_charge ELSE o.pay_price END)"

# 深海节 45 包白名单（2026-07-03 origin/dev ActvOnline 100598 快照；含许愿池 1002001）
_DEEPSEA_IDS = ("'800005','800006','800007','800008','800009','211019','130046','130035',"
                "'211016','211017','211018','211020','211022','211024','211026','211028','211030',"
                "'1002001','2026101','2026102','2026103','2026104','130036','130037',"
                "'207104','207106','207108','207110','207112',"
                "'2801001','2801002','2801003','2801004','2801005','2801006','2801007','2801008',"
                "'2801009','2801010','2801011','280001','13021','13022','13023','13024'")

# 深海 59 服显式清单（合服空 id 已剔，别用 BETWEEN）
_DEEPSEA_SERVERS = ("1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,"
                    "1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,"
                    "1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,"
                    "1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010")

# 节日定义（按 CASE 顺序取第一个命中 → 每单只归一个节日；新的放前面）。d0 用于图上竖线标注。
FESTIVALS = [
    {"name": "深海节", "color": "#38bdf8", "d0": "2026-07-03",
     "pred": (f"(o.iap_id IN ({_DEEPSEA_IDS}) "
              "AND o.created_at >= TIMESTAMP '2026-07-03 08:00:00' "
              "AND o.created_at <  TIMESTAMP '2026-07-17 08:00:00')")},
    {"name": "世界杯", "color": "#6c63ff", "d0": "2026-06-26",
     "pred": ("((o.iap_id LIKE '894%' OR o.iap_id IN "
              "('211002','211004','211006','211008','211010','211012','211013','211014','211015',"
              "'130020','130021','1002001')) "
              "AND o.created_at >= TIMESTAMP '2026-06-26 08:00:00' "
              "AND o.created_at <  TIMESTAMP '2026-07-20 08:00:00')")},
    {"name": "夏日恋语", "color": "#ec4899", "d0": "2026-05-29",
     "pred": ("((o.iap_id LIKE '2109%' OR o.iap_id LIKE '2107%' OR o.iap_id IN "
              "('130020','130021','1002001')) "
              "AND o.created_at >= TIMESTAMP '2026-05-29 08:00:00' "
              "AND o.created_at <  TIMESTAMP '2026-06-29 08:00:00')")},
    {"name": "尼罗(滚动)", "color": "#f59e0b", "d0": None,
     "pred": "(o.iap_id LIKE '2106%')"},
]

# 上线时间点标注（除各节日 D0 外的补充节点）
EXTRA_EVENTS = [
    ("2026-06-09", "夏日批二", "#ec4899"),
    ("2026-06-19", "夏日批三", "#ec4899"),
]

# 服段页签（key 用 ASCII，label 展示；filter 为空 = 全服）
SEGMENTS = [
    {"key": "all", "label": "全服", "note": "全部服务器",
     "filter": ""},
    {"key": "worldcup", "label": "世界杯范围 1-98服", "note": "server_id 1000-1970（世界杯全服投放段）",
     "filter": "AND TRY_CAST(o.server_id AS INTEGER) BETWEEN 1000 AND 1970"},
    {"key": "deepsea", "label": "深海节范围 59服", "note": "server_id 1170-2010 非连续显式清单（D35+ 老服）",
     "filter": f"AND TRY_CAST(o.server_id AS INTEGER) IN ({_DEEPSEA_SERVERS})"},
    {"key": "core88", "label": "总效果 1-88服", "note": ("server_id 1000-1870（成熟服基本盘=夏日第一批投放段；"
     "所有指标含节日收入都只算这 88 服内的订单，1880+ 年轻服的节日收入已剔除——年轻服处于新服爆发期会把 ARPU 趋势带偏，"
     "看节日净拉动认这个页签）"),
     "filter": "AND TRY_CAST(o.server_id AS INTEGER) BETWEEN 1000 AND 1870"},
]


def query(sql):
    return execute_sql(sql.strip().rstrip(";"), DATASOURCE) or []


def cum(series):
    out, s = [], 0.0
    for v in series:
        s += v
        out.append(s)
    return out


def date_range(start, end):
    d0 = datetime.strptime(start, "%Y-%m-%d")
    d1 = datetime.strptime(end, "%Y-%m-%d")
    return [(d0 + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((d1 - d0).days + 1)]


# ---------- 图形渲染 ----------
COLORS = {f["name"]: f["color"] for f in FESTIVALS}
W, H, PAD_L, PAD_R, PAD_T, PAD_B = 1160, 320, 64, 16, 26, 42


def line_chart(days, series_list, events, money_fmt="auto"):
    """series_list = [(label, color, width, dash, [values])]；events = [(date,label,color)] 竖线标注。"""
    n = len(days)

    def sx(i):
        return PAD_L + (W - PAD_L - PAD_R) * (i / max(n - 1, 1))

    ymax = max((max(s[4]) for s in series_list if s[4]), default=1) * 1.08 or 1

    def sy(v):
        return PAD_T + (H - PAD_T - PAD_B) * (1 - v / ymax)

    def ylab(v):
        if money_fmt == "small" or ymax < 5000:
            return f"${v:,.0f}" if ymax >= 50 else f"${v:.1f}"
        return f"${v/1000:.0f}k"

    parts = []
    for gy in range(5):
        v = ymax / 4 * gy
        parts.append(f"<line x1='{PAD_L}' y1='{sy(v):.1f}' x2='{W-PAD_R}' y2='{sy(v):.1f}' class='grid'/>"
                     f"<text x='{PAD_L-6}' y='{sy(v)+4:.1f}' class='ylab'>{ylab(v)}</text>")
    # 节日上线竖线标注
    idx = {d: i for i, d in enumerate(days)}
    for edate, elabel, ecolor in events:
        if edate in idx:
            x = sx(idx[edate])
            parts.append(f"<line x1='{x:.1f}' y1='{PAD_T-6}' x2='{x:.1f}' y2='{H-PAD_B}' "
                         f"stroke='{ecolor}' stroke-width='1' stroke-dasharray='2 3' opacity='0.85'/>"
                         f"<text x='{x+3:.1f}' y='{PAD_T+2}' class='evlab' fill='{ecolor}'>{elabel}▶{edate[5:]}</text>")
    for label, color, width, dash, vals in series_list:
        pts = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, v in enumerate(vals))
        d = f" stroke-dasharray='{dash}'" if dash else ""
        parts.append(f"<polyline points='{pts}' fill='none' stroke='{color}' stroke-width='{width}'{d}/>")
        for i, v in enumerate(vals):
            fmt = f"${v:,.0f}" if ymax >= 100 else f"${v:.2f}"
            parts.append(f"<circle cx='{sx(i):.1f}' cy='{sy(v):.1f}' r='6' fill='transparent'>"
                         f"<title>{days[i]} {label} {fmt}</title></circle>")
    step = max(1, n // 15)
    for i in range(0, n, step):
        parts.append(f"<text x='{sx(i):.1f}' y='{H-8}' class='xlab'>{days[i][5:]}</text>")
    return f"<svg viewBox='0 0 {W} {H}'>" + "".join(parts) + "</svg>"


def legend(series_list):
    return "".join(f"<span class='lg'><i style='background:{c}'></i>{lb}</span>"
                   for lb, c, _, _, _ in series_list)


def build_segment(seg, days, fest_case, start, end, events):
    """跑一个服段的两条查询，返回 (section_html, console_line)。"""
    sf = seg["filter"]
    sql_rev = f"""
    SELECT pd, fest, round(sum(rev),0) rev
    FROM (
      SELECT o.partition_date pd, {fest_case} fest, {REV_EXPR} rev
      FROM v1090.ods_user_order o
      WHERE o.pay_status=1 AND o.partition_date BETWEEN '{start}' AND '{end}' {sf}
    ) GROUP BY 1,2 ORDER BY 1
    """
    sql_payers = f"""
    SELECT o.partition_date pd, count(distinct o.user_id) payers
    FROM v1090.ods_user_order o
    WHERE o.pay_status=1 AND o.partition_date BETWEEN '{start}' AND '{end}' {sf}
    GROUP BY 1 ORDER BY 1
    """
    rows, prows = query(sql_rev), query(sql_payers)
    names = [f["name"] for f in FESTIVALS]
    per_day = {n: {} for n in names + ["非节日"]}
    for r in rows:
        if r["fest"] in per_day:
            per_day[r["fest"]][r["pd"]] = float(r["rev"] or 0)
    payers = {r["pd"]: int(r["payers"] or 0) for r in prows}

    total_by_day = [sum(per_day[n].get(d, 0) for n in per_day) for d in days]
    fest_by_day = [sum(per_day[n].get(d, 0) for n in names) for d in days]
    # 累计从 CUM_START(夏日D0) 起算：之前的日子日线照画、不进累计（避免无节日时段稀释占比）
    i0 = next((i for i, d in enumerate(days) if d >= CUM_START), 0)

    def cum_from(series):
        out, s = [], 0.0
        for i, v in enumerate(series):
            if i >= i0:
                s += v
            out.append(s)
        return out

    cum_total, cum_fest = cum_from(total_by_day), cum_from(fest_by_day)
    arpu_total = [total_by_day[i] / payers[d] if payers.get(d) else 0 for i, d in enumerate(days)]
    arpu_fest = [fest_by_day[i] / payers[d] if payers.get(d) else 0 for i, d in enumerate(days)]

    fest_totals = {n: sum(v for d, v in per_day[n].items() if d >= CUM_START) for n in names}
    grand_total, grand_fest = cum_total[-1], cum_fest[-1]
    share = grand_fest / grand_total * 100 if grand_total else 0
    payer_sum = sum(v for d, v in payers.items() if d >= CUM_START) or 1
    w_arpu, w_arpu_fest = grand_total / payer_sum, grand_fest / payer_sum
    cum_days = len(days) - i0

    daily_series = ([("总付费", "#e2e8f0", 2.5, "", total_by_day),
                     ("节日合计", "#00d4aa", 2.5, "", fest_by_day)]
                    + [(nm, COLORS[nm], 1.5, "5 3", [per_day[nm].get(d, 0) for d in days])
                       for nm in names if fest_totals[nm] > 0])
    cum_series = ([("总付费累计", "#e2e8f0", 2.5, "", cum_total),
                   ("节日合计累计", "#00d4aa", 2.5, "", cum_fest)]
                  + [(nm, COLORS[nm], 1.5, "5 3", cum_from([per_day[nm].get(d, 0) for d in days]))
                     for nm in names if fest_totals[nm] > 0])
    arpu_series = [("大盘ARPU", "#e2e8f0", 2.5, "", arpu_total),
                   ("节日ARPU", "#00d4aa", 2.5, "", arpu_fest)]

    kpi_fest = "".join(
        f"<div class='kpi'><div class='k-label' style='color:{COLORS[n_]}'>{n_}</div>"
        f"<div class='k-val'>${fest_totals[n_]:,.0f}</div>"
        f"<div class='k-sub'>{fest_totals[n_]/grand_total*100 if grand_total else 0:.1f}% 大盘</div></div>"
        for n_ in names)

    section = f"""
<div class="seg" id="seg-{seg['key']}">
<div class="sub">服段：{seg['note']}</div>
<div class="kpis">
  <div class="kpi"><div class="k-label">总付费(自夏日D0累计)</div><div class="k-val">${grand_total:,.0f}</div><div class="k-sub">{CUM_START} 起 {cum_days} 天</div></div>
  <div class="kpi"><div class="k-label" style="color:#00d4aa">节日付费合计</div><div class="k-val">${grand_fest:,.0f}</div><div class="k-sub">占大盘 {share:.1f}%</div></div>
  <div class="kpi"><div class="k-label">大盘ARPU(自夏日D0)</div><div class="k-val">${w_arpu:.2f}</div><div class="k-sub">节日贡献 ${w_arpu_fest:.2f}</div></div>
  {kpi_fest}
</div>
<div class="card"><h2>① 日流水折线（白=总付费 / 绿=节日合计 / 虚线=各节日；竖线=节日上线点）</h2>{legend(daily_series)}{line_chart(days, daily_series, events)}</div>
<div class="card"><h2>② 累计付费折线（累计自 {CUM_START} 夏日D0 起算=节日时代起点；之前日子只画日线不进累计）</h2>{legend(cum_series)}{line_chart(days, cum_series, events)}</div>
<div class="card"><h2>③ ARPU 折线（分母=当日总付费人数；节日ARPU=节日流水/总付费人数）</h2>{legend(arpu_series)}{line_chart(days, arpu_series, events, money_fmt="small")}</div>
</div>"""
    console = (f"[{seg['label']}] 总 ${grand_total:,.0f} | 节日 ${grand_fest:,.0f} ({share:.1f}%) | ARPU ${w_arpu:.2f}")
    return section, console


def main():
    today = datetime.now()
    start = (today - timedelta(days=WINDOW_DAYS - 1)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    days = date_range(start, end)

    fest_case = "CASE " + " ".join(
        f"WHEN {f['pred']} THEN '{f['name']}'" for f in FESTIVALS) + " ELSE '非节日' END"
    events = ([(f["d0"], f["name"], f["color"]) for f in FESTIVALS if f["d0"]]
              + EXTRA_EVENTS)
    events = [e for e in events if start <= e[0] <= end]
    events.sort(key=lambda e: e[0])

    sections, consoles = [], []
    for seg in SEGMENTS:
        sec, con = build_segment(seg, days, fest_case, start, end, events)
        sections.append(sec)
        consoles.append(con)

    tabs = "".join(
        f"<button class='tab-btn{' active' if i == 0 else ''}' data-seg='seg-{s['key']}'>{s['label']}</button>"
        for i, s in enumerate(SEGMENTS))

    html = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>X3 累计付费监控（近2个月）</title><style>
body{{background:#0f1420;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;margin:0;padding:24px}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#8892a4;font-size:12px;margin-bottom:14px}}
.tabs{{margin:14px 0 18px}} .tab-btn{{background:#161d2e;color:#a5b4cf;border:1px solid #232c42;border-radius:8px;
padding:7px 16px;margin-right:8px;font-size:13px;cursor:pointer}}
.tab-btn.active{{background:#00d4aa22;color:#00d4aa;border-color:#00d4aa}}
.seg{{display:none}} .seg.show{{display:block}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}}
.kpi{{background:#161d2e;border:1px solid #232c42;border-radius:10px;padding:12px 18px;min-width:130px}}
.k-label{{font-size:12px;color:#8892a4}} .k-val{{font-size:22px;font-weight:700;margin:2px 0}}
.k-sub{{font-size:11px;color:#8892a4}}
.card{{background:#161d2e;border:1px solid #232c42;border-radius:10px;padding:16px;margin-bottom:18px;overflow-x:auto}}
.card h2{{font-size:14px;margin:0 0 10px;color:#a5b4cf}}
svg{{width:100%;height:auto;min-width:900px}}
.grid{{stroke:#232c42;stroke-width:1}} .ylab{{fill:#8892a4;font-size:10px;text-anchor:end}}
.xlab{{fill:#8892a4;font-size:10px;text-anchor:middle}} .evlab{{font-size:9px}}
.lg{{margin-right:14px;font-size:12px;color:#a5b4cf}} .lg i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}}
.footer{{color:#5c677d;font-size:11px;margin-top:8px}}
</style></head><body>
<h1>X3 <span style="color:#00d4aa">累计付费监控</span>（近 2 个月滚动 · 全折线 · 服段页签）</h1>
<div class="sub">窗口 {start} ~ {end}（北京日切·今日为进行中不完整日）· 生成于 {today.strftime('%Y-%m-%d %H:%M')} · 竖线=节日上线时间点</div>
<div class="tabs">{tabs}</div>
{"".join(sections)}
<div class="footer">口径：v1090.ods_user_order pay_status=1；USD=usd取actual_charge其余取pay_price；
节日归属=CASE链每单只记一个节日(新节日优先)，复用包130020/021/1002001按活动时间窗归属；
尼罗为滚动回归只认2106xx专属包(无固定服段不设页签)；ARPU分母=当日总付费人数。谓词/窗口/服段见 x3_cumulative_monitor.py。</div>
<script>
const btns=document.querySelectorAll('.tab-btn'),segs=document.querySelectorAll('.seg');
function show(id){{segs.forEach(s=>s.classList.toggle('show',s.id===id));
btns.forEach(b=>b.classList.toggle('active',b.dataset.seg===id));}}
btns.forEach(b=>b.addEventListener('click',()=>show(b.dataset.seg)));
show('seg-all');
</script>
</body></html>"""

    latest = os.path.join(OUTPUT_DIR, "X3累计付费日报_latest.html")
    with open(latest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成: {latest}")
    for c in consoles:
        print(c)


if __name__ == "__main__":
    main()
