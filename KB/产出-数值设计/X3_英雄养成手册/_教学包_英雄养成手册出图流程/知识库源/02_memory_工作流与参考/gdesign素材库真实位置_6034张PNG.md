---
tags: [kind/交接, domain/配置换皮, proj/X3, year/2026]
name: gdesign-designdeck-x3
description: gdesign/.designdeck 是什么、在哪、全量素材库真实路径；文档里 E:\ 路径是旧的别信
metadata: 
  node_type: memory
  type: reference
  originSessionId: e64e6447-8b1d-4f10-9e1a-491ee73228ca
---

**gdesign = `C:\Users\linkang\.designdeck\projects\X3\`**：一套 X3 移动端 UI 设计系统 + 工作流基础设施（不是单工具）。含 design token(harness.config.json/colors_and_type.css)、Figma 权威源映射、curated 素材子集(assets/ 64张)、分阶段工作流(work/<feature>/ state.json：1_intro→2_structure wireframe.html→3_mockup→4_split)、HTML editor、references/ 规范库。是 L1_game_ux harness 的地基。

**⚠️ 路径陷阱**：gdesign 的 SKILL.md / README / harness.config.json 里写的素材/CSV 路径是 **`E:\x3git\...` / `E:\AIProgram\...`，全是旧路径，这台机器 E: 盘不可达**。别照抄、别因此以为"在另一台机器"。

**真实位置（本机 C:）**：
- 全量素材库 = `C:\x3-project\client\Assets\Res\UI\Spirits\`（**6034 张 PNG**，按 Activity/Common/CommonNew/ItemIcons/MechaMain/CardCollectionV2 等子目录分）
- gdesign curated 子集 = `.designdeck\projects\X3\assets\`（仅 64 张代表）
- figma 反查 CSV (`figma_spirits_mapping.csv`) 本机**没有**（E: 上的，不可达）；要 node↔path 直接扫 Spirits 目录树代替

**交互原型保真目标**：原型做到跟真游戏 8-9 成相似；现状缺口=核心控件用 emoji/CSS 渐变糊而非引真 PNG。补法见独立工作流 [[workflow_interaction_prototype_assetization]]（真素材优先→缺则Morphix生成→KB自包含三步 + 航海之路对照表）。

**⚠️ 工作流与产物全在 KB，不在 .designdeck**：交互原型/保真版/素材/工作流文档都落 `C:\ADHD_agent\KB\`（产物在 `KB\产出-交互原型\`，方法在 `KB\方法论\`）；`.designdeck` 仅上游参考，不作运行时依赖。相关 [[workflow_design_merit_critique]] [[reference_x3_client_resources]] [[reference_morphix_reskin_prompts]]。
