---
name: reference_cc_config_partition
description: "工作号/个人号 Claude Code 配置隔离机制（默认=工作纯净，claude-personal=个人配置目录）；问\"怎么切工作/个人\"\"个人项目在哪\"\"claude-personal\"先读"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ae741d4f-3076-4b80-ab99-52997a1a54f4
---

# 工作/个人 Claude Code 配置隔离（2026-07-16 建）

**背景**：同机器 /login 切工作号↔个人号时，两个号读的是**同一套配置**（登录账号≠配置隔离）。为让**工作号读不到个人私密项目**，改用**配置目录**隔离。

## 机制（失败也安全：默认=工作纯净）
| | 工作 | 个人 |
|---|---|---|
| 启动命令 | 直接 `claude` | `claude-personal`（PS 函数 / `%APPDATA%\npm\claude-personal.cmd`，自动设 `CLAUDE_CONFIG_DIR=~/.claude-personal`） |
| 配置目录 | `~/.claude`（默认） | `~/.claude-personal` |
| 能读到的个人私密项目 | ❌ 已物理剔除 | ✅ 全有 |
| 登录 | 工作号 | 个人号（个人配置无凭证，首次启动提示登录） |

**失败安全**：默认配置里**物理上就没有个人内容**，所以忘了切/手滑用工作号也**读不到个人**（顶多个人会话忘用 claude-personal = 少加载个人，不泄漏）。

## 共享 vs 隔离
- **共享**（个人配置里对默认 `junction`）：skills / agents / commands / plugins（工具两边同步、不重复维护）。
- **个人独有**：`~/.claude-personal` 的 settings.json（多挂了一个屏蔽某媒体渠道的 PreToolUse hook）+ 自己的 memory。
- **memory 现状**：个人配置的 memory 是隔离时的**全量快照**——个人项目 memory 在这里独立累积、永不回流工作默认；但个人配置里的"工作类"memory 是**快照会变旧**（个人会话很少用工作知识，可接受；需要刷新时把默认 memory 里的工作 topic 拷过去即可）。

## 维护注意
- 隔离操作的备份在 `~/.claude/backups/partition_<时间戳>/`（memory + settings + CLAUDE.md）。
- ⚠️ 每周的 `ClaudeWeeklyBackup` 只镜像 `~/.claude`、**不含 `~/.claude-personal`**——个人配置要单独纳入备份（待办）。
- 往工作默认 memory 写东西时**别再引入个人私密项目名/链接**（保持工作号读不到）。个人内容一律写进 `claude-personal` 会话。
