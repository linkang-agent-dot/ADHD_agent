# codex exec 冒烟测试选在非 Git 工作目录被启动检查拒绝

- 日期：2026-08-03
- 任务：真实验证受信任 handoff hooks
- 现象：从 `C:\Users\linkang` 启动 `codex exec`，在触发会话前退出并提示不在受信任目录。
- 根因：复用了配置审计的 cwd，没有把 `codex exec` 自身的 Git 工作区启动约束纳入测试前置检查。
- 处理：改在已信任的 `C:\ADHD_agent` Git 仓启动；不带 `--dangerously-bypass-hook-trust` 的新会话 37 秒内回复 OK，并由 SessionStart 创建对应 handoff 记录。
- 状态：resolved
