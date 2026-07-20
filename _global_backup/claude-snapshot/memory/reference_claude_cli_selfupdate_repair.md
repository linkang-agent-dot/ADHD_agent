---
name: claude-cli-selfupdate-repair
description: claude 命令突然 not recognized 的诊断修复法——根因多为C盘满导致自升级中断，占位exe+挪走的shim三件套，零下载修复姿势
metadata: 
  node_type: memory
  type: reference
  originSessionId: 42ce653e-2e7b-416e-a7f6-25cb4ac83e33
---

# claude CLI「command not found」自升级损坏修复（2026-07-13 实战）

**症状**：新开终端 `claude` 报 not recognized；已开的 Claude Code 会话不受影响（进程镜像已在内存）。

**根因链**：C 盘满（当时 0.33GB）→ 自升级中断 → 现场特征三件套：
1. `%APPDATA%\npm\` 下启动脚本被改名挪走：`.claude-XXXX` / `.claude.cmd-XXXX` / `.claude.ps1-XXXX`（npm 原子改名临时文件）
2. `%APPDATA%\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe` 只剩 **500 字节占位**（内容是报错脚本，真身由 postinstall 下载）
3. 同目录一堆 `claude.exe.old.<epoch毫秒>`（~250MB/个）= 历次自升级把**运行中 exe** 改名的备份；**每个 .old 可能被一个还在跑的会话占用**（删不动=有会话在用，正常）

**修复（零下载）**：
1. 三个临时文件改名归位：`.claude-XXXX`→`claude`、`.claude.cmd-XXXX`→`claude.cmd`、`.claude.ps1-XXXX`→`claude.ps1`
2. 最新的 `claude.exe.old.*` 直接 `Copy-Item` 覆盖 `claude.exe`（先确认磁盘空间够 250MB！）
3. `claude --version` 验证

**坑**：
- `npm install -g @anthropic-ai/claude-code` 完整重装会 **EBUSY**——运行中会话的镜像锁着 bin 目录改名；要重装须先关所有 Claude Code 会话
- 修复操作目录会被升级器重试**动态改动**（文件列出来下一秒就没）——查看+拷贝要一条命令原子做
- `.old` 文件们 ~250MB×N 是 C 盘隐形大户；会话都关掉后升级器自清，也可手动删（删不动=有会话占用，跳过）
- 官方兜底：`node node_modules/@anthropic-ai/claude-code/install.cjs`（重跑 postinstall 下载原生包 `@anthropic-ai/claude-code-win32-x64`，需网络+磁盘）
