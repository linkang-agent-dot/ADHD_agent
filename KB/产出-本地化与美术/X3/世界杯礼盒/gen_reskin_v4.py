# -*- coding: utf-8 -*-
"""世界杯开箱 reskin v4：以V2(更接近最终)为底,仅调构图——礼盒下移+缩小,人物全身露出不被遮挡,当主体。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒'
REF=os.path.join(OUT,'WorldCup_开箱reskin_人物主体_v2.png')  # V2:用户认可更接近最终

PROMPT=(
 "Use the reference image as the base and keep it almost identical: same World Cup box-opening activity UI, "
 "same silver-white-haired white-and-gold cheerleader as the main hero figure, same soccer-patterned gift box with gold ribbon, "
 "same football-stadium background (no national flags), same top title bar, same horizontal milestone progress bar with x50..x3000 coin nodes, "
 "same two bottom buttons (开启1次/开启所有), same bottom reward tab row, same Chinese UI text and art style. "
 "ONLY ADJUST THE COMPOSITION so the character is NOT occluded: move the gift box DOWNWARD to the lower-center and make it somewhat SMALLER, "
 "so the cheerleader's FULL BODY is clearly visible as the dominant main element; the gift box sits in front at the bottom, "
 "overlapping only around her feet / lower legs, and must NOT cover her torso, waist or chest. "
 "Keep everything else exactly the same. Official mobile game activity screen mockup, high detail."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gemini','aspect_ratio':'9:16'},ensure_ascii=False),
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
        dst=os.path.join(OUT,f'WorldCup_开箱reskin_人物主体_v4_不遮挡_v{i+1}.png')
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
