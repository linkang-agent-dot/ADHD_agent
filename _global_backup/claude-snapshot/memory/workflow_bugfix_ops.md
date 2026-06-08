---
name: 配置BUG修复运维文档
description: 定时查BUG/改BUG的运维规范，含检查清单、Review问题记录、翻译流程。每次处理配置类BUG时必须先读此文档。
type: feedback
originSessionId: 1bbe1da0-274c-4eb5-a1f4-56404b87cb28
---
运维文档路径: `C:\ADHD_agent\docs\ops_auto_bugfix.md`

## 必读时机
1. **查 BUG 开始时** — 看检查清单（SSL、编码、项目 key 等已知坑）
2. **修 BUG 之前** — 看 Review 问题记录，避免重复犯错
3. **修完之后** — 必须沉淀（见下面强制规则）

## 📌 强制规则：BUG 操作前必须用户确认（不能自己点）
**所有对 Jira BUG 的操作前都要先问用户确认**，包括：
- 写入 Google Sheet（暂存区/目标页签）
- 加 Jira 评论
- 转派 BUG（assignee 变更）
- 关闭/重开/改状态/改优先级

**正确做法**：分析完问题 → 列出"准备做什么" → 等用户回复"OK / 改 / 转吧"再动手。
**Why:** BUG 操作影响协作流程和线上数据，不可逆。

## 📌 强制规则：每处理完一个 BUG 必须沉淀（无论修好/转派/搁置）
1. **更新配置知识库** `C:\ADHD_agent\.cursor\config-library\table-index.md`
   - 新发现的表编号/SheetID、活动 ID、道具 ID、display_key
   - 新的配置追踪链/字段含义
2. **更新运维文档** `C:\ADHD_agent\docs\ops_auto_bugfix.md`
   - 历史记录追加一行（BUG ID + 操作 + 状态）
   - 新踩坑点 → 加进 Review 问题记录

**Why:** 同类 BUG 下次能秒查，避免重复搜索。沉淀是自动化的前提。
**How to apply:** 修复/转派/搁置前最后一步，必须沉淀。未沉淀视为未完成。

## 关键 Review 点（从实践中踩过的坑）

1. **翻译类问题必须走 game-localization-translator skill** — 不要手写 18 语言，会导致 JSON 解析失败、shell 引号冲突。skill 路径: `C:\ADHD_agent\.agents\skills\game-localization-translator\SKILL.md`
2. **已有 key 直接更新目标页签行，新建 key 走暂存区** — 两种写入方式不同
3. **规则文案类 BUG 需策划案** — 读老规则 → 让用户提供策划案 → 写新规则 → 用户确认措辞 → 翻译 skill
4. **1011 处理流程** — 改中文 → 翻译 skill 扩 18 语言 → 写暂存区 → linkang review/导表/关 Jira
5. **背包显示控制** — `C_ARR_display_labels` 和 `A_ARR_use_labels` 两个字段都要改，缺一不可

**How to apply:** 每次收到"查BUG"、"改BUG"、"配置修复"等请求时，先 `Read C:\ADHD_agent\docs\ops_auto_bugfix.md` 看最新的检查清单和 Review 记录。

## 📌 Token 优化规范：BUG 排查必须隔离上下文

**问题背景：** 一次 BUG 修复全流程（查列表→定位→改表→导表→提交）在单 session 中跑完，调查阶段的大量 Bash/Read 调用会撑大上下文，导致后续每次 API call 都背着巨量 cache_read。实测一个 157 次 API call 的修 BUG session 消耗 9.7M cache_read tokens，其中 53% 烧在定位根因环节。

**强制规则 — 主会话只做调度，sub-agent 干活：**

主会话的职责：接收用户指令 → 派 sub-agent 调查 → 展示结论和 checklist → 等用户确认 → 派 sub-agent 执行修复 → 汇报结果。主会话自身不做重操作（不查配置、不改表、不跑导表命令）。

1. **Phase 1：定位根因 → sub-agent 调查**
   - 将"查配置/查日志/定位根因"委托给 Agent，prompt 给足 BUG 描述 + 可能涉及的表号/文件
   - sub-agent 返回：根因 + 涉及文件/行 + 修复方案
   - 主会话整理成 **确认 checklist** 展示给用户（要改哪些表、改什么值、影响范围）

2. **Phase 2：等用户确认**
   - 用户说 OK / 调整 → 进入 Phase 3
   - 用户说不改 / 转派 → 走对应流程，结束

3. **Phase 3：执行修复 → sub-agent 干活**
   - 将确认后的修复方案委托给新的 sub-agent 执行（改表、写 GSheet、导表、推分支等）
   - sub-agent 返回：执行结果 + 验证截图/diff
   - 主会话汇报给用户，走沉淀流程

4. **合并 Bash 调用** — sub-agent 内部也要遵守：能合并的命令用 `&&` 串联或并行发起多个 Bash tool call，减少 API 轮次。
5. **多 BUG 拆 session** — 一次要修多个 BUG 时，每个 BUG 用独立 session，避免交叉污染上下文。

**Why:** 单 session 全流程跑，后半段每次 API call 的 cache_read 是前半段的 1.6 倍。调查 + 修复都隔离到 sub-agent 后，主会话上下文始终保持轻量，预估可砍 60-70% token 消耗。
**How to apply:** 每次处理 BUG 时默认走三阶段流程（调查→确认→执行），除非问题极简单（预估 <5 次工具调用可完成全流程）。

## 📌 换皮中途的 BUG：必须带本轮换皮背景

换皮过程中冒出的 BUG，根因常常就是本轮刚改的配置。单独派改 BUG 的 sub-agent 时：
1. 先查 `C:\ADHD_agent\KB\换皮档案\索引.md` → 找该项目状态 🔄进行中 的那轮。
2. 让 BUG agent **先读那轮换皮档案** `KB\换皮档案\{项目}\{日期}.md`，拿到本轮改过哪些表/ID 作背景，别脱离上下文盲查。
3. BUG 修完，把 BUG + 解决回写该换皮档案对应模块，并在档案/索引的「关联 BUG 单」登记。

**Why:** 换皮中途的 BUG 多半是本轮配置引起，没有本轮背景容易误判、重复排查。
**How to apply:** 换皮期间收到 BUG，派 sub-agent 前先取本轮档案路径塞进它的 prompt。
