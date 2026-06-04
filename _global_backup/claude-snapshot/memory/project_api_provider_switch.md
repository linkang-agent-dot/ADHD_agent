---
name: API Provider 切换记录
description: Claude Code API provider 切换历史，已切回 Anthropic 官方
type: project
originSessionId: d5bd0ce4-d56d-4f22-a97f-0637b23e7a83
---
**当前状态（2026-05-25 起）**：已切回 Anthropic 官方 API
- settings.json 无 `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN`，走官方 OAuth

**历史**：
- 2026-05-22：临时切到 one-hub（`https://onehub.akacm.com/claude`）
- 2026-05-25：按计划切回官方

**Why:** 之前 one-hub 走内部渠道是临时方案
**How to apply:** 用户问"现在用的什么 API/渠道"时，确认是 Anthropic 官方；如再次需要切换，参考历史配置格式
