# GitLab API 环境变量在当前 Codex 运行时未加载

- 日期：2026-08-06
- 任务：为航海奖励随机修复创建 target=dev 的 MR。
- 现象：`$env:GITLAB_TAP4FUN_TOKEN` 为空，无法调用 GitLab API。
- 根因：知识库记录该 PAT 已持久化，但当前托管 PowerShell 会话未继承该用户环境变量。
- 处理：不读取或复制明文凭据，改用已认证 SSH 通道的 GitLab push option 创建 MR。
- 状态：open。
