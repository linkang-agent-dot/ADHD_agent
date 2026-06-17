# -*- coding: utf-8 -*-
"""补 X3 自动key到 live Text: 活动标题/描述(TXT_ActvOnline_ActvName/ActvDesc_{ID}) + 礼包猜对加送(TXT_Pack_Desc_{ID}) + 规则(TXT_RuleTips_*_1190)。保LF,跳过已存在。"""
import io,sys,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE=r'C:\x3\gdconfig'
def norm(s): return s.replace('\r\n','\n').replace('\r','\n')
def rows(p):
    with open(p,encoding='utf-8',newline='') as f: return [l.split('\t') for l in norm(f.read()).split('\n') if l!='']
def mktext(key,zh): return '\t'.join([key,"AI",""]+[zh]*16+[""]*8)

AO=rows(os.path.join(BASE,'tsv','ActvOnline__ActvOnline.tsv'))
PK=rows(os.path.join(BASE,'tsv','Pack__Pack.tsv'))
tp=os.path.join(BASE,'tsv','i18n','Text__Text.tsv')
with open(tp,encoding='utf-8',newline='') as f: tcontent=norm(f.read())
existing={l.split('\t')[0] for l in tcontent.split('\n') if l!=''}
new=[]
def add(key,zh):
    if key not in existing and key not in {n.split('\t')[0] for n in new}: new.append(mktext(key,zh))

# 1) 活动标题/描述 102920-102992
for r in AO:
    if not r[0].isdigit() or not(102920<=int(r[0])<=102992): continue
    nm=r[1]  # "WC竞猜-32强-JORvsIRN-$4.99" or "WC免费竞猜-0628-..."
    if "免费" in nm:
        add(f"TXT_ActvOnline_ActvName_{r[0]}","胜负预言·免费预测")
        add(f"TXT_ActvOnline_ActvDesc_{r[0]}","每日免费预测一场，猜对赢取抽奖券！")
    else:
        m=re.search(r"WC竞猜-([^-]+)-",nm); rnd=m.group(1) if m else "胜负预言"
        add(f"TXT_ActvOnline_ActvName_{r[0]}",f"胜负预言·{rnd}")
        add(f"TXT_ActvOnline_ActvDesc_{r[0]}","预言绿茵胜负，赢取冠军抽奖券！")

# 2) 礼包猜对加送 TXT_Pack_Desc_{ID} (按col6价格)
BONUS={"4.99":"猜对加送 +15","9.99":"猜对加送 +30","19.99":"猜对加送 +60","0":"猜对加送 +5"}
for r in PK:
    if not r[0].isdigit() or not(892001<=int(r[0])<=893034): continue
    b=BONUS.get(r[6])
    if b: add(f"TXT_Pack_Desc_{r[0]}",b)

# 3) RuleTips 1190 三key
add("TXT_RuleTips_Tab_1190","规则")
add("TXT_RuleTips_Title_1190","世界杯竞猜规则")
add("TXT_RuleTips_Content_1190",
    "1.每场比赛只能竞猜一方，购买助威礼包/领取免费预测后锁定不可更改、不可对冲。\\n"
    "2.礼包必得奖励购买即得；猜对额外加送的抽奖券于赛果确定后【次日】通过邮件发放。\\n"
    "3.赛果以该场含加时/点球的最终晋级（决赛为夺冠）方为准。\\n"
    "4.本活动最终解释权归运营方所有。")

if tcontent and not tcontent.endswith('\n'): tcontent+='\n'
with open(tp,'w',encoding='utf-8',newline='') as f: f.write(tcontent+'\n'.join(new)+'\n')
print(f"补了{len(new)}个自动key | CRLF={chr(13) in chr(10).join(new)}")
from collections import Counter
c=Counter(k.split('\t')[0].rsplit('_',1)[0] if k.split('\t')[0][-1].isdigit() else k.split('\t')[0] for k in new)
for pfx,n in sorted(c.items()): print(f"  {pfx}_* : {n}")
