# -*- coding: utf-8 -*-
"""世界杯竞猜 ActvID → 国家 → 礼包奖励 对照表 HTML。"""
import io, sys, pathlib, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
STAGE = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_activities")
LIVE_RW = r"C:\x3\gdconfig\tsv\Reward__Reward.tsv"
def rows(p): return [l.split('\t') for l in pathlib.Path(p).read_text(encoding='utf-8').split('\n') if l]

# 国家名: code->中文 (从框道具note或PersonalizeCfg)
code2cn={}
for r in rows(r"C:\x3\gdconfig\tsv\Personalize__PersonalizeAvatarFrameCfg.tsv"):
    if len(r)>9 and r[4].startswith("DK_Img_Player_AvatarFrame_WC"):
        code2cn[r[4].replace("DK_Img_Player_AvatarFrame_WC_","")]=r[9].replace("世界杯·","")

# 奖励组 -> [(item,note,num)]
groups={}
for r in rows(STAGE/"Reward_add.tsv"): groups.setdefault(r[1],[]).append((r[3],r[4],r[5]))
for r in rows(LIVE_RW):
    if len(r)>5 and r[1]=="291101": groups.setdefault("291101",[]).append((r[3],r[4],r[5]))

# Pack -> (code, price, content组)
pk={}
for r in rows(STAGE/"Pack_add.tsv"):
    code=r[25].replace("DK_WC_TeamPanel_","")
    pk[r[0]]=dict(code=code, price=r[6], content=r[13], name=r[2])

# manifest -> 实例
ICON={"4.99":"🎫纯竞猜","9.99":"🖼️头像框","19.99":"😀聊天表情"}
recs=[]
for line in pathlib.Path(STAGE/"_manifest.txt").read_text(encoding='utf-8').split('\n'):
    if not line.strip(): continue
    m=re.match(r"(\S+) (\w+)vs(\w+) \$(\S+)\|AO(\d+)\|AP(\d+)\|TC(\d+)\|Pack(\d+)\((\w+)\)/(\d+)\((\w+)\)", line)
    if not m: continue
    rnd,cA,cB,price,ao,ap,tc,pA,_,pB,_=m.groups()
    recs.append(dict(rnd=rnd,price=price,ao=ao,ap=ap,pA=pA,pB=pB,cA=cA,cB=cB))

def reward_html(grp):
    out=[]
    for it,note,num in groups.get(grp,[]):
        cls="cos" if (it.startswith("803") or (it.startswith("157")) or it in("1148","1149")) else ""
        out.append(f'<span class="rw {cls}">{note}×{num}</span>')
    return "".join(out)

ROUND_ORDER=["32强","16强","8强","半决赛","季军","决赛"]
recs.sort(key=lambda r:(ROUND_ORDER.index(r["rnd"]), r["ao"]))

trs=[]
prev=None
for r in recs:
    if r["rnd"]!=prev:
        trs.append(f'<tr class="rh"><td colspan="6">{r["rnd"]}　<span class="tier">{ICON[r["price"]] if False else ""}</span></td></tr>')
        prev=r["rnd"]
    for side,pid,code in [("A",r["pA"],r["cA"]),("B",r["pB"],r["cB"])]:
        info=pk.get(pid,{})
        grp=info.get("content","")
        cn=code2cn.get(code,code)
        trs.append(
          f'<tr><td class="ao">{r["ao"]}</td><td class="ap">{r["ap"]}</td>'
          f'<td class="pk">{pid}</td><td class="team"><b>{cn}</b> <span class="code">{code}</span></td>'
          f'<td class="tier {ICON[r["price"]][0:1]}">${r["price"]}<br><span class="ti">{ICON[r["price"]]}</span></td>'
          f'<td class="rwcell">{reward_html(grp)}<span class="grp">组{grp}</span></td></tr>')

html=f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>世界杯竞猜 · ActvID×国家×礼包奖励</title><style>
:root{{--bg:#15171f;--ink:#ece9e0;--mut:#8f8a80;--line:#2c3340}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;padding:26px 22px}}
h1{{font-size:20px;margin:0 0 6px}}.sub{{color:var(--mut);font-size:13px;margin-bottom:18px;line-height:1.7}}
.sub b{{color:#e0a94a}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th{{background:#1c212c;color:#9fb8d8;padding:8px 10px;text-align:left;position:sticky;top:0;border-bottom:2px solid var(--line)}}
td{{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:middle}}
tr.rh td{{background:#222a36;color:#7fd8a8;font-weight:700;font-size:14px;padding:9px 10px}}
.ao{{color:#e0a94a;font-weight:700;font-family:monospace}}.ap,.pk{{color:var(--mut);font-family:monospace}}
.team b{{font-size:14px}}.code{{color:var(--mut);font-size:11px;font-family:monospace}}
.tier{{font-weight:700;text-align:center;white-space:nowrap}}.ti{{font-size:11px;color:var(--mut);font-weight:400}}
.rw{{display:inline-block;background:#232a36;border:1px solid #313a48;border-radius:5px;padding:2px 7px;margin:2px 4px 2px 0;font-size:12px}}
.rw.cos{{background:#2a2418;border-color:#7a6a3f;color:#e7c873}}
.grp{{display:inline-block;color:var(--mut);font-size:10.5px;font-family:monospace;margin-left:4px}}
.rwcell{{max-width:560px}}
</style></head><body>
<h1>⚽ 世界杯竞猜 · ActvID × 国家 × 礼包奖励对照</h1>
<div class="sub">
共 <b>56</b> 个竞猜活动实例 / <b>112</b> 个礼包（每场两队各一包）。随机48队22-24对抗（种子2026·验证美术用，对阵抽签后替换）。<br>
<b>$4.99 纯竞猜</b>=共享奖励(无外显) ｜ <b>$9.99 头像框</b>=该队助威头像框+自选框宝箱 ｜ <b>$19.99 聊天表情</b>=该队加油表情+自选表情宝箱。<span class="rw cos">金底</span>=队伍专属外显道具。
</div>
<table>
<thead><tr><th>ActvID</th><th>ActvPack</th><th>礼包ID</th><th>国家</th><th>价格/类型</th><th>礼包奖励</th></tr></thead>
<tbody>
{chr(10).join(trs)}
</tbody></table>
</body></html>"""
out=pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\世界杯竞猜_ActvID国家礼包奖励对照.html")
out.write_text(html,encoding='utf-8')
print("写出:",out)
print(f"实例{len(recs)} 礼包{len(recs)*2} 奖励组{len(groups)}")
