# -*- coding: utf-8 -*-
"""世界杯开箱活动 reskin 效果图 v2：双参考=已有reskin布局底 + 足球宝贝V2角色。
把足球宝贝爱莉希雅合进开箱场景 + 去掉看台国旗,保留开箱UI布局/世界杯礼盒/进度条/按钮。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒'
REF1=os.path.join(OUT,'WorldCup_reskin_byorig_pick1.png')          # 已有开箱UI reskin布局底
REF2=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\足球宝贝爱莉希雅_r5白金加徽章_v2.png'  # 足球宝贝主稿

PROMPT=(
 "This is a mobile game box-opening activity UI mockup, World Cup football theme. "
 "Use reference image 1 as the LAYOUT and scene base: keep the same vertical phone UI layout — top title bar, "
 "a central big soccer-patterned gift box with gold trophy ribbon as the focal element, a golden championship trophy beside it, "
 "a horizontal milestone progress bar with coin icons and x50/x100/x200... nodes, two big bottom buttons (开启1次 / 开启所有), "
 "and the bottom reward tab row. Football stadium with green pitch and bright lights as background. "
 "CHANGE 1: add the silver-white-haired cheerleader from reference image 2 (white-and-gold cheerleader outfit, holding pom-poms) "
 "standing in the scene to one side, integrated as the activity's character mascot. "
 "CHANGE 2: REMOVE all national flags, country flags and national symbols from the stadium stands — plain cheering crowd only. "
 "Gold-green-white World Cup palette, keep Chinese UI text, official mobile game activity screen mockup, high detail."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gemini','aspect_ratio':'9:16'},ensure_ascii=False),
           '--file',f'reference_images={REF1}','--file',f'reference_images={REF2}','--submit-only','--timeout','900'])
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
        dst=os.path.join(OUT,f'WorldCup_开箱reskin_含足球宝贝_v{i+1}.png')
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
