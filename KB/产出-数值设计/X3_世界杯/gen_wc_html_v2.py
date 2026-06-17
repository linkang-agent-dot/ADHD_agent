# -*- coding: utf-8 -*-
"""世界杯竞猜 · 排期×对阵×档位×奖励 对照 HTML（v2 修正版）。
- 模拟真实32队晋级树→32个对阵全唯一(赢家上轮,不跨轮重复)
- 按真实2026赛程逐日排布(17比赛日)
- 每场显示双方各价格档奖励
- 每比赛日1个免费竞猜实例
仅出HTML,不写配置表。
"""
import io, sys, pathlib, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
random.seed(2026)
R = r"C:\x3\gdconfig\tsv"
def rows(p): return [l.split('\t') for l in pathlib.Path(p).read_text(encoding='utf-8').split('\n') if l]

# 48队: code, country, frameItem(80300+idx), emoteItem(15700+idx)
fr=[(int(r[0]),r[4].replace("DK_Img_Player_AvatarFrame_WC_",""),r[9].replace("世界杯·","")) for r in rows(R+r"\Personalize__PersonalizeAvatarFrameCfg.tsv") if len(r)>9 and r[4].startswith("DK_Img_Player_AvatarFrame_WC")]
fr.sort()
T={}
for i,(cfg,code,country) in enumerate(fr):
    T[code]=dict(code=code,country=country,frame=80300+i,emote=15700+i)
codes=list(T.keys()); assert len(codes)==48

# ── 模拟晋级树:32队入淘汰赛,赢家=每对第一个 ──
pool=codes[:]; random.shuffle(pool)
ko=pool[:32]
def pairup(lst): return [(lst[i],lst[i+1]) for i in range(0,len(lst),2)]
def winners(lst): return [lst[i] for i in range(0,len(lst),2)]
R32=pairup(ko)                         # 16场
w32=winners(ko)
R16=pairup(w32)                        # 8场
w16=winners(w32)
QF=pairup(w16)                         # 4场
w8=winners(w16)
SF=pairup(w8)                          # 2场
sf_w=[w8[0],w8[2]]; sf_l=[w8[1],w8[3]]
FINAL=[(sf_w[0],sf_w[1])]              # 1场 冠军赛
THIRD=[(sf_l[0],sf_l[1])]             # 1场 季军赛
# 轮次定义: key,名,对阵列表,价格档
ROUNDS=[("R32","32强",R32,["4.99"]),("R16","16强",R16,["4.99","9.99"]),
        ("QF","8强",QF,["4.99","9.99","19.99"]),("SF","4强(半决赛)",SF,["4.99","9.99","19.99"]),
        ("3RD","季军赛",THIRD,["4.99","9.99","19.99"]),("FINAL","冠军赛(决赛)",FINAL,["4.99","9.99","19.99"])]
# 扁平化按轮次顺序(供逐日消费)
queue=[]
for key,nm,matches,tiers in ROUNDS:
    for mA,mB in matches: queue.append(dict(rkey=key,rnm=nm,A=mA,B=mB,tiers=tiers))

# ── 真实赛程(date,周,轮次key,当日场次) ──
SCHEDULE=[("06/28","日","R32",1),("06/29","一","R32",3),("06/30","二","R32",3),
 ("07/01","三","R32",3),("07/02","四","R32",3),("07/03","五","R32",3),
 ("07/04","六","R16",2),("07/05","日","R16",2),("07/06","一","R16",2),("07/07","二","R16",2),
 ("07/08","三","REST",0),
 ("07/09","四","QF",1),("07/10","五","QF",1),("07/11","六","QF",2),
 ("07/12","日","REST",0),("07/13","一","REST",0),
 ("07/14","二","SF",1),("07/15","三","SF",1),
 ("07/16","四","REST",0),("07/17","五","REST",0),
 ("07/18","六","3RD",1),("07/19","日","FINAL",1)]

TIER_META={"4.99":("$4.99","🎫纯竞猜","#5b8fd8"),"9.99":("$9.99","🖼️头像框","#d8a24a"),"19.99":("$19.99","😀聊天表情","#c578d8")}
# 真实数值(策划案定稿): 必得券/钻/VIP/金币 + 猜对加送(必得75%) + 商会赠礼档 + 焦点战胜利加赠(走本地化)
PACK={
 "4.99": {"base":[("世界杯抽奖券",20),("钻石",2500),("VIP点数",25)],"bonus":15,"gift":"商会赠礼I","win":False},
 "9.99": {"base":[("世界杯抽奖券",40),("钻石",5000),("VIP点数",50)],"bonus":30,"gift":"商会赠礼II","win":True},
 "19.99":{"base":[("世界杯抽奖券",80),("钻石",10000),("VIP点数",100)],"bonus":60,"gift":"商会赠礼III","win":True},
}
FREE_BASE=[("世界杯抽奖券",1),("钻石",1),("金币",500),("30分钟通用加速",1),("基础资源袋",1)]
def base_rw(price): return PACK[price]["base"]
# 外显按轮次给(头像框不能重复投): 头像框档16强起·表情档8强起
def team_rw(rkey,price,t):
    if price=="9.99":  # 头像框档
        return {"R16":[(f"{t['country']}助威头像框",1,True)],
                "QF":[("自选头像框宝箱",1,True)],
                "SF":[("晋级之路头像框",1,True)],
                "3RD":[("自选头像框宝箱",1,True)],
                "FINAL":[("世界之巅头像框",1,True)]}.get(rkey,[])
    if price=="19.99":  # 聊天表情档(也不能重复:8强per-team首投,之后宝箱,决赛世界之巅)
        return {"QF":[(f"{t['country']}聊天表情",1,True)],
                "SF":[("自选表情宝箱",1,True)],
                "3RD":[("自选表情宝箱",1,True)],
                "FINAL":[("世界之巅聊天表情",1,True)]}.get(rkey,[])
    return []

# ── 分配ActvID(提案,配置别人弄) ──
paid_id=102920; free_id=102976
# 逐日消费
days=[]
for date,wk,rkey,cnt in SCHEDULE:
    if cnt==0:
        days.append(dict(date=date,wk=wk,rest=True)); continue
    todays=[queue.pop(0) for _ in range(cnt)]
    for mt in todays:
        mt["aos"]={}
        for price in mt["tiers"]:
            mt["aos"][price]=paid_id; paid_id+=1
    fid=free_id; free_id+=1
    days.append(dict(date=date,wk=wk,rest=False,rnm=todays[0]["rnm"],matches=todays,free=fid))
assert not queue, f"剩余未分配:{queue}"
n_paid=paid_id-102920; n_free=free_id-102976

def fmt(nm,num): return f'{nm}×{num}' if not isinstance(num,str) else f'{nm}{num}'
def rw_spans(rkey,price,t):
    out=[]
    for nm,num in base_rw(price): out.append(f'<span class="rw">{fmt(nm,num)}</span>')
    for nm,num,cos in team_rw(rkey,price,t): out.append(f'<span class="rw cos">{fmt(nm,num)}</span>')
    return "".join(out)

def team_cell(t):
    return f'<b>{t["country"]}</b> <span class="code">{t["code"]}</span>'

# ── 渲染 ──
H=[]
H.append(f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>世界杯竞猜 · 排期×对阵×档位×奖励</title><style>
:root{{--bg:#14161d;--ink:#ece9e0;--mut:#8c877d;--line:#2a313d}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;padding:24px 22px}}
h1{{font-size:20px;margin:0 0 6px}}.sub{{color:var(--mut);font-size:13px;line-height:1.8;margin-bottom:16px}}.sub b{{color:#e0a94a}}
.sum{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}}
.sum .box{{background:#1b212c;border:1px solid var(--line);border-radius:9px;padding:10px 16px;font-size:13px}}
.sum .box b{{font-size:20px;color:#7fd8a8;display:block}}
.day{{border:1px solid var(--line);border-radius:12px;margin-bottom:14px;overflow:hidden}}
.day .dh{{background:#1d2532;padding:9px 16px;font-size:14px;font-weight:700;display:flex;align-items:center;gap:12px}}
.day .dh .dt{{color:#e0a94a;font-family:monospace}}.day .dh .rd{{color:#7fb0e0}}.day .dh .wk{{color:var(--mut);font-weight:400;font-size:12px}}
.day.rest .dh{{background:#181c24;color:var(--mut);font-weight:400}}
.match{{padding:10px 16px;border-top:1px dashed #262d38}}
.match:first-of-type{{border-top:none}}
.mvs{{font-size:14px;margin-bottom:7px;display:flex;align-items:center;gap:10px}}
.mvs .vs{{color:#e0a94a;font-weight:700}}.code{{color:var(--mut);font-size:11px;font-family:monospace}}
.tier{{display:flex;align-items:flex-start;gap:10px;padding:4px 0;font-size:12.5px}}
.tlabel{{min-width:118px;font-weight:600;white-space:nowrap}}.aoid{{color:var(--mut);font-size:10.5px;font-family:monospace;min-width:58px}}
.pks{{flex:1;display:flex;gap:8px;flex-wrap:wrap}}
.pkbox{{flex:1;min-width:300px;background:#1a1f29;border:1px solid #262d38;border-radius:7px;padding:5px 9px}}
.pkbox .pn{{font-size:11px;color:#9fb8d8;margin-bottom:3px}}
.rw{{display:inline-block;background:#232a36;border:1px solid #313a48;border-radius:4px;padding:1px 6px;margin:1px 3px 1px 0;font-size:11.5px}}
.rw.cos{{background:#2a2418;border-color:#7a6a3f;color:#e7c873}}
.free{{padding:8px 16px;background:#16201a;border-top:1px solid #2a3a2e;font-size:12.5px;color:#9fd8b0}}
.free b{{color:#7fd8a8}}.free .aoid{{color:#5a8a6a}}.free .rw{{background:#1c2a20;border-color:#2e4435}}
.bonus{{padding:2px 0 4px 128px;font-size:12px;color:#e0b95a}}.bonus b{{color:#f0c860;font-size:13px}}
.gift{{color:var(--mut);font-size:11px}}.winb{{color:#d88a78;font-size:11px}}
.foot{{margin-top:20px;background:#1b212c;border:1px solid var(--line);border-radius:10px;padding:14px 18px;font-size:12.5px;line-height:1.9;color:var(--ink)}}
.foot b{{color:#e0a94a}}.foot .h{{color:#7fb0e0;font-weight:700}}
.rule{{margin:14px 0 4px;background:#24201a;border:1px solid #6a5a3a;border-radius:10px;padding:13px 18px;font-size:12.8px;line-height:2;color:#ece4d2}}
.rule .rh2{{color:#e7c052;font-weight:700;font-size:14px;margin-bottom:5px}}.rule b{{color:#f0c860}}
.cosmap{{margin:14px 0;background:#1b212c;border:1px solid var(--line);border-radius:10px;padding:6px 0;overflow:hidden}}
.cosmap table{{font-size:12.5px}}.cosmap th{{background:#222a36}}.cosmap td{{padding:6px 12px;border-bottom:1px solid #232a34}}
.cosmap .cos{{color:#e7c873}}
</style></head><body>
<h1>⚽ 世界杯竞猜 · 排期 × 对阵 × 档位 × 奖励</h1>
<div class="sub">
对齐真实 2026 世界杯淘汰赛赛程（FIFA/Wikipedia 核实）。窗口 <b>6/28 → 7/19（22天，17比赛日 + 5休息日）</b>。<br>
晋级树模拟：32队入淘汰赛，赢家进下一轮 → <b>32个对阵全唯一</b>（修掉了跨轮重复）。对阵为随机占位，真抽签后替换。<br>
档位：<b>$4.99 纯竞猜</b>(无外显) ｜ <b>$9.99 头像框</b>(该队助威头像框+自选框宝箱) ｜ <b>$19.99 聊天表情</b>(该队加油表情+自选表情宝箱)。<span class="rw cos">金底</span>=队伍专属外显。
</div>
<div class="sum">
<div class="box"><b>32</b>付费比赛场</div>
<div class="box"><b>{n_paid}</b>付费实例</div>
<div class="box"><b>{n_free}</b>免费实例(每比赛日1个)</div>
<div class="box"><b>{n_paid+n_free}</b>实例总计</div>
</div>
<div class="rule">
<div class="rh2">📜 规则说明（界面必展示）</div>
① 每人每场只能竞猜一方，购买助威礼包 / 领取免费预测后<b>锁定不可更改、不可对冲</b>（另一方置灰）。<br>
② 礼包<b>必得奖励购买即得</b>；<b>猜对加送的抽奖券于赛果确定后【次日】通过邮件发放</b>（兼赛果通知，游戏内不另设赛果展示）。<br>
③ 赛果以该场<b>含加时/点球的最终晋级（决赛为夺冠）方</b>为准。<br>
④ <b>本活动最终解释权归运营方所有。</b>
</div>
""")
for d in days:
    if d.get("rest"):
        H.append(f'<div class="day rest"><div class="dh"><span class="dt">{d["date"]}</span><span class="wk">周{d["wk"]}</span>　休息日（不新开实例，已开实例继续可买/结算）</div></div>')
        continue
    H.append(f'<div class="day"><div class="dh"><span class="dt">{d["date"]}</span><span class="wk">周{d["wk"]}</span><span class="rd">{d["rnm"]}</span><span class="wk">· 当日{len(d["matches"])}场</span></div>')
    for mt in d["matches"]:
        tA,tB=T[mt["A"]],T[mt["B"]]
        H.append(f'<div class="match"><div class="mvs">{team_cell(tA)} <span class="vs">VS</span> {team_cell(tB)}</div>')
        for price in mt["tiers"]:
            lab,ti,col=TIER_META[price]; pk=PACK[price]; rk=mt["rkey"]
            win='　<span class="winb">焦点战·胜利加赠（指定方获胜额外加送，数值见「胜利加赠」本地化文案）</span>' if pk["win"] else ''
            H.append(f'<div class="tier"><span class="tlabel" style="color:{col}">{lab} {ti}</span><span class="aoid">AO{mt["aos"][price]}</span>'
                     f'<span class="pks"><span class="pkbox"><span class="pn">{tA["country"]}包</span>{rw_spans(rk,price,tA)}</span>'
                     f'<span class="pkbox"><span class="pn">{tB["country"]}包</span>{rw_spans(rk,price,tB)}</span></span></div>'
                     f'<div class="bonus">🎯 猜对加送 <b>+{pk["bonus"]}券</b>（赛果次日邮件发放）　<span class="gift">+{pk["gift"]}(系统按价档挂载)</span>{win}</div>')
        H.append('</div>')
    free_items="".join(f'<span class="rw">{fmt(nm,num)}</span>' for nm,num in FREE_BASE)
    H.append(f'<div class="free">🆓 <b>免费竞猜</b>（当日赛事预言·免费领取非IAP）　<span class="aoid">AO{d["free"]}</span>　必得：{free_items}　🎯 猜对加送 <b>+5券</b></div>')
    H.append('</div>')
H.append("""<div class="cosmap"><table>
<thead><tr><th>轮次</th><th>$4.99 纯竞猜</th><th>$9.99 头像框档</th><th>$19.99 聊天表情档</th></tr></thead><tbody>
<tr><td>32强</td><td>券20+钻2500+VIP25</td><td>—（不开）</td><td>—（不开）</td></tr>
<tr><td>16强</td><td>纯竞猜</td><td class="cos">该队助威头像框（per-team·首投）</td><td>—（不开）</td></tr>
<tr><td>8强</td><td>纯竞猜</td><td class="cos">自选头像框宝箱</td><td class="cos">该队聊天表情（per-team·首投）</td></tr>
<tr><td>半决赛(4强)</td><td>纯竞猜</td><td class="cos">晋级之路头像框</td><td class="cos">自选表情宝箱</td></tr>
<tr><td>季军赛</td><td>纯竞猜</td><td class="cos">自选头像框宝箱</td><td class="cos">自选表情宝箱</td></tr>
<tr><td>决赛</td><td>纯竞猜</td><td class="cos">世界之巅头像框</td><td class="cos">世界之巅聊天表情</td></tr>
</tbody></table></div>
<div class="foot">
<div class="h">📐 数值说明（策划案定稿）</div>
• <b>外显不重复投</b>：头像框/聊天表情 per-team 只在该档首轮投（16强框 / 8强表情）；之后轮次用<b>自选宝箱</b>（玩家自选不撞已得），半决赛=晋级之路款，决赛=世界之巅款。<br>
• <b>必得抽奖券</b>：$4.99=20 / $9.99=40 / $19.99=80券（保底，花钱必得，合规非赌博）；免费场必得1券（留资产记录+参与奖）。<br>
• <b>🎯猜对加送</b>=必得的 75%（赛果命中走结算邮件发）：$4.99 <b>+15</b> / $9.99 <b>+30</b> / $19.99 <b>+60</b> / 免费 <b>+5</b>。命中合计：40→70 / 80→140券。单券≈$0.15（用户定标）。<br>
• <b>焦点战·胜利加赠</b>（运营每场指定一方携带，押中且该方获胜额外加送）：<b>数值与文案沿用现有「胜利加赠」本地化</b>，标签固定挂在指定方队伍横幅侧。<br>
• <b>商会赠礼</b> I/II/III 按价档（$4.99/$9.99/$19.99）系统挂载，不占礼包奖励位。<br>
• <b>免费产出预估</b>：17比赛日各1场，必得17券 + 猜对约50%≈42券 ≈ <b>59券</b>（约5.9次开箱·偏薄待校准）。<br>
• 抽奖券=世界杯开箱唯一货币（开箱冲排行榜 → 足球宝贝皮肤/限定英雄），竞猜礼包（同档券量+猜对bonus）=获券最优解。
</div>
</body></html>""")
out=pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\世界杯竞猜_排期对阵奖励对照.html")
out.write_text("\n".join(H),encoding='utf-8')
print("写出:",out)
print(f"付费比赛32场 | 付费实例{n_paid} | 免费实例{n_free} | 总计{n_paid+n_free}")
# 对阵唯一性自检
allp=[tuple(sorted((m["A"],m["B"]))) for d in days if not d.get("rest") for m in d["matches"]]
from collections import Counter
dup=[p for p,c in Counter(allp).items() if c>1]
print(f"对阵总数{len(allp)} 唯一{len(set(allp))} 重复{len(dup)}")
