#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X2 节日收入日监控 — 全天页签 HTML 日报"""

import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-to-sql", "scripts"))
from _datain_api import execute_sql

# ============ 配置 ============
DATASOURCE = "TRINO_HF"
FESTIVAL_NAME = "占星节"
FESTIVAL_D0 = "2026-05-11"
BASELINE_START = "2026-04-27"
BASELINE_END = "2026-05-10"
SERVER_FILTER = "AND o.server_id >= '1001202' AND o.server_id <= '1007502'"
SERVER_LABEL = "12-75服"
OUTPUT_DIR = os.path.expanduser("~")

MODULE_RULES = [
    ("GACHA", ["GACHA礼包", "随机GACHA"]),
    ("大富翁", ["大富翁", "骰子", "存钱罐"]),
    ("BP通行证", ["通行证", "bp集结", "节日活动BP"]),
    ("七日活动", ["七日活动", "连锁触发"]),
    ("行军表情", ["行军表情"]),
    ("自选周卡", ["自选周卡", "fes_weekly_card"]),
    ("每日礼包", ["每日礼包"]),
    ("掉落转付费", ["掉落转付费"]),
]

# 节日 iap_id 前缀（dim_iap 未及时更新时兜底）
FESTIVAL_IAP_PREFIX = "201392"

MODULE_COLORS = {
    "GACHA": "#6c63ff", "大富翁": "#00d4aa", "BP通行证": "#ffd166",
    "七日活动": "#ff6b6b", "行军表情": "#a78bfa",
    "自选周卡": "#38bdf8", "每日礼包": "#f472b6", "掉落转付费": "#fb923c",
    "其他": "#8892a4",
}


def query(sql, limit=500):
    rows = execute_sql(sql.strip().rstrip(";"), DATASOURCE)
    return rows[:limit] if rows else []


def calc_day_number(date_str):
    d0 = datetime.strptime(FESTIVAL_D0, "%Y-%m-%d")
    return (datetime.strptime(date_str, "%Y-%m-%d") - d0).days


def classify_module(iap_name):
    if not iap_name:
        return "其他"
    for module, keywords in MODULE_RULES:
        for kw in keywords:
            if kw in iap_name:
                return module
    return "其他"


def fmt_money(v):
    return f"${v:,.0f}" if v >= 1000 else f"${v:.0f}"


def main():
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    day_num = calc_day_number(report_date)

    # ---- 1. 每日汇总（基线期 + 节日期） ----
    # 节日判定：iap_type 匹配 OR iap_id 前缀兜底
    fest_cond = f"(i.iap_type IN ('混合-节日活动','活动礼包') OR o.iap_id LIKE '{FESTIVAL_IAP_PREFIX}%')"
    sql_daily = f"""
    SELECT o.partition_date,
      sum(CASE WHEN {fest_cond} THEN o.pay_price ELSE 0 END) as festival_rev,
      sum(o.pay_price) - sum(CASE WHEN {fest_cond} THEN o.pay_price ELSE 0 END) as non_festival_rev,
      sum(o.pay_price) as total_rev,
      count(distinct o.user_id) as payers
    FROM v1089.dl_user_order o
    LEFT JOIN v1089.dim_iap i ON o.iap_id = i.iap_id
    WHERE o.partition_date BETWEEN '{BASELINE_START}' AND '{report_date}'
    {SERVER_FILTER}
    GROUP BY o.partition_date
    ORDER BY o.partition_date
    """
    rows_daily = query(sql_daily)
    if not rows_daily:
        print("ERROR: 未查到数据"); sys.exit(1)

    # ---- 2. 每天的模块明细（仅节日期） ----
    sql_modules = f"""
    SELECT o.partition_date, COALESCE(i.iap_id_name, o.iap_id) as iap_id_name,
      sum(o.pay_price) as revenue
    FROM v1089.dl_user_order o
    LEFT JOIN v1089.dim_iap i ON o.iap_id = i.iap_id
    WHERE o.partition_date BETWEEN '{FESTIVAL_D0}' AND '{report_date}'
      AND {fest_cond}
    {SERVER_FILTER}
    GROUP BY o.partition_date, COALESCE(i.iap_id_name, o.iap_id)
    """
    rows_modules = query(sql_modules)

    # 聚合模块数据: {date: {module: revenue}}
    mod_by_date = {}
    all_mod_names = set()
    for r in rows_modules:
        d = r["partition_date"]
        mod = classify_module(r.get("iap_id_name", ""))
        rev = float(r["revenue"])
        mod_by_date.setdefault(d, {})
        mod_by_date[d][mod] = mod_by_date[d].get(mod, 0) + rev
        all_mod_names.add(mod)

    # ---- 3. 基线 ----
    baseline_rows = [r for r in rows_daily if BASELINE_START <= r["partition_date"] <= BASELINE_END]
    n_bl = max(len(baseline_rows), 1)
    bl_total = sum(float(r["total_rev"]) for r in baseline_rows) / n_bl
    bl_nonfest = sum(float(r["non_festival_rev"]) for r in baseline_rows) / n_bl
    bl_payers = sum(int(r["payers"]) for r in baseline_rows) / n_bl

    baseline = {
        "total": round(bl_total, 2),
        "non_festival": round(bl_nonfest, 2),
        "payers": round(bl_payers, 1),
        "arpu_total": round(bl_total / max(bl_payers, 1), 2),
        "arpu_nonfest": round(bl_nonfest / max(bl_payers, 1), 2),
    }

    # ---- 4. 构建 allDays ----
    festival_rows = [r for r in rows_daily if r["partition_date"] >= FESTIVAL_D0]
    all_days = []
    for r in festival_rows:
        d = r["partition_date"]
        dn = calc_day_number(d)
        modules = {}
        for m in sorted(all_mod_names):
            modules[m] = round(mod_by_date.get(d, {}).get(m, 0))
        all_days.append({
            "date": d,
            "day_label": f"D{dn}",
            "day_num": dn,
            "total": round(float(r["total_rev"])),
            "festival": round(float(r["festival_rev"])),
            "non_festival": round(float(r["non_festival_rev"])),
            "payers": int(r["payers"]),
            "modules": modules,
        })

    if not all_days:
        print("ERROR: 无节日期数据"); sys.exit(1)

    # ---- 5. 生成 HTML ----
    all_days_json = json.dumps(all_days, ensure_ascii=False)
    baseline_json = json.dumps(baseline, ensure_ascii=False)
    module_colors_json = json.dumps(MODULE_COLORS, ensure_ascii=False)
    bl_total_int = int(baseline["total"])
    bl_total_str = fmt_money(baseline["total"])

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X2{FESTIVAL_NAME}日报 D{day_num}</title>
<style>
  :root {{
    --bg: #0f1117; --surface: #1a1d27; --surface2: #222536; --border: #2e3248;
    --accent: #6c63ff; --accent2: #00d4aa; --accent3: #ff6b6b; --accent4: #ffd166;
    --text: #e2e8f0; --text-muted: #8892a4; --green: #22c55e; --orange: #f97316; --red: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; font-size: 14px; }}
  .header {{ background: linear-gradient(135deg, #1a1d27 0%, #0f1117 100%); border-bottom: 1px solid var(--border); padding: 28px 40px 20px; }}
  .header h1 {{ font-size: 24px; font-weight: 700; }}
  .header h1 .hl {{ color: var(--accent); }}
  .meta-row {{ margin-top: 6px; display: flex; gap: 20px; font-size: 12px; color: var(--text-muted); }}
  .meta-row b {{ color: var(--text); }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 28px 40px 60px; }}
  .section {{ margin-bottom: 36px; }}
  .section-title {{ font-size: 14px; font-weight: 700; color: var(--accent); border-left: 3px solid var(--accent); padding-left: 10px; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; }}
  .day-tabs {{ display: flex; gap: 0; margin-bottom: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
  .day-tab {{ flex: 1; padding: 12px 0; text-align: center; cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text-muted); border-right: 1px solid var(--border); transition: all .15s; }}
  .day-tab:last-child {{ border-right: none; }}
  .day-tab:hover {{ background: var(--surface2); color: var(--text); }}
  .day-tab.active {{ background: var(--accent); color: #fff; }}
  .day-tab .day-date {{ font-size: 10px; font-weight: 400; opacity: .7; display: block; margin-top: 2px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }}
  .kpi-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 18px; border-top: 3px solid var(--accent); }}
  .kpi-label {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .8px; }}
  .kpi-value {{ font-size: 24px; font-weight: 800; margin: 4px 0 2px; font-variant-numeric: tabular-nums; }}
  .kpi-change {{ font-size: 12px; }}
  .up {{ color: var(--green); }} .down {{ color: var(--red); }} .muted {{ color: var(--text-muted); }}
  .row-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .table-wrap {{ border-radius: 10px; border: 1px solid var(--border); overflow: hidden; }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ background: var(--surface2); padding: 10px 14px; font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .6px; border-bottom: 1px solid var(--border); text-align: left; white-space: nowrap; }}
  tbody td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: rgba(108,99,255,.05); }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .conclusion {{ margin-top: 10px; padding: 10px 14px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; font-size: 13px; }}
  .mod-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
  .mod-name {{ width: 72px; font-size: 12px; color: var(--text-muted); text-align: right; flex-shrink: 0; }}
  .mod-bar-wrap {{ flex: 1; background: var(--surface2); border-radius: 4px; height: 24px; }}
  .mod-bar {{ height: 100%; border-radius: 4px; min-width: 2px; transition: width .25s; }}
  .mod-val {{ width: 64px; font-size: 13px; font-variant-numeric: tabular-nums; text-align: right; flex-shrink: 0; font-weight: 600; }}
  .mod-pct {{ width: 36px; font-size: 11px; color: var(--text-muted); text-align: right; flex-shrink: 0; }}
  .mod-chg {{ width: 56px; font-size: 11px; text-align: right; flex-shrink: 0; }}
  .mod-hdr {{ display: flex; gap: 10px; font-size: 10px; color: var(--text-muted); margin-bottom: 10px; padding-left: 82px; }}
  .mod-hdr span {{ text-align: right; }}
  .chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .chart-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }}
  .chart-label {{ font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }}
  canvas {{ width: 100%; display: block; }}
  .canvas-200 {{ height: 200px; }} .canvas-220 {{ height: 220px; }}
  .mod-tabs {{ display: flex; gap: 4px; margin-bottom: 14px; flex-wrap: wrap; }}
  .mod-tab {{ padding: 6px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text-muted); font-size: 12px; font-weight: 600; cursor: pointer; transition: all .15s; }}
  .mod-tab:hover {{ background: var(--surface2); color: var(--text); }}
  .mod-tab.active {{ color: #fff; border-color: transparent; }}
  .alert {{ padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; font-size: 13px; display: flex; align-items: flex-start; gap: 8px; }}
  .alert-icon {{ flex-shrink: 0; }}
  .alert-warn {{ background: rgba(249,115,22,.08); border: 1px solid rgba(249,115,22,.2); }}
  .alert-info {{ background: rgba(108,99,255,.06); border: 1px solid rgba(108,99,255,.15); }}
  .footer {{ text-align: center; color: var(--text-muted); font-size: 11px; padding: 20px 0; }}
</style>
</head>
<body>
<div class="header">
  <h1>X2 <span class="hl">{FESTIVAL_NAME}</span> 日报</h1>
  <div class="meta-row">
    <span>{SERVER_LABEL}</span>
    <span>基线 {BASELINE_START} ~ {BASELINE_END} (14日均值)</span>
    <span>生成于 {datetime.now().strftime("%H:%M")}</span>
  </div>
</div>
<div class="container">
  <div class="day-tabs" id="dayTabs"></div>
  <div class="section"><div class="kpi-grid" id="kpiGrid"></div></div>
  <div class="section row-2col">
    <div>
      <div class="section-title">ARPU 增量分析</div>
      <div class="table-wrap"><table>
        <thead><tr><th>指标</th><th class="num">当日</th><th class="num">基线</th><th class="num">净增</th></tr></thead>
        <tbody id="arpuBody"></tbody>
      </table></div>
      <div class="conclusion" id="arpuConclusion"></div>
    </div>
    <div>
      <div class="section-title">节日模块构成</div>
      <div class="mod-hdr"><span>模块</span><span style="flex:1"></span><span style="width:64px">当日</span><span style="width:36px">占比</span><span style="width:56px">环比</span></div>
      <div id="modBars"></div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">每日流水趋势</div>
    <div class="chart-row">
      <div class="chart-box"><div class="chart-label">总流水</div><canvas id="totalChart" class="canvas-200"></canvas></div>
      <div class="chart-box"><div class="chart-label">节日流水（独立坐标轴）</div><canvas id="festChart" class="canvas-200"></canvas></div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">模块变化趋势</div>
    <div class="chart-box"><div class="mod-tabs" id="modTabs"></div><canvas id="modTrendChart" class="canvas-220"></canvas></div>
  </div>
  <div class="section">
    <div class="section-title">关注点</div>
    <div id="alertsBox"></div>
  </div>
</div>
<div class="footer">X2 {FESTIVAL_NAME} | 数据口径：{SERVER_LABEL}，节日模块 = dim_iap 中 iap_type 为「混合-节日活动」+「活动礼包」</div>
<script>
const allDays = {all_days_json};
const baseline = {baseline_json};
const modColors = {module_colors_json};
const dpr = window.devicePixelRatio || 1;
let currentDayIdx = allDays.length - 1;
let currentMod = null;

function $(id) {{ return document.getElementById(id); }}
function fmtMoney(v) {{ return v >= 1000 ? '$' + v.toLocaleString('en-US', {{maximumFractionDigits:0}}) : '$' + Math.round(v); }}
function fmtPct(v) {{ if (v == null || v === 0) return '\u2014'; return (v > 0 ? '+' : '') + v.toFixed(1) + '%'; }}
function fmtDelta(v) {{ return (v >= 0 ? '+$' : '-$') + Math.abs(v).toFixed(2); }}
function pctChg(a, b) {{ return b ? (a - b) / b * 100 : null; }}

function buildDayTabs() {{
  const el = $('dayTabs'); el.innerHTML = '';
  allDays.forEach((d, i) => {{
    const div = document.createElement('div');
    div.className = 'day-tab' + (i === currentDayIdx ? ' active' : '');
    div.innerHTML = d.day_label + '<span class="day-date">' + d.date + '</span>';
    div.onclick = () => {{ currentDayIdx = i; renderAll(); }};
    el.appendChild(div);
  }});
}}

function renderKPI() {{
  const d = allDays[currentDayIdx];
  const prev = currentDayIdx > 0 ? allDays[currentDayIdx - 1] : null;
  const cum_total = allDays.slice(0, currentDayIdx + 1).reduce((s, x) => s + x.total, 0);
  const cum_fest = allDays.slice(0, currentDayIdx + 1).reduce((s, x) => s + x.festival, 0);
  const festRatio = cum_total > 0 ? (cum_fest / cum_total * 100) : 0;
  const items = [
    {{ label: '总流水', value: fmtMoney(d.total), chg: prev ? pctChg(d.total, prev.total) : null, color: 'var(--accent)' }},
    {{ label: '付费人数', value: d.payers, chg: prev ? pctChg(d.payers, prev.payers) : null, color: 'var(--accent2)' }},
    {{ label: '节日流水', value: fmtMoney(d.festival), chg: prev ? pctChg(d.festival, prev.festival) : null, color: 'var(--accent4)' }},
    {{ label: '非节日流水', value: fmtMoney(d.non_festival), chg: prev ? pctChg(d.non_festival, prev.non_festival) : null, color: 'var(--green)' }},
    {{ label: '节日累计流水', value: fmtMoney(cum_fest), chg: null, sub: 'D0~' + d.day_label, color: 'var(--accent3)' }},
    {{ label: '节日累计占比', value: festRatio.toFixed(1) + '%', chg: null, sub: fmtMoney(cum_fest) + ' / ' + fmtMoney(cum_total), color: 'var(--orange)' }},
  ];
  $('kpiGrid').innerHTML = items.map(it => {{
    const chgCls = it.chg == null ? 'muted' : it.chg > 0 ? 'up' : it.chg < 0 ? 'down' : 'muted';
    const chgStr = it.chg != null ? fmtPct(it.chg) + ' vs 昨日' : (it.sub || 'D0~' + d.day_label);
    return '<div class="kpi-card" style="border-top-color:' + it.color + '"><div class="kpi-label">' + it.label + '</div><div class="kpi-value">' + it.value + '</div><div class="kpi-change ' + chgCls + '">' + chgStr + '</div></div>';
  }}).join('');
}}

function renderARPU() {{
  const d = allDays[currentDayIdx];
  const fa = d.festival / Math.max(d.payers, 1), nfa = d.non_festival / Math.max(d.payers, 1), ta = d.total / Math.max(d.payers, 1);
  const rows = [['节日 ARPU', fa, 0, fa], ['非节日 ARPU', nfa, baseline.arpu_nonfest, nfa - baseline.arpu_nonfest], ['综合 ARPU', ta, baseline.arpu_total, ta - baseline.arpu_total]];
  $('arpuBody').innerHTML = rows.map(r => {{
    const cls = r[3] > 0.5 ? 'up' : r[3] < -0.5 ? 'down' : 'muted';
    return '<tr><td>' + r[0] + '</td><td class="num">$' + r[1].toFixed(2) + '</td><td class="num muted">$' + r[2].toFixed(2) + '</td><td class="num ' + cls + '">' + fmtDelta(r[3]) + '</td></tr>';
  }}).join('');
  const nfD = nfa - baseline.arpu_nonfest; let c, cl;
  if (nfD > 1) {{ c = '节日纯增量 +$' + fa.toFixed(2) + '/人，非节日被带动 +$' + nfD.toFixed(2) + '/人'; cl = 'up'; }}
  else if (nfD < -1) {{ c = '节日纯增量 +$' + fa.toFixed(2) + '/人，非节日被挤占 ' + fmtDelta(nfD) + '/人'; cl = 'down'; }}
  else {{ c = '节日纯增量 +$' + fa.toFixed(2) + '/人，非节日基本持平'; cl = 'muted'; }}
  $('arpuConclusion').className = 'conclusion ' + cl; $('arpuConclusion').textContent = c;
}}

function renderModBars() {{
  const d = allDays[currentDayIdx], prev = currentDayIdx > 0 ? allDays[currentDayIdx - 1] : null;
  const mods = d.modules, modNames = Object.keys(mods).sort((a, b) => mods[b] - mods[a]);
  const maxRev = Math.max(...Object.values(mods), 1), modTotal = Object.values(mods).reduce((s, v) => s + v, 0);
  $('modBars').innerHTML = modNames.map(m => {{
    const rev = mods[m], pct = modTotal > 0 ? rev / modTotal * 100 : 0, barW = rev / maxRev * 100;
    const color = modColors[m] || '#8892a4', prevRev = prev ? (prev.modules[m] || 0) : 0;
    const chg = pctChg(rev, prevRev), chgCls = chg != null ? (chg > 0 ? 'up' : 'down') : 'muted';
    return '<div class="mod-row"><div class="mod-name">' + m + '</div><div class="mod-bar-wrap"><div class="mod-bar" style="width:' + barW.toFixed(1) + '%;background:' + color + '"></div></div><div class="mod-val">' + fmtMoney(rev) + '</div><div class="mod-pct">' + pct.toFixed(0) + '%</div><div class="mod-chg"><span class="' + chgCls + '">' + (chg != null ? fmtPct(chg) : '\u2014') + '</span></div></div>';
  }}).join('');
}}

function drawTrend(canvasId, key, color, areaColor, blVal, blLabel) {{
  const canvas = $(canvasId), W0 = canvas.offsetWidth, H = 200;
  canvas.width = W0 * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
  const pad = {{ top: 20, right: 16, bottom: 32, left: 52 }};
  const cW = W0 - pad.left - pad.right, cH = H - pad.top - pad.bottom;
  const series = allDays.map(d => d[key]), n = series.length, maxVal = Math.max(...series, 1) * 1.3;
  function xp(i) {{ return pad.left + (n > 1 ? i / (n - 1) * cW : cW / 2); }}
  function yp(v) {{ return pad.top + cH - (v / maxVal * cH); }}
  ctx.strokeStyle = '#2e3248'; ctx.lineWidth = 0.5;
  for (let i = 0; i <= 4; i++) {{ const yy = pad.top + cH * i / 4; ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(W0 - pad.right, yy); ctx.stroke(); ctx.fillStyle = '#8892a4'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText('$' + Math.round(maxVal * (4 - i) / 4).toLocaleString(), pad.left - 6, yy + 3); }}
  if (blVal > 0) {{ const blY = yp(blVal); ctx.setLineDash([4,4]); ctx.strokeStyle = '#f97316'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(pad.left, blY); ctx.lineTo(W0 - pad.right, blY); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle = '#f97316'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText(blLabel, W0 - pad.right, blY - 5); }}
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.lineTo(xp(n-1), yp(0)); ctx.lineTo(xp(0), yp(0)); ctx.closePath(); ctx.fillStyle = areaColor; ctx.fill();
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
  for (let i = 0; i < n; i++) {{ const sel = (i === currentDayIdx), r = sel ? 6 : 4; ctx.beginPath(); ctx.arc(xp(i), yp(series[i]), r, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill(); ctx.strokeStyle = sel ? '#fff' : '#1a1d27'; ctx.lineWidth = sel ? 2.5 : 2; ctx.stroke(); ctx.fillStyle = sel ? '#fff' : '#e2e8f0'; ctx.font = (sel ? 'bold 12px' : '11px') + ' -apple-system,sans-serif'; ctx.textAlign = 'center'; ctx.fillText('$' + series[i].toLocaleString(), xp(i), yp(series[i]) - (sel ? 16 : 12)); ctx.fillStyle = sel ? '#fff' : '#8892a4'; ctx.font = (sel ? 'bold ' : '') + '10px -apple-system,sans-serif'; ctx.fillText(allDays[i].day_label, xp(i), H - pad.bottom + 14); }}
}}

function buildModTabs() {{
  const mods = Object.keys(allDays[0].modules);
  let best = mods[0], bestSum = 0;
  mods.forEach(m => {{ const s = allDays.reduce((a, d) => a + (d.modules[m] || 0), 0); if (s > bestSum) {{ bestSum = s; best = m; }} }});
  currentMod = currentMod || best;
  const el = $('modTabs'); el.innerHTML = '';
  mods.sort((a, b) => {{ const sa = allDays.reduce((a2, d) => a2 + (d.modules[a] || 0), 0), sb = allDays.reduce((a2, d) => a2 + (d.modules[b] || 0), 0); return sb - sa; }});
  mods.forEach(m => {{ const btn = document.createElement('div'); btn.className = 'mod-tab' + (m === currentMod ? ' active' : ''); btn.style.background = m === currentMod ? (modColors[m] || '#8892a4') : ''; btn.style.borderColor = m === currentMod ? 'transparent' : ''; btn.textContent = m; btn.onclick = () => {{ currentMod = m; buildModTabs(); drawModTrend(); }}; el.appendChild(btn); }});
}}

function drawModTrend() {{
  const mod = currentMod, series = allDays.map(d => d.modules[mod] || 0), color = modColors[mod] || '#8892a4';
  const canvas = $('modTrendChart'), W0 = canvas.offsetWidth, H = 220;
  canvas.width = W0 * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
  const pad = {{ top: 28, right: 20, bottom: 32, left: 52 }}, cW = W0 - pad.left - pad.right, cH = H - pad.top - pad.bottom;
  const n = series.length, maxVal = Math.max(...series, 1) * 1.35;
  function xp(i) {{ return pad.left + (n > 1 ? i / (n - 1) * cW : cW / 2); }}
  function yp(v) {{ return pad.top + cH - (v / maxVal * cH); }}
  ctx.strokeStyle = '#2e3248'; ctx.lineWidth = 0.5;
  for (let i = 0; i <= 4; i++) {{ const yy = pad.top + cH * i / 4; ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(W0 - pad.right, yy); ctx.stroke(); ctx.fillStyle = '#8892a4'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText('$' + Math.round(maxVal * (4 - i) / 4).toLocaleString(), pad.left - 6, yy + 3); }}
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.lineTo(xp(n-1), yp(0)); ctx.lineTo(xp(0), yp(0)); ctx.closePath();
  const grad = ctx.createLinearGradient(0, pad.top, 0, H - pad.bottom); grad.addColorStop(0, color + '30'); grad.addColorStop(1, color + '05'); ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
  for (let i = 0; i < n; i++) {{ const sel = (i === currentDayIdx), r = sel ? 6 : 4; ctx.beginPath(); ctx.arc(xp(i), yp(series[i]), r, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill(); ctx.strokeStyle = sel ? '#fff' : '#1a1d27'; ctx.lineWidth = sel ? 2.5 : 2; ctx.stroke(); ctx.fillStyle = sel ? '#fff' : '#e2e8f0'; ctx.font = (sel ? 'bold 12px' : 'bold 11px') + ' -apple-system,sans-serif'; ctx.textAlign = 'center'; ctx.fillText('$' + series[i].toLocaleString(), xp(i), yp(series[i]) - 18); if (i > 0 && series[i-1] > 0) {{ const chg = (series[i] - series[i-1]) / series[i-1] * 100; ctx.fillStyle = chg >= 0 ? '#22c55e' : '#ef4444'; ctx.font = '10px -apple-system,sans-serif'; ctx.fillText((chg >= 0 ? '+' : '') + chg.toFixed(0) + '%', xp(i), yp(series[i]) - 30); }} ctx.fillStyle = sel ? '#fff' : '#8892a4'; ctx.font = (sel ? 'bold ' : '') + '11px -apple-system,sans-serif'; ctx.fillText(allDays[i].day_label, xp(i), H - pad.bottom + 16); }}
  const cum = series.reduce((a, b) => a + b, 0); ctx.fillStyle = color; ctx.font = 'bold 13px -apple-system,sans-serif'; ctx.textAlign = 'left'; ctx.fillText(mod, pad.left, 18); ctx.fillStyle = '#8892a4'; ctx.font = '12px -apple-system,sans-serif'; ctx.fillText('累计 $' + cum.toLocaleString(), pad.left + ctx.measureText(mod + '  ').width + 8, 18);
}}

function renderAlerts() {{
  const d = allDays[currentDayIdx], prev = currentDayIdx > 0 ? allDays[currentDayIdx - 1] : null;
  const nfArpu = d.non_festival / Math.max(d.payers, 1), nfDelta = nfArpu - baseline.arpu_nonfest;
  const modTotal = Object.values(d.modules).reduce((s, v) => s + v, 0);
  const alerts = [];
  if (prev) {{ for (const [m, rev] of Object.entries(d.modules)) {{ const p = prev.modules[m] || 0; if (p > 100 && rev < p * 0.5) alerts.push(['warn', m + '从' + prev.day_label + '的' + fmtMoney(p) + '降至' + d.day_label + '的' + fmtMoney(rev) + '，降幅' + Math.abs(pctChg(rev, p)).toFixed(0) + '%']); if (p < 50 && rev > 500) alerts.push(['info', m + '今日新开即贡献' + fmtMoney(rev) + '，占节日收入' + (rev / modTotal * 100).toFixed(0) + '%']); }} }}
  if (nfDelta < -2) alerts.push(['warn', '非节日ARPU下降' + fmtDelta(nfDelta) + '/人，存在挤占风险']);
  else if (nfDelta > 2) alerts.push(['info', '非节日ARPU上升' + fmtDelta(nfDelta) + '/人，节日带动日常消费']);
  else alerts.push(['info', '非节日消费持平，节日为纯增量模型']);
  $('alertsBox').innerHTML = alerts.map(([t, msg]) => '<div class="alert ' + (t === 'warn' ? 'alert-warn' : 'alert-info') + '"><span class="alert-icon">' + (t === 'warn' ? '&#9888;&#65039;' : '&#128204;') + '</span>' + msg + '</div>').join('');
}}

function renderAll() {{
  buildDayTabs(); renderKPI(); renderARPU(); renderModBars();
  drawTrend('totalChart', 'total', '#6c63ff', 'rgba(108,99,255,.1)', {bl_total_int}, '基线 {bl_total_str}');
  drawTrend('festChart', 'festival', '#ffd166', 'rgba(255,209,102,.1)', 0, '');
  buildModTabs(); drawModTrend(); renderAlerts();
}}
renderAll();
</script>
</body>
</html>"""

    filename = f"X2{FESTIVAL_NAME}日报_D{day_num}_{report_date}.html"
    output_path = os.path.join(OUTPUT_DIR, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    last_day = all_days[-1]
    print(f"HTML 日报已生成: {output_path}")
    print(f"D{day_num} | {report_date} | 总流水 {fmt_money(last_day['total'])} | 节日 {fmt_money(last_day['festival'])} | 付费 {last_day['payers']}人")


if __name__ == "__main__":
    main()
