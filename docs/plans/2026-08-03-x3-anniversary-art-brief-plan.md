# X3 Anniversary Art Brief Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将用户提供的主城皮肤、行军特效、装饰物截图准确迁入周年庆美需 HTML，并消除现有需求冲突。

**Architecture:** 直接修改仓库内唯一真源 HTML；仅替换周年庆相关表格行并内嵌三张截图，不引入生成器或额外运行时依赖。使用 Chrome headless 做 CLI 环境下的渲染验收。

**Tech Stack:** HTML/CSS、内嵌 PNG base64、Google Chrome headless、PowerShell 只读验证。

---

### Task 1: 更新周年庆三项美需

**Files:**
- Modify: `KB/产出-数值设计/X3_8-10月节日需求/美需清单_周年+万圣_给PM.html`

**Step 1:** 把主城普通/高级双档合并为 A 块“美术搬运”条目，引用 `PirateSkin2026Lv1/Lv2`，状态改为已确认。

**Step 2:** 把原地板/墙纸合并条目拆为两条独立美需，各用一句话写清周年主题方向与待确认状态。

**Step 3:** 新增鲨鱼 3D 装饰物候选，补齐主体、底座、周年轻包装、交付物与避坑。

**Step 4:** 门头只保留一句周年主题方向与待确认状态。

**Step 5:** 把高级行军特效条目改为“璀璨之星”候选结构，补齐前端主体、飘散元素、拖尾、配色、动效和避坑。

**Step 6:** 删除 B 块中已被合并的“主城皮肤·低品质”冲突行，更新说明和文档日期。

### Task 2: 静态与渲染验收

**Files:**
- Verify: `KB/产出-数值设计/X3_8-10月节日需求/美需清单_周年+万圣_给PM.html`

**Step 1:** 搜索确认旧冲突文本“AI 生成周年主题低模贴图风格主城”和“装饰物（地板+墙纸）”已不存在，且地板、墙纸已拆为独立条目。

**Step 2:** 搜索确认 `PirateSkin2026Lv1`、`PirateSkin2026Lv2`、“璀璨之星”、“鲨鱼装饰物”与状态字段存在。

**Step 3:** 用 Chrome headless 渲染 1440px 页面截图，检查表格、图片、状态标签和文字换行。

**Step 4:** 对比修改前后文件范围，确认 10 月万圣部分未被改动。
