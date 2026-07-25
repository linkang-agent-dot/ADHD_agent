# -*- coding: utf-8 -*-
"""传奇永恒(EL)性价比报告生成器 — 数据源: cn.fifaaddict.com (2026-07-24抓取)"""
import json, os, tempfile

SP = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(SP, 'el_scored.json'), encoding='utf-8'))
OUT = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\传奇永恒EL_66人性价比全解_20260724.html'

POS_CN = {'ST':'中锋','CF':'前锋','LW':'左边锋','RW':'右边锋','CAM':'前腰','CM':'中前卫','RM':'右中场','LM':'左中场','CDM':'后腰','CB':'中卫','LB':'左后卫','RB':'右后卫','GK':'门将'}
POS_ORDER = ['ST','CF','LW','RW','CAM','CM','RM','CDM','CB','LB','GK']

rk = [r for r in rows if r.get('cost_perf')]
by_str = sorted(rk, key=lambda x: -x['str_score'])
by_cp = sorted(rk, key=lambda x: -x['cost_perf'])

def wf_badge(w):
    w = int(w)
    cls = 'wf5' if w == 5 else ('wf4' if w == 4 else 'wf3')
    return f'<span class="wf {cls}">{"★"*w}</span>'

def row_html(i, r, key):
    hl = ' class="hl"' if i <= 3 else ''
    return (f'<tr{hl}><td>{i}</td><td class="nm">{r["name"]}</td>'
            f'<td>{POS_CN.get(r["pos1"],r["pos1"])}</td><td>{r["ovr"]}</td>'
            f'<td>{r["速度"]}</td><td>{r["射门"]}</td><td>{r["传球"]}</td><td>{r["盘带"]}</td><td>{r["防守"]}</td><td>{r["强壮"]}</td>'
            f'<td>{wf_badge(r["weakfoot"])}</td><td>{r["height"]}cm·{r["body"]}</td><td>{r["salary"]}</td>'
            f'<td class="sc">{r["str_score"]}</td><td class="sc">{r["cost_perf"]}</td>'
            f'<td class="tr8">{"、".join(r["traits"][:4])}</td></tr>')

TH = ('<tr><th>#</th><th>球员</th><th>位置</th><th>OVR</th>'
      '<th>速度</th><th>射门</th><th>传球</th><th>盘带</th><th>防守</th><th>强壮</th>'
      '<th>逆足</th><th>模型</th><th>薪资</th><th>强度分</th><th>性价比</th><th>金特性</th></tr>')

t_str = '\n'.join(row_html(i, r, 'str') for i, r in enumerate(by_str[:15], 1))
t_cp = '\n'.join(row_html(i, r, 'cp') for i, r in enumerate(by_cp[:15], 1))

pos_sections = []
from collections import defaultdict
bypos = defaultdict(list)
for r in rk:
    bypos[r['pos1']].append(r)
gk = [r for r in rows if r['pos1'] == 'GK']
for pos in POS_ORDER:
    if pos == 'GK':
        if gk:
            g = gk[0]
            pos_sections.append(f'<h3>门将</h3><p>本赛季唯一门将：<b>卡恩(O. Kahn)</b> OVR {g["ovr"]}，{g["height"]}cm。无竞品，需要EL门将就是他。</p>')
        continue
    lst = sorted(bypos.get(pos, []), key=lambda x: -x['str_score'])
    if not lst:
        continue
    trs = '\n'.join(row_html(i, r, 'p') for i, r in enumerate(lst, 1))
    pos_sections.append(f'<h3>{POS_CN[pos]} ({pos})</h3><div class="tw"><table>{TH}{trs}</table></div>')

html = f'''<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>传奇永恒(EL) 66人性价比全解 · 2026-07-24</title>
<style>
body{{font-family:"Microsoft YaHei",sans-serif;margin:0;background:#0f1420;color:#dde3ee;line-height:1.6}}
.wrap{{max-width:1200px;margin:0 auto;padding:24px 16px 60px}}
h1{{font-size:26px;color:#ffd35c;margin:8px 0 2px}}
h2{{font-size:20px;color:#7ec8ff;margin:36px 0 10px;border-left:4px solid #7ec8ff;padding-left:10px}}
h3{{font-size:16px;color:#ffd35c;margin:24px 0 8px}}
.sub{{color:#8b93a7;font-size:13px}}
.card{{background:#171e2e;border:1px solid #263048;border-radius:10px;padding:16px 18px;margin:14px 0}}
.card b{{color:#ffd35c}}
table{{border-collapse:collapse;width:100%;font-size:12.5px;white-space:nowrap}}
th{{background:#1d2740;color:#9fb4d8;padding:6px 8px;position:sticky;top:0}}
td{{padding:5px 8px;border-bottom:1px solid #222c44;text-align:center}}
td.nm{{text-align:left;font-weight:bold;color:#fff}}
td.sc{{color:#ffd35c;font-weight:bold}}
td.tr8{{text-align:left;color:#8b93a7;font-size:11.5px}}
tr.hl td{{background:#20304e}}
.tw{{overflow-x:auto;border:1px solid #263048;border-radius:8px}}
.wf{{font-size:11px}}.wf5{{color:#5cff8f}}.wf4{{color:#ffd35c}}.wf3{{color:#ff7b7b}}
.tag{{display:inline-block;background:#243154;color:#9fc4ff;border-radius:4px;padding:1px 8px;font-size:12px;margin:2px 4px 2px 0}}
.warn{{color:#ff9d5c}}
ol li,ul li{{margin:6px 0}}
.big{{font-size:17px}}
</style></head><body><div class="wrap">
<h1>传奇永恒(EL) 66人性价比全解</h1>
<p class="sub">数据源：cn.fifaaddict.com（2026-07-24 实抓，国服专属赛季 Eternal Legends，共66人）｜评价框架：FCOL阿三资料库（数值 &gt; 模型 &gt; 特性 &gt; 逆足）</p>

<div class="card">
<p class="big"><b>一句话结论：</b>主力级里全场性价比最高的一张卡是 <b>中卫图拉姆(L. Thuram)</b>——135档中卫强度、35低薪、双五、可兼右后卫，一卡顶两位置；进攻端「花得最值」的是 <b>中锋埃托奥(S. Eto'o)</b> 和 <b>左边锋阿扎尔/孙兴慜</b>（130档强度只要35薪、双五）。预算无上限直接上 <b>亨利(ST)+梅西(RW)</b>，这两张是全赛季强度天花板。</p>
</div>

<h2>先说方法（价格口径）</h2>
<div class="card">
<p>EL是国服专属赛季，fifaaddict等数据站<b>没有国服转会市场价格</b>（已实测：66人价格字段全为空）。所以「价」用两层口径替代：</p>
<ol>
<li><b>获取成本</b>：EL卡主要出自扭蛋机/礼盒/转盘，同一卡池内抽取成本一致 → 抽卡决策看<b>强度分</b>（抽到谁最赚）；</li>
<li><b>薪资成本</b>：组队时薪资上限是硬约束，本赛季薪资31~38有区分 → 组队决策看<b>性价比分 = 强度分÷薪资</b>（归一到36薪）。</li>
</ol>
<p>强度分按阿三资料库的位置权重加权六维（如中锋=速度30%+射门30%+盘带20%…），再按KB规则修正：逆足4星-1.5/3星-4（前场）、健硕大高个-2、瘦小高个+1（理想模型）。</p>
</div>

<h2>① 主力强度榜 TOP15（抽卡视角：抽到谁最赚）</h2>
<div class="tw"><table>{TH}
{t_str}
</table></div>

<h2>② 性价比榜 TOP15（组队视角：强度÷薪资）</h2>
<p class="sub warn">⚠️ 该榜偏爱低OVR低薪卡（如因西涅124总评），适合填薪资缺口，不适合当核心。核心位请回到①。</p>
<div class="tw"><table>{TH}
{t_cp}
</table></div>

<h2>③ KB框架下的选购建议</h2>
<div class="card">
<ul>
<li><b>中锋优先（KB：一神带十废，中锋是唯一值得砸预算的位置）</b><br>
封神选择：<b>亨利</b>——速142/射139/盘136，188cm瘦小体型=KB说的「身高达标+瘦弱」理想模型，双五，标准<b>全能跑锋</b>（KB终极追求类型）。<br>
平替（省3薪）：<b>埃托奥</b>——速142双五，强度134.5只要35薪，性价比138.3全ST第一。<br>
情怀顶配：C罗/大罗强度137+，但薪资顶格，性价比排后。</li>
<li><b>边锋</b>：内马尔最强（136.2），但<b>阿扎尔(134.7/35薪)、孙兴慜(133.8/35薪)</b>更值——差1~2点强度省2~3薪，都是双五。</li>
<li><b>中前场</b>：齐达内最强前腰；<b>内德维德(133.1/36薪)</b>=KB球员解析里点名的性价比双五中场，CAM/LM/CM三位置通吃，结论与KB原文互相印证。</li>
<li><b>后场性价比之王：图拉姆</b>——CB/RB双位置135档，35薪双五，性价比140.1是全部主力级(OVR≥130)卡里最高。中卫搭档推荐费迪南德或内斯塔。</li>
<li><b>后腰</b>：维埃拉=里杰卡尔德并列135档（KB：给进攻中场配防守型后腰，正好搭内德维德/齐达内）。卡塞米罗低1档但便宜1薪。</li>
<li><b class="warn">避雷（KB规则）</b>：3逆足直接PASS——佩蒂特、耶罗、基耶利尼3逆（后场影响小可容忍，前场勿碰）；普斯卡什强度榜前列但「健硕+4逆」两项扣分，实战手感会低于面板。</li>
</ul>
</div>

<h2>④ 分位置完整数据（66人全量）</h2>
{''.join(pos_sections)}

<p class="sub">生成：Claude · 2026-07-24 ｜ 原始数据：scratchpad/el_stats.json（fifaaddict SSR抓取66页解析）｜ 强度公式与修正规则见§方法</p>
</div></body></html>'''

tmp = OUT + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, OUT)
print('written', OUT, len(html))
