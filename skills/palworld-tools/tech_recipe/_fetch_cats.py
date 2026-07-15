# -*- coding: utf-8 -*-
import urllib.request,re,json,time,os
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
def get(u):
    for _ in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30).read().decode("utf-8","ignore")
        except Exception: time.sleep(4)
    return ""
recipe=json.load(open("recipe_map.json",encoding="utf-8"))
donef="_cats_done.json"
done=set(json.load(open(donef,encoding="utf-8"))) if os.path.exists(donef) else set()
newcats=["ammo","furniture","foundation","defense","infrastructure","lighting","storage","glider","consumable","construction","other","ingredient","key","pal","schematic"]
log=open("_fetch_log.txt","a",encoding="utf-8")
for c in newcats:
    if c in done: continue
    h=get("https://paldb.cn/catalog/"+c)
    if not h:
        log.write(c+" FAIL\n"); log.flush(); time.sleep(3); continue
    t=h.replace('\\"','"').replace("\n"," ").replace("\u002F","/")
    blocks=re.split(r'(?="name":")',t)
    n=0
    for blk in blocks:
        mn=re.match(r'"name":"([^"]+)"',blk)
        if not mn: continue
        name=mn.group(1)
        mr=re.search(r'"recipes":\[(.*?)\](?:,"|\})',blk)
        if not mr: continue
        mats=re.findall(r'"material":"([^"]+)"[^}]*?"count":"?(\d+)"?',mr.group(1))
        if name not in recipe:
            recipe[name]={"r":[[m,int(cc)] for m,cc in mats]}; n+=1
    done.add(c)
    json.dump(recipe,open("recipe_map.json","w",encoding="utf-8"),ensure_ascii=False)
    json.dump(list(done),open(donef,"w",encoding="utf-8"),ensure_ascii=False)
    log.write("%s new %d (total %d)\n"%(c,n,len(recipe))); log.flush()
    time.sleep(2)
log.write("ALL DONE total %d\n"%len(recipe)); log.flush()
