# codex exec 不接受交互 CLI 的 -a/-s 参数位置

- 日期：2026-08-03
- 任务：真实验证 sub-agent handoff hooks
- 现象：调用 `codex exec --json -C ... -a never -s danger-full-access`，CLI 报 `unexpected argument '-a'`。
- 根因：把顶层交互 CLI 的 `-a/-s` 选项直接套到 `codex exec` 子命令后，未先读取该子命令自己的参数表。
- 处理：先运行 `codex exec --help`；按其支持参数调用，或把全局参数放在 `exec` 之前。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 一次性认知:exec子命令参数集与交互CLI不同,用--help核对即可
- 状态：resolved
