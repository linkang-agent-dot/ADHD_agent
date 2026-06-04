---
name: workflow-x3-decoration-video
description: X3 两类礼包（装饰礼包/拜访礼包）视觉资产全链路对比，含各自产出物+配置字段+制作流程+公共环节(GRFal/DK注册/HUD图标)+踩坑+产出记录
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2a901dcb-1931-4be2-a077-91ac77e43036
---

# X3 礼包美术制作流程

## 一、两类礼包对比

| 维度 | 装饰礼包 | 拜访礼包 |
|------|---------|---------|
| 典型活动 | 夏日装饰特惠(106101)、尼罗装饰特惠(106102) | 夏日柔情海灣(105603)、金字塔之城(105602) |
| 视频背景 | **有**，循环播放 | **无** |
| 弹窗主背景 | ActvOnline.ActvImg | ActvOnline.ActvImg（Pack.MainBg **必须空**） |
| 礼包行小图 | Pack.Icon | ActvVisitPack.DK_PackIcon |
| 底部 tab 图标 | **ChainPack.Icon (col 4)** | ActvOnline.ActvIcon (col 22) |
| 活动列表 HUD 图标 | ActvOnline.ActvIcon (col 22) | ActvOnline.ActvIcon (col 22) |
| 配置表 | Pack.xlsx → **ChainPack** 页签 | Pack.xlsx + **ActvVisitPack** |
| Video 字段 | ChainPack.Video (col 9) = `DK_video_{name}` | 无 |

### 关键区别
- **装饰礼包**需要出视频（540×960 竖屏 ~4s 循环 MP4），拜访礼包不需要
- **拜访礼包**的 Pack.MainBg **必须保持空**，否则会覆盖节日主视觉（详见 [[reference_x3_pack_panel_rendering]]）
- **装饰礼包底部 tab 图标**读 `ChainPack.Icon`（`UIGiftPack.cs:185`），**不是** `ActvOnline.ActvIcon`；拜访礼包走 `ActivityItem` 路径才读 ActvIcon（`UIGiftPack.cs:123`）
- 两类礼包共享：活动背景图、DK 注册流程

---

## 二、装饰礼包制作流程

### 产出物

| 类型 | 规格 | 用途 | 配置字段 |
|------|------|------|---------|
| 礼包背景视频 | 540×960 (9:16) ~4s 循环 MP4 | 购买界面背景循环播放 | ChainPack.Video |
| 活动背景图 | 540×960 PNG RGBA | 活动入口/展示背景 | ActvOnline.ActvImg (col 23) |
| HUD 活动图标 | 124×136 PNG RGBA 透明底 | 活动列表缩略图 | ActvOnline.ActvIcon (col 22) |

### 制作步骤

#### Step 1：收集参考素材
1. 装饰 **icon 图**：`Furniture\Actv\icon_jiaju_{节日}_{序号}.png`（非 UV 贴图）
2. 同类型已有视频/背景图了解规格
3. 截图游戏 UI，确认**可见区域比例**（礼包卡片遮挡下方 60-70%）

#### Step 2：确认画面规格
- 竖屏 9:16（540×960 或 720×1280）
- 上方 25-30% 是可见区域，下方被 UI 遮挡
- 注意标题文字叠加位置（约 8-21% 从顶部）

#### Step 3：生成基底图（GRFal generate_image）
- 模型：**GPT**（游戏卡通风最好，慢，必须 async API）
- 参考图：`reference_images: [base64 data URI]`（列表格式）
- **构图要点**：
  - 上方 25-30%：装饰主体（拱门/家具/主题元素）
  - 下方 70%：纯氛围渐变（会被 UI 遮挡）
  - 用**正面/微俯视角**，不要等轴 45°
  - 背景要有场景感（花园/房间），不要纯色渐变底

#### Step 4：生成循环视频（GRFal generate_video）
- 模型：**kling**，`aspect_ratio: "9:16"`
- `reference_images: [img_b64]`（必须列表格式）
- 提交 `/api/async/submit`，轮询 `/api/async/status/{task_id}`
- **上方 1/3 必须有明显特效**（花瓣/沙尘/光尘），否则"没感觉"

#### Step 5：生成活动背景图 + HUD 图标
- 背景图：同 Step 3，传布局参考图，严格 540×960 PNG
- HUD 图标：见第四章通用流程

#### Step 6：放入游戏路径 + 注册 DK + 配置
- 视频 → `client/Assets/Res/Video/VideoRes/{name}.mp4`
- DK 注册：Path_Video.asset + Path_Activity.asset + tableResInfo.txt（见第五章）
- **ChainPack 配置**（Pack.xlsx → ChainPack 页签）：
  - **Icon (col 4)**：底部 tab 图标 DK（⚠️ 不改这个底部 tab 不会换图标！）
  - **Video (col 9)**：填 `DK_video_{name}`
- 参考行：ID=647（夏日装饰），ID=648（埃及装饰）

#### Step 7：Push + 打表
- client push（图片 + DK 注册 + .meta 文件）
- gdconfig push（配置表）→ 自动触发 Jenkins 打表

---

## 三、拜访礼包制作流程

### 产出物

| 类型 | 规格 | 用途 | 配置字段 |
|------|------|------|---------|
| 活动背景图 | 540×960 PNG RGBA | 活动弹窗主背景 | ActvOnline.ActvImg (col 23) |
| HUD 活动图标 | 124×136 PNG RGBA 透明底 | 活动列表缩略图 | ActvOnline.ActvIcon (col 22) |

**无需制作视频。**

### 制作步骤

#### Step 1：收集参考素材
1. 岛屿皮肤 icon：`icon_island_{节日}.png`（作为 AI 生图参考）
2. 已有同类活动背景图了解布局（可用情人节岛屿 bg 做布局参考）

#### Step 2：生成活动背景图
- GRFal generate_image，GPT 模型，540×960
- 可传 2 张参考图：主题素材 + 布局参考

#### Step 3：生成 HUD 图标
- 见第四章通用流程

#### Step 4：放入游戏路径 + 注册 DK + 配置
- 背景图 → `ActivityImg/` 或 `ActivityImg_Download/`（按节日系列）
- DK 注册：Path_Activity.asset + tableResInfo.txt（见第五章）
- 改 ActvOnline.xlsx → ActvImg (col 23) 填新 DK
- **Pack.MainBg 必须空**，不要填！填了会覆盖节日主视觉

#### Step 5：Push + 打表
- 同装饰礼包

### 拜访礼包 MainBg 历史值

| Pack ID | 节日 | MainBg | 状态 |
|---------|------|--------|------|
| 210417 | 圣诞 | None | 标准 |
| 210617 | 尼罗 | None | 标准 |
| 210717 | 情人节 | None | 标准 |
| 210816 | 新春 | None | 标准 |
| 210921 | 夏日 | 曾错填 `DK_img_gift_bg_28`，已清空 | 已修 |

---

## 四、HUD 活动图标制作（通用）

两类礼包共用此流程。

### 制作步骤
1. **找参考图**：`Furniture\Actv\icon_jiaju_{节日}_{序号}.png` 或 `icon_island_{节日}.png`
2. **GRFal 生图**：`generate_image` + GPT 模型 + `reference_images`，prompt 写游戏图标风格 + 透明背景
3. **Resize**：PIL 缩放到 **124×136**，转 RGBA 透明底
4. **放入客户端**：
   - VD 系列 → `ActivityImg/img_Activity_VD_icon_{序号}.png`
   - Egypt 系列 → `ActivityImg_Download/img_Activity_Egypt_icon_{序号}.png`
5. **注册 DK**：Path_Activity.asset + tableResInfo.txt
6. **改配置**：ActvOnline.xlsx → ActvIcon (col 22) 填新 DK 名
7. **Push + 打表**

### 编号规则
- VD_icon 现有 1-10，新增从 11 起
- Egypt_icon 现有 1-12，新增从 13 起
- Egypt 系列文件在 `ActivityImg_Download/`（不是 `ActivityImg/`）

### ActvOnline.xlsx 字段速查
| 列号 | 字段 | 用途 |
|------|------|------|
| 22 | ActvIcon | HUD 活动图标 DK |
| 23 | ActvImg | 活动背景图 DK |

---

## 五、DK 注册（通用）

所有新增资源（视频/背景图/图标）都需注册 DisplayKey。

### 需改的文件

| 文件 | 路径 | 操作 |
|------|------|------|
| Path_Video.asset | `client/Assets/Res/Config/DisplayKey/Path_Video.asset` | 视频 DK，keys + values 各加一条 |
| Path_Activity.asset | `client/Assets/Res/Config/DisplayKey/Path_Activity.asset` | 背景图/图标 DK，keys + values 各加一条 |
| tableResInfo.txt | `client/Assets/Editor/Config/tableResInfo.txt` | 加一行 DK 名（按字母序插入） |

### Path_Video.asset 结构示例
```yaml
paths:
  keys:
    - DK_video_egypt_sphinx
  values:
    - key: DK_video_egypt_sphinx
      objPath: Assets/Res/Video/VideoRes/egypt_sphinx.mp4
```

### .meta 文件
- Unity 自动生成，**必须一起提交**，否则 GUID 引用丢失

### 提交后自动打表
- gdconfig `git push` → `python ~/.claude/jolt_export.py <分支名>` → Jenkins
- 参见 [[workflow-x3-auto-jolt-export]]

---

## 六、资源路径汇总

### 客户端
| 资源 | 路径 |
|------|------|
| 装饰 icon（参考图） | `client/Assets/Res/UI/Spirits/Furniture/Actv/icon_jiaju_{节日}_{序号}.png` |
| 岛屿 icon（参考图） | `client/Assets/Res/UI/Spirits/Furniture/Actv/icon_island_{节日}.png` |
| 视频 | `client/Assets/Res/Video/VideoRes/` |
| 活动背景图（VD） | `client/Assets/Res/UI/Spirits/ActivityImg/img_Activity_VD_bg_{序号}.png` |
| 活动背景图（Egypt） | `client/Assets/Res/UI/Spirits/ActivityImg_Download/img_Activity_Egypt_bg_{序号}.png` |
| HUD 图标（VD） | `client/Assets/Res/UI/Spirits/ActivityImg/img_Activity_VD_icon_{序号}.png` |
| HUD 图标（Egypt） | `client/Assets/Res/UI/Spirits/ActivityImg_Download/img_Activity_Egypt_icon_{序号}.png` |

### KB 存档
- 视频中间产物：`KB\产出-本地化与美术\X3\游戏视频\{节日}_frames\`
- 活动背景图：`KB\产出-本地化与美术\X3\活动背景\activity_bg_{模型}_{日期}_{主题}.png`
- HUD 活动图标：`KB\产出-本地化与美术\X3\活动图标\{序号}_{名称}.png`

---

## 七、GRFal API 踩坑记录

### 图片生成
| 坑 | 解决 |
|----|------|
| GPT 模型 + 参考图经常超时 | 用 async API（`/api/async/submit`） |
| 返回相对路径 `/api/output/...` | 拼上 `grfal_url` 前缀才能下载 |
| `trycloudflare.com` URL 内网不可达 | 替换前缀为 `http://172.20.90.45:6018` |
| 并行 4 张时个别超时 | 超时后重查 status 通常已完成，直接取 result |

### 视频生成
| 坑 | 解决 |
|----|------|
| `image` 参数无效 | 必须用 `reference_images: [b64]`（列表格式） |
| `ref_types: "首帧图片"` 报错 | 去掉 ref_types，让 API 自动检测 |
| 原图太大传不进去 | 先 resize 到 720px + PNG optimize |
| 下载到 HTML 而非视频 | URL 需拼 `grfal_url` 前缀 |
| 生成雾气 | prompt 写 "No fog, no mist, no haze" |
| 镜头乱动 | prompt 写 "Static fixed camera, no camera movement, no zoom, no pan" |
| 莫名光效 | prompt 写 "No extra light effects, no light bursts, no flashes, no lens flare" |

### 通用
| 坑 | 解决 |
|----|------|
| 401 Unauthorized | Cookie 从 `config.json` 的 `grfal_cookie` 读取 |
| config.json 位置 | `C:\ADHD_agent\.cursor\skills\x2-media\config.json` |

---

## 八、视频 Prompt 模板（仅装饰礼包）

```
Static fixed camera, no camera movement, no zoom, no pan.
[主体] stays completely still.
Animate:
1) [花瓣/沙尘描述] falling/drifting from top to bottom throughout the entire frame.
2) Tiny golden sparkle particles slowly floating.
3) Fairy string lights softly twinkling.
No fog, no mist, no haze. No extra light effects, no light bursts, no flashes.
Clean and crisp. Seamless loop.
```

---

## 九、2026 实际产出

### 情人节（装饰礼包）
- 基底图迭代：v1→v2→...→garden→portrait(竖屏9:16)
- 最终视频：`valentine_garden.mp4`（花园背景 + 密集花瓣）
- 活动背景图：覆盖 `img_Activity_VD_bg_13.png`

### 埃及斯芬克斯（装饰礼包，2026-05-25）
- 参考图：`icon_jiaju_Egypt01.png`
- 视频：`egypt_sphinx.mp4`（v4 左半边放斯芬克斯，kling 模型）
- 活动背景图：`img_Activity_VD_bg_18.png`（540×960）
- 配置：ChainPack ID=648 Video=`DK_video_egypt_sphinx`
- 踩坑：基底图迭代4版（居中被标题挡→缩太狠→太小→左半边，最终采用）

### 金字塔岛屿 Banner（拜访礼包，2026-05-26）
- 参考图：`icon_island_Egypt.png` + 情人节岛屿布局参考
- 产出：`activity_bg_gpt_20260526_pyramid_island_v2.png`（540×960）
- 替换：`img_Activity_Egypt_bg_7.png`（在 `ActivityImg_Download/`）

### HUD 活动图标（通用，2026-05-26）

| 活动 | 类型 | ID | 参考图 | 新 DK |
|------|------|-----|--------|-------|
| 夏日柔情海灣 | 拜访 | 105603 | icon_island_ValentinesDay | DK_img_Activity_VD_icon_9 |
| 金字塔之城 | 拜访 | 105602 | icon_island_Egypt | DK_img_Activity_Egypt_icon_11 |
| 夏日装饰特惠 | 装饰 | 106101 | icon_jiaju_ValentinesDay_2（花藤拱门） | DK_img_Activity_VD_icon_10 |
| 尼羅装饰特惠 | 装饰 | 106102 | icon_jiaju_Egypt01（斯芬克斯） | DK_img_Activity_Egypt_icon_12 |

- 踩坑：#3 初版用 ValentinesDay_1（心形沙发）不满意，换 ValentinesDay_2（花藤拱门）重新生成
- **踩坑：装饰特惠底部 tab 图标没换** — 只改了 ActvOnline.ActvIcon，但装饰特惠在底部 tab 走 `ChainPackItem` 渲染路径（`UIGiftPack.cs:185`），图标读 **ChainPack.Icon (col 4)**，不读 ActvOnline.ActvIcon。必须同时改 ChainPack.Icon 才能生效。
  - 647 夏日装饰：`None` → `DK_img_Activity_VD_icon_10`
  - 648 尼罗装饰：`DK_img_Activity_Egypt_icon_10` → `DK_img_Activity_Egypt_icon_12`
