# -*- coding: utf-8 -*-
"""护航令3档效果图 AI reskin(出图doc §12 第4步)。
图#1=真组件拼装截图(布局锚,视觉ERASE) + 图#2=猎杀时刻真实界面(design system整套抄) → gemini 统一成品。
"""
import subprocess, json, sys, io, os, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
CG = r'C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py'
IMG1 = r'C:\ADHD_agent\KB\产出-交互原型\X3_护航令至尊档\_render_v2.png'   # 拼装布局(图#1)
IMG2 = r'C:\Users\linkang\Pictures\X3验收\BP新增档位\猎杀时刻.png'         # 真实界面(图#2)
OUT  = r'C:\ADHD_agent\KB\产出-交互原型\X3_护航令至尊档\护航令3档_AIreskin_v1.png'

PROMPT = (
"You are a game-UI RESKIN engine. Two reference images are given.\n"
"IMAGE #1 = LAYOUT/CONTENT reference ONLY. Take strictly its STRUCTURE: position & arrangement of every element, "
"all Chinese text labels, the number of columns and reward slots, icon placement, the level-progress rail. "
"EVERY visual aspect of image #1 (its flat colors, rough edges, placeholder/collage look) MUST be ERASED. Only the WHAT and WHERE survive.\n"
"IMAGE #2 = DESIGN SYSTEM source (a real in-game battlepass screenshot). Copy its ENTIRE visual language: "
"the wooden/parchment reward board texture, the golden reward-slot frames, the beige rounded column-header labels, "
"the golden diamond level nodes on a vertical rail, the gold purchase buttons, red discount badges, the pirate-woman hero painting, "
"the stormy ship/sea backdrop, the lighting, materials, ornate gold trim and fonts.\n"
"OUTPUT: ONE cohesive, seamless, polished GAME-QUALITY battlepass UI = image #1's layout fully re-rendered in image #2's visual style.\n"
"LAYOUT (3 reward tracks left-to-right): 免费 column (free, narrow/compressed, 1 slot) | a vertical progress rail of golden diamond level nodes (numbers 10/20/30/40) | 进阶 column (advanced, 1 slot, locked with a small lock) | 至尊 column (supreme, 2 slots, locked).\n"
"Top: pirate-woman hero on the right over a ship/sea background; title 獵殺時刻 with a countdown chip top-left; a short subtitle.\n"
"Top-right TWO gold purchase buttons stacked: 进阶护航 $9.99 and 至尊护航 $19.99, each with a small red discount badge.\n"
"Column headers read exactly: 免费 / 进阶 / 至尊 (进阶 and 至尊 headers carry a small lock). Keep ALL Chinese text verbatim.\n"
"Reward slots show VARIED game items (gems, gold coins, skill books, resources) — NOT the same item repeated.\n"
"STYLE: ornate pirate/tavern golden mobile-game UI matching image #2. NO painterly or brush-stroke look, crisp clean UI. "
"Vary the gold ornamentation naturally as in the reference; do not flatten."
)

def run(args):
    p = subprocess.run([sys.executable, CG] + args, capture_output=True, timeout=900)
    return p.returncode, p.stdout.decode('utf-8','replace'), p.stderr.decode('utf-8','replace')

BASE = 'https://grfal.tap4fun.com'
params = {"prompt": PROMPT, "model": "gemini", "aspect_ratio": "9:16"}
print("submitting reskin (gemini, 图#1拼装 + 图#2真实界面)...")
rc, out, err = run(['--tool','generate_image','--params',json.dumps(params,ensure_ascii=False),
                    '--file',f'reference_images={IMG1}','--file',f'reference_images={IMG2}','--submit-only'])
d = json.loads(out); tid = d['task_id']; print("task:", tid)
for i in range(60):
    time.sleep(15)
    rc, out, err = run(['--check-task', tid])
    try: d = json.loads(out)
    except Exception: print("poll parse err", out[-300:]); continue
    if isinstance(d.get('result'), list) and d['result']:
        urls = d['result']; print("done,", len(urls), "candidates")
        for j, u in enumerate(urls):
            full = u if u.startswith('http') else BASE + u
            dst = OUT.replace('.png', f'_{chr(97+j)}.png')
            urllib.request.urlretrieve(full, dst); print("saved:", dst)
        break
    print(f"poll {i+1}: {d.get('status','?')}")
else:
    print("timeout")
