# 非交互 Codex sub-agent E2E 验收 120 秒超时无输出

- 日期：2026-08-03
- 任务：真实验证 BTW/sub-agent handoff hooks
- 现象：`codex -a never exec --json ...` 要求 spawn 一个 explorer，进程持续约 125 秒无输出后被 shell timeout 终止；随后用 `--dangerously-bypass-hook-trust --ephemeral` 做只回复 OK 的最小冷启动，仍在 25 秒内无模型输出并超时。
- 根因：尚未确认；可能是新 hooks 待信任、非交互 sub-agent 等待、模型调用或已有 Codex 运行时锁。统一执行层缓冲了 stdout，超时前没有可见诊断。
- 处理：检查确认残留的 33560→33164→27908 是第一次测试进程链后精确终止；终止后的 `Get-Process` 复查因目标已不存在返回 exit 1，不能误判为终止失败。第二次最小测试同样先按命令行精确定位并清理。smoke 落盘、直接事件模拟和单元测试只记为组件证据，不再称为验收；先完成 `/hooks` 信任，再分别跑真实交互 `/side` 与原生 Codex sub-agent E2E，并独立排查 `codex exec` 首 prompt 无响应根因。
- 状态：open
