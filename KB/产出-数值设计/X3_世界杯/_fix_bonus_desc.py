# -*- coding: utf-8 -*-
"""定向修 live: Pack.Desc(col36)按价格填 TXT_WC_Oracle_Bonus_T1/T2/T3/Free + Text补T2/T3删错配GuessBonus。保LF。"""
import io,sys,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE=r'C:\x3\gdconfig'
def norm(s): return s.replace('\r\n','\n').replace('\r','\n')
def load(p):
    with open(p,'r',encoding='utf-8',newline='') as f: return norm(f.read())
def save(p,s):
    with open(p,'w',encoding='utf-8',newline='') as f: f.write(s)
PRICE2KEY={"4.99":"TXT_WC_Oracle_Bonus_T1","9.99":"TXT_WC_Oracle_Bonus_T2","19.99":"TXT_WC_Oracle_Bonus_T3","0":"TXT_WC_Oracle_Bonus_Free"}

# 1) Pack col36 按col6价格
pp=os.path.join(BASE,'tsv','Pack__Pack.tsv')
lines=load(pp).split('\n'); out=[]; n=0
for ln in lines:
    if ln=='':continue
    r=ln.split('\t')
    if r[0].isdigit() and 892001<=int(r[0])<=893034 and len(r)>37:
        price=r[6]; key=PRICE2KEY.get(price)
        if key and r[36]!=key: r[36]=key; n+=1
        out.append('\t'.join(r))
    else: out.append(ln)
save(pp,'\n'.join(out)+'\n'); print(f"Pack col36 填了{n}个")

# 2) Text: 删TXT_WC_GuessBonus_* + 克隆T1行加T2/T3
tp=os.path.join(BASE,'tsv','i18n','Text__Text.tsv')
tlines=[l for l in load(tp).split('\n') if l!='']
t1row=next((l for l in tlines if l.split('\t')[0]=="TXT_WC_Oracle_Bonus_T1"),None)
if not t1row: raise SystemExit("T1模板未找到")
kept=[l for l in tlines if not l.split('\t')[0].startswith("TXT_WC_GuessBonus_") and l.split('\t')[0] not in("TXT_WC_Oracle_Bonus_T2","TXT_WC_Oracle_Bonus_T3")]
removed=len(tlines)-len(kept)
def clone(key,txt):
    c=t1row.split('\t'); c[0]=key
    if len(c)>2 and c[2].startswith("TXT_WC_Oracle"): c[2]=key
    for i in range(3,len(c)):
        if c[i] and "猜对加送" in c[i]: c[i]=txt
    return '\t'.join(c)
kept.append(clone("TXT_WC_Oracle_Bonus_T2","猜对加送 +30"))
kept.append(clone("TXT_WC_Oracle_Bonus_T3","猜对加送 +60"))
save(tp,'\n'.join(kept)+'\n'); print(f"Text 删GuessBonus {removed}行, 加T2/T3")
print("done")
