---
tags: [kind/交接, domain/配置换皮, proj/X3, year/2026]
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
| **★认证（2026-06-12 改）** | **走 `~/.config/grfal-api/token_store.json` 的 Bearer access_token（长效到2036），call_grfal 没有 GRFAL_COOKIE 时自动 fallback 到它——什么都不用设**。旧的 cookie 注入法已废（session cookie 内嵌 token 只活几天）。User 级环境变量 `GRFAL_COOKIE` 已删除；脚本统一开头 `os.environ.pop('GRFAL_COOKIE', None)` 兜底防复活 |
| **GRFal base URL** | `https://grfal.tap4fun.com` |

## 调用方式

```python
import json, subprocess, os
os.environ.pop('GRFAL_COOKIE', None)  # 防过期cookie顶掉token_store的长效Bearer
TOKEN = json.load(open(os.path.expanduser('~/.config/grfal-api/token_store.json')))['access_token']

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

URL 拼 base：`https://grfal.tap4fun.com{relative_path}`。下载带 **Bearer** 头。

```python
import urllib.request, ssl
req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=60) as r:
    open(local_path, 'wb').write(r.read())
```

## 关键坑

1. ~~必须设 GRFAL_COOKIE~~ **（已废,2026-06-12）：什么都别设，call_grfal 自动 fallback token_store Bearer**；反而要防环境里残留过期 cookie（优先级更高会顶掉 token→401）。验活：`GET /api/tasks?page=1&page_size=1` 带 Bearer 应 200。失效症状=轮询整场空 status（check-task 返 success:false），轮询循环要 fail-fast
2. **不要加 `--sync`**——同步模式 300s 硬超时；async polling 能跑长任务（GPT 模型生图常 1-3 分钟）
3. **`--file reference_images=path`** 可注入参考图（自动 base64），用于"按这张图风格"出图
4. **GPT 默认返回 2 张候选**（不是 1 张）
5. **下载也要带 cookie**，否则 401
6. **（6-8 仅当 token_store 的长效 Bearer 也失效时才用——正常走 Bearer 不需要刷 cookie）** cookie 过期刷新必须用户交互、不能后台跑——返回「未认证，请提供有效 Bearer token 或登录 session」=env 和 config 里的 cookie 都过期了。刷新跑 `x2-media/scripts/get_grfal_cookie.py --url https://grfal.tap4fun.com`，它弹 Chrome 钉钉扫码后**还要在终端按 ENTER**；后台(`run_in_background`)跑会因 stdin 关闭直接「Cancelled」失败 → 让用户用 `!` 前缀自己跑。
7. **刷新写 config 但 call_grfal 读 env，二者不同步**——`get_grfal_cookie.py` 把新 cookie 写进 `config.json`，而 `call_grfal.py` 读的是 `GRFAL_COOKIE` 环境变量。刷新后要么 `export GRFAL_COOKIE=$(从 config 读)` 当场注入，要么 `[Environment]::SetEnvironmentVariable('GRFAL_COOKIE',...,'User')` 持久化，否则 call_grfal 还在用旧的过期 env cookie。
8. **可复用自动抓 cookie 脚本**：`x2-media/scripts/auto_get_grfal_cookie.py`（2026-06-05 新建）——后台可跑、不用按 ENTER，弹 Chrome 后**轮询 CDP 直到检测到有效 `grfal_session`(len>=200)**，自动写 config + winreg 持久化用户级 env。判定一定要看**原始 cookie 列表里 name=='grfal_session' 的那枚 value 长度**，别去拼接串里搜子串(会漏判)。`grfal_session` 是会话级 cookie，但 Chrome 关了会落盘到 grfal_chrome_profile，重开同 profile 能恢复。端口冲突时先杀掉 CommandLine 含 `grfal_chrome_profile` 的 chrome(别误杀用户正常 Chrome)。
9. **`generate_image` 是 long_running**：直接 `/api/call` 会报「long_running 请用 async/submit」。必须 `--submit-only` 拿 task_id → `--check-task <id>` 轮询(GPT 带参考图常 4-9 分钟)。GPT 后端会整条链路(ucloud/cliproxy/azure/fal)全超时失败 → fallback gemini(快且稳)。
10. **gemini/GPT 出的"透明"图常是假透明**(mode=RGB 把棋盘格画进像素，alpha 全 255)→ 入库前必查 `mode!='RGBA' or alpha.max()==alpha.min()`；假透明就 `--tool remove_background` 抠真透明，再 `x2-dk-manager/scripts/image_utils.py resize <src> <dst> 256 0.05` 裁边缩放。见 [[feedback_transparent_asset_diff_check]]。

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
