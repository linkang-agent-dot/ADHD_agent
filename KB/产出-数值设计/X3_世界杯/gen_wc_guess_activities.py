# -*- coding: utf-8 -*-
"""世界杯竞猜活动 56 实例配置生成器 → 输出到【备份目录】(不碰 live gdconfig)。
等另一个agent干完 + 对阵抽签后,填队伍→同步进 gdconfig。
克隆 live 模板(ActvOnline102911/ActvPack2911/Pack891101/TC2911),按甘特图排期×价格档生成。
队伍(Head/Icon/Name)+开球时间=占位,对阵定了填。
"""
import io, sys, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = r"C:\x3\gdconfig\tsv"
OUT = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_activities")
OUT.mkdir(exist_ok=True)

def rows(p): return [ln.split('\t') for ln in pathlib.Path(p).read_text(encoding='utf-8').split('\n') if ln]
def by_id(p, i, idx=0):
    for r in rows(p):
        if len(r) > idx and r[idx] == str(i): return r[:]
    raise SystemExit(f"模板 {i} 未找到 in {p}")

TPL_AO  = by_id(REPO+r"\ActvOnline__ActvOnline.tsv", 102911)
TPL_AP  = by_id(REPO+r"\ActvPack__ActvPack.tsv", 2911)
TPL_PK  = by_id(REPO+r"\Pack__Pack.tsv", 891101)
TPL_TC  = by_id(REPO+r"\TimeCycle__TimeCycle.tsv", 2911)
TPL_RW  = next(r for r in rows(REPO+r"\Reward__Reward.tsv") if len(r)>1 and r[1]=="291101")

# ── 排期×价格档 → 56 实例 ──────────────────────────────
# (轮次, 比赛数, [价格档...]) ; 价格档: 4.99纯竞猜 / 9.99头像框 / 19.99表情
PLAN = [("32强",16,["4.99"]), ("16强",8,["4.99","9.99"]), ("8强",4,["4.99","9.99","19.99"]),
        ("半决赛",2,["4.99","9.99","19.99"]), ("季军",1,["4.99","9.99","19.99"]), ("决赛",1,["4.99","9.99","19.99"])]
TIER = {  # price -> (PackPrice档id, 奖励组, 档说明)
  "4.99":  ("105", "291101", "纯竞猜:券20+钻2500+VIP25"),
  "9.99":  ("106", "291302", "头像框:券40+钻5000+VIP50+自选头像框宝箱"),
  "19.99": ("107", "291303", "表情:券80+钻10000+VIP100+自选表情宝箱"),
}

# ── 2个新奖励组 (291302/291303), 行号 24700+ 连续 ──────────────
def mkrew(rowid, grp, item, name, num):
    r = TPL_RW[:]; r[0]=str(rowid); r[1]=str(grp); r[3]=str(item); r[4]=name; r[5]=str(num); return '\t'.join(r)
reward_rows, rid = [], 24700
for grp, items in [("291302",[(1146,"世界杯冠军抽奖券",40),(1002,"钻石",5000),(2022,"100VIP点数",50),(1148,"自选头像框宝箱",1)]),
                   ("291303",[(1146,"世界杯冠军抽奖券",80),(1002,"钻石",10000),(2022,"100VIP点数",100),(1149,"自选表情宝箱",1)])]:
    for it,nm,n in items: reward_rows.append(mkrew(rid,grp,it,nm,n)); rid+=1

# ── 56 实例 ──────────────────────────────────────────
ao_rows, ap_rows, pk_rows, tc_rows, txt_rows = [], [], [], [], []
ao_id, ap_id, tc_id, pk_id = 102920, 2920, 2920, 892001
i = 0
manifest = []
for rnd, nmatch, tiers in PLAN:
    for m in range(1, nmatch+1):
        for price in tiers:
            cid = ap_id            # ContentID = ActvPack id
            ppr, rgrp, tdesc = TIER[price]
            pkA, pkB = pk_id, pk_id+1
            # TimeCycle (相对窗口,部署起算;时长占位=按比赛日,ops部署时定)
            tc = TPL_TC[:]; tc[0]=str(tc_id); tc[1]=f"WC竞猜-{rnd}-M{m}-${price}"; tc_rows.append('\t'.join(tc))
            # ActvOnline (type64)
            ao = TPL_AO[:]; ao[0]=str(ao_id); ao[1]=f"世界杯竞猜-{rnd}-M{m}-${price}"
            ao[2]=f"TXT_WC_Guess_Title_{rnd}"; ao[3]="TXT_WC_Guess_Desc"; ao[4]=str(tc_id); ao[7]=str(cid)
            ao[21]="DK_WC_ActvIcon"; ao_rows.append('\t'.join(ao))
            # ActvPack (PackList=两队包, FinalReward占位用291102)
            ap = TPL_AP[:]; ap[0]=str(ap_id); ap[2]=f"{pkA}|{pkB}"; ap[3]="291102"; ap_rows.append('\t'.join(ap))
            # 2 Pack (队A/队B; Head/Icon/Name=占位空,对阵定了填)
            for pid, side in [(pkA,"A"),(pkB,"B")]:
                pk = TPL_PK[:]; pk[0]=str(pid); pk[2]=f"WC竞猜-{rnd}-M{m}-{side}-${price}"
                pk[6]=price; pk[7]=ppr; pk[13]=rgrp; pk_rows.append('\t'.join(pk))
            manifest.append(f"{rnd} M{m} ${price} | ActvOnline {ao_id} | ActvPack/ContentID {cid} | TC {tc_id} | Pack {pkA},{pkB} | 奖励组 {rgrp}")
            ao_id+=1; ap_id+=1; tc_id+=1; pk_id+=2; i+=1

# 标题i18n (每轮1个key)
for rnd,_,_ in PLAN:
    txt_rows.append(f"TXT_WC_Guess_Title_{rnd}\tAI\t\t胜负预言·{rnd}")

def w(n,l): (OUT/n).write_text('\n'.join(l)+'\n',encoding='utf-8')
w("ActvOnline_add.tsv",ao_rows); w("ActvPack_add.tsv",ap_rows); w("Pack_add.tsv",pk_rows)
w("TimeCycle_add.tsv",tc_rows); w("Reward_add.tsv",reward_rows); w("Text_add.tsv",txt_rows)
w("_manifest.txt",manifest)

print(f"备份输出 → {OUT}")
print(f"实例 {i} 个 | ActvOnline {ao_rows.__len__()} | ActvPack {len(ap_rows)} | Pack {len(pk_rows)} | TC {len(tc_rows)} | 新奖励行 {len(reward_rows)}(组291302/291303)")
print("ID段: ActvOnline 102920-%d / ActvPack&TC 2920-%d / Pack 892001-%d / Reward行 24700-%d" % (ao_id-1, ap_id-1, pk_id-1, rid-1))
