# -*- coding: utf-8 -*-
"""足球宝贝 R3：基于R2-V1,在球衣胸口加风格化金色冠军奖杯印花(原创风格化,非FIFA精确复刻),其余不变。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅'
REF=os.path.join(OUT,'足球宝贝爱莉希雅_r2_v1.png')

PROMPT=(
 "Use the reference image EXACTLY: same character, same face, same long silver-white hair, same fair skin, "
 "same voluptuous figure, same confident full-body cheerleader pose holding a soccer ball under one arm and pom-poms, "
 "same white-and-gold cheerleader outfit with small red accents, same cartoon stylized 3D game art style. "
 "ADD a stylized GOLDEN championship football trophy graphic printed on the center chest of her white jersey, "
 "like a printed team emblem — an ORIGINAL stylized gold cup/trophy motif (NOT an exact real-world trophy replica, no brand logos), "
 "tasteful and well integrated into the jersey. Keep absolutely everything else identical. "
 "No flags, no national symbols. Clean white background, official mobile game hero skin splash art, ultra detailed."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gpt','aspect_ratio':'2:3'},ensure_ascii=False),
           '--file',f'reference_images={REF}','--submit-only','--timeout','900'])
    out=r.stdout.decode('utf-8','replace'); print('[submit]',out[:200])
    try: return json.loads(out).get('task_id')
    except: return None
def poll(tid):
    for i in range(60):
        time.sleep(15)
        out=run(['--check-task',str(tid),'--timeout','120']).stdout.decode('utf-8','replace')
        try: d=json.loads(out)
        except: d={}
        st=d.get('status') or ''; print(f'[{i}] {st} {out[:110]}')
        res=d.get('result') or d.get('output')
        if res and st not in ('pending','running','processing',''): return res
        if res and st=='': return res
        if st in ('failed','error','FAILURE'): return None
    return None
def dl(paths):
    s=[]
    for i,p in enumerate(paths if isinstance(paths,list) else [paths]):
        if isinstance(p,dict): p=p.get('url') or p.get('path') or ''
        if not p: continue
        url=p if p.startswith('http') else BASE+p
        dst=os.path.join(OUT,f'足球宝贝爱莉希雅_r3印花_v{i+1}.png')
        req=urllib.request.Request(url,headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=90) as resp:
            open(dst,'wb').write(resp.read())
        print('SAVED',dst,os.path.getsize(dst)); s.append(dst)
    return s
tid=submit()
if tid:
    res=poll(tid)
    if res: dl(res); print('DONE')
    else: print('NO RESULT')
else: print('SUBMIT FAIL')
