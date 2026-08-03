# jolt_verify.py 被外层 shell 超时中断
- 日期：2026-08-03
- 任务：验证 qa 分支的马戏礼包主数据配置导表
- 现象：`jolt_verify.py qa` 仍在轮询 Jenkins 时，外层 `shell_command timeout_ms=120000` 于约 127 秒返回 exit 124，脚本未能自行打印最终结果。
- 初判根因：jolt_verify 的设计轮询窗口可达约 20 分钟，外层 shell 超时短于脚本上限；后续应让命令异步保持运行或直接用 Jenkins API 按 branch/启动时间轮询构建，不把 exit 124 当成 Jenkins FAILURE。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(跨模型)。护栏已写入 workflow_x3_auto_jolt_export.md:jolt_verify 一律后台跑/超时≥20min,exit124≠FAILURE
- 状态：resolved
