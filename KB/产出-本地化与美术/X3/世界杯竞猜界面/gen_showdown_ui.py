# -*- coding: utf-8 -*-
"""世界杯竞猜二选一界面效果图：SHOWDOWN对抗框架×互斥礼包逻辑(结构定稿v0.8)。
参考1=宝藏三选一(互斥提示/倒计时/柱状礼包) 参考2=FC26 SHOWDOWN(左右斜切VS对抗)。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面'
REF1=os.path.join(OUT,'参考2_FC26_SHOWDOWN_对抗VS.png')   # 主构图锚:VS对抗
REF2=os.path.join(OUT,'参考1_宝藏三选一_互斥结构.png')      # 礼包柱/倒计时/互斥提示锚

PROMPT=(
 "Mobile game match-prediction screen mockup (vertical 9:16), World Cup football theme, cartoon stylized game UI. "
 "STRUCTURE (combine the two references): "
 "TOP: title bar '胜负预言 · 32强' and a countdown chip '距开赛锁盘 17:43:06' (like reference 2's timer). "
 "MIDDLE: a dramatic diagonal split VS zone like reference 1: left half in RED team theme color with an ORIGINAL stylized football crest "
 "and Chinese team name text '红鹰队', right half in BLUE team theme color with a different ORIGINAL stylized crest and team name '蓝狮队', "
 "a golden 'VS' badge at the center of the diagonal split. "
 "STRICT: crests are ORIGINAL fantasy football club style — absolutely NO real national flags, NO national emblems, NO real club logos, NO player photos; "
 "use stylized mascot/shield crests only. "
 "BOTTOM: two mirrored symmetric cheer-pack columns (like reference 2's pack columns), one under each team side: "
 "each column shows a small gift chest, item rows (golden raffle ticket icon x30, resource icons), a highlighted bonus line '猜对加送 +20', "
 "and an orange price button 'US$4.99'. Both columns identical price and contents, only the team differs. "
 "VERY BOTTOM: a notice bar '每场仅可选一方助威，购买后锁定不可更改'. "
 "Gold-green-white World Cup accents, football stadium subtle background, Chinese UI text, official mobile game UI mockup, high detail."
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
        dst=os.path.join(OUT,f'竞猜二选一界面_v1_{i+1}.png')
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
