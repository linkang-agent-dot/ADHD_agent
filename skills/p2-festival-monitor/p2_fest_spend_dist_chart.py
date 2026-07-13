# -*- coding: utf-8 -*-
"""下钻④双图版：图A=$0-100每$10档(+>$100尾)，图B=$100+每$100档(+>$2k尾)。等距轴+面积图。"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

SC = r'C:\Users\linkang\AppData\Local\Temp\claude\C--Users-linkang\4320db8b-832c-417d-98a5-f5ada22cbf14\scratchpad'
B = json.load(open(SC + r'\p2_buckets2.json', encoding='utf-8'))
D = json.load(open(SC + r'\p2_dist.json', encoding='utf-8'))

SERIES = [
    ("P2春节·异族大富翁(28天)", "#34d399", 0, "P2"),
    ("P2春节·挖孔(28天)",       "#6ee7b7", 0, "P2"),
    ("P2春节·MJ8(28天)",        "#10b981", 0, "P2"),
    ("P2春节·钓鱼(28天)",       "#2dd4bf", 0, "P2"),
    ("P2拓荒·挖孔(29天)",       "#f59e0b", 1, "P2"),
    ("P2拓荒·弹珠GACHA(29天)",  "#a78bfa", 0, "P2"),
    ("P2拓荒·推币机(29天)",     "#c4b5fd", 0, "P2"),
    ("P2深海·猜酒杯(22天)",     "#38bdf8", 1, "P2"),
    ("P2深海·钓鱼(22天)",       "#7dd3fc", 0, "P2"),
    ("P2深海·限时抢购(22天)",   "#818cf8", 0, "P2"),
    ("P2深海·节日大富翁(22天)", "#22d3ee", 0, "P2"),
    ("P2圣诞24·外圈内圈GACHA(12/20-1/3·15天)", "#cbd5e1", 1, "P2"),
    ("X3世界杯·开箱族(6/27起D0-D10)", "#fda4af", 1, "X3"),
    ("X2占星·GACHA(D0-D10)",    "#a3e635", 1, "X2"),
    ("X3深海·大富翁族(D0-D10)",  "#ff9f7a", 0, "X3"),
    ("X3深海·双通行证(D0-D10)",  "#f472b6", 0, "X3"),
    ("X3深海·许愿池单列(D0-D10)","#fbbf24", 0, "X3"),
    ("X3夏日·开箱族(D0-D10全活动)",    "#e879f9", 1, "X3"),
    ("X3深海·转盘(连锁+锚点)(D0-D10)", "#ff6b6b", 1, "X3"),
]

data_js = {}
for k, c, on, grp in SERIES:
    s = B["series"][k]; v = D[k]
    data_js[k] = {"c": c, "on": on, "grp": grp, "a": s["a"], "b": s["b"],
                  "buyers": v["buyers"], "mean": v["mean"], "max": v["max"]}

def row(name):
    v = D[name]; g = dict(zip([round(p*100,1) for p in v["pcts"]], v["q"]))
    x3 = ' style="background:#1d1620"' if name.startswith("X3") else ""
    return (f'<tr{x3}><td>{name}</td><td>{v["buyers"]:,}</td><td>${v["mean"]:,.0f}</td><td>${g[50.0]:,.0f}</td>'
            f'<td>${g[1.0]:,.0f}</td><td>${g[5.0]:,.0f}</td><td>${g[10.0]:,.0f}</td><td>${v["max"]:,.0f}</td></tr>')
tbl = ['<table><tr><th>武器</th><th>买家数</th><th>人均</th><th>中位数</th><th>top1% 付费额</th><th>top5%</th><th>top10%</th><th>最大单人</th></tr>']
for name,_,_,_ in SERIES: tbl.append(row(name))
tbl.append('</table>')

section = r'''<h3>★ 弹药带下钻④：付费档位分布·双图面积版（图A=$0-100每$10一档 · 图B=$100以上每$100一档 · 轴距等宽 · 纵轴=买家占比% · 面积=付费比例分布 · 胶囊选模块 · 右上切换视图）</h3>
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
  <div id="distPills" style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0"></div>
  <div id="distMode" style="display:flex;gap:6px"></div>
</div>
<div style="color:#8892a4;font-size:12px;margin:4px 0">图A · 大众段 $0–100（每 $10 一档，末档「&gt;$100」= 溢出到图B的人）</div>
<div id="distChartA"></div>
<div style="color:#8892a4;font-size:12px;margin:10px 0 4px">图B · 鲸鱼段 $100+（每 $100 一档，纵轴自动放大 · 两图分母同为该模块全部买家）</div>
<div id="distChartB"></div>
__TABLE__
<div class="card"><b>双图读法（分母都是该模块全部买家；图A看大众盘形状，图B看鲸鱼段厚度）：</b>
①<b>图A：$50 以下两边形状几乎一样</b>（X3 甚至 $10-50 段占比更高）——普通买家行为相同；差别在末档「&gt;$100」：P2 各武器有 <b>8~26%</b> 的买家溢出到鲸鱼段，X3 只有 0~14%（D0-D10：转盘族 7.1%、深海开箱 6.6%、夏日开箱 13.9%）；
②<b>图B：P2 的面积从 $100 一路铺到 $2k+</b>（拓荒挖孔 $2k+ 还有 33 人、猜酒杯每个 $100 档都有人住）；<b>X3 的面积在 $500-700 处戛然而止</b>（D0-D10：转盘 $735(含许愿池口径)/纯连锁锚点 $585 / 大富翁族 $707 / 双通行证 $60 / 夏日开箱全活动 $550 / 深海开箱 $585 = 全货架买光——两代节日的开箱/抽奖族撞在同一堵 ~$500-600 的墙上，窗口拉长墙只随限购回填微抬），<b>最肯花钱的玩家被产品拒收</b>；
③P2 人均 $115~$170 vs X3 $35~$48（D0-D10）：人均差 ~80% 来自图B 段的缺人——这就是"逐档连锁+限购5"在档位分布上的形状；
④X3 双通行证全部压在图A（$60 买满即止）、许愿池（唯一可复购）能爬进图B 前两档——<b>天花板是 X3 全系统性问题</b>：所有武器按"买全一轮"设计，没有为 top1% 准备无限深度；
<br><b>直接结论</b>：X3 只要给头部 1%（每周约 15 个鲸鱼）一个 $1,000+ 的可花空间（顶档复购 30 次起/随机高档无限购），按 P2 猜酒杯图B 的形状回填 $200-2k 段，仅鲸鱼段就 ≈ $15-20k/周。⚠️ 口径注：X3 已更至 D0-D10（深海系=7/3-7/13·59服，7/13 为进行中/数仓可能 T+1 不完整；夏日开箱=5/29-6/8 全活动·批1 88服=情人节复用连锁210702-710双号+券锚点210712-15；深海无开箱活动(ActvType15仅元旦/情人/春节/酒馆/世界杯)——"转盘纯付费面"=转盘101025的连锁+藏宝图锚点、不含许愿池,与夏日开箱同结构对比用）vs P2 全活动 22-29 天；X2占星·GACHA=2026-05-12~05-21（D0-D10·18服部署14服有售·固定2013910064-68+随机2013910070-74 十档）；P2圣诞24·外圈内圈GACHA=2024圣诞节GACHA固定5档+随机3档（2024-12-20~2025-01-03·15天·总盘$22.2万）；X3世界杯·开箱族=福箱连锁付费211002-10双号+券锚点211012-15（6/27福箱上线起11天·98服1000-1970）；窗口拉长后 X3 天花板略抬（转盘族 max $735=许愿池复购+连锁限购随天数回填），但仍在 $500-700 量级，图B 断崖结论不变。</div>
<script>
const ALBL = __ALBL__;
const BLBL = __BLBL__;
const DIST = __DATA__;
let DMODE = 'pct';
(function(){
  function vals(arr, tot){
    if(DMODE==='pct') return arr.map(c=>c/tot*100);
    const out=[];let acc=0;
    for(let i=arr.length-1;i>=0;i--){acc+=arr[i];out[i]=acc/tot*100;}
    return out;
  }
  function drawOne(elId, labels, key, labelEvery){
    const W=1040,H=380,ML=56,MR=20,MT=14,MB=50,PW=W-ML-MR,PH=H-MT-MB;
    const N=labels.length;
    const xp=i=>ML+(i+0.5)/N*PW;
    let ymax=5;
    for(const v of Object.values(DIST)) if(v.on){
      const tot=v.a.reduce((x,y)=>x+y,0)+ (key==='b'?0:0);
      const total=v.a.reduce((x,y)=>x+y,0);      // a 含 >100 尾=全部买家
      ymax=Math.max(ymax,...vals(v[key], total));
    }
    ymax=Math.min(100,Math.ceil(ymax/5)*5);
    const yp=p=>MT+(1-p/ymax)*PH;
    let s=[`<svg viewBox="0 0 ${W} ${H}" style="width:100%;background:#10141f;border:1px solid #232c42;border-radius:10px">`];
    const step=ymax>50?10:(ymax>20?5:(ymax>8?2:1));
    for(let g=0;g<=ymax;g+=step){const y=yp(g);
      s.push(`<line x1="${ML}" y1="${y}" x2="${W-MR}" y2="${y}" stroke="#1d2536"/>`);
      s.push(`<text x="${ML-8}" y="${y+4}" fill="#5c677d" font-size="11" text-anchor="end">${g}%</text>`);}
    labels.forEach((b,i)=>{
      s.push(`<line x1="${ML+i/N*PW}" y1="${MT}" x2="${ML+i/N*PW}" y2="${H-MB}" stroke="#181f2e"/>`);
      if(i%labelEvery===0||i===N-1) s.push(`<text x="${xp(i)}" y="${H-MB+16}" fill="#8892a4" font-size="10" text-anchor="middle" font-weight="600">${b}</text>`);});
    s.push(`<text x="${(ML+W-MR)/2}" y="${H-8}" fill="#8892a4" font-size="12" text-anchor="middle">单人在该武器的总付费</text>`);
    let ly2=MT+8;
    for(const [k,v] of Object.entries(DIST)){
      if(!v.on) continue;
      const total=v.a.reduce((x,y)=>x+y,0);
      const ys=vals(v[key], total);
      const wd=v.grp==='X3'?2.6:1.6;
      const y0=yp(0);
      let dp=`M ${xp(0).toFixed(1)} ${y0.toFixed(1)} `;
      ys.forEach((p,i)=>{dp+=`L ${xp(i).toFixed(1)} ${yp(p).toFixed(1)} `;});
      dp+=`L ${xp(ys.length-1).toFixed(1)} ${y0.toFixed(1)} Z`;
      s.push(`<path d="${dp}" fill="${v.c}" fill-opacity="${v.grp==='X3'?0.30:0.20}" stroke="${v.c}" stroke-width="${wd}"/>`);
      ys.forEach((p,i)=>{if(v[key][i]>0)s.push(`<circle cx="${xp(i).toFixed(1)}" cy="${yp(p).toFixed(1)}" r="${v.grp==='X3'?3:2.2}" fill="${v.c}"/>`);});
      s.push(`<line x1="${W-MR-320}" y1="${ly2}" x2="${W-MR-296}" y2="${ly2}" stroke="${v.c}" stroke-width="${wd}"/>`);
      s.push(`<text x="${W-MR-290}" y="${ly2+4}" fill="#c4ccd5" font-size="11">${k}（${v.buyers}人 · 人均$${Math.round(v.mean)} · max$${Math.round(v.max)}）</text>`);
      ly2+=16;
    }
    s.push('</svg>');
    document.getElementById(elId).innerHTML=s.join('');
  }
  function draw(){
    drawOne('distChartA', ALBL, 'a', 1);
    drawOne('distChartB', BLBL, 'b', 2);
  }
  const pills=document.getElementById('distPills');
  for(const [k,v] of Object.entries(DIST)){
    const b=document.createElement('span');
    b.textContent=k.replace(/\(.*?\)/,'');
    b.style.cssText=`cursor:pointer;font-size:11.5px;padding:3px 10px;border-radius:12px;border:1px solid ${v.c};user-select:none`;
    const paint=()=>{b.style.background=v.on?v.c:'transparent';b.style.color=v.on?'#10141a':v.c;b.style.fontWeight=v.on?'700':'400';};
    paint();
    b.onclick=()=>{v.on=!v.on;paint();draw();};
    pills.appendChild(b);
  }
  const modes=[['pct','该档占比'],['cum','累计≥该档']];
  const mdiv=document.getElementById('distMode');
  modes.forEach(([m,label])=>{
    const b=document.createElement('span');
    b.textContent=label;
    b.style.cssText='cursor:pointer;font-size:12px;padding:4px 12px;border-radius:8px;border:1px solid #3a4a66;user-select:none';
    const paint=()=>{const on=DMODE===m;b.style.background=on?'#3a4a66':'transparent';b.style.color=on?'#e2e8f0':'#8892a4';b.style.fontWeight=on?'700':'400';};
    b.onclick=()=>{DMODE=m;mdiv.querySelectorAll('span').forEach((x,i)=>{const on=modes[i][0]===DMODE;x.style.background=on?'#3a4a66':'transparent';x.style.color=on?'#e2e8f0':'#8892a4';x.style.fontWeight=on?'700':'400';});draw();};
    mdiv.appendChild(b);paint();
  });
  draw();
})();
</script>
'''
section = (section.replace("__DATA__", json.dumps(data_js, ensure_ascii=False))
                  .replace("__ALBL__", json.dumps(B["a_labels"], ensure_ascii=False))
                  .replace("__BLBL__", json.dumps(B["b_labels"], ensure_ascii=False))
                  .replace("__TABLE__", "".join(tbl)))

path = r'C:\ADHD_agent\KB\产出-数据分析\X3vsP2_节日付费结构对比\P2三大节拉通_X3动作优先级_20260709.html'
html = open(path, encoding='utf-8').read()
start = html.index('<h3>★ 弹药带下钻④')
end = html.index('<h3>常青线（每节必上、数字极稳）</h3>')
html = html[:start] + section + html[end:]
open(path, 'w', encoding='utf-8').write(html)
print("replaced, chars:", len(section))
