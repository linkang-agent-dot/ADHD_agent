---
name: x3-grfal-banner
description: 用 GRFal API 给 X3 节日活动 banner / 主背景出图全流程；含 cookie 取法、async polling、reference 注入、保存路径、DK 落地
metadata: 
  node_type: memory
  type: workflow
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## 工具链

| 组件 | 路径 |
|------|------|
| **入口 skill** | `C:/ADHD_agent/.cursor/skills/x2-media/SKILL.md`（含 type router / default styles / available models） |
| **call_grfal.py** | `C:/ADHD_agent/.cursor/skills/grfal-api/scripts/call_grfal.py` |
| **GRFAL_COOKIE 来源** | `C:/ADHD_agent/.cursor/skills/x2-media/config.json` 里 `grfal_cookie` 字段 |
| **GRFal base URL** | `https://grfal.tap4fun.com` |

## 调用方式

```python
import json, subprocess, os
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json'))['grfal_cookie']

CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
params = {'prompt': '...', 'model': 'gpt', 'aspect_ratio': '1:1'}

r = subprocess.run([
    'python', CALL,
    '--tool', 'generate_image',
    '--params', json.dumps(params, ensure_ascii=False),
    '--file', f'reference_images={ref_image_path}',  # 可选：注入参考图（自动 base64）
    '--timeout', '900',
    # 注意：不要加 --sync！会触发 300s 同步超时；默认 async polling 才能跑长任务
], capture_output=True, text=False, timeout=950)
```

**返回**：`{"result": ["/api/output/image_generation/YYYY-MM-DD/N_0_0.png", ...], "success": true}`，通常 2 张候选。

## 下载

URL 拼 base：`https://grfal.tap4fun.com{relative_path}`。下载时也要带 Cookie header。

```python
import urllib.request, ssl
req = urllib.request.Request(url, headers={'Cookie': os.environ['GRFAL_COOKIE']})
with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=60) as r:
    open(local_path, 'wb').write(r.read())
```

## 关键坑

1. **必须设 `GRFAL_COOKIE` 环境变量**——`call_grfal.py` 不自动读 config.json，要手工注入
2. **不要加 `--sync`**——同步模式 300s 硬超时；async polling 能跑长任务（GPT 模型生图常 1-3 分钟）
3. **`--file reference_images=path`** 可注入参考图（自动 base64），用于"按这张图风格"出图
4. **GPT 默认返回 2 张候选**（不是 1 张）
5. **下载也要带 cookie**，否则 401

## 节日 Banner 出图 prompt 模板

参考黑猫神龛 Pack 210616.MainBg = `DK_img_Activity_Egypt_bg_19` 的构图（节日主体居中 + 周围环境 + 边缘渐隐透明 + 1:1）：

```
game environment, atmospheric lighting, detailed background, fantasy or modern setting, wide composition,
romantic <theme> themed gift pack background painting,
centered composition featuring the iconic <主体> as the main focal point
(use reference image exactly: <主体细节描述>, preserve the cartoon stylized 3D rendered look),
<环境描述：周围场景 / 远景 / 天气 / 时间>,
ENTIRE IMAGE softened with watercolor wash texture and warm dreamy glow,
edges fade dramatically into transparent background creating a vignette frame effect,
no harsh outlines, no foreground objects, no characters, no items,
square 1:1 aspect ratio with pronounced transparent edge fade-out on all sides
```

## 保存路径规范

| 项目 | 根路径 |
|------|--------|
| X3 节日活动主背景 | `C:\ADHD_agent\KB\产出-本地化与美术\X3\活动主背景\` |
| X2 节日活动主背景 | `C:\ADHD_agent\KB\产出-本地化与美术\X2\...\` |

**命名约定**：`{活动名}_{模型}_{YYYYMMDD_HHMMSS}_v{N}.png`，例 `夏日柔情海湾_gpt_20260527_103412_pick2.png`。

## 落地到 X3 客户端的完整链路

```
1. GRFal 生图 → 下载到 C:\ADHD_agent\KB\产出-本地化与美术\X3\活动主背景\
2. 用户选定其中 1 张 → 复制到 C:\x3-project\client\Assets\Res\UI\Spirits\ActivityImg_Download\img_Activity_<节日>_bg_<N>.png
3. Unity 打开 → 自动 import 生成 .meta（GUID）
4. 编辑 Assets/Res/Config/DisplayKey/Path_Activity.asset 加 DK→path 双列表 (详见 [[reference_x3_client_resources]])
   或在 Unity 菜单 Config/Display Key (Ctrl+T) 面板里加
5. git commit + push (feature branch + MR，因 dev 受保护，详见 [[workflow_x3_protected_branch_mr]])
6. gdconfig 配置 Pack/ActvOnline 字段 = 新 DK
7. push gdconfig + jolt 导表
```

## 实战案例（2026-05-27 X3 夏日柔情海湾 Pack 210921）

| 项 | 内容 |
|----|------|
| Prompt 主题 | 红顶白屋小岛 + 心形气球 + 椰林 + 夕阳海面 + 玫瑰花瓣 |
| Reference 注入 | `C:\x3-project\client\Assets\Res\UI\Spirits\ItemIcons\icon_island_ValentinesDay.png`（柔情海湾岛屿官方素材）|
| 模型 | gpt（GPT 模型，约 1-2 分钟 / 2 张）|
| 输出 | `夏日柔情海湾_v2_20260527_103412_pick2.png` (5 MB) |
| 落地 DK | `DK_img_Activity_summer_bg_12` |
| 客户端 commit | `9122ca5cecc` dev-summer-love-song / [MR !224](https://git.tap4fun.com/x3/x3-project/-/merge_requests/224) → dev |
| gdconfig 配置 | `Pack.210921.MainBg = DK_img_Activity_summer_bg_12` (commit `1d057bb`) |

## 相关

- 节日活动构图参考：黑猫神龛 `DK_img_Activity_Egypt_bg_19`（Pack 210616）
- DK 注册详细操作：[[reference_x3_client_resources]]
- 受保护分支 MR 流程：[[workflow_x3_protected_branch_mr]]
- jolt 自动导表：[[workflow_x3_auto_jolt_export]]
