# -*- coding: utf-8 -*-
"""竞猜界面最终效果图 v2：以FINAL为基底,只改一处——VS区队伍横幅改成【规则长方形面板】(对齐槽位拆解图,方便图槽生产)。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面'
REF=os.path.join(OUT,'竞猜界面_方向定稿_FINAL.png')

PROMPT=(
 "Use the reference image EXACTLY and keep EVERYTHING identical: same title banner '胜负预言·32强', same countdown chip, "
 "same Brazil and Argentina crests and team name plates, same golden VS badge, same two soccer-pattern gift chests, "
 "same two mirrored reward panels with all item icons and numbers, same price buttons 'US$4.99', same bottom notice bar, "
 "same stadium background, same art style and color grading. "
 "ONLY ONE CHANGE: the two team banner panels in the VS zone (currently irregular angled/clipped decorative shapes) "
 "must become clean REGULAR RECTANGLES with simple golden frames and slightly rounded corners — "
 "left rectangle: green-yellow gradient with Brazil crest + name plate; right rectangle: blue-white gradient with Argentina crest + name plate; "
 "the golden VS badge stays centered between/overlapping the two rectangles. Equal size, axis-aligned, no diagonal cuts, no irregular notches. "
 "Everything else stays exactly the same. Vertical mobile game UI mockup, high detail."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gpt','aspect_ratio':'9:16'},ensure_ascii=False),
           '--file',f'reference_images={REF}','--submit-only','--timeout','900'])
    out=r.stdout.decode('utf-8','replace'); print('[submit]',out[:200])
    try: return json.loads(out).get('task_id')
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
def dl(paths):
    s=[]
    for i,p in enumerate(paths if isinstance(paths,list) else [paths]):
        if isinstance(p,dict): p=p.get('url') or p.get('path') or ''
        if not p: continue
        url=p if p.startswith('http') else BASE+p
        dst=os.path.join(OUT,f'竞猜界面_FINAL_v2_矩形VS_{i+1}.png')
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
