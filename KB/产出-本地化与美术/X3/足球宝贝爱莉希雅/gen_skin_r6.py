# -*- coding: utf-8 -*-
"""足球宝贝皮肤 R6：以R5-V2主稿为基准,加一个足球(手臂夹着),其余(白金10号+奖杯徽章+花球+本人+姿势)全保留。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅'
REF=os.path.join(OUT,'足球宝贝爱莉希雅_r5白金加徽章_v2.png')  # 现皮肤主稿

PROMPT=(
 "Use the reference image EXACTLY and keep EVERYTHING identical: same silver-white-haired cheerleader, same face, "
 "same white-and-gold cheerleader outfit with the gold number '10' on the chest and the small gold trophy emblem/badge near the collar, "
 "same white-and-gold pleated cheer skirt, same knee-high socks, same sneakers, same gold pom-poms, same confident standing pose, "
 "same cartoon stylized 3D game art style, clean white background. "
 "ADD ONE element: a standard black-and-white soccer ball held under one of her arms, naturally and comfortably integrated into her pose "
 "(she can still hold a pom-pom in that hand). Keep her identity, outfit, the '10', the trophy badge and everything else exactly the same. "
 "Full body, official mobile game hero skin splash art, ultra detailed, high quality."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gpt','aspect_ratio':'2:3'},ensure_ascii=False),
           '--file',f'reference_images={REF}','--submit-only','--timeout','900'])
    out=r.stdout.decode('utf-8','replace'); print('[submit]',out[:200])
    try: return json.loads(out).get('task_id')
    except: return None
def poll(tid):
    for i in range(70):
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
        dst=os.path.join(OUT,f'足球宝贝爱莉希雅_r6加球_v{i+1}.png')
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
