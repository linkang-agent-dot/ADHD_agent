---
name: morphix-prompt
description: 内部 Morphix 网页是 GRFal 前处理层，8 个换皮功能的 prompt 全文已逆向归档，做 UI 换皮/节日换皮/图标/拆图时可直接调
metadata: 
  node_type: memory
  type: reference
  originSessionId: e64e6447-8b1d-4f10-9e1a-491ee73228ca
---

## ★已内置进 x3-media（2026-07-01·别再当独立网页工具/别自己 reimplement）
Morphix 的能力已固化进 **x3-media** skill 的两个 type，用户说"用 morphix"= 直接走对应 type，**别手写 media-worker task 自己复刻灰底切法**（我踩过：先派"真像素硬抠"错法、又手 reimplement 灰底雪碧图，被用户连怼"不听话/瞎搞"）：
- **切组件 / 拆图**（从效果图切出面板/图标/角标当真素材）→ `ui_extract` **路径B**（= Morphix 元素拆分：生成 #B8B8B8 灰底雪碧图→removebg→连通域切→分档量化）。见 `references/type-ui-extract.md`。
- **改整张界面出效果图**（加档位/页签、竞品转我方风格）→ `ui_reskin`（内置 Morphix `buildReskinPrompt` 五步法 + `buildFlipPrompt` 横竖转换）。见 `references/type-ui-reskin.md`。
- 走 x3-media 标准派发（主 agent 写 task json→派 media-worker）即可；下面的网页版/逆向 prompt 库是**沿革与 prompt 原文出处**，日常直接用上面两个 type。

---

内部工具 **Morphix**（`demo.tap4fun.com/morphix-demo_0e8f`）本质是 **GRFal 的一层"前处理"**：没有任何独有能力，底层只调 3 个我们已有的 GRFal 工具（`generate_image` / `describe_media` / `remove_background`），调用契约跟 x3-media 的 `call_grfal.py` 完全一致（sync `{tool,params}` + async submit/poll/result）。整套产品 IP = 精调过的 prompt + 多步编排。

**逆向报告 + 8 段 build*Prompt 全文 + 模版调优笔记**已归档：
`C:\ADHD_agent\KB\方法论\Morphix换皮工具逆向_prompt库.html`（分页签 HTML，含框架流程图）。

**做 UI 换皮 / 节日换皮 / 图标换皮 / UI 拆图前先读它**，prompt 直接可复用，别重写。关键复用点：
- **换皮铁律**：图#1 只留布局/文字/语义，视觉全部 ERASE；图#2 当 design system 整套抄。
- **主题转换**（最贴节日换皮，唯一鼓励"放飞"）：可重排布局+加节日氛围元素+角色完全重塑，文字逐字保留。
- **图标换皮**：两步——先 `describe_media` 把参考图榨成 ~80 词风格文本，再逐张 `generate_image` 并发；prompt 强制透明背景。
- **元素拆分**：4 步流水——`generate_image` 出 #B8B8B8 灰底雪碧图（灰底防抠图白边）→ `remove_background` → canvas 连通域切块 → `describe_media` 分类 → JSZip 打包。
- **横竖转换**：prompt 内置横/竖屏 UI 布局规范 + 轴向翻转（竖排阶梯→横排）+ "只画放得下的，其余可滚动"。
- **局部修改**：Morphix 用多边形坐标写进 prompt（短板）；我们有真·mask 的 `image_mask_edit`（见 [[reference_x3_art_resource_spec]] / grfal-api skill），能做得更准。
- **模版调优笔记**（templates.js 注释，现成踩坑手册）：X3 "painterly/笔触" 永久 BAN；"L 形角包"单独点名会让所有装饰退化；配方原则=参考图能说明的就别在 prompt 里说。

接入建议：① prompt 资产层零开发，沉淀成 x3-media/x2 skill 的 type-*.md；② 编排层把"图标 describe→批量""拆分 5 步"固化成 skill 命令。相关：[[workflow_x3_grfal_generate_image]]。
