# -*- coding: utf-8 -*-
# 深海节 i18n 体检 v2: 只在"母版非空"时才算漏建; 含漏翻(空缺/英文泄漏/中文泄漏)
import csv,sys,re
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
ROOT=r"C:\x3\gdconfig\tsv"
def load(f): return list(csv.reader(open(f"{ROOT}\\{f}",encoding='utf-8'),delimiter='\t'))
LANG={'cn':3,'en':4,'sp':5,'fr':6,'id':7,'de':8,'kr':9,'zh':10,'ru':11,'ua':12,'jp':13,'it':14,'pl':15,'po':16,'tr':17,'th':18}
NONCN=[k for k in LANG if k!='cn']
txt={}
for r in load("i18n\\Text__Text.tsv"):
    if len(r)<19 or not r[0]: continue
    vals={l:(r[LANG[l]] if len(r)>LANG[l] else '') for l in LANG}
    for k in r[0].split('|'): txt[k.strip()]=vals
CJK=re.compile(r'[一-鿿]')
def sent_en(s): return bool(s) and len(re.findall(r'[A-Za-z]',s))>=6 and (' ' in s or len(s)>12)
def audit(k):
    if k not in txt: return 'MISSING'
    v=txt[k]; cn=v['cn']
    if not cn: return 'OK'
    probs=[]
    for l in NONCN:
        if not v[l].strip(): probs.append('空:'+l)
    en=v['en']
    if sent_en(en):
        for l in NONCN:
            if l!='en' and v[l].strip()==en.strip(): probs.append('英泄:'+l)
    for l in NONCN:
        if l in('jp','zh'): continue
        if CJK.search(v[l]): probs.append('中泄:'+l)
    hard=[p for p in probs if not p.startswith('英泄')] + [p for p in probs if p.startswith('英泄')]
    return probs or 'OK'

# 母版取值
ao=load("ActvOnline__ActvOnline.tsv"); pk=load("Pack__Pack.tsv"); it=load("Item__Item.tsv"); rt=load("RuleTips__RuleTips.tsv")
def idx(rows,col=0):
    d={}
    for r in rows:
        if r and r[col].strip() and r[col].split('.')[0].isdigit(): d.setdefault(r[col],r)
    return d
AO=idx(ao); PK=idx(pk); IT=idx(it); RT=idx(rt)

checks=[]  # (key, 母版值, 标签)
# AO 名(col2)/描述(col3) + RuleTips
deep_rt=set()
for a,r in AO.items():
    if len(r)>38 and r[38] in('140','141'):
        checks.append((f"TXT_ActvOnline_ActvName_{a}", r[2] if len(r)>2 else '', f"AO{a}名"))
        checks.append((f"TXT_ActvOnline_ActvDesc_{a}", r[3] if len(r)>3 else '', f"AO{a}描述"))
        for x in (r[13] or '').split('|'):
            if x.strip(): deep_rt.add(x.strip())
# RuleTips Tab(col1)/Title(col2)/Content(col3)
for rid in sorted(deep_rt):
    r=RT.get(rid)
    if not r:
        checks.append((f"TXT_RuleTips_Content_{rid}", '??', f"规则{rid}(表里无此行!)")); continue
    checks.append((f"TXT_RuleTips_Tab_{rid}", r[1] if len(r)>1 else '', f"规则{rid}.Tab"))
    checks.append((f"TXT_RuleTips_Title_{rid}", r[2] if len(r)>2 else '', f"规则{rid}.Title"))
    checks.append((f"TXT_RuleTips_Content_{rid}", r[3] if len(r)>3 else '', f"规则{rid}.内容"))
# 深海 Pack: 名(col35)/描述(col36) — 只取深海ID段+主题且母版非空
DEEP=[(211016,211025),(280001,280001),(2801001,2801011),(2026101,2026104),(130034,130037),(13017,13020),(207101,207211)]
for pid,r in PK.items():
    p=int(pid) if pid.isdigit() else -1
    nm=r[2] if len(r)>2 else ''
    inr=any(a<=p<=b for a,b in DEEP)
    if not inr: continue
    name_mb=r[35] if len(r)>35 else ''
    desc_mb=r[36] if len(r)>36 else ''
    checks.append((f"TXT_Pack_Name_{pid}", name_mb, f"Pack{pid}名 {nm[:10]}"))
    checks.append((f"TXT_Pack_Desc_{pid}", desc_mb, f"Pack{pid}描述"))
# 深海 Item: 名(col1)/描述(col3) — 只取存在的
for iid in [1200,1201,1202,1204,1206,80100,82005,180080]:
    r=IT.get(str(iid))
    if not r: continue
    checks.append((f"TXT_Item_Name_{iid}", r[1] if len(r)>1 else '', f"Item{iid}名 {r[1][:8] if len(r)>1 else ''}"))
    checks.append((f"TXT_Item_Desc_{iid}", r[3] if len(r)>3 else '', f"Item{iid}描述"))
# ActvGroup 140/141 入口名(col4? 取ActvGroup表)
ag=load("ActvOnline__ActvGroup.tsv")
AG=idx(ag)
for g in('140','141'):
    r=AG.get(g)
    mb=(r[3] if r and len(r)>3 else '')
    checks.append((f"TXT_ActvGroup_MainEntranceName_{g}", mb if mb else '?', f"组{g}入口名"))

miss=[]; incomp=[]; ok=0
for k,mb,lab in checks:
    mb=(mb or '').strip()
    res=audit(k)
    if res=='MISSING':
        if mb and mb!='?':   # 母版非空才算真漏建
            miss.append((k,lab,mb[:24]))
        # 母版空=不该有key=正常,跳
        else: ok+=1
    elif res=='OK': ok+=1
    else: incomp.append((k,lab,res))
print(f"==== 深海 i18n 体检v2: {len(checks)}项, OK {ok} ====")
print(f"\n[1] 真漏建 {len(miss)} (母版有字但Text无key->空白)")
for k,lab,mb in miss: print(f"  ✗ {k} <{lab}> 母版=\"{mb}\"")
print(f"\n【② 漏翻/泄漏 {len(incomp)}】")
for k,lab,p in incomp: print(f"  ! {k} <{lab}>: {p}")
