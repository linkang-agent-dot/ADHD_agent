# Codex Memory Index

> Codex 专属持久记忆，位于 `C:\ADHD_agent` Git 仓库中并随仓库定期同步。项目事实与业务知识仍以 CLAUDE.md 路由到的共享 KB 为真源；这里主要记录 Codex 的能力边界、工具恢复链、模型协作反馈和专属工作流。

## 工具与运行时
- [Browser失败必须自行跑完恢复链](feedback_browser_self_recovery.md) — 单版本/单 selector 失败不等于能力不可用；完整版本检查→排障→实例发现→真实页面三证验证

## 记忆架构
- [Codex独立记忆与Claude增量复核](reference_codex_memory_architecture.md) — Codex 专属经验独立存储；Claude memory 会话开工增量复核；项目事实继续共用 KB
- [Codex与Claude资产边界](reference_codex_claude_asset_boundary.md) — 哪些必须独立、哪些必须共用、哪些只同步模板不上传运行状态

## 同步状态
- [Claude memory 复核 checkpoint](CLAUDE_REVIEW_CHECKPOINT.md) — 每次会话开工检查 Claude memory 增量，按需吸收，不整库镜像
