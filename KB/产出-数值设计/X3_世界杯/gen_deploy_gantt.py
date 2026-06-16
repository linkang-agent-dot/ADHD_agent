# -*- coding: utf-8 -*-
"""世界杯竞猜礼包投放甘特图生成器（对齐真实2026世界杯淘汰赛赛程）。

真实赛程来源(2026-06-16核实)：FIFA / Wikipedia 2026 World Cup knockout stage。
投放模型：一场比赛=一个竞猜活动实例；价格档=外显类型(用户定)。
改密度/起始轮次 → 改 RULE 再重跑覆盖 HTML。
输出：世界杯_竞猜礼包投放甘特图.html
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── 真实赛程：(日期, 星期, 轮次key, 当日场次) ──────────────────────
SCHEDULE = [
    ("06/28", "日", "R32", 1), ("06/29", "一", "R32", 3), ("06/30", "二", "R32", 3),
    ("07/01", "三", "R32", 3), ("07/02", "四", "R32", 3), ("07/03", "五", "R32", 3),
    ("07/04", "六", "R16", 2), ("07/05", "日", "R16", 2), ("07/06", "一", "R16", 2), ("07/07", "二", "R16", 2),
    ("07/08", "三", "REST", 0),
    ("07/09", "四", "QF", 1), ("07/10", "五", "QF", 1), ("07/11", "六", "QF", 2),
    ("07/12", "日", "REST", 0), ("07/13", "一", "REST", 0),
    ("07/14", "二", "SF", 1), ("07/15", "三", "SF", 1),
    ("07/16", "四", "REST", 0), ("07/17", "五", "REST", 0),
    ("07/18", "六", "3RD", 1), ("07/19", "日", "FINAL", 1),
]
ROUND_NAME = {"R32": "32强", "R16": "16强", "QF": "8强", "SF": "半决赛",
              "3RD": "季军赛", "FINAL": "决赛", "REST": "休息"}
ROUND_COLOR = {"R32": "#3b6ea5", "R16": "#2e8b6f", "QF": "#c79a3a",
               "SF": "#b5622f", "3RD": "#8a5a8a", "FINAL": "#b3322f", "REST": "#5a5750"}

# ── 投放规则（per-round 主题；空=不投）改这里再重跑 ───────────────
# tier: (key, 显示名, per_match是否每场, 颜色, {轮次:主题标签})
RULE = [
    ("p499",  "$4.99 纯竞猜",  True,  "#5b8fd0",
        {"R32": "竞猜", "R16": "竞猜", "QF": "竞猜", "SF": "竞猜", "3RD": "竞猜", "FINAL": "竞猜"}),
    ("p999",  "$9.99 头像框",  True,  "#3fae8a",
        {"R16": "球队款直发", "QF": "自选框宝箱", "SF": "四强专属(国旗裹框)", "3RD": "自选框宝箱", "FINAL": "自选框宝箱"}),
    ("p1999", "$19.99 聊天表情", True, "#d4a93f",
        {"QF": "球队款直发", "SF": "自选表情宝箱", "3RD": "自选表情宝箱", "FINAL": "自选表情宝箱"}),
    ("free",  "免费预测",      False, "#8a857a",
        {"R32": "免费", "R16": "免费", "QF": "免费", "SF": "免费", "3RD": "免费", "FINAL": "免费"}),
]
PAID = ["p499", "p999", "p1999"]
PRICE = {"p499": 4.99, "p999": 9.99, "p1999": 19.99}

def counts(rnd, m):
    out = {}
    for key, _name, per_match, _c, themes in RULE:
        if rnd in themes and m:
            out[key] = (m if per_match else 1, themes[rnd])
        else:
            out[key] = (0, "")
    return out

rows, totals, total_matches = [], {k: 0 for k, *_ in RULE}, 0
for date, wk, rnd, m in SCHEDULE:
    c = counts(rnd, m)
    for k in totals: totals[k] += c[k][0]
    total_matches += m
    rows.append((date, wk, rnd, m, c))

CMAP = {k: c for k, _n, _p, c, _t in RULE}
NMAP = {k: n for k, n, _p, _c, _t in RULE}

def pk(cell, color):
    n, theme = cell
    if not n:
        return '<span class="z">·</span>'
    th = f'<div class="th">{theme}</div>' if theme and theme not in ("竞猜", "免费") else ''
    return f'<span class="pk" style="background:{color}">×{n}</span>{th}'

H = ['''<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>X3 世界杯 · 竞猜礼包投放甘特图</title><style>
:root{--bg:#1a1d24;--ink:#e8e6df;--mut:#9a9486;--line:#363b47}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;padding:26px 22px}
h1{font-size:20px;margin:0 0 6px}.sub{color:var(--mut);font-size:12.5px;margin-bottom:14px;line-height:1.7}
.sub b{color:#d9b65a}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:10px 0 14px;font-size:12.5px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:12px;height:12px;border-radius:3px;display:inline-block}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{border:1px solid var(--line);padding:7px 6px;text-align:center}
th{background:#2b303c;color:#cfc9ba;font-weight:600}
td.date{font-weight:600;white-space:nowrap}
.bar{height:22px;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:700}
.rest{opacity:.5}
.pk{display:inline-block;min-width:24px;padding:2px 7px;border-radius:11px;color:#fff;font-weight:700}
.th{font-size:10.5px;color:#bdb6a6;margin-top:3px;line-height:1.2}
.pit{color:#e8b94a;font-weight:700;white-space:nowrap}
.z{color:#555}
.tot td{background:#2b303c;font-weight:700;border-top:2px solid #4a5160}
.knob{background:#202531;border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:6px 0 16px;font-size:12.5px;line-height:1.9}
.knob b{color:#d9b65a}
.note{margin-top:14px;color:var(--mut);font-size:12px;line-height:1.85}
.note b{color:#d9b65a}
</style></head><body>''']

H.append('<h1>⚽ X3 世界杯 · 竞猜礼包投放甘特图 <span style="color:#9a9486;font-size:13px;font-weight:400">（对齐 2026 真实淘汰赛赛程）</span></h1>')
H.append(f'<div class="sub">活动窗口 <b>32强 6/28 → 决赛 7/19</b>（22天，淘汰赛共 <b>{total_matches} 场</b>）· '
         '映射 <b>$4.99 纯竞猜 / $9.99 头像框 / $19.99 表情</b> · 一场比赛 = 一个竞猜活动实例 · '
         '赛程核实 2026-06-16 FIFA/Wikipedia</div>')

H.append('<div class="knob"><b>📐 投放方案（2026-06-16 定稿）</b><br>'
         '• <b>$4.99 纯竞猜</b>：32强起 · 每场都上（飞轮基底/低门槛引流）<br>'
         '• <b>$9.99 头像框</b>：32强不投 → 16强<b>球队款直发</b> → 8强<b>自选框宝箱</b> → <b>半决赛=四强专属头像框(单国旗裹框,新)</b> → 季军/决赛<b>自选框宝箱</b><br>'
         '• <b>$19.99 聊天表情</b>：8强<b>球队款直发</b> → 半决赛/季军/决赛<b>自选表情宝箱</b>(收集现成48表情,零重复)<br>'
         '• <b>免费预测</b>：每个比赛日 1 场（产券补免费盘）<br>'
         '<span style="color:#d9b65a">★新增美术仅 2 个宝箱图标：自选头像框宝箱 / 自选表情宝箱（框池&表情池都用现成48套）</span></div>')

H.append('<div class="legend">' + ''.join(
    f'<span><i class="dot" style="background:{CMAP[k]}"></i>{NMAP[k]}</span>' for k, *_ in RULE) + '</div>')

H.append('<table><thead><tr><th>日期</th><th>周</th><th>轮次</th><th>场次</th>'
         + ''.join(f'<th>{NMAP[k]}</th>' for k, *_ in RULE)
         + '<th>当日<br>付费实例</th><th>当日<br>付费总坑$</th></tr></thead><tbody>')
day_pits = []
for date, wk, rnd, m, c in rows:
    rest = ' class="rest"' if rnd == "REST" else ''
    paid_day = c["p499"][0] + c["p999"][0] + c["p1999"][0]
    pit = sum(c[k][0] * PRICE[k] for k in PAID)
    day_pits.append(pit)
    bar = f'<div class="bar" style="background:{ROUND_COLOR[rnd]}">{ROUND_NAME[rnd]}</div>'
    cells = ''.join(f'<td>{pk(c[k], CMAP[k])}</td>' for k, *_ in RULE)
    H.append(f'<tr{rest}><td class="date">{date}</td><td>{wk}</td><td style="min-width:74px">{bar}</td>'
             f'<td>{m if m else "—"}</td>{cells}'
             f'<td style="font-weight:700">{paid_day if paid_day else "—"}</td>'
             f'<td class="pit">{("$%.2f" % pit) if pit else "—"}</td></tr>')
total_pit = sum(totals[k] * PRICE[k] for k in PAID)
H.append('<tr class="tot"><td colspan="4">合计（实例数 / 全程总坑）</td>'
         + ''.join(f'<td>{totals[k]}</td>' for k, *_ in RULE)
         + f'<td>{sum(totals[k] for k in PAID)}</td>'
         + f'<td class="pit">${total_pit:.2f}</td></tr>')
H.append('</tbody></table>')

H.append(f'<div class="note">'
         f'★ <b>每日付费总坑</b> = 当天「所有场次 × 当天开放的所有价格档」全买齐的最高花费（单人当日付费天花板）；'
         f'全程总坑 = <b>${total_pit:.2f}</b>（$4.99×{totals["p499"]} ＋ $9.99×{totals["p999"]} ＋ $19.99×{totals["p1999"]}）。'
         f'实际人均远低于此（一场只押一边、按需买档）。<br>'
         f'★ <b>付费实例总计 {sum(totals[k] for k in PAID)} 个</b>'
         f'（$4.99×{totals["p499"]} ＋ $9.99×{totals["p999"]} ＋ $19.99×{totals["p1999"]}）；免费场 {totals["free"]} 个。<br>'
         '★ 每个付费实例 = 1 条 ActvOnline ＋ 1 条 ActvPack ＋ 2 条 Pack（两队各一包，押一边=买一边）。<br>'
         '★ 休息日（7/8、7/12-13、7/16-17）不新开实例；已开实例继续可买/结算。<br>'
         '★ 高价档（$9.99/$19.99）可换夜场金辉背景区分焦点；决赛日可叠加专属高价实例冲高潮。<br>'
         '★ <b>四强专属头像框（单国旗裹框）= 8强阶段预产</b>：QF 决出 8 强后，为这 8 支队预产 flag-banner 款头像框（库 `参考头像框/` 56 张概念图打底，清洗成透明），半决赛跑出哪 4 支都有现成。<br>'
         '★ 新美术清单：自选头像框宝箱图标 + 自选表情宝箱图标（各1，现成48框/48表情当池）＋ 四强国旗框（QF预产8支）。'
         '</div></body></html>')

OUT = r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\世界杯_竞猜礼包投放甘特图.html"
open(OUT, "w", encoding="utf-8").write('\n'.join(H))
print("生成:", OUT)
print(f"付费实例合计={sum(totals[k] for k in PAID)} | $4.99={totals['p499']} $9.99={totals['p999']} $19.99={totals['p1999']} 免费={totals['free']} 淘汰赛场次={total_matches}")
