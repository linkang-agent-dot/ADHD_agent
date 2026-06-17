# -*- coding: utf-8 -*-
"""世界杯竞猜 v2 完整配置【备份生成】→ _stage_v2/(不写live;等美术+用户叫了再同步)。
对齐 gen_wc_html_v2.py 的结构:32晋级树对阵(全唯一)+外显按轮次(不重复投)+17免费(每比赛日1)+猜对加送Pack.Desc文案+RuleTips规则。
缺美术的3里程碑款(晋级之路框80348/世界之巅框80349/世界之巅表情15748)=预留ID占位,美术出了建道具即可。
"""
import io,sys,pathlib,random
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
random.seed(2026)
R=r"C:\x3\gdconfig\tsv"
OUT=pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_v2");OUT.mkdir(exist_ok=True)
def rows(p):return[l.split('\t') for l in pathlib.Path(p).read_text(encoding='utf-8').split('\n') if l]
def tpl(p,i,idx=0):
    for r in rows(p):
        if len(r)>idx and r[idx]==str(i):return r[:]
    raise SystemExit(f"模板{i}未找到 {p}")
TPL_AO=tpl(R+r"\ActvOnline__ActvOnline.tsv",102911); TPL_AOF=tpl(R+r"\ActvOnline__ActvOnline.tsv",102912)
TPL_AP=tpl(R+r"\ActvPack__ActvPack.tsv",2911); TPL_TC=tpl(R+r"\TimeCycle__TimeCycle.tsv",2911)
TPL_PK=tpl(R+r"\Pack__Pack.tsv",891101); TPL_PKF=tpl(R+r"\Pack__Pack.tsv",891103)
TPL_RW=next(r for r in rows(R+r"\Reward__Reward.tsv") if len(r)>1 and r[1]=="291101")
TPL_RULE=tpl(R+r"\RuleTips__RuleTips.tsv",1001)

# 48队
fr=[(int(r[0]),r[4].replace("DK_Img_Player_AvatarFrame_WC_",""),r[9].replace("世界杯·","")) for r in rows(R+r"\Personalize__PersonalizeAvatarFrameCfg.tsv") if len(r)>9 and r[4].startswith("DK_Img_Player_AvatarFrame_WC")]
fr.sort()
T={}
for i,(cfg,code,country) in enumerate(fr):
    T[code]=dict(code=code,country=country,frame=80300+i,emote=15700+i,panel=f"DK_WC_TeamPanel_{code}",badge=f"DK_WC_Badge_{code}")
codes=list(T.keys())

# 晋级树→32唯一对阵
pool=codes[:];random.shuffle(pool);ko=pool[:32]
pair=lambda l:[(l[i],l[i+1]) for i in range(0,len(l),2)]; win=lambda l:[l[i] for i in range(0,len(l),2)]
R32=pair(ko);w32=win(ko);R16=pair(w32);w16=win(w32);QF=pair(w16);w8=win(w16);SF=pair(w8)
FINAL=[(w8[0],w8[2])];THIRD=[(w8[1],w8[3])]
ROUNDS=[("R32","32强",R32,["4.99"]),("R16","16强",R16,["4.99","9.99"]),("QF","8强",QF,["4.99","9.99","19.99"]),
        ("SF","半决赛",SF,["4.99","9.99","19.99"]),("3RD","季军",THIRD,["4.99","9.99","19.99"]),("FINAL","决赛",FINAL,["4.99","9.99","19.99"])]
SCHEDULE=[("0628","R32",1),("0629","R32",3),("0630","R32",3),("0701","R32",3),("0702","R32",3),("0703","R32",3),
 ("0704","R16",2),("0705","R16",2),("0706","R16",2),("0707","R16",2),("0709","QF",1),("0710","QF",1),("0711","QF",2),
 ("0714","SF",1),("0715","SF",1),("0718","3RD",1),("0719","FINAL",1)]
queue=[]
for k,nm,ms,tiers in ROUNDS:
    for a,b in ms: queue.append(dict(rkey=k,rnm=nm,A=a,B=b,tiers=tiers))

# 预留里程碑款道具ID(美术未出)
PH_SFFRAME=80348; PH_FINALFRAME=80349; PH_FINALEMOTE=15748
UNIONGIFT={"4.99":"202","9.99":"203","19.99":"204"}
# 猜对加送文案=Pack.Desc(col36)填共享key,客户端bonusTips.text=packCfg.Desc直接读
DESC_KEY={"4.99":"TXT_WC_Oracle_Bonus_T1","9.99":"TXT_WC_Oracle_Bonus_T2","19.99":"TXT_WC_Oracle_Bonus_T3"}

# ── 奖励组分配 ──
ao,ap,pk,tc,rw,txt=[],[],[],[],[],[]
rrow=24800
def addrw(grp,items):
    global rrow
    for it,nm,num in items:
        r=TPL_RW[:];r[0]=str(rrow);r[1]=str(grp);r[3]=str(it);r[4]=nm;r[5]=str(num);rw.append('\t'.join(r));rrow+=1
def mktext(key,zh):return '\t'.join([key,"AI",""]+[zh]*16+[""]*8)
BASE={"9.99":[(1146,"世界杯抽奖券",40),(1002,"钻石",5000),(2022,"VIP点数",50)],
      "19.99":[(1146,"世界杯抽奖券",80),(1002,"钻石",10000),(2022,"VIP点数",100)]}
# 共享组
G_FRCHEST=291330;G_EMCHEST=291331;G_SFFRAME=291332;G_FINFRAME=291333;G_FINEMOTE=291334;G_FREE=291335
addrw(G_FRCHEST,BASE["9.99"]+[(1148,"自选头像框宝箱",1)])
addrw(G_EMCHEST,BASE["19.99"]+[(1149,"自选表情宝箱",1)])
# 缺美术3款先用临时宝箱(导表能过),美术出了把这3组的道具换成 80348/80349/15748
addrw(G_SFFRAME,BASE["9.99"]+[(1148,"自选头像框宝箱【临时·待换晋级之路框80348】",1)])
addrw(G_FINFRAME,BASE["9.99"]+[(1148,"自选头像框宝箱【临时·待换世界之巅框80349】",1)])
addrw(G_FINEMOTE,BASE["19.99"]+[(1149,"自选表情宝箱【临时·待换世界之巅表情15748】",1)])
addrw(G_FREE,[(1146,"世界杯抽奖券",1),(1002,"钻石",1),(1001,"金币",500),(11003,"30分钟通用加速",1),(3101,"基础资源袋",1)])
# per-team组动态建
PT_FRAME_BASE=291301  # 16强per-team框组起
PT_EMOTE_BASE=291317  # 8强per-team表情组起

def content_group(rkey,price,t,ptframe_map,ptemote_map):
    """返回该pack的奖励组ID"""
    if price=="4.99": return "291101"
    if price=="9.99":
        if rkey=="R16": return ptframe_map[t['code']]      # per-team框
        if rkey in("QF","3RD"): return str(G_FRCHEST)       # 框宝箱
        if rkey=="SF": return str(G_SFFRAME)                # 晋级之路框(占位)
        if rkey=="FINAL": return str(G_FINFRAME)            # 世界之巅框(占位)
    if price=="19.99":
        if rkey=="QF": return ptemote_map[t['code']]        # per-team表情
        if rkey in("SF","3RD"): return str(G_EMCHEST)       # 表情宝箱
        if rkey=="FINAL": return str(G_FINEMOTE)            # 世界之巅表情(占位)
    return "291101"
BONUS={"4.99":15,"9.99":30,"19.99":60}

# 先建per-team组(只16强出现的队的框 + 8强出现的队的表情)
ptframe_map={};ptemote_map={}
gid=PT_FRAME_BASE
for a,b in R16:
    for c in (a,b):
        if c not in ptframe_map:
            ptframe_map[c]=str(gid);addrw(gid,BASE["9.99"]+[(T[c]['frame'],f"{T[c]['country']}助威头像框",1)]);gid+=1
gid=PT_EMOTE_BASE
for a,b in QF:
    for c in (a,b):
        if c not in ptemote_map:
            ptemote_map[c]=str(gid);addrw(gid,BASE["19.99"]+[(T[c]['emote'],f"{T[c]['country']}聊天表情",1)]);gid+=1

# ── 逐日生成实例 ──
paid_ao=102920;paid_ap=2920;paid_tc=2920;paid_pk=892001
free_ao=102976;free_ap=2976;free_tc=2976;free_pk=893001
manifest=[]
for date,rkey,cnt in SCHEDULE:
    todays=[queue.pop(0) for _ in range(cnt)]
    # 付费实例
    for mt in todays:
        for price in mt["tiers"]:
            cid=paid_ap;pkA,pkB=paid_pk,paid_pk+1
            t=TPL_TC[:];t[0]=str(paid_tc);t[1]=f"WC-{mt['rnm']}-{mt['A']}vs{mt['B']}-${price}";tc.append('\t'.join(t))
            a=TPL_AO[:];a[0]=str(paid_ao);a[1]=f"WC竞猜-{mt['rnm']}-{mt['A']}vs{mt['B']}-${price}";a[2]=f"TXT_WC_Guess_Title_{rkey}";a[3]="TXT_WC_Guess_Desc";a[4]=str(paid_tc);a[7]=str(cid);a[13]="1190";a[21]="DK_WC_ActvIcon";a[38]="139";ao.append('\t'.join(a))
            p=TPL_AP[:];p[0]=str(paid_ap);p[2]=f"{pkA}|{pkB}";p[3]="291102";ap.append('\t'.join(p))
            for pid,code in [(pkA,mt['A']),(pkB,mt['B'])]:
                tm=T[code];grp=content_group(rkey,price,tm,ptframe_map,ptemote_map)
                pp=TPL_PK[:];pp[0]=str(pid);pp[2]=f"WC-{mt['rnm']}-{code}-${price}";pp[6]=price;pp[7]={"4.99":"105","9.99":"106","19.99":"107"}[price];pp[13]=grp
                pp[25]=tm['panel'];pp[27]=tm['badge']
                if len(pp)>40: pp[35]=tm['country'];pp[36]=DESC_KEY[price];pp[40]=UNIONGIFT[price]
                pk.append('\t'.join(pp))
                txt.append(mktext(f"TXT_Pack_Name_{pid}",tm['country']))
                # 猜对加送=按档共享key(不per-pack),Pack.Desc直接写共享key
            manifest.append(f"付费|{mt['rnm']}|{mt['A']}vs{mt['B']}|${price}|AO{paid_ao}|Pack{pkA}/{pkB}|组{grp if price=='4.99' else content_group(rkey,price,T[mt['A']],ptframe_map,ptemote_map)+'/'+content_group(rkey,price,T[mt['B']],ptframe_map,ptemote_map)}")
            paid_ao+=1;paid_ap+=1;paid_tc+=1;paid_pk+=2
    # 免费实例(当日首场)
    mt=todays[0];pkA,pkB=free_pk,free_pk+1
    t=TPL_TC[:];t[0]=str(free_tc);t[1]=f"WC免费-{date}-{mt['A']}vs{mt['B']}";tc.append('\t'.join(t))
    a=TPL_AOF[:];a[0]=str(free_ao);a[1]=f"WC免费竞猜-{date}-{mt['A']}vs{mt['B']}";a[2]=f"TXT_WC_Guess_Title_{rkey}";a[3]="TXT_WC_Guess_Desc";a[4]=str(free_tc);a[7]=str(free_ap);
    if len(a)>21:a[21]="DK_WC_ActvIcon"
    if len(a)>38:a[38]="139"
    a[13]="1190"
    ao.append('\t'.join(a))
    p=TPL_AP[:];p[0]=str(free_ap);p[2]=f"{pkA}|{pkB}";p[3]="291102";ap.append('\t'.join(p))
    for pid,code in [(pkA,mt['A']),(pkB,mt['B'])]:
        tm=T[code];pp=TPL_PKF[:];pp[0]=str(pid);pp[2]=f"WC免费-{date}-{code}";pp[13]=str(G_FREE)
        if len(pp)>27:pp[25]=tm['panel'];pp[27]=tm['badge']
        if len(pp)>36:pp[35]=tm['country'];pp[36]="TXT_WC_Oracle_Bonus_Free"
        pk.append('\t'.join(pp))
        txt.append(mktext(f"TXT_Pack_Name_{pid}",tm['country']))
    manifest.append(f"免费|{date}|{mt['A']}vs{mt['B']}|AO{free_ao}|Pack{pkA}/{pkB}|组{G_FREE}")
    free_ao+=1;free_ap+=1;free_tc+=1;free_pk+=2
assert not queue

# 标题i18n
for k,nm,_,_ in ROUNDS: txt.append(mktext(f"TXT_WC_Guess_Title_{k}",f"胜负预言·{nm}"))
txt.append(mktext("TXT_WC_Guess_Desc","预言绿茵胜负，赢取冠军抽奖券！"))
# 猜对加送=Pack.Desc填共享key(客户端bonusTips.text=packCfg.Desc)。T1/Free已在live(别人建),只补T2/T3
txt.append(mktext("TXT_WC_Oracle_Bonus_T2","猜对加送 +30"))
txt.append(mktext("TXT_WC_Oracle_Bonus_T3","猜对加送 +60"))

# RuleTips 规则(1条;Content用\n+color沿用现有风格)
RULE_ID=1190
rule=TPL_RULE[:];rule[0]=str(RULE_ID);rule[1]="规则";rule[2]="世界杯竞猜规则"
rule[3]=("1.每场比赛只能竞猜一方，购买助威礼包/领取免费预测后锁定不可更改、不可对冲。\\n"
         "2.礼包必得奖励购买即得；猜对额外加送的抽奖券于赛果确定后【次日】通过邮件发放。\\n"
         "3.赛果以该场含加时/点球的最终晋级（决赛为夺冠）方为准。\\n"
         "4.本活动最终解释权归运营方所有。")
ruletips=['\t'.join(rule)]

def w(n,l):(OUT/n).write_text('\n'.join(l)+'\n',encoding='utf-8')
w("ActvOnline_add.tsv",ao);w("ActvPack_add.tsv",ap);w("Pack_add.tsv",pk);w("TimeCycle_add.tsv",tc)
w("Reward_add.tsv",rw);w("Text_add.tsv",txt);w("RuleTips_add.tsv",ruletips);w("_manifest.txt",manifest)
print(f"AO{len(ao)}(付费56+免费17={len(ao)}) | AP{len(ap)} | Pack{len(pk)} | TC{len(tc)} | Reward行{len(rw)} | Text{len(txt)} | RuleTips1")
print(f"奖励组: per-team框{len(ptframe_map)}(291301+) per-team表情{len(ptemote_map)}(291317+) 共享6(291330-335) + 291101(存量)")
print(f"占位道具(美术未出·TODO): 晋级之路框{PH_SFFRAME}/世界之巅框{PH_FINALFRAME}/世界之巅表情{PH_FINALEMOTE}(需:美术+Item+Personalize/Emoticons+DK+i18n)")
print(f"ID段: AO付费102920-{paid_ao-1}/免费102976-{free_ao-1} | Pack付费892001-{paid_pk-1}/免费893001-{free_pk-1} | RewardRow24800-{rrow-1} | RuleTips{RULE_ID}")
