# -*- coding: utf-8 -*-
"""v7→透明: ①video_remove_background去背得alpha ②export_sbs_video打包成Unity要的SBS(左彩右白模)。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
TOKEN = json.load(open(os.path.expanduser('~/.config/grfal-api/token_store.json')))['access_token']
os.environ.pop('GRFAL_COOKIE', None)
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(OUT, sys.argv[1] if len(sys.argv)>1 else 'intro_full_v8_1.mp4')

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit(tool,params,files):
    cmd=['--tool',tool,'--params',json.dumps(params,ensure_ascii=False)]
    for f in files: cmd+=['--file',f]
    out=run(cmd+['--submit-only','--timeout','900']).stdout.decode('utf-8','replace')
    print(f'[{tool} submit]',out[:250])
    try: return json.loads(out).get('task_id')
    except: return None
def poll(tid):
    for i in range(90):
        time.sleep(20)
        out=run(['--check-task',str(tid),'--timeout','120']).stdout.decode('utf-8','replace')
        try: d=json.loads(out)
        except: d={}
        if d.get('success') is False: print('FAIL-FAST:', str(d.get('error'))[:200]); return None
        st=d.get('status') or ''; print(f'[{i}] {st}')
        res=d.get('result') or d.get('output')
        if res and st not in ('pending','running','processing',''): return res
        if res and st=='': return res
        if st in ('failed','error','FAILURE'): print('FAIL',out[:300]); return None
    return None
def flat(x):
    o=[]
    if isinstance(x,list):
        for i in x: o+=flat(i)
    elif isinstance(x,dict): o.append(x.get('url') or x.get('path') or '')
    elif isinstance(x,str): o.append(x)
    return [u for u in o if u]
def dl(paths,prefix):
    s=[]
    for i,u in enumerate(flat(paths),1):
        url=u if u.startswith('http') else BASE+u
        ext=os.path.splitext(u.split('?')[0])[1] or '.mp4'
        dst=os.path.join(OUT,f'{prefix}_{i}{ext}')
        req=urllib.request.Request(url,headers={'Authorization': f'Bearer {TOKEN}'})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=300) as resp:
            open(dst,'wb').write(resp.read())
        print('SAVED',dst,os.path.getsize(dst)); s.append(dst)
    return s

# ① 去背
print('=== ① video_remove_background ===')
t1=submit('video_remove_background',{},[f'video_path={SRC}'])
if not t1: print('STEP1 SUBMIT FAIL'); sys.exit(1)
r1=poll(t1)
if not r1: print('STEP1 NO RESULT'); sys.exit(1)
nobg=dl(r1,'入场v8_去背')
# ② SBS
print('=== ② export_sbs_video ===')
src2=nobg[0] if nobg else None
t2=submit('export_sbs_video',{'quality':12},[f'input_videos={src2}'])
if t2:
    r2=poll(t2)
    if r2: dl(r2,'入场v8_SBS_q12'); print('SBS DONE')
    else: print('STEP2 NO RESULT')
else: print('STEP2 SUBMIT FAIL')
print('ALL DONE')
