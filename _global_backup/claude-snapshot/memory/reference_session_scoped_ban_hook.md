---
name: reference_session_scoped_ban_hook
description: "会话级/项目级选择性禁用某工具的 PreToolUse hook 模式（全局注册+双开关自门控）；要\"本会话严禁调X\"类需求直接套用"
metadata: 
  node_type: memory
  type: reference
  originSessionId: fd3b3ccf-262a-424d-ad12-d49316bd5204
---

# 会话级选择性禁令 hook 模式（2026-07-13 首例：GRFal 禁令）

**需求形态**：某个会话/项目内严禁触发某平台/工具，但其他日常会话要照常能用。

**方案**：hook 全局注册（用户 `~/.claude/settings.json` PreToolUse），但脚本自带双开关，不满足直接 exit 0 放行：
1. `session_id` 在名单文件里（一行一个，# 注释）→ 生效
2. 会话 `cwd` 含项目关键词 → 生效（新开平行会话从项目目录启动即自动带防护）

**实现锚点**（可直接复制改造）：`~/.claude/hooks/block_grfal.py` + `grfal_ban_sessions.txt`。
- 检查逻辑：特定工具名（Skill 按 skill 前缀 / Agent 按 subagent_type）+ 兜底把整个 tool_input `json.dumps` 后正则扫特征串（宁可误杀）。
- 拦截输出：`{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}`，exit 0。
- matcher 建议覆盖：`Bash|PowerShell|Skill|WebFetch|Agent|Workflow`（间接通道也要堵：skill 后端、专用 subagent、workflow 脚本）。

**三个坑**：
- ⚠️ **hook stdout 必须纯 ASCII**：Windows 控制台可能 GBK，deny JSON 里带 emoji 直接 `UnicodeEncodeError` → `json.dumps(..., ensure_ascii=True)` + 文案别用 emoji。
- 管道测试载荷里 Windows 路径写 `C:\\Users` 经 echo 会变非法 JSON 转义（`\U`）→ 测试 payload 的 cwd 用正斜杠。
- 本机实测（2026-07-13）：改 settings.json 后 hook **当场生效无需重启**（settings watcher 在看）；但仍应实弹验证（发一条含特征串的无害命令看被不被拦），别只信管道测试。

首例应用见 [[project_avatar_replace]]（GRFal 禁令）。
