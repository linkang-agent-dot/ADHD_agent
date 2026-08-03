# 会话 JSONL 流式读取遭并行写入锁定
- 日期：2026-08-03
- 任务：整理 Codex CLI 五任务验收测试纪要时审计当天会话日志
- 现象：`[System.IO.File]::ReadLines()` 读取 `~/.codex/sessions/2026/08/03/rollout-*.jsonl` 时，部分仍被 Codex 进程写入的文件报 `The process cannot access the file ... because it is being used by another process`。
- 初判根因：`ReadLines()` 使用的默认文件共享模式不能兼容正在写入的 rollout 日志；后续应显式用 `FileStream(FileShare.ReadWrite)` 做只读快照解析，或只处理已关闭会话。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(Codex运行时)。归并 feedback_shell_composite_exitcode.md:FileShare.ReadWrite读并行写文件
- 状态：resolved
