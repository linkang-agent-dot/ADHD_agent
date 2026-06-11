# -*- coding: utf-8 -*-
"""焦点战(爆冷bonus)版效果图: 基于FINAL定稿叠焦点战层——
①「焦点之战」角标 ②弱势方侧爆冷加成标签 ③礼包柱多档并存(三档价格) ④底部最终解释权声明。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面'
REF=os.path.join(OUT,'竞猜界面_焦点战版v3_WinBonus_v1.png')

PROMPT=(
 "Use the reference image as the base and keep EVERYTHING identical: night stadium atmosphere, '焦点之战' ribbon badge, "
 "teams, rectangular banners, VS badge, gift chests, reward panels, 'US$19.99' price buttons, bottom notice bar. "
 "ONLY ONE CHANGE: REMOVE the centered '胜利加赠' strip below the VS zone — instead ATTACH the glowing green-gold "
 "'胜利加赠' label (with small golden ticket icon and '+40') to the LEFT team banner (Brazil side), "
 "docked at the bottom edge of the left rectangular banner like a fixed tag belonging to that team "
 "(clearly inside/attached to the left team's area, not floating in the center, not on the right side, not covering the crest). "
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
def flat(x):
    out=[]
    if isinstance(x,list):
        for i in x: out+=flat(i)
    elif isinstance(x,dict): out.append(x.get('url') or x.get('path') or '')
    elif isinstance(x,str): out.append(x)
    return [u for u in out if u]
def dl(paths):
    s=[]
    for i,u in enumerate(flat(paths),1):
        url=u if u.startswith('http') else BASE+u
        dst=os.path.join(OUT,f'竞猜界面_焦点战版v4_指定方加赠_v{i}.png')
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
