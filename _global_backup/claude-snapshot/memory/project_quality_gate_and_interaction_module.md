---
name: quality-gate
description: 2026-06-03 搭建——收工自动验收的 quality-gate(task-checker+清单+Stop hook) 和 交互模块「活原型+实时说明一体HTML」工作流；改X3配置/写策划案/做交互原型时相关
metadata: 
  node_type: memory
  type: project
  originSessionId: 4347d131-6f1c-4e7f-8b84-565e8bfb54de
---

2026-06-03 跟用户一起，从分析 DesignDeck(GDesign) 沉淀出两套自用机制。

## quality-gate（收工前自动验收）
- **位置**：脚本+清单在 `C:\ADHD_agent\.claude\quality-gate\`（`pending_verify_gate.py` + `design-doc-checklist.md` / `config-checklist.md` / `i18n-checklist.md` + README）；验收员 agent 在全局 `~/.claude/agents/task-checker.md`。
- **机制**：主 Claude 开工时在 `~/.claude/.pending_verify/<任务>.json` 建标记（带 `type` + 产物位置 + `status:pending`）。`settings.json` 的 **Stop hook** 在每次收工时跑 gate 脚本：有 `pending` 标记就**拦住**，提示派 `task-checker`(按 type 读对应清单) 跑 block/warn 验收。全过→删标记收工；有 blocker→标记改 `reviewed`(放行)+列给用户定『修/跳』；读不到产物→也 reviewed+明示需人工确认(fail-closed)。脚本自身出错→放行(fail-open，不卡死全部工作)。
- **关掉**：删 `.pending_verify/` 对应 json（取消单次）；删 settings.json 的 `Stop` hook（彻底关）。
- **迭代飞轮**：验收漏网的坑 → 当场回填对应 checklist 一条规则（如已加的「删除链/悬空引用」block）。改 block 规则要先报用户确认。
- 已挂进流程真源：[[workflow_x3_festival_design_doc]]（design-doc）、[[feedback_verification_end_to_end]]（config）、[[reference_x3_i18n_workflow]]（i18n）。

## 交互模块工作流
- **位置**：`C:\ADHD_agent\KB\方法论\X3交互模块工作流.md` + 同目录范本 `范本_交互模块_限时商店一体原型.html`。
- **交付物**：一份「**活原型 + 实时说明**」一体 HTML——左边能点的原型，右边实时跟着操作讲解（点哪讲哪，不两边对照）。
- **顺序：原型先行**：可点原型 → 点出问题定待定 → 照原型 1:1 写交互说明(状态机/动线/边界/🟡待定，标【已演示】vs【规则】) → 合成一体HTML → 确认 → 回填策划案「界面交互」。
- **归属**：附属在策划案流程的「界面交互」槽下（有交互的子功能才走；纯数值/无交互直接逐元素填）。
- **美术/落地的落地法（2026-06-04 珍珠贝案例补全）**：原型内嵌折叠的「美术对接说明书」= 每个新增美术(占位资源名 + 录入方式[client路径/注册DK/配置字段如 Item.DKIcon/代码API 如 SetImageWithDisplayKey] + 出图后替换路径)，程序照此接；原型到位即交付、不必再誊文字说明。详见《X3交互模块工作流》★实战要点 + 范本 `范本_交互模块_珍珠贝进度_自动播放.html`（均在 `KB\方法论\`）。

## x3-media 透明化「整机」（两条路子，均已可脱离 DesignDeck 跑）
背景：DesignDeck 把"画mask/双底差分/去绿"这些本地图像运算埋在编译进 main.jsc 的主进程(jimp)里，靠 stdout 标记触发——所以原来只有零件没整机，CLI 跑不全。这次照"补 wrapper"思路补齐：
- **双底差分**（**生成新透明资产**：技能/活动/资源/道具/小图标/英雄碎片图标、行军表情、道具相关 DK）→ `~/.claude/skills/x3-media/scripts/transparify_asset.py`（`--prompt` 全自动生白底+黑底+差分 / `--white --black` 只差分）；底层 `transparify_dual_bg.py`。已写进 x3-media SKILL.md「★透明化硬规则」设为这些类型**默认**，禁用 generate-transparent/removebg。
- **精细拆图**（**从现成图拆多层**，100% 对齐源图）→ `scripts/ui_extract_fine.py`（人工节点：看图写 `manifest_layers.json` 定层+bbox → `--preview` 画框确认 → 去掉 preview 开拆）；底层新补 `make_bbox_mask.py`(画反向mask) + `chroma_key.py`(去绿)，中间调 grfal `image_mask_edit`。
- 区分：要"凭描述生成一个透明 icon" 用双底差分；要"把一张现成效果图拆成多个透明图层" 用精细拆图。

## GDesign 对外反馈（待集中反馈，未发）
暂存在 `C:\ADHD_agent\KB\GDesign学习.md`：①前置gate"问全才开干"不适配迭代流程 ②工作流该分型、颗粒度下沉到子功能。讨论完再集中反馈给 GDesign 团队。
