---
name: 拓荒节换皮第二轮踩坑（测试阶段）
description: 换皮配置写入GSheet后测试阶段暴露的问题，主要是引用链不完整和写入位置BUG
type: feedback
originSessionId: 03f54909-5392-432f-954e-d30d028b3fc8
---
## 引用链遗漏

换皮脚本只追踪了 2112 components 直接引用的子表，但很多**间接引用**被漏掉了：

| 漏掉的链路 | 表现 | 修复 |
|-----------|------|------|
| 2121 wonder_egg_drop → expr 内的 2124 drop ID | Wonder 金蛋还是旧奖池 | 替换 expr 内 7 个 drop ID |
| 2121 task_group → array 内的 2115 任务 ID | Wonder 积分任务还是观星球 | 新建 15 个任务 + 更新 array |
| 2121 discount → status 内的 2011 IAP ID | 掉落转付费礼包不触发 | 新建 2011+2013 + 更新 status |
| 2011 iap_status → drop ID（随机礼包奖池）| Gacha 随机礼包不出 | 新建 5 行 2124 + 更新 iap_status |
| 2141/2142 通过 activity ID 关联（不在 components 里）| Gacha 内圈没奖池 | 新建 2141(2行)+2142(9行) |
| 2024 iap_custom_chest 通过 2013 template_id 关联 | 周卡自选坑位空 | 新建 30 行 |
| 1111 金蛋道具 category_param → 2124 drop ID | 金蛋掉落旧道具 | 替换 7 行 |
| 1111 周卡解锁 category_param → 2013 ID | 周卡解锁不对 | 修正 3 行 |
| 累充 2122 score_rule → 需包含所有新 2011 ID | 累充没记上 | 每新增 2011 都要加进 score_rule |

**Why:** 脚本只追踪 2112→components→子表 的一级引用。但子表行内部的 JSON 字段（expr/status/iap_status/category_param）还会引用更深层的表，这些二级、三级引用没有自动追踪。

**How to apply:** 
1. 换皮后必须做**全链路验证**：从 2112 出发，递归检查每个引用的子表行，再检查行内 JSON 里的所有 ID 引用
2. 以下表需要手动检查：2141/2142（通过 activity ID 关联）、2024（通过 2013 template_id 关联）、1111 category_param（内含 2124/2013 引用）

## 写入位置 BUG（再犯）

| 问题 | 原因 | 修复 |
|------|------|------|
| 2142 数据插到表头 | 手写脚本用 `len(rows)` 当最后行，但 API 返回值可能截断 | 新建 `gsheet_utils.py` 的 `find_last_data_row()` 遍历 ID 列找真正最后非空行 |
| 2142 写到了错误页签 | 表有两个同名页签（带/不带后缀），默认写到了不带后缀的那个 | 写入前确认页签名跟导表工具读的一致 |
| 2024 新增行缺 A_INT_max 列 | 克隆时源行只有 10 列，目标表有 11 列 | 克隆必须读表头列数，不足补默认值 |
| 2013 pkg_title 用 astro LC key | 脚本只换了 2112 的 LC key，没换 2013 的 | 所有含 LC key 的表都要检查 |
| 1111 use_labels 列被写入了错误数据 | 修 category_param 时列号算错 | 修改前先对比源行确认列位置 |

## 新增的必检表

之前的 reskin skill 只覆盖了 2112/2115/2116/2121/2122/2124/2135/2011/2013/2137。这次新发现需要配的表：

| 表 | 说明 | 何时需要 |
|---|------|---------|
| 2141 activity_without_gacha_pool | 无底 Gacha 奖池 | 有 Gacha 抽奖活动时 |
| 2142 activity_without_gacha_reward | 无底 Gacha 奖励 | 同上，注意页签名可能带后缀 |
| 2024 iap_custom_chest | 自选礼包坑位 | 有周卡/自选礼包时 |
| 2151 activity_monopoly_gacha_map | 大富翁地图 | 有大富翁活动时 |
| 1365 march_effect | 行军特效外观 | 有行军特效时，注意全列克隆 |
| 1187 FurnitureBuild | 装饰品家具 | 有装饰品时 |

## 关键经验

1. **复用旧组件不等于不用检查**：复用的旧行里的 JSON 字段可能引用了旧节日道具/活动 ID
2. **每新增一个 2011 ID 都要加到累充 2122 的 score_rule**：否则该礼包购买不计入累充排名
3. **`len(values)` 严禁用于定位最后行**：已经犯了 3 次，必须用遍历 ID 列的方式
4. **页签名要跟导表工具完全一致**：有后缀的（如"天赋投放活动"）不能省
5. **克隆行必须补全所有列**：INT 列为空会导致 fwcli 报错
