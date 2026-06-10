# -*- coding: utf-8 -*-
"""竞猜二选一界面 X3风格 v2（按用户反馈）：
框架=X3真实界面「怦然心动」(验收截图,design system)；绿茵场背景；足球主题宝箱(世界杯礼盒)；
队徽=真实国家队风格(巴西vs阿根廷,用户已放开)；结构=已确认的二选一结构稿。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面'
REF1=os.path.join(OUT,'竞猜二选一界面_v1_2.png')                          # 布局/内容源(结构已确认)
REF2=r'C:\Users\linkang\Pictures\X3验收\夏日\怦然心动.png'                  # X3真实UI框架=design system
REF3=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯礼盒\WorldCup_box1_pick2_trans.png'  # 足球宝箱

PROMPT=(
 "I am providing THREE reference images. Complete visual style transfer task. "
 "Reference image #1 = LAYOUT & CONTENT SOURCE only. Extract ONLY the structure: "
 "top title '胜负预言 · 32强' with countdown chip '距开赛锁盘 17:43:06'; a VS zone with two national-team crests and team names; "
 "two mirrored cheer-pack columns (chest, raffle-ticket row x30, resource rows, bonus line '猜对加送 +20' with a small golden ticket icon before '+20', "
 "price button 'US$4.99'); bottom notice '每场仅可选一方助威，购买后锁定不可更改'. "
 "ERASE every visual aspect of image #1 — only WHAT and WHERE survives. "
 "Reference image #2 = the game's REAL UI, the COMPLETE VISUAL STYLE SOURCE: copy its panel framing, ornate golden border treatment, "
 "title banner style, countdown chip style, item-slot rendering, price-button rendering, tab/notice bar styling, overall material finish and color grading. "
 "Reference image #3 = the soccer-patterned gift chest with golden trophy ribbon: use THIS chest design as the pack chest in both columns. "
 "SCENE CHANGES: the background must be a bright green FOOTBALL PITCH stadium scene (grass field, stadium lights, World Cup festive atmosphere), "
 "NOT an indoor tavern; the whole UI dressing carries football World Cup theming (subtle soccer-ball / trophy / laurel accents on frames). "
 "TEAMS: left = Brazil-style national team crest with yellow-green theme, name '巴西'; right = Argentina-style national team crest with sky-blue-white theme, name '阿根廷'; "
 "golden VS badge between them. Keep all Chinese UI text readable. "
 "Vertical mobile game UI mockup, official quality, high detail."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit():
    r=run(['--tool','generate_image','--params',json.dumps({'prompt':PROMPT,'model':'gpt','aspect_ratio':'9:16'},ensure_ascii=False),
           '--file',f'reference_images={REF1}','--file',f'reference_images={REF2}','--file',f'reference_images={REF3}','--submit-only','--timeout','900'])
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
        dst=os.path.join(OUT,f'竞猜二选一界面_X3风格v2_{i+1}.png')
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
