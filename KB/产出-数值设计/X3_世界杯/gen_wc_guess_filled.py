# -*- coding: utf-8 -*-
"""世界杯竞猜活动 56实例【填真队伍·验证美术】→ 暂存,随后append到live gdconfig。
随机配对48队;每Pack配 队伍板(Head=col25)/队徽(Icon=col27)/队名(i18n TXT_Pack_Name)/加送(TXT_Pack_Desc)/奖励组(Content=col13)。
$9.99头像框=该队框道具+自选框宝箱; $19.99表情=该队表情道具+自选表情宝箱; $4.99=纯竞猜共享291101。
作为模板,对阵抽签后改队即可。
"""
import io, sys, pathlib, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
random.seed(2026)  # 可复现
R = r"C:\x3\gdconfig\tsv"
OUT = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_activities"); OUT.mkdir(exist_ok=True)
def rows(p): return [ln.split('\t') for ln in pathlib.Path(p).read_text(encoding='utf-8').split('\n') if ln]
def tpl(p,i,idx=0):
    for r in rows(p):
        if len(r)>idx and r[idx]==str(i): return r[:]
    raise SystemExit(f"{i} not found {p}")
TPL_AO=tpl(R+r"\ActvOnline__ActvOnline.tsv",102911); TPL_AP=tpl(R+r"\ActvPack__ActvPack.tsv",2911)
TPL_PK=tpl(R+r"\Pack__Pack.tsv",891101); TPL_TC=tpl(R+r"\TimeCycle__TimeCycle.tsv",2911)
TPL_RW=next(r for r in rows(R+r"\Reward__Reward.tsv") if len(r)>1 and r[1]=="291101")
NPK=len(TPL_PK)

# 48队: code, country, frameItem(80300+i), emoteItem(15700+i)
fr=[(int(r[0]),r[4].replace("DK_Img_Player_AvatarFrame_WC_",""),r[9]) for r in rows(R+r"\Personalize__PersonalizeAvatarFrameCfg.tsv") if len(r)>9 and r[4].startswith("DK_Img_Player_AvatarFrame_WC")]
fr.sort()
teams=[]
for i,(cfg,code,nm) in enumerate(fr):
    country=nm.replace("世界杯·","")
    teams.append(dict(code=code,country=country,frame=80300+i,emote=15700+i,
                      panel=f"DK_WC_TeamPanel_{code}",badge=f"DK_WC_Badge_{code}"))
assert len(teams)==48

# 随机配对48队→24对
pool=teams[:]; random.shuffle(pool)
pairs=[(pool[i],pool[i+1]) for i in range(0,48,2)]  # 24对

PLAN=[("32强",16,["4.99"]),("16强",8,["4.99","9.99"]),("8强",4,["4.99","9.99","19.99"]),
      ("半决赛",2,["4.99","9.99","19.99"]),("季军",1,["4.99","9.99","19.99"]),("决赛",1,["4.99","9.99","19.99"])]
TIER={"4.99":("105",[(1146,40//2,20),(1002,2500),(2022,25)]),  # 占位,$4.99用共享组291101
      "9.99":("106",None),"19.99":("107",None)}
PRICE_PPR={"4.99":"105","9.99":"106","19.99":"107"}
UNIONGIFT={"4.99":"202","9.99":"203","19.99":"204"}  # 商会赠礼按IAP价格档(UnionGiftCfg)

ao,ap,pk,tc,rw,txt=[],[],[],[],[],[]
def mkrw(rid,grp,item,num,nm):
    r=TPL_RW[:]; r[0]=str(rid); r[1]=str(grp); r[3]=str(item); r[4]=nm; r[5]=str(num); return '\t'.join(r)
def mktext(key,zh):
    # Text表27列: [键值,校对结果AI,中文修改备份] + 16语言列(全填中文占位待翻) + 8尾列(校对情况等)空
    return '\t'.join([key,"AI",""]+[zh]*16+[""]*8)

aoid,apid,tcid,pkid=102920,2920,2920,892001
rgid=291401; rrow=24800  # 行号24710起已被RewardID30585占,改24800空闲段
manifest=[]
pair_i=0
for rnd,nmatch,tiers in PLAN:
    for m in range(nmatch):
        tA,tB=pairs[pair_i % 24]; pair_i+=1
        for price in tiers:
            cid=apid; ppr=PRICE_PPR[price]; pkA,pkB=pkid,pkid+1
            tc_r=TPL_TC[:]; tc_r[0]=str(tcid); tc_r[1]=f"WC-{rnd}-{tA['code']}vs{tB['code']}-${price}"; tc.append('\t'.join(tc_r))
            ao_r=TPL_AO[:]; ao_r[0]=str(aoid); ao_r[1]=f"WC竞猜-{rnd}-{tA['code']}vs{tB['code']}-${price}"
            ao_r[2]=f"TXT_WC_Guess_Title_{rnd}"; ao_r[3]="TXT_WC_Guess_Desc"; ao_r[4]=str(tcid); ao_r[7]=str(cid); ao_r[21]="DK_WC_ActvIcon"; ao.append('\t'.join(ao_r))
            ap_r=TPL_AP[:]; ap_r[0]=str(apid); ap_r[2]=f"{pkA}|{pkB}"; ap_r[3]="291102"; ap.append('\t'.join(ap_r))
            for pid,t in [(pkA,tA),(pkB,tB)]:
                # 奖励组: $4.99共享291101; 否则建该队组
                if price=="4.99":
                    content="291101"
                else:
                    content=str(rgid)
                    if price=="9.99":
                        items=[(1146,40,"世界杯冠军抽奖券"),(1002,5000,"钻石"),(2022,50,"100VIP点数"),(t['frame'],1,f"{t['country']}助威头像框"),(1148,1,"自选头像框宝箱")]
                    else:
                        items=[(1146,80,"世界杯冠军抽奖券"),(1002,10000,"钻石"),(2022,100,"100VIP点数"),(t['emote'],1,f"{t['country']}加油表情"),(1149,1,"自选表情宝箱")]
                    for it,n,inm in items: rw.append(mkrw(rrow,rgid,it,n,inm)); rrow+=1
                    rgid+=1
                p=TPL_PK[:]; p[0]=str(pid); p[2]=f"WC-{rnd}-{t['code']}-${price}"; p[6]=price; p[7]=ppr; p[13]=content
                p[25]=t['panel']; p[27]=t['badge']  # Head队伍板 / Icon队徽
                if len(p)>40:
                    p[35]=t['country']      # 清模板残留"巴西"→按队队名(readable)
                    p[36]=""                # 清模板残留"猜对加送 +15"(误导)
                    p[40]=UNIONGIFT[price]  # 商会赠礼随价格档(202/203/204)
                pk.append('\t'.join(p))
                txt.append(mktext(f"TXT_Pack_Name_{pid}", t['country']))
                txt.append(mktext(f"TXT_Pack_Desc_{pid}", "押中加送世界杯冠军抽奖券！"))
            manifest.append(f"{rnd} {tA['code']}vs{tB['code']} ${price}|AO{aoid}|AP{cid}|TC{tcid}|Pack{pkA}({tA['code']})/{pkB}({tB['code']})|Content {content if price!='4.99' else '291101'}")
            aoid+=1;apid+=1;tcid+=1;pkid+=2
for rnd,_,_ in PLAN: txt.append(mktext(f"TXT_WC_Guess_Title_{rnd}",f"胜负预言·{rnd}"))
txt.append(mktext("TXT_WC_Guess_Desc","预言绿茵胜负，赢取冠军抽奖券！"))

def w(n,l):(OUT/n).write_text('\n'.join(l)+'\n',encoding='utf-8')
w("ActvOnline_add.tsv",ao);w("ActvPack_add.tsv",ap);w("Pack_add.tsv",pk);w("TimeCycle_add.tsv",tc);w("Reward_add.tsv",rw);w("Text_add.tsv",txt);w("_manifest.txt",manifest)
print(f"实例56|AO{len(ao)}|AP{len(ap)}|Pack{len(pk)}|TC{len(tc)}|奖励行{len(rw)}(组291401-{rgid-1})|Text{len(txt)}")
print(f"ID段: AO102920-{aoid-1}/AP&TC2920-{apid-1}/Pack892001-{pkid-1}/Reward组291401-{rgid-1}行24710-{rrow-1}")
print("样本Pack:",pk[32][:160])
print("样本奖励组首行:",rw[0])
