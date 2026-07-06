---
tags: [kind/交接, domain/配置换皮, proj/X3, year/2026-06]
name: morphix-prompt
description: 内部 Morphix 网页是 GRFal 前处理层，8 个换皮功能的 prompt 全文已逆向归档，做 UI 换皮/节日换皮/图标/拆图时可直接调
metadata: 
  node_type: memory
  type: reference
  originSessionId: e64e6447-8b1d-4f10-9e1a-491ee73228ca
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
