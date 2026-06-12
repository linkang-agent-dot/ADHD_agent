# -*- coding: utf-8 -*-
"""SBS糊=quality参数没给对(疑似CRF,越低越清晰)。拿清晰webm重导多档对比挑清晰的。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\视频'
WEBM=os.path.join(OUT,'足球宝贝_v7_去背_1.webm')
import cv2,numpy as np
def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit(q):
    out=run(['--tool','export_sbs_video','--params',json.dumps({'quality':q}),
             '--file',f'input_videos={WEBM}','--submit-only','--timeout','900']).stdout.decode('utf-8','replace')
    print(f'[q={q} submit]',out[:150])
    try: return json.loads(out).get('task_id')
    except: return None
def poll(tid):
    for i in range(60):
        time.sleep(15)
        out=run(['--check-task',str(tid),'--timeout','120']).stdout.decode('utf-8','replace')
        try: d=json.loads(out)
        except: d={}
        st=d.get('status') or ''
        res=d.get('result') or d.get('output')
        if res and st not in ('pending','running','processing',''): return res
        if res and st=='': return res
        if st in ('failed','error','FAILURE'): print('FAIL',out[:200]);return None
    return None
def flat(x):
    o=[]
    if isinstance(x,list):
        for i in x:o+=flat(i)
    elif isinstance(x,dict):o.append(x.get('url') or x.get('path') or '')
    elif isinstance(x,str):o.append(x)
    return [u for u in o if u]
def dl(paths,q):
    for u in flat(paths):
        url=u if u.startswith('http') else BASE+u
        dst=os.path.join(OUT,f'_sbs_q{q}.mp4')
        req=urllib.request.Request(url,headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=300) as resp:
            open(dst,'wb').write(resp.read())
        return dst
def sharp(fn):
    cap=cv2.VideoCapture(fn);n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES,n//2);_,fr=cap.read();cap.release()
    w=fr.shape[1];L=fr[:,:w//2]
    return cv2.Laplacian(cv2.cvtColor(L,cv2.COLOR_BGR2GRAY),cv2.CV_64F).var()

print('(参考: 源v7锐度539, 旧SBS(q=95)锐度46/145KB)')
for q in [16,18]:
    t=submit(q)
    if not t: print(f'q={q} submit fail');continue
    r=poll(t)
    if not r: print(f'q={q} no result');continue
    fn=dl(r,q)
    print(f'>>> q={q}: {os.path.getsize(fn)/1e6:.2f}MB 左半锐度=%.0f'%sharp(fn))
print('DONE 看哪档锐度接近539/文件够大')
