# -*- coding: utf-8 -*-
"""v2 替换 live: 删旧v1 WC竞猜行 + 追加 _stage_v2 新行。保LF。"""
import io,sys,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE=r'C:\x3\gdconfig'; STAGE=r'C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_v2'
def load(p):
    with open(p,'r',encoding='utf-8',newline='') as f: return f.read()
def save(p,s):
    with open(p,'w',encoding='utf-8',newline='') as f: f.write(s)
def isint(s): return s.isdigit()

def norm(s): return s.replace('\r\n','\n').replace('\r','\n')
def do(live_rel, add_file, keep_pred):
    lp=os.path.join(BASE,*live_rel.split('/'))
    cur=norm(load(lp))
    kept=[]; removed=0
    for ln in cur.split('\n'):
        if ln=='' : continue
        if keep_pred(ln.split('\t')): kept.append(ln)
        else: removed+=1
    add_rows=[l for l in norm(load(os.path.join(STAGE,add_file))).split('\n') if l]
    new='\n'.join(kept+add_rows)+'\n'
    save(lp,new)
    print(f"{live_rel}: 删旧{removed} +新{len(add_rows)} CRLF={chr(13) in new}")

# ActvOnline: 删 col0 in 102920-102992
do('tsv/ActvOnline__ActvOnline.tsv','ActvOnline_add.tsv',
   lambda r: not(isint(r[0]) and 102920<=int(r[0])<=102992))
# ActvPack: 删 col0 2920-2992
do('tsv/ActvPack__ActvPack.tsv','ActvPack_add.tsv',
   lambda r: not(isint(r[0]) and 2920<=int(r[0])<=2992))
# TimeCycle: 删 col0 2920-2992
do('tsv/TimeCycle__TimeCycle.tsv','TimeCycle_add.tsv',
   lambda r: not(isint(r[0]) and 2920<=int(r[0])<=2992))
# Pack: 删 col0 892001-893034
do('tsv/Pack__Pack.tsv','Pack_add.tsv',
   lambda r: not(isint(r[0]) and 892001<=int(r[0])<=893034))
# Reward: 删 col1(RewardID) in 291401-291448 (旧v1组)
do('tsv/Reward__Reward.tsv','Reward_add.tsv',
   lambda r: not(len(r)>1 and isint(r[1]) and 291401<=int(r[1])<=291448))
# Text: 删 旧key(TXT_Pack_Name_89*/Desc_89*/WC_Guess_Title_*/WC_Guess_Desc)
def text_keep(r):
    k=r[0]
    if re.match(r'TXT_Pack_(Name|Desc)_89\d{4}$',k): return False
    if k.startswith('TXT_WC_Guess_Title_'): return False
    if k=='TXT_WC_Guess_Desc': return False
    return True
do('tsv/i18n/Text__Text.tsv','Text_add.tsv',text_keep)
# RuleTips: 纯追加(无旧)
do('tsv/RuleTips__RuleTips.tsv','RuleTips_add.tsv', lambda r: True)
print("done")
