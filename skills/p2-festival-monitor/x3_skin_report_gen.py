# -*- coding: utf-8 -*-
"""把 x3_skin_ownership.json 渲染成「英雄皮肤分层 × 获取率」HTML 报告。

先跑 x3_skin_ownership.py 生成 json，再跑本脚本。
产出：KB\产出-数值设计\X3_8-10月节日需求\英雄皮肤分层与获取率.html
"""
import json, os, sys, math, base64, subprocess, shutil, hashlib, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\ADHD_agent\KB\产出-数值设计\X3_8-10月节日需求\英雄皮肤分层与获取率.html"
ART = r"C:\x3-project\client\Assets\Res\UI\Spirits\Role"
CACHE = os.path.join(HERE, ".skin_img_cache")

# ---- 皮肤图：客户端资源命名 Role_C_<英雄短号>_Skin<nn>.png（大小写不统一，需忽略大小写）----
#   英雄短号 = heroId - 1000；皮肤序号 = skin_id 去掉 heroId 前缀后补零两位
#   优先级：专属英雄卡 → 专属头像 → 本体英雄卡（标注"无专属卡"）
def build_art_index():
    idx = {}
    for sub in ("HeroCard", "Character Portraits"):
        for p in glob.glob(os.path.join(ART, sub, "*.png")):
            idx[os.path.basename(p).lower()] = p
    return idx


ART_IDX = build_art_index()


def find_art(skin_id, hero_id):
    if not hero_id.isdigit():
        return None, ""
    short = str(int(hero_id) - 1000)
    suffix = skin_id[len(hero_id):] or "1"
    nn = suffix.zfill(2)
    for pat, kind in ((f"role_c_{short}_skin{nn}.png", "card"),
                      (f"img_c_h_{short}_skin{nn}.png", "portrait"),
                      (f"role_c_{short}.png", "base")):
        if pat in ART_IDX:
            return ART_IDX[pat], kind
    return None, ""


def img_data_uri(path, height=300):
    """转 WebP 内嵌（原 PNG 太大）。缓存按 路径+尺寸+mtime。"""
    if not path:
        return ""
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.md5(f"{path}|{height}|{os.path.getmtime(path)}".encode()).hexdigest()[:16]
    out = os.path.join(CACHE, key + ".webp")
    if not os.path.exists(out):
        if not shutil.which("ffmpeg"):
            return ""
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", path,
                            "-vf", f"scale=-1:{height}", "-q:v", "80", out, "-y"],
                           capture_output=True)
        if r.returncode != 0 or not os.path.exists(out):
            return ""
    return "data:image/webp;base64," + base64.b64encode(open(out, "rb").read()).decode()

d = json.load(open(os.path.join(HERE, "x3_skin_ownership.json"), encoding="utf-8"))
skins = d["skins"]
seg = d["segment"]

TIER_ORDER = ["至尊", "传说", "史诗", "限定", "1周年", "夏日", "黑金", ""]
TIER_COLOR = {"至尊": "#f87171", "传说": "#c084fc", "史诗": "#5ad1ff",
              "限定": "#fbbf24", "1周年": "#4ade80", "夏日": "#2dd4bf",
              "黑金": "#a3a3a3", "": "#64748b"}
TIER_NAME = {"": "无标签"}


def pct(v):
    if v is None:
        return "—"
    return f"{v:.1f}%" if v < 100 else f"<b style='color:#f87171'>{v:.0f}%</b>"


def hero_of(name):
    return name.split("·")[-1] if "·" in name else (name or "?")


# ---- 分层聚合 ----
tiers = {}
for s in skins:
    t = s["tag"]
    tiers.setdefault(t, []).append(s)

tier_rows = []
for t in TIER_ORDER:
    if t not in tiers:
        continue
    g = tiers[t]
    valid = [x for x in g if x["rate"] is not None and x["rate"] <= 100]
    avg = sum(x["rate"] for x in valid) / len(valid) if valid else 0
    tot = sum(x["owners"] for x in g)
    zero = sum(1 for x in g if x["owners"] == 0)
    props = {x["prop_num"] for x in g if x["prop_num"].isdigit() and int(x["prop_num"]) >= 100}
    pr = "/".join(f"+{int(p)//100}%" for p in sorted(props, key=lambda z: -int(z))) or "—"
    tier_rows.append((TIER_NAME.get(t, t), len(g), tot, avg, zero, pr))

max_avg = max((r[3] for r in tier_rows), default=1) or 1

# ---- 散点图：X=英雄持有(log10) Y=获取率(log) ----
pts = [s for s in skins if s["hero_owners"] > 0 and s["owners"] > 0]
W, H, PAD = 980, 440, 62
xs = [math.log10(max(s["hero_owners"], 1)) for s in pts]
ys = [math.log10(max(s["rate"], 0.01)) for s in pts]
x0, x1 = min(xs) - .3, max(xs) + .3
y0, y1 = min(ys) - .3, max(ys) + .3


def sx(v): return PAD + (v - x0) / (x1 - x0) * (W - PAD - 30)
def sy(v): return H - PAD - (v - y0) / (y1 - y0) * (H - PAD - 30)


dots = []
for s in pts:
    cx, cy = sx(math.log10(s["hero_owners"])), sy(math.log10(max(s["rate"], .01)))
    r = max(3.5, min(17, math.sqrt(s["owners"]) / 7))
    c = TIER_COLOR.get(s["tag"], "#64748b")
    op = .95 if s["tag"] else .5
    dots.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{c}" fill-opacity="{op}" '
        f'stroke="{c}" stroke-width="1.2"><title>{s["name"]}｜{s["tag"] or "无标签"}\n'
        f'获取 {s["owners"]:,} 人 / 解锁英雄 {s["hero_owners"]:,} 人 = {s["rate"]:.2f}%</title></circle>')

# 标注几个关键点
LABELS = {"红绸剑姬·阿米娜": (8, -10), "海上女王·阿米娜": (8, 14), "初妆·鲁比": (-96, -8),
          "传奇女仆·贝拉": (-104, -6), "月影华裳·霍普金斯": (8, -8), "笑迎春·茉莉": (8, 12)}
for s in pts:
    if s["name"] in LABELS:
        dx, dy = LABELS[s["name"]]
        cx, cy = sx(math.log10(s["hero_owners"])), sy(math.log10(max(s["rate"], .01)))
        dots.append(f'<text x="{cx+dx:.0f}" y="{cy+dy:.0f}" font-size="10.5" fill="#c9d6e4">{s["name"]}</text>')

gx = []
for e in range(int(x0), int(x1) + 1):
    if x0 <= e <= x1:
        X = sx(e)
        gx.append(f'<line x1="{X:.0f}" y1="{PAD-26}" x2="{X:.0f}" y2="{H-PAD}" stroke="#243040"/>'
                  f'<text x="{X:.0f}" y="{H-PAD+16}" font-size="10.5" fill="#6b7f95" text-anchor="middle">'
                  f'{10**e:,.0f}</text>')
gy = []
for e in range(int(y0), int(y1) + 1):
    if y0 <= e <= y1:
        Y = sy(e)
        v = 10.0 ** e
        lbl = f"{v:.2f}%" if v < 1 else f"{v:.0f}%"
        gy.append(f'<line x1="{PAD}" y1="{Y:.0f}" x2="{W-30}" y2="{Y:.0f}" stroke="#243040"/>'
                  f'<text x="{PAD-8}" y="{Y+4:.0f}" font-size="10.5" fill="#6b7f95" text-anchor="end">{lbl}</text>')

# ---- 皮肤图卡（按分层分组，组内按获取人数降序）----
for s in skins:
    p, kind = find_art(s["skin_id"], s["hero_id"])
    s["art_path"], s["art_kind"] = p, kind
    s["art"] = img_data_uri(p)

n_own_art = sum(1 for s in skins if s["art_kind"] in ("card", "portrait"))
n_no_art = sum(1 for s in skins if not s["art"])

gallery = []
for t in TIER_ORDER:
    if t not in tiers:
        continue
    g = sorted(tiers[t], key=lambda x: -x["owners"])
    c = TIER_COLOR.get(t, "#64748b")
    label = TIER_NAME.get(t, t) if t else "无标签"
    props = {x["prop_num"] for x in g if x["prop_num"].isdigit() and int(x["prop_num"]) >= 100}
    pr = "/".join(f"+{int(p)//100}%" for p in sorted(props, key=lambda z: -int(z))) or "无属性"
    gallery.append(f'<h3 class="gh"><span class="tag" style="color:{c};border-color:{c}66;'
                   f'background:{c}18">{label}</span> <span class="ghn">{len(g)} 款 · {pr}</span></h3>'
                   f'<div class="grid">')
    for s in g:
        rate = "—" if s["rate"] is None else (f"{s['rate']:.1f}%" if s["rate"] <= 100 else f"{s['rate']:.0f}%")
        bad = "hi" if (s["rate"] is not None and s["rate"] > 100) or s["hero_owners"] == 0 else ""
        zero = "zero" if s["owners"] == 0 else ""
        art = (f'<img src="{s["art"]}" alt="{s["name"]}" loading="lazy">' if s["art"]
               else '<div class="noart">无美术资产</div>')
        badge = ""
        if s["art_kind"] == "base":
            badge = '<span class="ab">无专属卡</span>'
        elif s["art_kind"] == "portrait":
            badge = '<span class="ab">仅头像</span>'
        pn = s["prop_num"]
        prop = f"+{int(pn)//100}%" if pn.isdigit() and int(pn) >= 100 else ""
        gallery.append(
            f'<figure class="card {bad} {zero}"><div class="ph">{art}{badge}'
            f'{"<span class=zt>0 人持有</span>" if s["owners"]==0 else ""}</div>'
            f'<figcaption><div class="nm">{s["name"] or s["skin_id"]}</div>'
            f'<div class="mt"><b style="color:{c}">{s["owners"]:,}</b> 人 · 获取率 {rate}'
            f'{" · " + prop if prop else ""}</div>'
            f'<div class="mt2">英雄 {hero_of(s["name"])} 解锁 {s["hero_owners"]:,} 人</div>'
            f'</figcaption></figure>')
    gallery.append("</div>")

# ---- 全表 ----
rows = []
for s in sorted(skins, key=lambda x: -x["owners"]):
    c = TIER_COLOR.get(s["tag"], "#64748b")
    tag = (f'<span class="tag" style="color:{c};border-color:{c}55;background:{c}18">'
           f'{s["tag"] or "无"}</span>')
    pn = s["prop_num"]
    prop = f"+{int(pn)//100}%" if pn.isdigit() and int(pn) >= 100 else ("—" if not pn.isdigit() else f"+{int(pn)/100:.0f}%")
    warn = ' class="warn"' if (s["rate"] is not None and s["rate"] > 100) or s["hero_owners"] == 0 else ""
    rows.append(f'<tr{warn}><td>{s["skin_id"]}</td><td>{tag}</td><td>{s["name"] or "—"}</td>'
                f'<td class="n">{hero_of(s["name"])}</td>'
                f'<td class="n">{s["owners"]:,}</td><td class="n">{s["hero_owners"]:,}</td>'
                f'<td class="n">{pct(s["rate"])}</td><td class="n">{prop}</td></tr>')

n_tag = sum(1 for s in skins if s["tag"])
n_zero = sum(1 for s in skins if s["owners"] == 0)
top = max(skins, key=lambda s: s["rate"] if s["rate"] and s["rate"] <= 100 else -1)

html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>X3 英雄皮肤分层 × 获取率</title><style>
:root{{--bg:#0d1117;--panel:#141b24;--panel2:#1a232e;--line:#243040;--fg:#e8f0f8;
--dim:#8fa3b8;--dim2:#6b7f95;--acc:#5ad1ff;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171}}
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
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:12px;margin:18px 0}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:13px 15px;border-top:2px solid var(--acc)}}
.kpi.bad{{border-top-color:var(--bad)}}.kpi.ok{{border-top-color:var(--ok)}}
.kpi b{{display:block;font-size:25px;line-height:1.25}}.kpi .t{{font-size:12px;color:var(--dim)}}
.kpi .n{{font-size:11px;color:var(--dim2);margin-top:4px}}
h2{{font-size:18px;margin:40px 0 4px}}h2 .no{{display:inline-block;background:var(--acc);color:#06202b;
font-size:12px;font-weight:700;border-radius:4px;padding:1px 8px;margin-right:9px;vertical-align:2px}}
h2+.lead{{color:var(--dim);margin:0 0 14px;font-size:13px}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:12.5px;background:var(--panel)}}
th,td{{border:1px solid var(--line);padding:6px 10px;text-align:left}}
th{{background:var(--panel2);color:var(--dim);font-size:11.5px;white-space:nowrap}}
td.n{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
tr:hover td{{background:rgba(90,209,255,.04)}}
tr.warn td{{background:rgba(248,113,113,.07)}}
.tag{{display:inline-block;font-size:10.5px;padding:0 7px;border-radius:3px;border:1px solid}}
.bar{{height:15px;border-radius:3px;display:inline-block;vertical-align:-2px}}
.note{{background:var(--panel2);border:1px solid var(--line);border-left:3px solid var(--dim2);
border-radius:5px;padding:11px 15px;font-size:12.5px;color:var(--dim);margin:14px 0}}
.note b{{color:var(--fg)}}.note.bad{{border-left-color:var(--bad)}}.note.ok{{border-left-color:var(--ok)}}
svg{{background:var(--panel);border:1px solid var(--line);border-radius:6px}}
.lg{{display:flex;gap:14px;flex-wrap:wrap;font-size:11.5px;color:var(--dim);margin:8px 0}}
.lg i{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}}
/* 皮肤图卡 */
.gh{{font-size:14px;margin:26px 0 10px;display:flex;align-items:center;gap:10px}}
.ghn{{color:var(--dim2);font-size:12px;font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:14px}}
.card{{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:7px;
overflow:hidden;transition:.2s}}
.card:hover{{border-color:var(--acc);transform:translateY(-3px);box-shadow:0 10px 24px rgba(0,0,0,.5)}}
.card.hi{{border-color:#f8717166;background:rgba(248,113,113,.05)}}
.card.zero{{opacity:.62;filter:grayscale(.5)}}
.card.zero:hover{{opacity:1;filter:none}}
.ph{{position:relative;height:212px;background:#0a0f15;display:flex;align-items:center;justify-content:center}}
.ph img{{max-width:100%;max-height:100%;object-fit:contain;display:block}}
.noart{{color:var(--dim2);font-size:12px}}
.ab{{position:absolute;top:6px;left:6px;font-size:10px;padding:1px 6px;border-radius:3px;
background:rgba(0,0,0,.7);border:1px solid var(--line);color:var(--warn)}}
.zt{{position:absolute;bottom:6px;left:6px;font-size:10px;padding:1px 6px;border-radius:3px;
background:rgba(248,113,113,.85);color:#1a0505;font-weight:700}}
figcaption{{padding:8px 10px 10px}}
.nm{{font-size:12.5px;font-weight:600;line-height:1.35}}
.mt{{font-size:11.5px;color:var(--dim);margin-top:3px}}
.mt2{{font-size:11px;color:var(--dim2)}}
</style></head><body><main>

<h1>X3 英雄皮肤 · 分层 × 获取率</h1>
<div class="sub">分层越高，获取率越低——四档属性梯度完全没跑起来</div>
<div class="meta">口径＝<b>获取率 = 皮肤获取人数 / 该英雄解锁人数</b>（曾获得即拥有，外显永久）·
服段 <b>{seg}</b> · 数仓实查 2026-07-29 ·
全表 106 款皮肤中<b>仅 48 款配了获取道具</b>（其余不可单独获取），本页只统计这 48 款</div>

<div class="verdict"><div class="t">VERDICT · 结论先行</div>
<p>① <b>属性梯度对获取率毫无影响</b>：至尊 +150% 的红绸剑姬·阿米娜只有 <b>11 人</b>，而 +1% 的初妆·鲁比有 <b>4,336 人</b>。驱动获取的是<b>发放渠道（免费/低门槛）</b>，不是属性档位——所以"皮肤分品质＋定价拉深度"光加品质层没用，<b>四档梯度早就存在且完全没跑起来</b>。</p>
<p>② <b>英雄持有集中度是被忽略的前置变量</b>：阿米娜 <b>599,305</b> 人解锁，阿什顿只有 <b>37</b> 人——<b>差 16,000 倍</b>。而阿米娜身上两款皮肤合计仅 675 人，<b>X3 最大的皮肤市场基本没开发</b>。<b>给谁做皮肤，要先看英雄持有量。</b></p>
<p>③ <b>3 款皮肤零持有</b>（黑金契约·霍普金斯 / 金海商使·霍普金斯 / 魅影魔术师·琥珀），另有 4 款获取率 >100%＋2 款英雄 0 人却有人持皮——<b>皮肤被当活动奖励发给了没有该英雄的玩家</b>（待抽查验证，见文末）。</p>
</div>

<h2 style="margin-top:28px"><span class="no">★</span>分层定位 · 拍板进度</h2>
<p class="lead">2026-07-29 起逐档确定。已定的按此执行，待定的下轮继续。</p>
<table>
<tr><th style="width:78px">档位</th><th style="width:62px">状态</th><th>定位</th><th style="width:210px">现状数据</th></tr>
<tr style="background:rgba(74,222,128,.06)">
  <td><span class="tag" style="color:#5ad1ff;border-color:#5ad1ff55;background:#5ad1ff18">史诗</span></td>
  <td><b style="color:var(--ok)">已定</b></td>
  <td><b>转化钩子，不做纯付费</b>——卖外观为主 · 属性低 · 动画以静态为主 · 价位 <b>$49.99</b> 左右；
      <b>必须挂进某个玩法/功能的「前 50 刀阶段奖励」</b>，靠它把玩家往上推一档。<br>
      <span style="color:var(--dim2)">依据：当纯付费卖 = 把有美术成本的资产锁进 1% 的人手里；P2 圣诞三层的第一层（2 天试用钩子）拉了 17,222 人，本就不是拿来卖的。</span></td>
  <td>4 款 · 获取率 <b>0.4%–1.1%</b><br><span style="color:var(--dim2)">705 / 665 / 119 / <b style="color:var(--bad)">0</b> 人</span></td></tr>
<tr><td><span class="tag" style="color:#f87171;border-color:#f8717155;background:#f8717118">至尊</span></td>
  <td><span style="color:var(--warn)">待定</span></td>
  <td>顶层给谁？现在是"卖"还是"榜奖"？<span style="color:var(--dim2)">P2 对位＝跨服榜 30 份 + Top3 染色，上榜线 $1,444 / 中位 $2,529——冲榜消耗无上限，正好绕开货架 $590 封顶</span></td>
  <td>2 款 · 各 <b>11 人</b> · +150%</td></tr>
<tr><td><span class="tag" style="color:#c084fc;border-color:#c084fc55;background:#c084fc18">传说</span></td>
  <td><span style="color:var(--warn)">待定</span></td>
  <td>史诗当钩子之后，传说是否接<b>主力付费层</b>？<span style="color:var(--dim2)">P2 对位＝本体永久皮中位 $517，132 人贡献总盘 64.9%</span></td>
  <td>4 款 · 5–154 人 · +100%</td></tr>
<tr><td><span class="tag" style="color:#fbbf24;border-color:#fbbf2455;background:#fbbf2418">限定</span></td>
  <td><span style="color:var(--warn)">待定</span></td>
  <td>+30% 梯度低于史诗、名字却更稀缺，<b>这层要不要保留</b></td>
  <td>2 款 · 21 / 188 人 · +30%</td></tr>
<tr><td><span class="tag" style="color:#64748b;border-color:#64748b55;background:#64748b18">无标签</span></td>
  <td><span style="color:var(--warn)">待定</span></td>
  <td>事实上的<b>免费触达层</b>（自然形成），要不要正式确立为漏斗第一层</td>
  <td>跑量层 · 最高 <b>4,336 人 / 38.6%</b></td></tr>
</table>
<div class="note bad"><b>拆分层时要一并清掉的两处脏数据：</b>
① <b>23/48 款没有专属英雄卡</b>，列表里显示的还是英雄本体形象——史诗若要当钩子大量投，<b>美术规格必须先定死</b>，钩子不好看反而劝退；
② <b>黑金 +1%、金海商使 +1%</b> 属性等于纯外显却挂着高级标签，属于分层里的脏数据。</div>

<div class="kpis">
<div class="kpi"><b>48</b><div class="t">可获取皮肤款数</div><div class="n">全表 106 款 · 58 款无获取道具</div></div>
<div class="kpi"><b>{n_tag}</b><div class="t">带典藏标签</div><div class="n">其余 {48-n_tag} 款无标签</div></div>
<div class="kpi bad"><b>{n_zero}</b><div class="t">零持有款数</div><div class="n">配了但一个人都没有</div></div>
<div class="kpi ok"><b>{top['rate']:.1f}%</b><div class="t">最高获取率</div><div class="n">{top['name']}（无标签·+1%）</div></div>
</div>

<h2><span class="no">01</span>分层 × 获取率 — 倒挂</h2>
<p class="lead">每档取"获取率 ≤100% 的皮肤"求均值（>100% 的异常款单列在 §03）。</p>
<table><tr><th>典藏标签</th><th>属性档</th><th class="n">款数</th><th class="n">获取总人数</th>
<th class="n">平均获取率</th><th style="width:260px">对比</th><th class="n">零持有</th></tr>
{"".join(f'<tr><td><span class="tag" style="color:{TIER_COLOR.get(t if t!="无标签" else "","#64748b")};border-color:{TIER_COLOR.get(t if t!="无标签" else "","#64748b")}55">{t}</span></td><td>{pr}</td><td class="n">{n}</td><td class="n">{tot:,}</td><td class="n">{avg:.2f}%</td><td><span class="bar" style="width:{max(2,avg/max_avg*250):.0f}px;background:{TIER_COLOR.get(t if t!="无标签" else "","#64748b")}"></span></td><td class="n">{"<b style=color:#f87171>"+str(z)+"</b>" if z else "0"}</td></tr>' for t,n,tot,avg,z,pr in tier_rows)}
</table>
<div class="note bad"><b>倒挂看这里：</b>「无标签」那一档（多为无属性或 +1% 的老皮肤）平均获取率和获取总人数<b>双双碾压所有带标签档位</b>。至尊/传说/1周年这些"最贵最稀有"的层，人数是个位到两位数。</div>

<h2><span class="no">02</span>英雄持有量 × 皮肤获取率</h2>
<p class="lead">横轴＝该英雄解锁人数（对数）· 纵轴＝皮肤获取率（对数）· 气泡大小＝皮肤获取人数 · 颜色＝典藏标签。<b>右下角＝有巨大受众却几乎没人拿到的皮肤，就是待开发的市场。</b></p>
<div class="lg">{"".join(f'<span><i style="background:{TIER_COLOR[t]}"></i>{TIER_NAME.get(t,t) if t else "无标签"}</span>' for t in TIER_ORDER if t in tiers)}</div>
<svg viewBox="0 0 {W} {H}" width="100%">
{"".join(gx)}{"".join(gy)}
<text x="{W//2}" y="{H-14}" font-size="11.5" fill="var(--dim)" text-anchor="middle">英雄解锁人数（对数）→</text>
<text x="16" y="{H//2}" font-size="11.5" fill="#8fa3b8" transform="rotate(-90 16 {H//2})" text-anchor="middle">皮肤获取率（对数）→</text>
{"".join(dots)}
</svg>
<div class="note"><b>怎么读：</b>左上角那几个（阿什顿、克里斯塔尔、斯隆）＝<b>冷门英雄 + 高获取率</b>，皮肤发得比英雄还多，属于投放错位；
右下角的<b>红绸剑姬·阿米娜、海上女王·阿米娜、笑迎春·茉莉</b>＝<b>几十万人持有该英雄，皮肤却只有几百人拿到</b>——这里才是没开发的市场。</div>

<h2><span class="no">03</span>逐款过图 · 按分层分组</h2>
<p class="lead">组内按获取人数降序。图＝客户端实际资产（专属英雄卡优先，没有则退到头像/本体卡并标注）。
<b>48 款里只有 {n_own_art} 款有专属美术资产</b>，{48-n_own_art} 款是复用本体卡或干脆没有。</p>
{"".join(gallery)}
<div class="note bad"><b>过图时重点看三件事：</b>① 同一档标签下的皮肤，<b>品质/完成度是否配得上它的层级</b>（至尊只有 2 款，值不值这个名）；
② 标「无专属卡」的款＝<b>连专属英雄卡都没出</b>，玩家在列表里看到的还是本体形象；
③ 标红「0 人持有」的三款，<b>美术做了但一个人都没拿到</b>。</div>

<h2><span class="no">04</span>全量清单（48 款 · 按获取人数排序）</h2>
<table><tr><th>皮肤ID</th><th>标签</th><th>皮肤名</th><th class="n">英雄</th>
<th class="n">获取人数</th><th class="n">解锁英雄</th><th class="n">获取率</th><th class="n">属性</th></tr>
{"".join(rows)}
</table>
<div class="note bad"><b>标红行＝需要核实的异常</b>：获取率 >100%（阿什顿两款 500%/478%、克里斯塔尔 216%、斯隆 140%）或英雄解锁数为 0（塞拉菲娜 87 人持皮、维丹蒂亚 44 人持皮）。<br>
最可能的解释是<b>皮肤当活动奖励白送给了没有该英雄的玩家＝投了等于没投</b>；但也不能排除英雄资产口径仍不全。
⏳<b>建议抽查几个 user_id 验证后再定性</b>——我已把英雄的本体与晋升形态（<code>Item_500XX</code> + <code>Item_500XXn</code>）合并去重，分母从 37/2/0 这种异常值修上来过一轮。</div>

<div class="note" style="margin-top:24px"><b>数据来源</b>　<code>v1090.ods_user_asset</code>（change_type='1' 曾获得）· 皮肤＝<code>Item_530xxxx</code> · 英雄＝<code>Item_500XX</code> 及其晋升形态合并去重 · 服段 {seg}。<br>
<b>脚本</b>　查数＝<code>skills\\p2-festival-monitor\\x3_skin_ownership.py</code>（<code>--all-servers</code> 可切全服）· 出页＝同目录 <code>x3_skin_report_gen.py</code>。</div>

</main></body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
tmp = OUT + ".tmp"
open(tmp, "w", encoding="utf-8", newline="").write(html)
os.replace(tmp, OUT)
print(f"wrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB, {len(skins)} skins)")
