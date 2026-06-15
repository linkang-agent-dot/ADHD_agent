---
name: feedback_x2_pass_reuse_limit_trap
description: X2通行证/周期礼包复用旧iap id时，limit_cnt=1+period≈100年=终身限购，老玩家上期已用掉名额→本期无法购买
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d12fd14c-cff7-4af9-8795-368b02c153a5
---

X2 节日通行证（battle_pass）换皮时若**复用上期活动的 iap 配置 id**（iap_config 2011xxx / iap_template 2013xxx），要警惕购买限制把老玩家挡在外面：

- 通行证礼包的 `A_MAP_limit` 常配 `{"limit_cnt":1,"limit_type":"period"}`，而 `iap_config.A_MAP_time_info` 的 period 时长被配成 `3153600000ms ≈ 100 年` → **等同"该 id 终身只能买 1 次"**，period 不会随新活动重置。
- 复用 id 时，**买过上期同 id 通行证的老玩家购买计数已=1**，到本期就无法购买；新玩家计数 0 不受影响 → 线上表现 = "**仅老玩家无法购买新通行证礼包**"（2026拓荒节实例：复用占星节 id 2011910030/031，老玩家买不了拓荒节通行证）。
- **判据**：通行证「部分玩家买不了 / 老玩家买不了」类反馈 → 先查 iap_config.pkg_desc 是不是上期节日名（=复用 id 铁证）+ 查 limit_cnt 与 time_info period 时长。

**Why:** limit_type=period 在 period≈100年时实际是终身限购，复用 id 会把历史购买记录带过来卡住老玩家；只用新账号验证无法复现。

**How to apply:**
1. 通行证/周期礼包换皮**优先用新 iap id**；必须复用旧 id 时，把 `limit_cnt` 按复用次数递增（如 1→2），或让 period 真正按当期活动重置。
2. 上线前验证清单加「**有历史购买记录的老玩家账号实购验证**」，别只用新号测。
3. 应急修复 = `iap_template` 对应行 `A_MAP_limit.limit_cnt` +1（2026拓荒节走 master commit 13424fa10：2013910062/063 由 1→2）。

相关：[[workflow_x2_table_import]]（行筛选导这两表）、[[feedback_reskin_lessons_learned]]。
