---
name: feedback_hook_path_forward_slash
description: "Windows 上 settings.json 的 hook command 路径必须用正斜杠，反斜杠会被 POSIX shell 吃掉报\"脚本丢失\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e9da8e3-9195-48df-9c54-bd175d28bbb7
---

settings.json 里 hook 的 `command` 字段，在 Windows 上路径**必须用正斜杠** `C:/ADHD_agent/.claude/...`，不能用反斜杠 `C:\\ADHD_agent\\...`。

**Why:** Claude Code 在本机通过 POSIX shell(bash/sh) 执行 hook 命令，bash 把 `\` 当转义符 → `C:\ADHD_agent\.claude\x.py` 被吃成 `C:ADHD_agent.claudex.py` → python 当相对路径拼到 cwd → 报 "Hook script appears to be missing"，但脚本其实没丢。

**How to apply:** 遇到 hook 报 "script missing / No such file" 且报错路径里反斜杠全没了(如 `C:\Users\linkang\ADHD_agent.claudequality-gate...`)，第一反应是路径转义问题不是文件丢失——先 Glob 确认脚本真实存在，再把 settings.json 命令路径全改成正斜杠(python/任何 shell 通用)。2026-06-04 Stop hook quality-gate 踩坑。
