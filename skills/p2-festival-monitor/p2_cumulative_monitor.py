#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P2 大盘累计付费监控 — 近 2 个月滚动窗口，全折线图：日流水 / 累计付费 / ARPU
   克隆自 X3 x3_cumulative_monitor.py（2026-07-06），改 P2 口径。

与 X3 版的口径差异：
  - 数仓 TRINO_AWS / v1041.dl_user_order（dl 层=成交单，无 pay_status 列）+ v1041.dim_iap
  - 收入 = pay_price（USD 归一价，X2/P2 家族口径，无 TOKEN actual_charge 坑）
  - created_at/partition_date 均北京时间（见 feedback_p2_datain_timezone），北京日切
  - 节日判定 = dim_iap.iap_type='混合-节日活动'（P2 dim 表干净自带节日标记，无需白名单）；
    具体归哪个节日 = 按日期窗切（P2 节日一个接一个跑、几乎不重叠，窗口由日流水曲线实测：
    拓荒节 5/12-6/02 → 空窗 → 深海节 6/10-7/01 → 世界杯竞猜 7/02+）
  - 服段：P2 节日全服开，单页签（保留 SEGMENTS 结构以便日后加段）

新节日上线时：FEST_WINDOWS 头部加一项（名字+起止+颜色），其余不用动。
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-to-sql", "scripts"))
from _datain_api import execute_sql

DATASOURCE = "TRINO_AWS"
WINDOW_DAYS = 61
OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-数据分析\节日日报_实时"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FEST_TYPE_PRED = "i.iap_type = '混合-节日活动'"

# P2 节日时间窗（北京日；end=None 表示进行中；新节日往头部加）
FEST_WINDOWS = [
    {"name": "世界杯竞猜", "color": "#6c63ff", "start": "2026-07-02", "end": None},
    {"name": "深海节", "color": "#38bdf8", "start": "2026-06-10", "end": "2026-07-01"},
    {"name": "拓荒节", "color": "#f59e0b", "start": "2026-05-12", "end": "2026-06-09"},
]

SEGMENTS = [
    {"key": "all", "label": "全服", "note": "全部服务器（P2 节日全服开）", "filter": ""},
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


COLORS = {f["name"]: f["color"] for f in FEST_WINDOWS}
W, H, PAD_L, PAD_R, PAD_T, PAD_B = 1160, 320, 64, 16, 26, 42


def line_chart(days, series_list, events, money_fmt="auto"):
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
    sf = seg["filter"]
    sql_rev = f"""
    SELECT pd, fest, round(sum(rev),0) rev
    FROM (
      SELECT o.partition_date pd, {fest_case} fest, o.pay_price rev
      FROM v1041.dl_user_order o
      LEFT JOIN v1041.dim_iap i ON o.iap_id = i.iap_id
      WHERE o.partition_date BETWEEN '{start}' AND '{end}' {sf}
    ) GROUP BY 1,2 ORDER BY 1
    """
    sql_payers = f"""
    SELECT o.partition_date pd, count(distinct o.user_id) payers
    FROM v1041.dl_user_order o
    WHERE o.partition_date BETWEEN '{start}' AND '{end}' {sf}
    GROUP BY 1 ORDER BY 1
    """
    rows, prows = query(sql_rev), query(sql_payers)
    names = [f["name"] for f in FEST_WINDOWS] + ["节日(窗外)"]
    per_day = {n: {} for n in names + ["非节日"]}
    for r in rows:
        if r["fest"] in per_day:
            per_day[r["fest"]][r["pd"]] = float(r["rev"] or 0)
    payers = {r["pd"]: int(r["payers"] or 0) for r in prows}

    fest_names = [n for n in names]
    total_by_day = [sum(per_day[n].get(d, 0) for n in per_day) for d in days]
    fest_by_day = [sum(per_day[n].get(d, 0) for n in fest_names) for d in days]
    cum_total, cum_fest = cum(total_by_day), cum(fest_by_day)
    arpu_total = [total_by_day[i] / payers[d] if payers.get(d) else 0 for i, d in enumerate(days)]
    arpu_fest = [fest_by_day[i] / payers[d] if payers.get(d) else 0 for i, d in enumerate(days)]

    fest_totals = {n: sum(per_day[n].values()) for n in fest_names}
    grand_total, grand_fest = cum_total[-1], cum_fest[-1]
    share = grand_fest / grand_total * 100 if grand_total else 0
    payer_sum = sum(payers.get(d, 0) for d in days) or 1
    w_arpu, w_arpu_fest = grand_total / payer_sum, grand_fest / payer_sum

    line_names = [n for n in fest_names if fest_totals.get(n, 0) > 0 and n != "节日(窗外)"]
    daily_series = ([("总付费", "#e2e8f0", 2.5, "", total_by_day),
                     ("节日合计", "#00d4aa", 2.5, "", fest_by_day)]
                    + [(nm, COLORS[nm], 1.5, "5 3", [per_day[nm].get(d, 0) for d in days])
                       for nm in line_names])
    cum_series = ([("总付费累计", "#e2e8f0", 2.5, "", cum_total),
                   ("节日合计累计", "#00d4aa", 2.5, "", cum_fest)]
                  + [(nm, COLORS[nm], 1.5, "5 3", cum([per_day[nm].get(d, 0) for d in days]))
                     for nm in line_names])
    arpu_series = [("大盘ARPU", "#e2e8f0", 2.5, "", arpu_total),
                   ("节日ARPU", "#00d4aa", 2.5, "", arpu_fest)]

    kpi_fest = "".join(
        f"<div class='kpi'><div class='k-label' style='color:{COLORS[n_]}'>{n_}</div>"
        f"<div class='k-val'>${fest_totals[n_]:,.0f}</div>"
        f"<div class='k-sub'>{fest_totals[n_]/grand_total*100 if grand_total else 0:.1f}% 大盘</div></div>"
        for n_ in line_names)

    section = f"""
<div class="seg show" id="seg-{seg['key']}">
<div class="sub">服段：{seg['note']}</div>
<div class="kpis">
  <div class="kpi"><div class="k-label">窗口总付费</div><div class="k-val">${grand_total:,.0f}</div><div class="k-sub">{len(days)} 天累计</div></div>
  <div class="kpi"><div class="k-label" style="color:#00d4aa">节日付费合计</div><div class="k-val">${grand_fest:,.0f}</div><div class="k-sub">占大盘 {share:.1f}%</div></div>
  <div class="kpi"><div class="k-label">窗口大盘ARPU</div><div class="k-val">${w_arpu:.2f}</div><div class="k-sub">节日贡献 ${w_arpu_fest:.2f}</div></div>
  {kpi_fest}
</div>
<div class="card"><h2>① 日流水折线（白=总付费 / 绿=节日合计 / 虚线=各节日；竖线=节日上线点）</h2>{legend(daily_series)}{line_chart(days, daily_series, events)}</div>
<div class="card"><h2>② 累计付费折线</h2>{legend(cum_series)}{line_chart(days, cum_series, events)}</div>
<div class="card"><h2>③ ARPU 折线（分母=当日总付费人数；节日ARPU=节日流水/总付费人数）</h2>{legend(arpu_series)}{line_chart(days, arpu_series, events, money_fmt="small")}</div>
</div>"""
    console = f"[{seg['label']}] 总 ${grand_total:,.0f} | 节日 ${grand_fest:,.0f} ({share:.1f}%) | ARPU ${w_arpu:.2f} | " \
              + " | ".join(f"{k} ${v:,.0f}" for k, v in fest_totals.items() if v > 0)
    return section, console


def main():
    today = datetime.now()
    start = (today - timedelta(days=WINDOW_DAYS - 1)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    days = date_range(start, end)

    # 节日归属 CASE：先判节日类目，再按日期窗归节日；窗外的节日类目零星流水归"节日(窗外)"
    win_case = " ".join(
        f"WHEN o.partition_date >= '{f['start']}'"
        + (f" AND o.partition_date <= '{f['end']}'" if f["end"] else "")
        + f" THEN '{f['name']}'"
        for f in FEST_WINDOWS)
    fest_case = f"CASE WHEN {FEST_TYPE_PRED} THEN (CASE {win_case} ELSE '节日(窗外)' END) ELSE '非节日' END"

    events = [(f["start"], f["name"], f["color"]) for f in FEST_WINDOWS]
    events = [e for e in events if start <= e[0] <= end]
    events.sort(key=lambda e: e[0])

    sections, consoles = [], []
    for seg in SEGMENTS:
        sec, con = build_segment(seg, days, fest_case, start, end, events)
        sections.append(sec)
        consoles.append(con)

    html = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>P2 累计付费监控（近2个月）</title><style>
body{{background:#0f1420;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;margin:0;padding:24px}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#8892a4;font-size:12px;margin-bottom:14px}}
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
.seg{{display:block}}
</style></head><body>
<h1>P2 <span style="color:#00d4aa">累计付费监控</span>（近 2 个月滚动 · 全折线）</h1>
<div class="sub">窗口 {start} ~ {end}（北京日切·今日为进行中不完整日）· 生成于 {today.strftime('%Y-%m-%d %H:%M')} · 竖线=节日上线时间点</div>
{"".join(sections)}
<div class="footer">口径：v1041.dl_user_order(成交单) pay_price(USD)；节日=dim_iap.iap_type『混合-节日活动』，
归属按日期窗切（拓荒节5/12-6/09→深海节6/10-7/01→世界杯竞猜7/02+，窗口由日流水曲线实测）；
ARPU分母=当日总付费人数。谓词/窗口见 p2_cumulative_monitor.py 头注释。</div>
</body></html>"""

    latest = os.path.join(OUTPUT_DIR, "P2累计付费日报_latest.html")
    with open(latest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成: {latest}")
    for c in consoles:
        print(c)


if __name__ == "__main__":
    main()
