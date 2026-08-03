# 非交互 Codex sub-agent E2E 验收 120 秒超时无输出

- 日期：2026-08-03
- 任务：真实验证 BTW/sub-agent handoff hooks
- 现象：`codex -a never exec --json ...` 要求 spawn 一个 explorer，进程持续约 125 秒无输出后被 shell timeout 终止；随后用 `--dangerously-bypass-hook-trust --ephemeral` 做只回复 OK 的最小冷启动，仍在 25 秒内无模型输出并超时。
- 根因：原 120 秒超时根因仍未确认；hook 信任缺失是独立阻断，但不是该超时的充分解释，因为绕过信任的最小冷启动也曾超时。
- 处理：已补齐全部 9 条当前定义的信任哈希；不带 bypass 的最小 `codex exec` 于 37 秒内成功回复，说明“首 prompt 必然无响应”已无法复现。smoke、直接事件模拟和单元测试仍只记为组件证据；此记录保持 open，直到要求 spawn explorer 的原生 sub-agent E2E 成功，并另跑真实交互 `/side`。
- 状态：open
