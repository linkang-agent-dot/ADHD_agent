# -*- coding: utf-8 -*-
"""世界杯开箱 reskin v7：以V5_v1为基准,人物大小/比例/居中原样不动(用户要求按V5),
仅:①礼盒缩小+下移到脚前(只压脚踝不挡身体) ②旁边背景加一个小金奖杯填空。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒'
REF=os.path.join(OUT,'WorldCup_开箱reskin_v5_照原布局_v1.png')  # V5:人物比例正确,作基准

PROMPT=(
 "Use the reference image as the base and keep the CHARACTER EXACTLY as-is: same silver-white-haired white-and-gold cheerleader, "
 "SAME SIZE, SAME PROPORTION, SAME centered position as in the reference — do NOT shrink, enlarge or move the character. "
 "Keep the World Cup football-stadium background (no national flags), the top status bar, the title and description text (fully visible, unobstructed), "
 "the horizontal milestone progress bar with x50..x3000 coin nodes, the two bottom buttons (开启1次/开启所有), the bottom reward tab row, and the Chinese UI text. "
 "ONLY TWO CHANGES: "
 "(1) make the soccer-patterned gift box SMALLER and move it slightly LOWER so it sits in front at the bottom-center, "
 "overlapping ONLY the character's feet / lower shins — it must NOT cover her torso, waist or chest. "
 "(2) add ONE SMALL golden championship trophy in the background beside the character as a subtle filler element to fill empty space "
 "(keep it small, it must NOT dominate or upstage the gift box or the character). "
 "Everything else stays identical to the reference. Official mobile game activity screen mockup, high detail."
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
        dst=os.path.join(OUT,f'WorldCup_开箱reskin_v7_V5比例+礼盒下移+小奖杯_v{i+1}.png')
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
