# -*- coding: utf-8 -*-
"""生成「世界杯竞猜 首批4场 iGame 部署清单」HTML(4场×4档=16实例)。可复跑覆盖。"""
import io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base={"RSA":894390,"CAN":894080,"BRA":894070,"JPN":894270,"GER":894210,"PAR":894360,"NED":894320,"MAR":894300}
# 场: (中文对阵, A三码, B三码, 锁盘UTC, 开球北京/ET)
matches=[
 ("🇿🇦南非 vs 🇨🇦加拿大","RSA","CAN","2026-06-28 18:50","北京6/29 03:00 / ET6/28 15:00"),
 ("🇧🇷巴西 vs 🇯🇵日本","BRA","JPN","2026-06-29 16:50","北京6/30 01:00 / ET6/29 13:00"),
 ("🇩🇪德国 vs 🇵🇾巴拉圭","GER","PAR","2026-06-29 20:20","北京6/30 04:30 / ET6/29 16:30"),
 ("🇳🇱荷兰 vs 🇲🇦摩洛哥","NED","MAR","2026-06-30 00:50","北京6/30 09:00 / ET6/29 21:00"),
]
tiers=[("免费","free",0),("$4.99","paid",1),("$9.99","paid",2),("$19.99","paid",3)]
OPEN="2026-06-27 06:30"  # prod 1970 真实时间基准(=13732)
rows=[]; cid=102920
for vs,A,B,lock,ko in matches:
    rows.append(f'<tr class="grp"><td colspan="8">{vs} ｜ {A}(池{base[A]}) vs {B}(池{base[B]}) ｜ 锁盘 {lock} UTC</td></tr>')
    for tn,cls,t in tiers:
        a=base[A]+t; b=base[B]+t
        cp='{"packIdA":%d,"packIdB":%d}'%(a,b)
        rows.append(f'<tr><td>{vs}</td><td class="{cls}">{tn}</td><td class="id">{cid}</td><td class="aname">胜负预言·32强</td><td class="cp">{cp}</td><td class="open">{OPEN}</td><td class="lock">{lock}</td><td>{ko}</td></tr>')
        cid+=1
TR="\n".join(rows)
html=f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<title>世界杯竞猜 · 首批4场 iGame 部署清单(4×4=16)</title>
<style>body{{font-family:"Microsoft YaHei",sans-serif;margin:0;background:#0d1117;color:#e6edf3;padding:24px}}h1{{font-size:22px;margin:0 0 4px}}.sub{{color:#8b949e;font-size:13px;margin-bottom:16px}}.warn{{background:#3d2a00;border:1px solid #9e6a00;border-radius:8px;padding:12px 16px;margin:0 0 12px;color:#ffd479;font-size:13px;line-height:1.7}}.red{{background:#3d0d0d;border:1px solid #b91c1c;border-radius:8px;padding:12px 16px;margin:0 0 14px;color:#ff9b9b;font-size:13px;line-height:1.7}}table{{border-collapse:collapse;width:100%;font-size:12.5px;margin-bottom:18px}}th,td{{border:1px solid #30363d;padding:7px 9px;text-align:left}}th{{background:#161b22;color:#58a6ff}}tr:nth-child(even){{background:#11161d}}.free{{color:#3fb950;font-weight:bold}}.paid{{color:#d29922}}.cp{{font-family:Consolas,monospace;color:#79c0ff}}.id{{font-family:Consolas,monospace;color:#ff7b72}}.aname{{color:#a5d6ff}}.lock{{font-family:Consolas,monospace;color:#ff9b9b;font-weight:bold}}.open{{font-family:Consolas,monospace;color:#7ee787}}.grp{{background:#1f2937;font-weight:bold;color:#fff}}.note{{color:#8b949e;font-size:12px}}b.sv{{color:#d2a8ff}}</style></head><body>
<h1>世界杯竞猜 · 首批 4 场 iGame 部署清单（4 场 × 4 档 = 16 实例）</h1>
<div class="sub">2026 世界杯 1/16(32强) · prod 服 <b class="sv">1970</b> 真实时间基准 · 每场 免费+$4.99+$9.99+$19.99 · 数据已对 live Pack/i18n 验证</div>
<div class="warn">✅ 部署=官方 skill <code>igame-x3-activity-deploy</code> <code>--env prod --file &lt;payload&gt; --no-aggregate</code>，payload 每实例带 <code>customParam</code>(JSON字符串) + acrossServer=0。已 beta 220 全链路验证通过(16/16 deploy=success)。</div>
<div class="red">🔴 <b>锁盘=手动，靠 endTime=开球-10min</b>(锁盘列)。🔴 <b>iGame 网关success≠真部署success</b>，发后读 <code>/ark/activity/list</code> 看 responses.deploy=="success"+activityId 非空。🔴 备注名是旧mock占位勿信，按活动ID+customParam 认。</div>
<table><thead><tr><th>对阵</th><th>档位</th><th>活动ID</th><th>活动名</th><th>customParam</th><th>开启(UTC)</th><th>锁盘/结束(UTC)</th><th>开球(北京/ET)</th></tr></thead>
<tbody>
{TR}
</tbody></table>
<div class="note">活动ID 102920-102935(竞猜池102920-992顺次取)。packId=894000+队号×10+档位(队号FIFA字母序:RSA39/CAN8/BRA7/JPN27/GER21/PAR36/NED32/MAR30；档0免费/1=$4.99/2=$9.99/3=$19.99)。prod开启统一06-27 06:30 UTC(北京14:30·=已上线的免费场13732基准);结束=各场开球-10min。beta测试用同结构、窗口改08-15~09-20(对齐beta时钟)。</div>
</body></html>'''
open("世界杯竞猜_首批4场部署清单.html","w",encoding="utf-8").write(html)
print("WROTE 16-instance HTML")
