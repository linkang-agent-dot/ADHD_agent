# -*- coding: utf-8 -*-
"""世界杯抽奖券icon重出: 带足球元素(票面星星→黑白足球)。ref=现有金票(风格/形状锚)。
①generate_image灰底 ②remove_background ③验真透明+裁方128。"""
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL=r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE='https://grfal.tap4fun.com'
OUT=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\切图'
REF=os.path.join(OUT,'icon_抽奖券_底稿.png')

PROMPT=(
 "Use the reference golden raffle ticket icon as the STYLE and SHAPE anchor: same golden ticket silhouette with notched edges, "
 "same gold material, gloss and outline rendering, same game-item-icon style. "
 "ONLY ONE CHANGE: replace the star emblem on the ticket face with a classic BLACK-AND-WHITE SOCCER BALL (pentagon pattern), "
 "nicely embossed/printed on the gold ticket, slightly tilted for energy; optionally tiny laurel accents around it. "
 "World Cup gold-green premium feel. Single item icon, centered, large in frame. "
 "OUTPUT BACKGROUND — CRITICAL: uniform light gray solid #B8B8B8 (184,184,184) filling the whole image, "
 "no white, no gradient, no pattern. No text, no numbers."
)

def run(a): return subprocess.run(['python',CALL]+a,capture_output=True,text=False,timeout=950)
def submit(tool,params,files=None):
    cmd=['--tool',tool,'--params',json.dumps(params,ensure_ascii=False)]
    for f in (files or []): cmd+=['--file',f]
    r=run(cmd+['--submit-only','--timeout','900'])
    out=r.stdout.decode('utf-8','replace'); print(f'[{tool} submit]',out[:200])
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
def dl(paths,prefix):
    s=[]
    for i,u in enumerate(flat(paths),1):
        url=u if u.startswith('http') else BASE+u
        dst=os.path.join(OUT,f'{prefix}_{i}.png')
        req=urllib.request.Request(url,headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=90) as resp:
            open(dst,'wb').write(resp.read())
        print('SAVED',dst); s.append(dst)
    return s

tid=submit('generate_image',{'prompt':PROMPT,'model':'gpt','aspect_ratio':'1:1'},[f'reference_images={REF}'])
if not tid: print('SUBMIT FAIL'); sys.exit(1)
res=poll(tid)
if not res: print('NO RESULT'); sys.exit(1)
gray=dl(res,'抽奖券足球版_灰底')
# 去底(两张都去,用户挑)
for g in gray:
    cmd=['--tool','remove_background','--params','{}','--file',f'image_paths={g}','--timeout','600']
    out=run(cmd).stdout.decode('utf-8','replace')
    try: d=json.loads(out)
    except: d={}
    r=d.get('result') or d.get('output')
    if r: dl(r, os.path.basename(g).replace('_灰底','_透明').replace('.png',''))
    else: print('rmbg fail for',g,out[:150])
# 验真透明
from PIL import Image
for f in os.listdir(OUT):
    if '抽奖券足球版_透明' in f:
        im=Image.open(os.path.join(OUT,f))
        a=im.getchannel('A').getextrema() if im.mode=='RGBA' else None
        print(f, im.size, im.mode, 'alpha:',a)
print('DONE')
