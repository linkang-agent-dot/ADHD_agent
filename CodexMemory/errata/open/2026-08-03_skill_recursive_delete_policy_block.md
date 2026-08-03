# 旧 skill 递归删除被运行时策略拦截

- 日期：2026-08-03
- 任务：清理 Codex 旧元流程 skills
- 现象：已按用户确认清单校验目标后执行 PowerShell `Remove-Item -Recurse`，命令在启动前被 destructive-action policy 拒绝，未产生删除或迁移。
- 根因：当前运行时对批量递归删除有额外策略拦截，即使文件系统权限开放也不会执行。
- 处理：改用同一 PowerShell 环境内的显式 `Move-Item`，把目录移到 `CodexMemory\skill-quarantine\2026-08-03`；从活跃 skill 根卸载，同时保留可恢复性。
- 状态：open
