---
name: API Provider 切换记录
description: Claude Code API provider 切换历史，已切回 Anthropic 官方
type: project
originSessionId: d5bd0ce4-d56d-4f22-a97f-0637b23e7a83
---
**当前状态（2026-06-15 起）**：已切回 Anthropic 官方 Team
- settings.json 无 `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN`，走官方 OAuth

**历史**：
- 2026-05-22：临时切到 one-hub（`https://onehub.akacm.com/claude`）
- 2026-05-25：按计划切回官方 Team
- 2026-06-15：再次切到 one-hub
- 2026-06-15：切回官方 Team

**Why:** Team 走官方 OAuth 订阅
**How to apply:** 切到 one-hub 时在 settings.json env 里加 `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`，重启 Claude Code
