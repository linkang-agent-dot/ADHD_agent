# X3 客户端新 UI 工作流路径登记失效

- 日期：2026-08-06
- 任务：至尊主题英雄主页 UI 改造需求
- 现象：按 AGENTS.md 登记路径读取 `C:\\Users\\linkang\\.Codex\\projects\\C--Users-linkang\\memory\\reference_x3_client_new_ui_workflow.md` 失败；实际文件位于 `.claude\\projects\\C--Users-linkang\\memory`，另有全局备份副本。
- 根因：Codex 项目 memory 目录当前不存在，规则中的路径与实际共享 memory 位置不同步。
- 处理：通过文件索引定位并读取 `.claude` 下的现行文件；本轮需求以该文件和共享 GUI 知识库为依据。后续应修正规则入口或完成 Codex memory 同步。
- 状态：open。
