# Codex 独立记忆与 Claude 增量复核

## 决策
- Codex memory 唯一真源：`C:\ADHD_agent\CodexMemory\`，由 ADHD_agent Git 仓库定期同步上传。
- Claude memory：每次 Codex 会话开始做增量复核，按需吸收，不作为 Codex 默认写入目标。
- 共享 KB：项目事实、配置链路和跨模型业务方法论仍保持单一真源。

## 原因
Claude 与 Codex 的工具、插件、运行时和行为短板不同。共用模型行为记忆会把一侧的能力边界错误套到另一侧；但项目事实若拆成两套，又会产生真源漂移。因此采用“模型经验分开、项目知识共用”的分层。

## 开工流程
1. 读 `C:\Users\linkang\CLAUDE.md` 获取共享规则和项目 KB 路由。
2. 读本目录 `MEMORY.md` 获取 Codex 专属经验。
3. 运行 `scripts\review_claude_memory.ps1`，检查 Claude memory 自上次 checkpoint 后的变更。
4. 只读取与当前任务或 Codex 能力相关的变更；需要吸收时改写为 Codex 版本并挂入本索引。
5. 完成复核后推进 checkpoint。
