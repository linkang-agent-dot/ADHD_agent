---
tags: [kind/产出, domain/本地化, domain/美术媒体, proj/X3, year/2026-05]
---

# X3 节日活动 Banner / 礼包主背景 — AI 生图 prompt 模板

> **适用项目：** X3（机甲海盗）
> **适用场景：** 节日活动 Banner / 礼包弹窗主背景图（Pack.MainBg / ActvOnline.ActvImg 等）
> **AI 工具：** GRFal（`x2-media` skill + `call_grfal.py`）
> **首次产出：** 2026-05-27 夏日柔情海湾礼包背景图

---

## 一、X3 节日 Banner 的标杆参考

**黑猫神龛（Pack 210616 尼罗家具礼包 MainBg）= `DK_img_Activity_Egypt_bg_19`**

构图特征（X3 节日 banner 通用范式）：
- 接近 1:1 正方形
- **居中主体** + 周围环境/装饰
- **底部地面有透视感**（向画外延伸）
- **边缘四向渐隐**（softly fade to transparent）方便嵌入 UI 弹窗不出硬边
- 主体偏画面中上部，下半部留 30% 给前景空间
- **暖色调** + 节日主题色

这是 X3 项目内最干净的 banner 范式，新节日出图都建议对齐。

---

## 二、Prompt 通用模板

```
game environment, atmospheric lighting, detailed background, fantasy or modern setting, wide composition,
romantic <节日主题> themed gift pack background painting,
centered composition featuring the iconic <主体名称> as the main focal point
(use reference image exactly: <主体细节描述：颜色/形状/标志元素>,
preserve the cartoon stylized 3D rendered look of the reference exactly),
<环境层描述：周围植被/远景/天气/光照>,
<点缀层：飘落物 / 光点 / 装饰>,
overall composition has strong painterly hand-drawn quality,
ENTIRE IMAGE softened with watercolor wash texture and warm dreamy glow,
edges fade dramatically into transparent background creating a vignette frame effect
similar to traditional festival event banner artwork,
no harsh outlines, no sharp edges, no foreground objects, no characters, no items,
soft blurred ambient lighting envelops everything,
square 1:1 aspect ratio with pronounced transparent edge fade-out on all sides
```

**模板要点：**
- 开头 `game environment, atmospheric lighting, detailed background, fantasy or modern setting, wide composition` 是 x2-media 的 scene 默认风格全文，**禁止改写**
- 主体描述部分用 `use reference image exactly: ...` 锁定参考图风格
- 边缘渐隐用 `vignette frame effect` + `edges fade dramatically into transparent` 强调
- 明确 `no foreground objects, no characters, no items` 避免画面杂乱
- `watercolor wash texture and warm dreamy glow` 让画面虚化柔和（避免太"实"）

---

## 三、Reference Images 注入

**必须注入官方素材**，让 AI 锁定该节日的视觉锚点。

### 怎么找节日的官方 reference

| 候选位置 | 内容 |
|---------|------|
| `client/Assets/Res/UI/Spirits/ItemIcons/` | 道具图标 — 主城皮肤 / 家具 / 标志道具 |
| `client/Assets/Res/UI/Spirits/ActivityImg/` | 历史活动主图 |
| `client/Assets/Res/UI/Spirits/ActivityImg_Download/` | 当期节日已出的零散图 |

**好的 reference 例：**
- 节日主城皮肤 png（`icon_island_<节日>.png`）
- 节日代表道具高清图
- 历史同类节日的 Banner 图（同节日不同期次复用）

**注入方式（call_grfal.py）：**
```bash
--file reference_images=<本地图片路径>
```
脚本自动 base64 编码注入 API。

---

## 四、调用代码（一次成功版）

```python
import json, subprocess, os
os.environ['GRFAL_COOKIE'] = json.load(open(r'C:/ADHD_agent/.cursor/skills/x2-media/config.json'))['grfal_cookie']

CALL = r'C:\ADHD_agent\.cursor\skills\grfal-api\scripts\call_grfal.py'
prompt = '...'  # 按二节模板填
ref_img = r'<reference 图片绝对路径>'

params = {'prompt': prompt, 'model': 'gpt', 'aspect_ratio': '1:1'}
r = subprocess.run([
    'python', CALL,
    '--tool', 'generate_image',
    '--params', json.dumps(params, ensure_ascii=False),
    '--file', f'reference_images={ref_img}',
    '--timeout', '900',
    # ⚠️ 不要加 --sync（同步模式 300s 硬超时；默认 async 才能跑长任务）
], capture_output=True, text=False, timeout=950)
```

**返回**：`{"result": ["/api/output/image_generation/YYYY-MM-DD/N_0_0.png", ...], "success": true}`，GPT 模型默认 2 张候选。

---

## 五、保存路径规范

```
C:\ADHD_agent\KB\产出-本地化与美术\X3\活动主背景\<活动名>_<模型>_<YYYYMMDD_HHMMSS>_v<N>.png
```

每次让用户选 v1 / v2，选定后再复制到 client 仓的 `Assets/Res/UI/Spirits/ActivityImg_Download/img_Activity_<节日>_bg_<N>.png` 走 DK 注册流程。

---

## 六、模型选择

| 模型 | key | 速度 | 风格 | 推荐场景 |
|------|-----|------|------|---------|
| **GPT** | `gpt` | 慢（1-3 分钟）| 写实+精致 | **节日 Banner 主推荐** |
| 即梦豆包 | `doubao` | 快 | 偏卡通 Q | 集卡 / 头像 |
| Gemini | `gemini` | 中 | 通用 | 通用补充 |
| Flux Max | `flux_max` | 中 | 写实 | 风景 / 立绘 |

节日 Banner 用 GPT 质量最稳。

---

## 七、实战案例：夏日柔情海湾礼包 Pack 210921

### 关键参数

| 项 | 值 |
|----|---|
| 节日主题 | summer love / 夏日恋语 |
| 主体 | 红顶白屋小岛 + 心形气球 + 圆形小岛底座 |
| Reference | `client/Assets/Res/UI/Spirits/ItemIcons/icon_island_ValentinesDay.png`（柔情海湾岛屿官方素材）|
| 环境 | 夕阳海面 + 椰林 + 飘落玫瑰花瓣 |
| 风格 | 水彩渐隐 / vignette / 1:1 |
| 模型 | gpt |
| 落地 DK | `DK_img_Activity_summer_bg_12` |

### v1（无 reference 第一版，过于"实"）

直接描述海湾别墅+椰林+夕阳，没注入参考图。结果偏写实风景画，跟 X3 卡通游戏风格不搭。

### v2（注入 reference + 加重水彩虚化，✅ 选用）

- 注入 `icon_island_ValentinesDay.png`
- prompt 加 `watercolor wash texture and warm dreamy glow`
- prompt 加 `vignette frame effect`
- 结果：保留官方岛屿 Q 版 3D 风格 + 整体水彩柔化 + 边缘渐隐，完美匹配 X3 节日 banner 范式

### 落地链路

```
1. GRFal 生图 → KB/产出-本地化与美术/X3/活动主背景/夏日柔情海湾_v2_20260527_103412_pick2.png
2. 复制到 client/Assets/Res/UI/Spirits/ActivityImg_Download/img_Activity_summer_bg_12.png
3. Unity import 生成 .meta (GUID)
4. Path_Activity.asset 加 DK→path 注册（keys + values 双列表对应）
5. x3-project: feature branch + MR !224 → dev
6. gdconfig: Pack.210921.MainBg = DK_img_Activity_summer_bg_12, push + jolt
```

---

## 八、Checklist：下次出节日 Banner

- [ ] 找到该节日的官方 reference 图（主城皮肤 / 代表道具 / 历史 banner）
- [ ] 用本文 prompt 模板填充节日主题/主体/环境
- [ ] `--file reference_images=...` 注入 reference
- [ ] 模型选 GPT，aspect_ratio=1:1，不加 --sync
- [ ] 生成 2 张候选，让用户/美术挑
- [ ] 选定后走 DK 注册流程（`workflow_x3_grfal_generate_image.md` 详细步骤）
- [ ] 配 Pack.MainBg 或 ActvOnline.ActvImg 字段
- [ ] push gdconfig + jolt 导表

---

## 关联

- 完整工作流：`memory/workflow_x3_grfal_generate_image.md`
- 客户端 DK 注册：`memory/reference_x3_client_resources.md`
- x3-project MR 流程：`memory/workflow_x3_protected_branch_mr.md`
- 弹窗渲染原理：`memory/reference_x3_pack_panel_rendering.md`
