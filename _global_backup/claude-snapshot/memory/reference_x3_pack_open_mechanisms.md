---
name: reference_x3_pack_open_mechanisms
description: "X3 礼包靠什么触发/显示——OpenActv 常为空时的 4 类开启机制速查；问\"礼包怎么开/为啥不显示\"先读"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 83315ed9-056a-42dd-a38f-ffd420801357
---

X3 一个 Pack 能不能在玩家端弹出来，**不只看 `Pack.IsOn` 和 `OpenActv`**——很多节日包 `OpenActv`/`ContentID` 都是空的，靠**外部表反向引用 + TimeCycle 窗口**才显示。问"这个礼包怎么开 / 为啥不显示"时，按 PackType 反查下面 4 张绑定表（用全仓 grep 礼包 ID，排除 `Route__RouteLevels`/`UnitConfigMonster` 的 ID 撞车命中）。

## 四类开启机制（按 PackType 判断）

| PackType | 类型 | 靠什么开 | 绑定表 |
|----------|------|---------|--------|
| **1**（UIType=3） | 英雄晋升礼包 | 玩家持有该英雄 + 进晋升界面触发；售卖窗口走 TimeCycle | `PackHeroPromotion__PackHeroPromotion`（行=某英雄某段晋升→PackID）+ 可能挂 `PackTypeInfo` 商城推荐位 |
| **15** | 道具获取弹窗礼包 | 玩家在"道具获取"入口点对应道具时弹出；常驻看 TimeCycleID | `ItemObtain__ItemObtain`（行=某道具获取入口→引用 PackID）+ `Pack.TimeCycleID` |
| **16** | 活动礼包（拜访礼包等） | 靠独立活动开启，**ActvType=56=拜访礼包** | `ActvVisitPack__ActvVisitPack`（行 `PackID` 列指向 Pack）→ 对应 `ActvOnline` type=56 活动需部署 |
| 11 / 15 | 链式/锚点 | 父链或活动面板引用 | `Pack__ChainPack.PackList` / `ActvOnline.ChainPackID` |

## 触发字段（Pack__Pack 自身）
- `TriggerType=1` → `TriggerParameter` 填 **TimeCycle ID**（不是单独的 TimeCycleID 列）；其余 TriggerType 见表内说明行（2=等级 5=买指定包 9=获得英雄 12=任务计数…）。
- `TimeCycleID` 列（col19）= 礼包自身**售卖循环窗口**，与 TriggerType 的推送是两回事。
- ⚠️ **`Pack__Pack.tsv` 表头在 row5（英文字段名），数据 row6 起**——不是标准 7 行头！脚本定位列别套通用 row7。

## 实战陷阱（2026-06-08 情人节包 210716/210717/210718 查询）
- 三个同节日包开法各不同：210716=英雄晋升触发 / 210717=拜访礼包活动(ActvVisitPack 5603,type=56) / 210718=道具获取弹窗(ItemObtain 100329)+TimeCycle 6001(礼包-永久)常驻。
- **TimeCycle 名字是历史复用残留**：TC 1826 名"白色花嫁活动"(2026-02-06起10天,情人节)，却被"夏日柔情海湾"拜访礼包活动(ActvOnline 105603,type=56)复用绑定——看 StartTime 实际值判断窗口，别信名字（见 [[feedback_x3_timecycle_name_legacy]]）。
- 节日过期后这些包玩家端开不出来=TimeCycle 窗口已过；想重开要新建/改 TimeCycle 到目标日期，别直接改被其他活动复用的 TC。

## 关联
- [[reference_x3_config_library]] §2.2 礼包族 · [[reference_x3_timecycle]] · [[reference_x3_pack_panel_rendering]] · [[reference_x3_pack_tab_icon]]
