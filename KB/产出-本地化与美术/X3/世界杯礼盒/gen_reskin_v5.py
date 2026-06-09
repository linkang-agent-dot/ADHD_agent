# -*- coding: utf-8 -*-
"""世界杯开箱 reskin v5：按原图人物布局——角色=中等场景插画,置于顶栏+标题文字带下方的场景区,
不顶到/不被文字遮挡,比例协调;礼盒在前居中。三参考:原UI(布局/人物尺寸位置锚)+足球宝贝V2(角色)+足球礼盒。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒'
REF1=os.path.join(OUT,'orig_ui.png')                                 # 布局+人物尺寸位置锚
REF2=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\足球宝贝爱莉希雅_r5白金加徽章_v2.png'
REF3=os.path.join(OUT,'WorldCup_box1_pick2_trans.png')

PROMPT=(
 "Mobile game box-opening activity UI mockup, World Cup football theme. "
 "Follow reference image 1 (original UI) for the LAYOUT and ESPECIALLY the character placement & size: "
 "the hero character is a MEDIUM-sized scene illustration placed in the UPPER-MIDDLE scene area, "
 "positioned FULLY BELOW the top status bar and below the activity title/description text band — "
 "the top title and the description text must stay completely visible and UNOBSTRUCTED, the character must NOT overlap or cover any UI text. "
 "The character is integrated as background scene art, well-proportioned and harmonious; "
 "do NOT make her an oversized figure that fills or spills out of the screen. "
 "Replace the original scene character with the silver-white-haired white-and-gold cheerleader from reference image 2 (keep her identity and outfit). "
 "Place the soccer-patterned gift box with gold ribbon from reference image 3 in FRONT at the center-lower scene area, in front of the character. "
 "Keep the rest of the UI from reference 1: top bar, horizontal milestone progress bar with x50..x3000 coin nodes, "
 "two bottom buttons (开启1次/开启所有), bottom reward tab row, Chinese UI text. "
 "Background: football stadium with green pitch, NO national flags or country symbols. "
 "No large standalone trophy. Gold-green-white World Cup palette, official mobile game activity screen mockup, high detail."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gemini','aspect_ratio':'9:16'},ensure_ascii=False),
           '--file',f'reference_images={REF1}','--file',f'reference_images={REF2}','--file',f'reference_images={REF3}','--submit-only','--timeout','900'])
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
        dst=os.path.join(OUT,f'WorldCup_开箱reskin_v5_照原布局_v{i+1}.png')
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
