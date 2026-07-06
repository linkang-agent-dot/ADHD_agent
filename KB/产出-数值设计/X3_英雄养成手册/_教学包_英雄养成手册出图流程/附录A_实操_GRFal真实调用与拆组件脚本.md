---
tags: [kind/交接, domain/配置换皮, proj/X3, year/2026-06]
---

# 附录 A · 实操：GRFal 真实调用 + 拆组件全链路（能照着跑）

> 同事反馈：方法讲清了，但「实际怎么调」缺。这份补全 —— 真实调用接口、Morphix 拆组件 4 步全链路（含 prompt 全文 + 切块代码）、可复用脚本清单。
> 配套脚本全在本教学包 `脚本可复用\`，改 REF/PROMPT/OUT 即可复跑。

---

## 0. 底层就一个 CLI：`call_grfal.py`

「Morphix」不是独立工具，本质是 **GRFal 的一层 prompt 前处理**——底层只调 3 个 GRFal 工具（`generate_image` / `describe_media` / `remove_background`）。所以**所有出图/拆图，最终都是命令行调 `call_grfal.py`**。

| 项 | 值 |
|---|---|
| CLI | `C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py` |
| cookie | 读 `C:\ADHD_agent\.cursor\skills\x2-media\config.json` 的 `grfal_cookie` 字段，注入 env `GRFAL_COOKIE` |
| base url | `https://grfal.tap4fun.com`（result 是相对路径要拼这个前缀） |
| 工具目录 | `C:\ADHD_agent\.cursor\skills\grfal-api\references\tool_catalog.md`（39 个工具全参数） |

### 三种调用模式（关键：图片工具是 async，必须 submit-only 轮询）
```bash
# 列工具
python call_grfal.py --list-tools

# 同步（仅快工具如 remove_background 可用；generate_image 用 --sync 会 300s 硬超时）
python call_grfal.py --tool remove_background --file image_paths=C:\x.png

# ★ async：submit-only 拿 task_id → --check-task 轮询（generate_image 必走这条）
python call_grfal.py --tool generate_image \
  --params "{\"prompt\":\"...\",\"model\":\"gemini\",\"aspect_ratio\":\"9:16\"}" \
  --file reference_images=C:\img1.png --file reference_images=C:\img2.png --submit-only
python call_grfal.py --check-task <task_id>
```

### 调用骨架（每个生图脚本都这套，照抄）
```python
import json, subprocess, os, time, urllib.request, ssl, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')  # 防 GBK 控制台崩
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json', encoding='utf-8'))['grfal_cookie']
CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
BASE = 'https://grfal.tap4fun.com'

def submit(tool, params, files):           # 提交拿 task_id
    cmd = ['--tool',tool,'--params',json.dumps(params,ensure_ascii=False)]
    for f in files: cmd += ['--file', f]
    out = subprocess.run(['python',CALL]+cmd+['--submit-only','--timeout','900'],
                         capture_output=True).stdout.decode('utf-8','replace')
    return json.loads(out).get('task_id')

def poll(tid):                             # 每 15s 轮询，拿 result（url 列表）
    for i in range(80):
        time.sleep(15)
        out = subprocess.run(['python',CALL,'--check-task',str(tid)],capture_output=True).stdout.decode('utf-8','replace')
        d = json.loads(out) if out.strip().startswith('{') else {}
        if isinstance(d.get('result'), list) and d['result']: return d['result']
        if d.get('status') in ('failed','error','FAILURE'): return None
    return None

def download(urls, out_dir, prefix):       # 下载（必须带 cookie，否则 401）
    for i,u in enumerate(urls):
        url = u if u.startswith('http') else BASE+u
        req = urllib.request.Request(url, headers={'Cookie':os.environ['GRFAL_COOKIE']})
        with urllib.request.urlopen(req, context=ssl._create_unverified_context()) as r:
            open(os.path.join(out_dir,f'{prefix}_{i+1}.png'),'wb').write(r.read())
```

---

## 1. ★拆组件（Morphix E 元素拆分）全链路 4 步 —— 同事最想要的这块

**目标**：把一张界面效果图，拆成「一件件原子 UI 组件」的透明 PNG（图标/按钮/边框/格子…），给美术/程序直接用。

### 链路总览
```
效果图 ──①generate_image(gpt)+buildSplitPrompt──► #B8B8B8 灰底雪碧图（所有组件平铺）
       ──②remove_background──► 透明雪碧图
       ──③PIL 连通域投影切块──► 一件件原子 PNG
       ──④describe_media 分类 + 命名归档──► 按槽位命名的组件库
```
> 脚本：①② = `脚本可复用\01_拆组件_出灰底雪碧图+去底_gen_split_fixed.py`；③ = `脚本可复用\02_拆组件_连通域切块_split_blocks.py`

### 第①步 出灰底雪碧图（buildSplitPrompt 的核心约束，照着改）
关键不是模型，是 **prompt 把"拆什么/原子化/去重/灰底"说死**。世界杯竞猜界面实测的真实 prompt（直接复用，改组件清单即可）：
```text
This is a UI ART ASSET extraction task. The output is a sprite sheet for game artists / developers.
From the reference game UI, extract ONLY these FIXED UI components as GRAPHIC ART ASSETS, each EMPTY with NO text and NO numbers:
1) the top ornate green-gold title banner plate (EMPTY, no Chinese text, keep laurel/ribbon ornaments);
2) the countdown pill/chip plate (empty, keep hourglass ornament as separate icon);
3) the golden circular VS badge (the VS lettering is part of the badge emblem art, keep it);
4) the tall cream/parchment reward panel plate with golden frame (EMPTY inside, no items);
5) the golden pill price button (empty, no price text);
6) one reward slot square frame (single empty tile frame, deduplicated);
7) the golden ticket icon (the raffle ticket star icon alone).
DECOMPOSE compound widgets into atomic parts; STRICT DEDUPLICATION (each unique element once, mirror copies keep one);
do NOT redraw or recolor — preserve each element's exact original style from the reference.
Layout: tidy rows by category with at least 20px padding between elements.
OUTPUT BACKGROUND — CRITICAL: uniform light gray solid #B8B8B8 (184,184,184) filling the whole image.
Do NOT use white, off-gray, gradient, cream, paper, checkerboard or any pattern.
Output: a single high-res sprite sheet with ATOMIC, DEDUPLICATED assets on uniform #B8B8B8. No text strings, no numbers.
```
**4 条不能省的约束**（漏一条就翻车）：
1. **#B8B8B8 灰底**（不是白底！）—— 白/浅底抠图会留白边，灰底干净。
2. **原子化 + 严格去重** —— 复合控件拆成最小件，镜像件只留一个。
3. **EMPTY / no text / no numbers** —— 出"空壳"组件，文字走 TextKey 层别烤进图。
4. **don't redraw or recolor** —— 保原始风格，别让 AI 重画。
> 模型用 `gpt`（拆图保真好），`aspect_ratio` 按组件多少给 `3:4`。

### 第②步 去底 `remove_background`
```python
r = call_sync('remove_background', {}, [f'image_paths={灰底雪碧图}'])
# ⚠️ result 可能是嵌套 list [[url],null]，要解开；去底后验真透明（RGBA alpha 有 0-255）
```

### 第③步 PIL 连通域切块（纯本地，零 AI）—— `split_blocks.py` 核心
透明雪碧图按 alpha 投影递归分割成一件件：
```python
from PIL import Image; import numpy as np
im = Image.open('透明雪碧图.png').convert('RGBA')
a = np.array(im.getchannel('A')); mask = a > 10

def segments(proj, gap=18):                  # 一维投影 → 连续段（gap 内间断合并）
    idx = np.where(proj)[0]
    if len(idx)==0: return []
    segs=[]; s=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i-prev>gap: segs.append((s,prev)); s=i
        prev=i
    segs.append((s,prev)); return segs

blocks=[]
for (r0,r1) in segments(mask.any(axis=1)):   # 先按行带切
    band=mask[r0:r1+1]
    for (c0,c1) in segments(band.any(axis=0)):  # 行带内再按列切
        # …收紧到真实 bbox，过滤 <24px 噪点…
        blocks.append((r0,c0,r1,c1))
# 每块 crop + pad 存 raw_NN_WxH.png
```

### 第④步 分类命名归档
`describe_media` 给每块分类，或人工按槽位命名（`F1_标题横幅_九宫格_无字.png`）+ 写 README 映射规格表（目标尺寸/九宫格 vs 整图/数量）。

> **实证产物**：世界杯竞猜界面 9 件原子组件 `KB\产出-本地化与美术\X3\世界杯竞猜界面\切图\`。

---

## 2. ★换皮出图（reskin）真实调用 —— `gen_reskin.py`

图#1 拼装截图（布局锚·视觉 ERASE）+ 图#2 真实界面（design system 整套抄）→ gemini 出成品。**护航令 3 档实测的真实 buildReskinPrompt 全文**（复用骨架，改 LAYOUT 段）：
```text
You are a game-UI RESKIN engine. Two reference images are given.
IMAGE #1 = LAYOUT/CONTENT reference ONLY. Take strictly its STRUCTURE: position & arrangement of every element,
all Chinese text labels, the number of columns and reward slots, icon placement, the level-progress rail.
EVERY visual aspect of image #1 (its flat colors, rough edges, placeholder/collage look) MUST be ERASED. Only the WHAT and WHERE survive.
IMAGE #2 = DESIGN SYSTEM source (a real in-game screenshot). Copy its ENTIRE visual language:
the board texture, the golden reward-slot frames, the column-header labels, the level nodes, the gold buttons,
red discount badges, the hero painting, the backdrop, the lighting, materials, ornate gold trim and fonts.
OUTPUT: ONE cohesive, seamless, polished GAME-QUALITY UI = image #1's layout fully re-rendered in image #2's visual style.
LAYOUT (...逐项把布局/列数/文案/按钮写死...). Keep ALL Chinese text verbatim.
STYLE: ornate golden mobile-game UI matching image #2. NO painterly or brush-stroke look, crisp clean UI.
Vary the gold ornamentation naturally as in the reference; do not flatten.
```
调用关键：
```python
params = {"prompt": PROMPT, "model": "gemini", "aspect_ratio": "9:16"}
run(['--tool','generate_image','--params',json.dumps(params,ensure_ascii=False),
     '--file',f'reference_images={IMG1拼装}','--file',f'reference_images={IMG2真实界面}','--submit-only'])
# 轮询拿 result（多候选 url），逐个下载成 _a.png/_b.png
```
> 脚本：`脚本可复用\03_reskin换皮_图1拼装+图2真界面_gen_reskin.py`。**X3 调优必加**：NO painterly/笔触；金饰列举多种别单点名；中文逐字保留。

---

## 3. 横竖转换（竞品方向不对时，reskin 前先转）
Morphix `buildFlipPrompt`：reference=竞品截图，gemini，aspect=目标方向，**只翻布局不换风格**（关闭键/货币/标题按目标方向重排、网格列数 reflow、轴向翻转、文字逐字留）。产出竖屏结构稿后再当图#1 走第 2 节 reskin。
> 全文 + 另 7 个 build*Prompt：`KB\方法论\Morphix换皮工具逆向_prompt库.html`（分页签，含框架流程图）。

---

## 4. 可复用脚本清单（本包 `脚本可复用\`，下次改 3 个变量复跑）

| 脚本 | 干什么 | 改哪 3 个变量 |
|---|---|---|
| `01_拆组件_出灰底雪碧图+去底_gen_split_fixed.py` | 效果图 → 灰底雪碧图 → 去底 | `REF`(效果图) / `PROMPT`(组件清单) / `OUT` |
| `02_拆组件_连通域切块_split_blocks.py` | 透明雪碧图 → 一件件原子 PNG | `SRC`(透明雪碧图) |
| `03_reskin换皮_图1拼装+图2真界面_gen_reskin.py` | 拼装+真界面 → 成品效果图 | `IMG1` / `IMG2` / `PROMPT` 的 LAYOUT 段 |
| `00_单图换皮_gen_focal.py` | 单张换皮参考 | 同上 |

---

## 5. 踩坑清单（调用层最值钱）
1. `generate_image` 是 **async** → 必须 `--submit-only` + `--check-task` 轮询；加 `--sync` 会 300s 硬超时。
2. python 脚本 `print` 中文 → Windows GBK 控制台 `UnicodeEncodeError` 崩（任务没崩只是 print 炸）→ 必加 `sys.stdout=io.TextIOWrapper(...,encoding='utf-8',errors='replace')`。
3. cookie 要手工注入 `GRFAL_COOKIE`（call_grfal 不自动读 config）；**下载也要带 cookie 否则 401**。
4. result 是**相对路径**要拼 `https://grfal.tap4fun.com`；`remove_background` result 可能是嵌套 list `[[url],null]` 要解开。
5. 多图参考：`--file reference_images=` 写多次 = 多图（append 生效）。
6. 模型：`gpt` 保身份/拆图质量好但慢；`gemini` 快/稳/保布局好 → 拆图/换装用 gpt，UI 换皮用 gemini。
7. 拆图灰底**必须 #B8B8B8**，白底/浅底会留白边。
8. chrome 无头渲染拼装 HTML 时**中文路径 file:// 会 ERR_FILE_NOT_FOUND** → 拷 html+_assets 到纯 ASCII 临时目录再渲染。

---
> 权威源：`KB\方法论\X3_AI出图工作流…世界杯案.md` §0/§11/§12 + `KB\方法论\Morphix换皮工具逆向_prompt库.html` + `memory\reference_morphix_reskin_prompts.md`。本附录是教学可执行版。
