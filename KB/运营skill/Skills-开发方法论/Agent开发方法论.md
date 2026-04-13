---
aliases: [开发方法论, brainstorming, planning, debugging]
tags: [skill, 方法论, agent, 开发流程]
---

# Agent 开发方法论

覆盖从需求澄清到验证完成的全流程方法论技能。

---

## 1. 头脑风暴（brainstorming）
**路径**：`.agents/skills/brainstorming/`
**何时用**：任何创造性/改行为工作前**必用**

在实现前先澄清需求、探索多方案并获得用户批准设计。
> 禁止未经批准就开始实现。

---

## 2. 写计划（writing-plans）
**路径**：`.agents/skills/writing-plans/`
**何时用**：有多步需求、规格阶段，动代码前

把需求写成可执行的细粒度实现计划：
- 明确文件路径
- 具体命令
- TDD 测试步骤

---

## 3. 文件规划（planning-with-files）
**路径**：`.agents/skills/planning-with-files/`
**何时用**：复杂任务（>5 tool calls）、需要跨会话恢复

Manus 风格持久化规划：
- `task_plan.md` — 任务计划
- `findings.md` — 发现记录
- `progress.md` — 进度跟踪
- 支持 `/clear` 后自动恢复会话

---

## 4. WBS 规划（wbs-planner）
**路径**：`.cursor/skills/wbs-planner/`
**何时用**：项目级拆解

Work Breakdown Structure 层级：
- **Roadmap** → **Epic** → **Task**
- 含模板与粒度标准

---

## 5. 执行计划（executing-plans）
**路径**：`.agents/skills/executing-plans/`
**何时用**：在**另一会话**按书面计划执行

分批执行并在批次间设检查点等待反馈。

---

## 6. 并行 Agent 派发（dispatching-parallel-agents）
**路径**：`.agents/skills/dispatching-parallel-agents/`
**何时用**：2+ 独立任务、无共享状态

按领域并行派代理执行，最后合并结果。

---

## 7. 子 Agent 开发（subagent-driven-development）
**路径**：`.agents/skills/subagent-driven-development/`
**何时用**：本会话内有独立任务的实现计划

按任务派实现子代理 → 规格审查 → 代码质量审查。

包含提示模板：
- `implementer-prompt.md`
- `spec-reviewer-prompt.md`
- `code-quality-reviewer-prompt.md`

---

## 8. 系统调试（systematic-debugging）
**路径**：`.agents/skills/systematic-debugging/`
**何时用**：遇到 bug、测试失败、异常行为

**先根因再修复**，禁止猜补丁式乱改：
1. 复现问题
2. 对比正常行为
3. 建立假设
4. 最小化验证

---

## 9. 验证完成（verification-before-completion）
**路径**：`.agents/skills/verification-before-completion/`
**何时用**：声称完成/通过前，提交/PR 前

必须跑验证命令并展示输出，**证据在先，断言在后**。

---

## 10. Git Worktrees（using-git-worktrees）
**路径**：`.agents/skills/using-git-worktrees/`
**何时用**：需要隔离工作区的功能开发

流程：选目录 → 验 `.gitignore` → 建 worktree → 装依赖 → 基线测试。

---

## 11. 超能力指南（using-superpowers）
**路径**：`.agents/skills/using-superpowers/`
**何时用**：对话开始时

强调：有疑问先查是否有 skill 可用，Skill 工具优先于 Read。
