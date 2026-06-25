# -*- coding: utf-8 -*-
"""Morphix E元素拆分①②: 从竞猜界面FINAL提取F固定层组件→#B8B8B8灰底雪碧图→remove_background去底。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\切图'
os.makedirs(OUT,exist_ok=True)
REF=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\竞猜界面_最终效果图_FINAL.png'

PROMPT=(
 "This is a UI ART ASSET extraction task. The output is a sprite sheet for game artists / developers. "
 "From the reference game UI, extract ONLY these FIXED UI components as GRAPHIC ART ASSETS, each EMPTY with NO text and NO numbers: "
 "1) the top ornate green-gold title banner plate (EMPTY, no Chinese text, keep laurel/ribbon ornaments); "
 "2) the countdown pill/chip plate (empty, keep hourglass ornament as separate icon); "
 "3) the golden circular VS badge (the VS lettering is part of the badge emblem art, keep it); "
 "4) the tall cream/parchment reward panel plate with golden frame (EMPTY inside, no items); "
 "5) the golden pill price button (empty, no price text); "
 "6) the bottom notice bar plate (empty, no text, keep end ornaments separate if detachable); "
 "7) one reward slot square frame (single empty tile frame, deduplicated); "
 "8) the golden ticket icon (the raffle ticket star icon alone). "
 "DECOMPOSE compound widgets into atomic parts; STRICT DEDUPLICATION (each unique element once, mirror copies keep one); "
 "do NOT redraw or recolor — preserve each element's exact original style from the reference. "
 "Layout: tidy rows by category with at least 20px padding between elements. "
 "OUTPUT BACKGROUND — CRITICAL: uniform light gray solid #B8B8B8 (184,184,184) filling the whole image. "
 "Do NOT use white, off-gray, gradient, cream, paper, checkerboard or any pattern. "
 "Output: a single high-res sprite sheet with ATOMIC, DEDUPLICATED assets on uniform #B8B8B8. No text strings, no numbers."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit(tool,params,files=None):
    cmd=['--tool',tool,'--params',json.dumps(params,ensure_ascii=False)]
    for f in (files or []): cmd+=['--file',f]
    r=run(cmd+['--submit-only','--timeout','900'])
    out=r.stdout.decode('utf-8','replace'); print(f'[{tool} submit]',out[:200])
    try: return json.loads(out).get('task_id')
    except: return None
def call_sync(tool,params,files=None):
    cmd=['--tool',tool,'--params',json.dumps(params,ensure_ascii=False)]
    for f in (files or []): cmd+=['--file',f]
    r=run(cmd+['--timeout','600'])
    out=r.stdout.decode('utf-8','replace'); print(f'[{tool}]',out[:300])
    try: return json.loads(out)
    except: return None
def poll(tid):
    for i in range(80):
        time.sleep(15)
        out=run(['--check-task',str(tid),'--timeout','120']).stdout.decode('utf-8','replace')
        try: d=json.loads(out)
        except: d={}
        st=d.get('status') or ''; print(f'[{i}] {st}')
        res=d.get('result') or d.get('output')
        if res and st not in ('pending','running','processing',''): return res
        if res and st=='': return res
        if st in ('failed','error','FAILURE'): return None
    return None
def dl(paths,prefix):
    s=[]
    for i,p in enumerate(paths if isinstance(paths,list) else [paths]):
        if isinstance(p,dict): p=p.get('url') or p.get('path') or ''
        if not p: continue
        url=p if p.startswith('http') else BASE+p
        dst=os.path.join(OUT,f'{prefix}_{i+1}.png')
        req=urllib.request.Request(url,headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=90) as resp:
            open(dst,'wb').write(resp.read())
        print('SAVED',dst,os.path.getsize(dst)); s.append(dst)
    return s

# ① 雪碧图
tid=submit('generate_image',{'prompt':PROMPT,'model':'gpt','aspect_ratio':'3:4'},[f'reference_images={REF}'])
if not tid: print('SUBMIT FAIL'); sys.exit(1)
res=poll(tid)
if not res: print('NO RESULT'); sys.exit(1)
sheets=dl(res,'固定组件雪碧图_灰底')
# ② 去底(第一张)
if sheets:
    r=call_sync('remove_background',{},[f'image_paths={sheets[0]}'])
    if r and (r.get('result') or r.get('output')):
        dl(r.get('result') or r.get('output'),'固定组件雪碧图_透明')
    else:
        # long_running fallback
        tid2=submit('remove_background',{},[f'image_paths={sheets[0]}'])
        if tid2:
            res2=poll(tid2)
            if res2: dl(res2,'固定组件雪碧图_透明')
print('DONE')
