# -*- coding: utf-8 -*-
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT  = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅'
TASK = 'generate_image_1c804c7e_1780989592'

def check(tid):
    r=subprocess.run(['python',CALL,'--check-task',str(tid),'--timeout','120'],capture_output=True,text=False,timeout=150)
    return r.stdout.decode('utf-8','replace')

def dl(paths,tag):
    saved=[]
    for i,p in enumerate(paths if isinstance(paths,list) else [paths]):
        if isinstance(p,dict): p=p.get('url') or p.get('path') or ''
        if not p: continue
        url=p if p.startswith('http') else BASE+p
        dst=os.path.join(OUT,f'足球宝贝爱莉希雅_{tag}_v{i+1}.png')
        req=urllib.request.Request(url,headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=90) as resp:
            open(dst,'wb').write(resp.read())
        print('SAVED',dst,os.path.getsize(dst)); saved.append(dst)
    return saved

for i in range(50):
    out=check(TASK)
    try: d=json.loads(out)
    except: d={}
    st=d.get('status') or d.get('state') or ''
    print(f'[{i}] {st} {out[:150]}')
    res=d.get('result') or d.get('output')
    if res and st not in ('pending','running','processing',''):
        if dl(res,'gpt'): print('DONE'); break
    if res and isinstance(res,(list,dict)) and st=='':
        if dl(res,'gpt'): print('DONE'); break
    if st in ('failed','error','FAILURE'): print('FAILED'); break
    time.sleep(15)
