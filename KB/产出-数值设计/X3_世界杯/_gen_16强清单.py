# -*- coding: utf-8 -*-
import io,sys,datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
ZH={"ALG":"阿尔及利亚","ARG":"阿根廷","AUS":"澳大利亚","AUT":"奥地利","BEL":"比利时","BIH":"波黑","BRA":"巴西","CAN":"加拿大","CIV":"科特迪瓦","COD":"刚果金","COL":"哥伦比亚","CPV":"佛得角","CRO":"克罗地亚","CUW":"库拉索","CZE":"捷克","ECU":"厄瓜多尔","EGY":"埃及","ENG":"英格兰","ESP":"西班牙","FRA":"法国","GER":"德国","GHA":"加纳","HAI":"海地","IRN":"伊朗","IRQ":"伊拉克","JOR":"约旦","JPN":"日本","KOR":"韩国","KSA":"沙特","MAR":"摩洛哥","MEX":"墨西哥","NED":"荷兰","NOR":"挪威","NZL":"新西兰","PAN":"巴拿马","PAR":"巴拉圭","POR":"葡萄牙","QAT":"卡塔尔","RSA":"南非","SCO":"苏格兰","SEN":"塞内加尔","SUI":"瑞士","SWE":"瑞典","TUN":"突尼斯","TUR":"土耳其","URU":"乌拉圭","USA":"美国","UZB":"乌兹别克斯坦"}
CODES=sorted(ZH.keys())
def base(c): return 894000+(CODES.index(c)+1)*10
def bj(u): return (u+datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')
def lk(u): return (u-datetime.timedelta(minutes=10))  # 锁盘=开球-10min
TIER=["免费","$4.99","$9.99","$19.99"]
# 8场R16(ESPN);TBD用None标;kickoff UTC
M=[("CAN","MAR",datetime.datetime(2026,7,4,17,0),None),
   ("PAR","FRA",datetime.datetime(2026,7,4,21,0),None),
   ("BRA","NOR",datetime.datetime(2026,7,5,20,0),None),
   ("MEX","ENG",datetime.datetime(2026,7,6,0,0),None),
   ("POR","ESP",datetime.datetime(2026,7,6,19,0),None),
   ("USA","BEL",datetime.datetime(2026,7,7,0,0),None),
   (None,None,datetime.datetime(2026,7,7,16,0),"R32-14胜(澳/埃) vs R32-16胜(哥/加)"),
   ("SUI",None,datetime.datetime(2026,7,7,20,0),"瑞士 vs R32-15胜(阿/佛)")]
rows=""
for i,(a,b,ko,tbd) in enumerate(M):
    c0=102920+i*4
    if tbd:
        vs=f'<b class=tbd>🔶 {tbd}</b>'; cp='<span class=mut>待R32(7/4)定队后填</span>'
    else:
        vs=f'{ZH[a]} <span class=mut>vs</span> {ZH[b]}'
        cp=' / '.join(f'{TIER[t]}:<code>{{"packIdA":{base(a)+t},"packIdB":{base(b)+t}}}</code>' for t in range(4))
    rows+=f'<tr><td>M{i+1}</td><td>{vs}</td><td>{bj(ko)}<br><span class=mut>{ko.strftime("%m-%d %H:%M")}Z</span></td><td>{bj(lk(ko))}<br><span class=mut>{lk(ko).strftime("%m-%d %H:%M")}Z</span></td><td><code>{c0}-{c0+3}</code></td><td class=cp>{cp}</td></tr>\n'
html=f'''<style>
body{{font-family:"Microsoft YaHei",sans-serif;background:#f7fafc;color:#1a202c;max-width:1200px;margin:0 auto;padding:22px;line-height:1.5}}
h1{{font-size:22px;margin:0 0 4px}} .sub{{color:#718096;font-size:13px;margin-bottom:16px}}
h2{{font-size:17px;border-left:5px solid #2b6cb0;padding-left:9px;color:#2b6cb0;margin:22px 0 10px}}
table{{border-collapse:collapse;width:100%;font-size:12.5px}} th,td{{border:1px solid #e2e8f0;padding:6px 8px;text-align:left;vertical-align:top}}
th{{background:#edf2f7}} code{{background:#edf2f7;padding:1px 4px;border-radius:3px;font-size:11px;font-family:Consolas}}
.mut{{color:#a0aec0;font-size:11px}} .tbd{{color:#c05621}} .cp{{font-size:10.5px;line-height:1.7}}
.card{{background:#fff;border:1px solid #e2e8f0;border-radius:9px;padding:13px 15px;margin:12px 0}}
.warn{{background:#fffaf0;border:1px solid #f6ad55;border-radius:8px;padding:10px 13px;font-size:13px;margin:10px 0}}
ul{{margin:5px 0;padding-left:20px}} li{{margin:3px 0;font-size:13px}} b.ok{{color:#2f855a}}
</style>
<h1>世界杯 16 强竞猜 · 部署清单</h1>
<div class=sub>生成 {datetime.datetime.utcnow().strftime('%Y-%m-%d')} ｜ 8 场(6定+2待R32) ｜ cfg 复用 R32 池 102920-102951 ｜ 结盘=开球-10min</div>

<h2>① 8 场对阵 + cfg + customParam</h2>
<table><tr><th>场</th><th>对阵</th><th>开球(北京/UTC)</th><th>结盘(北京/UTC)</th><th>cfg(4档)</th><th>customParam(队礼包)</th></tr>
{rows}</table>
<div class=warn>🔶 <b>M7/M8 待定</b>：等 R32 剩余 3 场(澳埃/阿佛/哥加·7/4)打完→队伍确定→填 customParam。其余 6 场对阵已定可先配。</div>

<h2>② 部署机制</h2>
<div class=card><ul>
<li><b>cfg 复用</b>：16 强复用 R32 池 <code>102920-102951</code>(场序1-8×4档)。<b>先撤回打完的 R32 竞猜实例</b>(它们占着这些 cfg)→改 <code>wc_dashboard_data.json</code> schedule 为 16 强对阵→重跑部署器(double-check 防撞)。</li>
<li><b>老服(55)</b>：<code>python deploy_wc.py &lt;场序&gt; prod --go</code> ｜ <b>新服(28·1980-2250)</b>：<code>python deploy_wc_newservers.py &lt;场序&gt; prod --go</code>。两器同 wc_dashboard_data.json。</li>
<li><b>档位</b>：清单按 R32 一致的 <b>4 档(免费/4.99/9.99/19.99)</b>出。⚠️设计甘特里 16 强曾规划"双档焦点战"——<b>要 4 档还是双档你定</b>，双档我删掉免费+某档重出。</li>
<li><b>结盘</b>：每场 endTime=开球-10min(靠 iGame 时间窗手动锁,无自动机制)。</li>
</ul></div>

<div class=warn>⚠️ <b>时间紧</b>：M1(加摩)开球 7/4 17:00Z=<b>北京 7/5 01:00</b>，而 R32 seq14-16 也是 7/4——16 强首场跟 R32 末场几乎连着。6 场已定的建议 <b>7/4 白天先上</b>，M7/M8 等 R32 结果补。</div>
'''
open('世界杯16强竞猜_部署清单.html','w',encoding='utf-8').write(html)
print('已生成 世界杯16强竞猜_部署清单.html')
