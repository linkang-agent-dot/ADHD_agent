# -*- coding: utf-8 -*-
import urllib.request,re,json,time,os
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
pals=json.load(open("C:/ADHD_agent/skills/palworld-tools/pals_full.json",encoding="utf-8"))
out=json.load(open("pal_skills.json",encoding="utf-8")) if os.path.exists("pal_skills.json") else {}
log=open("_ps_log.txt","a",encoding="utf-8")
seen=set()
todo=[p for p in pals if p.get("href") and p["name"] not in out and p["name"] not in seen and not seen.add(p["name"])]
log.write("todo %d\n"%len(todo)); log.flush()
for i,p in enumerate(todo):
    try:
        h=urllib.request.urlopen(urllib.request.Request("https://paldb.cn"+p["href"],headers=H),timeout=30).read().decode("utf-8","ignore")
        sk=[]
        for s in re.findall(r'href="/skills/([^"]+)"',h):
            if s not in sk: sk.append(s)
        out[p["name"]]=sk
    except Exception as e:
        out[p["name"]]=[]
    if (i+1)%25==0:
        json.dump(out,open("pal_skills.json","w",encoding="utf-8"),ensure_ascii=False)
        log.write("%d/%d\n"%(i+1,len(todo))); log.flush()
    time.sleep(0.7)
json.dump(out,open("pal_skills.json","w",encoding="utf-8"),ensure_ascii=False)
log.write("DONE total %d\n"%len(out)); log.flush()
