# X3 合并审计 memory 的 Codex 路径不存在

- 时间：2026-08-06
- 场景：将马戏节文案从 dev 同步到 qa，按项目规则加载 `workflow_x3_merge_conflict_audit.md`。
- 现象：`C:\Users\linkang\.Codex\projects\C--Users-linkang\memory\workflow_x3_merge_conflict_audit.md` 不存在；组合命令因后续 claim 成功而最终 exit 0，容易掩盖前段 `Get-Content` 错误。
- 原因：项目规则列的是 Codex memory 前缀，但该共享工作流可能仍只存在 `.claude` 真源或其他同步位置。
- 绕道：先用 `rg --files` 定位真实文件并全文读取；以后关键多命令读取要逐段检查 `$LASTEXITCODE`/`$?`，不要让末尾成功命令掩盖前段失败。
