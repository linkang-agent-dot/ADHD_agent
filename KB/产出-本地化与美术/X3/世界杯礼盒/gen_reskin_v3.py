# -*- coding: utf-8 -*-
"""世界杯开箱 reskin v3：去掉大力神杯+足球,足球宝贝人物站后面当主体大图(占C位),礼盒在前当开箱焦点。
三参考: 原始UI(构图锚:大角色在后+礼盒在前+UI布局) + 足球宝贝V2(角色) + 足球礼盒(透明)。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒'
REF1=os.path.join(OUT,'orig_ui.png')                                 # 构图锚:大角色在后+礼盒在前+完整UI
REF2=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\足球宝贝爱莉希雅_r5白金加徽章_v2.png'  # 角色主体
REF3=os.path.join(OUT,'WorldCup_box1_pick2_trans.png')               # 足球礼盒

PROMPT=(
 "Mobile game box-opening activity UI mockup, World Cup football theme. "
 "Use reference image 1 ONLY for the UI LAYOUT and composition: a tall character art filling the upper-center/back as the MAIN hero element, "
 "a gift box placed IN FRONT of the character at lower-center as the box-opening focal point, "
 "top title bar, a horizontal milestone progress bar with coin icons and x50/x100/x200... nodes, "
 "two big bottom buttons (开启1次 / 开启所有), and the bottom reward tab row. "
 "MAIN ELEMENT: the silver-white-haired cheerleader from reference image 2 (white-and-gold cheerleader outfit, pom-poms) "
 "stands tall in the back/upper-center as the dominant hero figure of the screen. "
 "FOCAL OBJECT: the soccer-patterned gift box with gold trophy ribbon from reference image 3, placed in front of her at lower-center. "
 "IMPORTANT: do NOT include any large standalone championship trophy and do NOT include a separate loose soccer ball — "
 "the character is the main element, the gift box is the focal object. "
 "Background: a sunny football stadium with green pitch, NO national flags or country symbols (plain cheering crowd). "
 "Gold-green-white World Cup palette, keep Chinese UI text, official mobile game activity screen mockup, high detail."
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
        dst=os.path.join(OUT,f'WorldCup_开箱reskin_人物主体_v{i+1}.png')
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
