# -*- coding: utf-8 -*-
"""9-10 月模块规划页：以「模块当周收入 / 当周大盘」为唯一 KPI。

数据源（先跑出这两个 json）：
  scratchpad/p2_weekly.json      P2 逐周 挖孔/弹珠/节日总/大盘/付费人数
  scratchpad/x3_weekly_share.json X3 逐周 各模块/大盘/付费人数（成熟服 1000-1880）
产出：KB\\产出-数值设计\\X3_8-10月节日需求\\9-10月模块规划_周占比.html
"""
import json, os

SCR = r"C:/Users/linkang/AppData/Local/Temp/claude/C--Users-linkang/549921cb-db7d-4567-bdb3-e36bd4b4e0c7/scratchpad"
OUT = r"C:\ADHD_agent\KB\产出-数值设计\X3_8-10月节日需求\9-10月模块规划_周占比.html"

p2 = json.load(open(f"{SCR}/p2_weekly.json", encoding="utf-8"))
x3 = json.load(open(f"{SCR}/x3_weekly_share.json", encoding="utf-8"))

# ---- P2：只保留有投放的周 ----
p2r = []
for x in p2:
    tot, f = float(x["total"]), float(x["fest"])
    m, p_ = float(x["mining"]), float(x["pin"])
    if m + p_ < 3000:
        continue
    p2r.append({"wk": x["wk"], "tot": tot, "fest": f, "m": m, "p": p_,
                "sm": m / tot * 100, "sp": p_ / tot * 100, "sf": f / tot * 100})

ms = sorted(r["sm"] for r in p2r if r["m"] > 3000)
ps = sorted(r["sp"] for r in p2r if r["p"] > 3000)
m_med, m_max = ms[len(ms) // 2], max(ms)
p_med, p_max = ps[len(ps) // 2], max(ps)
fest_share = sorted(r["sf"] for r in p2r)

X3_MODS = ["开箱族(世界杯)", "开箱族(夏日)", "大富翁族(深海)", "转盘(深海)", "双通行证(深海)", "许愿池"]
COL = {"开箱族(世界杯)": "#5ad1ff", "开箱族(夏日)": "#38bdf8", "大富翁族(深海)": "#4ade80",
       "转盘(深海)": "#f87171", "双通行证(深海)": "#c084fc", "许愿池": "#fbbf24"}
x3_best_single = max((v / r["total"] * 100, n, r["week"]) for r in x3 for n, v in r["mods"].items() if r["total"])
x3_best_sum = max((r["fest_sum"] / r["total"] * 100, r["week"]) for r in x3 if r["total"])
x3_gap = [(r["week"], r["fest_sum"] / r["total"] * 100) for r in x3 if r["total"] and r["fest_sum"] / r["total"] < .02]


def bars(rows, key, color, maxv, w=980, h=170, lbl=""):
    """单序列柱状图"""
    n = len(rows)
    bw = (w - 70) / n
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%">']
    for gy in (0, 10, 20, 30, 40):
        if gy > maxv: break
        y = h - 26 - gy / maxv * (h - 46)
        out.append(f'<line x1="56" y1="{y:.0f}" x2="{w-8}" y2="{y:.0f}" stroke="#243040"/>'
                   f'<text x="50" y="{y+4:.0f}" font-size="10" fill="#6b7f95" text-anchor="end">{gy}%</text>')
    for i, r in enumerate(rows):
        v = r[key]
        bh = max(1, v / maxv * (h - 46))
        x = 60 + i * bw
        out.append(f'<rect x="{x:.1f}" y="{h-26-bh:.1f}" width="{bw*.72:.1f}" height="{bh:.1f}" '
                   f'fill="{color}" rx="2"><title>{r["wk"]} · {v:.1f}%</title></rect>')
        if v >= maxv * .55:
            out.append(f'<text x="{x+bw*.36:.1f}" y="{h-30-bh:.1f}" font-size="9.5" fill="{color}" '
                       f'text-anchor="middle">{v:.0f}%</text>')
        if i % 3 == 0:
            out.append(f'<text x="{x+bw*.36:.1f}" y="{h-10}" font-size="9" fill="#6b7f95" '
                       f'text-anchor="middle">{r["wk"][5:]}</text>')
    out.append("</svg>")
    return "".join(out)


def stack(rows, w=980, h=210):
    n = len(rows)
    bw = (w - 70) / n
    maxv = 26
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%">']
    for gy in (0, 10, 20):
        y = h - 26 - gy / maxv * (h - 46)
        out.append(f'<line x1="56" y1="{y:.0f}" x2="{w-8}" y2="{y:.0f}" stroke="#243040"/>'
                   f'<text x="50" y="{y+4:.0f}" font-size="10" fill="#6b7f95" text-anchor="end">{gy}%</text>')
    for i, r in enumerate(rows):
        if not r["total"]:
            continue
        x = 60 + i * bw
        acc = 0.0
        for nme in X3_MODS:
            v = r["mods"].get(nme, 0) / r["total"] * 100
            if v <= 0:
                continue
            bh = v / maxv * (h - 46)
            out.append(f'<rect x="{x:.1f}" y="{h-26-(acc+v)/maxv*(h-46):.1f}" width="{bw*.72:.1f}" '
                       f'height="{bh:.1f}" fill="{COL[nme]}" rx="1.5">'
                       f'<title>{r["week"]} · {nme} {v:.1f}%</title></rect>')
            acc += v
        tag = f'{acc:.1f}%'
        out.append(f'<text x="{x+bw*.36:.1f}" y="{h-30-acc/maxv*(h-46):.1f}" font-size="9.5" '
                   f'fill="{"#f87171" if acc<2 else "#8fa3b8"}" text-anchor="middle">{tag}</text>')
        out.append(f'<text x="{x+bw*.36:.1f}" y="{h-10}" font-size="9" fill="#6b7f95" '
                   f'text-anchor="middle">{r["week"][5:]}</text>')
    out.append("</svg>")
    return "".join(out)


rev = json.load(open(f"{SCR}/revival.json", encoding="utf-8"))

# ---- 当周节日 ARPPU + 渗透（10 月 KPI）----
ar = json.load(open(f"{SCR}/arppu.json", encoding="utf-8"))


def arppu_rows(rows, key_f="fest", min_b=50):
    o = []
    for x in rows:
        f, b, py = float(x[key_f]), x["fb"] or 0, x["payers"]
        if b < min_b:
            continue
        o.append({"wk": x["wk"], "fest": f, "b": b, "arppu": f / b, "pen": b / py * 100})
    return o


p2a = arppu_rows(ar["p2"], min_b=50)
x3a = arppu_rows(ar["x3"], min_b=20)
p2_arppu = sorted(r["arppu"] for r in p2a)
x3_arppu = sorted(r["arppu"] for r in x3a)
p2_am, p2_amax = p2_arppu[len(p2_arppu) // 2], max(p2_arppu)
x3_am, x3_amax = x3_arppu[len(x3_arppu) // 2], max(x3_arppu)
p2_pen = sorted(r["pen"] for r in p2a)
x3_pen = sorted(r["pen"] for r in x3a)
p2_pm, x3_pm = p2_pen[len(p2_pen) // 2], x3_pen[len(x3_pen) // 2]

# ---- 日粒度三因子拆解（P2 4-6月 vs X3）----
TS = json.load(open(f"{SCR}/target_split.json", encoding="utf-8"))
DP, DX = TS["p2"], TS["x3"]


def cum(d):
    return (1 - d["gap_ratio"] / 100) * d["payrate"] * d["arppu"] / d["arpu"]


def paths(target):
    need = target / DX["share"]
    k = need ** .5
    return {
        "need": need,
        "A": (DX["payrate"] * need, DX["payrate"] * need <= DP["payrate"] * 1.05),
        "B": (DX["arppu"] * need, DX["arppu"] * need <= DP["arppu"] * 1.05),
        "C": (DX["payrate"] * k, DX["arppu"] * k,
              DX["payrate"] * k / DP["payrate"] * 100, DX["arppu"] * k / DP["arppu"] * 100),
    }


P40, P50 = paths(40), paths(50)

# ---- 时间轴：X3/P2 日粒度三指标（付费率 / 节日ARPU / 节日ARPPU）----
def series(fn):
    o = []
    for x in json.load(open(f"{SCR}/{fn}", encoding="utf-8")):
        fe, b, t, p = float(x["fest"]), x["fb"] or 0, float(x["total"]), x["payers"]
        if not p:
            continue
        o.append({"d": x["d"], "payrate": round(b / p * 100, 2),
                  "arpu": round(fe / p, 2), "arppu": round(fe / b, 2) if b else 0,
                  "fest": fe, "share": round(fe / t * 100, 2)})
    return o


SX, SP = series("x3_daily.json"), series("p2_daily.json")


# ---- 自动切节日活跃段（付费率≥10% 的连续日，容 1 天间断），再按 D0 对齐 ----
def segments(rows, thr=10, gap_tol=1, min_len=4):
    out, cur, miss = [], [], 0
    for r in rows:
        if r["payrate"] >= thr:
            cur.append(r); miss = 0
        elif cur:
            miss += 1
            if miss > gap_tol:
                out.append(cur); cur, miss = [], 0
            else:
                cur.append(r)
    if cur:
        out.append(cur)
    return [s for s in out if len(s) >= min_len]


# 段命名（按 top 礼包实查确认：段3=拓荒节、段4=深海节、段2=4月节日期）
SEG_NAME_P2 = {"2026-05-12": ("P2 拓荒节", "#c084fc", 2.6, ""),
               "2026-06-10": ("P2 深海节", "#a78bfa", 1.9, "6 4"),
               "2026-04-09": ("P2 4月节日期", "#8b7fd0", 1.4, "3 3")}
SEG_NAME_X3 = {"2026-06-26": ("X3 世界杯+深海（双节）", "#5ad1ff", 2.6, ""),
               "2026-05-29": ("X3 夏日恋语", "#38bdf8", 1.9, "6 4")}

SEGS = []
for rows, mapping, side in ((SP, SEG_NAME_P2, "P2"), (SX, SEG_NAME_X3, "X3")):
    for s in segments(rows):
        key = s[0]["d"]
        if key not in mapping:
            continue
        nm, color, wdt, dash = mapping[key]
        pr = sorted(x["payrate"] for x in s)
        ap = sorted(x["arppu"] for x in s)
        SEGS.append({"name": nm, "side": side, "color": color, "w": wdt, "dash": dash,
                     "start": s[0]["d"], "end": s[-1]["d"], "n": len(s),
                     "rev": round(sum(x["fest"] for x in s)),
                     "pr_med": round(pr[len(pr) // 2], 1), "ap_med": round(ap[len(ap) // 2], 1),
                     "pts": [{"i": i, "d": r["d"], "payrate": r["payrate"],
                              "arpu": r["arpu"], "arppu": r["arppu"],
                              "fest": r["fest"], "share": r["share"]} for i, r in enumerate(s)]})
SEGS.sort(key=lambda z: (z["side"], -z["rev"]))
# X3 已上节日的时间锚（成熟服口径收入来自累计监控 07-29）
X3_EVENTS = [
    ("2026-05-29", "夏日恋语 D0"), ("2026-06-09", "夏日批二"), ("2026-06-19", "夏日批三"),
    ("2026-06-26", "世界杯 D0"), ("2026-07-03", "深海节 D0"), ("2026-07-20", "双节下线"),
]
X3_FESTS = [
    ("夏日恋语", "05-29 ~ 06-08（批一，后续批二/批三滚动）", 20338, 4.5, "开箱族 + 通行证 + 拜访皮肤 + 装饰"),
    ("世界杯", "06-26 ~ 07-20", 18284, 4.1, "开箱族（福箱连锁+券锚点）+ 通行证 + 竞猜"),
    ("深海节", "07-03 ~ 07-19", 26945, 6.0, "大富翁族 + 双通行证 + 转盘 + 每日/周卡/拜访/装饰"),
    ("尼罗（滚动）", "滚动投放", 1525, 0.3, "2106xx 专属包"),
]


def scatter_pen_arppu(w=980, h=340):
    """渗透 × ARPPU 散点：P2 灰点做背景云，X3 亮点在前"""
    PADL, PADB = 62, 40
    xmax, ymax = 70, 145
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%">']
    for gx in range(0, xmax + 1, 10):
        X = PADL + gx / xmax * (w - PADL - 24)
        out.append(f'<line x1="{X:.0f}" y1="14" x2="{X:.0f}" y2="{h-PADB}" stroke="#243040"/>'
                   f'<text x="{X:.0f}" y="{h-PADB+16}" font-size="10" fill="#6b7f95" text-anchor="middle">{gx}%</text>')
    for gy in range(0, ymax + 1, 25):
        Y = h - PADB - gy / ymax * (h - PADB - 20)
        out.append(f'<line x1="{PADL}" y1="{Y:.0f}" x2="{w-24}" y2="{Y:.0f}" stroke="#243040"/>'
                   f'<text x="{PADL-8}" y="{Y+4:.0f}" font-size="10" fill="#6b7f95" text-anchor="end">${gy}</text>')

    def XY(pen, a):
        return (PADL + min(pen, xmax) / xmax * (w - PADL - 24),
                h - PADB - min(a, ymax) / ymax * (h - PADB - 20))
    for r in p2a:
        x, y = XY(r["pen"], r["arppu"])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#c084fc" fill-opacity=".38">'
                   f'<title>P2 {r["wk"]}｜渗透 {r["pen"]:.1f}% · ARPPU ${r["arppu"]:.1f}</title></circle>')
    for r in x3a:
        x, y = XY(r["pen"], r["arppu"])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#5ad1ff" stroke="#0d1117" stroke-width="1.2">'
                   f'<title>X3 {r["wk"]}｜渗透 {r["pen"]:.1f}% · ARPPU ${r["arppu"]:.1f}</title></circle>')
    # 目标区
    tx, ty = XY(50, 60)
    tx2, ty2 = XY(65, 100)
    out.append(f'<rect x="{tx:.0f}" y="{ty2:.0f}" width="{tx2-tx:.0f}" height="{ty-ty2:.0f}" '
               f'fill="#4ade80" fill-opacity=".07" stroke="#4ade80" stroke-dasharray="4 3"/>'
               f'<text x="{(tx+tx2)/2:.0f}" y="{ty2-6:.0f}" font-size="11" fill="#4ade80" text-anchor="middle">P2 主力周所在区</text>')
    out.append(f'<text x="{w//2}" y="{h-6}" font-size="11" fill="#8fa3b8" text-anchor="middle">'
               f'节日渗透（节日付费人数 / 当周总付费人数）→</text>')
    out.append(f'<text x="14" y="{h//2}" font-size="11" fill="#8fa3b8" transform="rotate(-90 14 {h//2})" '
               f'text-anchor="middle">当周节日 ARPPU →</text>')
    out.append("</svg>")
    return "".join(out)

SEP9 = [
    ("W1", "D0 – D6", "内外圈抽奖", "主城皮肤 · 二周年限定（普通 + 高级）", "#5ad1ff",
     "P2 圣诞 GACHA 原型：1,447 买家 / 人均 $153.6 / max $8,219 / 溢出率 25.4%", "15–19%"),
    ("W2", "D7 – D13", "挖孔", "英雄皮肤 · 史诗 + 英雄皮肤 · 周年限定", "#4ade80",
     f"P2 最强单品：16 个投放周中位 {m_med:.1f}%、峰值 {m_max:.1f}%（渗透 44%）", f"{m_med:.0f}–25%"),
    ("W3", "D14 – D20", "弹珠 ＋ 开箱（堆叠）",
     "弹珠→海妖皮肤 · 周年限定 + 行军皮肤 / 行军拖尾 · 周年限定　｜　开箱→<b>一批皮肤返场</b>", "#c084fc",
     f"弹珠 P2 中位 {p_med:.1f}%／峰值 {p_max:.1f}%（带榜 $222k vs 无榜 $167k）＋ 开箱 X3 自身最好 15.2%",
     f"{p_med:.0f}+10 ≈ <b>20–27%</b>"),
]

# 21 天填充清单：层 × 三周（"这 21 天里每一天都有东西可玩可买"）
FILL = [
    ("★ 弹药带<br><span class='sm'>当周主力·spotlight</span>", "#5ad1ff",
     "内外圈抽奖<br><span class='sm'>主城皮肤二周年限定（普通+高级）</span>",
     "挖孔 v1<br><span class='sm'>英雄皮肤史诗 + 周年限定</span>",
     "弹珠 ＋ 开箱（堆叠）<br><span class='sm'>海妖/行军外显 + 皮肤返场</span>"),
    ("贯穿压舱<br><span class='sm'>全 21 天不换</span>", "#4ade80",
     "大富翁 + 纪念卡（基础卡免费线 / 高级卡付费线）　—— 全程 D0→D20", "", ""),
    ("通行证线<br><span class='sm'>拉到 D20 末</span>", "#c084fc",
     "主 BP 开启（积分源＝三周通用任务）", "各周核心挂子 BP（内外圈/挖孔/弹珠各一条）", "BP 冲刺 + 满级奖励结算"),
    ("外显投放<br><span class='sm'>每周一套 · <span style='color:#f87171'>红＝本次新做</span></span>", "#fbbf24",
     "<b>普通主城皮肤</b>·二周年（外圈随机走量）<br><span style='color:#f87171'><b>高级主城皮肤</b>·二周年（内圈固定收鲸）＝新增品质档</span>"
     "<br><span class='sm'>现有 20 款品质全封顶在 3（紫），高级档要新开品质位</span>",
     "英雄皮肤 · 史诗（$49.99 钩子档）＋ 周年限定<br><span class='sm'>已有档位，只出新款</span>",
     "<span style='color:#f87171'><b>海妖皮肤</b>＝新系统</span> + 行军皮肤 + 行军拖尾 + <b>返场皮</b>"),
    ("付费货架<br><span class='sm'>常驻</span>", "#8fa3b8",
     "累充（分两期：W1 内外圈期）· 每日礼包 · 节日周卡", "累充（W2 开箱期）· 每日礼包 · 装饰阶梯礼包 · 兑换商店①", "兑换商店② · 拜访礼包 · 进度礼包 · 门票/券阶梯"),
    ("免费向 · 留存<br><span class='sm'>拉付费率的底座</span>", "#2dd4bf",
     "签到（7天）· BINGO 拼图开启 · 许愿池", "签到续 · 拼图推进 · 酒馆积分赛开启", "拼图收官（发纪念卡）· 酒馆结算 · 双榜结算发奖"),
]

NOV_PACKS = [
    ("2023 感恩节黑五小额", 5822, 10.5, "宽入口", "#2dd4bf"),
    ("25 感恩节每日补给升级礼包", 3868, 12.7, "宽入口", "#2dd4bf"),
    ("黑五省省卡礼包", 1815, 22.1, "中额", "#5ad1ff"),
    ("2023 感恩节 GACHA", 1685, 77.1, "中额抽奖", "#5ad1ff"),
    ("2024 感恩节随机 GACHA", 1277, 119.1, "抽奖收鲸", "#c084fc"),
    ("感恩节终极连锁礼包", 947, 174.3, "收鲸", "#f87171"),
    ("黑五英雄专属礼包", 888, 44.5, "定向", "#5ad1ff"),
    ("2023 感恩节黑五大额", 596, 99.3, "收鲸", "#f87171"),
    ("黑五折扣 2024", 439, 123.6, "收鲸", "#f87171"),
]

DEC_LAYERS = [
    ("内外墙<b>回到原生场景</b>", "#c084fc",
     "P2 2024 圣诞 GACHA <b>就是内外墙的老家</b>（1,447 买家 / 人均 $153.6 / max $8,219 / 总盘 $22.2 万 / 溢出率 25.4%）。"
     "8 月首投若只做了本体，12 月<b>把三层结构补齐</b>：2 天试用钩子（P2 拉到 17,222 人）→ 本体永久皮（中位 $517，132 人贡献总盘 64.9%）→ "
     "跨服榜 30 份高级皮 + Top3 染色（上榜线 $1,444 / 中位 $2,529）",
     "同一套资产二次收割，钩子层拉付费率、榜层拉 ARPPU"),
    ("<b>套装 2 期</b>", "#5ad1ff",
     "10 月已把套装<b>系统</b>做出来，12 月只出<b>内容</b>——零系统开发、纯美术＋配置。"
     "这是半年里性价比最高的一次投放（系统成本已在 10 月摊掉）",
     "复用系统 ⇒ 开发成本极低，直接贡献流水"),
    ("<b>冲流水</b>（年度收官）", "#fbbf24",
     "P2 12 月是全年高点之一：周节日收入 <b>$369,579（占大盘 55.5%）</b>、次周 $338,081（52.0%）。"
     "年底玩家付费意愿本身最高，<b>叠加圣诞＋套装 2 期＋前三个月已建成的全部弹药</b>",
     "四件弹药（内外墙/挖孔/弹珠/开箱）此时全部就绪，可同月轮转"),
]

NOV_FIX = [
    ("9 月 · 节日期长度", "21 天（D0–D20）不断档",
     "黑五本身是价格驱动、内容压力小，<b>正好用来再跑一次 21 天满程</b>——验证「排满」这件事能不能稳定复制"),
    ("9 月 · 付费玩家付费率", f"{DX['payrate']:.1f}% → 46.8%",
     "<b>黑五小额是全场最快的付费率杠杆</b>：P2「感恩节黑五小额」单品 <b>5,822 买家</b>、人均仅 $10.5，比挖孔（2,757 买家）还广一倍"),
    ("10 月 · 节日日均 ARPPU", f"${DX['arppu']:.1f} → $30.5–34.1",
     "黑五的<b>大额/折扣档补深度</b>：终极连锁人均 $174、黑五折扣 $124、黑五大额 $99，三档都是靠「折扣感」拉高单笔"),
    ("9/10 月 · 未上线内容", "回补", "11 月是<b>轻开发月</b>（原计划只有 3 天新开发），产能余量正好吃掉 9/10 月的欠账"),
]

OCT = [
    ("主城皮肤深度付费挖掘", "主城皮肤<b>套装系统</b>",
     "现有 20 款主城皮肤是单件售卖，套装化＝把同一资产从「买一件」变成「集一套」",
     "P2 圣诞跨服榜 30 份高级皮 + Top3 染色，上榜线 $1,444 / 中位 $2,529"),
    ("英雄皮肤深度品质挖掘", "分品质 + 按品质定价",
     "四档梯度（至尊+150%/传说+100%/史诗+50%/限定+30%）<b>早已存在但完全没跑起来</b>——至尊仅 11 人持有",
     "内部先例：家具皮肤已有青铜/白银/黄金三档带不同属性"),
    ("装饰物升级系统", "装饰从「买断」变「可升级」",
     "现有装饰 146 件多为功能性家具，节日装饰礼包深海仅 $1.3k / 夏日 $0.58k＝几乎卖不动",
     "升级系统＝给已售出的装饰开续费口，不用新出美术"),
    ("新增节日卡册", "卡册节日版",
     "与纪念卡分属两套系统；纪念卡 9 月已做「拆分投放定位」，卡册是另一条收集线",
     "10 月开发预估 5 天"),
]

html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>X3 9-10月模块规划 · 周占比达标</title><style>
:root{{--bg:#0d1117;--panel:#141b24;--panel2:#1a232e;--line:#243040;--fg:#e8f0f8;
--dim:#8fa3b8;--dim2:#6b7f95;--acc:#5ad1ff;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;--new:#c084fc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);line-height:1.7;
font-family:"Microsoft YaHei","PingFang SC",sans-serif;font-size:14px}}
main{{max-width:1120px;margin:0 auto;padding:34px 32px 90px}}
h1{{margin:0;font-size:27px}}.sub{{color:var(--warn);font-size:16.5px;font-weight:700;margin:6px 0 10px}}
.meta{{color:var(--dim2);font-size:12.5px;border-bottom:1px solid var(--line);padding-bottom:16px}}
.meta b{{color:var(--acc)}}
.verdict{{background:linear-gradient(180deg,#16202b,#131a23);border:1px solid var(--line);
border-left:3px solid var(--warn);border-radius:6px;padding:15px 19px;margin:20px 0}}
.verdict .t{{font-size:10.5px;letter-spacing:.22em;color:var(--warn);font-weight:700}}
.verdict p{{margin:8px 0 0}}.verdict b{{color:#fff}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:13px 15px;border-top:2px solid var(--acc)}}
.kpi.bad{{border-top-color:var(--bad)}}.kpi.ok{{border-top-color:var(--ok)}}.kpi.warn{{border-top-color:var(--warn)}}
.kpi b{{display:block;font-size:25px;line-height:1.25}}.kpi .t{{font-size:12px;color:var(--dim)}}
.kpi .n{{font-size:11px;color:var(--dim2);margin-top:4px}}
h2{{font-size:18px;margin:42px 0 4px}}h2 .no{{display:inline-block;background:var(--acc);color:#06202b;
font-size:12px;font-weight:700;border-radius:4px;padding:1px 8px;margin-right:9px;vertical-align:2px}}
h2+.lead{{color:var(--dim);margin:0 0 14px;font-size:13px}}
h3{{font-size:14.5px;margin:22px 0 6px}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:12.5px;background:var(--panel)}}
th,td{{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}}
th{{background:var(--panel2);color:var(--dim);font-size:11.5px;white-space:nowrap}}
td.n{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
tr:hover td{{background:rgba(90,209,255,.04)}}
.note{{background:var(--panel2);border:1px solid var(--line);border-left:3px solid var(--dim2);
border-radius:5px;padding:11px 15px;font-size:12.5px;color:var(--dim);margin:14px 0}}
.note b{{color:var(--fg)}}.note.bad{{border-left-color:var(--bad)}}.note.ok{{border-left-color:var(--ok)}}
svg{{background:var(--panel);border:1px solid var(--line);border-radius:6px;margin-top:8px}}
.lg{{display:flex;gap:14px;flex-wrap:wrap;font-size:11.5px;color:var(--dim);margin:8px 0}}
.lg i{{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px}}
.wk{{border-left:3px solid;padding:12px 15px;background:var(--panel);border-radius:0 6px 6px 0;margin:10px 0}}
.wk .h{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}}
.wk .w{{font-size:11px;letter-spacing:.14em;color:var(--dim2)}}
.wk .m{{font-size:16px;font-weight:700}}
.wk .goal{{margin-left:auto;font-size:12px;color:var(--dim)}}
.wk .goal b{{font-size:17px;color:var(--warn)}}
.wk .art{{font-size:12.5px;color:var(--fg);margin-top:4px}}
.wk .ev{{font-size:11.5px;color:var(--dim2);margin-top:3px}}
/* 时间轴切换 */
.tabs{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:12px 0 0}}
.tabs .mt{{background:transparent;color:var(--dim);border:1px solid var(--line);border-radius:4px;
padding:5px 13px;font-size:12.5px;cursor:pointer;font-family:inherit;transition:.15s}}
.tabs .mt:hover{{color:var(--fg);border-color:var(--acc)}}
.tabs .mt.on{{background:var(--acc);border-color:var(--acc);color:#06202b;font-weight:700}}
.tabs .hint{{font-size:11.5px;color:var(--dim2);margin-left:6px}}
#chart svg{{margin-top:8px}}
</style></head><body><main>

<h1>X3 9–10 月模块规划</h1>
<div class="sub">KPI 只看一个数：该模块当周收入 ÷ 当周大盘收入</div>
<div class="meta">P2 对照＝2025-10 ~ 2026-07 逐周实查（全服）· X3＝成熟服 1000–1880 逐周 ·
数仓实查 2026-07-29 · 口径统一为<b>模块周收入 / 当周大盘收入</b>（各模块周占比可直接加总，对齐节日占比目标）</div>

<div class="verdict"><div class="t">VERDICT · 宏观三句话</div>
<p>① <b>X3 单模块强度其实不弱</b>：夏日开箱单周做到 <b>15.2%</b>，已经摸到 P2 挖孔的中位线（{m_med:.1f}%）。<b>差的不是模块做得好不好，是一周只有一个模块在打、且一个月只有一两周有。</b></p>
<p>② <b>真正的窟窿是空窗</b>：X3 有整周节日占比掉到 <b>0.3%–0.6%</b>（6/08、6/15、7/27），而 P2 常年 <b>40–58%</b>，最低也有 19.4%。<b>空窗周的钱是白丢的，而补空窗不需要任何新玩法。</b></p>
<p>③ <b>40–50% 怎么凑出来</b>：P2 的做法不是把一个模块做到 50%，而是<b>每周有一个 15%+ 的主力模块顶着，再叠辅助层</b>。挖孔峰值周单个就 <b>{m_max:.1f}%</b>——一个模块顶起半个目标。</p>
</div>

<div class="kpis">
<div class="kpi ok"><b>{m_med:.1f}%</b><div class="t">P2 挖孔 · 周占比中位</div><div class="n">16 个投放周 · 峰值 <b>{m_max:.1f}%</b></div></div>
<div class="kpi"><b>{p_med:.1f}%</b><div class="t">P2 弹珠 · 周占比中位</div><div class="n">12 个投放周 · 峰值 {p_max:.1f}%</div></div>
<div class="kpi warn"><b>{x3_best_single[0]:.1f}%</b><div class="t">X3 最好的单模块周</div><div class="n">{x3_best_single[1]} · {x3_best_single[2]}</div></div>
<div class="kpi bad"><b>{x3_gap[0][1]:.1f}%</b><div class="t">X3 空窗周占比</div><div class="n">{len(x3_gap)} 个整周几乎归零</div></div>
</div>

<h2><span class="no">01</span>达标线 — 一个模块一周该拿多少</h2>
<p class="lead">P2 同口径实测。<b>主力模块单周 ≥15% 算达标，峰值周应到 25%+。</b></p>
<table>
<tr><th>模块</th><th class="n">投放周数</th><th class="n">中位</th><th class="n">峰值</th><th class="n">最低</th><th>判读</th></tr>
<tr><td><b>P2 挖孔</b></td><td class="n">16</td><td class="n"><b style="color:var(--ok)">{m_med:.1f}%</b></td><td class="n"><b>{m_max:.1f}%</b></td><td class="n">{min(ms):.1f}%</td><td>单兵之王，峰值周一个模块顶起 40% 目标的全部</td></tr>
<tr><td><b>P2 弹珠</b></td><td class="n">12</td><td class="n">{p_med:.1f}%</td><td class="n">{p_max:.1f}%</td><td class="n">{min(ps):.1f}%</td><td>约挖孔的 6 成；<b>带排行榜 $222k vs 无榜 $167k</b></td></tr>
<tr><td>X3 夏日开箱</td><td class="n">3</td><td class="n">—</td><td class="n">15.2%</td><td class="n">0.3%</td><td>X3 自身最好成绩，已达 P2 挖孔中位线</td></tr>
<tr><td>X3 大富翁族</td><td class="n">3</td><td class="n">—</td><td class="n">7.6%</td><td class="n">2.8%</td><td>压舱石，但只有主力线的一半</td></tr>
<tr><td>X3 转盘</td><td class="n">3</td><td class="n">—</td><td class="n">3.5%</td><td class="n">0.5%</td><td>判退役正确</td></tr>
</table>
<div class="note ok"><b>结论：把"周占比 ≥15%"当作主力模块的验收线。</b>X3 已经证明自己做得到（夏日开箱 15.2%），
问题是<b>做到的周太少</b>——9 月的排布就是要让<b>每一周都有一个够到这条线的模块</b>。</div>

<h2><span class="no">02</span>P2 实证 — 挖孔 vs 弹珠 逐周占比</h2>
<p class="lead">柱高＝该模块当周收入占 P2 当周大盘的比例。只显示有投放的周。</p>
<h3 style="color:var(--ok)">挖孔（16 周 · 中位 {m_med:.1f}% · 峰值 {m_max:.1f}%）</h3>
{bars([r for r in p2r if r["m"]>3000], "sm", "#4ade80", 45)}
<h3 style="color:var(--new)">弹珠（12 周 · 中位 {p_med:.1f}% · 峰值 {p_max:.1f}%）</h3>
{bars([r for r in p2r if r["p"]>3000], "sp", "#c084fc", 45)}
<div class="note"><b>看两件事</b>：① 挖孔<b>反复投放且不衰减</b>——从 2025-11 到 2026-07 投了 16 个周，中位仍有 {m_med:.1f}%，
说明它不是"新鲜感收割"，是可持续弹药；② 峰值 {m_max:.1f}% 那周（2026-05-25 拓荒 W3），
<b>节日整体占比冲到 66.5%</b>——一个模块把整月拉起来。</div>

<h2><span class="no">03</span>X3 现状 — 逐周各模块占比（成熟服）</h2>
<p class="lead">堆叠柱＝当周各节日模块占大盘之和。数字标在柱顶，<b style="color:var(--bad)">红色＝该周几乎无节日收入</b>。</p>
<div class="lg">{"".join(f'<span><i style="background:{COL[n]}"></i>{n}</span>' for n in X3_MODS)}</div>
{stack(x3)}
<div class="note bad"><b>三个问题一目了然</b>：① <b>{len(x3_gap)} 个整周归零</b>（{", ".join(w for w,_ in x3_gap)}）——空窗期大盘照常有 $45–53k，节日一分钱没拿到；
② 最好的一周也只有 <b>{x3_best_sum[0]:.1f}%</b>（{x3_best_sum[1]}），且是<b>四个模块叠出来的</b>，没有单个主力顶梁柱；
③ 模块之间<b>此消彼长</b>而不是接力——开箱起来时大富翁还没上，大富翁上来时开箱已衰减。</div>

<h2><span class="no">04</span>9 月排布 — 三个 W ＝ 21 天，全程不断档</h2>

<div class="note warn"><b>先定节日期长度：9 月要做到 21 天（D0–D20）。</b>
依据＝X3 夏日恋语只撑了 <b>12 天</b>就断（付费率中位 32.8%），而 P2 深海节 <b>21 天</b>、拓荒节 <b>23 天</b>，
且它们在 D12 之后<b>还能反复起波</b>（见 §10 图）。
<b>三个 W × 7 天 ＝ 21 天，正好对齐 P2 的单节日长度</b>——这一轮的核心不只是"每周有主力"，
更是<b>把线拉到 D20 且中间不许出现空档</b>。</div>

<p class="lead">右侧＝该周<b>主力模块的周占比目标</b>（依据 P2 同形式实测）。</p>
{"".join(f'''<div class="wk" style="border-left-color:{c}">
<div class="h"><span class="w">{w} · {rng}</span><span class="m" style="color:{c}">{mod}</span>
<span class="goal">周占比目标 <b>{goal}</b></span></div>
<div class="art">配套外显：{art}</div><div class="ev">依据：{ev}</div></div>''' for w, rng, mod, art, c, ev, goal in SEP9)}

<h3>21 天填充清单 — 每一层都要接上，不留空档</h3>
<p class="lead">横向读＝该层在三周里怎么接力；纵向读＝该周玩家能碰到的全部内容。
<b>弹药带负责冲高，其余五层负责"不掉下来"。</b></p>
<table>
<tr><th style="width:132px">层</th><th>W1 · D0–D6</th><th>W2 · D7–D13</th><th>W3 · D14–D20</th></tr>
{"".join(
  (f'<tr><td style="border-left:3px solid {c}"><b>{lay}</b></td>'
   f'<td colspan="3" style="text-align:center;background:rgba(74,222,128,.07)">{w1}</td></tr>')
  if not w2 and not w3 else
  (f'<tr><td style="border-left:3px solid {c}"><b>{lay}</b></td>'
   f'<td>{w1}</td><td>{w2}</td><td>{w3}</td></tr>')
  for lay, c, w1, w2, w3 in FILL)}
</table>

<div class="note"><b>三周加总</b>：主力模块 15–19 + {m_med:.0f}–25 + 20–27 ≈ <b>50–70% 分布在三周</b>，
再叠常驻货架层（累充/每日/周卡/拜访/装饰/兑换，合计约 8–12%）。<br>
<b>两个关键设计点</b>：① <b>W3 堆叠</b>——弹珠中位只有 {p_med:.1f}%，单独撑一周够不到 15% 主力线，和开箱并行才能把该周做到 20%+；
② <b>免费向那一层是拉付费率的底座</b>——签到/拼图/酒馆/许愿池不直接赚钱，但它们决定了有多少付费玩家"进到节日里"，
而 §09 已经算过：<b>40% 目标只需付费率从 32.1% 提到 46.8%，ARPPU 都不用动。</b></div>

<h3>W3 开箱 · 皮肤返场标的（按"潜在受众"排序）</h3>
<p class="lead">潜在受众 ＝ 该英雄解锁人数 − 该皮肤已获取人数。<b>这批皮肤的美术成本早就付过了，返场几乎零美术投入。</b></p>
<table>
<tr><th style="width:26px">#</th><th>皮肤</th><th>标签</th><th class="n">属性</th><th class="n">已获取</th>
<th class="n">英雄解锁</th><th class="n">潜在受众</th><th class="n">当前获取率</th></tr>
{"".join(f'''<tr><td class="n">{i+1}</td><td><b>{s["name"] or s["skin_id"]}</b></td>
<td>{s["tag"] or "—"}</td>
<td class="n">{("+"+str(int(s["prop_num"])//100)+"%") if s["prop_num"].isdigit() and int(s["prop_num"])>=100 else "—"}</td>
<td class="n">{s["owners"]:,}</td><td class="n">{s["hero_owners"]:,}</td>
<td class="n"><b style="color:var(--warn)">{s["gap"]:,}</b></td>
<td class="n">{s["rate"]:.2f}%</td></tr>''' for i, s in enumerate(rev[:12]))}
</table>
<div class="note ok"><b>返场为什么值得做（三条依据）</b>：
① <b>头号标的是红绸剑姬·阿米娜</b>——至尊 +150%，阿米娜有 <b>599,305 人</b>解锁，皮肤却只有 <b>11 人</b>持有，
潜在受众近 60 万，是全表最大的一块未开发市场；
② 榜单里 <b>热浪尤物·赛米拉（0.02%）、永恒誓约·赛米拉（0.04%）、笑迎春·茉莉（0.40%）</b>都是带属性的高级皮，
<b>当年当纯付费品卖没卖出去，不等于没需求</b>——把它们放进开箱奖池是二次变现；
③ P2 有现成先例：<b>返场皮走兑换商店三档（白嫖自选宝箱 → 高级返场中位 $893）</b>，形式可直接照搬。</div>
<div class="note"><b>⚠️ 返场要避的坑</b>：返场会稀释"限定"的稀缺承诺。建议 ①<b>只返 1 年以上的老皮</b>，
②<b>至尊/传说档返场要换获取路径</b>（当年是直购，返场走开箱概率），别原价重售，
③把 <b>3 款零持有的皮肤</b>（黑金契约·霍普金斯 / 金海商使·霍普金斯 / 魅影魔术师·琥珀）优先塞进首批，
它们从没被任何人拿到过，<b>返场对老玩家零伤害</b>。</div>

<h2><span class="no">05</span>10 月 — 优化投放，拉「节日日均 ARPPU」</h2>
<p class="lead">9 月把线<b>横向拉长</b>（21 天不断档、每周一个主力），10 月把线<b>纵向抬高</b>（同一批人卖更深）。
两个动作在 §10 的图上分别是绿色横箭头和黄色竖箭头。</p>

<div class="note warn"><b>KPI 口径钉死：日粒度 · 节日活跃日 · ARPPU 中位数</b>　＝ 当日节日收入 ÷ 当日节日付费人数，
取活跃日（付费率≥10%）的中位。<b>现状 ${DX['arppu']:.1f} → 目标 $30.5–34.1</b>（P2 为 ${DP['arppu']:.1f}）。<br>
⚠️别跟周粒度混：同一指标按周聚合是 X3 ${x3_am:.1f} / P2 ${p2_am:.1f}（周维度收入累加而人数去重，天然更高）。
<b>考核用哪个粒度必须先说清，否则同一件事会得出两个结论。</b></div>

<div class="kpis">
<div class="kpi bad"><b>${DX['arppu']:.1f}</b><div class="t">X3 节日日均 ARPPU · 中位</div><div class="n">活跃日区间 ${min(r['arppu'] for r in SX if r['payrate']>=10):.1f}–${max(r['arppu'] for r in SX):.1f}</div></div>
<div class="kpi ok"><b>${DP['arppu']:.1f}</b><div class="t">P2 同指标 · 中位</div><div class="n">差 {DP['arppu']/DX['arppu']:.2f}× · 拓荒节达 $38.5</div></div>
<div class="kpi warn"><b>{DX['payrate']:.1f}%</b><div class="t">X3 付费玩家付费率</div><div class="n">9 月要拉的那条（P2 {DP['payrate']:.1f}%）</div></div>
<div class="kpi"><b>$30.5–34.1</b><div class="t">10 月 ARPPU 目标</div><div class="n">＝P2 的 92%–103%</div></div>
</div>

<h3>两个因子一起看 — 渗透 × ARPPU</h3>
<div class="lg"><span><i style="background:#5ad1ff;border-radius:50%"></i>X3 每周（成熟服）</span>
<span><i style="background:#c084fc;border-radius:50%;opacity:.5"></i>P2 每周（背景云）</span>
<span><i style="background:#4ade80;opacity:.3;border:1px dashed #4ade80"></i>P2 主力周所在区</span></div>
{scatter_pen_arppu()}
<div class="note bad"><b>这张图是 9 月/10 月分开做的根据：</b>
X3 的点<b>全部落在左下角</b>——渗透中位 {x3_pm:.0f}%（P2 {p2_pm:.0f}%）、ARPPU 中位 ${x3_am:.1f}（P2 ${p2_am:.1f}）。
更关键的是 <b>X3 两个因子还互相拖</b>：渗透最高那周（52.4%）ARPPU 只有 $35.9，
而 ARPPU 最高那周（${x3_amax:.1f}）渗透只有 31.5%——<b>广度和深度没法同时拿到</b>。
P2 则是两者同时高（渗透 60%+ 且 ARPPU $90+），所以它的绿色目标区在右上。</div>

<h3>10 月四个方向 — 都是冲 ARPPU 的</h3>
<table>
<tr><th style="width:180px">方向</th><th style="width:165px">做法</th><th>为什么现在做</th><th style="width:220px">参照</th></tr>
{"".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td style="color:var(--dim2)">{dd}</td></tr>' for a, b, c, dd in OCT)}
</table>
<div class="note ok"><b>10 月的验收线</b>：节日日均 ARPPU 从 <b>${DX['arppu']:.1f}</b> 拉到 <b>$30.5–34.1</b>
（＝P2 的 92%–103%），<b>且付费率不许掉回 9 月以前</b>——占比 ＝ 付费率 × ARPPU，
任一因子跌回去都白做（§09 恒等式）。<br>
<b>四个方向为什么都能拉 ARPPU</b>：套装＝把"买一件"变"集一套"（同一批人多买几件）；
分品质定价＝给愿意多花的人开更高档位；装饰升级＝给已买过的人开续费口；
卡册＝新增一条收集线，深度由坑深决定而不是靠拉新人。<b>四条全部作用在"已经在花钱的人"身上，这才是 ARPPU 而非付费率。</b></div>

<h2><span class="no">06</span>11 月 — 黑五 ＋ 查漏补缺 9/10 月</h2>
<p class="lead">黑五是<b>价格驱动</b>的付费节点（不是玩法驱动），内容开发压力小，
所以它同时承担两个角色：<b>用折扣拉付费率</b> ＋ <b>把 9/10 月没达成的目标补回来</b>。</p>

<div class="note ok"><b>为什么黑五正好打在 X3 的短板上：</b>
我们早就量出 X3 有四个形式差，其中一条是<b>「没有 $0.99–4.99 的宽入口」</b>。
而 P2 黑五的头号单品「感恩节黑五小额」——<b>5,822 买家、人均仅 $10.5</b>，
<b>比挖孔（2,757 买家）还广一倍</b>。这是全场最快的付费率杠杆，而且开发成本几乎为零（纯配置礼包）。</div>

<h3>P2 黑五 / 感恩节礼包结构 — 小额宽入口 ＋ 大额收鲸双轨</h3>
<table>
<tr><th>礼包</th><th class="n">买家</th><th class="n">人均</th><th>定位</th><th style="width:230px">买家规模对比</th></tr>
{"".join(f'''<tr><td>{n}</td><td class="n"><b>{b:,}</b></td><td class="n">${a}</td>
<td><span class="pill" style="color:{c};border:1px solid {c}55;background:{c}18">{r}</span></td>
<td><span class="bar" style="width:{b/5822*210:.0f}px;background:{c}"></span></td></tr>''' for n, b, a, r, c in NOV_PACKS)}
</table>
<div class="note"><b>双轨结构看得很清楚</b>：小额三档（5,822 / 3,868 / 1,815 买家，人均 $10–22）负责<b>把人拉进来</b>；
大额三档（947 / 596 / 439 买家，人均 $99–174）负责<b>收鲸</b>。
<b>两头都做才是黑五</b>——只做折扣小额则 ARPPU 掉，只做大额则付费率上不去。<br>
P2 2025 感恩节期实测（11-13~11-30，18 天）：付费率 <b>30–55%</b>、ARPPU <b>$23–57</b>、占大盘 <b>31–67%</b>，
峰值日 11-23（付费率 51.6% / ARPPU $56.7 / <b>占大盘 67.3%</b>）。</div>

<h3>查漏补缺 — 9/10 月的目标在 11 月结账</h3>
<table>
<tr><th style="width:170px">来源</th><th style="width:170px">原定目标</th><th>若未达成，11 月怎么补</th></tr>
{"".join(f'<tr><td><b>{a}</b></td><td class="n">{b}</td><td>{c}</td></tr>' for a, b, c in NOV_FIX)}
</table>
<div class="note warn"><b>把 11 月设成"结账月"是这套半年规划的安全阀</b>：
9 月拉广度、10 月拉深度，两个月都是<b>新东西</b>，有翻车风险；
11 月内容压力最小、产能余量最大，<b>是唯一能回补的窗口</b>。
所以 11 月的动作清单应该在 <b>10 月底根据实际数据再定</b>，现在只锁"黑五双轨"这一件。</div>

<h2><span class="no">07</span>12 月 — 圣诞 ＋ 套装 2 期，冲流水</h2>
<p class="lead">年度收官月。三个抓手叠在一起：内外墙回到原生场景、套装复用系统只出内容、四件弹药全部就绪。</p>
{"".join(f'''<div class="wk" style="border-left-color:{c}">
<div class="h"><span class="m" style="color:{c}">{t}</span></div>
<div class="art">{d}</div><div class="ev">价值：{v}</div></div>''' for t, c, d, v in DEC_LAYERS)}
<div class="note ok"><b>12 月是半年里"投入产出比"最好的一个月</b>：
系统开发都在 9/10 月摊完了（挖孔、弹珠、套装系统、品质分档），
12 月<b>只需出美术＋配置</b>就能把四件弹药 + 套装 2 期全部铺开。
P2 12 月周节日收入能到 <b>$369,579（占大盘 55.5%）</b>——年底本身就是付费意愿高点，
<b>这是全年最该冲的一个月，而不是收摊的月份。</b></div>

<h2><span class="no">08</span>宏观账 — 40–50% 从哪儿来</h2>
<div class="note"><b>先把公式摆出来，两个月各攻一个因子：</b><br>
<span style="color:var(--fg);font-size:14px">节日占比 ＝ <b style="color:var(--warn)">节日渗透</b> × <b style="color:var(--acc)">节日 ARPPU</b> ÷ 大盘 ARPU</span><br>
以 X3 07-13 那周实测校验：198 人 × $51.8 ÷ $48,599 ＝ <b>21.1%</b> ✓（与直接算 $10,250/$48,599 一致）<br>
同周 P2：2,500 人 × $74.2 ÷ $453,284 ＝ <b>40.9%</b> ✓<br>
→ <b>要从 21% 走到 40%，需要「渗透 ×1.6」×「ARPPU ×1.35」＝ ×2.16。这就是 9 月和 10 月各自的任务量。</b></div>
<table>
<tr><th>来源</th><th>攻哪个因子</th><th>动作</th><th class="n">贡献</th><th class="n">累计</th><th>开发成本</th></tr>
<tr><td>现状</td><td>—</td><td>成熟服 61 天累计</td><td class="n">—</td><td class="n"><b>15.0%</b></td><td>—</td></tr>
<tr><td><b>补空窗</b></td><td>渗透（时间维）</td><td>每月排满，消灭 0.3% 的整周</td><td class="n">+5–7pt</td><td class="n"><b>20–22%</b></td><td><b style="color:var(--ok)">0 天</b>（纯排期）</td></tr>
<tr><td><b>9 月：每周一个主力</b></td><td><b style="color:var(--warn)">渗透 ×1.6</b></td><td>三个 W 各达 15%+ 线，W3 双模块堆叠</td><td class="n">+7–13pt</td><td class="n"><b>27–35%</b></td><td>挖孔 7d + 弹珠 5d</td></tr>
<tr><td><b>10 月：深度付费优化</b></td><td><b style="color:var(--acc)">ARPPU ×1.35</b></td><td>套装 / 品质 / 装饰升级 / 卡册，把投放做深</td><td class="n">+8–14pt</td><td class="n"><b>35–49%</b></td><td>套装 7d + 品质 5d + 装饰 3d + 卡册 5d</td></tr>
</table>
<div class="note"><b>三段全做才够到 40–50%</b>，且第一段零开发成本。
⚠️三段之间有重叠（补空窗的收益部分来自主力模块本身），表中已按下沿取值；
<b>对外承诺建议按"半年到 35%"讲，40–50% 作为上限空间。</b></div>

<h2><span class="no">09</span>目标拆解 — 按日拉通 P2 4/5/6 月</h2>
<p class="lead">P2 取 2026-04-01~06-30（91 天，含拓荒全程 + 深海前段），X3 取 2026-05-25~07-27（64 天）。
「节日活跃日」＝付费玩家付费率 ≥10% 的日子；下列均为<b>活跃日中位数</b>。</p>

<table>
<tr><th>指标</th><th class="n">P2</th><th class="n">X3</th><th class="n">倍数</th><th>判读</th></tr>
<tr><td><b>付费玩家付费率</b><br><span style="color:var(--dim2);font-size:11.5px">节日付费人数 / 当日总付费人数</span></td>
  <td class="n"><b>{DP['payrate']:.1f}%</b></td><td class="n"><b style="color:var(--warn)">{DX['payrate']:.1f}%</b></td>
  <td class="n">{DP['payrate']/DX['payrate']:.2f}×</td><td><b>广度差距</b>——一半付费玩家碰不到节日</td></tr>
<tr><td><b>付费玩家 ARPPU</b><br><span style="color:var(--dim2);font-size:11.5px">节日收入 / 节日付费人数</span></td>
  <td class="n"><b>${DP['arppu']:.1f}</b></td><td class="n"><b style="color:var(--warn)">${DX['arppu']:.1f}</b></td>
  <td class="n">{DP['arppu']/DX['arppu']:.2f}×</td><td><b>深度差距</b>——比广度差距小得多</td></tr>
<tr><td>节日占大盘</td><td class="n">{DP['share']:.1f}%</td><td class="n">{DX['share']:.1f}%</td>
  <td class="n">{DP['share']/DX['share']:.2f}×</td><td>＝上面两项相乘的结果</td></tr>
<tr style="background:rgba(74,222,128,.06)"><td><b>大盘日 ARPU</b></td>
  <td class="n">${DP['arpu']:.1f}</td><td class="n">${DX['arpu']:.1f}</td>
  <td class="n"><b style="color:var(--ok)">{DP['arpu']/DX['arpu']:.2f}×</b></td>
  <td><b style="color:var(--ok)">钱包几乎一样</b>——差距不在玩家有多少钱</td></tr>
<tr style="background:rgba(248,113,113,.06)"><td><b>空窗日占比</b></td>
  <td class="n">{DP['gap_ratio']:.1f}%</td><td class="n"><b style="color:var(--bad)">{DX['gap_ratio']:.1f}%</b></td>
  <td class="n">X3 是 {DX['gap_ratio']/DP['gap_ratio']:.1f} 倍</td>
  <td><b>这是累计占比 15% vs 37.7% 的主因</b></td></tr>
</table>

<div class="note ok"><b>三因子恒等式（两边实测都对得上，可以拿去汇报）</b><br>
<span style="color:var(--fg);font-size:14.5px">累计节日占比 ＝ <b style="color:var(--bad)">(1 − 空窗率)</b> × <b style="color:var(--warn)">付费玩家付费率</b> × <b style="color:var(--acc)">节日 ARPPU</b> ÷ 大盘 ARPU</span><br>
X3：(1−{DX['gap_ratio']/100:.3f}) × {DX['payrate']:.1f}% × ${DX['arppu']:.1f} ÷ ${DX['arpu']:.1f} ＝ <b>{cum(DX):.1f}%</b>（实测累计 15.0%）<br>
P2：(1−{DP['gap_ratio']/100:.3f}) × {DP['payrate']:.1f}% × ${DP['arppu']:.1f} ÷ ${DP['arpu']:.1f} ＝ <b>{cum(DP):.1f}%</b>（实测 37.7%）<br>
→ <b>三个因子刚好对应三件事：排期（空窗率）· 9 月（付费率）· 10 月（ARPPU）。</b></div>

<h3>活跃日占比 {DX['share']:.1f}% → 40% / 50% 的三条路径</h3>
<table>
<tr><th style="width:88px">目标</th><th style="width:150px">路径</th><th>要把哪个数推到多少</th><th class="n">对标 P2</th><th>可行性</th></tr>
<tr><td rowspan="3"><b>40%</b><br><span style="color:var(--dim2);font-size:11.5px">需 ×{P40['need']:.2f}</span></td>
  <td>A · 只提付费率</td><td>付费率 {DX['payrate']:.1f}% → <b>{P40['A'][0]:.1f}%</b>（ARPPU 不动）</td>
  <td class="n">P2 {DP['payrate']:.1f}%</td><td><b style="color:var(--ok)">✓ 单腿可达</b>，且仍低于 P2</td></tr>
<tr><td>B · 只提 ARPPU</td><td>ARPPU ${DX['arppu']:.1f} → <b>${P40['B'][0]:.1f}</b>（付费率不动）</td>
  <td class="n">P2 ${DP['arppu']:.1f}</td><td><span style="color:var(--bad)">✗ 要超过 P2</span></td></tr>
<tr><td><b>C · 两者同抬</b></td><td>付费率 → <b>{P40['C'][0]:.1f}%</b>　+　ARPPU → <b>${P40['C'][1]:.1f}</b></td>
  <td class="n">P2 的 {P40['C'][2]:.0f}% / {P40['C'][3]:.0f}%</td><td><b style="color:var(--ok)">✓ 最稳</b>，两项都不用超 P2</td></tr>
<tr><td rowspan="3"><b>50%</b><br><span style="color:var(--dim2);font-size:11.5px">需 ×{P50['need']:.2f}</span></td>
  <td>A · 只提付费率</td><td>付费率 → {P50['A'][0]:.1f}%</td><td class="n">P2 {DP['payrate']:.1f}%</td>
  <td><span style="color:var(--bad)">✗ 要超过 P2</span></td></tr>
<tr><td>B · 只提 ARPPU</td><td>ARPPU → ${P50['B'][0]:.1f}</td><td class="n">P2 ${DP['arppu']:.1f}</td>
  <td><span style="color:var(--bad)">✗ 远超 P2</span></td></tr>
<tr><td><b>C · 两者同抬</b></td><td>付费率 → <b>{P50['C'][0]:.1f}%</b>　+　ARPPU → <b>${P50['C'][1]:.1f}</b></td>
  <td class="n">P2 的 {P50['C'][2]:.0f}% / {P50['C'][3]:.0f}%</td>
  <td><span style="color:var(--warn)">△ ARPPU 需略超 P2</span></td></tr>
</table>

<div class="note"><b>拆解结论（建议照这个定目标）</b><br>
① <b>40% 是舒适目标</b>：只把付费玩家付费率从 {DX['payrate']:.1f}% 提到 {P40['A'][0]:.1f}%（<b>仍低于 P2 的 {DP['payrate']:.1f}%</b>）就够，ARPPU 一动不用动——<b>这正是 9 月"每周一个主力模块"要干的事</b>。<br>
② <b>50% 必须两条腿一起走</b>，且 ARPPU 要摸到 P2 的 {P50['C'][3]:.0f}%。所以 <b>10 月的深度优化不是可选项，是 50% 的必要条件</b>。<br>
③ <b>但上面两条都只是"活跃日"的账</b>。要让<b>累计占比</b>也到 40%，还得把空窗率从 {DX['gap_ratio']:.1f}% 压下来——
按恒等式：空窗率降到 15% + 活跃日占比做到 47%（＝P2 水平），累计 ＝ 0.85 × 47% ＝ <b>40.0%</b>。
<b>三件事缺一不可：排满日历、9 月拉付费率、10 月拉 ARPPU。</b></div>

<h2><span class="no">10</span>节日期时间轴 — P2 / X3 同图对比（D0 对齐）</h2>
<p class="lead">只截取<b>节日期</b>（付费玩家付费率 ≥10% 的连续日，容 1 天间断），横轴＝<b>节日第 N 天</b>而非日历日期，
这样两边的<b>开场高度和衰减形状可以直接叠着比</b>。纵轴三个指标可切换，图例可点击开关。</p>
<div class="tabs">
  <button class="mt on" data-k="payrate">付费玩家付费率</button>
  <button class="mt" data-k="arpu">节日 ARPU</button>
  <button class="mt" data-k="arppu">节日 ARPPU</button>
  <span class="hint" id="mhint"></span>
</div>
<div class="lg" id="legend"></div>
<div id="chart"></div>
<div class="note" id="mnote"></div>

<h3>各节日期汇总（自动切段实查）</h3>
<table>
<tr><th>节日期</th><th>窗口</th><th class="n">天数</th><th class="n">节日收入</th>
<th class="n">付费率中位</th><th class="n">ARPPU 中位</th></tr>
{"".join(f'''<tr{' style="background:rgba(90,209,255,.05)"' if s["side"]=="X3" else ''}>
<td><b style="color:{s["color"]}">{s["name"]}</b></td><td>{s["start"]} ~ {s["end"]}</td>
<td class="n">{s["n"]}</td><td class="n">${s["rev"]:,}</td>
<td class="n">{s["pr_med"]}%</td><td class="n">${s["ap_med"]}</td></tr>''' for s in SEGS)}
</table>
<div class="note bad"><b>这张表最扎心的一行对比</b>：
<b>P2 拓荒节 23 天做了 $1,033,100</b>（付费率中位 54.1% / ARPPU $38.5），
而 <b>X3 世界杯+深海双节叠在一起、拉了 27 天，只做了 $45,603</b>（付费率 28.9% / ARPPU $26.8）。
<b>X3 的节日期更长，但付费率只有一半、ARPPU 七成</b>——时间拉得久不等于收得多。<br>
再看图上的形状：P2 各节日在 D0 冲高后<b>能在高位反复起波</b>（每周换弹药），
X3 是<b>D0 冲高后单调衰减</b>，中途没有第二波。</div>

<h3>X3 已上过的节日（成熟服 1000–1880 · 自夏日 D0 累计 61 天）</h3>
<table>
<tr><th>节日</th><th>窗口</th><th class="n">节日收入</th><th class="n">占大盘</th><th>主要模块</th></tr>
{"".join(f'<tr><td><b>{n}</b></td><td>{w}</td><td class="n">${r:,}</td><td class="n">{s}%</td><td style="color:var(--dim2)">{m}</td></tr>' for n, w, r, s, m in X3_FESTS)}
<tr style="background:rgba(90,209,255,.05)"><td><b>合计</b></td><td>—</td>
  <td class="n"><b>${sum(f[2] for f in X3_FESTS):,}</b></td>
  <td class="n"><b>15.0%</b></td><td>大盘 $447,247</td></tr>
</table>
<div class="note"><b>空窗提醒</b>：上表是"节日期内"的账，<b>不含空窗</b>。X3 在 <b>06-09 ~ 06-25</b>（夏日结束、世界杯未开）
和 <b>07-22 之后</b>（双节下线至今）都处于空窗，这两段合计占了统计期的 <b>{DX['gap_ratio']:.0f}%</b>，
是累计占比只有 15.0% 的主因（见 §09 恒等式）。</div>

<div class="note" style="margin-top:24px"><b>数据来源</b>　P2＝<code>v1041.dl_user_order</code> × <code>dim_iap</code>（挖孔/弹珠按 iap_id_name 匹配，节日收入＝<code>iap_type='混合-节日活动'</code>）·
X3＝<code>v1090.ods_user_order</code>（成熟服 1000–1880，USD 口径）· 均按自然周聚合。<br>
<b>脚本</b>　<code>skills\\p2-festival-monitor\\x3_module_weekly_plan_gen.py</code>（数据 json 在 scratchpad，重跑查询后再跑本脚本即刷新）。</div>

<script>
const SEGS = {json.dumps(SEGS, ensure_ascii=False)};
const META = {{
  payrate: {{label:"付费玩家付费率", unit:"%", fmt:v=>v.toFixed(1)+"%",
    note:"＝当日<b>节日付费人数 ÷ 当日总付费人数</b>。衡量<b>广度</b>——有多少付费玩家碰到了节日。X3 活跃日中位 {DX['payrate']:.1f}%、P2 {DP['payrate']:.1f}%。<b>9 月要拉的就是这条线。</b>",
    p2med:{DP['payrate']:.2f}, x3med:{DX['payrate']:.2f}}},
  arpu:    {{label:"节日 ARPU", unit:"$", fmt:v=>"$"+v.toFixed(1),
    note:"＝当日<b>节日收入 ÷ 当日总付费人数</b>（分母是全部付费玩家，不是节日付费人数——这是我们的既定口径）。它等于「付费率 × ARPPU」，是占比的直接来源。",
    p2med:null, x3med:null}},
  arppu:   {{label:"节日 ARPPU", unit:"$", fmt:v=>"$"+v.toFixed(1),
    note:"＝当日<b>节日收入 ÷ 当日节日付费人数</b>。衡量<b>深度</b>——碰到节日的人平均掏多少。X3 活跃日中位 ${DX['arppu']:.1f}、P2 ${DP['arppu']:.1f}。<b>10 月要拉的就是这条线。</b>",
    p2med:{DP['arppu']:.2f}, x3med:{DX['arppu']:.2f}}}
}};
const W=980,H=380,PL=58,PR=22,PT=22,PB=48;
const maxDay=Math.max(...SEGS.map(s=>s.pts.length))-1;
// 默认只开「P2 拓荒节」与「X3 夏日恋语」，其余点图例展开
const DEF=["P2 拓荒节","X3 夏日恋语"];
const off={{}}; SEGS.forEach(s=>off[s.name]=DEF.includes(s.name));
const X=i=>PL+i/maxDay*(W-PL-PR);
let curKey="payrate";

function legend(){{
  document.getElementById("legend").innerHTML=SEGS.map(s=>
    `<span style="cursor:pointer;opacity:${{off[s.name]?1:.35}}" data-n="${{s.name}}">
      <i style="background:${{s.color}};border-radius:2px"></i>${{s.name}}
      <span style="color:var(--dim2)">（${{s.n}}天 · $${{s.rev.toLocaleString()}}）</span></span>`).join("");
  document.querySelectorAll("#legend span[data-n]").forEach(el=>
    el.addEventListener("click",()=>{{ off[el.dataset.n]=!off[el.dataset.n]; legend(); draw(curKey); }}));
}}

function draw(key){{
  curKey=key;
  const m=META[key];
  const vis=SEGS.filter(s=>off[s.name]);
  const all=vis.flatMap(s=>s.pts.map(p=>p[key]));
  const top=(Math.max(...all, m.p2med||0, 1))*1.12;
  const Y=v=>H-PB-(v/top)*(H-PB-PT);
  let s=`<svg viewBox="0 0 ${{W}} ${{H}}" width="100%">`;
  for(let i=0;i<=5;i++){{
    const v=top*i/5, y=Y(v);
    s+=`<line x1="${{PL}}" y1="${{y.toFixed(0)}}" x2="${{W-PR}}" y2="${{y.toFixed(0)}}" stroke="#243040"/>`
      +`<text x="${{PL-7}}" y="${{(y+4).toFixed(0)}}" font-size="10" fill="#6b7f95" text-anchor="end">${{m.fmt(v)}}</text>`;
  }}
  for(let i=0;i<=maxDay;i+=(maxDay>20?3:2)){{
    const x=X(i);
    s+=`<line x1="${{x.toFixed(0)}}" y1="${{PT}}" x2="${{x.toFixed(0)}}" y2="${{H-PB}}" stroke="#1c2733"/>`
      +`<text x="${{x.toFixed(0)}}" y="${{H-PB+16}}" font-size="10" fill="#6b7f95" text-anchor="middle">D${{i}}</text>`;
  }}
  if(m.p2med){{
    s+=`<line x1="${{PL}}" y1="${{Y(m.p2med).toFixed(1)}}" x2="${{W-PR}}" y2="${{Y(m.p2med).toFixed(1)}}" stroke="#c084fc" stroke-dasharray="7 4" stroke-width="1.3" opacity=".75"/>`
      +`<text x="${{W-PR-4}}" y="${{(Y(m.p2med)-6).toFixed(0)}}" font-size="10.5" fill="#c084fc" text-anchor="end">P2 活跃日中位 ${{m.fmt(m.p2med)}}</text>`;
  }}
  if(m.x3med){{
    s+=`<line x1="${{PL}}" y1="${{Y(m.x3med).toFixed(1)}}" x2="${{W-PR}}" y2="${{Y(m.x3med).toFixed(1)}}" stroke="#5ad1ff" stroke-dasharray="3 3" stroke-width="1.2" opacity=".6"/>`
      +`<text x="${{PL+4}}" y="${{(Y(m.x3med)-6).toFixed(0)}}" font-size="10.5" fill="#5ad1ff">X3 活跃日中位 ${{m.fmt(m.x3med)}}</text>`;
  }}
  vis.forEach(sg=>{{
    const d=sg.pts.map((p,i)=>(i?"L":"M")+X(p.i).toFixed(1)+" "+Y(p[key]).toFixed(1)).join(" ");
    s+=`<path d="${{d}}" fill="none" stroke="${{sg.color}}" stroke-width="${{sg.w}}"`
      +(sg.dash?` stroke-dasharray="${{sg.dash}}"`:"")+` opacity="${{sg.side==='X3'?1:.9}}"/>`;
    sg.pts.forEach(p=>{{
      s+=`<circle cx="${{X(p.i).toFixed(1)}}" cy="${{Y(p[key]).toFixed(1)}}" r="${{sg.side==='X3'?3:2.4}}" fill="${{sg.color}}">`
        +`<title>${{sg.name}} · D${{p.i}}（${{p.d}}）\\n${{m.label}} ${{m.fmt(p[key])}}\\n节日收入 $${{p.fest.toLocaleString()}} · 占大盘 ${{p.share}}%</title></circle>`;
    }});
  }});
  // ---- 两个月的动作方向：9月横向拉长到 D20，10月纵向抬高 ARPPU ----
  if(maxDay>=20){{
    const x20=X(20), x11=X(11);
    s+=`<line x1="${{x20.toFixed(0)}}" y1="${{PT}}" x2="${{x20.toFixed(0)}}" y2="${{H-PB}}" stroke="#4ade80" stroke-dasharray="5 4" stroke-width="1.5"/>`
      +`<text x="${{(x20-4).toFixed(0)}}" y="${{PT+12}}" font-size="10.5" fill="#4ade80" text-anchor="end">9月目标 D20（21天）</text>`;
    const yArrow=H-PB-16;
    s+=`<line x1="${{x11.toFixed(0)}}" y1="${{yArrow}}" x2="${{(x20-6).toFixed(0)}}" y2="${{yArrow}}" stroke="#4ade80" stroke-width="1.6" marker-end="url(#ar)"/>`
      +`<text x="${{((x11+x20)/2).toFixed(0)}}" y="${{yArrow-6}}" font-size="10.5" fill="#4ade80" text-anchor="middle">9月：把线拉长（夏日只到 D11）</text>`;
  }}
  if(key==="arppu" && m.x3med && m.p2med){{
    const xa=W-PR-150, y1=Y(m.x3med), y2=Y(m.p2med);
    s+=`<line x1="${{xa}}" y1="${{y1.toFixed(1)}}" x2="${{xa}}" y2="${{(y2+7).toFixed(1)}}" stroke="#fbbf24" stroke-width="2" marker-end="url(#ar2)"/>`
      +`<text x="${{xa+8}}" y="${{((y1+y2)/2).toFixed(0)}}" font-size="11" fill="#fbbf24">10月：抬高日均 ARPPU</text>`
      +`<text x="${{xa+8}}" y="${{((y1+y2)/2+14).toFixed(0)}}" font-size="10.5" fill="#fbbf24">${{m.fmt(m.x3med)}} → ${{m.fmt(m.p2med)}}</text>`;
  }}
  s+=`<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#4ade80"/></marker>
      <marker id="ar2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#fbbf24"/></marker></defs>`;
  s+=`<text x="${{W/2}}" y="${{H-6}}" font-size="11" fill="#8fa3b8" text-anchor="middle">节日第 N 天（D0 ＝ 各节日自己的开场日）→</text></svg>`;
  document.getElementById("chart").innerHTML=s;
  document.getElementById("mnote").innerHTML="<b>"+m.label+"</b>　"+m.note;
  document.getElementById("mhint").textContent="点图例可开关曲线 · 悬停看当日数值";
}}
document.querySelectorAll(".tabs .mt").forEach(b=>b.addEventListener("click",()=>{{
  document.querySelectorAll(".tabs .mt").forEach(o=>o.classList.toggle("on",o===b));
  draw(b.dataset.k);
}}));
legend(); draw("payrate");
</script>
</main></body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
tmp = OUT + ".tmp"
open(tmp, "w", encoding="utf-8", newline="").write(html)
os.replace(tmp, OUT)
print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")
