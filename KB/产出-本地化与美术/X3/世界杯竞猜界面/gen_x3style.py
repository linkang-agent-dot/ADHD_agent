# -*- coding: utf-8 -*-
"""竞猜二选一界面 → X3 UI 风格换皮。Morphix buildReskinPrompt 职责切分法:
图#1=布局/内容(竞猜结构图v1_2,视觉ERASE) 图#2=X3真实UI(orig_ui天马藏宝阁=design system)。
X3调优:BAN painterly/笔触;金色装饰列举多种;参考图能说明的不写。附加:猜对加送行加抽奖券icon。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面'
REF1=os.path.join(OUT,'竞猜二选一界面_v1_2.png')                       # 布局+内容源
REF2=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒\orig_ui.png'   # X3 design system

PROMPT=(
 "I am providing TWO reference images. This is a complete visual style transfer task. "
 "Reference image #1 = LAYOUT & CONTENT SOURCE. From image #1, extract ONLY: "
 "the structural arrangement (top title bar with countdown chip; a diagonal split VS zone with two team crests, "
 "team names '红鹰队' and '蓝狮队' and a central VS badge; two mirrored cheer-pack columns each with a chest, "
 "a raffle-ticket item row 'x30', resource item rows, a bonus line '猜对加送 +20', a price button 'US$4.99'; "
 "a bottom notice bar '每场仅可选一方助威，购买后锁定不可更改'); the text labels and what they say; "
 "what each icon represents semantically. DISCARD EVERYTHING ELSE about image #1: its background color, panel color, "
 "border style, ornaments, button shapes and colors, font choice, color palette, icon rendering style — "
 "every visual aspect of image #1 must be ERASED. Only the WHAT and WHERE survives, never the HOW IT LOOKS. "
 "Reference image #2 = COMPLETE VISUAL STYLE SOURCE (this game's real UI). From image #2, copy EVERY visual aspect: "
 "background and panel color/texture, frame and border treatment, the varied golden ornamental details as they appear in the reference, "
 "section heading typography, button rendering (shape, gradient, depth, outline), item-slot rendering, "
 "progress/notice bar styling, the overall material feel of the panels. "
 "ADDITIONAL REQUIREMENTS: ① on each '猜对加送 +20' bonus line, place a small golden raffle-ticket ICON right before '+20' "
 "(same ticket icon as the x30 item row) so the bonus clearly reads as ticket reward; "
 "② team crests stay ORIGINAL stylized football club shields (eagle / lion), absolutely NO real national flags or emblems; "
 "③ keep all Chinese UI text readable. Vertical mobile screen, official game UI mockup, high detail."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gpt','aspect_ratio':'9:16'},ensure_ascii=False),
           '--file',f'reference_images={REF1}','--file',f'reference_images={REF2}','--submit-only','--timeout','900'])
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
        dst=os.path.join(OUT,f'竞猜二选一界面_X3风格_v{i+1}.png')
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
