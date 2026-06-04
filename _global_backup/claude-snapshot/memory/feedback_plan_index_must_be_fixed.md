---
name: plan编号必须用固定值不能自增
description: 3513 display_key plan数组的plan编号必须和3510 val一致，不能用max_plan+1自增，否则同type不同条目plan编号不一致导致查不到
type: feedback
originSessionId: 690372d5-b172-4b8e-a263-d918fb7ac2d6
---
配置表里"上游用统一编号查下游数组"的结构，下游的编号必须用上游指定的固定值，不能按当前数组长度自增。

**Why:** 3513 map_units 的 C_ARR_display_key 是 plan 数组，3510 的 plan_display_key_map_units 按 type 发一个 val（如 type4→val=5）。同 type 的所有 3513 条目都用这个 val 查自己的 plan 数组。如果用 max_plan+1，不同条目（如阶1有5个plan vs 地下世界_阶1有3个plan）会得到不同编号（plan=5 vs plan=3），导致 val=5 查地下世界_阶时找不到拓荒節 dk。

**How to apply:** 
1. 写前：先确定上游的选择器值（如 3510 val），用固定值写入，不用自增
2. **写后必须验证**：反查所有受影响条目，确认目标 plan 编号存在且 displayKey 正确。验证逻辑："3510 val=X → 每条同 type 的 3513 是否都有 plan=X？"。写完不检查是根本原因，算法选错只是表象。
3. **搬运前必须从用户实际部署的配置出发追引用链**：不能用"看起来类似的其他条目"的引用来代替。先查用户 3510 的 iap_scene 实际引用了哪些 2013 ID，再查这些 ID 在 X2 是否存在，最后才决定搬不搬。
